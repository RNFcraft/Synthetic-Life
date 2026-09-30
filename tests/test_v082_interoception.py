"""Causal and persistence contracts for opt-in nonsemantic interoception."""
from dataclasses import replace
from pathlib import Path
import ast

import pytest

from config import Settings
from persistence import load_container
from physiology.interoception import InteroceptiveTransducer
from simulation import Simulation
from simulation.continuous import ContinuousRuntime


def settings(**changes):
    return replace(Settings(world_width=8,world_height=8,object_count=0,max_objects=0),**changes)


def test_bounded_deterministic_encoding_and_config():
    configured=settings(interoception_enabled=True,interoception_bins=4)
    sim=Simulation(3,configured)
    encode=InteroceptiveTransducer(configured)
    assert encode.sample(sim.physiology.snapshot())==encode.sample(sim.physiology.snapshot())
    assert all(0<=value<4 for value in encode.sample(sim.physiology.snapshot()).levels)
    sim.physiology.advance_to(.01)
    assert encode.sample(sim.physiology.snapshot()).levels==encode.sample(Simulation(3,configured).physiology.snapshot()).levels
    for invalid in (1,33,True,2.0):
        with pytest.raises(ValueError):settings(interoception_bins=invalid)
    with pytest.raises(ValueError):settings(interoception_enabled=1)


def test_internal_evidence_enters_ordinary_patterns_without_spatial_tracks():
    sim=Simulation(4,settings(interoception_enabled=True,proto_min_occurrences=1,cognit_birth_threshold=0.0))
    sim.run(5)
    keys=[event.channel for event in sim.core.patterns.last_events]
    assert {"internal_0","internal_1","internal_2"}.issubset(keys)
    assert all(token not in repr(sim.core.patterns.last_events).lower() for token in ("hunger","thirst","food","water","reward"))
    assert any(any(part[2].startswith("internal_") for part in node.pattern.participants) for node in sim.core.graph.nodes.values() if node.pattern)
    assert all(not any(part[2].startswith("internal_") for part in track.participants) for track in sim.core.perception.tracks.values())
    off=Simulation(4,settings())
    off.step()
    assert not any(e.channel.startswith("internal_") for e in off.core.patterns.last_events)


def test_combined_saved_settings_and_exact_continuation(tmp_path):
    configured=settings(interoception_enabled=True,sensory_neural_enabled=True,resource_spawning_enabled=True,
        resource_spawn_interval_seconds=.5,resource_max_live=7,physiology_initial_energy=64.)
    original=ContinuousRuntime(8,configured)
    original.run_until(.8)
    path=tmp_path/"combined.seworld"
    original.save_world(path)
    saved=load_container(path,"world",{"META","STATE","CONT","NBRN"})
    assert saved["META"]["version"]==10
    assert saved["STATE"]["version"]==7
    restored=ContinuousRuntime.load_world(path)
    for name in ("interoception_enabled","interoception_bins","sensory_neural_enabled","resource_spawning_enabled","resource_max_live","physiology_initial_energy"):
        assert getattr(restored.simulation.settings,name)==getattr(configured,name)
    assert restored.last_internal==original.last_internal
    assert restored.simulation.snapshot_data()==original.simulation.snapshot_data()
    for runtime in (original,restored):runtime.run_until(1.3)
    left,right=restored.simulation.snapshot_data(),original.simulation.snapshot_data()
    assert left==right,[(section,[key for key in left[section] if left[section][key]!=right[section][key]]) for section in ("core","cognitive_graph")]
    assert restored.scheduler_state()==original.scheduler_state()
    with pytest.raises(ValueError,match="incompatible"):
        ContinuousRuntime.load_world(path,settings(interoception_enabled=True,sensory_neural_enabled=True,resource_spawning_enabled=True))


def test_manual_resources_save_config_even_when_spawning_disabled(tmp_path):
    configured=settings(resource_max_live=9,resource_nutrient_payload=37.)
    sim=Simulation(9,configured,"native")
    for index in range(5):sim.world.spawn_resource((index+1,2),1,37.,0.,0.,index+1)
    path=tmp_path/"manual.seworld"
    sim.save_world(path)
    assert load_container(path,"world")["META"]["version"]==3
    saved=Simulation.load_world(path,backend="native")
    assert saved.settings.resource_max_live==9
    assert saved.settings.resource_nutrient_payload==37.
    assert saved.world.resource_count()==5
    assert saved.snapshot_data()["resource_config"]["resource_max_live"]==9


def test_brain_transfer_discards_episode_state(tmp_path):
    configured=settings(interoception_enabled=True)
    source=Simulation(12,configured,"native")
    source.step()
    source.physiology.advance_to(10.)
    path=tmp_path/"internal.sebrain"
    source.save_brain(path)
    sections=load_container(path,"brain")
    assert "physiology" not in str(sections)
    assert "sensory_previous_internal" not in str(sections)
    target=Simulation(13,configured,"native")
    target.load_brain(path)
    assert target.physiology.world_time==0.
    assert target.core.patterns.layer.previous_internal is None


def test_discrete_interoception_artifact_version_and_restore(tmp_path):
    original=Simulation(14,settings(interoception_enabled=True,interoception_bins=5),"native")
    original.step()
    path=tmp_path/"discrete.seworld"
    original.save_world(path)
    assert load_container(path,"world")["META"]["version"]==4
    restored=Simulation.load_world(path,backend="native")
    assert restored.settings.interoception_bins==5
    assert restored.snapshot_data()==original.snapshot_data()


def test_architecture_import_guards():
    root=Path(__file__).resolve().parents[1]
    for name in ("consciousness/choice.py","consciousness/planner.py","consciousness/language.py"):
        path=root/name
        if not path.exists():continue
        tree=ast.parse(path.read_text(encoding="utf-8"))
        imports=[node.module or "" for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)]
        imports += [alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names]
        assert not any(module.startswith("physiology") for module in imports)
