"""Manual extended v0.6.6 soak; intentionally excluded from normal pytest."""
import argparse,json,time
from config import Settings
from simulation.continuous import ContinuousRuntime
from simulation.long_life import LongLifeDiagnostics,validate_long_life_state


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--duration",type=float,default=50_000.);parser.add_argument("--windows",type=int,default=10);parser.add_argument("--seed",type=int,default=6606);args=parser.parse_args()
    runtime=ContinuousRuntime(args.seed,Settings(sensory_neural_enabled=True,neural_behavioral_participation=True));diagnostics=LongLifeDiagnostics();started=time.perf_counter();rows=[]
    for index in range(1,args.windows+1):
        target=args.duration*index/args.windows;before=time.perf_counter();runtime.run_until(target);validate_long_life_state(runtime);sample=diagnostics.sample(runtime).to_dict();sample["host_seconds"]=time.perf_counter()-before;rows.append(sample);print(json.dumps(sample,sort_keys=True),flush=True)
    print(json.dumps({"duration":args.duration,"host_seconds":time.perf_counter()-started,"windows":rows},sort_keys=True))


if __name__=="__main__":main()
