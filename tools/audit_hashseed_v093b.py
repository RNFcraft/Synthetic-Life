"""Replay a declared episode and localize hashseed-dependent numeric operations."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from experiments.v092.runner import instantiate
from experiments.v093a.credit_trace import boundary_state, plain
from experiments.v093a.determinism import BoundaryTrace
from telemetry.provenance import execution_provenance

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brain',required=True)
    parser.add_argument('--scenario',default='scenarios/v092/train_adjacent_north.sescenario')
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--detail-index',type=int,default=50)
    parser.add_argument('--seconds',type=float,default=6.)
    args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise ValueError('use a new audit output directory')
    output.mkdir(parents=True)
    provenance=execution_provenance()
    runtime,_=instantiate(args.scenario,args.seed,'EXPERIENCED_FULL',args.brain)
    initial=boundary_state(runtime)
    from consciousness import memory
    original=memory._similarity
    similarities=[]
    def measured(a,b,weights=None):
        value=original(a,b,weights)
        left,right=set(a),set(b);union=left|right;table=weights or {}
        ordered=(sum(table.get(item,1.) for item in sorted(left&right))/
                 max(1e-9,sum(table.get(item,1.) for item in sorted(union)))) if union else 1.
        if value!=ordered:
            similarities.append(dict(time=runtime.world_time,a=plain(a),b=plain(b),
                                     value=value,canonical_diagnostic_value=ordered))
        return value
    memory._similarity=measured
    with (output/'events.jsonl').open('w',encoding='utf-8') as stream:
        trace=BoundaryTrace(stream,detail_index=args.detail_index)
        runtime.diagnostic_observer=trace
        try:runtime.run_until(args.seconds)
        finally:memory._similarity=original
    report=dict(provenance=provenance,brain=args.brain,seed=args.seed,scenario=args.scenario,
                initial=initial,detail=trace.detail,final=boundary_state(runtime),
                unordered_similarity_differences=similarities)
    (output/'audit.json').write_text(json.dumps(plain(report),indent=2),encoding='utf-8')
    print(json.dumps(dict(hashseed=provenance['hashseed'],unordered_similarity_differences=len(similarities))))
