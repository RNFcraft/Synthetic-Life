from config import Settings
from consciousness.core import SyntheticEntityCore
from consciousness.relation import RelationStatus,RelationType
from world.actions import ActionType
from consciousness.patterns import CognitPattern,PatternNode,PatternParticipantType,SensoryEventKind


def test_relation_knowledge_survives_evidence_clear_and_ablation()->None:
    core=SyntheticEntityCore(Settings());a=core.graph.add_cognit();b=core.graph.add_cognit();a.activity=1
    r,_=core.graph.connect(a.id,b.id,RelationType.SEQUENTIAL);r.strength=r.prediction_probability=.8;r.confidence=.9;r.status=RelationStatus.CONSOLIDATED
    core.transitions.clear_evidence();assert core.predict_from_relations({a.id})[b.id]>0.5
    core.relation_prediction_enabled=False;assert core.predict_from_relations({a.id})=={}


def test_self_action_relation_prediction()->None:
    core=SyntheticEntityCore(Settings());a=core.graph.add_cognit();b=core.graph.add_cognit();a.activity=1
    r,_=core.graph.connect(a.id,b.id,RelationType.SELF_ACTION,ActionType.MOVE_RIGHT.value);r.strength=r.prediction_probability=1;r.confidence=1
    assert core.predict_from_relations({a.id},ActionType.MOVE_RIGHT)[b.id]==1
    assert b.id not in core.predict_from_relations({a.id},ActionType.MOVE_LEFT)


def test_relation_contradiction_and_consolidation()->None:
    core=SyntheticEntityCore(Settings());a=core.graph.add_cognit();b=core.graph.add_cognit();r,_=core.graph.connect(a.id,b.id);r.confidence=.8;r.status=RelationStatus.CONSOLIDATED
    core.previous_active={a.id};core._update_relation_outcomes(1,set());assert r.confidence<.8 and r.contradiction_evidence>0


def test_pattern_selectivity_and_composite_predictive_contribution()->None:
    key=(0,0,"occupied",1,SensoryEventKind.OCCUPIED_PRESENT.value);other=(1,0,"state",1,SensoryEventKind.STATE_CHANGED.value)
    pattern=CognitPattern((key,));pattern.observe_selectivity(1.0,0.0);assert pattern.match_selectivity==1.0
    core=SyntheticEntityCore(Settings());primitive=core.graph.add_cognit();composite=core.graph.add_cognit();composite.pattern=CognitPattern((),nodes=(PatternNode(PatternParticipantType.COGNIT,primitive.id),))
    # Counterfactual contribution is signed error_without - error_with.
    core.previous_active={composite.id};core.state.predictions={primitive.id:1.0};core.predictions_without_composites={primitive.id:0.0};core._prediction_error({primitive.id})
    assert composite.predictive_contribution>0
