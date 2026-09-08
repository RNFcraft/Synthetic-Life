from dataclasses import replace
from pathlib import Path
from random import Random

import pytest

from config import Settings
from consciousness.native_engine import EventScheduler, RuntimeEvent, RuntimeEventType
from simulation import ContinuousRuntime
from world import Action, ActionType
from world.native_world import NativeWorld
from persistence import load_container, save_container


def _spawn_events(runtime):
    return [(e.time, e.id) for e in runtime.scheduler.snapshot() if e.type == RuntimeEventType.WORLD_SPAWN]

def _behavior_state(runtime):
    time, sequence=runtime.simulation.world.native.time_state()
    frontier=runtime.simulation.core.continuous_frontier
    return (runtime.scheduler_state(),runtime.simulation.event_sequence.value,time,sequence,runtime.simulation.rng.getstate(),runtime.simulation.world.to_dict(),runtime.maintenance_ordinal,runtime.cognition_generation,runtime.actions_completed,None if frontier is None else (frontier.generation,frontier.phase,frontier.committed))

def _roundtrip(runtime,tmp_path,name="world"):
    path=Path(tmp_path)/f"{name}.seworld";runtime.save_world(path);return ContinuousRuntime.load_world(path,runtime.simulation.settings)


def test_continuous_world_never_uses_legacy_heartbeat(monkeypatch):
    monkeypatch.setattr(NativeWorld, "world_tick", lambda *_: (_ for _ in ()).throw(AssertionError("legacy heartbeat")))
    settings = replace(Settings(), object_count=0, max_objects=2, spawn_interval_min=1, spawn_interval_max=1)
    runtime = ContinuousRuntime(700, settings)
    runtime.run_until(2.1)
    assert runtime.simulation.world.world_tick_count == 0
    assert len(runtime.simulation.world.objects) == 2


def test_spawn_deadline_is_absolute_and_partition_invariant():
    settings = replace(Settings(), object_count=0, max_objects=4, spawn_interval_min=2, spawn_interval_max=2)
    whole, partitioned = ContinuousRuntime(701, settings), ContinuousRuntime(701, settings)
    whole.run_until(8.0)
    for point in (1.0, 3.5, 6.25, 8.0):
        partitioned.run_until(point)
    assert partitioned.scheduler_state() == whole.scheduler_state()
    assert partitioned.simulation.world.to_dict() == whole.simulation.world.to_dict()
    assert partitioned.simulation.rng.getstate() == whole.simulation.rng.getstate()


def test_subsecond_spawn_advances_native_time_and_event_sequence():
    runtime = ContinuousRuntime(702, replace(Settings(), object_count=0, max_objects=2))
    event_id = runtime.scheduler.schedule(.437, RuntimeEventType.WORLD_SPAWN)
    runtime.run_until(.437)
    time, sequence = runtime.simulation.world.native.time_state()
    assert time == pytest.approx(.437)
    assert sequence == runtime.simulation.event_sequence.value
    assert sequence != event_id  # scheduler insertion order is not physical execution order


def test_save_load_preserves_spawn_rng_frontier(tmp_path):
    settings = replace(Settings(), object_count=0, max_objects=4, spawn_interval_min=1, spawn_interval_max=3)
    direct, saved = ContinuousRuntime(703, settings), ContinuousRuntime(703, settings)
    direct.run_until(.99); saved.run_until(.99)
    path = tmp_path / "world-timer.seworld"; saved.save_world(path)
    restored = ContinuousRuntime.load_world(path, settings)
    direct.run_until(9.0); restored.run_until(9.0)
    assert restored.simulation.world.to_dict() == direct.simulation.world.to_dict()
    assert restored.simulation.rng.getstate() == direct.simulation.rng.getstate()
    assert _spawn_events(restored) == _spawn_events(direct)


def test_low_scheduler_spawn_id_advances_physical_sequence_at_execution():
    settings = replace(Settings(), object_count=0, max_objects=3, spawn_interval_min=2, spawn_interval_max=2)
    runtime = ContinuousRuntime(704, settings)
    spawn = next(e for e in runtime.scheduler.snapshot() if e.type == RuntimeEventType.WORLD_SPAWN)
    runtime.run_until(1.95)
    before = runtime.simulation.event_sequence.value
    assert spawn.id < before
    runtime.run_until(2.0)
    assert runtime.simulation.event_sequence.value == before + 1
    runtime.run_until(2.1)
    assert runtime.simulation.event_sequence.value == before + 2


def test_maintenance_enters_exact_continuous_world_time_without_cognitive_tick():
    settings = replace(Settings(), continuous_maintenance_interval_seconds=10.0)
    runtime = ContinuousRuntime(705, settings)
    runtime.scheduler.schedule(.437, RuntimeEventType.MAINTENANCE)
    runtime.run_until(.437)
    elapsed = runtime.simulation.core.backend.engine.continuous_time_state()
    assert elapsed[2] == pytest.approx(.437)


@pytest.mark.parametrize("order", ((RuntimeEventType.WORLD_SPAWN, RuntimeEventType.WORLD_ACTION_COMPLETE), (RuntimeEventType.WORLD_ACTION_COMPLETE, RuntimeEventType.WORLD_SPAWN)))
def test_same_time_physical_events_follow_scheduler_insertion_order(monkeypatch, order):
    runtime = ContinuousRuntime(706, replace(Settings(), object_count=0, max_objects=3))
    runtime.scheduler = EventScheduler()
    runtime.scheduler.restore(0.0, 100, [])
    monkeypatch.setattr(runtime.simulation.world, "continuous_spawn_position", lambda: (0, 1))
    for kind in order:
        runtime.scheduler.schedule(.437, kind, ActionType.IDLE.value if kind == RuntimeEventType.WORLD_ACTION_COMPLETE else 0)
    events = runtime.scheduler.pop_ready(.437)
    assert [event.type for event in events] == list(order)
    for event in events:
        runtime._process(event)
    assert runtime.simulation.event_sequence.value == 2
    assert runtime.simulation.world.native.time_state()[1] == 2


def test_full_capacity_spawn_preserves_rng_and_physical_sequence():
    runtime = ContinuousRuntime(707, replace(Settings(), object_count=1, max_objects=1))
    runtime.scheduler = EventScheduler(); runtime.scheduler.restore(0.0, 10, [])
    runtime.scheduler.schedule(.5, RuntimeEventType.WORLD_SPAWN)
    before_rng, before_sequence = runtime.simulation.rng.getstate(), runtime.simulation.event_sequence.value
    event = runtime.scheduler.pop_ready(.5)[0]; runtime._process(event)
    assert runtime.simulation.rng.getstate() == before_rng
    assert runtime.simulation.event_sequence.value == before_sequence
    assert not _spawn_events(runtime)


def test_blocked_spawn_does_not_consume_position_draw_but_reschedules(monkeypatch):
    settings = replace(Settings(), world_width=1, world_height=1, object_count=0, max_objects=2, spawn_interval_min=3, spawn_interval_max=3)
    runtime = ContinuousRuntime(708, settings)
    runtime.scheduler = EventScheduler(); runtime.scheduler.restore(0.0, 10, [])
    runtime.scheduler.schedule(.5, RuntimeEventType.WORLD_SPAWN)
    choice_calls = []
    original_choice = runtime.simulation.rng.choice
    monkeypatch.setattr(runtime.simulation.rng, "choice", lambda values: choice_calls.append(values) or original_choice(values))
    event = runtime.scheduler.pop_ready(.5)[0]; runtime._process(event)
    assert choice_calls == []
    assert runtime.simulation.event_sequence.value == 0
    assert _spawn_events(runtime) == [(3.5, 11)]

def test_physical_event_sequence_survives_save_load(tmp_path):
    settings=replace(Settings(),object_count=0,max_objects=3,spawn_interval_min=1,spawn_interval_max=1)
    runtime=ContinuousRuntime(709,settings);runtime.run_until(1.2);before=runtime.simulation.event_sequence.value
    assert before==runtime.simulation.world.native.time_state()[1] and before>0
    restored=_roundtrip(runtime,tmp_path,"sequence")
    assert restored.simulation.event_sequence.value==restored.simulation.world.native.time_state()[1]==before
    for expected in (before+1,before+2):
        while True:
            event=restored.scheduler.snapshot()[0]
            for ready in restored.scheduler.pop_ready(event.time):
                was=restored.simulation.event_sequence.value;restored._process(ready)
                if restored.simulation.event_sequence.value!=was:break
            if restored.simulation.event_sequence.value==expected:break
        assert restored.simulation.event_sequence.value==expected

def test_v3_world_migrates_to_v4_without_rng_draw(tmp_path):
    settings=replace(Settings(),object_count=0,max_objects=3,spawn_interval_min=5,spawn_interval_max=5)
    source=ContinuousRuntime(710,settings);source.run_until(.4);current=source.world_time;legacy=7
    v4=Path(tmp_path)/"v4.seworld";source.save_world(v4);data=load_container(v4,"world",{"META","STATE","CONT","NBRN"})
    data["META"]["version"]=3;data["STATE"]["world"]["next_spawn_tick"]=legacy;data["CONT"]["scheduler"]["events"]=[e for e in data["CONT"]["scheduler"]["events"] if e[2] not in {"WORLD_SPAWN","MAINTENANCE"}]
    v3=Path(tmp_path)/"v3.seworld";save_container(v3,"world",data,{"NBRN"});rng=data["STATE"]["random_state"]
    migrated=ContinuousRuntime.load_world(v3,settings);spawns=_spawn_events(migrated);maint=[e for e in migrated.scheduler.snapshot() if e.type==RuntimeEventType.MAINTENANCE]
    assert spawns and spawns[0][0]==max(current,float(legacy));assert len(maint)==1 and maint[0].time==current+settings.continuous_maintenance_interval_seconds
    assert migrated.simulation.world.next_spawn_tick is None and migrated.simulation.snapshot_data()["random_state"]==rng
    out=Path(tmp_path)/"migrated.seworld";migrated.save_world(out);assert load_container(out,"world",{"META","STATE","CONT","NBRN"})["META"]["version"]==4

@pytest.mark.parametrize("boundary",(.99,1.0,1.01,1.15,1.2,1.35))
def test_continuous_world_persistence_matrix(tmp_path,boundary):
    settings=replace(Settings(),object_count=0,max_objects=4,spawn_interval_min=1,spawn_interval_max=2)
    direct=ContinuousRuntime(711,settings);saved=ContinuousRuntime(711,settings);loaded=ContinuousRuntime(711,settings)
    for runtime in (direct,saved,loaded):runtime.run_until(boundary)
    saved.save_world(Path(tmp_path)/f"save-{boundary}.seworld");loaded=_roundtrip(loaded,tmp_path,f"load-{boundary}")
    for runtime in (direct,saved,loaded):runtime.run_until(3.0)
    assert _behavior_state(direct)==_behavior_state(saved)==_behavior_state(loaded)

def _spawn_at(runtime, monkeypatch, position, now=.5):
    runtime.scheduler=EventScheduler();runtime.scheduler.restore(0.,10,[]);runtime.scheduler.schedule(now,RuntimeEventType.WORLD_SPAWN)
    monkeypatch.setattr(runtime.simulation.world,"continuous_spawn_position",lambda:position)
    event=runtime.scheduler.pop_ready(now)[0];runtime._process(event)

def test_visible_spawn_schedules_one_sensory_change(monkeypatch):
    runtime=ContinuousRuntime(712,replace(Settings(),world_width=4,world_height=4,object_count=0,max_objects=2));world=runtime.simulation.world
    world.native.set_body_state(0,1,1,"N");world._refresh();before=runtime._sensory_signature();ordinal,generation=runtime.observation_ordinal,runtime.cognition_generation
    _spawn_at(runtime,monkeypatch,(1,0));assert runtime._sensory_signature()!=before
    sensory=[e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.SENSORY_CHANGE];assert len(sensory)==1
    runtime._process(runtime.scheduler.pop_ready(.5)[0]);assert runtime.observation_ordinal==ordinal+1 and runtime.cognition_generation==generation+1

def test_invisible_spawn_does_not_wake_cognition(monkeypatch):
    runtime=ContinuousRuntime(713,replace(Settings(),world_width=8,world_height=8,object_count=0,max_objects=2));world=runtime.simulation.world
    world.native.set_body_state(0,1,1,"N");world._refresh();before=runtime._sensory_signature();ordinal,generation=runtime.observation_ordinal,runtime.cognition_generation
    _spawn_at(runtime,monkeypatch,(7,7));assert runtime._sensory_signature()==before
    assert runtime.observation_ordinal==ordinal and runtime.cognition_generation==generation
    assert not [e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.SENSORY_CHANGE]

def test_held_object_counts_toward_spawn_capacity():
    runtime=ContinuousRuntime(714,replace(Settings(),world_width=4,world_height=4,object_count=1,max_objects=1));world=runtime.simulation.world
    before=(runtime.simulation.rng.getstate(),runtime.simulation.event_sequence.value,world.to_dict())
    runtime.scheduler=EventScheduler();runtime.scheduler.restore(0.,10,[]);runtime.scheduler.schedule(.5,RuntimeEventType.WORLD_SPAWN);runtime._process(runtime.scheduler.pop_ready(.5)[0])
    assert (runtime.simulation.rng.getstate(),runtime.simulation.event_sequence.value,world.to_dict())==before and not _spawn_events(runtime)

def test_visible_spawn_invalidates_old_cognition_generation(monkeypatch):
    runtime=ContinuousRuntime(715,replace(Settings(),world_width=4,world_height=4,object_count=0,max_objects=2));world=runtime.simulation.world
    world.native.set_body_state(0,1,1,"N");world._refresh()
    for event in runtime.scheduler.pop_ready(0.):runtime._process(event)
    wake=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.COGNITION_WAKE);runtime._process(wake)
    old=runtime.cognition_generation;assert any(e.type==RuntimeEventType.COGNITION_CONTINUE for e in runtime.scheduler.snapshot())
    monkeypatch.setattr(world,"continuous_spawn_position",lambda:(1,0));runtime._process(RuntimeEvent(0.,999,RuntimeEventType.WORLD_SPAWN,0))
    sensory=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.SENSORY_CHANGE);runtime._process(sensory)
    frontier=runtime.simulation.core.continuous_frontier;state=(frontier.generation,frontier.phase,list(frontier.session.pending_work) if frontier.session else None);seq=runtime.simulation.event_sequence.value
    runtime._process(RuntimeEvent(0.,1000,RuntimeEventType.COGNITION_CONTINUE,old))
    f=runtime.simulation.core.continuous_frontier;assert runtime.cognition_generation==old+1 and (f.generation,f.phase,list(f.session.pending_work) if f.session else None)==state and runtime.simulation.event_sequence.value==seq

def test_visible_spawn_during_action_in_flight_does_not_overlap(monkeypatch):
    runtime=ContinuousRuntime(716,replace(Settings(),world_width=4,world_height=4,object_count=0,max_objects=2));world=runtime.simulation.world
    world.native.set_body_state(0,1,1,"N");world._refresh();runtime.run_to_quiescence();pending=[e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE];assert len(pending)==1
    monkeypatch.setattr(world,"continuous_spawn_position",lambda:(1,0));runtime._process(RuntimeEvent(0.,999,RuntimeEventType.WORLD_SPAWN,0));assert len([e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE])==1
    runtime._process(pending[0]);assert runtime.actions_completed==1

def test_real_held_object_counts_toward_capacity():
    runtime=ContinuousRuntime(717,replace(Settings(),world_width=4,world_height=4,object_count=1,max_objects=1));world=runtime.simulation.world
    world.native.set_body_state(0,1,1,"N");world._refresh();world.native.initialize_multi([(0,1,1,"N",1)],[(1,1,0,0)]);world._refresh();assert world.apply_action(Action(ActionType.GRAB_UP)).name=="SUCCESS"
    assert len(world.objects)<1 and len(world.objects)+len(world.held_objects)==1
    before=(runtime.simulation.rng.getstate(),runtime.simulation.event_sequence.value,world.to_dict());runtime._process(RuntimeEvent(.5,999,RuntimeEventType.WORLD_SPAWN,0))
    assert (runtime.simulation.rng.getstate(),runtime.simulation.event_sequence.value,world.to_dict())==before

def test_spawn_rng_matches_row_major_oracle():
    settings=replace(Settings(),world_width=4,world_height=4,object_count=0,max_objects=3,spawn_interval_min=1,spawn_interval_max=3);runtime=ContinuousRuntime(718,settings);world=runtime.simulation.world;oracle=Random();oracle.setstate(runtime.simulation.rng.getstate());now=0.
    for _ in range(3):
        free=[(x,y) for y in range(world.grid.height) for x in range(world.grid.width) if (x,y) not in {o.position for o in world.objects}|{b.position for b in world.bodies.values()}];expected=oracle.choice(free);before={o.id for o in world.objects};events_before=set(_spawn_events(runtime));runtime._process(RuntimeEvent(now,999,RuntimeEventType.WORLD_SPAWN,0));new=next(o for o in world.objects if o.id not in before);assert new.position==expected
        if world.can_spawn_more():interval=oracle.randint(settings.spawn_interval_min,settings.spawn_interval_max);next_time=next(time for time,_ in _spawn_events(runtime) if (time,_) not in events_before);assert next_time==now+interval
        assert runtime.simulation.rng.getstate()==oracle.getstate();now+=1

def test_maintenance_defers_at_same_time_during_cognition(monkeypatch):
    runtime=ContinuousRuntime(719);runtime.scheduler=EventScheduler();runtime.scheduler.restore(0.,10,[]);runtime.scheduler.schedule(0.,RuntimeEventType.SENSORY_CHANGE)
    runtime._process(runtime.scheduler.pop_ready(0.)[0]);frontier=runtime.simulation.core.continuous_frontier;assert frontier.phase=="OBSERVED";calls=[];original=runtime.simulation.core.continuous_maintenance
    monkeypatch.setattr(runtime.simulation.core,"continuous_maintenance",lambda *a:(calls.append(a),original(*a))[1]);runtime.scheduler.schedule(0.,RuntimeEventType.MAINTENANCE);ready=runtime.scheduler.pop_ready(0.);runtime._process(next(e for e in ready if e.type==RuntimeEventType.COGNITION_WAKE));event=next(e for e in ready if e.type==RuntimeEventType.MAINTENANCE);runtime._process(event)
    deferred=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.MAINTENANCE);assert calls==[] and deferred.time==0. and deferred.id>event.id
    runtime.run_to_quiescence();assert len(calls)==1 and runtime.maintenance_ordinal==1

def test_renderer_host_work_and_partition_are_observational():
    settings=replace(Settings(),object_count=0,max_objects=3,spawn_interval_min=1,spawn_interval_max=2);plain=ContinuousRuntime(720,settings);sampled=ContinuousRuntime(720,settings)
    plain.run_until(3.); 
    for point in (.4,1.,1.7,3.):
        for _ in range(20):sampled.render_snapshot()
        sum(i*i for i in range(1000));sampled.run_until(point)
    assert _behavior_state(sampled)==_behavior_state(plain)

def test_maintenance_cadence_depends_only_on_world_time(monkeypatch):
    settings=replace(Settings(),continuous_maintenance_interval_seconds=.5)
    def run(seed,sample):
        runtime=ContinuousRuntime(seed,settings);times=[];original=runtime.simulation.core.continuous_maintenance
        monkeypatch.setattr(runtime.simulation.core,"continuous_maintenance",lambda now,ordinal:(times.append(now),original(now,ordinal))[1])
        for point in (.4,1.,1.6,2.):
            for _ in range(sample):runtime.render_snapshot()
            runtime.run_until(point)
        return times
    assert run(721,0)==run(721,20)==[.5,1.,1.5,2.]
