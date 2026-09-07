"""Small correctness-first v0.5.1 causal validation; intentionally not a benchmark."""
from __future__ import annotations
from collections import Counter
from dataclasses import asdict
from pathlib import Path
import json

from config import Settings
from curriculum import TARGET_PATTERNS
from simulation import Simulation
from world import Action,ActionType
from consciousness.relation import RelationType

SETTINGS=Settings(object_count=0,perception_radius=4,relation_provisional_support=3,relation_provisional_lift=1.)

def distance(sim):
    positions={o.id:o.position for o in sim.world.objects}
    for body_id,obj in sim.world.held_objects.items():positions[obj.id]=sim.world.bodies[body_id].position
    if len(positions)<2:return 99
    a,b=[positions[i] for i in sorted(positions)[:2]];return abs(a[0]-b[0])+abs(a[1]-b[1])

def configure(sim,positions=((5,2),(5,4))):
    sim.world.body.x,sim.world.body.y,sim.world.body.orientation=positions[0][0],5,"NORTH"
    sim.world.initialize_controlled_objects(list(positions));sim.core.previous_action=None

def train(seed=511,backend="native"):
    sim=Simulation(seed,SETTINGS,backend=backend)
    for episode in range(5):
        sim.core.belief_scene.new_episode()
        for trial in range(4):
            configure(sim);sim.core.step(sim.world.perceive(episode*100+2*trial))
            sim.world.apply_action(Action(ActionType.MOVE_UP));sim.core.previous_action=ActionType.MOVE_UP
            sim.core.step(sim.world.perceive(episode*100+2*trial+1))
    return sim

def bound_effects(sim):
    graph=sim.core.graph;bound={r.cognit_id:r for r in sim.core.belief_scene.relations.values()};out=[]
    for source in graph.nodes:
        for rho in graph.outgoing(source):
            before,after=bound.get(rho.source_id),bound.get(rho.target_id)
            if rho.relation_type is RelationType.SELF_ACTION and before and after and before.token!=after.token and (before.source_id,before.target_id)==(after.source_id,after.target_id):
                out.append((rho,before,after))
    return sorted(out,key=lambda x:x[0].support,reverse=True)

def causal_trace(sim):
    rho,before,after=bound_effects(sim)[0];configure(sim);tick=900
    sim.core.step(sim.world.perceive(tick));binding_before=asdict(sim.core.belief_scene.best_binding(TARGET_PATTERNS["pair"] and sim.core.target_structure)) if sim.core.target_structure else None
    mismatch_before=sim.core.target_mismatch;uncertainty_before=sim.core.target_knowledge_uncertainty;positions_before=[o.position for o in sim.world.objects];d0=distance(sim)
    active={before.cognit_id};pred=sim.core.predict_from_relations(active,ActionType.MOVE_UP);progress=sim.core.predicted_target_progress(active,ActionType.MOVE_UP)
    outcome=sim.world.apply_action(Action(ActionType.MOVE_UP));sim.core.previous_action=ActionType.MOVE_UP;sim.core.step(sim.world.perceive(tick+1))
    return {"world_tick":tick,"action":"MOVE_UP","internal_binding_before":binding_before,"structural_mismatch_before":mismatch_before,"uncertainty_before":uncertainty_before,
      "predicted_graph_effects":{str(k):v for k,v in pred.items()},"predicted_progress":progress,"learned_effect":{"source":rho.source_id,"target":rho.target_id,"support":rho.support},
      "action_outcome":outcome.name,"internal_binding_after":asdict(sim.core.belief_scene.last_binding),"structural_mismatch_after":sim.core.target_mismatch,"uncertainty_after":sim.core.target_knowledge_uncertainty,
      "external_positions_before":positions_before,"external_positions_after":[o.position for o in sim.world.objects],"external_pair_distance_before":d0,"external_pair_distance_after":distance(sim),"external_pair_distance_change":distance(sim)-d0,
      "subgoal":asdict(sim.core.state.goal) if sim.core.state.goal else None}

def evaluate(sim,episode,budget=30):
    # Held-out translations preserve the learned relation but change absolute location.
    x=6+episode;configure(sim,((x,2),(x,4)));sim.core.belief_scene.new_episode();sim.core.receive_target(TARGET_PATTERNS["pair"])
    initial=distance(sim);minimum=initial;useful=0;unnecessary=0;first=None;counts=Counter()
    for tick in range(budget):
        before=distance(sim);mod_before=sim.world.world_modification();metric=sim.step();after=distance(sim);counts[metric.action]+=1
        if after<before:useful+=1;first=tick if first is None else first
        if sim.world.world_modification()>mod_before and after>=before:unnecessary+=1
        minimum=min(minimum,after)
        if after==1:break
    return {"episode":episode,"success":distance(sim)==1,"initial_pair_distance":initial,"minimum_pair_distance":minimum,"final_pair_distance":distance(sim),"target_relevant_displacements":useful,"useful_modifications":useful,"first_useful_action":first,"unnecessary_manipulation":unnecessary,"actions":sum(counts.values()),"action_counts":dict(counts)}

def clone(path,seed):
    sim=Simulation(seed,SETTINGS,backend="native");sim.load_brain(path);return sim

def main():
    out=Path("runs/v051-causal");out.mkdir(parents=True,exist_ok=True);brain=out/"experienced.sebrain"
    trained=train();trained.core.receive_target(TARGET_PATTERNS["pair"]);trace=causal_trace(trained);trained.save_brain(brain)
    groups={"experienced":[],"fresh":[],"causal_rho_ablated":[]}
    for episode in range(5):
        experienced=clone(brain,700+episode);fresh=Simulation(700+episode,SETTINGS,backend="native");ablated=clone(brain,700+episode)
        for source in list(ablated.core.graph.nodes):
            for rho in list(ablated.core.graph.outgoing(source)):
                if rho.relation_type is RelationType.SELF_ACTION and ablated.core.graph.nodes.get(rho.target_id) and ablated.core.graph.nodes[rho.target_id].kind=="BOUND_RELATION":ablated.core.graph.remove_relation(source,rho.target_id,rho.relation_type,rho.context_id)
        groups["experienced"].append(evaluate(experienced,episode));groups["fresh"].append(evaluate(fresh,episode));groups["causal_rho_ablated"].append(evaluate(ablated,episode))
    summary={name:{"successes":sum(x["success"] for x in rows),"mean_min_pair_distance":sum(x["minimum_pair_distance"] for x in rows)/len(rows),"useful_modifications":sum(x["useful_modifications"] for x in rows),"mean_first_useful_action":(sum(x["first_useful_action"] for x in rows if x["first_useful_action"] is not None)/max(1,sum(x["first_useful_action"] is not None for x in rows))),"mean_actions":sum(x["actions"] for x in rows)/len(rows),"unnecessary_manipulation":sum(x["unnecessary_manipulation"] for x in rows)} for name,rows in groups.items()}
    result={"version":"v0.5.2-native","backend":"native","python_transition_updates_in_native_mode":0,"seed":511,"scope":"native authority causal regression","training":{"episodes":5,"forced_physical_calibrations_per_episode":4},"evaluation_budget":30,"causal_trace":trace,"groups":groups,"summary":summary}
    (out/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
