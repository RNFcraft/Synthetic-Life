"""Reproduce the locked 22-episode production prefix with an optional base native module."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--reference-module')
parser.add_argument('--output',required=True)
args=parser.parse_args()
if args.reference_module:
    spec=importlib.util.spec_from_file_location('consciousness._native_brain',args.reference_module)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original=module.NativeBrainEngine
    class CompatibleEngine:
        # Adapt only the new host publication argument; every causal call delegates.
        def __init__(self,*args,**kwargs):self.inner=original(*args,**kwargs)
        def __getattr__(self,name):return getattr(self.inner,name)
        def publish_brain_snapshot(self,time,tick,generation,active,force=True):
            return self.inner.publish_brain_snapshot(time,tick,generation,active)
    module.NativeBrainEngine=CompatibleEngine
    sys.modules['consciousness._native_brain']=module

from experiments.v092.protocol import load_protocol
from experiments.v092.runner import train_stage
from experiments.v093a.credit_trace import digest

output=Path(args.output).resolve()
for frozen in (ROOT/'results/v092',ROOT/'results/v093a'):
    if output==frozen or output.is_relative_to(frozen) or frozen.is_relative_to(output):
        raise ValueError('differential output must not overlap historical research artifacts')
if output.exists() and any(output.iterdir()):raise ValueError('use a new differential output directory')
output.mkdir(parents=True,exist_ok=True)
protocol=load_protocol(ROOT/'experiments/protocols/v092_survival.securriculum')
stage=protocol.data['STAGES'][0];stage['training'][0]['episodes']=22
brain,rows=train_stage(protocol,stage,output,None)
records=[json.loads((output/row['trajectory_reference']).read_text(encoding='utf-8')) for row in rows]
summary=dict(hashseed=os.environ.get('PYTHONHASHSEED','random'),records_digest=digest(records),
             episode_consumptions=[row['consumptions'] for row in rows],
             final_episode_has_consumption=bool(records[-1]['consumptions']))
(output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary))
