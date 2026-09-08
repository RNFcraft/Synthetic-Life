import pytest
from consciousness.native_engine import EventScheduler,RuntimeEvent,RuntimeEventType
from simulation import ContinuousRuntime

def test_scheduler_subsecond_same_time_order_and_monotonicity():
    q=EventScheduler();a=q.schedule(.25,RuntimeEventType.EXTERNAL_INPUT,7);b=q.schedule(.10,RuntimeEventType.SENSORY_CHANGE);c=q.schedule(.25,RuntimeEventType.MAINTENANCE)
    assert [(e.time,e.id) for e in q.pop_ready(.25)]==[(.10,b),(.25,a),(.25,c)];assert q.now==.25
    with pytest.raises(ValueError):q.schedule(.2,RuntimeEventType.COGNITION_WAKE)

def test_event_sequence_is_independent_of_time_and_queue_restores():
    q=EventScheduler();q.schedule(.5,RuntimeEventType.EXTERNAL_INPUT,1);q.schedule(.5,RuntimeEventType.EXTERNAL_INPUT,2);events=q.snapshot();restored=EventScheduler();restored.restore(0.,q.next_id,events)
    assert [(e.time,e.id,e.payload) for e in restored.pop_ready(.5)]==[(e.time,e.id,e.payload) for e in q.pop_ready(.5)]

def test_multiple_action_sensory_cognition_cycles_inside_one_second():
    runtime=ContinuousRuntime(8);runtime.run_until(.99)
    assert runtime.actions_completed>=6 and runtime.cognition_wakes>=7 and runtime.observation_ordinal>=7
    assert runtime.world_time==.99 and runtime.simulation.world.native.time_state()[0]==.99

def test_cognition_wakes_then_becomes_quiescent_without_fixed_cycle_budget():
    runtime=ContinuousRuntime(9);processed=runtime.run_to_quiescence()
    assert processed==5 and runtime.cognition_wakes==1 and runtime.cognition_continuations==3
    assert runtime.simulation.core.planner.cycles_last==3 and runtime.scheduler.snapshot()[0].time==pytest.approx(.15)

def test_render_sampling_frequency_cannot_change_runtime_state():
    states=[]
    for samples in (0,30,60,240):
        runtime=ContinuousRuntime(10)
        for i in range(samples):runtime.render_snapshot()
        runtime.run_until(.9)
        for i in range(samples):runtime.render_snapshot()
        states.append((runtime.simulation.snapshot_data(),runtime.scheduler_state(),runtime.actions_completed))
    assert all(x==states[0] for x in states[1:])

def test_continuous_seworld_restores_pending_events_exactly(tmp_path):
    uninterrupted=ContinuousRuntime(11);uninterrupted.run_until(12.437);path=tmp_path/"continuous.seworld";uninterrupted.save_world(path);restored=ContinuousRuntime.load_world(path)
    assert restored.scheduler_state()==uninterrupted.scheduler_state()
    uninterrupted.run_until(13.2);restored.run_until(13.2)
    assert restored.scheduler_state()==uninterrupted.scheduler_state();assert restored.simulation.snapshot_data()==uninterrupted.simulation.snapshot_data()

@pytest.mark.parametrize("boundary",(12.001,12.149,12.437,12.999))
def test_continuous_save_boundary_event_by_event_matrix(tmp_path,boundary):
    original=ContinuousRuntime(27);original.run_until(boundary);path=tmp_path/f"{boundary}.seworld";original.save_world(path);restored=ContinuousRuntime.load_world(path)
    for _ in range(12):
        left=original.scheduler.snapshot()[0];right=restored.scheduler.snapshot()[0]
        assert (left.time,left.id,left.type,left.payload)==(right.time,right.id,right.type,right.payload)
        for event in original.scheduler.pop_ready(left.time):original._process(event)
        for event in restored.scheduler.pop_ready(right.time):restored._process(event)
        assert original.scheduler_state()==restored.scheduler_state();assert original.simulation.world.to_dict()==restored.simulation.world.to_dict();assert original.last_frame==restored.last_frame
        assert original.simulation.core.last_wave==restored.simulation.core.last_wave;assert original.simulation.core.patterns.prototypes==restored.simulation.core.patterns.prototypes;assert original.simulation.core.state.goal==restored.simulation.core.state.goal;assert original.simulation.last_action==restored.simulation.last_action

@pytest.mark.parametrize("events_to_process",(1,2,3))
def test_save_around_action_sensory_and_cognition_boundaries(tmp_path,events_to_process):
    original=ContinuousRuntime(41)
    for _ in range(events_to_process):
        event=original.scheduler.snapshot()[0]
        for ready in original.scheduler.pop_ready(event.time):original._process(ready)
    path=tmp_path/f"frontier-{events_to_process}.seworld";original.save_world(path);restored=ContinuousRuntime.load_world(path)
    for _ in range(6):
        a=original.scheduler.snapshot()[0];b=restored.scheduler.snapshot()[0];assert (a.time,a.id,a.type,a.payload)==(b.time,b.id,b.type,b.payload)
        for ready in original.scheduler.pop_ready(a.time):original._process(ready)
        for ready in restored.scheduler.pop_ready(b.time):restored._process(ready)
        assert original.simulation.snapshot_data()==restored.simulation.snapshot_data()
