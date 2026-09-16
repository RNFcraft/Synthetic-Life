from dataclasses import replace
from pathlib import Path

from config import Settings
from consciousness.core import SyntheticEntityCore
from consciousness.planning import CognitiveWorkKind
from consciousness.relation import RelationStatus,RelationType
from consciousness.state import Goal
from simulation.continuous import ContinuousRuntime
from consciousness.native_engine import EventScheduler,RuntimeEvent,RuntimeEventType
from world import ActionType


def _ordinary_context(participates=True):
    core=SyntheticEntityCore(replace(Settings(),neural_behavioral_participation=participates),"native")
    source=core.graph.add_cognit();source.kind="NEURAL_ASSEMBLY";source.threshold=source.homeostatic_threshold=.01
    downstream=core.graph.add_cognit();downstream.threshold=downstream.homeostatic_threshold=.01
    target=core.graph.add_cognit();target.novelty=1.
    relation,_=core.graph.connect(source.id,downstream.id);relation.strength=relation.confidence=relation.prediction_probability=1.;relation.status=RelationStatus.CONSOLIDATED
    action_relation,_=core.graph.connect(downstream.id,target.id,RelationType.SELF_ACTION,ActionType.MOVE_LEFT.value);action_relation.strength=action_relation.confidence=action_relation.prediction_probability=1.;action_relation.status=RelationStatus.CONSOLIDATED
    core.backend.receive(source.id,1.,1,core.settings)
    return core,source.id,downstream.id,target.id


def _world_runtime(participates=True):
    runtime=ContinuousRuntime(6506,Settings(sensory_neural_enabled=True,neural_behavioral_participation=participates));runtime.ACTION_DURATION=.95
    body=runtime.simulation.world.body
    runtime.simulation.world.initialize_controlled_objects([(body.x+dx,body.y+dy) for dx,dy in ((1,0),(0,1),(-1,0),(0,-1))])
    runtime.simulation.core.available_actions=(ActionType.IDLE,);return runtime


def _trained_world_runtime(participates=True):
    runtime=_world_runtime(participates);runtime.run_until(4.)
    mapping=runtime.simulation.core.backend.engine.assembly_cognit_mapping();assert len(mapping)==1
    source=mapping[0][1]+1;target=runtime.simulation.core.graph.add_cognit();target.novelty=1.
    relation,_=runtime.simulation.core.graph.connect(source,target.id,RelationType.SELF_ACTION,ActionType.MOVE_LEFT.value)
    relation.strength=relation.confidence=relation.prediction_probability=1.;relation.status=RelationStatus.CONSOLIDATED
    runtime.simulation.core.state.goal=Goal(999,(target.id,),1.,1.,1.);runtime.simulation.core.available_actions=tuple(ActionType)
    return runtime,source,target.id


def _open_world_recognition():
    runtime,source,target=_trained_world_runtime(True);runtime.run_until(5.65)
    completion=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE)
    for event in runtime.scheduler.pop_ready(completion.time):runtime._process(event)
    sensory=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.SENSORY_CHANGE)
    runtime._process(runtime.scheduler.pop_ready(sensory.time)[0]);generation=runtime.cognition_generation
    kept=[e for e in runtime.scheduler.snapshot() if e.type!=RuntimeEventType.COGNITION_WAKE];runtime.scheduler.restore(runtime.world_time,runtime.scheduler.next_id,kept)
    runtime._process(RuntimeEvent(runtime.world_time,90_001,RuntimeEventType.COGNITION_WAKE,generation))
    continuation=next(e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.COGNITION_CONTINUE);runtime._process(runtime.scheduler.pop_ready(continuation.time)[0])
    kept=[e for e in runtime.scheduler.snapshot() if e.type not in {RuntimeEventType.COGNITION_CONTINUE,RuntimeEventType.MAINTENANCE}]
    runtime.scheduler.restore(runtime.world_time,runtime.scheduler.next_id,kept);old_revision=runtime.simulation.core.continuous_frontier.session.working_revision
    runtime.run_until(5.71);frontier=runtime.simulation.core.continuous_frontier
    assert frontier.phase=="DELIBERATING" and source in frontier.current and source in frontier.session.working
    assert frontier.session.working_revision>old_revision and frontier.session.candidate is None
    assert [work.kind for work in frontier.session.pending_work]==[CognitiveWorkKind.PROPAGATE]
    return runtime,source,target


def test_open_frontier_merge_uses_normal_relation_and_invalidates_stale_plan():
    core,source,downstream,_=_ordinary_context();session=core.planner.begin_continuous(core,set(),1)
    session.candidate=object();session.quiescent=True
    wave=core._propagate({source},2)
    assert downstream in wave.active_ids and core.planner.merge_context(core,session,set(wave.active_ids))
    assert {source,downstream}<=session.working and session.candidate is None and not session.quiescent
    assert [work.kind for work in session.pending_work]==[CognitiveWorkKind.PROPAGATE]
    core.graph.remove_relation(source,downstream)
    core.backend.receive(source,1.,3,core.settings)
    assert downstream not in core._propagate({source},3).active_ids


def test_behavioral_ablation_changes_existing_planner_prediction_without_changing_graph():
    core,source,downstream,target=_ordinary_context()
    core.backend.receive(downstream,1.,2,core.settings)
    core.state.goal=Goal(1,(target,),1.,1.,1.)
    with_neural={source,downstream};without_neural=set()
    enabled=core._imagine(with_neural);ablated=core._imagine(without_neural)
    assert enabled[ActionType.MOVE_LEFT].probabilities.get(target,0)>0
    assert ablated[ActionType.MOVE_LEFT].probabilities.get(target,0)==0
    assert enabled[ActionType.MOVE_LEFT].score!=ablated[ActionType.MOVE_LEFT].score
    enabled_plan=core.planner._search(core,with_neural,1,initial_predictions={a:f.probabilities for a,f in enabled.items()})
    ablated_plan=core.planner._search(core,without_neural,1,initial_predictions={a:f.probabilities for a,f in ablated.items()})
    assert enabled_plan.actions[0] is ActionType.MOVE_LEFT and ablated_plan.actions!=enabled_plan.actions


def test_real_world_neural_cognit_reaches_planner_and_changes_chosen_action_under_ablation():
    enabled,source,target=_trained_world_runtime(True);ablated,other_source,other_target=_trained_world_runtime(False)
    assert (source,target)==(other_source,other_target)
    assert enabled.simulation.snapshot_data()["world"]==ablated.simulation.snapshot_data()["world"]
    assert enabled.simulation.core.backend.engine.assembly_cognit_mapping()==ablated.simulation.core.backend.engine.assembly_cognit_mapping()
    enabled.run_until(6.);ablated.run_until(6.)
    left,right=enabled.simulation.core.trace.entries[-1],ablated.simulation.core.trace.entries[-1]
    assert source in left.signature and source not in right.signature
    assert left.action is ActionType.MOVE_LEFT and right.action is not left.action
    assert enabled.simulation.core.state.action_scores[ActionType.MOVE_LEFT]!=ablated.simulation.core.state.action_scores[ActionType.MOVE_LEFT]
    assert enabled.simulation.core.state.predictions.get(target,0)>ablated.simulation.core.state.predictions.get(target,0)


def test_host_batching_preserves_neural_planner_actions_and_world_state():
    left,right=_world_runtime(),_world_runtime();left.run_until(10.);right.run_until(2.);right.run_until(5.);right.run_until(10.)
    le,re=left.simulation.core.backend.engine,right.simulation.core.backend.engine
    assert le.neurodynamic_substrate().snapshot()==re.neurodynamic_substrate().snapshot()
    assert le.neurodynamic_substrate().assemblies()==re.neurodynamic_substrate().assemblies() and le.assembly_cognit_mapping()==re.assembly_cognit_mapping() and le.assembly_bridge_state()==re.assembly_bridge_state()
    assert left.scheduler_state()==right.scheduler_state() and left.simulation.snapshot_data()==right.simulation.snapshot_data()
    assert [x.action for x in left.simulation.core.trace.entries]==[x.action for x in right.simulation.core.trace.entries]


def test_silent_interval_adds_no_behavioral_work():
    runtime=_world_runtime();runtime.run_until(.2);runtime.scheduler=EventScheduler();before=(runtime.cognition_wakes,runtime.cognition_continuations,runtime.simulation.core.planner.total_cycles,runtime.simulation.core.cognitive_tick)
    runtime.run_until(100.);assert before==(runtime.cognition_wakes,runtime.cognition_continuations,runtime.simulation.core.planner.total_cycles,runtime.simulation.core.cognitive_tick)


def test_real_scheduler_bridge_refines_open_frontier_and_commits_once():
    runtime,source,_=_open_world_recognition();generation=runtime.cognition_generation
    runtime.scheduler.schedule(runtime.world_time,RuntimeEventType.COGNITION_CONTINUE,generation);runtime.run_to_quiescence()
    frontier=runtime.simulation.core.continuous_frontier;pending=[e for e in runtime.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE]
    assert frontier.committed and source in frontier.session.working and len(pending)==1
    before=runtime.actions_completed;runtime.run_until(pending[0].time)
    assert runtime.actions_completed==before+1


def test_snapshot_after_real_neural_merge_before_commit_is_exact(tmp_path):
    original,source,_=_open_world_recognition();path=tmp_path/"neural-before-commit.seworld";original.save_world(path);restored=ContinuousRuntime.load_world(path);restored.ACTION_DURATION=original.ACTION_DURATION
    def frontier_state(runtime):
        f=runtime.simulation.core.continuous_frontier;s=f.session
        return (f.current,s.working,s.working_revision,[(w.kind,w.key,w.payload) for w in s.pending_work],s.candidate)
    assert frontier_state(original)==frontier_state(restored)
    assert original.simulation.core.backend.engine.neurodynamic_substrate().snapshot()==restored.simulation.core.backend.engine.neurodynamic_substrate().snapshot()
    for runtime in (original,restored):runtime.scheduler.schedule(runtime.world_time,RuntimeEventType.COGNITION_CONTINUE,runtime.cognition_generation);runtime.run_to_quiescence()
    assert frontier_state(original)==frontier_state(restored)
    assert original.scheduler_state()==restored.scheduler_state()
    pending=[e for e in original.scheduler.snapshot() if e.type==RuntimeEventType.WORLD_ACTION_COMPLETE];assert len(pending)==1
    for runtime in (original,restored):runtime.run_until(pending[0].time)
    assert original.actions_completed==restored.actions_completed and original.simulation.last_action==restored.simulation.last_action
    assert original.simulation.world.to_dict()==restored.simulation.world.to_dict()


def test_deleted_cognit_is_removed_from_all_behavioral_frontiers():
    core,source,_,_=_ordinary_context();core.previous_active={source};core.previous_context=frozenset({source});core.dirty_cognits={source}
    core.continuous_frontier=type("F",(),{})();f=core.continuous_frontier;f.current={source};f.session=core.planner.begin_continuous(core,{source},1)
    core.settings=replace(core.settings,retention_threshold=2.,retention_grace_ticks=0,lifecycle_batch_size=len(core.graph.nodes));core.deletion_candidates.appendleft(source);core._prune(1)
    assert all(source not in values for values in (core.graph.nodes,core.previous_active,core.previous_context,core.dirty_cognits,f.current,f.session.working))


def test_ablation_flag_round_trips_with_pending_world(tmp_path):
    settings=replace(Settings(),sensory_neural_enabled=True,neural_behavioral_participation=False)
    runtime=ContinuousRuntime(6505,settings);path=tmp_path/"ablation.seworld";runtime.save_world(path)
    restored=ContinuousRuntime.load_world(path)
    assert restored.simulation.settings.neural_behavioral_participation is False
    assert restored.scheduler_state()==runtime.scheduler_state()


def test_neural_layers_contain_no_action_policy_tokens():
    root=Path(__file__).parents[1]
    paths=[root/"consciousness"/"neural_sensory.py",root/"cpp"/"src"/"neurodynamic_substrate.cpp",root/"cpp"/"include"/"se"/"neurodynamic_substrate.hpp"]
    forbidden=("ActionType","MOVE_","GRAB_","INTERACT_","reward label","goal target")
    for path in paths:
        text=path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden)
