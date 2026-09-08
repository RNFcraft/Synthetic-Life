from dataclasses import replace

import pytest

from config import Settings
from consciousness.native_engine import RuntimeEvent,RuntimeEventType
from simulation import ContinuousRuntime
from consciousness.core import SyntheticEntityCore
from consciousness.planning import DeliberativePlanner


def _one(runtime):
    event=runtime.scheduler.snapshot()[0]
    ready=runtime.scheduler.pop_ready(event.time)
    assert len(ready)==1
    runtime._process(ready[0])
    return event


def _semantic(runtime):
    frontier=runtime.simulation.core.continuous_frontier
    return (runtime.scheduler_state(),runtime.simulation.snapshot_data(),runtime.simulation.world.to_dict(),runtime.last_frame,
            None if frontier is None else runtime.simulation.core.planner.session_to_dict(frontier.session) if frontier.session else frontier.phase,
            runtime.actions_completed,runtime.cognition_wakes,runtime.cognition_continuations)


def test_scheduler_exposes_exactly_one_planner_iteration_per_continue():
    runtime=ContinuousRuntime(301);events=[];ticks=[];times=[]
    for _ in range(5):
        event=_one(runtime);events.append(event.type);ticks.append(runtime.simulation.core.cognitive_tick);times.append(event.time)
    assert events==[RuntimeEventType.SENSORY_CHANGE,RuntimeEventType.COGNITION_WAKE,RuntimeEventType.COGNITION_CONTINUE,RuntimeEventType.COGNITION_CONTINUE,RuntimeEventType.COGNITION_CONTINUE]
    assert ticks[2:]==[ticks[1]+1,ticks[1]+2,ticks[1]+3]
    assert times==[0.]*5
    assert runtime.simulation.core.continuous_frontier.committed
    assert len(runtime.simulation.core.trace.entries)==1


def test_continuous_trajectory_ignores_legacy_max_cycle_budget():
    low=ContinuousRuntime(302,replace(Settings(),max_deliberation_cycles=1));high=ContinuousRuntime(302,replace(Settings(),max_deliberation_cycles=12))
    low.run_until(.75);high.run_until(.75)
    assert low.cognition_continuations==high.cognition_continuations
    assert low.simulation.last_action==high.simulation.last_action
    assert low.simulation.core.trace.entries==high.simulation.core.trace.entries
    assert low.simulation.core.planner.cycles_last==3>low.simulation.core.settings.max_deliberation_cycles


def test_stale_generation_is_a_deterministic_noop():
    runtime=ContinuousRuntime(303);_one(runtime);_one(runtime)
    before=_semantic(runtime);tick=runtime.simulation.core.cognitive_tick
    runtime._process(RuntimeEvent(0.,999,RuntimeEventType.COGNITION_CONTINUE,runtime.cognition_generation-1))
    assert runtime.simulation.core.cognitive_tick==tick
    assert _semantic(runtime)==before


@pytest.mark.parametrize("events_before_save",(1,2,3,4,5,6))
def test_exact_save_load_at_every_cognition_frontier(tmp_path,events_before_save):
    original=ContinuousRuntime(304)
    for _ in range(events_before_save):_one(original)
    path=tmp_path/f"cognition-{events_before_save}.seworld";original.save_world(path);restored=ContinuousRuntime.load_world(path)
    assert _semantic(restored)==_semantic(original)
    for _ in range(12):
        left,right=_one(restored),_one(original)
        assert (left.time,left.id,left.type,left.payload)==(right.time,right.id,right.type,right.payload)
        assert _semantic(restored)==_semantic(original)


def test_action_and_observation_side_effects_commit_once():
    runtime=ContinuousRuntime(305);_one(runtime)
    occurrences=sum(p.occurrences for p in runtime.simulation.core.patterns.prototypes.values())
    trace_size=len(runtime.simulation.core.trace.entries)
    for _ in range(4):_one(runtime)
    assert sum(p.occurrences for p in runtime.simulation.core.patterns.prototypes.values())==occurrences
    assert trace_size==0 and len(runtime.simulation.core.trace.entries)==1
    assert runtime.simulation.core.planner.plan_steps_executed==1


def test_normal_continuous_path_never_calls_legacy_monoliths(monkeypatch):
    monkeypatch.setattr(SyntheticEntityCore,"step",lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError("legacy step called")))
    monkeypatch.setattr(DeliberativePlanner,"deliberate",lambda *args,**kwargs: (_ for _ in ()).throw(AssertionError("legacy deliberate called")))
    runtime=ContinuousRuntime(306);runtime.run_until(.45)
    assert runtime.actions_completed==3


def test_runaway_guard_raises_without_forcing_action(monkeypatch):
    runtime=ContinuousRuntime(307);_one(runtime);_one(runtime)
    monkeypatch.setattr(runtime.simulation.core.planner,"continue_continuous",lambda core,session: False)
    with pytest.raises(RuntimeError,match="event guard exceeded"):runtime.run_to_quiescence(guard=4)
    assert runtime.actions_completed==0 and not runtime.simulation.core.continuous_frontier.committed


def test_render_and_host_work_between_continuations_are_observational():
    plain=ContinuousRuntime(308);sampled=ContinuousRuntime(308)
    for _ in range(18):
        _one(plain);sampled.render_snapshot()
        sum(i*i for i in range(2000))
        _one(sampled);sampled.render_snapshot()
        assert _semantic(sampled)==_semantic(plain)


def test_save_is_observational_during_unfinished_cognition(tmp_path):
    baseline=ContinuousRuntime(309);saved=ContinuousRuntime(309);loaded=ContinuousRuntime(309)
    for runtime in (baseline,saved,loaded):
        for _ in range(3):_one(runtime)
    saved.save_world(tmp_path/"observed-only.seworld")
    loaded.save_world(tmp_path/"restored.seworld");loaded=ContinuousRuntime.load_world(tmp_path/"restored.seworld")
    for _ in range(15):
        _one(baseline);_one(saved);_one(loaded)
        assert _semantic(saved)==_semantic(baseline)==_semantic(loaded)
