"""Inert observer and exact differential regression coverage."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys

from experiments.v092.runner import instantiate
from experiments.v092.recorder import record
from experiments.v093a.credit_trace import CreditTrace, attach, boundary_state, digest
from experiments.v093a.determinism import first_boundary, first_difference
from consciousness.native_engine import EventScheduler, RuntimeEventType

SCENARIO=Path(__file__).parents[1]/"scenarios/v092/train_adjacent_north.sescenario"


def test_trace_disabled_and_stored_reads_inert():
    runtime,_=instantiate(SCENARIO,92001)
    assert runtime.diagnostic_observer is None
    assert runtime.simulation.core.diagnostic_observer is None
    runtime.run_until(.6)
    state=boundary_state(runtime)
    for _ in range(3): assert boundary_state(runtime)==state
    assert runtime.simulation.core.backend.full_graph_sync_calls==0


def test_trace_equivalence_rng_scheduler_graph_digest():
    off,_=instantiate(SCENARIO,92001)
    on,_=instantiate(SCENARIO,92001)
    stream=io.StringIO();sink=CreditTrace(stream);attach(on,sink)
    a=record(off,1.2,.02);b=record(on,1.2,.02)
    assert a==b
    assert boundary_state(off)==boundary_state(on)
    assert off.simulation.rng.getstate()==on.simulation.rng.getstate()
    assert off.scheduler_state()==on.scheduler_state()
    assert on.simulation.core.backend.full_graph_sync_calls==0
    rows=[json.loads(line) for line in stream.getvalue().splitlines()]
    assert rows and sink.rows==len(rows)
    assert all("reasons" in candidate for row in rows if row["kind"]=="learning" for candidate in row["candidates"])


def test_trace_streams_without_retained_event_history():
    class CounterStream:
        def __init__(self):self.count=0
        def write(self,value): self.count+=1
    stream=CounterStream();sink=CreditTrace(stream)
    for index in range(10000):sink.write(dict(index=index))
    assert stream.count==sink.rows==10000
    assert vars(sink)==dict(stream=stream,rows=10000)
    assert digest({"b":2,"a":1})==digest({"a":1,"b":2})


def test_first_difference_preserves_last_bit_and_first_event(tmp_path):
    a=tmp_path/"a.jsonl";b=tmp_path/"b.jsonl"
    a.write_text('{"index":0}\n{"value":1.0}\n')
    b.write_text('{"index":0}\n{"value":1.0000000000000002}\n')
    assert first_boundary(a,b)["index"]==1
    diff=first_difference({"value":1.0},{"value":1.0000000000000002})
    assert diff[0]["right"]!=diff[0]["left"]


def test_equal_time_scheduler_order_is_instance_owned():
    for _ in range(2):
        scheduler=EventScheduler()
        for kind in (RuntimeEventType.MAINTENANCE,RuntimeEventType.SENSORY_CHANGE,RuntimeEventType.COGNITION_WAKE):scheduler.schedule(0.,kind)
        rows=scheduler.pop_ready(0.)
        assert [e.id for e in rows]==[1,2,3]
        assert [e.type for e in rows]==[RuntimeEventType.MAINTENANCE,RuntimeEventType.SENSORY_CHANGE,RuntimeEventType.COGNITION_WAKE]


def test_exact_old_selectivity_failure_across_hashseeds():
    # This physical trial first differed at event 1243 / t=25.95 before the
    # canonical matched traversal fix. No actions or supported rho are injected.
    code="""
import json
from experiments.v092.runner import instantiate
from experiments.v092.recorder import record
r,_=instantiate('scenarios/v092/stage4_scarcity_b.sescenario',92101)
row=record(r,30.,.02)
print(json.dumps(dict(record=row,selectivity=r.simulation.core._selectivity_sum),sort_keys=True))
"""
    results=[]
    for seed in ("1","777"):
        output=subprocess.check_output([sys.executable,"-B","-c",code],
            cwd=SCENARIO.parents[2],env={**os.environ,"PYTHONHASHSEED":seed},text=True)
        results.append(json.loads(output))
    assert results[0]==results[1]


def test_trace_with_transferred_brain_exact_equivalence(tmp_path):
    source,_=instantiate(SCENARIO,92001)
    source.run_until(.9)
    brain=tmp_path/"small.sebrain";source.simulation.save_brain(brain)
    off,_=instantiate(SCENARIO,92002,"EXPERIENCED_FULL",brain)
    on,_=instantiate(SCENARIO,92002,"EXPERIENCED_FULL",brain)
    sink=CreditTrace(io.StringIO());attach(on,sink)
    assert record(off,.9,.02)==record(on,.9,.02)
    assert boundary_state(off)==boundary_state(on)
