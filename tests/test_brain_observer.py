from simulation import ContinuousRuntime
import time


def _causal(runtime):
    core=runtime.simulation.core
    engine=core.backend.engine
    ids=list(range(engine.cognit_count))
    return (runtime.scheduler_state(),runtime.simulation.snapshot_data(),core.cognitive_tick,
            tuple(engine.cognit_state_full(ids)),engine.relation_count,
            runtime.actions_completed,runtime.maintenance_ordinal)


def test_native_brain_snapshot_has_real_graph_and_activity():
    runtime=ContinuousRuntime(seed=531)
    runtime.run_until(1.0)
    runtime.publish_brain_snapshot()
    snap=runtime.simulation.core.backend.engine.latest_brain_snapshot()
    assert snap[0]==runtime.world_time and snap[1]==runtime.simulation.core.cognitive_tick
    nodes,edges=snap[3],snap[4]
    assert len(nodes)==runtime.simulation.core.backend.engine.live_cognit_count
    assert len(edges)==runtime.simulation.core.backend.engine.relation_count
    assert {row[0]+1 for row in nodes if row[1]>0}.issuperset(runtime.simulation.core.last_wave.active_ids)


def test_brain_publication_is_causally_inert_and_not_full_graph_sync():
    plain=ContinuousRuntime(seed=532);observed=ContinuousRuntime(seed=532)
    plain.run_until(2.0)
    for step in range(1,21):
        observed.run_until(step/10)
        observed.publish_brain_snapshot()
    assert _causal(observed)==_causal(plain)
    assert observed.simulation.core.backend.full_graph_sync_calls==0


def test_brain_snapshots_are_immutable_latest_only():
    runtime=ContinuousRuntime(seed=533);engine=runtime.simulation.core.backend.engine
    runtime.publish_brain_snapshot();old=engine.latest_brain_snapshot()
    runtime.run_until(.5);runtime.publish_brain_snapshot();new=engine.latest_brain_snapshot()
    assert old[0]==0.0 and new[0]==.5 and old!=new


def test_same_snapshot_is_not_rebuilt_each_render_frame():
    runtime=ContinuousRuntime(seed=534);runtime.publish_brain_snapshot()
    observer=runtime.simulation.world.native.create_brain_observer(runtime.simulation.core.backend.engine)
    assert observer.start()
    deadline=time.monotonic()+5
    while observer.frames_rendered<10 and time.monotonic()<deadline:time.sleep(.01)
    before=(observer.frames_rendered,observer.brain_snapshot_rebuilds)
    time.sleep(.1);middle=(observer.frames_rendered,observer.brain_snapshot_rebuilds)
    runtime.publish_brain_snapshot();deadline=time.monotonic()+5
    while observer.brain_snapshot_rebuilds<middle[1]+1 and time.monotonic()<deadline:time.sleep(.01)
    after=observer.brain_snapshot_rebuilds;observer.stop()
    assert middle[0]>before[0] and middle[1]==before[1] and after==middle[1]+1
