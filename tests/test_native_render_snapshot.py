from consciousness.native_engine import WorldRuntime
from simulation import ContinuousRuntime
from world import ActionType


def test_snapshot_initial_action_spawn_restore_and_time():
    world=WorldRuntime(4,4,2);world.initialize_multi([(0,1,1,"N",7)],[(1,1,0,3)]);world.configure_spawning(5,None,2)
    initial=world.latest_render_snapshot()
    assert initial[:4]==(0.,0,4,4) and initial[4]==[(0,1,1,"N",7,0)] and initial[5]==[(1,1,0,3)] and initial[6]==[]
    world.apply_intent(4,.25,1);after=world.latest_render_snapshot()
    assert initial[4]==[(0,1,1,"N",7,0)] and after[0:2]==(.25,1)
    assert world.apply_spawn_event((2,2),.5,2)==2
    spawned=world.latest_render_snapshot();assert spawned[0:2]==(.5,2) and (2,2,2,0) in spawned[5]
    world.advance_world_time(1.);advanced=world.latest_render_snapshot();assert advanced[0:2]==(1.,2)
    before=(world.time_state(),world.full_state(),advanced)
    for _ in range(1000):assert world.latest_render_snapshot()==advanced
    assert (world.time_state(),world.full_state(),world.latest_render_snapshot())==before


def test_snapshot_held_and_restore_are_immediate():
    world=WorldRuntime(4,4,2);world.initialize_multi([(0,1,1,"N",1)],[(1,1,0,5)])
    world.apply(ActionType.GRAB_UP.value,0);held=world.latest_render_snapshot();assert held[4][0][-1]==1 and held[5]==[] and held[6]==[(0,1,5)]
    world.restore([(0,2,2,"E",1)],[(9,0,0,4)],[],[0.],0,None,10,0,0,[0],3.,7,10)
    restored=world.latest_render_snapshot();assert restored[0:2]==(3.,7) and restored[4][0][1:4]==(2,2,"E") and restored[5]==[(9,0,0,4)]


def test_native_snapshot_sampling_is_trajectory_invisible():
    plain=ContinuousRuntime(811);sampled=ContinuousRuntime(811)
    plain.run_until(2.)
    for point in (.4,.9,1.3,2.):
        for _ in range(100):sampled.simulation.world.native.latest_render_snapshot()
        sampled.run_until(point)
    assert (sampled.scheduler_state(),sampled.simulation.world.native.time_state(),sampled.simulation.rng.getstate(),sampled.simulation.world.to_dict(),sampled.cognition_generation,sampled.actions_completed,sampled.maintenance_ordinal)==(plain.scheduler_state(),plain.simulation.world.native.time_state(),plain.simulation.rng.getstate(),plain.simulation.world.to_dict(),plain.cognition_generation,plain.actions_completed,plain.maintenance_ordinal)
