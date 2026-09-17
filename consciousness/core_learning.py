"""Transition evidence and Relation-learning responsibilities of the core."""
from .relation import RelationStatus, RelationType


class CoreLearningMixin:
    """Single implementation mixed into ``SyntheticEntityCore``.

    The mixin owns no state: it mutates the authoritative fields composed by the
    facade and preserves the original call and iteration order.
    """

    def _prediction_error(self,current:set[int])->None:
        predicted=self.state.predictions;universe=set(predicted)|current
        if not universe:self.state.prediction_error=self.settings.prediction_error_neutral;self.state.prediction_error_valid=False;return
        errors=[abs((1.0 if i in current else 0.0)-predicted.get(i,0.0)) for i in universe]
        self.state.prediction_error=sum(errors)/len(errors);self.state.prediction_error_valid=True
        valid=[node_id for node_id in universe if node_id in self.graph.nodes]
        if self.backend:
            contributions=self.backend.cognit_state_fields(valid,(10,));updates=[]
            for node_id in valid:
                correct=1-abs((1. if node_id in current else 0.)-predicted.get(node_id,0.));updates.append((node_id,10,.95*contributions[node_id][0]+.05*correct))
            self.backend.set_cognit_fields(updates)
        else:
            for node_id in valid:
                correct=1-abs((1. if node_id in current else 0.)-predicted.get(node_id,0.));node=self.graph.nodes[node_id]
                node.predictive_contribution=.95*node.predictive_contribution+.05*correct
        self.calibration.observe(predicted,current);self.state.brier_score=self.calibration.brier_score;self.state.ece=self.calibration.ece
        if self.predictions_without_composites:
            universe2=set(self.predictions_without_composites)|current
            error_without=sum(abs((1. if i in current else 0.)-self.predictions_without_composites.get(i,0.)) for i in universe2)/max(1,len(universe2))
            contribution=error_without-self.state.prediction_error
            for node_id in self.previous_active:
                node=self.graph.nodes.get(node_id)
                if node and node.pattern and node.pattern.nodes:node.predictive_contribution=.95*node.predictive_contribution+.05*contribution

    def _materialize_relations(self,tick:int,current:set[int])->None:
        created=0;relation_count=self.graph.relation_count
        candidates={(s,t) for s in self.previous_active for t in current if s!=t}
        for source,target in sorted(candidates):
            support,conditional,_,lift=self.transitions.metrics(source,target)
            self.relation_candidates+=1;self.candidate_supports.append(support);self.candidate_lifts.append(lift)
            if support<self.settings.relation_provisional_support or lift<self.settings.relation_provisional_lift:continue
            if (target,RelationType.SEQUENTIAL,None) not in self.graph.adjacency.get(source,{}) and created>=max(1,self.settings.max_new_relations_per_tick//2):continue
            if relation_count>=self.settings.max_relations and (target,RelationType.SEQUENTIAL,None) not in self.graph.adjacency.get(source,{}):continue
            relation,is_new=self.graph.connect(source,target,RelationType.SEQUENTIAL)
            if is_new:
                if created>=self.settings.max_new_relations_per_tick or relation_count>=self.settings.max_relations:self.graph.remove_relation(source,target);continue
                created+=1;relation_count+=1;self.relations_materialized+=1;self.events.append(f"RELATION_CREATED κ{source} -> κ{target} SEQUENTIAL")
            relation.materialize_decay(tick,self.settings.relation_confidence_decay);relation.support=support;relation.lift=lift
            relation.strength=max(0.0,min(1.0,conditional));relation.prediction_probability=relation.strength
            relation.confidence=support/(support+self.settings.relation_confidence_k);relation.uncertainty=1-relation.confidence;relation.last_evidence_world_tick=tick
            if support>=self.settings.relation_consolidated_support and relation.confidence>=self.settings.relation_consolidated_confidence:relation.status=RelationStatus.CONSOLIDATED
        # Materialize action-conditioned evidence only where it has repeated support.
        if self.previous_action is not None:
            priority=lambda i:(0 if self.graph.nodes.get(i) and self.graph.nodes[i].kind=="BOUND_RELATION" else 1,i)
            for source in sorted(self.previous_active,key=priority):
                for target in sorted(current,key=priority):
                    probability,support=self.transitions.action_probability(source,self.previous_action,target)
                    _,conditional,_,_=self.transitions.metrics(source,target)
                    lift=probability/max(conditional,1e-9)
                    self.relation_candidates+=1;self.candidate_supports.append(support);self.candidate_lifts.append(lift)
                    if support>=self.settings.relation_provisional_support and lift>=self.settings.relation_provisional_lift and source!=target:
                        key=(target,RelationType.SELF_ACTION,self.previous_action.value)
                        if relation_count>=self.settings.max_relations and key not in self.graph.adjacency.get(source,{}):continue
                        relation,is_new=self.graph.connect(source,target,RelationType.SELF_ACTION,self.previous_action.value)
                        if is_new and (created>=self.settings.max_new_relations_per_tick or relation_count>=self.settings.max_relations):
                            self.graph.remove_relation(source,target,RelationType.SELF_ACTION,self.previous_action.value);continue
                        if is_new:created+=1;relation_count+=1
                        if is_new:self.relations_materialized+=1;self.events.append(f"RELATION_CREATED κ{source} -> κ{target} SELF_ACTION")
                        relation.strength=probability;relation.prediction_probability=probability;relation.support=support;relation.lift=lift
                        relation.confidence=support/(support+self.settings.relation_confidence_k);relation.uncertainty=1-relation.confidence;relation.last_evidence_world_tick=tick
                        if support>=self.settings.relation_consolidated_support and relation.confidence>=self.settings.relation_consolidated_confidence:relation.status=RelationStatus.CONSOLIDATED

    def _update_relation_outcomes(self,tick:int,current:set[int])->None:
        if self.backend:
            self.backend.update_outcomes(self.previous_active,current,self.previous_action,tick)
            return
        for source in self.previous_active:
            for relation in self.graph.outgoing(source):
                if relation.relation_type is RelationType.SELF_ACTION and (self.previous_action is None or relation.context_id!=self.previous_action.value):continue
                confirmed=relation.target_id in current
                relation.update_outcome(confirmed,self.settings.relation_confirmation_rate,self.settings.relation_contradiction_rate)
                relation.usefulness=max(0.,min(1.,relation.usefulness+self.settings.relation_utility_rate*((1. if confirmed else 0.)-relation.strength)))
                relation.last_evidence_world_tick=tick
                if relation.status is RelationStatus.CONSOLIDATED and relation.confidence<self.settings.relation_consolidated_confidence*.6:relation.status=RelationStatus.PROVISIONAL


__all__ = ["CoreLearningMixin"]
