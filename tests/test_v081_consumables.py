"""v0.8.1 physical resources, native authority and exact continuation."""

from dataclasses import replace
from random import Random
from pathlib import Path
import ast
import os
import subprocess
import sys

import pytest

from config import Settings
from persistence import load_container
from simulation import Simulation
from simulation.continuous import ContinuousRuntime
from world import Action, ActionResult, ActionType, NativeWorld, World


def resource_settings(**kwargs):
    return replace(Settings(world_width=8, world_height=8, object_count=0,
                            max_objects=0, resource_spawning_enabled=True,
                            resource_spawn_interval_seconds=0.5,
                            resource_max_live=2), **kwargs)


def test_world_interaction_consumes_once_with_native_parity():
    settings = resource_settings()
    oracle = World(settings, Random(17))
    native = NativeWorld(settings, Random(17))
    oracle.body.x, oracle.body.y = 3, 4
    native.native.set_body_state(0, 3, 4, "N")
    native._refresh()
    for world in (oracle, native):
        world.spawn_resource((3, 3), 1, 23., 0., 0., 1)
        assert world.perceive(0).cells
        assert world.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.SUCCESS
        assert world.objects == []
        assert world.take_consequence() == (23., 0.)
        assert world.take_consequence() == (0., 0.)
        assert world.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.BLOCKED
        assert world.take_consequence() == (0., 0.)
    assert oracle.to_dict() == native.to_dict()


def test_failed_interaction_and_hydration_consequence():
    settings = resource_settings(resource_nutrient_payload=0., resource_hydration_payload=30.)
    simulation = Simulation(18, settings, "native")
    world = simulation.world
    world.native.set_body_state(0, 3, 4, "N")
    world._refresh()
    assert world.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.BLOCKED
    simulation.apply_world_consequence()
    before = simulation.physiology.hydration
    world.spawn_resource((3, 3), 2, 0., 30., 0., 1)
    assert world.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.SUCCESS
    simulation.apply_world_consequence()
    assert simulation.physiology.hydration == min(settings.physiology_max_hydration, before + 30.)
    simulation.apply_world_consequence()
    assert simulation.physiology.hydration == min(settings.physiology_max_hydration, before + 30.)


def test_pending_spawn_and_consumed_state_roundtrip(tmp_path):
    settings = resource_settings()
    original = ContinuousRuntime(19, settings)
    path = tmp_path / "pending.seworld"
    original.save_world(path)
    saved = load_container(path, "world", {"META", "STATE", "CONT", "NBRN"})
    assert saved["META"]["version"] == 9
    assert any(row[2:] == ["WORLD_SPAWN", 1] for row in saved["CONT"]["scheduler"]["events"])
    restored = ContinuousRuntime.load_world(path)
    for runtime in (original, restored):
        runtime.run_until(1.1)
    assert original.simulation.snapshot_data() == restored.simulation.snapshot_data()
    assert original.scheduler_state() == restored.scheduler_state()
    assert len(original.simulation.world.objects) == 2
    consumed = original.simulation.world.objects[0]
    original.simulation.world.native.set_body_state(0, consumed.x, consumed.y + 1, "N") if consumed.y < 7 else original.simulation.world.native.set_body_state(0, consumed.x, consumed.y - 1, "S")
    original.simulation.world._refresh()
    action = ActionType.INTERACT_UP if consumed.y < 7 else ActionType.INTERACT_DOWN
    assert original.simulation.world.apply_action(Action(action)) is ActionResult.SUCCESS
    original.simulation.apply_world_consequence()
    spent = tmp_path / "consumed.seworld"
    original.save_world(spent)
    loaded = ContinuousRuntime.load_world(spent)
    assert loaded.simulation.world.resource_count() == 1
    assert all(o.id != consumed.id for o in loaded.simulation.world.objects)
    assert loaded.simulation.physiology.to_dict() == original.simulation.physiology.to_dict()


def test_brain_artifact_excludes_resources_and_reserves(tmp_path):
    sim = Simulation(20, resource_settings(), "native")
    sim.world.spawn_resource((3, 3), 1, 20., 0., 0., 1)
    brain = tmp_path / "resource.sebrain"
    sim.save_brain(brain)
    sections = load_container(brain, "brain")
    assert "STATE" not in sections
    assert "resource_config" not in str(sections)
    assert "physiology" not in str(sections)


def test_spawn_sequence_ignores_observer_activity_and_wall_pacing():
    settings=resource_settings(resource_max_live=4)
    plain=ContinuousRuntime(21,settings)
    observed=ContinuousRuntime(21,settings)
    for time in (0.5,1.,1.5,2.):
        plain.run_until(time)
        for _ in range(7):observed.render_snapshot()
        observed.run_until(time)
    assert plain.simulation.snapshot_data()==observed.simulation.snapshot_data()
    assert plain.scheduler_state()==observed.scheduler_state()


def test_resource_sequence_is_hash_seed_independent():
    code=("import hashlib,json;from config import Settings;from dataclasses import replace;"
          "from simulation.continuous import ContinuousRuntime;"
          "s=replace(Settings(),object_count=0,max_objects=0,resource_spawning_enabled=True,"
          "resource_spawn_interval_seconds=.5,resource_max_live=3);"
          "r=ContinuousRuntime(22,s);r.run_until(2.);"
          "print(hashlib.sha256(json.dumps([r.simulation.world.to_dict(),r.scheduler_state()],"
          "sort_keys=True,default=str).encode()).hexdigest())")
    results=[]
    for seed in ("1","777"):
        env={**os.environ,"PYTHONHASHSEED":seed}
        results.append(subprocess.check_output([sys.executable,"-c",code],cwd=Path(__file__).parents[1],env=env,text=True).strip())
    assert results[0]==results[1]


def test_pending_consequence_roundtrip_is_applied_once(tmp_path):
    settings=resource_settings()
    source=Simulation(23,settings,"native")
    source.world.native.set_body_state(0,3,4,"N")
    source.world._refresh()
    source.world.spawn_resource((3,3),1,20.,0.,0.,1)
    assert source.world.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.SUCCESS
    path=tmp_path / "pending-consequence.seworld"
    source.save_world(path)
    restored=Simulation.load_world(path,settings,"native")
    before=restored.physiology.nutrients
    restored.apply_world_consequence()
    assert restored.physiology.nutrients==min(settings.physiology_max_nutrients,before+20.)
    restored.apply_world_consequence()
    assert restored.physiology.nutrients==min(settings.physiology_max_nutrients,before+20.)


def test_cognition_and_observer_have_no_resource_mutation_path():
    root=Path(__file__).parents[1]
    for path in [*(root / "consciousness").glob("*.py"),root / "cpp" / "src" / "observer.cpp"]:
        source=path.read_text(encoding="utf-8")
        assert "spawn_resource" not in source and "take_consequence" not in source
        if path.suffix==".py":
            tree=ast.parse(source)
            assert not any(isinstance(node,ast.Attribute) and node.attr=="apply_consequence" for node in ast.walk(tree))


@pytest.mark.parametrize("amount", [float("nan"), float("inf"), -1., 101.])
def test_resource_payload_bounds_are_rejected(amount):
    with pytest.raises(ValueError):
        resource_settings(resource_nutrient_payload=amount)
