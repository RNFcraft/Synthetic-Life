import pytest
from consciousness.elapsed_time import CognitElapsedState,GoalElapsedState,LazyCognitStore,MemoryElapsedState,RelationElapsedState

POLICY=(.95,.025,.12,.9,.72,.999)
def cognit():return CognitElapsedState(.8,.7,.4,.3,.08,10.)

@pytest.mark.parametrize("parts",((.1,.2),(.25,.75),(1.,0.),(10.,0.),(1000.,0.)))
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
