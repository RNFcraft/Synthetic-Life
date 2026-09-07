from config import Settings
from simulation import MultiEntitySimulation
from world import Action,ActionResult,ActionType


def test_two_independent_entities_and_no_shared_graph()->None:
    sim=MultiEntitySimulation(2,5,Settings(object_count=0));assert len(sim.world.bodies)==2
    assert sim.cores[0].graph is not sim.cores[1].graph and sim.cores[0].memory is not sim.cores[1].memory


def test_same_world_observation_snapshot_and_other_not_semantic()->None:
    sim=MultiEntitySimulation(2,6,Settings(object_count=0));frames={i:sim.world.perceive(0,i) for i in sim.cores}
    assert frames[0].tick==frames[1].tick==0 and not hasattr(frames[0],"other_entity_id")


def test_simultaneous_commit_and_conflict_symmetry()->None:
    sim=MultiEntitySimulation(2,7,Settings(object_count=0));a,b=sim.world.bodies.values();a.x,a.y=4,5;b.x,b.y=6,5
    intents={0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.MOVE_LEFT)}
    first=sim.world.resolve_intents(intents);assert sorted(first.values(),key=lambda x:x.value)==[ActionResult.SUCCESS,ActionResult.BLOCKED]
    a.x,a.y=4,5;b.x,b.y=6,5;second=sim.world.resolve_intents(intents);assert first[0] is not second[0]
