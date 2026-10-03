"""Autonomous fixed-budget training and isolated paired evaluation."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from experiments.scenario_runner import _write_result
from simulation import ContinuousRuntime
from simulation.scenario import ScenarioDefinition, artifact_checksum, canonical_json, load_scenario
from .protocol import GROUPS, ROOT, load_protocol, scenario_path
from .recorder import record


def instantiate(path,seed,group="FRESH_FULL",brain=None):
    if group not in GROUPS: raise ValueError("unknown trial group")
    if group=="FRESH_FULL" and brain is not None: raise ValueError("fresh group cannot load experienced brain")
    sections=load_scenario(path).sections
    sections["CONFIG"]["seed"]=seed
    for name,value in GROUPS[group].items(): sections["CONFIG"]["settings"]["runtime"][name]=value
    definition=ScenarioDefinition.from_sections(sections)
    runtime=ContinuousRuntime.from_scenario(definition,brain)
    assert runtime.world_time==runtime.simulation.event_sequence.value==0
    assert runtime.simulation.core.backend.full_graph_sync_calls==0
    return runtime,definition


def trial_id(stage,path,seed,group):return f"{stage}__{Path(path).stem}__{seed}__{group}"


def run_trial(protocol,case,seed,group,brain,stage):
    path=scenario_path(case["scenario"])
    checksum=artifact_checksum(brain) if brain else "FRESH"
    runtime,definition=instantiate(path,seed,group,brain)
    initial_relation_count=runtime.simulation.core.backend.engine.relation_count
    result=record(runtime,case["horizon"],protocol.data["PROTOCOL"]["evaluation_discount"])
    if brain and artifact_checksum(brain)!=checksum: raise RuntimeError("input brain modified by evaluation")
    result.update(schema="synthetic-life-survival-trial",version=1,protocol_checksum=protocol.checksum,
        scenario=case["scenario"],scenario_checksum=artifact_checksum(path),
        effective_causal_checksum=definition.causal_checksum,
        geometry_checksum=sha256(canonical_json(definition.sections["INITIAL"]).encode()).hexdigest(),
        brain_checksum=checksum,group=group,stage=stage,seed=seed,horizon=case["horizon"],
        initial_relation_count=initial_relation_count,
        trial_id=trial_id(stage,path,seed,group),software_version="0.9.2",numeric_backend="native")
    return runtime,result


def compact(result,relative_path):
    excluded={"trajectory","decisions","evidence"}
    row={k:v for k,v in result.items() if k not in excluded}
    row["trajectory_reference"]=relative_path
    row["planner_summary"]=dict(decisions=len(result["decisions"]),
        temporal_usable=sum(bool(d["diagnostics"].get("temporal",{}).get("usable")) for d in result["decisions"]),
        multi_step=sum(bool(d["plan"] and len(d["plan"]["actions"])>1) for d in result["decisions"]))
    evidence=result["evidence"]
    row["acquisition"]=dict(timing_observations=evidence["timing_observations"],passive_observations=evidence["passive_observations"],
        beneficial_relations=len(evidence["beneficial_relations"]),
        timed_beneficial_relations=sum(bool(r["timing"]) for r in evidence["beneficial_relations"]))
    return row


def train_stage(protocol,stage,output,brain,episode_offset=0):
    rows=[];seeds=protocol.data["PROTOCOL"]["training_seeds"]
    for case in stage["training"]:
        for episode in range(case["episodes"]):
            seed=seeds[(episode_offset+len(rows))%len(seeds)]
            runtime,definition=instantiate(scenario_path(case["scenario"]),seed,"EXPERIENCED_FULL",brain)
            initial=dict(world_time=runtime.world_time,event_sequence=runtime.simulation.event_sequence.value,
                reserves={key:getattr(runtime.simulation.physiology,key) for key in ("energy","nutrients","hydration")},
                relations=runtime.simulation.core.backend.engine.relation_count,
                brain_checksum=artifact_checksum(brain) if brain else "FRESH")
            if brain is None and initial["relations"]!=0: raise RuntimeError("initial brain is not fresh")
            result=record(runtime,case["horizon"],protocol.data["PROTOCOL"]["evaluation_discount"])
            number=episode_offset+len(rows)+1
            new_brain=output/"brains"/f"episode_{number:03d}.sebrain"
            new_brain.parent.mkdir(parents=True,exist_ok=True)
            runtime.simulation.save_brain(new_brain)
            result.update(stage=stage["id"],episode=number,seed=seed,scenario=case["scenario"],
                scenario_checksum=artifact_checksum(scenario_path(case["scenario"])),protocol_checksum=protocol.checksum,
                initial_episode=initial,brain_checksum=artifact_checksum(new_brain))
            relative=f"training/episode_{number:03d}.json"
            _write_result(output/relative,result)
            rows.append(dict(stage=stage["id"],episode=number,seed=seed,horizon=case["horizon"],
                scenario=case["scenario"],scenario_checksum=result["scenario_checksum"],
                input_brain_checksum=initial["brain_checksum"],brain_checksum=result["brain_checksum"],
                initial_episode=initial,consumptions=result["consumption_count"],
                nutrient_gain=sum(c["nutrient_gain"] for c in result["consumptions"]),
                internal_bin_changes=sum(bool(result["consumptions"]) and b["time"]>=result["consumptions"][0]["time"] and a["internal"] is not None and b["internal"] is not None and any(y>x for x,y in zip(a["internal"][:3],b["internal"][:3]))
                                         for a,b in zip(result["trajectory"],result["trajectory"][1:])),
                evidence=result["evidence"],trajectory_reference=relative))
            brain=new_brain
            print(f"{stage['id']} training {number}: consumptions={result['consumption_count']}",flush=True)
    if stage["training"]:
        checkpoint=output/"brains"/(stage["checkpoint"]+".sebrain")
        shutil.copyfile(brain,checkpoint);brain=checkpoint
    if brain is None: raise RuntimeError("no training checkpoint produced")
    return brain,rows


def evaluate_stage(protocol,stage,brain,output,seeds=None,group_order=None):
    rows=[]
    for case in stage["evaluation"]:
        for seed in seeds or protocol.data["PROTOCOL"]["evaluation_seeds"]:
            for group in group_order or GROUPS:
                _,result=run_trial(protocol,case,seed,group,None if group=="FRESH_FULL" else brain,stage["id"])
                relative="trials/"+result["trial_id"]+".json"
                _write_result(output/relative,result);rows.append(compact(result,relative))
            print(f"{stage['id']} evaluation {Path(case['scenario']).stem}, seed {seed}",flush=True)
    return rows


def software_provenance():
    return dict(git_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        project_version="0.9.2",numeric_backend="native",python=sys.version.split()[0],platform=platform.platform())


def execute(protocol,output,mode="all"):
    output=Path(output).resolve()
    if mode in ("all","train") and output.exists() and any(output.iterdir()): raise ValueError("use a clean research output directory")
    if output.is_relative_to(ROOT/"scenarios") or output.is_relative_to(ROOT/"experiments/protocols"):
        raise ValueError("output cannot overwrite input artifacts")
    output.mkdir(parents=True,exist_ok=True)
    _write_result(output/"protocol-lock.json",dict(protocol_checksum=protocol.checksum,protocol=protocol.data,
                                                 software=software_provenance(),thresholds_changed_after_full_run=False))
    stages=protocol.data["STAGES"];training=[];trials=[];checkpoints={};brain=None
    if mode in ("all","train"):
        for stage in stages:
            brain,rows=train_stage(protocol,stage,output,brain,len(training));training.extend(rows)
            checkpoints[stage["id"]]=dict(path=str(brain.relative_to(output)),sha256=artifact_checksum(brain))
            _write_result(output/"training.json",dict(protocol_checksum=protocol.checksum,episodes=training,checkpoints=checkpoints))
            if mode=="all": trials.extend(evaluate_stage(protocol,stage,brain,output))
    elif mode=="evaluate":
        data=json.loads((output/"training.json").read_text(encoding="utf-8"))
        if data["protocol_checksum"]!=protocol.checksum: raise ValueError("training protocol checksum mismatch")
        training,checkpoints=data["episodes"],data["checkpoints"]
        for stage in stages:
            checkpoint=checkpoints[stage["id"]];brain=output/checkpoint["path"]
            if artifact_checksum(brain)!=checkpoint["sha256"]: raise ValueError("checkpoint checksum mismatch")
            trials.extend(evaluate_stage(protocol,stage,brain,output))
    if mode!="train":
        counter_case=dict(scenario=protocol.data["PROTOCOL"]["counterfactual"],horizon=protocol.data["PROTOCOL"]["counterfactual_horizon"])
        counter=[]
        for group in ("FRESH_FULL","EXPERIENCED_FULL"):
            _,row=run_trial(protocol,counter_case,protocol.data["PROTOCOL"]["evaluation_seeds"][0],group,
                            None if group=="FRESH_FULL" else brain,"counterfactual")
            relative="trials/"+row["trial_id"]+".json";_write_result(output/relative,row);counter.append(compact(row,relative))
        result=dict(schema="synthetic-life-survival-results",version=1,protocol_checksum=protocol.checksum,
                    software=software_provenance(),training=training,checkpoints=checkpoints,trials=trials,counterfactual=counter,
                    thresholds_changed_after_full_run=False)
        from .report import analyze, write_report
        result["acceptance"]=analyze(protocol,result,output)
        _write_result(output/"results.json",result);write_report(protocol,result,output/"RESULTS.md")
        print("Overall proof:",result["acceptance"]["verdict"],flush=True)
        return result
    return dict(training=training,checkpoints=checkpoints)


def _rerun_job(job):
    from .protocol import Curriculum
    canonical,stage,brain,output,seed=job
    from .resume import validate_saved
    protocol=Curriculum(canonical);rows=[];output=Path(output)
    for case in stage['evaluation']:
        for group in reversed(GROUPS):
            input_brain=None if group=='FRESH_FULL' else Path(brain)
            relative='trials/'+trial_id(stage['id'],case['scenario'],seed,group)+'.json'
            target=output/relative
            if target.exists():
                result=json.loads(target.read_text(encoding='utf-8'))
                validate_saved(protocol,case,seed,group,input_brain,stage['id'],result)
            else:
                _,result=run_trial(protocol,case,seed,group,input_brain,stage['id'])
                _write_result(target,result)
            rows.append(compact(result,relative))
    print(f"{stage['id']} reverse-order audit seed {seed}",flush=True)
    return rows


def rerun_subset(protocol,output,workers=1):
    output=Path(output).resolve();results=json.loads((output/"results.json").read_text(encoding="utf-8"))
    if results["protocol_checksum"]!=protocol.checksum: raise ValueError("protocol checksum mismatch")
    rerun=output/"determinism";count=0;mismatches=[]
    if workers not in (1,2,3,4):raise ValueError("invalid audit worker count")
    jobs=[]
    for stage in protocol.data["STAGES"]:
        checkpoint=results["checkpoints"][stage["id"]]
        brain=output/checkpoint["path"]
        if artifact_checksum(brain)!=checkpoint["sha256"]:raise ValueError("checkpoint checksum mismatch")
        for case in stage["evaluation"]:
            isolated_stage=dict(stage,evaluation=[case])
            for seed in protocol.data["PROTOCOL"]["determinism_seeds"]:
                jobs.append((protocol.canonical,isolated_stage,str(brain),str(rerun),seed))
    def compare_rows(rows):
        for row in rows:
            expected=json.loads((output/row["trajectory_reference"]).read_text(encoding="utf-8"))
            actual=json.loads((rerun/row["trajectory_reference"]).read_text(encoding="utf-8"))
            if canonical_json(expected)!=canonical_json(actual):
                metric_keys=('success','censored_time','censored_actions','energy_spent','brownout','J','consumption_count')
                mismatches.append(dict(trial_id=row['trial_id'],
                    differing_fields=[k for k in expected if canonical_json(expected[k])!=canonical_json(actual[k])],
                    metrics_identical=all(expected[k]==actual[k] for k in metric_keys)))
        return len(rows)
    if workers==1:
        for job in jobs:count+=compare_rows(_rerun_job(job))
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as executor:
            for rows in executor.map(_rerun_job,jobs):count+=compare_rows(rows)
    from .determinism import hashseed_probe
    hashseed=hashseed_probe(protocol,output,results)
    result=dict(protocol_checksum=protocol.checksum,independent_trials_compared=count,group_order_reversed=True,workers=workers,
                identical=not mismatches and hashseed['identical'],mismatches=mismatches,hashseed=hashseed)
    _write_result(output/"determinism.json",result);print("Determinism rerun:",result,flush=True)
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol",required=True);parser.add_argument("--output",required=True)
    parser.add_argument("--mode",choices=("all","train","evaluate","report","rerun"),default="all")
    parser.add_argument("--require-proof",action="store_true")
    parser.add_argument("--workers",type=int,choices=(1,2,3,4),default=1,help="independent processes for rerun audit only")
    args=parser.parse_args(argv);protocol=load_protocol(args.protocol)
    if args.workers!=1 and args.mode!="rerun":parser.error("parallel workers are only supported for rerun audit")
    if args.mode=="rerun":rerun_subset(protocol,args.output,args.workers);return
    if args.mode=="report":
        from .report import write_report
        result=json.loads((Path(args.output)/"results.json").read_text(encoding="utf-8"))
        if result["protocol_checksum"]!=protocol.checksum: raise ValueError("protocol checksum mismatch")
        write_report(protocol,result,Path(args.output)/"RESULTS.md");return
    result=execute(protocol,args.output,args.mode)
    if args.require_proof and args.mode!="train" and result["acceptance"]["verdict"]!="PASS":raise SystemExit(2)


if __name__=="__main__":main()
