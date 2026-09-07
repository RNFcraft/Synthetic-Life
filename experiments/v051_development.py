"""Does accumulated cognition transfer to held-out pair placements? No scripted actions."""
from __future__ import annotations
import json,tempfile,time
from dataclasses import asdict
from pathlib import Path
from random import Random
from config import Settings
from curriculum import TARGET_PATTERNS,evaluate_pattern
from simulation import Simulation
from consciousness.relation import RelationType

VERSION="v051-development-1"
SETTINGS=Settings(object_count=0,max_objects=8,place_birth_visits=1,telemetry_history=1)

def placement(seed):
    rng=Random(seed);points=[]
    while len(points)<4:
        p=(rng.randint(3,26),rng.randint(3,26))
        if p!=(15,15) and p not in points and all(abs(p[0]-x)+abs(p[1]-y)>1 for x,y in points):points.append(p)
    return points

def episode(seed,budget,brain=None,ablate=False):
    sim=Simulation(seed,SETTINGS)
    if brain:sim.load_brain(str(brain))
    if ablate:
        for source,edges in sim.core.graph.adjacency.items():
            for key in [k for k,r in edges.items() if r.relation_type in {RelationType.SPATIAL,RelationType.SELF_ACTION}]:edges.pop(key)
        sim.core.affordances.entries=[]
    sim.world.body.x=sim.world.body.y=15;sim.world.body.orientation="NORTH";points=placement(seed);sim.world.initialize_controlled_objects(points)
    sim.core.receive_target(TARGET_PATTERNS["pair"]);history=[];started=time.perf_counter();before=sim.world.action_counts.copy();initial_config=[{"id":o.id,"position":o.position} for o in sim.world.objects]
    success=False
    for tick in range(1,budget+1):
        metric=sim.step();history.append(sim.core.target_mismatch)
        if evaluate_pattern(sim.world.objects,TARGET_PATTERNS["pair"]):success=True;break
    elapsed=time.perf_counter()-started;counts={k:sim.world.action_counts[k]-before.get(k,0) for k in sim.world.action_counts}
    raw={"version":VERSION,"seed":seed,"settings":asdict(SETTINGS),"initial_configuration":initial_config,"budget":budget,"actions":tick,"success":success,"target_mismatch_history":history,"minimum_target_mismatch":min(history,default=1.),"final_target_mismatch":history[-1] if history else 1.,"world_modification":sim.world.world_modification(),"action_counts":counts,"subgoals":{"created":sim.core.state.subgoals_created,"completed":sim.core.state.subgoals_completed,"failed":sim.core.state.subgoals_failed},"memory_retrievals":sim.core.memory.reactivation_count,"cognits":len(sim.core.graph.nodes),"relations":sim.core.graph.relation_count,"elapsed_seconds":elapsed,"physical_actions_per_second":tick/max(elapsed,1e-9),"cognitive_cycles_per_second":sim.core.planner.total_cycles/max(elapsed,1e-9),"ablated":ablate}
    return sim,raw

def summarize(runs):
    return {"successes":sum(r["success"] for r in runs),"mean_minimum_mismatch":sum(r["minimum_target_mismatch"] for r in runs)/len(runs),"mean_world_modification":sum(r["world_modification"] for r in runs)/len(runs),"mean_blind_interactions":sum(r["action_counts"]["blind_interactions"] for r in runs)/len(runs)}

def main():
    budget=60;root=Path("runs/v051-development");root.mkdir(parents=True,exist_ok=True);brain=root/"experienced.sebrain";training=[]
    for index,seed in enumerate((2101,2102,2103)):
        sim,result=episode(seed,budget,brain if index else None);training.append(result);sim.save_brain(brain)
    experienced=[];fresh=[];ablated=[]
    for seed in (2201,2202,2203):
        _,a=episode(seed,budget,brain);experienced.append(a);_,b=episode(seed,budget);fresh.append(b);_,c=episode(seed,budget,brain,True);ablated.append(c)
    payload={"version":VERSION,"training":training,"held_out":{"experienced":experienced,"fresh":fresh,"ablated":ablated},"summary":{"experienced":summarize(experienced),"fresh":summarize(fresh),"ablated":summarize(ablated)}}
    (root/"result.json").write_text(json.dumps(payload,indent=2),encoding="utf-8");print(json.dumps(payload["summary"],indent=2))

if __name__=="__main__":main()
