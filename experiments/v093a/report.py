"""Bounded forensic protocol, artifact preservation and offline conclusions."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess

from experiments.v092.protocol import GROUPS, ROOT, load_protocol, scenario_path
from experiments.v092.runner import instantiate, run_trial
from experiments.v092.recorder import record
from simulation.scenario import artifact_checksum, canonical_json, causal_digest
from .credit_trace import CreditTrace, attach, candidate_rows, read_rows, digest, plain, boundary_state
from .determinism import BoundaryTrace, first_boundary, first_difference

EPISODES = 8
PROTOCOL = ROOT / "experiments/protocols/v092_survival.securriculum"


def hashseed_suite(output,baseline):
    protocol=load_protocol(PROTOCOL)
    rows=[]
    for stage_index,groups in ((0,("EXPERIENCED_NO_MOTIVATION",)),(1,tuple(GROUPS))):
        stage=protocol.data["STAGES"][stage_index]
        brain=baseline/("brains/stage1_experienced.sebrain" if stage_index==0 else "brains/stage2_experienced.sebrain")
        checksum=artifact_checksum(brain)
        for group in groups:
            _,row=run_trial(protocol,stage["evaluation"][0],92101,group,
                None if group=="FRESH_FULL" else brain,stage["id"])
            write(output/(row["trial_id"]+".json"),row)
            rows.append(dict(trial_id=row["trial_id"],digest=row["final_digest"],full_graph_sync_calls=row["full_graph_sync_calls"]))
        assert artifact_checksum(brain)==checksum
    write(output/"summary.json",rows)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(plain(value))+"\n", encoding="utf-8")


def traced_episode(scenario, seed, brain, horizon, path, *, group="EXPERIENCED_FULL", boundary=False, detail_index=None):
    runtime, _ = instantiate(scenario, seed, group, brain)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        observer = BoundaryTrace(stream, detail_index=detail_index) if boundary else CreditTrace(stream)
        attach(runtime, observer)
        row = record(runtime, horizon, .02)
        attach(runtime, None)
    return runtime, row, observer


def summarize_credit(path):
    consumption = None
    before = None
    candidate = None
    learned = []
    decisions = []
    for row in read_rows(path):
        if row["kind"] == "event":
            if row["phase"] == "before": before = row["measurement"]
            elif row["event_type"] == "WORLD_ACTION_COMPLETE" and before:
                after = row["measurement"]
                missing = set(r[0] for r in before["resources"])-set(r[0] for r in after["resources"])
                if missing and after["nutrients"] > before["nutrients"] and consumption is None:
                    consumption = dict(time=row["time"], event_id=row["event_id"], before=before, after=after,
                        resource_ids_measurement_only=sorted(missing))
        elif row["kind"] == "learning" and row["phase"] == "after":
            if consumption and row["time"] >= consumption["time"] and candidate is None:
                candidate = row
            if row["candidates"]:
                learned.append(dict(time=row["time"], elapsed=row["elapsed"],
                    maximum_support=max(r["support"] for r in row["candidates"]),
                    admitted=sum(r["admitted"] for r in row["candidates"]),
                    reasons=sorted(set(reason for r in row["candidates"] for reason in r["reasons"]))))
    return dict(consumption=consumption, first_post_consumption_learning=candidate,
        observations=learned, trace_path=str(path))


def credit_audit(output, baseline):
    protocol = load_protocol(PROTOCOL)
    scenario = scenario_path(protocol.data["STAGES"][0]["training"][0]["scenario"])
    brain = baseline / "brains/stage1_experienced.sebrain"
    source_checksum = artifact_checksum(brain)
    # The protocol lock is written before the first observation.
    write(output/"protocol-lock.json", dict(schema="v093a-credit-audit", version=1,
        episodes=EPISODES, seeds=list(range(92001,92009)), horizon=6,
        scenario_checksum=artifact_checksum(scenario), initial_brain_checksum=source_checksum,
        initial_brain="frozen v0.9.2 stage1", forced_actions=False))
    rows = []
    for episode in range(1, EPISODES+1):
        runtime, result, _ = traced_episode(scenario, 92000+episode, brain, 6,
            output/f"episode_{episode:02d}.jsonl")
        summary = summarize_credit(output/f"episode_{episode:02d}.jsonl")
        core = runtime.simulation.core
        timing_before = plain(core.backend.engine.temporal_state())
        relations_before = plain(core.backend.engine.outgoing([i-1 for i in sorted(core.graph.nodes)]))
        brain = output/f"episode_{episode:02d}.sebrain"
        runtime.simulation.save_brain(brain)
        reloaded, _ = instantiate(scenario, 92000+episode, "EXPERIENCED_FULL", brain)
        restored_core = reloaded.simulation.core
        # Brain loading resets volatile activation and relation use/evidence clocks;
        # compare durable fields by semantic identity, not native handles.
        def durable(rows):
            return sorted((r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[10],r[11],r[12],r[13]) for r in rows)
        restored = restored_core.backend.engine.outgoing([i-1 for i in sorted(restored_core.graph.nodes)])
        context = summary["first_post_consumption_learning"]
        restored_candidates = []
        if context:
            from world.actions import ActionType
            completion=context["completion"]
            completion=(ActionType[completion[0]],completion[1]) if completion else None
            restored_candidates = candidate_rows(restored_core, context["sources"], completion, context["targets"])
        rows.append(dict(episode=episode, seed=92000+episode, consumption_count=result["consumption_count"],
            credit=summary, final_digest=result["final_digest"], evidence=result["evidence"],
            persistence=dict(timing_identical=timing_before==plain(restored_core.backend.engine.temporal_state()),
                durable_relations_identical=durable(relations_before)==durable(restored),
                window_before=len(core.backend.engine.transition_history()),
                window_after=len(restored_core.backend.engine.transition_history()),
                restored_candidates=restored_candidates),
            full_graph_sync_calls=core.backend.full_graph_sync_calls))
        print(f"credit episode {episode}/{EPISODES}: consumption={result['consumption_count']}", flush=True)
    assert artifact_checksum(baseline/"brains/stage1_experienced.sebrain") == source_checksum
    # Fresh single episode is retained even when autonomous discovery does not occur.
    _, fresh, _ = traced_episode(scenario,92001,None,6,output/"single_fresh.jsonl")
    write(output/"single_fresh.json",fresh)
    result=dict(episodes=rows, fresh_consumption_count=fresh["consumption_count"],
        original_protocol_checksum=protocol.checksum, thresholds_changed=False)
    write(output/"summary.json",result)
    return result


def stage2_audit(output, baseline):
    protocol=load_protocol(PROTOCOL)
    case=protocol.data["STAGES"][1]["evaluation"][0]
    brain=baseline/"brains/stage2_experienced.sebrain"
    rows={}
    for group in ("EXPERIENCED_FULL","EXPERIENCED_NO_MOTIVATION"):
        _,row,_=traced_episode(scenario_path(case["scenario"]),92101,brain,case["horizon"],output/(group+".jsonl"),group=group)
        rows[group]=row
        write(output/(group+".json"),row)
    left,right=(rows[g]["decisions"] for g in rows)
    first=None
    for index,(a,b) in enumerate(zip(left,right)):
        if a["action"]!=b["action"]:
            first=dict(index=index,left=a,right=b);break
    result=dict(first_action_divergence=first, records={g:dict(success=r["success"],digest=r["final_digest"]) for g,r in rows.items()})
    write(output/"summary.json",result)
    return result


def differential(output, baseline):
    protocol=load_protocol(PROTOCOL)
    case=protocol.data["STAGES"][1]["evaluation"][0]
    scenario=scenario_path(case["scenario"])
    brain=baseline/"brains/stage2_experienced.sebrain"
    rows=[]
    for label in ("left","right"):
        _,row,_=traced_episode(scenario,92101,brain,case["horizon"],output/(label+".jsonl"),boundary=True)
        rows.append(row)
    boundary=first_boundary(output/"left.jsonl",output/"right.jsonl")
    details=None
    if boundary:
        snapshots=[]
        for label in ("left","right"):
            _,_,observer=traced_episode(scenario,92101,brain,case["horizon"],output/(label+"_replay.jsonl"),boundary=True,detail_index=boundary["index"])
            snapshots.append(observer.detail)
        details=first_difference(*snapshots)
    result=dict(exact_records_equal=rows[0]==rows[1],first_boundary=boundary,details=details,
        record_differences=first_difference(*rows))
    write(output/"summary.json",result)
    return result


def _reverse_job(job):
    canonical,stage,case,seed,brain,output,baseline=job
    from experiments.v092.protocol import Curriculum
    protocol=Curriculum(canonical); output=Path(output);baseline=Path(baseline)
    mismatches=[];historical=[]
    for group in GROUPS:
        _,row=run_trial(protocol,case,seed,group,None if group=="FRESH_FULL" else brain,stage["id"])
        write(output/"forward"/(row["trial_id"]+".json"),row)
        old=json.loads((baseline/"trials"/(row["trial_id"]+".json")).read_text(encoding="utf-8"))
        if canonical_json(row)!=canonical_json(old): historical.append(dict(trial_id=row["trial_id"],differences=first_difference(old,row,limit=3)))
    for group in reversed(GROUPS):
        _,row=run_trial(protocol,case,seed,group,None if group=="FRESH_FULL" else brain,stage["id"])
        write(output/"reverse"/(row["trial_id"]+".json"),row)
        forward=json.loads((output/"forward"/(row["trial_id"]+".json")).read_text(encoding="utf-8"))
        if canonical_json(row)!=canonical_json(forward): mismatches.append(dict(trial_id=row["trial_id"],differences=first_difference(forward,row,limit=3)))
    return dict(mismatches=mismatches,historical=historical,comparisons=4)


def reverse_audit(output, baseline, workers=1):
    """Fresh/fresh comparison, never overwrite historical v0.9.2 trials."""
    protocol=load_protocol(PROTOCOL)
    results=json.loads((baseline/"results.json").read_text(encoding="utf-8"))
    jobs=[]
    for stage in protocol.data["STAGES"]:
        brain=baseline/results["checkpoints"][stage["id"]]["path"]
        for case in stage["evaluation"]:
            for seed in protocol.data["PROTOCOL"]["determinism_seeds"]:
                jobs.append((protocol.canonical,stage,case,seed,str(brain),str(output),str(baseline)))
    mismatches=[];historical=[];count=0
    def collect(rows):
        nonlocal count
        for row in rows:
            count+=row["comparisons"];mismatches.extend(row["mismatches"]);historical.extend(row["historical"])
            print(f"exact reverse audit {count}/64",flush=True)
    if workers==1: collect(map(_reverse_job,jobs))
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as pool: collect(pool.map(_reverse_job,jobs))
    result=dict(comparisons=count,exact_matches=count-len(mismatches),mismatches=mismatches,
        historical_comparisons=count,historical_mismatches=historical)
    write(output/"reverse_summary.json",result)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode",choices=("credit","stage2","differential","reverse","probe","hashsuite"),required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--baseline",default="results/v092/full")
    parser.add_argument("--scenario",default="scenarios/v092/stage4_scarcity_b.sescenario")
    parser.add_argument("--group",choices=tuple(GROUPS),default="FRESH_FULL")
    parser.add_argument("--brain")
    parser.add_argument("--horizon",type=float,default=.9)
    parser.add_argument("--record-only",action="store_true")
    parser.add_argument("--detail-index",type=int)
    parser.add_argument("--workers",type=int,choices=(1,2,3),default=1)
    args=parser.parse_args()
    output=Path(args.output).resolve();baseline=Path(args.baseline).resolve()
    if output==baseline or output.is_relative_to(baseline) or baseline.is_relative_to(output):
        raise ValueError("audit output must not overlap frozen baseline")
    if output.exists() and any(output.iterdir()): raise ValueError("use a new output directory")
    output.mkdir(parents=True,exist_ok=True)
    write(output/"provenance.json",dict(milestone="v0.9.3a",numeric_version="0.9.3",
        git_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        source_protocol_checksum=load_protocol(PROTOCOL).checksum,
        trial_record_format="v0.9.2",thresholds_changed=False))
    if args.mode=="hashsuite":
        hashseed_suite(output,baseline)
        return
    if args.mode=="probe":
        if args.record_only:
            runtime,_=instantiate(scenario_path(args.scenario),92101,args.group,args.brain)
            row=record(runtime,args.horizon,.02)
            write(output/"final_state.json",runtime.simulation.snapshot_data())
            write(output/"final_boundary_state.json",boundary_state(runtime))
        else:
            _,row,observer=traced_episode(scenario_path(args.scenario),92101,args.brain,args.horizon,
                output/"events.jsonl",group=args.group,boundary=True,detail_index=args.detail_index)
            if observer.detail is not None: write(output/"first_state.json",observer.detail)
            if observer.operations: write(output/"first_operations.json",observer.operations)
        write(output/"record.json",row)
        return
    if args.mode=="reverse": reverse_audit(output,baseline,args.workers)
    else: {"credit":credit_audit,"stage2":stage2_audit,"differential":differential}[args.mode](output,baseline)


if __name__=="__main__":main()
