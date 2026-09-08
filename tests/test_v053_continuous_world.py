from dataclasses import replace
from pathlib import Path

import pytest

from config import Settings
from consciousness.native_engine import EventScheduler, RuntimeEventType
from simulation import ContinuousRuntime
from world import ActionType
from world.native_world import NativeWorld
from persistence import load_container, save_container


def _spawn_events(runtime):
    return [(e.time, e.id) for e in runtime.scheduler.snapshot() if e.type == RuntimeEventType.WORLD_SPAWN]

def _behavior_state(runtime):
    time, sequence=runtime.simulation.world.native.time_state()
    frontier=runtime.simulation.core.continuous_frontier
    return (runtime.scheduler_state(),runtime.simulation.event_sequence.value,time,sequence,runtime.simulation.rng.getstate(),runtime.simulation.world.to_dict(),runtime.maintenance_ordinal,runtime.cognition_generation,runtime.actions_completed,None if frontier is None else (frontier.generation,frontier.phase,frontier.committed))

def _roundtrip(runtime,tmp_path,name="world"):
    path=Path(tmp_path)/f"{name}.seworld";runtime.save_world(path);return ContinuousRuntime.load_world(path,runtime.simulation.settings)


def test_continuous_world_never_uses_legacy_heartbeat(monkeypatch):
    monkeypatch.setattr(NativeWorld, "world_tick", lambda *_: (_ for _ in ()).throw(AssertionError("legacy heartbeat")))
    settings = replace(Settings(), object_count=0, max_objects=2, spawn_interval_min=1, spawn_interval_max=1)
    runtime = ContinuousRuntime(700, settings)
    runtime.run_until(2.1)
    assert runtime.simulation.world.world_tick_count == 0
    assert len(runtime.simulation.world.objects) == 2


def test_spawn_deadline_is_absolute_and_partition_invariant():
    settings = replace(Settings(), object_count=0, max_objects=4, spawn_interval_min=2, spawn_interval_max=2)
    whole, partitioned = ContinuousRuntime(701, settings), ContinuousRuntime(701, settings)
    whole.run_until(8.0)
    for point in (1.0, 3.5, 6.25, 8.0):
        partitioned.run_until(point)
    assert partitioned.scheduler_state() == whole.scheduler_state()
    assert partitioned.simulation.world.to_dict() == whole.simulation.world.to_dict()
    assert partitioned.simulation.rng.getstate() == whole.simulation.rng.getstate()


def test_subsecond_spawn_advances_native_time_and_event_sequence():
    runtime = ContinuousRuntime(702, replace(Settings(), object_count=0, max_objects=2))
    event_id = runtime.scheduler.schedule(.437, RuntimeEventType.WORLD_SPAWN)
    runtime.run_until(.437)
    time, sequence = runtime.simulation.world.native.time_state()
    assert time == pytest.approx(.437)
    assert sequence == runtime.simulation.event_sequence.value
    assert sequence != event_id  # scheduler insertion order is not physical execution order


def test_save_load_preserves_spawn_rng_frontier(tmp_path):
    settings = replace(Settings(), object_count=0, max_objects=4, spawn_interval_min=1, spawn_interval_max=3)
    direct, saved = ContinuousRuntime(703, settings), ContinuousRuntime(703, settings)
    direct.run_until(.99); saved.run_until(.99)
    path = tmp_path / "world-timer.seworld"; saved.save_world(path)
    restored = ContinuousRuntime.load_world(path, settings)
    direct.run_until(9.0); restored.run_until(9.0)
    assert restored.simulation.world.to_dict() == direct.simulation.world.to_dict()
    assert restored.simulation.rng.getstate() == direct.simulation.rng.getstate()
    assert _spawn_events(restored) == _spawn_events(direct)


def test_low_scheduler_spawn_id_advances_physical_sequence_at_execution():
    settings = replace(Settings(), object_count=0, max_objects=3, spawn_interval_min=2, spawn_interval_max=2)
    runtime = ContinuousRuntime(704, settings)
    spawn = next(e for e in runtime.scheduler.snapshot() if e.type == RuntimeEventType.WORLD_SPAWN)
    runtime.run_until(1.95)
    before = runtime.simulation.event_sequence.value
    assert spawn.id < before
    runtime.run_until(2.0)
    assert runtime.simulation.event_sequence.value == before + 1
    runtime.run_until(2.1)
    assert runtime.simulation.event_sequence.value == before + 2


def test_maintenance_enters_exact_continuous_world_time_without_cognitive_tick():
    settings = replace(Settings(), continuous_maintenance_interval_seconds=10.0)
    runtime = ContinuousRuntime(705, settings)
    runtime.scheduler.schedule(.437, RuntimeEventType.MAINTENANCE)
    runtime.run_until(.437)
    elapsed = runtime.simulation.core.backend.engine.continuous_time_state()
    assert elapsed[2] == pytest.approx(.437)


@pytest.mark.parametrize("order", ((RuntimeEventType.WORLD_SPAWN, RuntimeEventType.WORLD_ACTION_COMPLETE), (RuntimeEventType.WORLD_ACTION_COMPLETE, RuntimeEventType.WORLD_SPAWN)))
def test_same_time_physical_events_follow_scheduler_insertion_order(monkeypatch, order):
    runtime = ContinuousRuntime(706, replace(Settings(), object_count=0, max_objects=3))
    runtime.scheduler = EventScheduler()
    runtime.scheduler.restore(0.0, 100, [])
    monkeypatch.setattr(runtime.simulation.world, "continuous_spawn_position", lambda: (0, 1))
    for kind in order:
        runtime.scheduler.schedule(.437, kind, ActionType.IDLE.value if kind == RuntimeEventType.WORLD_ACTION_COMPLETE else 0)
    events = runtime.scheduler.pop_ready(.437)
    assert [event.type for event in events] == list(order)
    for event in events:
        runtime._process(event)
    assert runtime.simulation.event_sequence.value == 2
    assert runtime.simulation.world.native.time_state()[1] == 2


def test_full_capacity_spawn_preserves_rng_and_physical_sequence():
    runtime = ContinuousRuntime(707, replace(Settings(), object_count=1, max_objects=1))
    runtime.scheduler = EventScheduler(); runtime.scheduler.restore(0.0, 10, [])
    runtime.scheduler.schedule(.5, RuntimeEventType.WORLD_SPAWN)
    before_rng, before_sequence = runtime.simulation.rng.getstate(), runtime.simulation.event_sequence.value
    event = runtime.scheduler.pop_ready(.5)[0]; runtime._process(event)
    assert runtime.simulation.rng.getstate() == before_rng
    assert runtime.simulation.event_sequence.value == before_sequence
    assert not _spawn_events(runtime)


def test_blocked_spawn_does_not_consume_position_draw_but_reschedules(monkeypatch):
    settings = replace(Settings(), world_width=1, world_height=1, object_count=0, max_objects=2, spawn_interval_min=3, spawn_interval_max=3)
    runtime = ContinuousRuntime(708, settings)
    runtime.scheduler = EventScheduler(); runtime.scheduler.restore(0.0, 10, [])
    runtime.scheduler.schedule(.5, RuntimeEventType.WORLD_SPAWN)
    choice_calls = []
    original_choice = runtime.simulation.rng.choice
    monkeypatch.setattr(runtime.simulation.rng, "choice", lambda values: choice_calls.append(values) or original_choice(values))
    event = runtime.scheduler.pop_ready(.5)[0]; runtime._process(event)
    assert choice_calls == []
    assert runtime.simulation.event_sequence.value == 0
    assert _spawn_events(runtime) == [(3.5, 11)]

def test_physical_event_sequence_survives_save_load(tmp_path):
    settings=replace(Settings(),object_count=0,max_objects=3,spawn_interval_min=1,spawn_interval_max=1)
    runtime=ContinuousRuntime(709,settings);runtime.run_until(1.2);before=runtime.simulation.event_sequence.value
    assert before==runtime.simulation.world.native.time_state()[1] and before>0
    restored=_roundtrip(runtime,tmp_path,"sequence")
    assert restored.simulation.event_sequence.value==restored.simulation.world.native.time_state()[1]==before
    for expected in (before+1,before+2):
        while True:
            event=restored.scheduler.snapshot()[0]
            for ready in restored.scheduler.pop_ready(event.time):
                was=restored.simulation.event_sequence.value;restored._process(ready)
                if restored.simulation.event_sequence.value!=was:break
            if restored.simulation.event_sequence.value==expected:break
        assert restored.simulation.event_sequence.value==expected

def test_v3_world_migrates_to_v4_without_rng_draw(tmp_path):
    settings=replace(Settings(),object_count=0,max_objects=3,spawn_interval_min=5,spawn_interval_max=5)
    source=ContinuousRuntime(710,settings);source.run_until(.4);current=source.world_time;legacy=7
    v4=Path(tmp_path)/"v4.seworld";source.save_world(v4);data=load_container(v4,"world",{"META","STATE","CONT","NBRN"})
    data["META"]["version"]=3;data["STATE"]["world"]["next_spawn_tick"]=legacy;data["CONT"]["scheduler"]["events"]=[e for e in data["CONT"]["scheduler"]["events"] if e[2] not in {"WORLD_SPAWN","MAINTENANCE"}]
    v3=Path(tmp_path)/"v3.seworld";save_container(v3,"world",data,{"NBRN"});rng=data["STATE"]["random_state"]
    migrated=ContinuousRuntime.load_world(v3,settings);spawns=_spawn_events(migrated);maint=[e for e in migrated.scheduler.snapshot() if e.type==RuntimeEventType.MAINTENANCE]
    assert spawns and spawns[0][0]==max(current,float(legacy));assert len(maint)==1 and maint[0].time==current+settings.continuous_maintenance_interval_seconds
    assert migrated.simulation.world.next_spawn_tick is None and migrated.simulation.snapshot_data()["random_state"]==rng
    out=Path(tmp_path)/"migrated.seworld";migrated.save_world(out);assert load_container(out,"world",{"META","STATE","CONT","NBRN"})["META"]["version"]==4

@pytest.mark.parametrize("boundary",(.99,1.0,1.01,1.15,1.2,1.35))
def test_continuous_world_persistence_matrix(tmp_path,boundary):
    settings=replace(Settings(),object_count=0,max_objects=4,spawn_interval_min=1,spawn_interval_max=2)
    direct=ContinuousRuntime(711,settings);saved=ContinuousRuntime(711,settings);loaded=ContinuousRuntime(711,settings)
    for runtime in (direct,saved,loaded):runtime.run_until(boundary)
    saved.save_world(Path(tmp_path)/f"save-{boundary}.seworld");loaded=_roundtrip(loaded,tmp_path,f"load-{boundary}")
    for runtime in (direct,saved,loaded):runtime.run_until(3.0)
    assert _behavior_state(direct)==_behavior_state(saved)==_behavior_state(loaded)
