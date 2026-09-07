from dataclasses import FrozenInstanceError
from random import Random
import pytest
from config import Settings
from world import Action,ActionResult,ActionType,World
from world.objects import WorldObject


def configured()->World:
    w=World(Settings(object_count=0,spawn_interval_min=100,spawn_interval_max=100),Random(1));w.body.x=w.body.y=5;return w


def test_world_30x30_spawn_schedule_and_limit()->None:
    w=World(Settings(object_count=0,max_objects=10,spawn_interval_min=1,spawn_interval_max=1),Random(2));assert (w.grid.width,w.grid.height)==(30,30)
    for _ in range(20):w.world_tick()
    assert len(w.objects)==10 and w.next_spawn_tick is None


def test_push_success_and_blocked()->None:
    w=configured();w.objects=[WorldObject(1,6,5)]
    assert w.apply_action(Action(ActionType.MOVE_RIGHT)) is ActionResult.SUCCESS
    assert (w.body.position,w.objects[0].position)==((6,5),(7,5))
    w.body.x=27;w.objects=[WorldObject(1,28,5),WorldObject(2,29,5)]
    assert w.apply_action(Action(ActionType.MOVE_RIGHT)) is ActionResult.BLOCKED


def test_grab_carry_release_and_interact()->None:
    w=configured();w.objects=[WorldObject(1,6,5,state=1)]
    assert w.apply_action(Action(ActionType.GRAB_RIGHT)) is ActionResult.SUCCESS and w.body.held_object_id==1
    assert w.apply_action(Action(ActionType.MOVE_UP)) is ActionResult.SUCCESS and w.held_object is not None
    assert w.apply_action(Action(ActionType.RELEASE)) is ActionResult.SUCCESS
    obj=w.object_at((5,3));assert obj is not None and obj.state==1
    assert w.apply_action(Action(ActionType.INTERACT_UP)) is ActionResult.SUCCESS and obj.state==0


def test_body_sense_is_immutable_and_nonsemantic()->None:
    w=configured();w.objects=[WorldObject(1,6,5)];frame=w.perceive(0)
    assert frame.body.touch_right and not hasattr(frame.body,"object_id") and not hasattr(frame.body,"blocked_by")
    w.apply_action(Action(ActionType.MOVE_LEFT));w.body.x=0;w.apply_action(Action(ActionType.MOVE_LEFT));assert w.perceive(1).body.action_resistance==1
    with pytest.raises(FrozenInstanceError):frame.body.holding=True


def test_no_world_or_semantic_outcome_leak()->None:
    from pathlib import Path
    source="\n".join(p.read_text(encoding="utf-8") for p in Path("consciousness").glob("*.py"))
    assert "import World" not in source and "import Grid" not in source and "import WorldObject" not in source
    assert "ActionResult" not in source
