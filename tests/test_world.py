from random import Random
from config import Settings
from world import Action, ActionResult, ActionType, World


def test_spawn_has_no_overlap() -> None:
    world = World(Settings(), Random(7))
    positions = [world.body.position] + [o.position for o in world.objects]
    assert len(set(positions)) == 26
    assert world.grid.width == world.grid.height == 30


def test_entity_cannot_leave_world() -> None:
    world = World(Settings(), Random(1)); world.body.x = world.body.y = 0
    assert world.apply_action(Action(ActionType.MOVE_LEFT)) is ActionResult.BLOCKED
    assert world.apply_action(Action(ActionType.MOVE_UP)) is ActionResult.BLOCKED


def test_spawned_objects_do_not_move_autonomously() -> None:
    world = World(Settings(spawn_interval_min=1,spawn_interval_max=1), Random(9))
    world.world_tick();positions={o.id:o.position for o in world.objects}
    for _ in range(100):world.world_tick()
    assert all(positions.get(o.id,o.position)==o.position for o in world.objects)
