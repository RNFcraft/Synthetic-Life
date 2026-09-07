"""External v0.3 observations; physical metrics never enter the cognitive core."""
import argparse,json,statistics,time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from config import Settings
from consciousness import SyntheticEntityCore
from world.perception import SensoryCell,SensoryFrame
from simulation import Simulation
from experiments.v02_behavior import longest_position_loop,percentile


def symmetric_actions(ticks:int=10_000)->dict[str,int]:
    core=SyntheticEntityCore(Settings());counts:Counter[str]=Counter()
    cells=tuple(SensoryCell(x,y,False,0,False,x==y==0) for y in range(-3,4) for x in range(-3,4))
    for tick in range(ticks):counts[core.step(SensoryFrame(tick,3,cells)).kind.name]+=1
    return dict(counts)


def run_seed(seed:int,ticks:int)->dict:
    simulation=Simulation(seed,replace(Settings(),telemetry_history=1));started=time.perf_counter();positions=[];actions:Counter[str]=Counter()
    active=[];energy=[];known=[];coverage=[];continuity=[];brier=[];loops=[];tie_methods:Counter[str]=Counter()
    for _ in range(ticks):
        m=simulation.step();positions.append(m.entity_position);actions[m.action]+=1;active.append(m.active_ratio);energy.append(m.wave_energy)
        if m.prediction_error_valid:known.append(m.known_prediction_error)
        coverage.append(m.representation_coverage);continuity.append(m.continuity_error);brier.append(m.brier_score);loops.append(m.loop_score)
        if m.tie_set_size>1:tie_methods[m.tie_resolution_method]+=1
    elapsed=time.perf_counter()-started;m=simulation.telemetry.latest;perception=simulation.core.perception
    return {"seed":seed,"ticks":ticks,"elapsed_seconds":elapsed,"ticks_per_second":ticks/max(elapsed,1e-9),"cognits":m.cognit_count,
      "primitive_cognits":m.primitive_cognit_count,"composite_cognits":m.composite_cognit_count,"relations":m.relation_count,"relation_density":m.relation_density,
      "mean_active_ratio":statistics.fmean(active),"p95_active_ratio":percentile(active,.95),"mean_wave_energy":statistics.fmean(energy),
      "mean_known_prediction_error":statistics.fmean(known) if known else 0.,"mean_representation_coverage":statistics.fmean(coverage),
      "mean_continuity_error":statistics.fmean(continuity),"mean_brier_score":statistics.fmean(brier),"mean_loop_score":statistics.fmean(loops),
      "tracks_created":perception.created_total,"tracks_closed":perception.closed_total,"mean_track_lifetime":statistics.fmean(perception.completed_lifetimes) if perception.completed_lifetimes else 0.,
      "goals_generated":simulation.core.state.goals_generated,"goals_retired":simulation.core.state.goals_retired,
      "unique_positions":len(set(positions)),"longest_physical_loop":longest_position_loop(positions),"action_distribution":dict(actions),
      "tie_count":m.action_tie_count,"tie_resolution_distribution":dict(tie_methods),"sensorimotor":{a.name:{"support":s.support,"mean_dx":s.mean_dx,"mean_dy":s.mean_dy,"confidence":perception.transforms.estimate(a)[3]} for a,s in perception.transforms.stats.items()}}


def _job(args:tuple[int,int])->dict:return run_seed(*args)


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--seeds",type=int,default=10);parser.add_argument("--ticks",type=int,default=50_000);parser.add_argument("--workers",type=int,default=1);parser.add_argument("--output",default="v03-results.json");parser.add_argument("--symmetric-ticks",type=int,default=10_000);args=parser.parse_args()
    jobs=[(seed,args.ticks) for seed in range(args.seeds)];iterator=ProcessPoolExecutor(args.workers).map(_job,jobs) if args.workers>1 else map(_job,jobs)
    results=[]
    for result in iterator:results.append(result);print(json.dumps(result,sort_keys=True),flush=True)
    payload={"symmetric_action_distribution":symmetric_actions(args.symmetric_ticks),"runs":results};Path(args.output).write_text(json.dumps(payload,indent=2),encoding="utf-8");print(json.dumps(payload["symmetric_action_distribution"],sort_keys=True))


if __name__=="__main__":main()
