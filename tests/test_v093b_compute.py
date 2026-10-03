"""Exact host execution and profiling boundaries, no tolerance or timing gates."""
import pytest
import io
from simulation.continuous import ContinuousRuntime
from experiments.v093a.credit_trace import boundary_state
from telemetry.performance import HostProfiler, Sample
from experiments.v093a.determinism import BoundaryTrace

@pytest.mark.parametrize('mode',['AUTO','FORCE_CPU_SERIAL','FORCE_CPU_PARALLEL'])
def test_execution_modes_exact_causal_state(mode):
    serial=ContinuousRuntime(6607);other=ContinuousRuntime(6607)
    serial.simulation.core.backend.engine.set_compute_mode('FORCE_CPU_SERIAL')
    other.simulation.core.backend.engine.set_compute_mode(mode)
    serial.run_until(2.);other.run_until(2.)
    assert boundary_state(serial)==boundary_state(other)
    assert other.simulation.core.backend.full_graph_sync_calls==0

def test_host_profiler_exact_and_bounded():
    off=ContinuousRuntime(6607);on=ContinuousRuntime(6607)
    profiler=HostProfiler().attach(on)
    off.run_until(2.);on.run_until(2.);profiler.close()
    assert boundary_state(off)==boundary_state(on)
    assert profiler.report()['scheduler_dispatch']['count']==on.scheduler_events_processed
    sample=Sample()
    for i in range(10000):sample.add(float(i),1)
    assert len(sample.recent)==256 and sample.count==10000
    assert '_dispatch' not in vars(on)

def test_unknown_mode_errors_without_mutation():
    runtime=ContinuousRuntime(6607);engine=runtime.simulation.core.backend.engine
    before=boundary_state(runtime)
    with pytest.raises(ValueError,match='unknown host compute mode'):engine.set_compute_mode('invented')
    assert boundary_state(runtime)==before

def test_gpu_errors_clearly_or_matches_exactly():
    runtime=ContinuousRuntime(6607);engine=runtime.simulation.core.backend.engine
    try:engine.set_compute_mode('FORCE_GPU')
    except RuntimeError as error:
        assert 'FORCE_GPU unavailable' in str(error)
        pytest.skip(str(error))
    reference=ContinuousRuntime(6607)
    runtime.run_until(2.);reference.run_until(2.)
    assert boundary_state(reference)==boundary_state(runtime)

@pytest.mark.parametrize('mode',['AUTO','FORCE_CPU_PARALLEL','FORCE_GPU'])
def test_every_event_boundary_matches(mode):
    reference=ContinuousRuntime(6607);other=ContinuousRuntime(6607)
    reference.simulation.core.backend.engine.set_compute_mode('FORCE_CPU_SERIAL')
    try:other.simulation.core.backend.engine.set_compute_mode(mode)
    except RuntimeError as error:
        if mode=='FORCE_GPU':pytest.skip(str(error))
        raise
    left=io.StringIO();right=io.StringIO()
    reference.diagnostic_observer=BoundaryTrace(left)
    other.diagnostic_observer=BoundaryTrace(right)
    reference.run_until(1.);other.run_until(1.)
    assert left.getvalue()==right.getvalue(), 'first unequal event must be investigated; no tolerance'

def test_native_artifact_bytes_do_not_contain_backend_scratch_padding(tmp_path):
    a=ContinuousRuntime(6607);b=ContinuousRuntime(6607)
    a.simulation.core.backend.engine.set_compute_mode('FORCE_CPU_SERIAL')
    b.simulation.core.backend.engine.set_compute_mode('FORCE_CPU_PARALLEL')
    a.run_until(2.);b.run_until(2.)
    left=tmp_path/'serial.sebrain';right=tmp_path/'parallel.sebrain'
    a.simulation.save_brain(left);b.simulation.save_brain(right)
    assert left.read_bytes()==right.read_bytes()
