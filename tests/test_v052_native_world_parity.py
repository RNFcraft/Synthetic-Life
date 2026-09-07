from random import Random

from config import Settings
from consciousness.native_engine import WorldRuntime
from world import Action,ActionResult,ActionType,World
from simulation.snapshot import decode_random_state,encode_random_state
from simulation import Simulation
from world import NativeWorld
from world.objects import WorldObject


def pair(seed,settings):
    oracle=World(settings,Random(seed));rng=Random(seed);count=min(settings.object_count,settings.max_objects)+max(1,settings.entity_count)
    positions=rng.sample([(x,y) for y in range(settings.world_height) for x in range(settings.world_width)],count)
    native=WorldRuntime(settings.world_width,settings.world_height,settings.perception_radius)
    native.initialize_multi([(i,*positions[i],'N',i+1) for i in range(max(1,settings.entity_count))],[(i+1,*p,0) for i,p in enumerate(positions[max(1,settings.entity_count):])])
    next_tick=(rng.randint(settings.spawn_interval_min,settings.spawn_interval_max) if settings.object_count<settings.max_objects else None)
    assert next_tick==oracle.next_spawn_tick
    native.configure_spawning(settings.max_objects,next_tick,len(oracle.objects)+1)
    return oracle,native


def state(world):
    bodies=sorted((b.id,b.x,b.y,b.orientation[0],b.held_object_id or 0,b.appearance) for b in world.bodies.values())
    objects=sorted((o.id,o.x,o.y,o.state) for o in world.objects);held=sorted((i,o.id,o.x,o.y,o.state) for i,o in world.held_objects.items())
    return bodies,objects,held,world.world_tick_count,world.next_spawn_tick,world.next_object_id,world.conflict_cursor,world.conflict_count,[world.fairness_wins[i] for i in sorted(world.fairness_wins)]


def frames_equal(oracle,native,tick,body_id):
    frame=oracle.perceive(tick,body_id);cells,body=native.perceive(tick,body_id)
    assert cells==[(c.relative_x,c.relative_y,c.occupied,c.state_channel,c.boundary,c.self_present,c.appearance_channel) for c in frame.cells]
    assert body==(frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right,frame.body.holding,frame.body.action_resistance)


def restore_native(source,settings,time=0.0,sequence=0):
    bodies,objects,held,tick,next_tick,next_id,cursor,conflicts,wins=source.full_state()
    restored=WorldRuntime(settings.world_width,settings.world_height,settings.perception_radius)
    restored.restore([(i,x,y,o,a) for i,x,y,o,_held,a in bodies],objects,held,[source.perceive(tick,i)[1][-1] for i,*_ in bodies],tick,next_tick,next_id,cursor,conflicts,wins,time,sequence,settings.max_objects)
    return restored


def test_seeded_initialization_and_spawn_rng_oracle_parity():
    settings=Settings(world_width=9,world_height=8,entity_count=2,object_count=2,max_objects=8,spawn_interval_min=2,spawn_interval_max=5)
    for seed in (1,19,5204):
        oracle,native=pair(seed,settings);assert native.full_state()==state(oracle)
        for tick in range(1,30):
            before={o.id for o in oracle.objects};expected=oracle.world_tick();created=next((o for o in oracle.objects if o.id not in before),None)
            actual=native.world_tick(None if created is None else created.position,oracle.next_spawn_tick)
            assert actual==expected;assert native.full_state()==state(oracle)
            for body_id in oracle.bodies:frames_equal(oracle,native,tick,body_id)


def test_multi_entity_conflict_and_fairness_parity():
    settings=Settings(world_width=12,world_height=12,entity_count=2,object_count=1,max_objects=1)
    oracle,native=pair(33,settings);oracle.objects[0].x,oracle.objects[0].y=5,5
    native.initialize_multi([(0,4,5,'E',1),(1,6,5,'W',2)],[(1,5,5,0)])
    for round_no in range(12):
        oracle.bodies[0].x,oracle.bodies[0].y,oracle.bodies[0].orientation=4,5,'EAST';oracle.bodies[1].x,oracle.bodies[1].y,oracle.bodies[1].orientation=6,5,'WEST'
        native.set_body_state(0,4,5,'E');native.set_body_state(1,6,5,'W')
        intents={0:Action(ActionType.INTERACT_RIGHT),1:Action(ActionType.INTERACT_LEFT)}
        expected=oracle.resolve_intents(intents);actual=native.resolve_intents([0,1],[ActionType.INTERACT_RIGHT.value,ActionType.INTERACT_LEFT.value])
        assert actual==[expected[0].value,expected[1].value];assert native.full_state()==state(oracle)
        frames_equal(oracle,native,round_no,0);frames_equal(oracle,native,round_no,1)
    assert abs(oracle.fairness_wins[0]-oracle.fairness_wins[1])<=1


def test_multi_entity_random_intent_trace_parity():
    settings=Settings(world_width=10,world_height=10,entity_count=3,object_count=8,max_objects=8);oracle,native=pair(71,settings);rng=Random(9917);actions=list(ActionType)
    for tick in range(1000):
        for body_id in oracle.bodies:frames_equal(oracle,native,tick,body_id)
        intents={i:Action(rng.choice(actions)) for i in oracle.bodies};expected=oracle.resolve_intents(intents);actual=native.resolve_intents(list(intents),[a.kind.value for a in intents.values()])
        assert actual==[expected[i].value for i in intents];assert native.full_state()==state(oracle)


def test_native_state_and_python_rng_continue_exactly_after_roundtrip():
    settings=Settings(world_width=9,world_height=9,entity_count=2,object_count=3,max_objects=7,spawn_interval_min=1,spawn_interval_max=3)
    oracle,native=pair(404,settings);actions=list(ActionType);action_rng=Random(88)
    for tick in range(40):
        intents={i:Action(action_rng.choice(actions)) for i in oracle.bodies};oracle.resolve_intents(intents);native.resolve_intents(list(intents),[a.kind.value for a in intents.values()]);oracle.world_tick()
        created=next((o for o in oracle.objects if o.id==oracle.next_object_id-1 and next((r for r in oracle.spawn_records if r['object_id']==o.id),{}).get('spawn_tick')==oracle.world_tick_count),None)
        native.world_tick(created.position if created else None,oracle.next_spawn_tick)
    rng_state=encode_random_state(oracle.rng.getstate());restored_rng=Random();restored_rng.setstate(decode_random_state(rng_state));restored=restore_native(native,settings,12.75,91)
    assert restored.full_state()==native.full_state();assert restored.time_state()==(12.75,91)
    for tick in range(40,100):
        intents={i:Action(action_rng.choice(actions)) for i in oracle.bodies};expected=oracle.resolve_intents(intents);actual=restored.resolve_intents(list(intents),[a.kind.value for a in intents.values()]);assert actual==[expected[i].value for i in intents]
        before={o.id for o in oracle.objects};expected_event=oracle.world_tick();created=next((o for o in oracle.objects if o.id not in before),None)
        spawn=None;next_tick=restored.full_state()[4]
        if next_tick is not None and restored.full_state()[3]+1>=next_tick:
            snapshot=restored.full_state();occupied={(x,y) for _id,x,y,_state in snapshot[1]}|{(x,y) for _id,x,y,*_ in snapshot[0]}
            free=[(x,y) for y in range(settings.world_height) for x in range(settings.world_width) if (x,y) not in occupied]
            if free:spawn=restored_rng.choice(free)
            count=len(snapshot[1])+(1 if snapshot[0][0][4] else 0)+(1 if spawn else 0)
            next_tick=snapshot[3]+1+restored_rng.randint(settings.spawn_interval_min,settings.spawn_interval_max) if count<settings.max_objects else None
        assert spawn==(created.position if created else None);assert restored_rng.getstate()==oracle.rng.getstate()
        assert restored.world_tick(spawn,next_tick)==expected_event
        assert restored.full_state()==state(oracle)


def test_normal_native_simulation_world_lockstep_and_seworld_continuation(tmp_path):
    settings=Settings(world_width=12,world_height=12,object_count=4,max_objects=7,spawn_interval_min=2,spawn_interval_max=4)
    python=Simulation(733,settings,"python");native=Simulation(733,settings,"native");assert isinstance(native.world,NativeWorld)
    for _ in range(100):
        left=python.step();right=native.step();assert (left.action,left.action_result,left.sensory_summary)==(right.action,right.action_result,right.sensory_summary);assert python.world.to_dict()==native.world.to_dict()
    path=tmp_path/"native-world.seworld";native.save_world(path);restored=Simulation.load_world(path,settings,"native");assert isinstance(restored.world,NativeWorld)
    for _ in range(25):
        left=native.step();right=restored.step();assert (left.action,left.action_result,left.sensory_summary)==(right.action,right.action_result,right.sensory_summary);assert native.world.to_dict()==restored.world.to_dict()


def controlled_case(bodies,objects=(),held=None):
    settings=Settings(world_width=8,world_height=8,entity_count=2,object_count=0,max_objects=0);oracle=World(settings,Random(1));oracle.objects=[WorldObject(i,x,y,state=state) for i,x,y,state in objects];oracle.next_object_id=max([x[0] for x in objects]+[0])+1
    for i,x,y,o in bodies:oracle.bodies[i].x=x;oracle.bodies[i].y=y;oracle.bodies[i].orientation={'N':'NORTH','E':'EAST','S':'SOUTH','W':'WEST'}[o]
    oracle.held_objects={};oracle.held_object=None
    if held:
        owner,obj=held;oracle.held_objects[owner]=WorldObject(*obj);oracle.bodies[owner].held_object_id=obj[0];oracle.held_object=oracle.held_objects.get(0)
    native=WorldRuntime(8,8,settings.perception_radius);native.restore([(i,x,y,o,i+1) for i,x,y,o in bodies],list(objects),[] if not held else [(held[0],*held[1][:3],held[1][4])],[0.,0.],0,None,max([x[0] for x in objects]+[0])+1,0,0,[0,0],0.,0,0)
    return oracle,native


def assert_case(bodies,objects,intents,held=None):
    oracle,native=controlled_case(bodies,objects,held);expected=oracle.resolve_intents(intents);actual=native.resolve_intents(list(intents),[a.kind.value for a in intents.values()]);assert actual==[expected[i].value for i in intents];assert native.full_state()==state(oracle)
    for i in oracle.bodies:frames_equal(oracle,native,0,i)


def test_explicit_simultaneous_conflict_matrix():
    # Same destination; direct swap; move into occupied body.
    assert_case([(0,1,2,'E'),(1,3,2,'W')],[],{0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.MOVE_LEFT)})
    assert_case([(0,1,2,'E'),(1,2,2,'W')],[],{0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.MOVE_LEFT)})
    assert_case([(0,1,2,'E'),(1,2,2,'N')],[],{0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.IDLE)})
    # Shared GRAB, push destination collision, and shared INTERACT.
    assert_case([(0,1,2,'E'),(1,3,2,'W')],[(1,2,2,0)],{0:Action(ActionType.GRAB_RIGHT),1:Action(ActionType.GRAB_LEFT)})
    assert_case([(0,1,2,'E'),(1,3,3,'N')],[(1,2,2,0)],{0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.MOVE_UP)})
    assert_case([(0,1,2,'E'),(1,3,2,'W')],[(1,2,2,0)],{0:Action(ActionType.INTERACT_RIGHT),1:Action(ActionType.INTERACT_LEFT)})


def test_explicit_release_held_motion_and_resistance():
    held=(0,(7,0,0,'generic',0,False))
    # RELEASE into occupied body is blocked and resistance is observable.
    assert_case([(0,1,2,'E'),(1,2,2,'W')],[],{0:Action(ActionType.RELEASE),1:Action(ActionType.IDLE)},held)
    # A carried object remains held while its owner moves.
    assert_case([(0,1,2,'E'),(1,5,5,'W')],[],{0:Action(ActionType.MOVE_RIGHT),1:Action(ActionType.IDLE)},held)


def test_normal_native_backend_never_calls_python_world_physics(monkeypatch):
    def forbidden(*_args,**_kwargs):raise AssertionError("Python World physical method called")
    for name in ("perceive","apply_action","resolve_intents","world_tick"):monkeypatch.setattr(World,name,forbidden)
    sim=Simulation(919,Settings(object_count=2,max_objects=4,spawn_interval_min=1,spawn_interval_max=1),"native")
    sim.run(10)
    assert sim.world.python_physical_calls==0
