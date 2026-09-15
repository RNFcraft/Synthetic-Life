from consciousness._native_brain import NeurodynamicSubstrate


def _substrate():
    return NeurodynamicSubstrate(assembly_tracking_enabled=True, assembly_window=2., assembly_consolidation_support=3)


def _train(substrate, order, start, repeats=1):
    for repeat in range(repeats):
        base = start + repeat * 10.
        for index, node in enumerate(order):
            substrate.inject(node, 3., base + index * .5)
            substrate.advance_to(base + index * .5)


def test_recurrent_native_spike_sequences_form_temporal_assembly_not_one_shot():
    substrate = _substrate(); nodes = [substrate.add_micro_kappa() for _ in range(4)]
    _train(substrate, nodes[:3], 0.)
    assert not any(row[-1] for row in substrate.assemblies())
    _train(substrate, nodes[:3], 10., 2)
    assemblies = substrate.assemblies()
    assert len(assemblies) == 1
    _, members, edges, support, _, _, consolidated = assemblies[0]
    assert members == nodes[:3] and edges == [(nodes[0], nodes[1]), (nodes[1], nodes[2])] and support == 3 and consolidated


def test_reversed_temporal_order_creates_distinct_native_structure():
    left = _substrate(); right = _substrate()
    left_nodes = [left.add_micro_kappa() for _ in range(3)]; right_nodes = [right.add_micro_kappa() for _ in range(3)]
    _train(left, left_nodes, 0., 3); _train(right, list(reversed(right_nodes)), 0., 3)
    assert left.assemblies()[0][2] != right.assemblies()[0][2]


def test_rare_noise_does_not_join_recurrent_core_and_tracking_disabled_is_read_only():
    substrate = _substrate(); nodes = [substrate.add_micro_kappa() for _ in range(4)]
    _train(substrate, nodes[:3], 0., 3); _train(substrate, nodes, 40.)
    assert substrate.assemblies()[0][1] == nodes[:3]
    disabled = NeurodynamicSubstrate(); ids = [disabled.add_micro_kappa() for _ in range(3)]
    _train(disabled, ids, 0., 4)
    assert disabled.assemblies() == []


def test_silent_scale_does_no_assembly_work():
    substrate = _substrate()
    for _ in range(10_000): substrate.add_micro_kappa()
    substrate.advance_to(1_000_000.)
    assert substrate.assemblies() == []
