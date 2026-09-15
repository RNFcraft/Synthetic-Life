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
    assert len(rows) == 1 and rows[0][4:7] == (0, True, False)
    assert engine.cognit_count == 1 and engine.assembly_cognit_mapping() == [(rows[0][1], rows[0][2])]
    assert engine.process_assembly_bridge(3) == []


def test_recognition_reuses_cognit_and_confidence_drives_ordinary_receive():
    engine, nodes = _engine(); assembly, cognit = _consolidate(engine, nodes[:3])
    engine.set_activity(cognit, 0.)
    _episode(engine, nodes[:2], 40.)
    partial = engine.process_assembly_bridge(10)
    partial_energy = sum(row[9] for row in partial if row[4] == 1)
    partial_activity = engine.cognit_state([cognit])[0]
    assert partial and all(row[1] == assembly and row[2] == cognit and not row[5] for row in partial)
    assert partial_activity == min(1., partial_energy)
    engine.set_activity(cognit, 0.)
    _episode(engine, nodes[:3], 50.)
    full = engine.process_assembly_bridge(11)
    full_energy = sum(row[9] for row in full if row[4] == 1)
    assert full_energy > partial_energy and engine.cognit_state([cognit])[0] == min(1., full_energy)
    engine.set_activity(cognit, 0.)
    _episode(engine, list(reversed(nodes[:3])), 60.)
    reversed_rows = engine.process_assembly_bridge(12)
    assert partial[-1][3] > reversed_rows[-1][3]
    assert engine.cognit_state([cognit])[0] == sum(row[9] for row in reversed_rows)


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
    from consciousness._native_brain import MicroPolarity
    for index in range(50_000):substrate.add_micro_rho(index%10_000,(index+1)%10_000,.1,1.,MicroPolarity.EXCITATORY)
    substrate.advance_to(50_000.)
    assert engine.process_assembly_bridge(1) == []
    assert engine.cognit_count == 0 and engine.assembly_bridge_state() == (0, [], 0, 0, 0)


def test_bridge_drain_does_not_change_upstream_neural_physics():
    left,nodes=_engine();right,right_nodes=_engine();_episode(left,nodes[:3],0.,4);_episode(right,right_nodes[:3],0.,4)
    before=left.neurodynamic_substrate().snapshot();assert before==right.neurodynamic_substrate().snapshot()
    left.process_assembly_bridge(9)
    assert left.neurodynamic_substrate().snapshot()==right.neurodynamic_substrate().snapshot()


def test_production_bridge_log_remains_bounded():
    engine,nodes=_engine();_consolidate(engine,nodes[:3])
    for index in range(300):
        time=40.+index*3.;engine.neurodynamic_substrate().inject(nodes[0],100.,time);engine.neurodynamic_substrate().advance_to(time)
    snapshot=engine.neurodynamic_substrate().snapshot()
    assert len(snapshot["assembly_bridge_events"])==256


def _recognition_activity(order):
    engine,nodes=_engine();_,cognit=_consolidate(engine,nodes[:3]);engine.set_activity(cognit,0.);_episode(engine,[nodes[i] for i in order],40.);rows=engine.process_assembly_bridge(9)
    return engine.cognit_state([cognit])[0],sum(row[9] for row in rows),rows


def test_actual_cognit_activity_is_full_then_partial_then_reversed_without_incremental_inflation():
    full,full_energy,full_rows=_recognition_activity((0,1,2));partial,partial_energy,_=_recognition_activity((0,1));reversed_activity,reversed_energy,_=_recognition_activity((2,1,0))
    assert full>partial>reversed_activity
    assert (full,partial,reversed_activity)==(full_energy,partial_energy,reversed_energy)
    assert full==max(row[3] for row in full_rows if row[4]==1)<=1.
    episode_ids={row[8] for row in full_rows if row[4]==1};assert len(episode_ids)==1


def test_separated_recurrences_each_contribute_one_bounded_recognition():
    engine,nodes=_engine();_,cognit=_consolidate(engine,nodes[:3])
    activities=[];episodes=[]
    for start in (40.,50.):
        engine.set_activity(cognit,0.);_episode(engine,nodes[:3],start);rows=engine.process_assembly_bridge(int(start));activities.append(engine.cognit_state([cognit])[0]);episodes.append({row[8] for row in rows})
    assert activities[0]==activities[1] and activities[0]<=1. and episodes[0].isdisjoint(episodes[1])


def test_global_cognit_capacity_and_per_drain_birth_budget_are_deterministic():
    engine,nodes=_engine()
    for members,start in ((nodes[:3],0.),(nodes[3:6],40.),(nodes[6:9],80.)):_episode(engine,members,start,3)
    rows=engine.process_assembly_bridge(1,64,2,1)
    assert engine.cognit_count==1 and sum(row[5] for row in rows)==1 and any(row[10] for row in rows)
    assert engine.assembly_bridge_state()[4]>0 and engine.process_assembly_bridge(2,64,2,1)==[]
    mapped_assembly=engine.assembly_cognit_mapping()[0][0];unmapped=next(row[0] for row in engine.neurodynamic_substrate().assemblies() if row[-1] and row[0]!=mapped_assembly)
    old=engine.assembly_cognit_mapping()[0][1];engine.remove_cognit(old)
    members=next(row[1] for row in engine.neurodynamic_substrate().assemblies() if row[0]==unmapped);_episode(engine,members,120.);rebirth=engine.process_assembly_bridge(3,64,2,1)
    assert any(row[1]==unmapped and row[5] and row[2]>old for row in rebirth) and len(engine.assembly_cognit_mapping())==1


def test_mid_recognition_snapshot_restore_preserves_peak_and_exact_continuation(tmp_path):
    left,nodes=_engine();_,cognit=_consolidate(left,nodes[:3]);left.set_activity(cognit,0.);_episode(left,nodes[:2],40.);left.process_assembly_bridge(10)
    graph=tmp_path/"mid.sebrain";left.save_graph(str(graph));neuro=left.neurodynamic_substrate().snapshot();bridge=left.assembly_bridge_state()
    right=NativeBrainEngine();right.load_graph(str(graph));right.neurodynamic_substrate().restore(neuro);right.restore_assembly_bridge_state(*bridge)
    for engine in (left,right):engine.neurodynamic_substrate().inject(nodes[2],3.,41.);engine.neurodynamic_substrate().advance_to(41.)
    assert left.process_assembly_bridge(11)==right.process_assembly_bridge(11)
    assert left.cognit_state([cognit])==right.cognit_state([cognit]) and left.neurodynamic_substrate().snapshot()==right.neurodynamic_substrate().snapshot()


def test_restore_rejects_bridge_overflow_and_invalid_episode_state():
    import pytest
    engine,nodes=_engine();_consolidate(engine,nodes[:3]);snapshot=engine.neurodynamic_substrate().snapshot()
    bad=dict(snapshot);bad["assembly_bridge_events"]=snapshot["assembly_bridge_events"]*257
    with pytest.raises(ValueError):NeurodynamicSubstrate().restore(bad)
    bad=dict(snapshot);bad["next_recognition_episode_id"]=0
    with pytest.raises(ValueError):NeurodynamicSubstrate().restore(bad)


def test_continuous_bridge_delivery_needs_no_new_world_observation():
    from simulation.continuous import ContinuousRuntime
    from consciousness.native_engine import RuntimeEvent,RuntimeEventType
    runtime=ContinuousRuntime(901);runtime.run_to_quiescence();observations=runtime.observation_ordinal;engine=runtime.simulation.core.backend.engine
    configured=NeurodynamicSubstrate(assembly_tracking_enabled=True,assembly_window=2.,assembly_consolidation_support=3);nodes=[configured.add_micro_kappa() for _ in range(3)];engine.neurodynamic_substrate().restore(configured.snapshot())
    _episode(engine,nodes,10.,3);runtime._process(RuntimeEvent(31.,9001,RuntimeEventType.NEURAL_BRIDGE,0));mapping=engine.assembly_cognit_mapping();assert len(mapping)==1
    for index,start in enumerate((40.,50.),1):_episode(engine,nodes,start);runtime._process(RuntimeEvent(start+1.,9001+index,RuntimeEventType.NEURAL_BRIDGE,0))
    recognized=[row for row in runtime.neural_bridge_deliveries if row[4]==1 and row[9]>0]
    assert len({row[8] for row in recognized})==2 and {row[2] for row in recognized}=={mapping[0][1]} and runtime.observation_ordinal==observations
    assert [(row[7],row[0]) for row in recognized]==sorted((row[7],row[0]) for row in recognized)


def _continuous_runtime_with_scheduled_history(event_count=2):
    from simulation.continuous import ContinuousRuntime
    runtime=ContinuousRuntime(902);runtime.run_to_quiescence();engine=runtime.simulation.core.backend.engine
    configured=NeurodynamicSubstrate(assembly_tracking_enabled=True,assembly_window=2.,assembly_consolidation_support=3);nodes=[configured.add_micro_kappa() for _ in range(3)];engine.neurodynamic_substrate().restore(configured.snapshot())
    substrate=engine.neurodynamic_substrate()
    for repeat in range(3):
        for index,node in enumerate(nodes):substrate.inject(node,3.,repeat*10.+index*.5)
    for index in range(event_count):substrate.inject(nodes[0],100.,40.+index*3.)
    return runtime,nodes


def test_event_time_is_causal_and_neural_advance_batching_has_exact_parity():
    left,_=_continuous_runtime_with_scheduled_history(2);right,_=_continuous_runtime_with_scheduled_history(2)
    left.advance_neural_to(41.);left.run_until(41.);left.advance_neural_to(50.);left.run_until(50.)
    right.advance_neural_to(50.);right.run_until(50.)
    le, re=left.simulation.core.backend.engine,right.simulation.core.backend.engine
    assert left.neural_bridge_deliveries==right.neural_bridge_deliveries
    assert le.assembly_bridge_state()==re.assembly_bridge_state()
    assert le.assembly_cognit_mapping()==re.assembly_cognit_mapping()
    cognit=le.assembly_cognit_mapping()[0][1]
    assert le.cognit_state_full([cognit])==re.cognit_state_full([cognit])
    assert le.continuous_time_state()==re.continuous_time_state()
    recognized=[row for row in left.neural_bridge_deliveries if row[4]==1 and row[9]>0]
    assert len(recognized)>=2 and recognized[-1][7]>recognized[-2][7]
    # The first activation decays before the second one arrives; treating both
    # as simultaneous at t=50 would leave their undiminished energy sum.
    assert le.cognit_state([cognit])[0]<sum(row[9] for row in recognized)


def test_single_long_neural_advance_streams_more_than_bounded_log_exactly_once():
    runtime,_=_continuous_runtime_with_scheduled_history(520);observations=runtime.observation_ordinal
    from consciousness._native_brain import EventScheduler
    runtime.scheduler=EventScheduler();runtime.advance_neural_to(1_600.);runtime.run_until(1_600.)
    engine=runtime.simulation.core.backend.engine;rows=runtime.neural_bridge_deliveries
    sequences=[row[0] for row in rows]
    assert len(rows)>500 and sequences==list(range(1,sequences[-1]+1))
    assert len(sequences)==len(set(sequences))
    assert engine.assembly_bridge_state()[0]==sequences[-1]
    assert len(engine.neurodynamic_substrate().snapshot()["assembly_bridge_events"])<=256
    assert len(engine.assembly_cognit_mapping())==1 and runtime.observation_ordinal==observations


def test_neural_bridge_shares_global_scheduler_chronology():
    runtime,_=_continuous_runtime_with_scheduled_history(1);order=[];original=runtime._process
    runtime.inject_language("before-five",5.);runtime.inject_language("before-ten",10.)
    def recorded(event):
        if event.type.name in {"LANGUAGE_INPUT","NEURAL_BRIDGE"}:order.append((event.time,event.type.name,event.id))
        original(event)
    runtime._process=recorded;runtime.advance_neural_to(50.);runtime.run_until(50.)
    assert [row[:2] for row in order[:3]]==[(5.,"LANGUAGE_INPUT"),(10.,"LANGUAGE_INPUT"),(21.,"NEURAL_BRIDGE")]
    assert runtime.simulation.core.backend.engine.continuous_time_state()[2]==50.


def _runtime_with_downstream_relation():
    from consciousness._native_brain import EventScheduler
    from consciousness.relation import RelationStatus
    runtime,nodes=_continuous_runtime_with_scheduled_history(0);runtime.scheduler=EventScheduler();runtime.advance_neural_to(31.);runtime.run_until(31.)
    engine=runtime.simulation.core.backend.engine;assembly=engine.assembly_cognit_mapping()[0][1]+1;runtime.simulation.core.graph.nodes[assembly].threshold=runtime.simulation.core.graph.nodes[assembly].homeostatic_threshold=.01;target=runtime.simulation.core.graph.add_cognit();target.threshold=target.homeostatic_threshold=.01
    relation,_=runtime.simulation.core.graph.connect(assembly,target.id);relation.strength=relation.confidence=1.;relation.status=RelationStatus.CONSOLIDATED
    substrate=engine.neurodynamic_substrate()
    for start in (40.,70.):
        for index,node in enumerate(nodes):substrate.inject(node,100.,start+index*.5)
    return runtime,assembly,target.id


def _bridge_causal_state(runtime,source,target):
    engine=runtime.simulation.core.backend.engine;relation=runtime.simulation.core.graph.outgoing(source)[0]
    return (engine.cognit_state_full([source-1,target-1]),relation.strength,relation.confidence,relation.last_used_cognitive_tick,engine.continuous_time_state(),engine.assembly_bridge_state(),runtime.scheduler_state())


def test_downstream_wave_occurs_at_event_time_and_batching_is_invariant():
    left,source,target=_runtime_with_downstream_relation();right,right_source,right_target=_runtime_with_downstream_relation()
    left.advance_neural_to(45.);left.run_until(45.)
    assert left.simulation.core.graph.nodes[target].last_activated_cognitive_tick is not None and left.simulation.core.graph.nodes[target].activity>0.
    left.advance_neural_to(80.);left.run_until(80.)
    right.advance_neural_to(80.);right.run_until(80.)
    assert _bridge_causal_state(left,source,target)==_bridge_causal_state(right,right_source,right_target)
    assert left.simulation.core.graph.nodes[target].last_activated_cognitive_tick is not None
    recognized=[row for row in left.neural_bridge_deliveries if row[4]==1 and row[9]>0]
    assert recognized and left.simulation.core.graph.nodes[target].last_activated_cognitive_tick==left.simulation.core.graph.nodes[source].last_activated_cognitive_tick


def test_snapshot_with_scheduled_bridge_resumes_once(tmp_path):
    runtime,_=_continuous_runtime_with_scheduled_history(3);runtime.advance_neural_to(60.)
    assert any(row[2]=="NEURAL_BRIDGE" for row in runtime.scheduler_state()["events"])
    path=tmp_path/"pending-bridge.seworld";runtime.save_world(path);restored=runtime.load_world(path)
    runtime.run_until(60.);restored.run_until(60.)
    assert runtime.neural_bridge_deliveries==restored.neural_bridge_deliveries
    assert runtime.simulation.core.backend.engine.assembly_bridge_state()==restored.simulation.core.backend.engine.assembly_bridge_state()
    assert runtime.scheduler_state()==restored.scheduler_state()
