"""Host-only deterministic performance/equivalence measurements; no policy changes."""
import argparse
import cProfile
import json
from pathlib import Path
import statistics
import sys
import time
import importlib.util
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from telemetry.provenance import execution_provenance


def trial(seconds, observer=False, mode=None, profile=False, calibrated=False, legacy=False,
          scenario=None, brain=None, reference_search=False):
    from simulation.continuous import ContinuousRuntime
    from experiments.v093a.credit_trace import boundary_state, digest
    if scenario:
        from experiments.v092.runner import instantiate
        runtime,_=instantiate(scenario,6607,'EXPERIENCED_FULL' if brain else 'FRESH_FULL',brain)
    else:runtime = ContinuousRuntime(6607)
    if reference_search:
        from heapq import nsmallest
        from types import MethodType
        from consciousness.planning_types import Plan
        scope=dict(nsmallest=nsmallest,Plan=Plan)
        exec((Path(__file__).parents[1]/'tests/fixtures/planner_search_774ada8.py.txt').read_text(encoding='utf-8'),scope)
        runtime.simulation.core.planner._search=MethodType(scope['_search'],runtime.simulation.core.planner)
    engine = runtime.simulation.core.backend.engine
    if mode is not None:
        engine.set_compute_mode(mode)
    if calibrated:
        engine.calibrate_compute()
    window = None
    if observer:
        from main import create_native_observer
        window = create_native_observer(runtime)
        if legacy:window.set_legacy_brain_renderer(True)
        window.start()
        time.sleep(.3)  # startup excluded from throughput
    profiler = cProfile.Profile() if profile else None
    start = time.perf_counter()
    if profiler:
        profiler.enable()
    runtime.run_until(seconds)
    if profiler:
        profiler.disable()
    elapsed = time.perf_counter() - start
    frames = window.frames_rendered if window else 0
    presentation = list(window.presentation_telemetry) if window and hasattr(window,'presentation_telemetry') else None
    if window:
        window.stop()
    result = dict(worldtime_per_second=seconds/elapsed, elapsed_seconds=elapsed,
                  actions=runtime.actions_completed, events=runtime.scheduler_events_processed,
                  digest=digest(boundary_state(runtime)), frames=frames,
                  presentation_telemetry=presentation,
                  compute_telemetry=engine.compute_telemetry() if hasattr(engine,'compute_telemetry') else [],
                  decisions_per_second=(runtime.simulation.core.planner.plans_created+runtime.simulation.core.planner.plans_revised+runtime.simulation.core.planner.plans_abandoned)/elapsed,
                  planner_numeric_launches=getattr(engine,'planner_numeric_launches',None),
                  full_graph_sync_calls=runtime.simulation.core.backend.full_graph_sync_calls)
    if profiler:
        import pstats
        stats = pstats.Stats(profiler)
        result['profile'] = [dict(function=f'{key[0]}:{key[1]}:{key[2]}', calls=v[1],
                                  self_seconds=v[2], cumulative_seconds=v[3])
                             for key,v in sorted(stats.stats.items(), key=lambda row: -row[1][3])[:30]]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--seconds', type=float, default=10.)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--mode', choices=['AUTO','FORCE_CPU_SERIAL','FORCE_CPU_PARALLEL','FORCE_GPU'])
    parser.add_argument('--observer', action='store_true')
    parser.add_argument('--calibrated', action='store_true')
    parser.add_argument('--legacy', action='store_true')
    parser.add_argument('--scenario')
    parser.add_argument('--brain')
    parser.add_argument('--reference-search',action='store_true')
    parser.add_argument('--native-module')
    args = parser.parse_args()
    if args.native_module:
        native_path=Path(args.native_module).resolve()
        dll_directory=os.add_dll_directory(str(native_path.parent))
        spec=importlib.util.spec_from_file_location('consciousness._native_brain',native_path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        sys.modules['consciousness._native_brain']=module
    provenance = execution_provenance()
    options=dict(calibrated=args.calibrated,legacy=args.legacy,scenario=args.scenario,brain=args.brain,reference_search=args.reference_search)
    rows = [trial(args.seconds,args.observer,args.mode,**options) for _ in range(args.repeats)]
    result = dict(provenance=provenance, seconds=args.seconds, mode=args.mode, observer=args.observer,calibrated=args.calibrated,legacy=args.legacy,scenario=args.scenario,brain=args.brain,reference_search=args.reference_search,trials=rows,
                  median_worldtime_per_second=statistics.median(r['worldtime_per_second'] for r in rows),
                  profile_trial=trial(args.seconds,args.observer,args.mode,True,**options))
    Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('provenance','trials','profile_trial')}))

