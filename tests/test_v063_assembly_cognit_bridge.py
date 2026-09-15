from consciousness._native_brain import NativeBrainEngine, NeurodynamicSubstrate


def _engine():
    configured = NeurodynamicSubstrate(
        assembly_tracking_enabled=True,
        assembly_window=2.,
        assembly_consolidation_support=3,
    )
    nodes = [configured.add_micro_kappa() for _ in range(9)]
    engine = NativeBrainEngine()
    engine.neurodynamic_substrate().restore(configured.snapshot())
    return engine, nodes


def _episode(engine, order, start, repeats=1):
    substrate = engine.neurodynamic_substrate()
    for repeat in range(repeats):
        base = start + repeat * 10.
        for index, node in enumerate(order):
            substrate.inject(node, 3., base + index * .5)
            substrate.advance_to(base + index * .5)


def _consolidate(engine, members, start=0.):
    _episode(engine, members, start, 3)
    rows = engine.process_assembly_bridge(1)
    born = [row for row in rows if row[4] == 0]
    assert len(born) == 1 and born[0][5]
    return born[0][1], born[0][2]


def test_candidate_and_one_shot_do_not_birth_but_consolidation_births_once():
    engine, nodes = _engine()
    _episode(engine, nodes[:3], 0., 2)
    assert engine.process_assembly_bridge(1) == []
    assert engine.cognit_count == 0
    _episode(engine, nodes[:3], 20.)
    rows = engine.process_assembly_bridge(2)
    assert len(rows) == 1 and rows[0][4:] == (0, True, False)
    assert engine.cognit_count == 1 and engine.assembly_cognit_mapping() == [(rows[0][1], rows[0][2])]
    assert engine.process_assembly_bridge(3) == []


def test_recognition_reuses_cognit_and_confidence_drives_ordinary_receive():
    engine, nodes = _engine(); assembly, cognit = _consolidate(engine, nodes[:3])
    engine.set_activity(cognit, 0.)
    _episode(engine, nodes[:2], 40.)
    partial = engine.process_assembly_bridge(10)
    partial_energy = sum(row[3] for row in partial if row[4] == 1)
    partial_activity = engine.cognit_state([cognit])[0]
    assert partial and all(row[1] == assembly and row[2] == cognit and not row[5] for row in partial)
    assert partial_activity == min(1., partial_energy)
    engine.set_activity(cognit, 0.)
    _episode(engine, nodes[:3], 50.)
    full = engine.process_assembly_bridge(11)
    full_energy = sum(row[3] for row in full if row[4] == 1)
    assert full_energy > partial_energy and engine.cognit_state([cognit])[0] == min(1., full_energy)
    engine.set_activity(cognit, 0.)
    _episode(engine, list(reversed(nodes[:3])), 60.)
    reversed_rows = engine.process_assembly_bridge(12)
    assert partial[-1][3] > reversed_rows[-1][3]


def test_overlap_and_novel_assemblies_get_distinct_cognits_without_relations():
    engine, nodes = _engine()
    ids = [_consolidate(engine, members, start)[1] for members, start in
           ((nodes[:3], 0.), (nodes[2:5], 40.), (nodes[5:8], 80.))]
    assert len(set(ids)) == 3 and engine.cognit_count == 3 and engine.relation_count == 0


def test_bridge_cursor_is_exactly_once_bounded_and_snapshot_preserves_pending_event(tmp_path):
    source, nodes = _engine(); _episode(source, nodes[:3], 0., 3)
    neuro = source.neurodynamic_substrate().snapshot()
    graph = tmp_path / "bridge.sebrain"; source.save_graph(str(graph))
    left, right = NativeBrainEngine(), NativeBrainEngine()
    for engine in (left, right):
        engine.load_graph(str(graph)); engine.neurodynamic_substrate().restore(neuro)
    first = left.process_assembly_bridge(1, 1)
    assert len(first) == 1 and left.process_assembly_bridge(1, 1) == []
    pending = right.process_assembly_bridge(1, 1)
    assert first == pending
    # A consumed event plus its mapping is restored with the matching graph state.
    consumed_graph = tmp_path / "consumed.sebrain"; left.save_graph(str(consumed_graph))
    bridge_state = left.assembly_bridge_state()
    restored = NativeBrainEngine(); restored.load_graph(str(consumed_graph)); restored.neurodynamic_substrate().restore(neuro)
    restored.restore_assembly_bridge_state(*bridge_state)
    assert restored.process_assembly_bridge(2) == []


def test_semantic_facade_adopts_native_birth_as_an_ordinary_neural_assembly_cognit():
    from consciousness.backends import NativeGraphBackend
    from consciousness.native_graph import NativeGraphFacade
    from config.settings import Settings
    backend = NativeGraphBackend(Settings()); graph = NativeGraphFacade(backend)
    configured = NeurodynamicSubstrate(assembly_tracking_enabled=True, assembly_window=2., assembly_consolidation_support=3)
    nodes = [configured.add_micro_kappa() for _ in range(3)]
    backend.engine.neurodynamic_substrate().restore(configured.snapshot())
    _episode(type("Holder", (), {"neurodynamic_substrate": lambda self: backend.engine.neurodynamic_substrate()})(), nodes, 0., 3)
    active = backend.process_assembly_bridge(graph, 7)
    mapping = backend.engine.assembly_cognit_mapping(); assert len(mapping) == 1
    node = graph.nodes[mapping[0][1] + 1]
    assert node.kind == "NEURAL_ASSEMBLY" and active == set() and backend.engine.relation_count == 0


def test_deleted_assembly_cognit_is_invalidated_and_recognition_rebirths_monotonically():
    engine, nodes = _engine(); assembly, old = _consolidate(engine, nodes[:3])
    assert engine.remove_cognit(old) and engine.assembly_cognit_mapping() == []
    _episode(engine, nodes[:3], 40.)
    rows = engine.process_assembly_bridge(5)
    assert rows[0][5] and rows[0][1] == assembly and rows[0][2] > old
    assert engine.assembly_cognit_mapping() == [(assembly, rows[0][2])]


def test_silent_scale_has_zero_bridge_work():
    engine = NativeBrainEngine(); substrate = engine.neurodynamic_substrate()
    for _ in range(10_000): substrate.add_micro_kappa()
    substrate.advance_to(50_000.)
    assert engine.process_assembly_bridge(1) == []
    assert engine.cognit_count == 0 and engine.assembly_bridge_state() == (0, [], 0, 0)
