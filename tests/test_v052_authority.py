import pytest
from config import Settings
from consciousness.native_engine import NativeBrainEngine,EvidenceConfig
from consciousness.backends import NativeGraphBackend
from consciousness.relation import RelationType


def test_deleted_cognit_cannot_be_revived_by_evidence_or_relations(tmp_path):
    e=NativeBrainEngine();e.add_cognits(3,1.)
    h=e.add_relation(0,1,RelationType.SEQUENTIAL.value)
    e.add_relation(1,2,RelationType.SEQUENTIAL.value)
    for _ in range(8):e.update_transition_evidence([0,1],2,[1,2])
    assert e.remove_cognit(1) and not e.remove_cognit(1)
    assert not e.relation_handle_valid(h)
    assert e.cognit_count==3 and e.live_cognit_count==2
    assert 1 not in e.propagate([0,1],2)[0]
    assert all(t!=1 for t,_ in e.predict([0,1],2))
    e.materialize_relations(EvidenceConfig(),3)
    assert all(row[0]!=1 and row[1]!=1 for row in e.outgoing([0,1,2]))
    with pytest.raises(IndexError):e.set_activity(1,1.)
    with pytest.raises(IndexError):e.add_relation(0,1,1)
    assert e.add_cognit()==3
    path=tmp_path/'deleted.bin';e.save_graph(str(path));loaded=NativeBrainEngine();loaded.load_graph(str(path))
    assert not loaded.cognit_alive(1) and loaded.live_cognit_count==3


def test_relation_context_id_is_not_truncated_and_reconnect_preserves_state():
    e=NativeBrainEngine();e.add_cognits(2)
    handle=e.add_relation(0,1,RelationType.SPATIAL.value,1001,.8,.7,.6)
    first=e.outgoing([0])[0]
    assert first[3]==1001
    assert tuple(first[15])==tuple(handle)
    again=e.add_relation(0,1,RelationType.SPATIAL.value,1001,.2,.3,0.)
    second=e.outgoing([0])[0]
    assert tuple(again)==tuple(handle)
    assert second[4:7]==pytest.approx((.8,.7,.6))
    assert e.provisional_count==1 and e.consolidated_count==0


def test_native_mutation_invalidates_cached_numeric_state():
    b=NativeGraphBackend(Settings());b.engine.add_cognit()
    assert b.cognit_state_one(1)[0]==0
    b.engine.set_activity(0,.8)
    assert b.cognit_state_one(1)[0]==pytest.approx(.8)
    b.engine.set_refractory(0,2)
    assert b.cognit_state_one(1)[5]==2


def test_binary_roundtrip_preserves_all_numeric_fields(tmp_path):
    e=NativeBrainEngine();e.add_cognit()
    state=[.3,.2,.7,.8,123,2,.4,.1,.09,31,.6,7]
    e.set_cognit_states([0],state);path=tmp_path/'numeric.bin';e.save_graph(str(path))
    loaded=NativeBrainEngine();loaded.load_graph(str(path))
    assert loaded.cognit_state_full([0])==pytest.approx(state)


def test_native_hybrid_brain_load_remains_native(tmp_path):
    from simulation import Simulation
    source=Simulation(77,Settings(object_count=0),backend='native');source.run(12)
    path=tmp_path/'native.sebrain';source.save_brain(path)
    from persistence import load_container
    sections=load_container(path,'brain',{'META','COGN','RELA','PATT','SPAT','BELS','LEAR','LANG','NBRN'})
    assert sections['RELA']['relations']==[] and sections['NBRN']['data']
    target=Simulation(78,Settings(object_count=0),backend='native');target.load_brain(path)
    assert target.core.backend_name=='native' and target.core.backend is not None
    assert target.core.backend.full_graph_sync_calls==0
    assert len(target.core.graph.nodes)==len(source.core.graph.nodes)
    assert target.core.graph.relation_count==source.core.graph.relation_count


def test_native_world_roundtrip_continues_deterministically(tmp_path):
    from simulation import Simulation
    settings=Settings(object_count=2);source=Simulation(91,settings,backend='native');source.run(15)
    path=tmp_path/'native.seworld';source.save_world(path);loaded=Simulation.load_world(path,settings,backend='native')
    assert loaded.world_time==source.world_time and loaded.event_sequence.value==source.event_sequence.value
    left=source.step();right=loaded.step()
    assert (left.action,left.action_result)==(right.action,right.action_result)
    assert source.world.to_dict()==loaded.world.to_dict()
    assert loaded.core.backend.full_graph_sync_calls==0


def test_refractory_activation_transmits_original_frontier_energy():
    from consciousness.graph import CognitiveGraph
    from consciousness.cognit import Cognit
    from consciousness.wave import ActivityWaveEngine
    graph=CognitiveGraph();e=NativeBrainEngine()
    for i,a in enumerate((1.,.8,0.)):
        graph.add_cognit(Cognit(i+1,activity=a));e.add_cognit(a)
    graph.nodes[2].refractory_ticks=1;e.set_refractory(1,1)
    for s,t in ((1,2),(2,3)):
        r,_=graph.connect(s,t);r.strength=.8;r.confidence=.8
        e.add_relation(s-1,t-1,1,0,.8,.8,0.)
    expected=ActivityWaveEngine(Settings()).propagate(graph,{1},5);actual=e.propagate([0],5)
    assert {x+1 for x in actual[0]}==set(expected.active_ids)
    assert actual[1]==pytest.approx(expected.energy)
    assert e.cognit_state([2])[0]==pytest.approx(graph.nodes[3].activity)


@pytest.mark.parametrize('cycles',[1,10,100,1000])
def test_lazy_homeostasis_matches_frozen_inactive_evolution(cycles):
    from consciousness.cognit import Cognit
    s=Settings();p=Cognit(1,activity=.7,utility=.8,activity_trace=.9,refractory_ticks=2)
    e=NativeBrainEngine();e.add_cognit();e.set_cognit_states([0],[p.activity,p.threshold,p.confidence,p.utility,0,p.refractory_ticks,p.homeostatic_threshold,p.activity_trace,p.target_activity,0,0,0])
    for _ in range(cycles):
        p.homeostatic_step(False,s)
        e.homeostatic_step([],s.homeostasis_trace_decay,s.homeostasis_learning_rate,s.threshold_min,s.threshold_max,s.cognit_activity_decay,.999)
    row=e.cognit_state_full([0])
    assert row[0]==pytest.approx(p.activity,abs=1e-6)
    assert row[3]==pytest.approx(p.utility,abs=2e-5)
    assert row[6]==pytest.approx(p.homeostatic_threshold,abs=2e-5)
    assert row[7]==pytest.approx(p.activity_trace,abs=2e-6)
    assert row[5]==p.refractory_ticks and row[9]==p.age
