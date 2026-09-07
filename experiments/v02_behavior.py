"""Deterministic multi-seed behavioral observation for Synthetic Entity v0.2."""
import argparse
import csv
import json
import statistics
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path
from config import Settings
from simulation import Simulation


def percentile(values:list[float],q:float)->float:
    if not values:return 0.0
    ordered=sorted(values);return ordered[min(len(ordered)-1,int(q*(len(ordered)-1)))]


def longest_position_loop(positions:list[tuple[int,int]],max_period:int=16)->int:
    longest=0
    for period in range(1,max_period+1):
        run=0
        for i in range(period,len(positions)):
            run=run+1 if positions[i]==positions[i-period] else 0;longest=max(longest,run+period if run else 0)
    return longest


def run_seed(seed:int,ticks:int,keep_rows:bool=False)->tuple[dict,list[dict]]:
    simulation=Simulation(seed,replace(Settings(),telemetry_history=1));started=time.perf_counter()
    active=[];errors=[];wave=[];loops=[];positions=[];actions:Counter[str]=Counter();rows=[]
    for _ in range(ticks):
        m=simulation.step();active.append(m.active_ratio);errors.append(m.prediction_error);wave.append(m.wave_energy);loops.append(m.loop_score)
        positions.append(m.entity_position);actions[m.action]+=1
        if keep_rows:rows.append(m.to_dict())
    elapsed=time.perf_counter()-started;quarter=max(1,len(errors)//4)
    node_count=len(simulation.core.graph.nodes);relation_count=simulation.core.graph.relation_count
    lifetimes=simulation.core.state.completed_goal_lifetimes[:]
    if simulation.core.state.goal:lifetimes.append(simulation.core.state.goal.age)
    summary={"seed":seed,"ticks":ticks,"elapsed_seconds":elapsed,"ticks_per_second":ticks/max(elapsed,1e-9),
      "unique_positions":len(set(positions)),"longest_position_loop":longest_position_loop(positions),"cognit_count":node_count,
      "relation_count":relation_count,"relation_density":relation_count/max(1,node_count*(node_count-1)),
      "mean_active_ratio":statistics.fmean(active),"p95_active_ratio":percentile(active,.95),
      "prediction_error_early":statistics.fmean(errors[:quarter]),"prediction_error_late":statistics.fmean(errors[-quarter:]),
      "mean_wave_energy":statistics.fmean(wave),"mean_internal_loop_score":statistics.fmean(loops),
      "goals_generated":simulation.core.state.goals_generated,"average_goal_lifetime":statistics.fmean(lifetimes) if lifetimes else 0.0,
      "action_distribution":dict(actions)}
    return summary,rows


def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument("--seeds",type=int,default=10);parser.add_argument("--ticks",type=int,default=50_000)
    parser.add_argument("--output",default="v02-results.json");parser.add_argument("--csv",default=None);parser.add_argument("--workers",type=int,default=1);args=parser.parse_args()
    summaries=[];csv_path=Path(args.csv) if args.csv else None
    jobs=[(seed,args.ticks,bool(csv_path)) for seed in range(args.seeds)]
    iterator=(ProcessPoolExecutor(max_workers=args.workers).map(_run_job,jobs) if args.workers>1 else map(_run_job,jobs))
    for summary,rows in iterator:
        summaries.append(summary);print(json.dumps(summary,sort_keys=True),flush=True)
        if csv_path:
            with csv_path.open("a" if csv_path.exists() else "w",newline="",encoding="utf-8") as stream:
                writer=csv.DictWriter(stream,fieldnames=rows[0].keys());
                if stream.tell()==0:writer.writeheader()
                writer.writerows(rows)
    Path(args.output).write_text(json.dumps(summaries,indent=2),encoding="utf-8")


def _run_job(job:tuple[int,int,bool])->tuple[dict,list[dict]]:
    return run_seed(*job)


if __name__=="__main__":main()
