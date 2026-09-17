import math

import pytest

from config import Settings
from physiology import HomeostaticEvaluator, Physiology
from simulation.continuous import ContinuousRuntime
from world import ActionType


def _settings(**overrides):
    return Settings(**overrides)


def test_worldtime_update_is_deterministic_and_bounded():
    left = Physiology(_settings())
    right = Physiology(_settings())
    for value in (0.25, 1.0, 7.5, 50_000.0):
        left.advance_to(value)
        right.advance_to(value)
    assert left.to_dict() == right.to_dict()
    snapshot = left.snapshot()
    assert all(math.isfinite(value) for value in (snapshot.energy, snapshot.nutrients, snapshot.hydration, snapshot.hunger, snapshot.tension))
    assert 0 <= snapshot.energy <= left.settings.physiology_max_energy
    assert 0 <= snapshot.nutrients <= left.settings.physiology_max_nutrients
    assert 0 <= snapshot.hydration <= left.settings.physiology_max_hydration
    assert 0 <= snapshot.tension <= 1


def test_worldtime_must_be_monotonic_and_finite():
    physiology = Physiology(_settings())
    physiology.advance_to(2.0)
    for invalid in (1.0, math.nan, math.inf):
        with pytest.raises(ValueError):
            physiology.advance_to(invalid)


def test_successful_movement_spends_energy_and_brownout_blocks_it():
    physiology = Physiology(_settings(physiology_initial_energy=1.0, physiology_movement_cost=0.25))
    physiology.apply_action(ActionType.MOVE_RIGHT, successful=True)
    assert physiology.energy == pytest.approx(0.75)
    physiology.energy = 0.1
    assert not physiology.can_begin(ActionType.MOVE_RIGHT)
    assert physiology.can_begin(ActionType.IDLE)
    physiology.apply_action(ActionType.MOVE_RIGHT, successful=False)
    assert physiology.energy == pytest.approx(0.1)


def test_external_food_and_water_consequence_hooks_restore_reserves():
    physiology = Physiology(_settings(physiology_initial_nutrients=10.0, physiology_initial_hydration=12.0))
    physiology.apply_consequence(nutrients=25.0)
    physiology.apply_consequence(hydration=30.0)
    assert physiology.nutrients == pytest.approx(35.0)
    assert physiology.hydration == pytest.approx(42.0)
    physiology.apply_consequence(nutrients=10_000.0, hydration=10_000.0)
    assert physiology.nutrients == physiology.settings.physiology_max_nutrients
    assert physiology.hydration == physiology.settings.physiology_max_hydration


def test_tension_is_bounded_and_monotonic_under_deficit():
    evaluator = HomeostaticEvaluator(75.0, 55.0, 75.0)
    stable = evaluator.tension(75.0, 55.0, 75.0)
    moderate = evaluator.tension(40.0, 30.0, 40.0)
    severe = evaluator.tension(0.0, 0.0, 0.0)
    assert 0.0 == stable < moderate < severe == 1.0


def test_physiology_roundtrip_and_exact_continuation():
    settings = _settings()
    original = Physiology(settings)
    original.advance_to(12.5)
    original.apply_action(ActionType.MOVE_LEFT, successful=True)
    raw = original.to_dict()
    restored = Physiology(settings)
    restored.restore(raw)
    original.advance_to(20.0)
    restored.advance_to(20.0)
    assert restored.to_dict() == original.to_dict()


def test_continuous_world_save_load_preserves_physiology(tmp_path):
    runtime = ContinuousRuntime(800, _settings(physiology_movement_cost=0.125))
    runtime.run_until(2.0)
    path = tmp_path / "physiology.seworld"
    runtime.save_world(path)
    restored = ContinuousRuntime.load_world(path)
    assert restored.simulation.settings.physiology_movement_cost == pytest.approx(0.125)
    assert restored.simulation.physiology.to_dict() == runtime.simulation.physiology.to_dict()
    runtime.run_until(3.0)
    restored.run_until(3.0)
    assert restored.simulation.physiology.to_dict() == runtime.simulation.physiology.to_dict()


def test_core_and_observer_receive_read_only_projections():
    runtime = ContinuousRuntime(801)
    runtime.run_until(0.0)
    physiology = runtime.simulation.physiology
    before = physiology.to_dict()
    projection = runtime.simulation.core.homeostatic_projection
    observed = runtime.render_snapshot().physiology
    assert projection == observed == physiology.snapshot()
    with pytest.raises((AttributeError, TypeError)):
        observed.energy = 0.0
    assert physiology.to_dict() == before


def test_projection_contains_no_action_or_object_policy():
    projection = Physiology(_settings()).snapshot()
    assert set(projection.__slots__) == {"world_time", "energy", "nutrients", "hydration", "hunger", "tension"}
