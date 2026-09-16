import hashlib,json,math,os,subprocess,sys
from dataclasses import replace
import pytest

from config import Settings
from consciousness.native_engine import EventScheduler,RuntimeEventType
from consciousness._native_brain import MicroPolarity,NeurodynamicSubstrate
from consciousness.core import ContinuousCognitionFrontier,SyntheticEntityCore
from consciousness.relation import RelationStatus,RelationType
from simulation.continuous import ContinuousRuntime
from simulation.long_life import LongLifeDiagnostics,validate_long_life_state
from world import ActionType
from world.perception import BodySense,SensoryFrame


SETTINGS=Settings(sensory_neural_enabled=True,neural_behavioral_participation=True)


def _runtime(seed=6601):return ContinuousRuntime(seed,SETTINGS)


def _stable_runtime(seed=6602):
    runtime=_runtime(seed);runtime.ACTION_DURATION=.95;body=runtime.simulation.world.body
    candidates=[(body.x+dx,body.y+dy) for radius in (1,2) for dx,dy in ((radius,0),(0,radius),(-radius,0),(0,-radius),(radius,radius),(-radius,-radius))]
    positions=[p for p in candidates if runtime.simulation.world.grid.contains(*p)][:4];runtime.simulation.world.initialize_controlled_objects(positions)
    runtime.simulation.core.available_actions=(ActionType.IDLE,);return runtime


def _causal(runtime):
    core=runtime.simulation.core;engine=core.backend.engine;frontier=core.continuous_frontier
    state=runtime.simulation.snapshot_data();graph=state.pop("cognitive_graph");semantic=([{"id":n["id"],"pattern":n["pattern"],"kind":n["kind"]} for n in graph["nodes"]],graph["relations"])
    return (runtime.scheduler_state(),state,semantic,engine.neurodynamic_substrate().snapshot(),engine.assembly_cognit_mapping(),engine.assembly_bridge_state(),None if frontier is None else runtime._frontier_state()["cognition"],runtime.actions_completed,runtime.scheduler_events_processed,runtime.peak_scheduler_queue)


def test_medium_production_soak_is_bounded_and_numerically_sane():
    runtime=_runtime();diagnostics=LongLifeDiagnostics();samples=[]
    for until in (10.,20.,30.,40.,50.):runtime.run_until(until);validate_long_life_state(runtime);samples.append(diagnostics.sample(runtime))
    final=samples[-1];settings=runtime.simulation.settings
    assert final.actions_completed>=300 and final.scheduler_events_processed>final.actions_completed
    assert final.peak_scheduler_queue<=8 and final.scheduler_queue<=4 and final.planner_pending_work<=4
    assert final.cognits_peak<=settings.max_cognits and final.relations_peak<=settings.max_relations
    assert final.bridge_log_peak<=256 and final.composite_candidates<=settings.max_composite_candidates
    assert final.full_graph_sync_calls==0 and runtime.simulation.event_sequence.value==runtime.actions_completed
    assert all(sample.cognits_current<=settings.max_cognits and sample.relations_current<=settings.max_relations for sample in samples)


def test_recurring_world_reuses_assembly_and_cognit_without_scheduler_growth():
    runtime=_stable_runtime();runtime.run_until(8.);engine=runtime.simulation.core.backend.engine;first=(engine.neurodynamic_substrate().assemblies(),engine.assembly_cognit_mapping())
    runtime.run_until(24.);second=(engine.neurodynamic_substrate().assemblies(),engine.assembly_cognit_mapping())
    assert len(first[0])==len(second[0])==1 and first[1]==second[1] and len(second[1])==1
    assert runtime.scheduler.size<=3 and runtime.peak_scheduler_queue<=4


def test_long_host_batching_and_runtime_counters_are_exact():
    left,right=_runtime(6603),_runtime(6603);left.run_until(20.)
    for until in (.1,.37,1.9,5.02,9.999,10.,math.nextafter(10.,math.inf),13.7,20.):right.run_until(until)
    assert _causal(left)==_causal(right)


def test_three_successive_snapshot_restores_have_no_drift(tmp_path):
    uninterrupted=_runtime(6604);cycled=_runtime(6604)
    for index,until in enumerate((2.,4.,6.)):
        uninterrupted.run_until(until);cycled.run_until(until);path=tmp_path/f"cycle-{index}.seworld";cycled.save_world(path);cycled=ContinuousRuntime.load_world(path)
    assert _causal(uninterrupted)==_causal(cycled) and cycled.simulation.core.backend.full_graph_sync_calls==0
    left=uninterrupted.simulation.core.backend.engine;right=cycled.simulation.core.backend.engine
    assert left.cognit_count==right.cognit_count
    assert left.cognit_state_full(range(left.cognit_count))==pytest.approx(right.cognit_state_full(range(right.cognit_count)),abs=2e-15,rel=0)


def test_snapshot_with_open_deliberation_and_before_action_completion(tmp_path):
    runtime=_runtime(6605);sensory=runtime.scheduler.pop_ready(0.)[0];runtime._process(sensory)
    wake=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.COGNITION_WAKE)
    for event in runtime.scheduler.pop_ready(wake.time):runtime._process(event)
    path=tmp_path/"open.seworld";runtime.save_world(path);restored=ContinuousRuntime.load_world(path)
    assert _causal(runtime)==_causal(restored)
    for item in (runtime,restored):item.run_to_quiescence()
    assert _causal(runtime)==_causal(restored)
    pending=[e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE];assert len(pending)==1
    path=tmp_path/"before-action.seworld";runtime.save_world(path);again=ContinuousRuntime.load_world(path);runtime.run_until(pending[0].time);again.run_until(pending[0].time)
    assert _causal(runtime)==_causal(again)


def test_silence_has_no_hidden_behavior_or_neural_work():
    runtime=_runtime(6606);runtime.run_until(.2);runtime.scheduler=EventScheduler();neural=runtime.simulation.core.backend.engine.neurodynamic_substrate();before=(runtime.scheduler_events_processed,runtime.cognition_wakes,runtime.cognition_continuations,runtime.simulation.core.planner.total_cycles,neural.telemetry(),runtime.simulation.core.backend.ffi_calls)
    runtime.run_until(100_000.);assert before==(runtime.scheduler_events_processed,runtime.cognition_wakes,runtime.cognition_continuations,runtime.simulation.core.planner.total_cycles,neural.telemetry(),runtime.simulation.core.backend.ffi_calls)


def test_long_run_pythonhashseed_digest_is_deterministic():
    code='''import hashlib,json\nfrom config import Settings\nfrom simulation.continuous import ContinuousRuntime\nr=ContinuousRuntime(6607,Settings(sensory_neural_enabled=True,neural_behavioral_participation=True));r.run_until(12.)\ndata=[r.scheduler_state(),r.simulation.snapshot_data(),r.simulation.core.backend.engine.assembly_cognit_mapping(),r.actions_completed,r.scheduler_events_processed,r.peak_scheduler_queue]\nprint(hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest())'''
    outputs=[]
    for seed in ("1","77"):
        env=os.environ.copy();env["PYTHONHASHSEED"]=seed;outputs.append(subprocess.check_output([sys.executable,"-c",code],env=env,text=True).strip())
    assert outputs[0]==outputs[1]


def test_diagnostics_are_json_struct_friendly_and_validator_rejects_corruption():
    runtime=_runtime(6608);runtime.run_until(1.);sample=LongLifeDiagnostics().sample(runtime);assert json.loads(json.dumps(sample.to_dict()))["simulated_time"]==1.
    substrate=runtime.simulation.core.backend.engine.neurodynamic_substrate();snapshot=substrate.snapshot();snapshot["potential"][0]=float("nan")
    with pytest.raises(ValueError):substrate.restore(snapshot)


def test_lifecycle_torture_deletes_and_rebirths_neural_cognit_without_stale_ids():
    runtime=_stable_runtime(6609);runtime.run_until(8.);core=runtime.simulation.core;engine=core.backend.engine;old=engine.assembly_cognit_mapping()[0][1]+1
    core.settings=replace(core.settings,retention_threshold=2.,retention_grace_ticks=0,lifecycle_batch_size=1);core.deletion_candidates.appendleft(old);core._prune(999)
    assert old not in core.graph.nodes and engine.assembly_cognit_mapping()==[]
    assert all(old not in values for values in (core.previous_active,core.previous_context,core.dirty_cognits,core.continuous_frontier.current,core.continuous_frontier.session.working,core.continuous_frontier.session.last_recalled))
    assert all(relation.source_id!=old and relation.target_id!=old for row in core.graph.adjacency.values() for relation in row.values())
    runtime.run_until(14.);mapping=engine.assembly_cognit_mapping();assert len(mapping)==1 and mapping[0][1]+1>old
    validate_long_life_state(runtime);assert core.backend.full_graph_sync_calls==0


def test_repeated_identical_context_merge_does_not_restart_planner():
    runtime=_runtime(6610);runtime.run_until(.2);core=runtime.simulation.core;session=core.continuous_frontier.session;active=set(session.working);revision=session.working_revision;pending=list(session.pending_work)
    for _ in range(1_000):assert not core.planner.merge_context(core,session,active)
    assert session.working_revision==revision and list(session.pending_work)==pending and len(session.pending_keys)==len(session.pending_work)


def test_stable_world_snapshot_growth_is_bounded_by_retained_evidence(tmp_path):
    runtime=_stable_runtime(6611);sizes=[];counts=[]
    for until in (8.,16.,24.):
        runtime.run_until(until);path=tmp_path/f"stable-{int(until)}.seworld";runtime.save_world(path);sizes.append(path.stat().st_size);counts.append((len(runtime.simulation.core.graph.nodes),runtime.simulation.core.graph.relation_count))
    assert sizes[-1]<sizes[0]*1.10 and sizes[2]-sizes[1]<=sizes[1]-sizes[0]
    assert all(b[0]-a[0]<=1 and b[1]-a[1]<=1 for a,b in zip(counts,counts[1:]))


def test_continuous_relation_lifecycle_uses_observation_tick_domain():
    settings=replace(Settings(),relation_max_idle=10,relation_death_threshold=.9,relation_confidence_decay=.9,lifecycle_batch_size=0);core=SyntheticEntityCore(settings)
    source,target=core.graph.add_cognit().id,core.graph.add_cognit().id;relation,_=core.graph.connect(source,target);relation.confidence=.1;relation.last_evidence_world_tick=100
    frame=SensoryFrame(192,4,(),BodySense(False,False,False,False,False,0.));core.continuous_frontier=ContinuousCognitionFrontier(1,1.,frame,set(),())
    core.continuous_maintenance(1.,1);assert core.graph.relation_count==0


def test_scheduler_peak_counts_same_time_batch_and_restore():
    scheduler=EventScheduler()
    for payload in range(50):scheduler.schedule(1.,RuntimeEventType.EXTERNAL_INPUT,payload)
    assert scheduler.peak_size==50
    events=scheduler.snapshot();scheduler.pop_ready(1.);scheduler.restore(1.,scheduler.next_id,[],50)
    assert len(events)==50 and scheduler.peak_size==50


def test_long_life_validator_respects_fixed_and_plastic_weight_contract():
    runtime=_runtime(6612);substrate=NeurodynamicSubstrate(weight_min=.2,weight_max=1.)
    a=substrate.add_micro_kappa();b=substrate.add_micro_kappa()
    substrate.add_micro_rho(a,b,2.,1.,MicroPolarity.EXCITATORY,False)
    runtime.simulation.core.backend.engine.neurodynamic_substrate().restore(substrate.snapshot())
    assert validate_long_life_state(runtime)
    for weight,plastic in ((2.,True),(-.1,False),(float("nan"),False),(float("inf"),False)):
        bad=substrate.snapshot();bad["weight"][0]=weight;bad["plasticity_enabled"][0]=plastic
        with pytest.raises((ValueError,AssertionError)):runtime.simulation.core.backend.engine.neurodynamic_substrate().restore(bad)


def test_repeated_identical_transition_reuses_relation_identity():
    runtime=ContinuousRuntime(6613,replace(Settings(),relation_provisional_support=1,relation_provisional_lift=0.));core=runtime.simulation.core
    source,target=core.graph.add_cognit().id,core.graph.add_cognit().id;engine=core.backend.engine
    for tick in range(1_000):
        engine.update_transition_evidence([source-1],ActionType.IDLE.value,[target-1])
        engine.materialize_current(core.backend.evidence_config,tick,[source-1],ActionType.IDLE.value,[target-1],16,16_384,.999)
    rows=[r for r in core.graph.adjacency[source].values() if r.target_id==target]
    assert len(rows)==2


def _evidence_engine(tick=1_000):
    from consciousness.native_engine import EvidenceConfig,NativeBrainEngine
    engine=NativeBrainEngine();engine.add_cognits(2)
    config=EvidenceConfig();config.minimum_support=1;config.minimum_lift=0.;config.confidence_k=4.
    engine.update_transition_evidence([0],ActionType.IDLE.value,[1])
    rows=engine.materialize_current(config,tick,[0],ActionType.IDLE.value,[1],16,16_384,.9)
    handle=next(h for h in engine.dirty_relation_state() if h[2]==2)
    return engine,config,rows,handle


def test_native_continuous_lifecycle_uses_evidence_ticks_not_seconds():
    engine,_,_,_= _evidence_engine()
    policy=(.95,.02,.05,.95,.9,.999)
    engine.begin_continuous_time(0.,*policy,.9);engine.begin_continuous_time(1_000.,*policy,.9)
    removed,kept=engine.lifecycle_step(1_050,100,.5,.9)
    assert (removed,kept)==(0,2)
    removed,kept=engine.lifecycle_step(1_101,100,.5,.9)
    assert removed==2 and kept==0 and engine.relation_count==0


def test_native_lifecycle_preserves_recent_or_effectively_confident_relation():
    recent,_,_,_=_evidence_engine();policy=(.95,.02,.05,.95,.9,.999)
    recent.begin_continuous_time(0.,*policy,.9);recent.begin_continuous_time(10_000.,*policy,.9)
    assert recent.lifecycle_step(1_050,100,.99,.9)==(0,2)
    useful,_,_,_=_evidence_engine();useful.begin_continuous_time(0.,*policy,1.);useful.begin_continuous_time(10_000.,*policy,1.)
    assert useful.lifecycle_step(1_101,100,.1,1.)==(0,2)


def test_materialization_apis_have_exact_self_action_statistical_parity():
    from consciousness.native_engine import EvidenceConfig,NativeBrainEngine
    config=EvidenceConfig();config.minimum_support=2;config.minimum_lift=0.;config.confidence_k=4.
    public,current=NativeBrainEngine(),NativeBrainEngine()
    for engine in (public,current):
        engine.add_cognits(3)
        for before,after in (([0],[1]),([0],[2]),([0],[1])):engine.update_transition_evidence(before,ActionType.IDLE.value,after)
    left=public.materialize_relations(config,3)
    right=[row for row in current.materialize_current(config,3,[0],ActionType.IDLE.value,[1],16,16_384,.999) if row[2]==ActionType.IDLE.value]
    assert left==right
    assert left==[(0,1,ActionType.IDLE.value,2,pytest.approx(2/3),pytest.approx(2/6),pytest.approx(1.))]


def test_repeated_materialization_does_not_duplicate_lifecycle_work():
    engine,config,_,_=_evidence_engine()
    for tick in range(1_001,2_001):engine.materialize_current(config,tick,[0],ActionType.IDLE.value,[1],16,16_384,.999)
    assert len(engine.dirty_relation_state())==2 and engine.lifecycle_step(2_001,10_000,1.,.999)==(0,2)


def test_snapshot_restore_across_relation_deletion_horizon_is_exact(tmp_path):
    settings=replace(SETTINGS,relation_max_idle=100,relation_death_threshold=.99)
    continuous=ContinuousRuntime(6614,settings);cycled=ContinuousRuntime(6614,settings)
    for runtime in (continuous,cycled):
        core=runtime.simulation.core;source=core.graph.add_cognit().id;target=core.graph.add_cognit().id
        core.backend.engine.add_relation(source-1,target-1,RelationType.ASSOCIATIVE.value,0,.1,.1,.1)
        runtime.run_until(10.)
    path=tmp_path/"before-relation-horizon.seworld";cycled.save_world(path);cycled=ContinuousRuntime.load_world(path,settings)
    continuous.run_until(20.);cycled.run_until(20.)
    left,right=_causal(continuous),_causal(cycled)
    assert left[:1]+left[2:]==right[:1]+right[2:]
    a,b=continuous.simulation.core.backend.engine,cycled.simulation.core.backend.engine
    assert a.cognit_state_full(range(a.cognit_count))==pytest.approx(b.cognit_state_full(range(b.cognit_count)),abs=2e-15,rel=0)
    assert continuous.simulation.core.backend.full_graph_sync_calls==cycled.simulation.core.backend.full_graph_sync_calls==0
