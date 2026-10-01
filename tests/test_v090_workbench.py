"""Explicit interventions and causally inert presentation of the v0.8.4 owner."""
from dataclasses import FrozenInstanceError, asdict, replace
from pathlib import Path
import ast

import pytest

from config import Settings
from consciousness._native_brain import WorkbenchCommandChannel, WorkbenchCommandKind
from consciousness.native_engine import RuntimeEventType
from persistence import load_container
from simulation import ContinuousRuntime
from simulation.workbench import WorkbenchController
from world import Action, ActionType


def runtime(seed=9000):
    configured=replace(Settings(),world_width=8,world_height=8,object_count=0,max_objects=8,
        interoception_enabled=True,homeostatic_valuation_enabled=True,delayed_homeostatic_prediction_enabled=True,
        resource_max_live=8,resource_nutrient_payload=31.,resource_hydration_payload=27.)
    return ContinuousRuntime(seed,configured)


def causal(r):
    return r.simulation.snapshot_data(),r.scheduler_state(),r._frontier_state()


def free(r):
    occupied={b.position for b in r.simulation.world.bodies.values()}|{o.position for o in r.simulation.world.objects}
    return next((x,y) for y in range(8) for x in range(8) if (x,y) not in occupied)


def apply(r,kind,**payload):
    command_id=r.accept_editor_command(kind,**payload);r.run_to_quiescence();return command_id


@pytest.mark.parametrize("samples",[0,1,15])
def test_status_snapshot_cadence_has_no_causal_effect(samples):
    plain,observed=runtime(),runtime()
    for horizon in (.15,.3,.6,.9):
        plain.run_until(horizon);observed.run_until(horizon)
        for _ in range(samples):
            observed.workbench_status();observed.render_snapshot();observed.publish_brain_snapshot()
    assert causal(plain)==causal(observed)
    assert observed.simulation.core.backend.full_graph_sync_calls==0


def test_status_is_frozen_detached_and_matches_real_diagnostics():
    r=runtime();r.run_until(.5);before=causal(r);s=r.workbench_status()
    physical=r.simulation.physiology.snapshot()
    assert (s.energy,s.nutrients,s.hydration)==(physical.energy,physical.nutrients,physical.hydration)
    assert s.bins==r.last_internal.levels and s.target_bins==r.simulation.interoception.target_levels
    assert s.internal_observed_at==r.last_internal.world_time
    assert s.pending_events==r.scheduler.size and s.relations==r.simulation.core.backend.engine.relation_count
    with pytest.raises(FrozenInstanceError):s.energy=0
    local=asdict(s);local["energy"]=0;local["planned_actions"]=()
    assert causal(r)==before
    p=r.simulation.core.planner.plan
    assert s.planned_actions==tuple(a.name for a in p.actions) if p else s.planned_actions==()


@pytest.mark.parametrize("kind,channel,payload,presentation",[
    ("PLACE_FOOD",1,(31.,0.),"Food"),("PLACE_WATER",2,(0.,27.),"Water"),
    ("PLACE_OBJECT",0,(0.,0.),"Neutral")])
def test_editor_placement_uses_native_physics_and_settings(kind,channel,payload,presentation):
    r=runtime();x,y=free(r);rng=r.simulation.rng.getstate();apply(r,kind,x=x,y=y)
    o=r.simulation.world.object_at((x,y));assert o is not None
    assert (o.resource_channel,o.nutrients,o.hydration)==(channel,*payload)
    assert next(o for o in r.render_snapshot().objects if o.x==x and o.y==y).presentation_kind==presentation
    assert r.simulation.rng.getstate()==rng


@pytest.mark.parametrize("kind",["PLACE_FOOD","PLACE_WATER"])
def test_placed_resources_produce_real_consequence_once(kind):
    r=runtime();w=r.simulation.world;w.native.set_body_state(0,3,4,"N");w._refresh()
    apply(r,kind,x=3,y=3)
    assert w.apply_action(Action(ActionType.INTERACT_UP)).name=="SUCCESS"
    before=r.simulation.physiology.snapshot();r.simulation.apply_world_consequence();after=r.simulation.physiology.snapshot()
    assert after.nutrients-before.nutrients==(31. if kind=="PLACE_FOOD" else 0.)
    assert after.hydration-before.hydration==min(27.,100.-before.hydration) if kind=="PLACE_WATER" else after.hydration==before.hydration
    r.simulation.apply_world_consequence();assert r.simulation.physiology.snapshot()==after


def test_remove_preserves_graph_knowledge_and_rejects_held_or_absent_ids():
    r=runtime();x,y=free(r);apply(r,"PLACE_OBJECT",x=x,y=y);oid=r.simulation.world.object_at((x,y)).id
    ids=set(r.simulation.core.graph.nodes);apply(r,"REMOVE_OBJECT",object_id=oid)
    assert r.simulation.world.object_at((x,y)) is None
    assert ids.issubset(r.simulation.core.graph.nodes)
    sequence=r.simulation.event_sequence.value;apply(r,"REMOVE_OBJECT",object_id=oid)
    assert "rejected" in r.last_editor_result and r.simulation.event_sequence.value==sequence


@pytest.mark.parametrize("position",[(-1,0),(8,0),(0,8)])
def test_invalid_placement_has_no_physical_or_rng_mutation(position):
    r=runtime();r.run_to_quiescence();world=r.simulation.world.to_dict();rng=r.simulation.rng.getstate();seq=r.simulation.event_sequence.value
    apply(r,"PLACE_FOOD",x=position[0],y=position[1])
    assert "rejected" in r.last_editor_result
    assert r.simulation.world.to_dict()==world and r.simulation.rng.getstate()==rng and r.simulation.event_sequence.value==seq


def test_occupied_cell_and_capacity_rejected_without_sequence_gap():
    r=runtime();b=r.simulation.world.body;apply(r,"PLACE_FOOD",x=b.x,y=b.y);assert "rejected" in r.last_editor_result
    x,y=free(r);apply(r,"PLACE_FOOD",x=x,y=y);seq=r.simulation.event_sequence.value
    apply(r,"PLACE_OBJECT",x=x,y=y);assert "rejected" in r.last_editor_result
    assert r.simulation.event_sequence.value==seq


def test_same_time_command_sequence_and_pending_world_continuation(tmp_path):
    original=runtime();x,y=free(original)
    first=original.accept_editor_command("PLACE_FOOD",x=x,y=y)
    second=original.accept_editor_command("PLACE_OBJECT",x=x,y=y)
    events=[e for e in original.scheduler.snapshot() if e.type==RuntimeEventType.EXTERNAL_INPUT]
    assert [e.payload for e in events]==[first,second] and events[0].id<events[1].id
    path=tmp_path/"pending.seworld";original.save_world(path)
    sections=load_container(path,"world")
    assert sections["META"]["version"]==11
    restored=ContinuousRuntime.load_world(path)
    for r in (original,restored):r.run_until(.6)
    assert causal(restored)==causal(original)
    assert original.simulation.world.object_at((x,y)).nutrients==31.
    assert "rejected" in original.last_editor_result
    assert not any(key in str(sections) for key in ("world_zoom","selected_tool","selected_object","frames_rendered"))


def test_command_at_action_completion_does_not_commit_parallel_action():
    r=runtime();r.run_to_quiescence();completion=next(e for e in r.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE)
    # Accept at the current frontier; a committed physical action remains intact.
    x,y=free(r);apply(r,"PLACE_OBJECT",x=x,y=y)
    assert sum(e.type==RuntimeEventType.WORLD_ACTION_COMPLETE for e in r.scheduler.snapshot())==1
    assert next(e for e in r.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE).id==completion.id
    r.run_until(completion.time)
    assert r.actions_completed==1


def test_ui_queue_dialogue_uses_existing_language_pipeline():
    r=runtime();controller=WorkbenchController(r);controller.paused=True
    controller.commands.submit(WorkbenchCommandKind.SEND_DIALOGUE,text="dax zup")
    controller.poll()
    assert r.language_utterances_processed==1 and r.language_tokens_processed==2
    lines=r.simulation.core.backend.engine.dialogue_snapshot()[1]
    assert lines[-1][3]=="dax zup"


def test_pause_resume_and_step_preserve_exact_frontier():
    r=runtime();controller=WorkbenchController(r)
    controller.commands.submit(WorkbenchCommandKind.PAUSE);controller.poll();before=causal(r)
    for _ in range(12):controller.poll()
    assert controller.paused and causal(r)==before
    controller.commands.submit(WorkbenchCommandKind.STEP);controller.poll()
    assert r.world_time==0. and any(e.type==RuntimeEventType.WORLD_ACTION_COMPLETE for e in r.scheduler.snapshot())
    next_time=r.scheduler.snapshot()[0].time
    controller.commands.submit(WorkbenchCommandKind.STEP);controller.poll();assert r.world_time==next_time
    controller.commands.submit(WorkbenchCommandKind.RESUME);controller.poll();assert not controller.paused


def test_counterfactual_appearance_remains_independent_of_payload():
    r=runtime();x,y=free(r);apply(r,"PLACE_FOOD",x=x,y=y);food=r.simulation.world.object_at((x,y))
    # Existing generic state can carry the same numeric appearance while its
    # resource payload differs. No presentation kind becomes a sensory field.
    b=r.simulation.world.body;r.simulation.world.native.initialize_multi([(0,b.x,b.y,"N",1)],[(1,x,y,food.state)])
    cells,body=r.simulation.world.native.perceive(0)
    assert len(cells[0])==7 and not r.simulation.world.native.resource_state()


def test_native_channel_bounded_nonblocking_and_ordered():
    channel=WorkbenchCommandChannel()
    ids=[channel.submit(WorkbenchCommandKind.PAUSE) for _ in range(256)]
    assert ids==list(range(1,257)) and channel.submit(WorkbenchCommandKind.PAUSE)==0
    assert [row[0] for row in channel.drain()]==ids
    channel.close();assert channel.submit(WorkbenchCommandKind.RESUME)==0


def test_host_rejects_full_runtime_inbox_without_crashing():
    r = runtime()
    controller = WorkbenchController(r)
    for _ in range(256):
        r.accept_editor_command("PLACE_OBJECT", x=0, y=0)
    controller.commands.submit(WorkbenchCommandKind.PLACE_OBJECT, x=1, y=0)
    controller.poll()
    assert len(r.editor_inbox) == 256
    assert "inbox is full" in r.last_editor_result


def test_brain_artifact_has_no_workbench_episode_state(tmp_path):
    r=runtime();r.accept_editor_command("PLACE_FOOD",x=0,y=0)
    path=tmp_path/"brain.sebrain";r.simulation.save_brain(path)
    sections=load_container(path,"brain")
    assert "workbench_commands" not in str(sections) and "editor_inbox" not in str(sections)


def test_missing_pending_command_state_fails_closed():
    r = runtime()
    r.accept_editor_command("PLACE_OBJECT", x=0, y=0)
    with pytest.raises(ValueError, match="inbox missing"):
        r._restore_editor_state(None)


def test_actual_resource_capacity_rejects_atomically():
    r = runtime()
    r.run_to_quiescence()
    for _ in range(r.simulation.settings.resource_max_live):
        x, y = free(r)
        apply(r, "PLACE_FOOD", x=x, y=y)
    before = r.simulation.world.to_dict(), r.simulation.event_sequence.value, r.simulation.rng.getstate()
    x, y = free(r)
    apply(r, "PLACE_WATER", x=x, y=y)
    assert "rejected" in r.last_editor_result
    assert before == (r.simulation.world.to_dict(), r.simulation.event_sequence.value, r.simulation.rng.getstate())


def test_live_workbench_status_and_queue_polling_are_inert():
    import time
    from main import create_native_observer
    r = runtime()
    r.run_until(.4)
    before = causal(r)
    observer = create_native_observer(r)
    controller = r._workbench_controller
    controller.paused = True
    assert observer.start()
    try:
        deadline = time.monotonic() + 5
        while observer.is_running and observer.frames_rendered < 8 and time.monotonic() < deadline:
            controller.poll()
            time.sleep(.01)
        if observer.frames_rendered < 8:
            pytest.skip("usable SDL3/OpenGL desktop unavailable")
        assert causal(r) == before
        assert observer.brain_snapshot_rebuilds == 1
    finally:
        observer.stop()


@pytest.mark.parametrize("field,value", [("id", True), ("text", " ")])
def test_corrupt_pending_dialogue_fails_closed(field, value):
    r = runtime()
    r.accept_editor_command("SEND_DIALOGUE", text="dax")
    state = r._editor_state()
    state["inbox"][0][field] = value
    with pytest.raises(ValueError):
        r._restore_editor_state(state)


def test_editor_continuation_is_hashseed_independent():
    import os
    import subprocess
    import sys
    script = """
import hashlib, json, runpy
helpers = runpy.run_path('tests/test_v090_workbench.py')
r = helpers['runtime']()
x, y = helpers['free'](r)
r.accept_editor_command('PLACE_FOOD', x=x, y=y)
r.accept_editor_command('PLACE_WATER', x=x, y=y)
r.accept_editor_command('SEND_DIALOGUE', text='dax zup')
r.run_until(.6)
print(hashlib.sha256(json.dumps(helpers['causal'](r), sort_keys=True, default=str).encode()).hexdigest())
"""
    outputs = [subprocess.check_output([sys.executable, "-B", "-c", script],
               cwd=Path(__file__).parents[1], env={**os.environ, "PYTHONHASHSEED": seed}, text=True)
               for seed in ("1", "777")]
    assert outputs[0] == outputs[1]
