from dataclasses import replace
from pathlib import Path

from config import Settings
from consciousness.core import SyntheticEntityCore
from consciousness.planning import CognitiveWorkKind
from consciousness.relation import RelationStatus,RelationType
from consciousness.state import Goal
from simulation.continuous import ContinuousRuntime
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
