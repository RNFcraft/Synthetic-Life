from random import Random
from config import Settings
from world import World


def test_frame_is_forward_cone_range_four_and_relative() -> None:
    world = World(Settings(), Random(2)); world.body.x = world.body.y = 12
    frame = world.perceive(0)
    assert frame.side == 9 and len(frame.cells) == 29
    assert all(y < 0 or (x,y)==(0,0) for x,y in ((c.relative_x,c.relative_y) for c in frame.cells))
    assert not hasattr(frame, "world") and not hasattr(frame, "entity_position")


def test_edges_are_reported_as_boundaries() -> None:
    world = World(Settings(), Random(2)); world.body.x = world.body.y = 0
    frame = world.perceive(0)
    assert sum(c.boundary for c in frame.cells) == 28
    assert next(c for c in frame.cells if (c.relative_x,c.relative_y)==(0,0)).self_present
