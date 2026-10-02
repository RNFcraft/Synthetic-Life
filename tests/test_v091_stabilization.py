"""Freeze closure: historical defaults, host replacement and canonical artifacts."""
from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
import json
import time

import pytest

from config import Settings
from consciousness._native_brain import WorkbenchCommandChannel, WorkbenchCommandKind
from experiments.create_scenario_example import example
from main import create_runtime, create_native_observer, replace_workbench_runtime
from persistence import load_container, save_container, inspect_container
from persistence.container import HEADER, ContainerError
from simulation import ContinuousRuntime
from simulation.scenario import ScenarioDefinition, causal_digest, export_scenario, load_scenario
from simulation.workbench import CAUSAL_COMMANDS, WorkbenchController
from simulation.workbench_settings import (configuration_draft, preset_draft, validate_draft,
                                         create_new_world, EDITABLE_FIELDS)


def test_default_world_settings_match_historical_baseline():
    settings = Settings()
    assert settings.object_count == 25
    assert settings.max_objects == 25


def test_default_startup_has_literal_canonical_seed_baseline():
    runtime = create_runtime(seed=12345)
    world = runtime.simulation.world.to_dict()
    # Literal reference with historical 25/25, not recomputed from defaults.
    assert world["bodies"][0]["x"] == 6 and world["bodies"][0]["y"] == 14
    assert len(world["objects"]) == 25
    assert sha256(json.dumps(world, sort_keys=True, separators=(",", ":")).encode()).hexdigest() == "d6ed9d919f00611292c92b8efe77cc2144341b81903b7cc44cd9a7a0253093af"
    assert sha256(repr(runtime.simulation.rng.getstate()).encode()).hexdigest() == "38ccc7ed121375582a94680f3b2024cf7e26177b8919212bf8a6fe9bfcaf98ab"


@pytest.mark.parametrize("name,count,maximum", [("Classic Baseline",25,25), ("Workbench Sparse",3,150), ("Empty Experiment",0,150)])
def test_presets_are_explicit_drafts_and_do_not_mutate_runtime(name,count,maximum):
    running = ContinuousRuntime(); before = causal_digest(running)
    draft = preset_draft(name, 321)
    assert (draft["object_count"], draft["max_objects"]) == (count, maximum)
    settings, seed = validate_draft(draft)
    assert settings == replace(Settings(), object_count=count, max_objects=maximum)
    assert seed == 321 and causal_digest(running) == before
    with pytest.raises(FrozenInstanceError):
        running.simulation.settings.world_width = 4


def test_host_command_creates_fresh_deterministic_runtime_without_learning_transfer():
    old = ContinuousRuntime(); old.run_until(.9)
    assert old.simulation.core.graph.nodes
    controller = WorkbenchController(old); before = causal_digest(old)
    draft = preset_draft("Workbench Sparse", 487)
    assert controller.commands.submit_new_world(draft)
    controller.poll(); fresh = controller.replacement
    assert fresh is not None and fresh is not old
    assert causal_digest(old) == before
    assert fresh.world_time == fresh.simulation.event_sequence.value == 0
    assert fresh.simulation.seed == 487
    assert not fresh.simulation.core.graph.nodes and fresh.simulation.core.graph.relation_count == 0
    assert len(fresh.simulation.world.objects) == 3
    expected = ContinuousRuntime(487, replace(Settings(), object_count=3, max_objects=150))
    assert causal_digest(fresh) == causal_digest(expected)
    assert causal_digest(create_new_world(draft)) == causal_digest(expected)
    for runtime in (fresh, expected): runtime.run_until(.5)
    assert causal_digest(fresh) == causal_digest(expected)
    assert fresh.simulation.core.backend.full_graph_sync_calls == 0
    assert "CREATE_NEW_WORLD" not in CAUSAL_COMMANDS


@pytest.mark.parametrize("field,value", [("world_width",0),("world_height",-1),("world_width",4097),
    ("world_height",4097),("object_count",151),("max_objects",-1),("object_count",True),
    ("seed",-1),("seed",2**63),("seed",True),("interoception_bins",33),
    ("physiology_initial_energy",1000),("resource_nutrient_payload",float("nan")),
    ("resource_spawning_enabled",1),("planning_beam_width",0)])
def test_invalid_drafts_fail_closed(field,value):
    draft = preset_draft("Workbench Sparse"); draft[field] = value
    with pytest.raises((ValueError,TypeError)):
        create_new_world(draft)


def test_invalid_host_payload_preserves_current_episode_and_dialogue():
    old = ContinuousRuntime(); controller = WorkbenchController(old)
    before = causal_digest(old); draft = preset_draft("Workbench Sparse")
    draft["world_width"] = 0
    controller.commands.submit_new_world(draft); controller.poll()
    assert controller.replacement is None and causal_digest(old) == before
    assert "rejected" in old.last_workbench_notice and not old.last_dialogue_notice
    with pytest.raises(ValueError):
        controller.commands.submit(WorkbenchCommandKind.CREATE_NEW_WORLD)
    with pytest.raises(ValueError):
        controller.commands.submit_new_world({**draft, "object_count": True})
    with pytest.raises((ValueError,KeyError)):
        validate_draft({"seed":0})


def test_current_draft_preserves_noneditable_configuration_and_presets_reset_it():
    current = replace(Settings(), cognit_birth_threshold=.9)
    assert validate_draft(configuration_draft(current), current)[0] == current
    assert validate_draft(preset_draft("Classic Baseline"), current)[0] == Settings()


def test_new_world_scenario_roundtrip_and_preset_metadata_is_not_persisted(tmp_path):
    fresh = create_new_world(preset_draft("Workbench Sparse", 12345))
    path = tmp_path / "sparse.sescenario"
    definition = export_scenario(fresh, path, seed=12345, name="Case", paused=True)
    replay = load_scenario(path).instantiate()
    assert replay.simulation.settings == fresh.simulation.settings
    assert replay.simulation.world.to_dict() == fresh.simulation.world.to_dict()
    assert "preset" not in json.dumps(definition.sections)
    # Scenario is a normalized initial condition, not continuation of bootstrap RNG.
    second_replay = load_scenario(path).instantiate()
    for r in (replay, second_replay): r.run_until(.6)
    assert causal_digest(replay) == causal_digest(second_replay)


@pytest.mark.parametrize("kind", ["brain","world","scenario","manifest"])
def test_generic_containers_reject_trailing_bytes(kind,tmp_path):
    path = tmp_path / kind; save_container(path,kind,{"A":{"x":1},"B":[]})
    assert load_container(path,kind)["A"] == {"x":1}
    path.write_bytes(path.read_bytes()+b"junk")
    for loader in (lambda:load_container(path,kind), lambda:inspect_container(path)):
        with pytest.raises(ContainerError,match="trailing"): loader()


@pytest.mark.parametrize("layout", ["gap","overlap","reversed"])
def test_generic_containers_reject_noncanonical_section_table(layout,tmp_path):
    path=tmp_path/"bad"; save_container(path,"world",{"A":{},"B":[]})
    raw=path.read_bytes(); magic,version,count,size=HEADER.unpack(raw[:HEADER.size])
    table=json.loads(raw[HEADER.size:HEADER.size+size]); payload=raw[HEADER.size+size:]
    if layout=="gap": table[1]["offset"]+=1;payload+=b" "
    elif layout=="overlap": table[1]["offset"]-=1
    else:table.reverse()
    encoded=json.dumps(table).encode();path.write_bytes(HEADER.pack(magic,version,count,len(encoded))+encoded+payload)
    with pytest.raises(ContainerError,match="layout|corrupt"):load_container(path,"world")


def test_scenario_tail_and_id_exhaustion_rejected(tmp_path):
    path=tmp_path/"bad.sescenario"
    from simulation.scenario import save_scenario
    save_scenario(example(),path);path.write_bytes(path.read_bytes()+b"junk")
    with pytest.raises(ValueError):load_scenario(path)
    sections=example().sections;sections["INITIAL"]["objects"][0]["id"]=2**32-2
    with pytest.raises(ValueError,match="exhaustion"):ScenarioDefinition.from_sections(sections)
    assert load_scenario("scenarios/examples/workbench_smoke.sescenario")


def test_observer_reconnects_to_fresh_runtime_and_closes_old_command_channel():
    old=ContinuousRuntime(); old.run_until(.3)
    observer=create_native_observer(old);controller=old._workbench_controller
    observer.start()
    try:
        controller.commands.submit_new_world(preset_draft("Workbench Sparse", 972))
        controller.poll();fresh=replace_workbench_runtime(old,observer)
        assert fresh.world_time==0 and fresh._workbench_controller.paused
        assert controller.commands.submit(WorkbenchCommandKind.PAUSE)==0
        assert fresh.workbench_channel is not old.workbench_channel
        assert fresh._workbench_controller.commands is not controller.commands
        deadline=time.monotonic()+5
        before=causal_digest(fresh)
        while observer.is_running and observer.frames_rendered<8 and time.monotonic()<deadline:
            fresh._workbench_controller.poll();time.sleep(.01)
        assert observer.frames_rendered>=8
        assert observer.latest_snapshot()[0]==0
        assert causal_digest(fresh)==before
    finally:observer.stop()


def test_world_area_limit_is_checked_before_construction():
    draft = preset_draft("Empty Experiment")
    draft.update(world_width=4096, world_height=4096)
    with pytest.raises(ValueError): create_new_world(draft)


def test_main_loop_returns_replacement_not_discarded_runtime():
    from main import drive_live
    old = ContinuousRuntime()
    observer = create_native_observer(old)
    old._workbench_controller.commands.submit_new_world(preset_draft("Empty Experiment", 842))
    fresh = drive_live(old, observer, seconds=0)
    assert fresh is not old and fresh.simulation.seed == 842 and fresh.world_time == 0
    assert not fresh.simulation.world.objects
