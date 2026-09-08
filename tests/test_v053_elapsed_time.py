import pytest
from consciousness.elapsed_time import CognitElapsedState,GoalElapsedState,LazyCognitStore,MemoryElapsedState,RelationElapsedState
from consciousness.native_engine import NativeBrainEngine
from consciousness.memory import PersistentStructureMemory,SpatialMemory
from consciousness.state import Goal
from consciousness import SyntheticEntityCore
from config import Settings

POLICY=(.95,.025,.12,.9,.72,.999)
def cognit():return CognitElapsedState(.8,.7,.4,.3,.08,10.)

@pytest.mark.parametrize("parts",((.001,0.),(.1,.2),(.25,.75),(1.,0.),(10.,0.),(1000.,0.)))
def test_cognit_elapsed_composition(parts):
    a,b=cognit(),cognit();a.materialize(10.+sum(parts),*POLICY);b.materialize(10.+parts[0],*POLICY);b.materialize(10.+sum(parts),*POLICY)
    assert a.activity==pytest.approx(b.activity,rel=1e-13,abs=1e-13);assert a.utility==pytest.approx(b.utility,rel=1e-13,abs=1e-13);assert a.activity_trace==pytest.approx(b.activity_trace,rel=1e-13,abs=1e-13);assert a.homeostatic_threshold==pytest.approx(b.homeostatic_threshold,rel=1e-12,abs=1e-12)

def test_relation_and_memory_touch_frequency_invariance():
    a,b=RelationElapsedState(.8),RelationElapsedState(.8)
    a.materialize(10.,.9995)
    for i in range(1,101):b.materialize(i/10,.9995)
    assert a.confidence==pytest.approx(b.confidence,rel=1e-13)
    m=MemoryElapsedState(.7,2.);m.materialize(10.,.9995);assert m.recency(10.,256)==pytest.approx(__import__('math').exp(-8/256))

def test_goal_subsecond_durations():
    g=GoalElapsedState(12.1,12.25,12.75);assert g.age(12.4)==pytest.approx(.3);assert g.unavailable_duration(12.4)==pytest.approx(.15);assert g.cooling_down(12.4)

def test_large_quiescent_jump_is_constant_then_touched_only():
    store=LazyCognitStore();store.states={i:CognitElapsedState(.8,.7,.4,.3,.08) for i in range(100000)};store.advance(1000.);assert store.materialization_work==0
    store.touch((7,19),*POLICY);assert store.materialization_work==2 and store.states[8].last_touch_time==0.


def test_native_cognit_uses_absolute_elapsed_time_and_matches_formula():
    engine=NativeBrainEngine();engine.add_cognit(.8,.25,.5)
    engine.set_cognit_fields([0,0,0,0],[3,7,6,8],[.7,.4,.3,.08])
    engine.begin_continuous_time(10.,*POLICY,.9995)
    engine.materialize_cognits_at([0],20.)
    expected=cognit();expected.materialize(20.,*POLICY)
    row=engine.cognit_state_full([0])
    assert row[0]==pytest.approx(expected.activity,rel=1e-13)
    assert row[3]==pytest.approx(expected.utility,rel=1e-13)
    assert row[7]==pytest.approx(expected.activity_trace,rel=1e-13)
    assert row[6]==pytest.approx(expected.homeostatic_threshold,rel=1e-13)


def test_native_cognit_touch_frequency_invariance():
    def make():
        e=NativeBrainEngine();e.add_cognit(.8,.25,.5);e.set_cognit_fields([0,0,0,0],[3,7,6,8],[.7,.4,.3,.08]);e.begin_continuous_time(10.,*POLICY,.9995);return e
    once,many=make(),make();once.materialize_cognits_at([0],20.)
    for n in range(1,101):many.materialize_cognits_at([0],10.+n/10)
    assert once.cognit_state_full([0])==pytest.approx(many.cognit_state_full([0]),rel=1e-12,abs=1e-12)


def test_native_quiescent_advance_materializes_only_touched_cognits():
    engine=NativeBrainEngine();engine.add_cognits(100_000,.8,.25,.5);engine.begin_continuous_time(1000.,*POLICY,.9995)
    enabled,epoch,now,frontiers,last_active,latent,work=engine.continuous_time_state()
    assert enabled and now==1000. and work==0 and len(frontiers)==100_000
    engine.materialize_cognits_at([7,19],2000.)
    assert engine.continuous_time_state()[6]==2


def test_native_elapsed_frontier_round_trip():
    source=NativeBrainEngine();source.add_cognits(3,.8,.25,.5);source.begin_continuous_time(12.437,*POLICY,.9995);source.materialize_cognits_at([1],12.999)
    state=source.continuous_time_state();restored=NativeBrainEngine();restored.add_cognits(3,.8,.25,.5);restored.restore_continuous_time_state(*state)
    assert restored.continuous_time_state()==state


def test_native_relation_consumers_share_one_elapsed_confidence_frontier():
    engine=NativeBrainEngine();engine.add_cognits(2,1.,.25,.5)
    handle=engine.add_relation(0,1,5,1,1.,.8,1.)
    engine.begin_continuous_time(10.,*POLICY,.9995);engine.begin_continuous_time(20.,*POLICY,.9995)
    engine.predict_actions_batch_at([0],[1],999,.9995)
    expected=.8*.9995**10
    assert engine.relation_state(0,handle)[5]==pytest.approx(expected,rel=1e-13)
    engine.action_effects_batch([0],[1],0.)
    engine.propagate([0],1)
    assert engine.relation_state(0,handle)[5]==pytest.approx(expected,rel=1e-13)
    rows,work=engine.continuous_relation_time_state()
    assert work==1 and rows[0][4]==20. and rows[0][5]==10.


def test_continuous_memory_ages_only_indexed_candidates():
    memory=SpatialMemory(Settings());memory.structures={i:PersistentStructureMemory(i,i,((i,0,"occupied",1),),i,(0.,0.),(1,),.8,0,last_confirmed_time_seconds=0.,last_touch_time_seconds=0.) for i in range(1,10_001)}
    memory._rebuild_indexes();memory.set_world_time(0.);memory.set_world_time(1000.)
    assert memory.materialization_work==0
    memory._match_structure(((7,0,"occupied",1),),(),0,0)
    assert memory.last_retrieval_candidates==1 and memory.materialization_work==1


def test_actual_goal_keeps_age_as_count_and_uses_elapsed_persistence():
    settings=Settings();core=SyntheticEntityCore(settings);core.world_time_seconds=20.
    goal=Goal(1,(1,),1.,.5,.5,created_time_seconds=10.,last_touch_time_seconds=10.);core.state.goal=goal;core.state.novelty=0.;core.state.prediction_error=0.
    core._update_goal(set())
    assert goal.age==1 and goal.persistence==pytest.approx(.85*settings.goal_decay**10*(1-settings.goal_understanding_decay),rel=1e-13)


def test_continuous_runtime_passes_exact_event_timestamp_to_native_cognition():
    from simulation import ContinuousRuntime
    runtime=ContinuousRuntime(53);runtime.run_until(.437)
    enabled,epoch,now,*_=runtime.simulation.core.backend.engine.continuous_time_state()
    assert enabled and epoch==0. and now==pytest.approx(.3)
    assert runtime.world_time==pytest.approx(.437)


@pytest.mark.parametrize("trace,target,initial",((.95,0.,.89),(0.,.95,.13)))
@pytest.mark.parametrize("parts",((.1,.2),(.25,.75),(1.,9.),(1000.,0.)))
def test_native_clamp_crossing_preserves_latent_semigroup(trace,target,initial,parts):
    policy=(.95,.5,.12,.9,1.,1.,1.)
    def make():
        e=NativeBrainEngine();e.add_cognit(0.,.25,.5);e.set_cognit_fields([0,0,0],[7,6,8],[trace,initial,target]);e.begin_continuous_time(10.,*policy);return e
    once,split=make(),make();end=10.+sum(parts);once.materialize_cognits_at([0],end);split.materialize_cognits_at([0],10.+parts[0]);split.materialize_cognits_at([0],end)
    assert once.cognit_state_full([0])[6]==pytest.approx(split.cognit_state_full([0])[6],rel=1e-13,abs=1e-13)
    assert once.continuous_time_state()[5][0]==pytest.approx(split.continuous_time_state()[5][0],rel=1e-13,abs=1e-13)


@pytest.mark.parametrize("trace,target,initial",((.95,0.,.89),(0.,.95,.13)))
def test_clamp_crossing_is_invariant_to_frequent_reads(trace,target,initial):
    policy=(.95,.5,.12,.9,1.,1.,1.)
    def make():
        e=NativeBrainEngine();e.add_cognit(0.,.25,.5);e.set_cognit_fields([0,0,0],[7,6,8],[trace,initial,target]);e.begin_continuous_time(0.,*policy);return e
    once,many=make(),make();once.materialize_cognits_at([0],10.)
    for step in range(1,1001):many.materialize_cognits_at([0],step/100)
    assert many.cognit_state_full([0])[6]==pytest.approx(once.cognit_state_full([0])[6],rel=1e-12,abs=1e-12)
    assert many.continuous_time_state()[5][0]==pytest.approx(once.continuous_time_state()[5][0],rel=1e-12,abs=1e-12)


def test_native_continuous_save_is_observational_and_save_load_matches(tmp_path):
    policy=(.95,.5,.12,.9,1.,1.,1.)
    def make():
        e=NativeBrainEngine();e.add_cognit(0.,.25,.5);e.set_cognit_fields([0,0,0],[7,6,8],[.95,.89,0.]);e.begin_continuous_time(10.,*policy);return e
    no_save,saved=make(),make();saved_state=saved.continuous_time_state();path=tmp_path/"continuous.sebrain";saved.save_graph(str(path));assert saved.continuous_time_state()==saved_state
    loaded=NativeBrainEngine();loaded.load_graph(str(path));loaded.restore_continuous_time_state(*saved_state)
    for engine in (no_save,saved,loaded):engine.begin_continuous_time(20.,*policy);engine.materialize_cognits_at([0],20.)
    for engine in (saved,loaded):
        assert engine.cognit_state_full([0])==pytest.approx(no_save.cognit_state_full([0]),rel=1e-13,abs=1e-13)
        assert engine.continuous_time_state()[5]==pytest.approx(no_save.continuous_time_state()[5],rel=1e-13,abs=1e-13)


def test_goal_understanding_is_event_causal_not_retroactive():
    settings=Settings();core=SyntheticEntityCore(settings);goal=Goal(1,(1,),1.,.5,.5,created_time_seconds=0.,last_touch_time_seconds=0.);core.state.goal=goal;core.world_time_seconds=10.;core.state.novelty=0.;core.state.prediction_error=0.;core._update_goal(set())
    assert goal.persistence==pytest.approx(.85*settings.goal_decay**10*(1-settings.goal_understanding_decay),rel=1e-13)


@pytest.mark.parametrize("before,after",((.1,.9),(.9,.1)))
def test_goal_understanding_before_and_after_sleep_are_separate_events(before,after):
    settings=Settings();core=SyntheticEntityCore(settings);goal=Goal(1,(1,),1.,.5,.5,created_time_seconds=0.,last_touch_time_seconds=0.);core.state.goal=goal
    core.world_time_seconds=0.;core.state.novelty=1-before;core.state.prediction_error=0.;core._update_goal(set())
    at_sleep_start=goal.persistence
    core.world_time_seconds=10.;core.state.novelty=1-after;core._update_goal(set())
    expected=at_sleep_start*settings.goal_decay**10*(1-settings.goal_understanding_decay*after)
    assert goal.persistence==pytest.approx(expected,rel=1e-13)


def test_goal_integer_cadence_matches_frozen_factorization():
    settings=Settings();core=SyntheticEntityCore(settings);goal=Goal(1,(1,),1.,.5,.5,created_time_seconds=0.,last_touch_time_seconds=0.);core.state.goal=goal;core.state.novelty=.4;core.state.prediction_error=.25
    understanding=(1-.4)*(1-.25);frozen=settings.goal_decay*(1-settings.goal_understanding_decay*understanding)
    for second in range(1,11):core.world_time_seconds=float(second);core._update_goal(set())
    assert goal.persistence==pytest.approx(.85*frozen**10,rel=1e-13)
