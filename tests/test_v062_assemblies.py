from consciousness._native_brain import MicroPolarity, NeurodynamicSubstrate


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
    assert members == nodes[:3] and edges == [(nodes[0], nodes[1]), (nodes[0], nodes[2]), (nodes[1], nodes[2])] and support == 3 and consolidated


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
    for index in range(50_000): substrate.add_micro_rho(index % 10_000, (index + 1) % 10_000, .1, 1., MicroPolarity.EXCITATORY)
    substrate.advance_to(1_000_000.)
    assert substrate.assemblies() == [] and substrate.telemetry()[14:18] == (0, 0, 0, 0)


def test_jitter_same_time_and_partial_temporal_recognition():
    substrate = _substrate(); nodes = [substrate.add_micro_kappa() for _ in range(3)]
    _train(substrate, nodes, 0., 3)
    assembly_id = substrate.assemblies()[0][0]
    # Jitter reinforces the same record.
    for node, time in zip(nodes, (40., 40.45, 41.1)):
        substrate.inject(node, 3., time); substrate.advance_to(time)
    assert len(substrate.assemblies()) == 1
    full = substrate.recent_assembly_matches()[-1]
    _train(substrate, nodes[:2], 50.)
    partial = substrate.recent_assembly_matches()[-1]
    _train(substrate, list(reversed(nodes)), 60.)
    reversed_match = substrate.recent_assembly_matches()[-1]
    assert full[0] == partial[0] == reversed_match[0] == assembly_id
    assert full[1] > partial[1] > reversed_match[1] and 0 < partial[2] < 1

    def simultaneous(reverse):
        s = _substrate(); ids = [s.add_micro_kappa() for _ in range(3)]
        for node in reversed(ids[:2]) if reverse else ids[:2]: s.inject(node, 3., 0.)
        s.advance_to(0.); s.inject(ids[2], 3., .5); s.advance_to(.5)
        return s.assemblies()[0][2]
    assert simultaneous(False) == simultaneous(True) == [(0, 2), (1, 2)]


def test_overlapping_and_novel_assemblies_and_frequent_distractor_rejection():
    substrate = _substrate(); nodes = [substrate.add_micro_kappa() for _ in range(9)]
    # Frequent isolated distractor activity is outside every trained episode.
    for index in range(6):
        substrate.inject(nodes[8], 3., index * 10.); substrate.advance_to(index * 10.)
    _train(substrate, nodes[:3], 70., 3)
    _train(substrate, nodes[2:5], 110., 3)
    _train(substrate, nodes[5:8], 150., 3)
    consolidated = [row for row in substrate.assemblies() if row[-1]]
    member_sets = [set(row[1]) for row in consolidated]
    assert set(nodes[:3]) in member_sets and set(nodes[2:5]) in member_sets and set(nodes[5:8]) in member_sets
    assert nodes[2] in member_sets[member_sets.index(set(nodes[:3]))] & member_sets[member_sets.index(set(nodes[2:5]))]
    assert all(nodes[8] not in members for members in member_sets)


def test_tracking_is_read_only_to_neural_physics_and_candidates_are_bounded():
    def physics(enabled):
        s = NeurodynamicSubstrate(assembly_tracking_enabled=enabled, adaptation_increment=.2, homeostasis_spike_increment=.1)
        ids = [s.add_micro_kappa() for _ in range(3)]
        _train(s, ids, 0., 4)
        snap = s.snapshot()
        return s.states(ids), snap["weight"], snap["pending"], snap["next_sequence"], s.telemetry()[:14]
    assert physics(False) == physics(True)

    bounded = _substrate(); ids = [bounded.add_micro_kappa() for _ in range(210)]
    for index in range(70): _train(bounded, ids[index * 3:index * 3 + 3], index * 10.)
    assert len([row for row in bounded.assemblies() if not row[-1]]) <= 64
    assert bounded.telemetry()[21] > 0


def test_candidate_snapshot_restore_has_exact_assembly_continuation_and_telemetry():
    uninterrupted = _substrate(); nodes = [uninterrupted.add_micro_kappa() for _ in range(3)]
    _train(uninterrupted, nodes, 0., 2)
    restored = NeurodynamicSubstrate(); restored.restore(uninterrupted.snapshot())
    _train(uninterrupted, nodes, 30.); _train(restored, nodes, 30.)
    assert uninterrupted.snapshot() == restored.snapshot()
    assert uninterrupted.assemblies() == restored.assemblies()
    telemetry = uninterrupted.telemetry()
    assert telemetry[14] >= 1 and telemetry[15] == 1 and telemetry[17] >= 1


def test_temporal_identity_is_closed_over_normalized_members_with_real_distractor_evidence():
    substrate = _substrate(); a, b, c, x = [substrate.add_micro_kappa() for _ in range(4)]
    # X is globally frequent, then also occurs inside three genuine ABC windows.
    for index in range(12):
        time = index * 5.
        substrate.inject(x, 3., time); substrate.advance_to(time)
    _train(substrate, [a, b, c], 70., 3)
    for repeat in range(3):
        base = 110. + repeat * 10.
        for node, offset in ((a, 0.), (x, .25), (b, .5), (c, 1.)):
            substrate.inject(node, 3., base + offset); substrate.advance_to(base + offset)

    assembly = next(row for row in substrate.assemblies() if row[1] == [a, b, c])
    assert x not in assembly[1]
    assert {(a, b), (a, c), (b, c)}.issubset(set(assembly[2]))
    assert all(x not in edge for edge in assembly[2])

    snapshot = substrate.snapshot()
    raw = next(row for row in snapshot["assembly_records"] if row[0] == assembly[0])
    x_temporal_evidence = [row for row in raw[4] if int(row[0]) == x or int(row[1]) == x]
    assert x_temporal_evidence and max(row[2] for row in x_temporal_evidence) >= 3

    restored = NeurodynamicSubstrate(); restored.restore(snapshot)
    restored_assembly = next(row for row in restored.assemblies() if row[0] == assembly[0])
    assert restored_assembly == assembly and all(x not in edge for edge in restored_assembly[2])
