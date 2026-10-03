"""Capture native benchmark CSV, executable identity and execution provenance."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import tempfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from telemetry.provenance import execution_provenance

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--executable',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    executable=Path(args.executable).resolve();output=Path(args.output)
    provenance=execution_provenance()
    provenance['executable_sha256']=sha256(executable.read_bytes()).hexdigest()
    start=time.perf_counter()
    with tempfile.TemporaryFile(mode='w+t') as errors:
        process=subprocess.Popen([str(executable)],stdout=subprocess.PIPE,stderr=errors,text=True)
        with output.with_suffix('.csv').open('w',encoding='utf-8') as csv:
            for line in process.stdout:
                csv.write(line);csv.flush()
                print(line.strip(),flush=True)
        returncode=process.wait();errors.seek(0);stderr=errors.read()
    output.write_text(json.dumps(dict(provenance=provenance,executable=str(executable),
                     elapsed_seconds=time.perf_counter()-start,returncode=returncode,
                     stderr=stderr,csv=str(output.with_suffix('.csv'))),indent=2),encoding='utf-8')
    print(json.dumps(dict(returncode=returncode,csv=str(output.with_suffix('.csv')))))
    sys.exit(returncode)
