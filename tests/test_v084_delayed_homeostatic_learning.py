"""Delayed graph acquisition, calibrated projections and physical acceptance."""
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from config import Settings
from consciousness.cognit import Cognit
from consciousness.patterns import CognitPattern
from consciousness.temporal_prediction import successors, calibrated_estimate
from simulation import Simulation
from simulation.continuous import ContinuousRuntime
from world import Action, ActionType, ActionResult
from consciousness.native_engine import RuntimeEventType


def configured(**changes):
    return replace(Settings(world_width=8, world_height=8, object_count=0, max_objects=0,
        interoception_enabled=True, homeostatic_valuation_enabled=True,
        delayed_homeostatic_prediction_enabled=True, planning_horizon=1), **changes)


def learned(backend="python", inconsistent=False, delay=2., repetitions=24):
    sim=Simulation(84,configured(),backend);core=sim.core
    keys=[(1,0,"appearance",1,1),(2,0,"appearance",2,1),
          (0,0,"internal_0",6,1),(0,0,"internal_0",1,1),(0,0,"internal_0",0,1)]
    ids=[core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,pattern=CognitPattern((key,)))).id for key in keys]
    core.available_actions=(ActionType.IDLE,ActionType.INTERACT_UP)
    core.patterns.layer.previous_internal=(1,4,6)
    for trial in range(repetitions):
        tick=trial*4
        core._acquire_timed_transition({ids[0]},ActionType.INTERACT_UP,{ids[1]},tick,.2)
        core._acquire_timed_transition({ids[0]},ActionType.IDLE,{ids[3]},tick+1,.2)
        core._acquire_timed_transition({ids[1]},None,{ids[4] if inconsistent and trial%2 else ids[2]},tick+2,delay)
        core._acquire_timed_transition({ids[3]},None,set(),tick+3,delay)
    return sim,ids


@pytest.mark.parametrize("backend",["python","native"])
def test_delayed_chain_and_planner_ablation(backend):
    sim,ids=learned(backend);core=sim.core
    direct=core.planner.homeostatic_effects(core,{ids[0]},ActionType.INTERACT_UP)
    assert ids[2] not in direct
    estimate=core.planner.homeostatic_estimate(core,{ids[0]},ActionType.INTERACT_UP)
    assert estimate.progress>0
    assert core.planner._search(core,{ids[0]},100).actions[0] is ActionType.INTERACT_UP
    for depth in (0,):
        core.planner.settings=core.settings=replace(core.settings,planning_passive_prediction_depth=depth)
        assert core.planner.homeostatic_estimate(core,{ids[0]},ActionType.INTERACT_UP).progress==0
    core.planner.settings=core.settings=replace(core.settings,delayed_homeostatic_prediction_enabled=False)
    assert core.planner.homeostatic_estimate(core,{ids[0]},ActionType.INTERACT_UP).progress==0
    if core.backend:assert core.backend.full_graph_sync_calls==0


@pytest.mark.parametrize("backend",["python","native"])
def test_calibration_contradiction_and_weak_support(backend):
    consistent,ids=learned(backend)
    mixed,mids=learned(backend,True)
    weak,wids=learned(backend,repetitions=2)
    a=ActionType.INTERACT_UP
    strong=consistent.core.planner.homeostatic_estimate(consistent.core,{ids[0]},a)
    ambiguous=mixed.core.planner.homeostatic_estimate(mixed.core,{mids[0]},a)
    assert 0<ambiguous.confidence<strong.confidence
    assert ambiguous.progress<strong.progress
    assert mixed.core.planner.temporal_diagnostics["ambiguity"]>0
    assert weak.core.planner.homeostatic_estimate(weak.core,{wids[0]},a).progress==0
    for tick in range(100,140):consistent.core._acquire_timed_transition({ids[1]},None,{ids[3]},tick,2.)
    after=consistent.core.planner.homeostatic_estimate(consistent.core,{ids[0]},a)
    assert after.progress<strong.progress


@pytest.mark.parametrize("backend",["python","native"])
def test_time_ranking_horizon_and_chain_confidence(backend):
    fast,ids=learned(backend,delay=1.)
    slow,sids=learned(backend,delay=12.)
    a=ActionType.INTERACT_UP
    assert fast.core.planner.homeostatic_estimate(fast.core,{ids[0]},a).progress>slow.core.planner.homeostatic_estimate(slow.core,{sids[0]},a).progress
    root=successors(fast.core,{ids[0]:(1.,0.)},a)
    leaf=successors(fast.core,root)
    assert 0<leaf[ids[2]][0]<root[ids[1]][0]<1
    assert leaf[ids[2]][1]==pytest.approx(1.2)
    fast.core.planner.settings=fast.core.settings=replace(fast.settings,planning_prediction_time_horizon=.5)
    assert fast.core.planner.homeostatic_estimate(fast.core,{ids[0]},a).progress==0


def test_duplicate_bins_unknown_mass_and_diagnostics():
    sim,ids=learned();core=sim.core
    duplicate=core.graph.add_cognit(Cognit(core.graph.next_id,pattern=core.graph.nodes[ids[2]].pattern)).id
    single,_=calibrated_estimate(core,{ids[2]:(.4,2.)},(1,4,6))
    repeated,_=calibrated_estimate(core,{ids[2]:(.4,2.),duplicate:(.4,2.)},(1,4,6))
    assert single==repeated and single.levels[0]==pytest.approx(3.)
    missing,_=calibrated_estimate(core,{},(1,4,6))
    assert missing.progress==0 and missing.levels==(1,4,6)
    core.planner.homeostatic_estimate(core,{ids[0]},ActionType.INTERACT_UP)
    original=core.planner.homeostatic_diagnostics()
    changed=core.planner.homeostatic_diagnostics();changed["temporal"]["elapsed"]=-100
    assert core.planner.homeostatic_diagnostics()==original


@pytest.mark.parametrize("backend",["python","native"])
def test_failed_action_is_not_credited(backend):
    sim,ids=learned(backend,repetitions=0);core=sim.core
    for trial in range(20):
        core.timed_previous_ids={ids[0]};core.timed_observation_time=float(trial)
        core.record_action_outcome(ActionType.INTERACT_UP,False)
        core._learn_timed_observation({ids[2]},trial+.2,trial)
    assert core.planner.homeostatic_estimate(core,{ids[0]},ActionType.INTERACT_UP).progress==0


@pytest.mark.parametrize("backend",["python","native"])
def test_world_and_brain_timing_transfer(tmp_path,backend):
    sim,ids=learned(backend);core=sim.core;a=ActionType.INTERACT_UP
    core.timed_previous_ids={ids[0]};core.timed_observation_time=12.
    core.record_action_outcome(a,True)
    expected=core.planner.homeostatic_estimate(core,{ids[0]},a)
    path=tmp_path/'timed.seworld';sim.save_world(path)
    restored=Simulation.load_world(path,backend=backend)
    assert restored.core.planner.homeostatic_estimate(restored.core,{ids[0]},a)==expected
    assert restored.core.timed_previous_ids=={ids[0]} and restored.core.timed_observation_time==12.
    if core.backend:
        assert restored.core.backend.engine.transition_history()==core.backend.engine.transition_history()
        assert restored.core.backend.engine.temporal_state()==core.backend.engine.temporal_state()
    path=tmp_path/'timed.sebrain';sim.save_brain(path)
    transferred=Simulation(87,sim.settings,backend);transferred.load_brain(path)
    assert transferred.core.timed_observation_time is None and not transferred.core.timed_previous_ids
    assert transferred.core.patterns.layer.previous_internal is None
    transferred.core.patterns.layer.previous_internal=(1,4,6)
    assert transferred.core.planner.homeostatic_estimate(transferred.core,{ids[0]},a)==expected


@pytest.mark.parametrize("phase",[0.,.01,.8])
def test_exact_continuous_frontier_and_causal_settings(tmp_path,phase):
    settings=configured(planning_horizon=2,planning_time_discount=.23,
        planning_passive_prediction_depth=2,planning_prediction_time_horizon=17.,
        planning_temporal_probability_floor=.03,continuous_maintenance_interval_seconds=.17)
    runtime=ContinuousRuntime(84,settings);runtime.run_until(phase)
    path=tmp_path/'frontier.seworld';runtime.save_world(path)
    restored=ContinuousRuntime.load_world(path)
    assert restored.simulation.snapshot_data()==runtime.simulation.snapshot_data()
    assert restored.scheduler_state()==runtime.scheduler_state()
    for item in (runtime,restored):item.run_until(phase+.6)
    assert restored.simulation.snapshot_data()==runtime.simulation.snapshot_data()
    assert restored.scheduler_state()==runtime.scheduler_state()
    for key,value in [("delayed_homeostatic_prediction_enabled",False),("planning_time_discount",.2),
                      ("planning_passive_prediction_depth",1),("planning_prediction_time_horizon",16.),
                      ("planning_temporal_probability_floor",.02)]:
        with pytest.raises(ValueError,match="incompatible"):
            ContinuousRuntime.load_world(path,replace(settings,**{key:value}))


def test_native_python_parity_and_hashseed():
    python,ids=learned();native,nids=learned("native")
    a=ActionType.INTERACT_UP
    assert python.core.planner.homeostatic_estimate(python.core,{ids[0]},a)==native.core.planner.homeostatic_estimate(native.core,{nids[0]},a)
    script="import runpy,json; m=runpy.run_path('tests/test_v084_delayed_homeostatic_learning.py'); s,i=m['learned']('native'); p=s.core.planner._search(s.core,{i[0]},100); print(json.dumps([p.actions[0].name,p.score,s.core.planner.homeostatic_diagnostics()],sort_keys=True))"
    output=[subprocess.check_output([sys.executable,'-B','-c',script],cwd=Path(__file__).parents[1],env={**os.environ,'PYTHONHASHSEED':seed},text=True) for seed in ('1','777')]
    assert output[0]==output[1]


def physical(payload):
    settings=configured(physiology_initial_energy=15.,physiology_initial_nutrients=0.,
        physiology_nutrient_target=.01,physiology_digestion_rate=30.,physiology_digestion_efficiency=1.,
        physiology_basal_body_rate=0.,physiology_basal_brain_rate=0.,physiology_hydration_rate=0.,
        physiology_interaction_cost=0.,cognit_birth_threshold=0.,proto_min_occurrences=1,
        max_new_cognits_per_tick=64,homeostasis_input_gain=0.,sensory_activation=1.)
    sim=Simulation(84,settings,"native");core=sim.core
    core.available_actions=(ActionType.IDLE,ActionType.INTERACT_UP)
    sim.world.native.set_body_state(0,3,4,'N');sim.world._refresh()
    for trial in range(32):
        time=trial*3.;sim.physiology.advance_to(time);sim.world.advance_world_time(time)
        sim.physiology.energy=15.;sim.physiology.nutrients=0.;sim.physiology.hydration=80.
        core.timed_previous_ids=set();core.timed_observation_time=None;core.pending_learning_action=None
        if not sim.world.resource_count():sim.world.spawn_resource((3,3),2,payload,1.,time,sim.world.native.time_state()[1]+1)
        before=sim.interoception.sample(sim.physiology.snapshot())
        core.step(sim.world.perceive(trial*3),world_time=time,internal=before)
        prior=set(core.timed_previous_ids)
        action=ActionType.INTERACT_UP if trial%2 else ActionType.IDLE
        result=sim.world.apply_action(Action(action));assert result is ActionResult.SUCCESS
        sim.physiology.apply_action(action,True);sim.apply_world_consequence()
        core.record_action_outcome(action,True)
        # Observe the precursor immediately: ingestion changes nutrients, not energy.
        immediate=sim.interoception.sample(sim.physiology.snapshot());assert immediate.levels[0]==before.levels[0]
        core.step(sim.world.perceive(trial*3+1),world_time=time,internal=immediate)
        sim.physiology.advance_to(time+2.);sim.world.advance_world_time(time+2.)
        delayed=sim.interoception.sample(sim.physiology.snapshot())
        core.step(sim.world.perceive(trial*3+2),world_time=time+2.,internal=delayed)
    core.patterns.layer.previous_internal=before.levels
    return sim,prior,before,immediate,delayed


def test_real_digestion_to_acquired_prediction_to_planner_counterfactual():
    real,prior,before,immediate,delayed=physical(60.)
    control,cprior,cbefore,cimmediate,cdelayed=physical(0.)
    assert delayed.levels[0]>immediate.levels[0]==before.levels[0]
    assert cdelayed.levels[0]==cimmediate.levels[0]==cbefore.levels[0]
    a=ActionType.INTERACT_UP;core=real.core
    learned=core.planner.homeostatic_estimate(core,prior,a)
    counter=control.core.planner.homeostatic_estimate(control.core,cprior,a)
    assert learned.progress>0 and counter.progress<=0
    assert core.planner._search(core,prior,100).actions[0] is a
    core.planner.settings=core.settings=replace(core.settings,planning_passive_prediction_depth=0)
    assert core.planner.homeostatic_estimate(core,prior,a).progress<=0
    assert core.planner._search(core,prior,100).actions[0] is ActionType.IDLE
    assert core.backend.full_graph_sync_calls==0


@pytest.mark.parametrize("key,value",[("delayed_homeostatic_prediction_enabled",1),
    ("planning_passive_prediction_depth",9),("planning_passive_prediction_depth",True),
    ("planning_prediction_time_horizon",0.),("planning_prediction_time_horizon",float('inf')),
    ("planning_time_discount",-1.),("planning_time_discount",True),
    ("planning_temporal_probability_floor",0.),("planning_temporal_probability_floor",float('nan'))])
def test_temporal_settings_validate(key,value):
    with pytest.raises(ValueError):configured(**{key:value})


def test_disabled_temporal_settings_preserve_baseline_causal_behavior():
    first=ContinuousRuntime(84,configured(delayed_homeostatic_prediction_enabled=False))
    second=ContinuousRuntime(84,configured(delayed_homeostatic_prediction_enabled=False,
        planning_passive_prediction_depth=0,planning_time_discount=10.,planning_prediction_time_horizon=.1))
    for runtime in (first,second):runtime.run_until(.8)
    left,right=first.simulation.snapshot_data(),second.simulation.snapshot_data()
    left.pop('causal_config');right.pop('causal_config')
    assert left==right and first.scheduler_state()==second.scheduler_state()
    assert not first.simulation.core.backend.engine.temporal_state()
    assert Settings().delayed_homeostatic_prediction_enabled is False
    assert Settings().homeostatic_valuation_enabled is False and Settings().interoception_enabled is False


@pytest.mark.parametrize("backend",["python","native"])
def test_direct_and_indirect_same_bin_are_not_added(backend):
    sim,ids=learned(backend);core=sim.core;a=ActionType.INTERACT_UP
    for tick in range(100,180):
        core._acquire_timed_transition({ids[0]},a,{ids[1],ids[2]},tick*2,.2)
        core._acquire_timed_transition({ids[0]},ActionType.IDLE,set(),tick*2+1,.2)
    combined=core.planner.homeostatic_estimate(core,{ids[0]},a)
    core.planner.settings=core.settings=replace(core.settings,planning_passive_prediction_depth=0)
    direct=core.planner.homeostatic_estimate(core,{ids[0]},a)
    assert combined.progress==direct.progress


def test_passive_projection_then_next_action_uses_cumulative_time():
    sim,ids=learned();core=sim.core;a=ActionType.INTERACT_UP
    terminal=core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,
        pattern=CognitPattern(((0,0,'internal_2',6,1),)))).id
    core.patterns.layer.previous_internal=(1,4,1)
    for trial in range(24):
        core._acquire_timed_transition({ids[2]},a,{terminal},100+trial*2,3.)
        core._acquire_timed_transition({ids[2]},ActionType.IDLE,set(),101+trial*2,3.)
    core.planner.settings=core.settings=replace(core.settings,planning_horizon=2)
    plan=core.planner._search(core,{ids[0]},160)
    assert plan.actions==(a,a)
    assert ids[2] in plan.predicted_states[0] and terminal in plan.predicted_states[1]
    core.planner.settings=core.settings=replace(core.settings,planning_prediction_time_horizon=4.)
    # Filtered timing falls back to acquired immediate knowledge, without
    # inventing a learned delay or deleting that knowledge.
    fallback=core.planner.homeostatic_estimate(core,{ids[2]},a,elapsed=2.2)
    assert fallback.progress>0 and core.planner.temporal_diagnostics['usable'] is False
    assert core.planner.temporal_diagnostics['elapsed']==2.2


@pytest.mark.parametrize("backend",["python","native"])
def test_planner_prefers_equal_improvement_at_shorter_delay(backend):
    sim,ids=learned(backend,repetitions=0);core=sim.core
    slow=core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,pattern=CognitPattern(((3,0,'appearance',3,1),)))).id
    fast_action,slow_action=ActionType.INTERACT_UP,ActionType.INTERACT_DOWN
    core.available_actions=(fast_action,slow_action)
    for trial in range(24):
        tick=trial*4
        core._acquire_timed_transition({ids[0]},fast_action,{ids[1]},tick,.2)
        core._acquire_timed_transition({ids[0]},slow_action,{slow},tick+1,.2)
        core._acquire_timed_transition({ids[1]},None,{ids[2]},tick+2,1.)
        core._acquire_timed_transition({slow},None,{ids[2]},tick+3,12.)
    assert core.planner._search(core,{ids[0]},100).actions[0] is fast_action


def test_legacy_causal_runtime_migrates_only_complete_old_group():
    from simulation.persisted_settings import causal_configuration,restore_settings,V084_CAUSAL_FIELDS
    legacy={'causal_config':causal_configuration(configured())}
    for name in V084_CAUSAL_FIELDS:del legacy['causal_config']['runtime'][name]
    assert restore_settings(legacy).delayed_homeostatic_prediction_enabled is False
    legacy['causal_config']['runtime']['planning_time_discount']=.5
    with pytest.raises(ValueError,match='invalid saved'):restore_settings(legacy)


@pytest.mark.parametrize('backend',['python','native'])
@pytest.mark.parametrize('filter_kind',['absent','floor','horizon'])
def test_unusable_timing_preserves_ordinary_planner_state(backend,filter_kind):
    sim,ids=learned(backend);core=sim.core;a=ActionType.INTERACT_UP
    if filter_kind=='absent':
        if core.backend:core.backend.engine.restore_temporal_state([])
        else:core.transitions.timings.clear()
    elif filter_kind=='floor':
        core.planner.settings=core.settings=replace(core.settings,planning_temporal_probability_floor=1.)
    else:
        core.planner.settings=core.settings=replace(core.settings,planning_prediction_time_horizon=.01)
    on=core.planner._search(core,{ids[0]},100)
    assert core.planner.temporal_diagnostics['usable'] is False
    core.planner.settings=core.settings=replace(core.settings,delayed_homeostatic_prediction_enabled=False)
    off=core.planner._search(core,{ids[0]},100)
    assert on==off and on.predicted_states and ids[1] in on.predicted_states[0]


@pytest.mark.parametrize('backend',['python','native'])
def test_legacy_brain_without_timing_preserves_immediate_valuation(tmp_path,backend):
    baseline=__import__('runpy').run_path('tests/test_v083_homeostatic_valuation.py')
    source,ids=baseline['learned'](backend)
    brain=tmp_path/'legacy.sebrain';source.save_brain(brain)
    target=Simulation(85,configured(),backend);target.load_brain(brain)
    core=target.core;core.patterns.layer.previous_internal=(6,4,1)
    action=source.core.available_actions[1]
    on=core.planner.homeostatic_estimate(core,{ids[0]},action)
    assert on.progress>0 and core.planner.temporal_diagnostics['usable'] is False
    assert core.planner.temporal_diagnostics['elapsed']==0
    core.planner.settings=core.settings=replace(core.settings,delayed_homeostatic_prediction_enabled=False)
    assert core.planner.homeostatic_estimate(core,{ids[0]},action)==on


@pytest.mark.parametrize('backend',['python','native'])
def test_passive_projection_preserves_context_for_second_action(backend):
    sim,ids=learned(backend);core=sim.core;a=ActionType.INTERACT_UP
    terminal=core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.,
        pattern=CognitPattern(((0,0,'internal_2',6,1),)))).id
    core.patterns.layer.previous_internal=(1,4,1)
    # Second action is learned from external B, never from internal C.
    for trial in range(24):
        core._acquire_timed_transition({ids[1]},a,{terminal},100+trial*2,1.)
        core._acquire_timed_transition({ids[1]},ActionType.IDLE,set(),101+trial*2,1.)
    core.planner.homeostatic_estimate(core,{ids[0]},a)
    projected=set(core.planner.temporal_diagnostics['projected_state'])
    assert {ids[1],ids[2]}<=projected
    core.planner.settings=core.settings=replace(core.settings,planning_horizon=2)
    # Control the first intervention; the second action is selected by search.
    plan=core.planner._search(core,{ids[0]},160,
        initial_predictions={a:core._graph_predict({ids[0]},a)})
    assert plan.actions==(a,a) and terminal in plan.predicted_states[1]


@pytest.mark.parametrize('backend',['python','native'])
def test_failed_trials_contradict_existing_effect_and_success_recovers(backend):
    sim,ids=learned(backend);core=sim.core;a=ActionType.INTERACT_UP
    before=core.planner.homeostatic_estimate(core,{ids[0]},a)
    count=core.graph.relation_count
    for trial in range(20):
        core.timed_previous_ids={ids[0]};core.timed_observation_time=100.+trial
        core.record_action_outcome(a,False)
        # Even an unrelated beneficial observed target cannot confirm a fail.
        core._learn_timed_observation({ids[2]},100.2+trial,100+trial)
    failed=core.planner.homeostatic_estimate(core,{ids[0]},a)
    assert failed.confidence<before.confidence and failed.progress<before.progress
    assert core.graph.relation_count==count
    assert ids[2] not in core.planner.homeostatic_effects(core,{ids[0]},a)
    for tick in range(150,190):core._acquire_timed_transition({ids[0]},a,{ids[1]},tick,.2)
    recovered=core.planner.homeostatic_estimate(core,{ids[0]},a)
    assert recovered.progress>failed.progress
    if core.backend:assert core.backend.full_graph_sync_calls==0


@pytest.mark.parametrize('backend',['python','native'])
def test_passive_sentinel_is_distinct_from_real_idle(backend):
    assert min(a.value for a in ActionType)>0
    sim,ids=learned(backend,repetitions=0);core=sim.core
    core._acquire_timed_transition({ids[0]},ActionType.IDLE,{ids[1]},0,.2)
    if core.backend:
        rows=core.backend.engine.temporal_state()
        assert rows and all(row[2]==ActionType.IDLE.value for row in rows)
    else:assert set(key[2] for key in core.transitions.timings)=={ActionType.IDLE.value}
    assert not successors(core,{ids[0]:(1.,0.)})
    core._acquire_timed_transition({ids[0]},None,{ids[1]},1,.3)
    if core.backend:assert {row[2] for row in core.backend.engine.temporal_state()}=={0,ActionType.IDLE.value}
    else:assert {key[2] for key in core.transitions.timings}=={0,ActionType.IDLE.value}


@pytest.mark.parametrize('source_backend,target_backend',[('python','native'),('native','python')])
def test_cross_backend_brain_transfer_fails_before_mutation(tmp_path,source_backend,target_backend):
    source,_=learned(source_backend);path=tmp_path/'backend.sebrain';source.save_brain(path)
    target=Simulation(85,configured(),target_backend);before=target.snapshot_data()
    with pytest.raises(ValueError,match='numeric_backend'):target.load_brain(path)
    assert target.snapshot_data()==before


def production_physical(monkeypatch,payload=60.,trials=32):
    settings=configured(continuous_maintenance_interval_seconds=.05,sensory_neural_enabled=False,
        physiology_initial_energy=15.,physiology_initial_nutrients=0.,physiology_nutrient_target=.01,
        physiology_digestion_rate=1500.,physiology_digestion_efficiency=1.,physiology_basal_body_rate=0.,
        physiology_basal_brain_rate=0.,physiology_hydration_rate=0.,physiology_interaction_cost=0.,
        cognit_birth_threshold=0.,proto_min_occurrences=1,max_new_cognits_per_tick=64,
        homeostasis_input_gain=0.,sensory_activation=1.)
    runtime=ContinuousRuntime(84,settings);sim=runtime.simulation;core=sim.core
    sim.world.native.set_body_state(0,3,4,'N');sim.world._refresh()
    # Experimental action intervention: permit one real scheduled action per
    # trial, then hold physical actions while the production scheduler observes.
    budget={'remaining':0};schedule=runtime._schedule_action
    def controlled(action,now):
        if budget['remaining']:
            budget['remaining']-=1;schedule(action,now)
    monkeypatch.setattr(runtime,'_schedule_action',controlled)
    for trial in range(trials):
        time=trial*.6
        if trial:runtime.run_until(time)
        sim.physiology.energy=15.;sim.physiology.nutrients=0.;sim.physiology.hydration=80.
        core.timed_previous_ids=set();core.timed_observation_time=None
        core.pending_learning_action=None;core.learning_action_attempt=None
        if not sim.world.resource_count():
            sim.world.spawn_resource((3,3),2,payload,1.,time,sim.event_sequence.next())
        action=ActionType.INTERACT_UP if trial%2 else ActionType.IDLE
        core.available_actions=(action,);budget['remaining']=1
        if trial:runtime.scheduler.schedule(time,RuntimeEventType.SENSORY_CHANGE)
        runtime.run_until(time)
        prior=set(core.timed_previous_ids)
        runtime.run_until(time+.151)
        immediate=runtime.last_internal
        runtime.run_until(time+.4)
        delayed=runtime.last_internal
    core.available_actions=(ActionType.IDLE,ActionType.INTERACT_UP)
    core.patterns.layer.previous_internal=(1,0,6)
    return runtime,prior,immediate,delayed


def test_production_runtime_physical_delayed_freeze_acceptance(monkeypatch):
    runtime,prior,immediate,delayed=production_physical(monkeypatch)
    control,cprior,cimmediate,cdelayed=production_physical(monkeypatch,0.)
    core=runtime.simulation.core;a=ActionType.INTERACT_UP
    assert immediate.levels[0]==1 and delayed.levels[0]==6
    assert cimmediate.levels[0]==cdelayed.levels[0]==1
    assert runtime.internal_observations>0 and control.internal_observations==0
    assert runtime.actions_completed==control.actions_completed==32
    estimate=core.planner.homeostatic_estimate(core,prior,a)
    assert estimate.progress>control.simulation.core.planner.homeostatic_estimate(control.simulation.core,cprior,a).progress
    assert core.planner.temporal_diagnostics['passive_depth']>0
    assert any(row[2]==0 and row[3]>=core.settings.relation_provisional_support
               for row in core.backend.engine.temporal_state())
    assert core.planner._search(core,prior,core.cognitive_tick).actions[0] is a
    core.planner.settings=core.settings=replace(core.settings,planning_passive_prediction_depth=0)
    assert core.planner.homeostatic_estimate(core,prior,a).progress<estimate.progress
    assert core.planner._search(core,prior,core.cognitive_tick).actions[0] is ActionType.IDLE
    assert runtime.internal_observations==16
    core.planner.settings=core.settings=replace(core.settings,planning_passive_prediction_depth=3,
        delayed_homeostatic_prediction_enabled=False)
    baseline=core.planner._search(core,prior,core.cognitive_tick)
    assert baseline.actions[0] is ActionType.IDLE
    timing=core.backend.engine.temporal_state();core.backend.engine.restore_temporal_state([])
    core.planner.settings=core.settings=replace(core.settings,delayed_homeostatic_prediction_enabled=True)
    untimed=core.planner._search(core,prior,core.cognitive_tick)
    assert untimed==baseline and core.planner.temporal_diagnostics['usable'] is False
    core.backend.engine.restore_temporal_state(timing)
    assert core.backend.full_graph_sync_calls==0


def test_production_runtime_raw_drift_without_bin_change_has_no_extra_observation():
    runtime=ContinuousRuntime(84,configured(sensory_neural_enabled=False,
        physiology_initial_nutrients=0.,continuous_maintenance_interval_seconds=.01))
    runtime.run_until(.1)
    assert runtime.simulation.physiology.energy<80.
    assert runtime.internal_observations==0 and runtime.observation_ordinal==1


def internal_change_settings(**changes):
    return configured(continuous_maintenance_interval_seconds=.05,
        physiology_initial_energy=24.,physiology_initial_nutrients=1.,
        physiology_digestion_rate=20.,physiology_digestion_efficiency=1.,
        physiology_basal_body_rate=0.,physiology_basal_brain_rate=0.,
        physiology_hydration_rate=0.,**changes)


@pytest.mark.parametrize('neural',[False,True])
def test_one_internal_change_preserves_in_flight_action_and_neural_path(neural):
    runtime=ContinuousRuntime(84,internal_change_settings(sensory_neural_enabled=neural))
    runtime.simulation.core.available_actions=(ActionType.IDLE,)
    runtime.run_until(.04)
    core=runtime.simulation.core;generation=runtime.cognition_generation
    frontier=core.continuous_frontier;trace_size=len(core.trace.entries)
    rng=runtime.simulation.rng.getstate();world_frame=runtime.simulation.world.perceive(0)
    transduced=runtime.neural_sensory.telemetry.sensory_frames_transduced if neural else 0
    runtime.run_until(.1)
    assert runtime.internal_observations==1
    assert runtime.actions_completed==0 and runtime.cognition_generation==generation
    assert core.continuous_frontier is frontier and frontier.committed
    assert len(core.trace.entries)==trace_size
    assert len([e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE])==1
    assert runtime.simulation.rng.getstate()==rng
    assert runtime.simulation.world.perceive(0)==world_frame
    assert runtime.last_internal.levels[0]==2
    if neural:assert runtime.neural_sensory.telemetry.sensory_frames_transduced==transduced
    assert core.backend.full_graph_sync_calls==0


def process_one_runtime_boundary(runtime):
    """Expose a production event boundary for a same-time checkpoint."""
    event=runtime.scheduler.snapshot()[0]
    due=runtime.scheduler.pop_ready(event.time)
    assert len(due)==1, 'fixture chooses isolated scheduler boundaries'
    runtime._process(due[0]);runtime.scheduler_events_processed+=1
    runtime.simulation.world.advance_world_time(event.time)
    runtime.simulation.world_time=__import__('world',fromlist=['WorldTime']).WorldTime(event.time)
    return event


@pytest.mark.parametrize('phase',['before','queued','observed','deliberating'])
def test_exact_world_continuation_around_internal_observation(tmp_path,phase):
    original=ContinuousRuntime(84,internal_change_settings(sensory_neural_enabled=False))
    original.simulation.core.available_actions=(ActionType.IDLE,)
    original.run_until(.04)
    if phase!='before':
        event=process_one_runtime_boundary(original)
        assert event.type==RuntimeEventType.MAINTENANCE
        assert any(e.type==RuntimeEventType.SENSORY_CHANGE and e.payload==1 for e in original.scheduler.snapshot())
    if phase in ('observed','deliberating'):
        event=process_one_runtime_boundary(original)
        assert event.type==RuntimeEventType.SENSORY_CHANGE and event.payload==1
        assert original.internal_observations==1
    if phase=='deliberating':
        # Reach the next actual action's ordinary observation and begin its
        # deliberation after the passive observation, without injecting cognition.
        while original.simulation.core.continuous_frontier.phase!='DELIBERATING':
            process_one_runtime_boundary(original)
    path=tmp_path/f'{phase}.seworld';original.save_world(path)
    restored=ContinuousRuntime.load_world(path)
    restored.simulation.core.available_actions=original.simulation.core.available_actions
    assert restored.scheduler_state()==original.scheduler_state()
    assert restored._frontier_state()==original._frontier_state()
    assert restored.simulation.snapshot_data()==original.simulation.snapshot_data()
    assert restored.internal_observations==original.internal_observations
    for runtime in (original,restored):runtime.run_until(.4)
    assert restored.scheduler_state()==original.scheduler_state()
    assert restored._frontier_state()==original._frontier_state()
    assert restored.simulation.snapshot_data()==original.simulation.snapshot_data()
    assert restored.internal_observations==original.internal_observations==1


def test_timing_ownership_and_failed_outcome_parity():
    python,ids=learned();native,nids=learned('native')
    canonical=[[*key,*moments] for key,moments in sorted(python.core.transitions.timings.items())]
    rows=[[int(s)+1,int(t)+1,int(a),n,mean,m2] for s,t,a,n,mean,m2 in native.core.backend.engine.temporal_state()]
    assert canonical==rows
    for sim,node_ids in ((python,ids),(native,nids)):
        core=sim.core
        for tick in range(100,120):
            core.timed_previous_ids={node_ids[0]};core.timed_observation_time=float(tick)
            core.record_action_outcome(ActionType.INTERACT_UP,False)
            core._learn_timed_observation({node_ids[2]},tick+.2,tick)
    assert python.core.planner.homeostatic_estimate(python.core,{ids[0]},ActionType.INTERACT_UP)==native.core.planner.homeostatic_estimate(native.core,{nids[0]},ActionType.INTERACT_UP)


def test_production_runtime_hashseed_determinism():
    script="import runpy,pytest,json; m=runpy.run_path('tests/test_v084_delayed_homeostatic_learning.py'); mp=pytest.MonkeyPatch(); r,p,i,d=m['production_physical'](mp); c=r.simulation.core; plan=c.planner._search(c,p,c.cognitive_tick); print(json.dumps([plan.actions[0].name,plan.score,r.internal_observations,r.scheduler_state()],sort_keys=True)); mp.undo()"
    results=[subprocess.check_output([sys.executable,'-B','-c',script],cwd=Path(__file__).parents[1],
        env={**os.environ,'PYTHONHASHSEED':seed},text=True) for seed in ('1','777')]
    assert results[0]==results[1]


@pytest.mark.parametrize('backend',['python','native'])
def test_brain_ablation_does_not_discard_durable_timing(tmp_path,backend):
    source,ids=learned(backend);path=tmp_path/'before.sebrain';source.save_brain(path)
    disabled=Simulation(85,replace(source.settings,delayed_homeostatic_prediction_enabled=False),backend)
    disabled.load_brain(path);path=tmp_path/'disabled.sebrain';disabled.save_brain(path)
    restored=Simulation(86,source.settings,backend);restored.load_brain(path)
    restored.core.patterns.layer.previous_internal=(1,4,6)
    expected=source.core.planner.homeostatic_estimate(source.core,{ids[0]},ActionType.INTERACT_UP)
    assert restored.core.planner.homeostatic_estimate(restored.core,{ids[0]},ActionType.INTERACT_UP)==expected
    incompatible=Simulation(87,replace(source.settings,interoception_bins=9),backend)
    with pytest.raises(ValueError,match='sensor contract'):incompatible.load_brain(path)


def test_same_time_action_completion_owns_full_observation():
    runtime=ContinuousRuntime(84,configured(sensory_neural_enabled=False,
        continuous_maintenance_interval_seconds=.15,physiology_initial_energy=24.9,
        physiology_initial_nutrients=1.,physiology_digestion_rate=1.,
        physiology_digestion_efficiency=1.,physiology_basal_body_rate=0.,
        physiology_basal_brain_rate=0.,physiology_hydration_rate=0.,physiology_interaction_cost=0.,
        cognit_birth_threshold=0.,proto_min_occurrences=1,max_new_cognits_per_tick=64))
    sim=runtime.simulation;core=sim.core;core.available_actions=(ActionType.INTERACT_UP,)
    sim.world.native.set_body_state(0,3,4,'N');sim.world._refresh()
    sim.world.spawn_resource((3,3),2,60.,1.,0.,sim.event_sequence.next())
    runtime.run_until(0.)
    before=set(core.timed_previous_ids)
    runtime.run_until(.151)
    assert sim.world.resource_count()==0 and runtime.actions_completed==1
    assert runtime.internal_observations==0 and runtime.observation_ordinal==2
    assert runtime.last_internal.levels[0]==2
    assert runtime.last_frame.cells==sim.world.perceive(0).cells
    assert getattr(core,'pending_learning_action',None) is None
    after=set(core.timed_previous_ids)
    assert any(int(s)+1 in before and int(t)+1 in after and a==ActionType.INTERACT_UP.value
               for s,t,a,*_ in core.backend.engine.temporal_state())


@pytest.mark.parametrize('backend',['python','native'])
def test_internal_replacement_drops_stale_mixed_pattern_keeps_external(backend):
    from consciousness.temporal_prediction import merge_projected_state
    sim,ids=learned(backend);core=sim.core
    mixed=core.graph.add_cognit(Cognit(core.graph.next_id,pattern=CognitPattern(
        core.graph.nodes[ids[1]].pattern.participants+core.graph.nodes[ids[3]].pattern.participants))).id
    baseline={ids[1],ids[3],mixed}
    assert merge_projected_state(core.graph,baseline,set(),set())==baseline
    merged=merge_projected_state(core.graph,baseline,{ids[2]},{0})
    assert merged=={ids[1],ids[2]}
