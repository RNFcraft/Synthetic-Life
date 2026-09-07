"""One-command v0.5.1 endurance run with crash-safe progress and artifacts."""
from __future__ import annotations
import argparse,json,os,statistics,time
from collections import Counter
from datetime import datetime
from pathlib import Path

from config import Settings
from curriculum import TARGET_PATTERNS,evaluate_pattern
from simulation import Simulation

def atomic_json(path:Path,value:dict)->None:
    tmp=path.with_suffix(path.suffix+".tmp");tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding="utf-8");os.replace(tmp,path)

def main()->None:
    parser=argparse.ArgumentParser(description="Synthetic Entity v0.5.1 50k autorun")
    parser.add_argument("--ticks",type=int,default=50_000);parser.add_argument("--seed",type=int,default=51001)
    parser.add_argument("--checkpoint-every",type=int,default=10_000);parser.add_argument("--output-dir")
    args=parser.parse_args();stamp=datetime.now().strftime("%Y%m%d-%H%M%S")
    out=Path(args.output_dir or f"runs/v051-{stamp}-seed{args.seed}");out.mkdir(parents=True,exist_ok=True)
    sim=Simulation(args.seed,Settings(telemetry_history=1));started=time.perf_counter();actions=Counter();results=Counter();samples=[]
    sums=Counter();metric_names=("prediction_error","controllability","agency_estimate","active_ratio","wave_energy","internal_tension","loop_score")
    manifest={"version":"v0.5.1","seed":args.seed,"target_ticks":args.ticks,"status":"running","started":datetime.now().isoformat(),"checkpoints":[]}
    atomic_json(out/"progress.json",manifest)
    try:
        for tick in range(1,args.ticks+1):
            metric=sim.step();actions[metric.action]+=1;results[metric.action_result]+=1
            for name in metric_names:sums[name]+=getattr(metric,name)
            if tick%args.checkpoint_every==0 or tick==args.ticks:
                checkpoint=out/f"checkpoint-{tick:06d}.seworld";sim.save_world(checkpoint)
                sample={"tick":tick,"elapsed_seconds":time.perf_counter()-started,"cognits":metric.cognit_count,"relations":metric.relation_count,"places":len(sim.core.memory.places),"object_memories":len(sim.core.memory.structures),"plans_created":sim.core.planner.plans_created,"world_modification":metric.world_modification}
                samples.append(sample);manifest["checkpoints"].append({"tick":tick,"file":checkpoint.name})
                manifest["latest"]=sample;atomic_json(out/"progress.json",manifest);print(json.dumps(sample),flush=True)
        elapsed=time.perf_counter()-started;sim.save_brain(out/"final.sebrain");sim.save_world(out/"final.seworld")
        report={"version":"v0.5.1","status":"complete","seed":args.seed,"ticks":args.ticks,"elapsed_seconds":elapsed,"physical_actions_per_second":args.ticks/max(elapsed,1e-9),"actions":dict(actions),"action_results":dict(results),"means":{k:sums[k]/args.ticks for k in metric_names},"final":{"cognits":len(sim.core.graph.nodes),"relations":sim.core.graph.relation_count,"places":len(sim.core.memory.places),"object_memories":len(sim.core.memory.structures),"plans_created":sim.core.planner.plans_created,"plans_revised":sim.core.planner.plans_revised,"plans_abandoned":sim.core.planner.plans_abandoned,"conflicts":sim.world.conflict_count,"curriculum":{name:evaluate_pattern(sim.world.objects,target) for name,target in TARGET_PATTERNS.items()}},"samples":samples,"artifacts":{"brain":"final.sebrain","world":"final.seworld"}}
        atomic_json(out/"result.json",report);manifest.update({"status":"complete","finished":datetime.now().isoformat(),"result":"result.json"});atomic_json(out/"progress.json",manifest)
    except BaseException as exc:
        manifest.update({"status":"failed","error":repr(exc),"failed":datetime.now().isoformat(),"tick":sim.clock.tick});atomic_json(out/"progress.json",manifest);raise
    print(f"RESULT_DIR={out.resolve()}",flush=True)

if __name__=="__main__":main()
