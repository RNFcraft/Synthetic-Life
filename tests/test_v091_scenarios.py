"""Initial-condition reproducibility, strict validation and host-only export."""
from dataclasses import replace
import json
import os
from pathlib import Path
from random import Random
import subprocess
import sys

import pytest

from config import Settings
from consciousness._native_brain import WorkbenchCommandKind
from consciousness.native_engine import RuntimeEventType
from experiments.create_scenario_example import example
from experiments.scenario_runner import ExperimentManifest, load_manifest, run_manifest, run_scenario, save_manifest
from main import create_runtime, parse_args
from persistence import load_container, save_container
from simulation import ContinuousRuntime
from simulation.persisted_settings import scenario_configuration
from simulation.scenario import (ScenarioDefinition, artifact_checksum, causal_digest,
                                 export_scenario, load_scenario, save_scenario)
from simulation.workbench import CAUSAL_COMMANDS, WorkbenchController
from world import Action, ActionType

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def scenario_path(tmp_path):
    path = tmp_path / "case.sescenario"
    save_scenario(example(), path)
    return path


def changed(definition, edit):
    sections = definition.sections
    edit(sections)
    return ScenarioDefinition.from_sections(sections)


def test_canonical_roundtrip_initial_reset_and_settings(scenario_path):
    definition = load_scenario(scenario_path)
    assert definition == example()
    a, b = definition.instantiate(), ContinuousRuntime.from_scenario(scenario_path)
    assert causal_digest(a) == causal_digest(b)
    assert scenario_configuration(a.simulation.settings) == definition.sections["CONFIG"]["settings"]
    assert a.simulation.physiology.world_time == a.world_time == 0
    assert a.simulation.event_sequence.value == 0
    assert not a._action_in_flight() and not a.editor_inbox and not a.language_inbox
    assert a.simulation.last_action is None and a.language_frontier is None
    assert a.simulation.core.continuous_frontier is None and a.simulation.core.planner.plan is None
    assert sum(e.type == RuntimeEventType.SENSORY_CHANGE for e in a.scheduler.snapshot()) == 1
    assert (a.simulation.physiology.energy, a.simulation.physiology.nutrients, a.simulation.physiology.hydration) == (60.,20.,35.)
    assert a.simulation.physiology.hunger == pytest.approx((55.-20.)/55.)
    for r in (a, b):r.run_until(.9)
    assert causal_digest(a) == causal_digest(b)
    assert a.simulation.core.backend.full_graph_sync_calls == b.simulation.core.backend.full_graph_sync_calls == 0


def test_metadata_and_record_order_are_noncausal():
    first = example()
    second = changed(first, lambda s: s["META"].update(name="Different human label", tags=["not cognition"]))
    assert first.causal_checksum == second.causal_checksum
    shuffled = changed(first, lambda s: s["INITIAL"]["objects"].reverse())
    assert shuffled == first
    a, b = first.instantiate(), second.instantiate()
    for r in (a,b):r.run_until(.6)
    assert causal_digest(a) == causal_digest(b)
    assert not a.simulation.core.backend.engine.dialogue_snapshot()[1]


def test_scenario_definition_is_detached():
    definition = example()
    sections = definition.sections
    sections["INITIAL"]["physiology"]["energy"] = 0
    assert definition.sections["INITIAL"]["physiology"]["energy"] == 60


def test_direct_geometry_does_not_consume_rng():
    first = example()
    second = changed(first, lambda s: s["INITIAL"].update(objects=[]))
    a, b = first.instantiate(), second.instantiate()
    rng = Random(first.seed)
    rng.randint(first.settings.spawn_interval_min, first.settings.spawn_interval_max)
    assert a.simulation.rng.getstate() == b.simulation.rng.getstate() == rng.getstate()
    assert a.scheduler_state() == b.scheduler_state()


def test_default_constructor_rng_path_remains_unchanged():
    seed = 12345
    settings = Settings()
    rng = Random(seed)
    positions = rng.sample([(x,y) for y in range(settings.world_height) for x in range(settings.world_width)],
                           min(settings.object_count,settings.max_objects)+settings.entity_count)
    if settings.object_count < settings.max_objects:rng.randint(settings.spawn_interval_min,settings.spawn_interval_max)
    runtime = ContinuousRuntime(seed)
    assert runtime.simulation.world.body.position == positions[0]
    assert runtime.simulation.rng.getstate() == rng.getstate()


def test_real_resource_consequence_and_same_appearance_counterfactual():
    first = example()
    def neutral(s):
        s["INITIAL"]["objects"][0].update(resource_channel=0, nutrients=0., hydration=0.)
    second = changed(first, neutral)
    a, b = first.instantiate(), second.instantiate()
    assert a.simulation.world.perceive(0).cells == b.simulation.world.perceive(0).cells
    assert a.simulation.core.backend.engine.relation_count == b.simulation.core.backend.engine.relation_count == 0
    for r in (a,b):
        assert r.simulation.world.apply_action(Action(ActionType.INTERACT_UP)).name == "SUCCESS"
        r.simulation.apply_world_consequence()
    assert a.simulation.physiology.nutrients == 51 and b.simulation.physiology.nutrients == 20
    a.simulation.apply_world_consequence()
    assert a.simulation.physiology.nutrients == 51


def test_held_resource_roundtrip(scenario_path):
    def held(s):
        obj = s["INITIAL"]["objects"].pop(0)
        s["INITIAL"]["held_objects"].append(dict(owner_id=0, **obj))
    definition = changed(example(), held)
    save_scenario(definition, scenario_path)
    r = load_scenario(scenario_path).instantiate()
    assert r.simulation.world.held_object.id == 1
    assert r.simulation.world.held_object.nutrients == 31
    exported = export_scenario(r, scenario_path, seed=definition.seed, name="Held", paused=True)
    assert exported.sections["INITIAL"] == definition.sections["INITIAL"]


@pytest.mark.parametrize("edit", [
    lambda s:s["META"].update(version=2),
    lambda s:s.pop("CONFIG"),
    lambda s:s.update(brain={}),
    lambda s:s["INITIAL"].update(scheduler=[]),
    lambda s:s["INITIAL"].update(rng_state=[]),
    lambda s:s["INITIAL"]["objects"].append(dict(s["INITIAL"]["objects"][0])),
    lambda s:s["INITIAL"]["objects"][1].update(x=3,y=3),
    lambda s:s["INITIAL"]["objects"][0].update(x=3,y=4),
    lambda s:s["INITIAL"]["objects"][0].update(x=-1),
    lambda s:s["INITIAL"]["bodies"][0].update(orientation="BAD"),
    lambda s:s["INITIAL"]["bodies"][0].update(id=True),
    lambda s:s["INITIAL"]["physiology"].update(energy=-1),
    lambda s:s["INITIAL"]["physiology"].update(energy=101),
    lambda s:s["INITIAL"]["physiology"].update(energy=float("nan")),
    lambda s:s["INITIAL"]["objects"][0].update(hydration=float("inf")),
    lambda s:s["INITIAL"]["objects"][0].update(nutrients=101),
    lambda s:s["INITIAL"]["objects"][0].update(resource_channel=3),
    lambda s:s["INITIAL"]["objects"][0].update(resource_channel=0),
    lambda s:s["CONFIG"].update(seed=-1),
    lambda s:s["CONFIG"].update(seed=True),
    lambda s:s["CONFIG"]["settings"]["resources"].update(resource_max_live=1),
    lambda s:s["CONFIG"]["settings"]["cognitive"].pop("wave_max_steps"),
    lambda s:s["CONFIG"]["settings"]["world"].update(world_width="8"),
    lambda s:s["META"].update(description="x"*4097),
])
def test_malformed_scenario_fails_closed(edit, scenario_path):
    sections = example().sections
    edit(sections)
    save_container(scenario_path, "scenario", sections)
    with pytest.raises((ValueError,TypeError)):
        load_scenario(scenario_path)


def test_checksum_corruption_rejected(scenario_path):
    raw = bytearray(scenario_path.read_bytes());raw[-2] ^= 1
    scenario_path.write_bytes(raw)
    with pytest.raises(ValueError,match="corrupt"):
        load_scenario(scenario_path)


def test_export_inert_and_editor_created_setup_replays(tmp_path):
    runtime = example().instantiate()
    controller = WorkbenchController(runtime);controller.paused = True
    controller.commands.submit(WorkbenchCommandKind.PLACE_FOOD,x=6,y=6)
    controller.poll()
    assert runtime.simulation.world.object_at((6,6)).nutrients == 31
    with pytest.raises(ValueError,match="in flight"):
        export_scenario(runtime,tmp_path/"unsafe.sescenario",seed=42,name="Unsafe",paused=True)
    controller.commands.submit(WorkbenchCommandKind.REACH_SCENARIO_BOUNDARY);controller.poll()
    before = causal_digest(runtime)
    path = tmp_path/"edited.sescenario"
    controller.commands.submit_export(str(path),"Edited",42);controller.poll()
    assert causal_digest(runtime) == before and runtime.next_editor_command_id == 2
    definition = load_scenario(path)
    assert "saved" in runtime.last_workbench_notice and "EXPORT_SCENARIO" not in CAUSAL_COMMANDS
    assert any(o["x"]==6 and o["y"]==6 and o["nutrients"]==31 for o in definition.sections["INITIAL"]["objects"])
    assert set(load_container(path,"scenario")) == {"META","CONFIG","INITIAL"}
    replay, result = run_scenario(path,.6)
    assert replay.world_time == .6 and result["seed"] == 42
    assert causal_digest(definition.instantiate()) == causal_digest(ContinuousRuntime.from_scenario(path))


@pytest.mark.parametrize("unsafe", ["running", "editor", "language", "action", "consequence"])
def test_export_safety_gate_is_inert(unsafe,tmp_path):
    r = example().instantiate()
    if unsafe == "editor":r.accept_editor_command("PLACE_OBJECT",x=7,y=7)
    if unsafe == "language":r.inject_utterance(("dax",),0.)
    if unsafe == "action":r.run_to_quiescence()
    if unsafe == "consequence":r.simulation.world.apply_action(Action(ActionType.INTERACT_UP))
    before=causal_digest(r)
    with pytest.raises(ValueError):
        export_scenario(r,tmp_path/"unsafe.sescenario",seed=1,name="Unsafe",paused=unsafe!="running")
    assert causal_digest(r)==before


def test_main_and_runner_share_factory_manifest_relative_paths(scenario_path,tmp_path,monkeypatch):
    direct = create_runtime(scenario_path=scenario_path)
    other, provenance = run_scenario(scenario_path,.6)
    direct.run_until(.6)
    assert causal_digest(direct) == provenance["final_digest"] == causal_digest(other)
    manifest_path=tmp_path/"run.semanifest"
    save_manifest(ExperimentManifest("case.sescenario",.6,result_out="result.json"),manifest_path)
    monkeypatch.chdir(ROOT.parent)
    loaded,result=run_manifest(manifest_path)
    assert result["final_digest"]==provenance["final_digest"]
    assert result["manifest_checksum"]==artifact_checksum(manifest_path)
    assert json.loads((tmp_path/"result.json").read_text())["final_digest"]==result["final_digest"]
    assert result["paths"]["declared"]["scenario"]=="case.sescenario"


@pytest.mark.parametrize("kwargs", [dict(scenario="",seconds=1),dict(scenario="case",seconds=-1),
    dict(scenario="case",seconds=float("inf")),dict(scenario=42,seconds=1),dict(scenario="case",seconds=1,brain_in=[]),
    dict(scenario="case",seconds=True)])
def test_manifest_payload_rejection(kwargs):
    with pytest.raises((ValueError,TypeError)):ExperimentManifest(**kwargs)


@pytest.mark.parametrize("args", [["--scenario","case","--load","world"],["--scenario","case","--seed","42"],["--brain","brain"]])
def test_main_rejects_ambiguous_cli(args):
    with pytest.raises(SystemExit):parse_args(args)


def test_brain_overlay_is_durable_only_and_fail_closed(scenario_path,tmp_path):
    r=example().instantiate();r.run_until(.6)
    path=tmp_path/"learned.sebrain";r.simulation.save_brain(path)
    receiving=ContinuousRuntime.from_scenario(scenario_path,path)
    assert receiving.world_time == receiving.simulation.physiology.world_time == 0
    assert receiving.simulation.core.continuous_frontier is None and receiving.simulation.core.planner.plan is None
    assert receiving.simulation.last_action is None and not receiving.language_inbox
    assert receiving.simulation.world.to_dict()==example().instantiate().simulation.world.to_dict()
    assert receiving.simulation.core.backend.engine.live_cognit_count == r.simulation.core.backend.engine.live_cognit_count
    source_memory=r.simulation.core.memory.to_dict()
    target_memory=receiving.simulation.core.memory.to_dict()
    assert target_memory["world_time_seconds"] == 0
    for group in ("places","structures"):
        for source,target in zip(source_memory[group],target_memory[group]):
            assert target["confidence"] == source["confidence"]
            for field in ("last_confirmed_time_seconds","last_touch_time_seconds"):
                if source.get(field) is not None:
                    assert target[field] == pytest.approx(source[field]-source_memory["world_time_seconds"])
    receiving.run_until(.6)
    assert receiving.world_time == .6
    incompatible=changed(example(),lambda s:s["CONFIG"]["settings"]["interoception"].update(interoception_bins=4))
    with pytest.raises(ValueError):incompatible.instantiate(path)


def test_hashseed_independence(scenario_path):
    script="from simulation import ContinuousRuntime;from simulation.scenario import causal_digest;import sys;r=ContinuousRuntime.from_scenario(sys.argv[1]);r.run_until(.6);print(causal_digest(r))"
    outputs=[subprocess.check_output([sys.executable,"-B","-c",script,str(scenario_path)],cwd=ROOT,
             env={**os.environ,"PYTHONHASHSEED":seed},text=True) for seed in ("1","777")]
    assert outputs[0]==outputs[1]


@pytest.mark.parametrize("edit", [lambda s:s["META"].update(version=2),
    lambda s:s["META"].update(schema="unknown"),lambda s:s["RUN"].pop("scenario"),
    lambda s:s["RUN"].update(callback="eval"),lambda s:s["RUN"].update(seconds=float("nan")),
    lambda s:s["RUN"].update(brain_in=42)])
def test_malformed_manifest_file_rejected(edit,tmp_path):
    sections=ExperimentManifest("case.sescenario",.6).sections();edit(sections)
    path=tmp_path/"bad.semanifest";save_container(path,"manifest",sections)
    with pytest.raises(ValueError):load_manifest(path)


def test_export_io_failure_is_inert_and_notice_not_dialogue(tmp_path):
    r=example().instantiate();controller=WorkbenchController(r);controller.paused=True
    before=causal_digest(r)
    controller.commands.submit_export(str(tmp_path),"Directory",42);controller.poll()
    assert causal_digest(r)==before
    assert "rejected" in r.last_workbench_notice and not r.last_dialogue_notice
    assert r.next_editor_command_id==1


def test_pending_checkpoint_continuation_after_scenario_start(tmp_path):
    original=example().instantiate();original.accept_editor_command("PLACE_OBJECT",x=7,y=7)
    path=tmp_path/"pending.seworld";original.save_world(path)
    assert load_container(path,"world")["META"]["version"]==11
    restored=ContinuousRuntime.load_world(path)
    for r in (original,restored):r.run_until(.9)
    assert causal_digest(original)==causal_digest(restored)


def test_json_record_complexity_rejected_before_materialization(tmp_path):
    path=tmp_path/"huge.sescenario"
    sections=example().sections;sections["INITIAL"]["objects"]=[{}]*12001
    save_container(path,"scenario",sections)
    with pytest.raises(ValueError,match="complexity"):load_scenario(path)


def test_neural_scenario_brain_overlay_rebinds_receiving_authority(tmp_path):
    definition=changed(example(),lambda s:s["CONFIG"]["settings"]["neural"].update(sensory_neural_enabled=True))
    source=definition.instantiate()
    path=tmp_path/"neural.sebrain";source.simulation.save_brain(path)
    receiving=definition.instantiate(path)
    assert receiving.neural_sensory.substrate is receiving.simulation.core.backend.engine.neurodynamic_substrate()
    assert receiving.neural_sensory.telemetry.sensory_frames_transduced==0
    receiving.run_until(.01)
    assert receiving.neural_sensory.telemetry.sensory_frames_transduced==1
    assert receiving.simulation.core.backend.full_graph_sync_calls==0
