from time import perf_counter
import json
from pathlib import Path
from consciousness.native_engine import NativeBrainEngine
from consciousness.relation import RelationType
from world import ActionType

def timed(fn,repeats=20):
    start=perf_counter()
    for _ in range(repeats):fn()
    return (perf_counter()-start)*1e6/repeats

def main():
    engine=NativeBrainEngine();engine.add_cognits(100_000,0.,.05,.5)
    for source in range(100_000):
        for degree in range(4):engine.add_relation(source,(source*4+degree+1)%100_000,RelationType.SEQUENTIAL.value,0,.8,.8,.7)
    active=list(range(1000));[engine.set_activity(i,1.) for i in active];actions=list(ActionType)
    prediction={str(n):timed(lambda n=n:engine.predict_actions_batch(active,[a.value for a in actions[:n]]),10) for n in (1,4,17)}
    compact=engine.predict_compact(active,ActionType.MOVE_UP.value)
    evidence={}
    for size in (8,100,1000,5000):
        e=NativeBrainEngine(1);e.add_cognits(size*2);before=list(range(size));after=list(range(size,2*size));insert=timed(lambda:e.update_transition_evidence(before,ActionType.MOVE_UP.value,after),1)
        query=timed(lambda:e.transition_metrics(0,size,ActionType.MOVE_UP.value),100)
        eviction=timed(lambda:e.update_transition_evidence(before,ActionType.MOVE_DOWN.value,after),1)
        evidence[str(size)]={"insertion_us":insert,"eviction_plus_insertion_us":eviction,"support_query_us":query,"source_events":e.evidence_stats[0],"target_events":e.evidence_stats[1],"candidate_pairs_represented":e.evidence_stats[2],"evidence_bytes":e.evidence_stats[3]}
    result={"prediction_batch_latency_us":prediction,"compact_result":{"ids_dtype":str(compact[0].dtype),"values_dtype":str(compact[1].dtype),"count":len(compact[0])},"evidence_update":evidence,"graph":{"cognits":engine.cognit_count,"relations":engine.relation_count,"logical_bytes":engine.logical_bytes,"reserved_bytes":engine.reserved_bytes},"note":"Native substrate/FFI benchmark, not full Entity throughput."}
    Path("runs/v052-native-hardening.json").write_text(json.dumps(result,indent=2),encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
