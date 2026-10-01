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
    assert core.planner.homeostatic_estimate(core,{ids[2]},a,elapsed=2.2).progress==0


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
