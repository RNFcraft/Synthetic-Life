"""New representative matrix; never substitutes for missing historical research."""
import argparse
from hashlib import sha256
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def run_case(scenario,brain,seed,seconds,mode,observer,calibrated_auto=False):
    from experiments.v092.runner import instantiate
    from experiments.v093a.credit_trace import boundary_state,digest
    from experiments.v093a.determinism import BoundaryTrace
    runtime,_=instantiate(scenario,seed,'EXPERIENCED_FULL' if brain else 'FRESH_FULL',brain)
    engine=runtime.simulation.core.backend.engine
    engine.set_compute_mode(mode)
    if calibrated_auto and mode=='AUTO':engine.calibrate_planner_compute()
    stream=io.StringIO();trace=BoundaryTrace(stream);runtime.diagnostic_observer=trace
    window=None
    if observer:
        from main import create_native_observer
        window=create_native_observer(runtime)
        window.start();time.sleep(.05)
    try:runtime.run_until(seconds)
    finally:
        if window:window.stop()
    with tempfile.TemporaryDirectory() as temporary:
        path=Path(temporary)/'brain.sebrain';runtime.simulation.save_brain(path)
        artifact=path.read_bytes()
    return dict(event_stream=sha256(stream.getvalue().encode()).hexdigest(),events=trace.index,
                final_causal_digest=digest(boundary_state(runtime)),artifact_bytes_sha256=sha256(artifact).hexdigest(),
                artifact_size=len(artifact),world_digest=digest(runtime.simulation.world.to_dict()),
                physiology_digest=digest(runtime.simulation.physiology.to_dict()),scheduler_digest=digest(runtime.scheduler_state()),
                full_graph_sync_calls=runtime.simulation.core.backend.full_graph_sync_calls,
                observer_frames=window.frames_rendered if window else 0,
                planner_backend=engine.compute_telemetry()[3]['backend'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brain',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--native-module')
    parser.add_argument('--seconds',type=float,default=2.)
    parser.add_argument('--calibrated-auto',action='store_true')
    args=parser.parse_args()
    if args.native_module:
        module_path=Path(args.native_module).resolve()
        dll_directory=os.add_dll_directory(str(module_path.parent))
        spec=importlib.util.spec_from_file_location('consciousness._native_brain',module_path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        sys.modules['consciousness._native_brain']=module
    from consciousness.native_engine import NativeBrainEngine
    from telemetry.provenance import execution_provenance
    provenance=execution_provenance()
    if args.native_module:provenance['loaded_native_module_sha256']=sha256(module_path.read_bytes()).hexdigest()
    probe=NativeBrainEngine()
    modes=['FORCE_CPU_SERIAL','FORCE_CPU_PARALLEL','AUTO']
    try:probe.set_compute_mode('FORCE_GPU');modes.append('FORCE_GPU');gpu_status='available'
    except RuntimeError as error:gpu_status=str(error)
    scenarios=['train_adjacent_north','train_one_move_north','train_consolidate_east','stage3_west_a',
               'stage4_scarcity_a','stage4_scarcity_b','counterfactual_same_appearance','stage3_north_translated']
    # Keep all scenario selection explicit and tracked, independent of artifacts.
    missing=[name for name in scenarios if not (ROOT/f'scenarios/v092/{name}.sescenario').is_file()]
    if missing:raise ValueError('missing declared scenarios: '+str(missing))
    rows=[];failures=[]
    for scenario_index,scenario in enumerate(scenarios):
        for trained in (False,True):
            identity=dict(scenario=f'scenarios/v092/{scenario}.sescenario',trained=trained,seed=92001+scenario_index)
            reference=None
            for mode in modes:
                for observer in (False,True):
                    result=run_case(identity['scenario'],args.brain if trained else None,identity['seed'],args.seconds,mode,observer,args.calibrated_auto)
                    causal={k:v for k,v in result.items() if k not in ('observer_frames','planner_backend')}
                    if reference is None:reference=causal
                    exact=causal==reference
                    if not exact:failures.append(dict(**identity,mode=mode,observer=observer))
                    rows.append(dict(**identity,mode=mode,observer=observer,exact=exact,**result))
            print(json.dumps(dict(**identity,completed=len(rows),failures=len(failures))),flush=True)
    result=dict(provenance=provenance,brain=str(args.brain),brain_sha256=sha256(Path(args.brain).read_bytes()).hexdigest(),
                representative_cases=16,seconds=args.seconds,gpu_status=gpu_status,calibrated_auto=args.calibrated_auto,
                historical_64_case_status='not rerun: frozen results/v092/full brain checkpoint absent',
                rows=rows,failures=failures)
    Path(args.output).write_text(json.dumps(result,indent=2),encoding='utf-8')
    if failures:sys.exit(1)
