from random import Random
from config import Settings
from world import Action,ActionType,World
from world.objects import WorldObject


def world()->World:
    w=World(Settings(object_count=0,perception_radius=4),Random(1));w.body.x=w.body.y=10;w.body.orientation="NORTH";return w


def test_fov_120_behind_not_visible_and_range_4()->None:
    w=world();w.objects=[WorldObject(1,10,6),WorldObject(2,10,11),WorldObject(3,10,5)]
    frame=w.perceive(0);positions={(c.relative_x,c.relative_y) for c in frame.cells if c.occupied}
    assert (0,-4) in positions and (0,1) not in positions and (0,-5) not in positions


def test_vision_rotates_with_body()->None:
    w=world();w.objects=[WorldObject(1,11,10)];assert not any(c.occupied for c in w.perceive(0).cells)
    w.apply_action(Action(ActionType.TURN_RIGHT));assert any(c.occupied for c in w.perceive(1).cells)
