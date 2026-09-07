from random import Random
import pytest

from config import Settings
from consciousness.native_engine import WorldRuntime
from world import Action,ActionType,World


def test_native_world_single_entity_action_and_sensory_lockstep_1000():
    settings=Settings(world_width=12,world_height=12,object_count=0,perception_radius=4)
    python=World(settings,Random(19));python.body.x=5;python.body.y=5;python.body.orientation='NORTH'
    positions=[(5,3),(7,5),(4,7)];python.initialize_controlled_objects(positions)
    native=WorldRuntime(12,12,4);native.initialize(5,5,'N',positions)
    actions=list(ActionType);rng=Random(991)
    for tick in range(1000):
        frame=python.perceive(tick);cells,body=native.perceive(tick)
        assert cells==[(c.relative_x,c.relative_y,c.occupied,c.state_channel,c.boundary,c.self_present,c.appearance_channel) for c in frame.cells]
        assert body==(frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right,frame.body.holding,frame.body.action_resistance)
        action=rng.choice(actions);expected=python.apply_action(Action(action));actual=native.apply(action.value)
        assert actual==expected.value
        x,y,orientation,held,objects,resistance=native.state()
        assert (x,y)==python.body.position and orientation==python.body.orientation[0]
        assert (held or None)==python.body.held_object_id and resistance==python.last_resistance
        assert sorted(objects)==sorted((o.id,o.x,o.y,o.state) for o in python.objects)
    native.apply_intent(ActionType.IDLE.value,12.274,1)
    assert native.time_state()==(12.274,1)
    with pytest.raises(ValueError):native.apply_intent(ActionType.IDLE.value,12.0,2)
