"""Forensic planner stages and host crossings on an isolated production runtime."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from simulation.continuous import ContinuousRuntime
from telemetry.performance import HostProfiler
from telemetry.planner_profile import PlannerForensicProfiler
from telemetry.provenance import execution_provenance
from experiments.v093a.credit_trace import boundary_state, digest

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    parser.add_argument('--seconds',type=float,default=10.)
    parser.add_argument('--scenario')
    parser.add_argument('--brain')
    parser.add_argument('--reference-search',action='store_true')
    args=parser.parse_args()
    if args.scenario:
        from experiments.v092.runner import instantiate
        runtime,_=instantiate(args.scenario,6607,'EXPERIENCED_FULL' if args.brain else 'FRESH_FULL',args.brain)
    else:runtime=ContinuousRuntime(6607)
    core=runtime.simulation.core
    if args.reference_search:
        from heapq import nsmallest
        from types import MethodType
        from consciousness.planning_types import Plan
        scope=dict(nsmallest=nsmallest,Plan=Plan)
        fixture=Path(__file__).parents[1]/'tests/fixtures/planner_search_774ada8.py.txt'
        exec(compile(fixture.read_text(encoding='utf-8'),str(fixture),'exec'),scope)
        core.planner._search=MethodType(scope['_search'],core.planner)
    provenance=execution_provenance()
    before=core.backend.ffi_calls
    host=HostProfiler().attach(runtime)
    host.attach_native_calls(core.backend.engine)
    with PlannerForensicProfiler(core.planner) as profiler:runtime.run_until(args.seconds)
    planner_report=profiler.report()
    host.close()
    native_calls=sum(sample.count for name,sample in host.samples.items() if name.startswith('native_call.'))
    planner_calls=sum(sample.count for name,sample in host.samples.items() if name.startswith('planner_native_call.'))
    decisions=core.planner.plans_created+core.planner.plans_revised+core.planner.plans_abandoned
    report=dict(provenance=provenance,seconds=args.seconds,scenario=args.scenario,brain=args.brain,reference_search=args.reference_search,
                actions=runtime.actions_completed,events=runtime.scheduler_events_processed,
                causal_digest=digest(boundary_state(runtime)),ffi_calls=core.backend.ffi_calls-before,
                ffi_calls_per_completed_action=(core.backend.ffi_calls-before)/max(1,runtime.actions_completed),
                native_method_calls=native_calls,native_method_calls_per_completed_action=native_calls/max(1,runtime.actions_completed),
                decisions=decisions,planner_native_method_calls=planner_calls,
                planner_native_calls_per_decision=planner_calls/max(1,decisions),
                planner=planner_report,host=host.report())
    Path(args.output).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('planner','host','provenance')}))
