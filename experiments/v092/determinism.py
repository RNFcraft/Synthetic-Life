"""Independent-process hashseed check for the serialized checkpoint input."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from simulation.scenario import canonical_json
from .protocol import ROOT,load_protocol,save_protocol


def hashseed_probe(protocol,output,results):
    brain=Path(output)/results["checkpoints"]["stage_2"]["path"]
    exact_protocol=Path(output)/"determinism-protocol.securriculum"
    save_protocol(protocol.data,exact_protocol)
    command=[sys.executable,"-B","-m","experiments.v092.determinism","--protocol",str(exact_protocol.resolve()),"--brain",str(brain)]
    values=[]
    for seed in ("1","777"):
        env={**os.environ,"PYTHONHASHSEED":seed}
        values.append(json.loads(subprocess.check_output(command,cwd=ROOT,env=env,text=True)))
    identical=canonical_json(values[0])==canonical_json(values[1])
    from experiments.scenario_runner import _write_result
    for seed,value in zip((1,777),values):
        _write_result(Path(output)/f'hashseed-{seed}.json',value)
    return dict(seeds=[1,777],groups=["FRESH_FULL","EXPERIENCED_FULL"],identical=identical)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--protocol",required=True);parser.add_argument("--brain",required=True)
    args=parser.parse_args();protocol=load_protocol(args.protocol)
    from .runner import run_trial
    case=protocol.data["STAGES"][1]["evaluation"][0];seed=protocol.data["PROTOCOL"]["evaluation_seeds"][0]
    rows=[]
    for group in ("FRESH_FULL","EXPERIENCED_FULL"):
        _,row=run_trial(protocol,case,seed,group,None if group=="FRESH_FULL" else args.brain,"stage_2")
        rows.append(row)
    print(canonical_json(rows))


if __name__=="__main__":main()
