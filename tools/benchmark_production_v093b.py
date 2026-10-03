"""Sequential isolated production modes; startup and cProfile are separate."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brain',required=True)
    parser.add_argument('--native-module',required=True)
    parser.add_argument('--output-dir',required=True)
    parser.add_argument('--calibrated-auto',action='store_true')
    args=parser.parse_args()
    output=Path(args.output_dir)
    if output.exists():raise ValueError('use a new production benchmark output directory')
    output.mkdir(parents=True)
    modes=['FORCE_CPU_SERIAL','FORCE_CPU_PARALLEL','FORCE_GPU','AUTO']
    failures=[]
    for workload in ('small','trained'):
        for mode in modes:
            for observer in (False,True):
                name=f'{workload}-{mode}-{"observer" if observer else "headless"}'
                command=[sys.executable,str(ROOT/'tools/benchmark_v093b.py'),'--output',str(output/(name+'.json')),
                         '--seconds','10' if workload=='small' else '6','--repeats','5',
                         '--mode',mode,'--native-module',args.native_module]
                if workload=='trained':command+=['--scenario','scenarios/v092/train_adjacent_north.sescenario','--brain',args.brain]
                if observer:command+=['--observer']
                if mode=='AUTO' and args.calibrated_auto:command+=['--calibrated']
                result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,
                                      env={**os.environ,'PYTHONHASHSEED':'1'})
                (output/(name+'.log')).write_text(result.stdout+result.stderr,encoding='utf-8')
                print(json.dumps(dict(workload=workload,mode=mode,observer=observer,returncode=result.returncode)),flush=True)
                if result.returncode:failures.append(name)
    (output/'summary.json').write_text(json.dumps(dict(failures=failures),indent=2),encoding='utf-8')
    if failures:sys.exit(1)
