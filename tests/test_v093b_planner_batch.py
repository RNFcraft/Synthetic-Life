"""Differential oracle captured from integration 774ada8 before Phase 2."""
from heapq import nsmallest
from pathlib import Path
from types import MethodType
import io
import pytest

from consciousness.planning_types import Plan
from consciousness._native_brain import NativeBrainEngine
from experiments.v093a.credit_trace import boundary_state
from experiments.v093a.determinism import BoundaryTrace
from simulation.continuous import ContinuousRuntime

scope = dict(nsmallest=nsmallest, Plan=Plan)
exec((Path(__file__).parent/'fixtures/planner_search_774ada8.py.txt').read_text(encoding='utf-8'), scope)
original_search = scope['_search']


@pytest.mark.parametrize('states', [[], [[]], [[0]], [[0,1],[1,2]], [list(range(80))]*8])
@pytest.mark.parametrize('mode', ['FORCE_CPU_SERIAL','FORCE_CPU_PARALLEL'])
def test_native_single_numeric_launch_matches_mixed_path(states, mode):
    old=NativeBrainEngine();new=NativeBrainEngine()
    for engine in (old,new):
        engine.add_cognits(100, .73, .25, .63)
        for source in range(80):
            for target in range(20):
                engine.add_relation(source,target,0,0,.31,.67,.53)
                for action in (1,2,3):engine.add_relation(source,target,2,action,.19,.61,.47)
    old.set_compute_mode('FORCE_CPU_SERIAL');new.set_compute_mode(mode)
    actions=[1,2,3]
    expected=[(old.predict_actions_batch_at(state,actions,7,.997),old.action_effects_batch(state,actions,.05)) for state in states]
    assert new.planner_transition_batch(states,actions,7,.997,.05)==expected
    assert new.planner_numeric_launches==1


@pytest.mark.parametrize('scenario', [None,'scenarios/v092/train_adjacent_north.sescenario'])
@pytest.mark.parametrize('beam,horizon', [(1,1),(4,3),(8,4)])
def test_production_candidates_scores_order_and_events_match_original(scenario, beam, horizon):
    from dataclasses import replace
    from config import Settings
    from simulation.scenario import load_scenario,ScenarioDefinition
    if scenario:
        data=load_scenario(scenario).sections
        data['CONFIG']['settings']['cognitive'].update(planning_beam_width=beam,planning_horizon=horizon)
        definition=ScenarioDefinition.from_sections(data)
        a=ContinuousRuntime.from_scenario(definition);b=ContinuousRuntime.from_scenario(definition)
    else:
        settings=replace(Settings(),planning_beam_width=beam,planning_horizon=horizon)
        a=ContinuousRuntime(6607,settings);b=ContinuousRuntime(6607,settings)
    a.simulation.core.planner._search=MethodType(original_search,a.simulation.core.planner)
    left=io.StringIO();right=io.StringIO()
    class Candidates(BoundaryTrace):
        def __init__(self,stream):super().__init__(stream);self.candidates=[]
        def plan_candidate(self,core,*args):self.candidates.append(args)
    x=Candidates(left);y=Candidates(right)
    a.diagnostic_observer=x;b.diagnostic_observer=y
    a.run_until(2.);b.run_until(2.)
    assert x.candidates==y.candidates
    assert left.getvalue()==right.getvalue()
    assert boundary_state(a)==boundary_state(b)


def test_native_batch_releases_gil_inspection_guard():
    source=(Path(__file__).parents[1]/'cpp/src/bindings.cpp').read_text(encoding='utf-8')
    block=source.split('.def("planner_transition_batch",',1)[1].split('.def_property_readonly',1)[0]
    assert block.index('py::gil_scoped_release release;')<block.index('e.planner_transition_batch(')<block.index('py::list out;')


def test_effect_only_request_preserves_lazy_materialization_boundary():
    a=NativeBrainEngine();b=NativeBrainEngine()
    for engine in (a,b):
        engine.add_cognits(3,.7,.25,.6)
        engine.add_relation(0,1,1,0,.4,.7,.5)
        engine.add_relation(0,2,2,1,.4,.7,.5)
        engine.begin_continuous_time(1.,.9,.01,.1,.9,.98,.99,.97)
    expected=a.action_effects_batch([0],[1],.05)
    predictions,effects=b.planner_transition_batch([[0]],[1],10,.97,.05,[0])[0]
    assert predictions==[[]] and effects==expected
    assert a.outgoing([0])==b.outgoing([0])
    assert a.continuous_relation_time_state()==b.continuous_relation_time_state()
    with pytest.raises(ValueError,match='prediction mask'):
        b.planner_transition_batch([[0]],[1],10,.97,.05,[2])


def test_forensic_profiler_is_causally_inert_and_restores_trace():
    import sys
    from telemetry.planner_profile import PlannerForensicProfiler
    a=ContinuousRuntime(6607);b=ContinuousRuntime(6607)
    with PlannerForensicProfiler(b.simulation.core.planner) as profiler:b.run_until(1.)
    a.run_until(1.)
    assert boundary_state(a)==boundary_state(b)
    assert sys.gettrace() is None
    assert profiler.report()['state_action_pairs']>0


@pytest.mark.parametrize('beam,horizon',[(1,1),(4,3),(8,4)])
def test_acquired_delayed_model_components_and_levels_match_reference(beam,horizon):
    from config import Settings
    from simulation import Simulation
    from consciousness.cognit import Cognit
    from consciousness.patterns import CognitPattern
    from world.actions import ActionType
    settings=Settings(world_width=8,world_height=8,object_count=0,max_objects=0,
        interoception_enabled=True,homeostatic_valuation_enabled=True,
        delayed_homeostatic_prediction_enabled=True,planning_beam_width=beam,planning_horizon=horizon)
    class Observer:
        def __init__(self):self.rows=[]
        def plan_candidate(self,core,*args):self.rows.append(args)
    cores=[]
    for index in range(2):
        core=Simulation(92,settings,'native').core
        keys=[(0,-2,'appearance',1,1),(0,-1,'appearance',1,1),(1,0,'appearance',2,1),
              (0,0,'internal_0',6,1),(0,0,'internal_0',1,1)]
        ids=[core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,pattern=CognitPattern((key,)))).id for key in keys]
        core.patterns.layer.previous_internal=(1,4,6)
        for trial in range(24):
            tick=trial*8
            for source,action,target,offset,delay in (
                (0,ActionType.MOVE_UP,1,0,.15),(0,ActionType.IDLE,4,1,.15),
                (1,ActionType.INTERACT_UP,2,2,.15),(1,ActionType.IDLE,4,3,.15),
                (2,None,3,4,1.),(4,None,None,5,1.)):
                core._acquire_timed_transition({ids[source]},action,{ids[target]} if target is not None else set(),tick+offset,delay)
        core.diagnostic_observer=Observer()
        cores.append((core,ids[0]))
    a,start=cores[0];b,_=cores[1]
    a.planner._search=MethodType(original_search,a.planner)
    before=a.planner._search(a,{start},200)
    after=b.planner._search(b,{start},200)
    assert before==after
    assert a.diagnostic_observer.rows==b.diagnostic_observer.rows
    assert a.planner.homeostatic_diagnostics()==b.planner.homeostatic_diagnostics()
