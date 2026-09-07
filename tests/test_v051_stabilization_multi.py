from config import Settings
from simulation import MultiEntitySimulation,Simulation
from world import Action,ActionResult,ActionType
from world.objects import WorldObject

def setup()->MultiEntitySimulation:
    sim=MultiEntitySimulation(2,81,Settings(object_count=0,place_birth_visits=1));a,b=sim.world.bodies.values();a.x,a.y,a.orientation=5,5,"EAST";b.x,b.y=7,5;return sim

def test_body_resistance_and_outcome_are_per_entity()->None:
    sim=setup();results=sim.world.resolve_intents({0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.IDLE)})
    assert results[0] is ActionResult.SUCCESS and sim.world.body_resistance[0]==0 and sim.world.body_resistance[1]==0
    sim.world.bodies[0].x=6;results=sim.world.resolve_intents({0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.IDLE)})
    assert results[0] is ActionResult.BLOCKED and sim.world.body_resistance[0]==1 and sim.world.body_outcomes[1]=="IDLE"

def test_push_and_release_cannot_enter_other_body()->None:
    sim=setup();a,b=sim.world.bodies.values();sim.world.objects=[WorldObject(1,6,5)]
    assert sim.world.apply_action(Action(ActionType.MOVE_RIGHT),0) is ActionResult.BLOCKED
    sim.world.objects=[];a.held_object_id=2;sim.world.held_objects[0]=WorldObject(2,0,0);a.x=6
    assert sim.world.apply_action(Action(ActionType.RELEASE),0) is ActionResult.BLOCKED

def test_two_grab_same_object_conflict_is_fair_and_order_independent()->None:
    def run(reverse):
        sim=setup();sim.world.bodies[0].x=5;sim.world.bodies[1].x=7;sim.world.objects=[WorldObject(1,6,5)]
        pairs=[(0,Action(ActionType.GRAB_RIGHT)),(1,Action(ActionType.GRAB_LEFT))];return sim.world.resolve_intents(dict(reversed(pairs)) if reverse else dict(pairs))
    assert run(False)==run(True) and sorted(run(False).values(),key=lambda x:x.value)==[ActionResult.SUCCESS,ActionResult.BLOCKED]

def test_other_entity_memory_reactivation_without_entity_id()->None:
    sim=setup();core=sim.cores[0];frame=sim.world.perceive(0,0);core.step(frame);before=len(core.memory.structures)
    sim.world.bodies[1].x=20
    for tick in range(1,6):core.step(sim.world.perceive(tick,0))
    sim.world.bodies[1].x=7;core.step(sim.world.perceive(6,0))
    assert before>0 and core.memory.reactivation_count>0 and not hasattr(frame,"other_entity_id")

def test_multi_seworld_roundtrip_and_deterministic_continuation(tmp_path)->None:
    sim=MultiEntitySimulation(2,82,Settings(object_count=2));sim.run(3);path=tmp_path/"multi.seworld";sim.save_world(path)
    a=MultiEntitySimulation.load_world(path);b=MultiEntitySimulation.load_world(path);actions_a=[];actions_b=[]
    for _ in range(3):actions_a.append(a.step());actions_b.append(b.step())
    assert actions_a==actions_b and a.snapshot_data()==b.snapshot_data()

def test_sebrain_starts_fresh_transient_episode(tmp_path)->None:
    trained=Simulation(83);trained.run(3);path=tmp_path/"brain.sebrain";trained.save_brain(path);fresh=Simulation(99);fresh.load_brain(path)
    assert fresh.core.trace.entries==fresh.core.trace.entries.__class__() and fresh.core.state.goal is None and not fresh.core.perception.tracks
