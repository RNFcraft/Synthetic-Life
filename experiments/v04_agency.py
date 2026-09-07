"""External v0.4 agency observations. No physical metric enters cognition."""
import argparse,json,math,statistics,time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from config import Settings
from simulation import Simulation
from world.actions import ActionType
from consciousness.relation import RelationStatus,RelationType
from experiments.v02_behavior import longest_position_loop,percentile


PASSIVE_ACTIONS=(ActionType.IDLE,ActionType.MOVE_UP,ActionType.MOVE_DOWN,ActionType.MOVE_LEFT,ActionType.MOVE_RIGHT)


def structure_metrics(sim:Simulation)->dict:
    positions={o.position for o in sim.world.objects};adjacent=sum((x+1,y) in positions or (x,y+1) in positions for x,y in positions)
    lines2=sum((x+1,y) in positions for x,y in positions)+sum((x,y+1) in positions for x,y in positions)
    lines3=sum((x+1,y) in positions and (x+2,y) in positions for x,y in positions)+sum((x,y+1) in positions and (x,y+2) in positions for x,y in positions)
    remaining=set(positions);clusters=[]
    while remaining:
        group={remaining.pop()};front=list(group)
        while front:
            x,y=front.pop()
            for p in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                if p in remaining:remaining.remove(p);group.add(p);front.append(p)
        clusters.append(len(group))
    return {"adjacent_pairs":adjacent,"lines_2":lines2,"lines_3_plus":lines3,"clusters":len(clusters),"largest_cluster":max(clusters,default=0)}


def run_seed(seed:int,ticks:int,manipulation:bool=True,relation_prediction:bool=True)->dict:
    sim=Simulation(seed,replace(Settings(),telemetry_history=1));sim.core.relation_prediction_enabled=relation_prediction
    if not manipulation:sim.core.available_actions=PASSIVE_ACTIONS
    started=time.perf_counter();positions=[];actions=Counter();samples=[];errors=[];agency=[];control=[];coverage=[];selectivity=[];brier=[];active=[];wave=[];continuity=[];tension=[];loops=[]
    boundaries={min(ticks,x) for x in (10_000,25_000,50_000,100_000,ticks)}
    for index in range(1,ticks+1):
        m=sim.step();positions.append(m.entity_position);actions[m.action]+=1;errors.append(m.known_prediction_error);agency.append(m.agency_estimate)
        control.append(m.controllability);coverage.append(m.representation_coverage);selectivity.append(m.pattern_selectivity);brier.append(m.brier_score)
        active.append(m.active_ratio);wave.append(m.wave_energy);continuity.append(m.continuity_error);tension.append(m.internal_tension);loops.append(m.loop_score)
        if index in boundaries:samples.append({"tick":index,"agency":statistics.fmean(agency[-min(index,10_000):]),"controllability":statistics.fmean(control[-min(index,10_000):]),
          "prediction_error":statistics.fmean(errors[-min(index,10_000):]),"self_action_relations":m.self_action_relations,"world_modification":m.world_modification,"actions":dict(actions)})
    elapsed=time.perf_counter()-started;m=sim.telemetry.latest;relations=[r for edges in sim.core.graph.adjacency.values() for r in edges.values()];nodes=list(sim.core.graph.nodes.values())
    result={"seed":seed,"ticks":ticks,"mode":"agency" if manipulation else "passive","relation_prediction":relation_prediction,"elapsed_seconds":elapsed,"ticks_per_second":ticks/max(elapsed,1e-9),
      "objects_spawned":m.objects_spawned,"unique_positions":len(set(positions)),"longest_physical_loop":longest_position_loop(positions),"world_configurations":m.unique_object_configurations,
      "world_modification":m.world_modification,**sim.world.action_counts,"action_distribution":dict(actions),"cognits":m.cognit_count,"primitive_cognits":m.primitive_cognit_count,
      "composite_cognits":m.composite_cognit_count,"relations":len(relations),"provisional_relations":sum(r.status is RelationStatus.PROVISIONAL for r in relations),
      "consolidated_relations":sum(r.status is RelationStatus.CONSOLIDATED for r in relations),"self_action_relations":sum(r.relation_type is RelationType.SELF_ACTION for r in relations),
      "relation_density":m.relation_density,"relation_candidates":sim.core.relation_candidates,"materialization_rate":sim.core.relations_materialized/max(1,sim.core.relation_candidates),
      "mean_active_ratio":statistics.fmean(active),"p95_active_ratio":percentile(active,.95),"mean_wave_energy":statistics.fmean(wave),"mean_prediction_error":statistics.fmean(errors),"mean_coverage":statistics.fmean(coverage),
      "mean_selectivity":statistics.fmean(selectivity),"mean_representation_quality":statistics.fmean(c*s for c,s in zip(coverage,selectivity)),"mean_brier":statistics.fmean(brier),
      "mean_continuity_error":statistics.fmean(continuity),"mean_internal_tension":statistics.fmean(tension),"mean_loop_score":statistics.fmean(loops),
      "mean_agency":statistics.fmean(agency),"final_agency":m.agency_estimate,"mean_controllability":statistics.fmean(control),"goals_generated":sim.core.state.goals_generated,
      "mean_goal_lifetime":statistics.fmean(sim.core.state.completed_goal_lifetimes) if sim.core.state.completed_goal_lifetimes else 0.,"intervals":samples,
      "candidate_support_min_mean_max":_min_mean_max(list(sim.core.candidate_supports)),"candidate_lift_min_mean_max":_min_mean_max(list(sim.core.candidate_lifts)),
      "mean_relation_age":statistics.fmean(r.age for r in relations) if relations else 0.,"relations_per_active_cognit":len(relations)/max(1,m.active_cognit_count),
      "spawn_records":sim.world.spawn_records,"structures":structure_metrics(sim)}
    assert all(math.isfinite(x) for x in _numbers(result))
    return result


def _numbers(value):
    if isinstance(value,(int,float)) and not isinstance(value,bool):yield float(value)
    elif isinstance(value,dict):
        for x in value.values():yield from _numbers(x)
    elif isinstance(value,(list,tuple)):
        for x in value:yield from _numbers(x)


def _min_mean_max(values:list[float])->list[float]:
    return [min(values),statistics.fmean(values),max(values)] if values else [0.,0.,0.]


def _job(args):return run_seed(*args)


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--seeds",type=int,default=10);parser.add_argument("--start-seed",type=int,default=0);parser.add_argument("--ticks",type=int,default=50_000);parser.add_argument("--workers",type=int,default=1);parser.add_argument("--output",default="v04-results.json");parser.add_argument("--controls",action="store_true");args=parser.parse_args()
    jobs=[(seed,args.ticks,True,True) for seed in range(args.start_seed,args.start_seed+args.seeds)];iterator=ProcessPoolExecutor(args.workers).map(_job,jobs) if args.workers>1 else map(_job,jobs);runs=[]
    for result in iterator:runs.append(result);print(json.dumps(result,sort_keys=True),flush=True)
    payload={"runs":runs}
    if args.controls:
        control_ticks=min(args.ticks,10_000);payload["passive_control"]=run_seed(123,control_ticks,False,True);payload["relation_ablation"]=run_seed(123,control_ticks,True,False)
    Path(args.output).write_text(json.dumps(payload,indent=2),encoding="utf-8")


if __name__=="__main__":main()
