"""Durable sensor topology compatibility, without transferring body state."""
from dataclasses import replace

import pytest

from config import Settings
from consciousness.cognit import Cognit
from consciousness.patterns import CognitPattern, PatternNode, PatternParticipantType
from persistence import load_container, save_container
from physiology.interoception import InteroceptiveFrame, InteroceptiveTransducer
from simulation import Simulation
from simulation.brain_sensor_contract import internal_knowledge
from world import ActionType


def settings(bins=8, **changes):
    return replace(Settings(world_width=8, world_height=8, object_count=0, max_objects=0,
        interoception_enabled=True, interoception_bins=bins, homeostatic_valuation_enabled=True,
        cognit_birth_threshold=0., proto_min_occurrences=1, max_new_cognits_per_tick=40,
        homeostasis_input_gain=0., sensory_activation=1.), **changes)


def source_brain(tmp_path, bins=8, backend="native"):
    source = Simulation(71, settings(bins), backend)
    core = source.core
    actions = tuple(ActionType)[:2]
    high = source.interoception.target_levels[2]
    for tick in range(80):
        action = actions[1] if tick % 4 == 1 else actions[0]
        level = high if tick % 4 == 1 else 1
        core.previous_action = action
        core.step(source.world.perceive(tick), internal=InteroceptiveFrame(float(tick), (high,1,level)))
    source.core.planner._search(core, set(core.previous_active), 80)
    source.physiology.advance_to(5.)
    path = tmp_path / f"learned-{bins}-{backend}.sebrain"
    source.save_brain(path)
    return source, path


@pytest.mark.parametrize("backend", ["python", "native"])
def test_compatible_transfer_retains_knowledge_resets_episode(tmp_path, backend):
    source, path = source_brain(tmp_path, backend=backend)
    sections = load_container(path, "brain")
    assert sections["META"]["version"] == (6 if backend == "native" else 4)
    assert sections["META"]["internal_sensor_contract"] == {
        "schema":1, "encoding":"reserve-ratio-floor-v1",
        "channels":["internal_0","internal_1","internal_2"], "bins":8}
    target = Simulation(72, source.settings, backend)
    initial_body = target.physiology.to_dict()
    target.load_brain(path)
    assert target.physiology.to_dict() == initial_body
    assert target.core.patterns.layer.previous_internal is None
    assert target.core.planner.plan is None
    assert target.core.continuous_frontier is None
    assert all(value == 0 for value in target.core.planner.homeostatic_diagnostics().values())
    assert all(node.activity == 0 for node in target.core.graph.nodes.values())
    assert target.core.graph.relation_count == source.core.graph.relation_count
    assert [n.pattern for n in target.core.graph.nodes.values()] == [n.pattern for n in source.core.graph.nodes.values()]
    # Fresh ordinary observation reactivates acquired knowledge; no bin injection
    # into planner, manual Relation probabilities, or transferred activation.
    target.physiology.hydration = 15.
    internal = target.interoception.sample(target.physiology.snapshot())
    target.core.step(target.world.perceive(81), internal=internal)
    active = set(target.core.previous_active)
    a, b = tuple(ActionType)[:2]
    assert target.core.planner.homeostatic_estimate(target.core,active,b).progress > target.core.planner.homeostatic_estimate(target.core,active,a).progress
    if target.core.backend:
        assert target.core.backend.full_graph_sync_calls == 0


@pytest.mark.parametrize("backend", ["python", "native"])
@pytest.mark.parametrize("bins,target_bins", [(8,4),(4,8)])
def test_topology_mismatch_rejected_before_graph_activation(tmp_path, backend, bins, target_bins):
    _, path = source_brain(tmp_path, bins, backend)
    target = Simulation(73, settings(target_bins), backend)
    original_core = target.core
    original = target.snapshot_data()
    with pytest.raises(ValueError, match="incompatible brain internal sensor contract"):
        target.load_brain(path)
    assert target.core is original_core
    assert target.snapshot_data() == original


@pytest.mark.parametrize("legacy", [False,True])
@pytest.mark.parametrize("backend", ["python","native"])
def test_external_only_brain_has_no_topology_dependency(tmp_path, legacy, backend):
    source = Simulation(74, settings(4,interoception_enabled=False), backend)
    source.core.step(source.world.perceive(0))
    path = tmp_path / "external.sebrain"
    source.save_brain(path)
    sections = load_container(path,"brain")
    assert not internal_knowledge(sections)
    assert "internal_sensor_contract" not in sections["META"]
    if not legacy:
        # Even irrelevant metadata must not impose an artificial dependency.
        sections["META"]["internal_sensor_contract"] = InteroceptiveTransducer.sensor_contract(source.settings)
        save_container(path,"brain",sections,{"LANG","NBRN"})
    target = Simulation(75, settings(8), backend)
    target.load_brain(path)
    assert target.core.graph.relation_count == source.core.graph.relation_count


@pytest.mark.parametrize("backend", ["python","native"])
def test_legacy_internal_brain_fails_closed(tmp_path, backend):
    _, path = source_brain(tmp_path, backend=backend)
    sections = load_container(path,"brain")
    sections["META"].pop("internal_sensor_contract")
    save_container(path,"brain",sections,{"LANG","NBRN"})
    target = Simulation(76, settings(), backend)
    with pytest.raises(ValueError,match="legacy brain.*no internal sensor contract"):
        target.load_brain(path)


@pytest.mark.parametrize("change", [
    {"schema":2}, {"schema":True}, {"bins":True},
    {"encoding":"unknown-v2"}, {"channels":["internal_2","internal_1","internal_0"]},
    {"channels":["internal_0","internal_1"]}, {"current_levels":[1,2,3]}])
def test_representation_contract_mismatch_or_malformed_metadata(tmp_path, change):
    _, path = source_brain(tmp_path)
    sections = load_container(path,"brain")
    sections["META"]["internal_sensor_contract"].update(change)
    save_container(path,"brain",sections,{"LANG","NBRN"})
    with pytest.raises(ValueError,match="incompatible brain internal sensor contract"):
        Simulation(77,settings(),"native").load_brain(path)


def test_internal_proto_knowledge_also_requires_contract(tmp_path):
    source = Simulation(78,settings(cognit_birth_threshold=1.),"native")
    source.core.step(source.world.perceive(0), internal=source.interoception.sample(source.physiology.snapshot()))
    assert not any(n.pattern for n in source.core.graph.nodes.values())
    path = tmp_path / "proto.sebrain"
    source.save_brain(path)
    sections = load_container(path,"brain")
    assert internal_knowledge(sections)
    assert "internal_sensor_contract" in sections["META"]
    with pytest.raises(ValueError,match="incompatible brain internal sensor contract"):
        Simulation(79,settings(4),"native").load_brain(path)


def test_primitive_pattern_node_is_structurally_detected(tmp_path):
    source = Simulation(80,settings(),"native")
    primitive = (0,0,"internal_2",3,1)
    source.core.graph.add_cognit(Cognit(source.core.graph.next_id, pattern=CognitPattern((),
        nodes=(PatternNode(PatternParticipantType.PRIMITIVE,primitive),))))
    path = tmp_path / "pattern-node.sebrain"
    source.save_brain(path)
    sections = load_container(path,"brain")
    assert internal_knowledge(sections)
    with pytest.raises(ValueError,match="incompatible brain internal sensor contract"):
        Simulation(81,settings(4),"native").load_brain(path)
