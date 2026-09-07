import pytest
import random
from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.cognit import Cognit
from consciousness.native_engine import NativeBrainEngine,EvidenceConfig
from consciousness.relation import RelationType
from consciousness.wave import ActivityWaveEngine
from simulation import Simulation
from world import Action,ActionType

def as_dict(rows):return {target:value for target,value in rows}

def test_native_prediction_matches_nontrivial_python_oracle()->None:
    core=SyntheticEntityCore(Settings());native=NativeBrainEngine()
    activities=(.4,.8,0.,0.)
    for activity in activities:core.graph.add_cognit(Cognit(core.graph.next_id,activity=activity));native.add_cognit(activity)
    cases=((1,4,RelationType.SEQUENTIAL,0,.5,.6,0.),(2,4,RelationType.ASSOCIATIVE,0,.9,.5,.25),(1,3,RelationType.SELF_ACTION,ActionType.MOVE_UP.value,.9,.5,.7),(2,3,RelationType.SELF_ACTION,ActionType.MOVE_DOWN.value,.8,.4,0.))
    for source,target,kind,action,strength,confidence,probability in cases:
        rho,_=core.graph.connect(source,target,kind,action or None);rho.strength=strength;rho.confidence=confidence;rho.prediction_probability=probability
        native.add_relation(source-1,target-1,kind.value,action,strength,confidence,probability)
    for action in (ActionType.MOVE_UP,ActionType.MOVE_DOWN,ActionType.IDLE):
        expected=core.predict_from_relations({1,2},action);actual={k+1:v for k,v in as_dict(native.predict([0,1],action.value)).items()}
        assert actual.keys()==expected.keys()
        for target,value in expected.items():assert actual[target]==pytest.approx(value,abs=1e-6)
    actions=list(ActionType);batch=native.predict_actions_batch([0,1],[a.value for a in actions])
    assert len(batch)==len(actions)
    for action,rows in zip(actions,batch):
        expected=core.predict_from_relations({1,2},action);actual={k+1:v for k,v in as_dict(rows).items()};assert actual==pytest.approx(expected,abs=1e-6)

def test_native_causal_materialization_matches_oracle_after_evidence_clear()->None:
    settings=Settings(object_count=0,relation_provisional_support=3,relation_provisional_lift=1.)
    sim=Simulation(52,settings);world=sim.world;core=sim.core;native=NativeBrainEngine()
    core.graph.add_cognit(Cognit(1,activity=1.));core.graph.add_cognit(Cognit(2));native.add_cognit(1.);native.add_cognit()
    for trial in range(4):
        world.body.x,world.body.y=5,5;world.initialize_controlled_objects([(5,2),(5,4)]);before=abs(world.objects[0].y-world.objects[1].y);result=world.apply_action(Action(ActionType.MOVE_UP));after=abs(world.objects[0].y-world.objects[1].y)
        assert result.name=="SUCCESS" and (before,after)==(2,1)
        core.transitions.observe({1},ActionType.MOVE_UP,{2});native.update_transition_evidence([0],ActionType.MOVE_UP.value,[1])
    core.previous_active={1};core.previous_action=ActionType.MOVE_UP;core._materialize_relations(0,{2})
    native_config=EvidenceConfig();native_config.minimum_support=3;native_config.minimum_lift=1.;native_config.confidence_k=settings.relation_confidence_k
    rows=native.materialize_relations(native_config,0);python_rho=next(r for r in core.graph.outgoing(1) if r.relation_type is RelationType.SELF_ACTION)
    native_rho=next(r for r in rows if r[0:3]==(0,1,ActionType.MOVE_UP.value))
    assert native_rho[3]==python_rho.support==4 and native_rho[4]==pytest.approx(python_rho.prediction_probability) and native_rho[5]==pytest.approx(python_rho.confidence)
    core.transitions.clear_evidence();native.clear_transition_evidence()
    assert as_dict(native.predict([0],ActionType.MOVE_UP.value))[1]==pytest.approx(core.predict_from_relations({1},ActionType.MOVE_UP)[2],abs=1e-6)

def test_native_hot_scratch_capacity_is_reused()->None:
    native=NativeBrainEngine();[native.add_cognit(1. if i<2 else 0.) for i in range(16)]
    for i in range(15):native.add_relation(i,i+1,RelationType.SEQUENTIAL.value,0,.8,.8,.7)
    native.propagate([0,1],1);native.predict_actions_batch([0,1],[a.value for a in ActionType]);reserved=native.reserved_bytes
    for tick in range(2,50):native.propagate([0,1],tick);native.predict_actions_batch([0,1],[ActionType.MOVE_UP.value,ActionType.MOVE_DOWN.value])
    assert native.reserved_bytes==reserved

@pytest.mark.parametrize("case",("excitatory","inhibitory","mixed","refractory","below_threshold","multi_source","cycle"))
def test_native_wave_matches_python_semantics(case)->None:
    settings=Settings();core=SyntheticEntityCore(settings);native=NativeBrainEngine();count=3 if case in {"mixed","multi_source","cycle"} else 2
    initial=[1.,1.,0.] if count==3 else [1.,0.];thresholds=[.25]*count
    if case=="inhibitory":initial[1]=.8
    if case=="below_threshold":thresholds[1]=.9
    for i in range(count):core.graph.add_cognit(Cognit(i+1,activity=initial[i],threshold=thresholds[i],homeostatic_threshold=thresholds[i]));native.add_cognit(initial[i],thresholds[i],.5)
    edges=[]
    if case=="inhibitory":edges=[(0,1,RelationType.INHIBITORY)]
    elif case=="mixed":edges=[(0,2,RelationType.ASSOCIATIVE),(1,2,RelationType.INHIBITORY)]
    elif case=="multi_source":edges=[(0,2,RelationType.ASSOCIATIVE),(1,2,RelationType.ASSOCIATIVE)]
    elif case=="cycle":edges=[(0,1,RelationType.ASSOCIATIVE),(1,2,RelationType.ASSOCIATIVE),(2,0,RelationType.ASSOCIATIVE)]
    else:edges=[(0,1,RelationType.ASSOCIATIVE)]
    for source,target,kind in edges:
        rho,_=core.graph.connect(source+1,target+1,kind);rho.strength=.8;rho.confidence=.75
        native.add_relation(source,target,kind.value,0,.8,.75,0.)
    if case=="refractory":core.graph.nodes[2].refractory_ticks=1;native.set_refractory(1,1)
    seeds={1,2} if case in {"mixed","multi_source"} else {1};expected=ActivityWaveEngine(settings).propagate(core.graph,seeds,7);actual=native.propagate([i-1 for i in sorted(seeds)],7)
    assert [i+1 for i in actual[0]]==sorted(expected.active_ids);assert actual[1]==pytest.approx(expected.energy,abs=1e-6);assert actual[2]==expected.steps;assert actual[3]==pytest.approx(expected.transmitted_energy,abs=1e-6)
    state=native.cognit_state(list(range(count)))
    for i in range(count):
        node=core.graph.nodes[i+1];assert state[i*5]==pytest.approx(node.activity,abs=1e-6);assert state[i*5+2]==pytest.approx(node.confidence,abs=1e-6);assert state[i*5+3]==pytest.approx(node.utility,abs=1e-6);assert state[i*5+4]==pytest.approx(float(node.last_activated_cognitive_tick or 0))

def test_native_bounded_evidence_matches_python_before_and_after_eviction()->None:
    from consciousness.learning import TransitionModel
    window=4;python=TransitionModel(window);native=NativeBrainEngine(window)
    stream=[({1},ActionType.MOVE_UP,{2}),({1,3},ActionType.MOVE_DOWN,{2,4}),({3},ActionType.MOVE_UP,set()),({1},ActionType.MOVE_UP,{2}),({3},ActionType.MOVE_DOWN,{4}),({1},ActionType.MOVE_UP,{2})]
    for index,(before,action,after) in enumerate(stream):
        python.observe(before,action,after);native.update_transition_evidence([x-1 for x in before],action.value,[x-1 for x in after])
        if index in (2,5):
            expected=python.metrics(1,2);actual=native.transition_metrics(0,1,ActionType.MOVE_UP.value)
            assert actual[:4]==pytest.approx(expected,abs=1e-6);probability,trials=python.action_probability(1,ActionType.MOVE_UP,2);assert actual[4:]==pytest.approx((probability,trials),abs=1e-6)
    assert native.evidence_stats[2]==sum(len(a)*len(c) for a,_,c in stream)

def test_native_factorized_evidence_matches_random_bounded_oracle()->None:
    from consciousness.learning import TransitionModel
    rng=random.Random(5202);window=11;python=TransitionModel(window);native=NativeBrainEngine(window);actions=list(ActionType)
    for _ in range(80):
        before=set(rng.sample(range(1,13),rng.randrange(0,7)));after=set(rng.sample(range(1,13),rng.randrange(0,7)));action=rng.choice(actions)
        python.observe(before,action,after);native.update_transition_evidence([x-1 for x in before],action.value,[x-1 for x in after])
        for source in range(1,13):
            for target in range(1,13):
                expected=python.metrics(source,target);actual=native.transition_metrics(source-1,target-1,action.value)
                assert actual[:4]==pytest.approx(expected,abs=1e-6)
                probability,trials=python.action_probability(source,action,target)
                assert actual[4:]==pytest.approx((probability,trials),abs=1e-6)

def test_versioned_relation_handle_rejects_reused_slot()->None:
    native=NativeBrainEngine();[native.add_cognit() for _ in range(3)];old=native.add_relation(0,1,RelationType.ASSOCIATIVE.value)
    assert native.relation_handle_valid(old) and native.remove_relation(old) and not native.relation_handle_valid(old)
    new=native.add_relation(0,2,RelationType.SEQUENTIAL.value)
    assert new[:2]==old[:2] and new[2]!=old[2] and not native.remove_relation(old) and native.relation_handle_valid(new)

def test_native_dirty_lifecycle_prunes_without_graph_scan()->None:
    native=NativeBrainEngine();native.add_cognits(3);stale=native.add_relation(0,1,RelationType.SEQUENTIAL.value,0,.2,.01,.2);live=native.add_relation(0,2,RelationType.SEQUENTIAL.value,0,.8,.9,.8)
    removed,kept=native.lifecycle_step(100,10,.05,.99)
    assert (removed,kept)==(1,1) and not native.relation_handle_valid(stale) and native.relation_handle_valid(live)

def test_relation_record_layout_separates_provisional_and_consolidated_metadata()->None:
    assert NativeBrainEngine.consolidated_relation_bytes<=NativeBrainEngine.provisional_relation_bytes

def test_native_graph_binary_roundtrip_and_checksum(tmp_path)->None:
    path=tmp_path/"brain.sebrain";native=NativeBrainEngine();native.add_cognits(4)
    native.set_activity(0,.8);native.add_relation(0,2,RelationType.SEQUENTIAL.value,0,.7,.6,.55);native.add_relation(0,3,RelationType.SELF_ACTION.value,ActionType.MOVE_UP.value,.9,.8,.75)
    expected=native.predict([0],ActionType.MOVE_UP.value);native.save_graph(str(path));loaded=NativeBrainEngine();loaded.load_graph(str(path))
    assert loaded.cognit_count==4 and loaded.relation_count==2
    assert loaded.cognit_state([0])==pytest.approx(native.cognit_state([0]))
    assert loaded.predict([0],ActionType.MOVE_UP.value)==pytest.approx(expected)
    damaged=bytearray(path.read_bytes());damaged[-1]^=0xff;path.write_bytes(damaged)
    with pytest.raises(RuntimeError,match="checksum"):loaded.load_graph(str(path))

def test_real_core_runs_on_native_backend_without_ffi_per_cognit_calls()->None:
    settings=Settings(object_count=0,telemetry_history=1);python=Simulation(77,settings);native=Simulation(77,settings,backend="native")
    for _ in range(10):
        p=python.step();n=native.step()
        assert n.action==p.action
        assert native.core.last_wave.active_ids==python.core.last_wave.active_ids
    assert native.core.backend.engine.cognit_count==native.core.graph.next_id-1
