from dataclasses import replace
from pathlib import Path
import time

import pytest

from config import Settings
from persistence import load_container
from simulation import ContinuousRuntime


def _causal(runtime):
    native_time, native_sequence = runtime.simulation.world.native.time_state()
    frontier = runtime.simulation.core.continuous_frontier
    return (
        runtime.scheduler_state(), runtime.simulation.event_sequence.value,
        native_time, native_sequence, runtime.simulation.rng.getstate(),
        runtime.simulation.world.to_dict(), runtime.maintenance_ordinal,
        runtime.cognition_generation, runtime.actions_completed,
        None if frontier is None else (frontier.generation, frontier.phase, frontier.committed),
    )


def _wait_for_frames(observer, minimum=3, timeout=5.0):
    deadline = time.monotonic() + timeout
    while observer.frames_rendered < minimum and observer.is_running and time.monotonic() < deadline:
        time.sleep(0.01)
    if observer.frames_rendered < minimum:
        observer.stop()
        pytest.skip("usable SDL3/OpenGL desktop is unavailable")


def _start(observer, minimum=3):
    assert observer.start() is True
    _wait_for_frames(observer, minimum)
    assert observer.is_running


def _keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _keys(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _keys(child)


def test_live_observer_attaches_to_same_authoritative_runtime_world():
    settings = replace(Settings(), world_width=6, world_height=6, object_count=0,
                       max_objects=2, spawn_interval_min=1, spawn_interval_max=1)
    runtime = ContinuousRuntime(901, settings)
    native = runtime.simulation.world.native
    observer = native.create_observer()
    initial = observer.latest_snapshot()
    assert initial == native.latest_render_snapshot()

    runtime.run_until(0.15)
    after_action = observer.latest_snapshot()
    assert after_action == native.latest_render_snapshot()
    assert after_action[1] == runtime.simulation.event_sequence.value
    assert after_action[4] == native.latest_render_snapshot()[4]

    before_ids = {row[0] for row in after_action[5]}
    runtime.run_until(1.0)
    after_spawn = observer.latest_snapshot()
    assert after_spawn == native.latest_render_snapshot()
    assert after_spawn[0:2] == native.time_state()
    assert {row[0] for row in after_spawn[5]} > before_ids


def test_native_observer_lifecycle_is_causally_inert():
    runtime = ContinuousRuntime(902)
    runtime.run_until(0.4)
    before = _causal(runtime)
    observer = runtime.simulation.world.native.create_observer()
    _start(observer)
    first = observer.frames_rendered
    _wait_for_frames(observer, first + 2)
    assert observer.start() is False
    observer.stop()
    observer.stop()
    assert observer.is_running is False
    assert _causal(runtime) == before


def test_continuous_runtime_continues_after_observer_stop():
    plain, observed = ContinuousRuntime(903), ContinuousRuntime(903)
    observer = observed.simulation.world.native.create_observer()
    _start(observer)
    observed.run_until(0.7)
    observer.stop()
    observed.run_until(2.0)
    plain.run_until(2.0)
    assert _causal(observed) == _causal(plain)


def test_live_observer_does_not_change_continuous_trajectory():
    states = []
    frame_targets = (0, 3, 20)
    for target in frame_targets:
        runtime = ContinuousRuntime(904)
        observer = None
        if target:
            observer = runtime.simulation.world.native.create_observer()
            _start(observer, target)
        runtime.run_until(2.0)
        if observer:
            _wait_for_frames(observer, target + 2)
            observer.stop()
        states.append(_causal(runtime))
    assert states[0] == states[1] == states[2]


def test_observer_state_is_not_persisted(tmp_path):
    plain, observed = ContinuousRuntime(905), ContinuousRuntime(905)
    observer = observed.simulation.world.native.create_observer()
    _start(observer)
    observer.stop()
    plain.run_until(1.2); observed.run_until(1.2)
    paths = Path(tmp_path) / "plain.seworld", Path(tmp_path) / "observed.seworld"
    plain.save_world(paths[0]); observed.save_world(paths[1])
    forbidden = {"frames_rendered", "observer_running", "observer_window_size", "opengl_handles",
                 "snapshot_channel", "presentation_cadence", "observer"}
    for path in paths:
        data = load_container(path, "world", {"META", "STATE", "CONT", "NBRN"})
        assert forbidden.isdisjoint(_keys(data))
    restored_plain = ContinuousRuntime.load_world(paths[0], plain.simulation.settings)
    restored_observed = ContinuousRuntime.load_world(paths[1], observed.simulation.settings)
    assert _causal(restored_plain) == _causal(restored_observed)
    assert not hasattr(restored_observed, "observer")
