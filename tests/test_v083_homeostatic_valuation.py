"""Controlled acquisition, intervention, ablation and continuation experiments."""
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from config import Settings
from consciousness.cognit import Cognit
from consciousness.patterns import CognitPattern, SensoryEventKind, is_spatial_primitive, is_internal_primitive
from consciousness.relation import RelationType
from consciousness.sensory import SensoryPatternTracker
from physiology.interoception import InteroceptiveFrame
from simulation import Simulation
from simulation.continuous import ContinuousRuntime
from world import Action, ActionType, ActionResult


def configured(**changes):
    return replace(Settings(world_width=8, world_height=8, object_count=0, max_objects=0,
        interoception_enabled=True, homeostatic_valuation_enabled=True, planning_horizon=1), **changes)


def learned(backend="python", reverse=False, repetitions=12, enabled=True):
    sim = Simulation(19, configured(homeostatic_valuation_enabled=enabled), backend)
    core = sim.core
    core.available_actions = tuple(ActionType)[:2]
    # Identical external context and sensor-domain metadata in both histories.
    keys = [(1, 0, "appearance", 1, 1), (0, 0, "internal_2", 1, 1),
            (0, 0, "internal_2", 6, 1)]
    ids = [core.graph.add_cognit(Cognit(core.graph.next_id, activity=1.,
        pattern=CognitPattern((key,)))).id for key in keys]
    core.patterns.layer.previous_internal = (6, 4, 1)
    for tick in range(repetitions * 2):
        action = core.available_actions[tick % 2]
        target = ids[2] if bool(tick % 2) != reverse else ids[1]
        acquire(core, {ids[0]}, action, {target}, tick)
    return sim, ids


def acquire(core, before, action, after, tick):
    # Production learning functions; no manually initialized rho probabilities.
    core.previous_active, core.previous_action = before, action
    core._update_relation_outcomes(tick, after)
    if core.backend:
        source, target = [i-1 for i in sorted(before)], [i-1 for i in sorted(after)]
        core.backend.update_transition_evidence(source, action, target)
        core.backend.materialize(tick, source, action, target)
    else:
        core.transitions.observe(before, action, after)
        core._materialize_relations(tick, after)


@pytest.mark.parametrize("backend", ["python", "native"])
@pytest.mark.parametrize("reverse", [False, True])
def test_learned_history_reverses_component_and_planner_ranking(backend, reverse):
    sim, ids = learned(backend, reverse)
    core = sim.core
    a, b = core.available_actions
    values = [core.planner.homeostatic_estimate(core, {ids[0]}, action).progress for action in (a,b)]
    good = a if reverse else b
    assert values[0] > values[1] if reverse else values[1] > values[0]
    assert core.planner._search(core, {ids[0]}, 24).actions[0] == good
    assert core.planner.homeostatic_plan_component > 0
    if core.backend:
        assert core.backend.full_graph_sync_calls == 0


@pytest.mark.parametrize("backend", ["python", "native"])
def test_weak_repeated_and_contradictory_evidence(backend):
    weak, ids = learned(backend, repetitions=1)
    action = weak.core.available_actions[1]
    assert weak.core.planner.homeostatic_estimate(weak.core, {ids[0]}, action).progress == 0
    strong, ids = learned(backend)
    core = strong.core
    before = core.planner.homeostatic_estimate(core, {ids[0]}, action).progress
    for tick in range(24,48):
        acquire(core, {ids[0]}, action, {ids[1]}, tick)
    after = core.planner.homeostatic_estimate(core, {ids[0]}, action).progress
    assert 0 <= after < before


def test_no_evidence_no_bonus_and_ablation():
    sim, ids = learned(repetitions=0)
    for action in sim.core.available_actions:
        assert sim.core.planner.homeostatic_estimate(sim.core, {ids[0]}, action).progress == 0
    on, ids = learned()
    off, off_ids = learned(enabled=False)
    assert on.core.planner._search(on.core, {ids[0]},24).actions[0] == on.core.available_actions[1]
    assert off.core.planner.homeostatic_estimate(off.core, {off_ids[0]},off.core.available_actions[1]) is None
    off.core.planner._search(off.core, {off_ids[0]},24)
    assert off.core.planner.homeostatic_plan_component == 0
    without = Simulation(19, configured(interoception_enabled=False))
    without.step()
    assert not any(p.channel.startswith("internal_") for p in without.core.patterns.last_events)


@pytest.mark.parametrize("payload", [0., 60.])
def test_physical_counterfactual_same_resource_channel_delayed_sensor_evidence(payload):
    sim = Simulation(20, configured(), "native")
    core = sim.core
    action = ActionType.INTERACT_UP
    sim.physiology.hydration = 15.
    before = sim.interoception.sample(sim.physiology.snapshot())
    sim.world.native.set_body_state(0,3,4,"N")
    sim.world._refresh()
    sim.world.spawn_resource((3,3),2,1.,payload,0.,1)
    external = core.graph.add_cognit(Cognit(core.graph.next_id, activity=1.,
        pattern=CognitPattern(((0,-1,"appearance",2,1),)))).id
    assert core.planner.homeostatic_estimate(core,{external},action) is None
    sim.world.apply_action(Action(action))
    sim.apply_world_consequence()
    # Consequence is perceived at the next observation, after WorldTime advances.
    sim.physiology.advance_to(.15)
    after = sim.interoception.sample(sim.physiology.snapshot())
    core.patterns.layer.previous_internal = before.levels
    target = core.graph.add_cognit(Cognit(core.graph.next_id, pattern=CognitPattern(
        ((0,0,"internal_2",after.levels[2],SensoryEventKind.OCCUPIED_PRESENT.value),)))).id
    for tick in range(24):
        # Background experience makes evidence action-specific, not semantic.
        acquire(core, {external}, action if tick % 2 else ActionType.IDLE,
                {target} if tick % 2 else set(), tick)
    estimate = core.planner.homeostatic_estimate(core,{external},action)
    assert (estimate.progress > 0) == bool(payload)


@pytest.mark.parametrize("phase", [0., .01, .8])
def test_nondefault_causal_settings_exact_frontier_continuation(tmp_path, phase):
    settings = configured(perception_radius=7, sensory_neural_enabled=False,
        continuous_maintenance_interval_seconds=.17, planning_horizon=2,
        max_deliberation_cycles=3, spawn_interval_min=2, spawn_interval_max=4)
    original = ContinuousRuntime(21, settings)
    original.run_until(phase)
    path = tmp_path / "frontier.seworld"
    original.save_world(path)
    restored = ContinuousRuntime.load_world(path)
    assert restored.simulation.settings == settings
    assert restored.simulation.snapshot_data() == original.simulation.snapshot_data()
    assert restored.scheduler_state() == original.scheduler_state()
    assert restored.simulation.world.perceive(0) == original.simulation.world.perceive(0)
    for runtime in (original,restored):runtime.run_until(phase+.6)
    assert restored.simulation.snapshot_data() == original.simulation.snapshot_data()
    assert restored.scheduler_state() == original.scheduler_state()
    with pytest.raises(ValueError, match="incompatible"):
        ContinuousRuntime.load_world(path,replace(settings,perception_radius=4))
    with pytest.raises(ValueError, match="incompatible"):
        ContinuousRuntime.load_world(path,replace(settings,planning_horizon=3))


def test_internal_geometry_and_cross_modal_cooccurrence():
    sim = Simulation(22,configured())
    tracker = SensoryPatternTracker(sim.settings)
    frame = sim.world.perceive(0)
    observation, candidates = tracker.observe(frame,0.,{},InteroceptiveFrame(0.,(1,2,3)))
    assert any(any(not is_spatial_primitive(p) for p in proto.participants) and
               any(is_spatial_primitive(p) for p in proto.participants) for proto,_ in candidates)
    assert all(all(is_spatial_primitive(p) for p in proto.participants)
               for proto,_ in candidates if proto.translation_tolerant)
    internal = (0,0,"internal_0",1,1)
    pattern = CognitPattern((internal,),is_translation_tolerant=True)
    assert pattern.match(frozenset({(3,4,"internal_0",1,1)})) == 0


def test_learned_world_and_brain_transfer(tmp_path):
    sim, ids = learned("native")
    world = tmp_path / "learned.seworld"
    sim.save_world(world)
    restored = Simulation.load_world(world,backend="native")
    for action in sim.core.available_actions:
        assert sim.core.planner.homeostatic_estimate(sim.core,{ids[0]},action) == restored.core.planner.homeostatic_estimate(restored.core,{ids[0]},action)
    brain = tmp_path / "learned.sebrain"
    sim.save_brain(brain)
    target = Simulation(23,sim.settings,"native")
    target.load_brain(brain)
    assert target.core.patterns.layer.previous_internal is None
    assert target.core.planner.homeostatic_estimate(target.core,{ids[0]},ActionType.IDLE) is None
    target.core.patterns.layer.previous_internal = (6,4,1)
    assert target.core.planner.homeostatic_estimate(target.core,{ids[0]},sim.core.available_actions[1]).progress > 0


def test_hashseed_determinism():
    script = "import runpy,json; m=runpy.run_path('tests/test_v083_homeostatic_valuation.py'); s,ids=m['learned']('native'); p=s.core.planner._search(s.core,{ids[0]},24); print(json.dumps([p.actions[0].name,p.score,s.core.planner.homeostatic_diagnostics()],sort_keys=True))"
    results = [subprocess.check_output([sys.executable,"-c",script],cwd=Path(__file__).parents[1],
        env={**os.environ,"PYTHONHASHSEED":seed},text=True) for seed in ("1","777")]
    assert results[0] == results[1]


@pytest.mark.parametrize("backend", ["python", "native"])
def test_complete_observation_learning_prediction_planner_slice(backend):
    # Keep sensory activation above adaptation thresholds in this controlled
    # acquisition protocol. All Cognits and rho arise from ordinary core.step.
    sim = Simulation(10, configured(cognit_birth_threshold=0., proto_min_occurrences=1,
        max_new_cognits_per_tick=40, homeostasis_input_gain=0., sensory_activation=1.), backend)
    core = sim.core
    core.available_actions = tuple(ActionType)[:2]
    for tick in range(80):
        if tick % 2 == 0:
            core.previous_action = core.available_actions[0]
            level = 1
        else:
            core.previous_action = core.available_actions[1 if tick % 4 == 1 else 0]
            level = 6 if tick % 4 == 1 else 1
        core.step(sim.world.perceive(tick), internal=InteroceptiveFrame(float(tick),(6,4,level)))
    a, b = core.available_actions
    active = set(core.previous_active)
    assert core.planner.homeostatic_estimate(core,active,b).progress > core.planner.homeostatic_estimate(core,active,a).progress
    assert core.planner._search(core,active,81).actions[0] == b
    assert any(node.pattern and any(part[2].startswith("internal_") for part in node.pattern.participants)
               for node in core.graph.nodes.values())


@pytest.mark.parametrize("backend", ["python", "native"])
def test_short_trajectory_requires_learned_intermediate_state(backend):
    sim, ids = learned(backend, repetitions=0)
    core = sim.core
    core.settings = replace(core.settings,planning_horizon=2)
    core.planner.settings = core.settings
    intermediate = core.graph.add_cognit(Cognit(core.graph.next_id, activity=1.,
        pattern=CognitPattern(((2,0,"appearance",3,1),)))).id
    a, b = core.available_actions
    history = [({ids[0]},a,{intermediate}), ({ids[0]},b,set()),
               ({intermediate},a,{ids[1]}), ({intermediate},b,{ids[2]})]
    for tick in range(80):
        before,action,after = history[tick % 4]
        acquire(core,before,action,after,tick)
    assert core.planner.homeostatic_estimate(core,{ids[0]},a).progress == 0
    assert core.planner.homeostatic_estimate(core,{intermediate},b).progress > 0
    plan = core.planner._search(core,{ids[0]},41)
    assert plan.actions == (a,b)
    assert core.planner.homeostatic_plan_component > 0


def test_settings_classification_is_exhaustive_and_config_sources_conflict():
    from dataclasses import fields
    from simulation.persisted_settings import CAUSAL_GROUPS, causal_configuration, restore_settings
    from physiology.model import Physiology
    causal = {name for group in CAUSAL_GROUPS.values() for name in group} | set(Physiology.CONFIG_FIELDS)
    assert {field.name for field in fields(Settings)} == causal | {"telemetry_history","simulation_speeds","world_event_weights"}
    state = {"causal_config":causal_configuration(configured()),
             "world_config":{name:getattr(configured(),name) for name in Settings.WORLD_FIELDS}}
    state["world_config"]["world_width"] = 9
    with pytest.raises(ValueError,match="conflicting saved"):
        restore_settings(state)
    state = {"causal_config":causal_configuration(configured())}
    del state["causal_config"]["runtime"]["world_tick_interval"]
    with pytest.raises(ValueError,match="invalid saved"):
        restore_settings(state)


def test_interoception_off_valuation_flag_preserves_causal_behavior():
    first = ContinuousRuntime(29,configured(interoception_enabled=False,homeostatic_valuation_enabled=False))
    second = ContinuousRuntime(29,configured(interoception_enabled=False,homeostatic_valuation_enabled=True))
    for runtime in (first,second):runtime.run_until(1.)
    left,right = first.simulation.snapshot_data(),second.simulation.snapshot_data()
    # The artifact records the ablation flag; episode behavior must match.
    left.pop("causal_config");right.pop("causal_config")
    assert left == right
    assert first.scheduler_state() == second.scheduler_state()
    assert first.actions_completed == second.actions_completed


def test_diagnostics_are_detached_observations():
    sim,ids = learned("native")
    sim.core.planner._search(sim.core,{ids[0]},24)
    original = sim.core.planner.homeostatic_diagnostics()
    changed = sim.core.planner.homeostatic_diagnostics()
    changed["homeostatic_plan_component"] = -100
    assert sim.core.planner.homeostatic_diagnostics() == original


def test_native_physical_interaction_enters_ordinary_internal_relation_learning():
    sim = Simulation(40, configured(physiology_initial_hydration=15.,
        cognit_birth_threshold=0., proto_min_occurrences=1, max_new_cognits_per_tick=40,
        homeostasis_input_gain=0., sensory_activation=1.), "native")
    core = sim.core
    sim.world.native.set_body_state(0,3,4,"N")
    sim.world._refresh()
    for trial in range(24):
        # Controlled trial precondition. Only the subsequent real World
        # interaction supplies the improving consequence used for learning.
        sim.physiology.hydration = 15.
        time = trial * .3
        sim.physiology.advance_to(time)
        sim.world.advance_world_time(time)
        if not sim.world.resource_count():
            event = sim.world.native.time_state()[1] + 1
            sim.world.spawn_resource((3,3),2,0.,65.,time,event)
        core.previous_action = ActionType.IDLE
        before = sim.interoception.sample(sim.physiology.snapshot())
        core.step(sim.world.perceive(2*trial), internal=before)
        prior = set(core.previous_active)
        action = ActionType.INTERACT_UP if trial % 2 else ActionType.IDLE
        reserve = sim.physiology.hydration
        result = sim.world.apply_action(Action(action))
        assert result is ActionResult.SUCCESS
        sim.physiology.apply_action(action, True)
        sim.apply_world_consequence()
        if action is ActionType.INTERACT_UP:
            assert sim.physiology.hydration == reserve + 65.
            assert sim.world.resource_count() == 0
        else:
            assert sim.physiology.hydration == reserve
        assert sim.world.take_consequence() == (0.,0.)
        sim.physiology.advance_to(time+.15)
        sim.world.advance_world_time(time+.15)
        after = sim.interoception.sample(sim.physiology.snapshot())
        core.previous_action = action
        core.step(sim.world.perceive(2*trial+1), internal=after)
    assert after.levels[2] > before.levels[2]
    assert any(p.channel == "internal_2" and p.previous_value == before.levels[2]
               and p.value == after.levels[2] for p in core.patterns.last_events)
    targets = {node.id for node in core.graph.nodes.values() if node.pattern
        and len(node.pattern.participants) == 1
        and is_internal_primitive(node.pattern.participants[0])
        and node.pattern.participants[0][2] == "internal_2"
        and node.pattern.participants[0][3] == after.levels[2]}
    effects = core.planner.homeostatic_effects(core,prior,ActionType.INTERACT_UP)
    assert any(effects.get(target,0.) > 0 for target in targets)
    acquired = [relation for source in prior for relation in core.graph.outgoing(source)
        if relation.target_id in targets and relation.relation_type is RelationType.SELF_ACTION
        and relation.context_id == ActionType.INTERACT_UP.value]
    assert any(r.support >= sim.settings.relation_provisional_support
               and r.prediction_probability > 0 for r in acquired)
    assert core.backend.full_graph_sync_calls == 0


def test_competing_internal_bins_use_existing_coarse_marginal_normalization():
    from consciousness.graph import CognitiveGraph
    from consciousness.valuation import internal_estimate
    graph = CognitiveGraph()
    ids = [graph.add_cognit(Cognit(graph.next_id,
        pattern=CognitPattern(((0,0,"internal_2",level,1),)))).id for level in (1,6,6)]
    # Two distinct event Cognits for the same bin do not count twice; total
    # mass > 1 is normalized across competing bins, not a joint distribution.
    probabilities = {ids[0]:.8, ids[1]:.8, ids[2]:.6}
    estimate = internal_estimate(graph,probabilities,(6,4,1),(6,4,6),8)
    assert estimate.levels == pytest.approx((6,4,3.5))
    assert estimate.progress == pytest.approx(2.5/21)
    assert estimate.confidence == pytest.approx(1/3)
    assert estimate.predictions == 2
    assert estimate == internal_estimate(graph,dict(reversed(list(probabilities.items()))),
                                        (6,4,1),(6,4,6),8)
    partial = internal_estimate(graph,{ids[1]:.2},(6,4,1),(6,4,6),8)
    assert partial.levels == pytest.approx((6,4,2))
    assert partial.progress == pytest.approx(1/21)
