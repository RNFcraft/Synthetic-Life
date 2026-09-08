from dataclasses import replace

import pytest

from config import Settings
from consciousness.native_engine import RuntimeEventType
from simulation import ContinuousRuntime
from world.native_world import NativeWorld


def _spawn_events(runtime):
    return [(e.time, e.id) for e in runtime.scheduler.snapshot() if e.type is RuntimeEventType.WORLD_SPAWN]


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
    spawn = next(e for e in runtime.scheduler.snapshot() if e.type is RuntimeEventType.WORLD_SPAWN)
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
    before_tick = runtime.simulation.core.cognitive_tick
    runtime.run_until(.437)
    elapsed = runtime.simulation.core.backend.engine.continuous_time_state()
    assert elapsed[2] == pytest.approx(.437)
    assert runtime.simulation.core.cognitive_tick == before_tick
