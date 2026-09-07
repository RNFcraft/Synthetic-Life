"""Growing full-Entity benchmark with bounded checkpoint output."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

from simulation import Simulation


def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=123);parser.add_argument('--steps',type=int,default=5000);parser.add_argument('--output',default='runs/v052-entity-benchmark.json');args=parser.parse_args()
    sim=Simulation(args.seed,backend='native');checkpoints=sorted({x for x in (100,1000,5000,10000,args.steps) if x<=args.steps});rows=[];previous_step=0;previous_time=perf_counter();started=previous_time;previous_ffi=0;previous_proxies=0
    for step in range(1,args.steps+1):
        sim.step()
        if step not in checkpoints:continue
        now=perf_counter();window=now-previous_time;backend=sim.core.backend;engine=backend.engine
        ffi_window=backend.ffi_calls-previous_ffi;proxy_window=backend.relation_proxy_objects_created-previous_proxies;window_actions=step-previous_step;memory=sim.core.memory
        row={'step':step,'wall_seconds':now-started,'window_seconds':window,'window_actions_per_second':window_actions/window,'cognits_total':engine.cognit_count,'cognits_live':engine.live_cognit_count,'relations':engine.relation_count,'provisional':engine.provisional_count,'consolidated':engine.consolidated_count,'active':len(sim.core.last_wave.active_ids),'ffi_calls':backend.ffi_calls,'ffi_calls_window':ffi_window,'ffi_calls_per_action':backend.ffi_calls/step,'ffi_calls_per_action_window':ffi_window/window_actions,'receive_calls':backend.receive_calls,'field_write_calls':backend.field_write_calls,'state_read_calls':backend.state_read_calls,'relation_proxies':backend.relation_proxy_objects_created,'relation_proxies_window':proxy_window,'relation_proxies_per_action':backend.relation_proxy_objects_created/step,'relation_proxies_per_action_window':proxy_window/window_actions,'memory_count':len(memory.structures),'retrieval_candidate_count':memory.last_retrieval_candidates,'retrieval_total_count':memory.last_retrieval_total,'graph_logical_bytes':engine.logical_bytes,'graph_reserved_bytes':engine.reserved_bytes,'full_graph_sync_calls':backend.full_graph_sync_calls}
        rows.append(row);print(json.dumps(row),flush=True);previous_step=step;previous_time=now;previous_ffi=backend.ffi_calls;previous_proxies=backend.relation_proxy_objects_created
        Path(args.output).write_text(json.dumps({'seed':args.seed,'steps':args.steps,'checkpoints':rows},indent=2),encoding='utf-8')


if __name__=='__main__':main()
