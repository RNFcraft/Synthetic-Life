"""Focused SpatialMemory indexed-vs-legacy retrieval microbenchmark."""
import argparse,json,random
from pathlib import Path
from time import perf_counter

from config import Settings
from consciousness.memory import PersistentStructureMemory,SpatialMemory


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--memories",type=int,default=10000);parser.add_argument("--queries",type=int,default=200);parser.add_argument("--output",default="runs/v052-memory-index.json");args=parser.parse_args()
    rng=random.Random(5203);memory=SpatialMemory(Settings());tokens=(("occupied",1),("state",1),("appearance",1),("state",2))
    for i in range(1,args.memories+1):
        features=tuple(sorted(rng.sample(tokens,rng.randrange(0,3))));state=tuple(rng.randrange(8) for _ in range(rng.randrange(0,4)))
        memory.structures[i]=PersistentStructureMemory(i,100000+i,features,200000+i%997,(float(i%7),float(i%5)),state,rng.random(),rng.randrange(500))
    queries=[]
    for tick in range(args.queries):queries.append((tuple(sorted(rng.sample(tokens,rng.randrange(0,3)))),tuple(rng.randrange(8) for _ in range(rng.randrange(0,4))),200000+rng.randrange(1200),500+tick))
    started=perf_counter();legacy=[memory._match_structure_legacy(*query) for query in queries];legacy_seconds=perf_counter()-started
    candidate_counts=[];started=perf_counter();indexed=[]
    for query in queries:indexed.append(memory._match_structure(*query));candidate_counts.append(memory.last_retrieval_candidates)
    indexed_seconds=perf_counter()-started
    assert [(x.id if x else None) for x in indexed]==[(x.id if x else None) for x in legacy]
    result={"retained_memories":args.memories,"queries":args.queries,"legacy_seconds":legacy_seconds,"indexed_seconds":indexed_seconds,"speedup":legacy_seconds/max(indexed_seconds,1e-12),"mean_candidates":sum(candidate_counts)/len(candidate_counts),"max_candidates":max(candidate_counts,default=0)}
    Path(args.output).write_text(json.dumps(result,indent=2),encoding="utf8");print(json.dumps(result,indent=2))


if __name__=="__main__":main()
