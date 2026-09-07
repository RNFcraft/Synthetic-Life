"""Semantic Python view over the single authoritative native numeric graph."""
from __future__ import annotations
from math import exp
from .relation import RelationStatus,RelationType


class NativeCognit:
    __slots__=("id","_backend","pattern","kind","novelty")
    def __init__(self,node_id,backend,template):
        self.id=node_id;self._backend=backend;self.pattern=template.pattern;self.kind=template.kind;self.novelty=template.novelty
    def _state(self):return self._backend.cognit_state_one(self.id)
    def _set(self,index,value):self._backend.set_cognit_field(self.id,index,value)
    activity=property(lambda s:s._backend.cognit_field(s.id,0),lambda s,v:s._set(0,v))
    threshold=property(lambda s:s._backend.cognit_field(s.id,1),lambda s,v:s._set(1,v))
    confidence=property(lambda s:s._backend.cognit_field(s.id,2),lambda s,v:s._set(2,v))
    utility=property(lambda s:s._backend.cognit_field(s.id,3),lambda s,v:s._set(3,v))
    last_activated_cognitive_tick=property(lambda s:(int(s._backend.cognit_field(s.id,4)) or None),lambda s,v:s._set(4,v or 0))
    refractory_ticks=property(lambda s:int(s._backend.cognit_field(s.id,5)),lambda s,v:s._set(5,v))
    homeostatic_threshold=property(lambda s:s._backend.cognit_field(s.id,6),lambda s,v:s._set(6,v))
    activity_trace=property(lambda s:s._backend.cognit_field(s.id,7),lambda s,v:s._set(7,v))
    target_activity=property(lambda s:s._backend.cognit_field(s.id,8),lambda s,v:s._set(8,v))
    age=property(lambda s:int(s._backend.cognit_field(s.id,9)),lambda s,v:s._set(9,v))
    predictive_contribution=property(lambda s:s._backend.cognit_field(s.id,10),lambda s,v:s._set(10,v))
    low_retention_ticks=property(lambda s:int(s._backend.cognit_field(s.id,11)),lambda s,v:s._set(11,v))
    @property
    def effective_threshold(self):return max(self.threshold,self.homeostatic_threshold)
    def receive(self,energy,tick,settings,wave_step=False):
        return self._backend.receive(self.id,energy,tick,settings,wave_step)
    def homeostatic_step(self,was_active,settings):
        self.age+=1;sample=1. if was_active else 0.;lam=settings.homeostasis_trace_decay;self.activity_trace=lam*self.activity_trace+(1-lam)*sample
        self.homeostatic_threshold=min(settings.threshold_max,max(settings.threshold_min,self.homeostatic_threshold+settings.homeostasis_learning_rate*(self.activity_trace-self.target_activity)))
        self.activity*=settings.cognit_activity_decay;self.utility*=.999;self.refractory_ticks=max(0,self.refractory_ticks-1)
    def retention_score(self,tick,settings):
        idle=tick-(self.last_activated_cognitive_tick or 0);recency=exp(-idle/max(1,settings.cognit_death_age))
        return settings.retention_utility_weight*self.utility+settings.retention_confidence_weight*self.confidence+settings.retention_prediction_weight*self.predictive_contribution+settings.retention_recency_weight*recency


class NativeRelation:
    __slots__=("_backend","_handle","source_id","target_id","relation_type","context_id","_values")
    def __init__(self,backend,row):
        backend.relation_proxy_objects_created+=1;self._backend=backend;self.source_id=row[0]+1;self.target_id=row[1]+1;self.relation_type=RelationType(row[2]);self.context_id=row[3] if row[3] else None;self._values=list(row[4:15]);self._handle=tuple(row[15])
    def _write(self):self._backend.ffi_calls+=1;self._backend.engine.update_relation(self._handle,tuple(self._values))
    def _prop(index):
        def get(self):return self._values[index]
        def set(self,value):self._values[index]=value;self._write()
        return property(get,set)
    strength=_prop(0);confidence=_prop(1);prediction_probability=_prop(2);support=_prop(3);lift=_prop(4);last_evidence_world_tick=_prop(5)
    status=property(lambda s:RelationStatus(s._values[6]),lambda s,v:(s._values.__setitem__(6,v.value),s._write()))
    contradiction_evidence=_prop(7);usefulness=_prop(8);confirmations=_prop(9)
    last_used_cognitive_tick=property(lambda s:(int(s._values[10]) or None),lambda s,v:(s._values.__setitem__(10,v or 0),s._write()))
    uncertainty=property(lambda s:1-s.confidence,lambda s,v:None)
    age=0;delay=0
    def effective_confidence(self,tick,decay):return self.confidence*decay**(tick-self.last_evidence_world_tick)
    def materialize_decay(self,tick,decay):
        if tick<self.last_evidence_world_tick:raise ValueError("world clock moved backwards")
        self.confidence=self.effective_confidence(tick,decay);self.last_evidence_world_tick=tick
    def update_outcome(self,confirmed,confirmation_rate,contradiction_rate):
        if confirmed:self.confirmations+=1;self.confidence+=confirmation_rate*(1-self.confidence);self.contradiction_evidence*=1-contradiction_rate
        else:self.contradiction_evidence+=contradiction_rate*(1-self.contradiction_evidence);self.confidence*=1-contradiction_rate
        self.confidence=max(0.,min(1.,self.confidence))


class NativeGraphFacade:
    def __init__(self,backend):self.backend=backend;self.nodes={}
    @property
    def next_id(self):return self.backend.engine.cognit_count+1
    @property
    def relation_count(self):return self.backend.engine.relation_count
    @property
    def adjacency(self):
        # Compatibility export used only by explicit persistence/debug paths.
        return {source:{(r.target_id,r.relation_type,r.context_id):r for r in self.outgoing(source)} for source in self.nodes}
    def to_dict(self):
        from .graph import CognitiveGraph
        return CognitiveGraph.to_dict(self)
    def semantic_to_dict(self):
        """Persistence metadata without materializing the native Relation graph."""
        from .graph import CognitiveGraph
        view=type('_SemanticView',(),{})();view.nodes=self.nodes;view.next_id=self.next_id;view.adjacency={}
        return CognitiveGraph.to_dict(view)
    def add_cognit(self,cognit=None):
        from .cognit import Cognit
        template=cognit or Cognit(self.next_id);native_id=self.backend.engine.add_cognit(template.activity,template.threshold,template.confidence)+1
        if cognit is not None and cognit.id!=native_id:raise ValueError(f"native CognitID mismatch: expected {cognit.id}, got {native_id}")
        node=NativeCognit(native_id,self.backend,template);self.nodes[native_id]=node
        values=(template.activity,template.threshold,template.confidence,template.utility,template.last_activated_cognitive_tick or 0,template.refractory_ticks,template.homeostatic_threshold,template.activity_trace,template.target_activity,template.age,template.predictive_contribution,template.low_retention_ticks)
        self.backend.ffi_calls+=1;self.backend.field_write_calls+=1;self.backend.engine.set_cognit_states([native_id-1],values)
        return node
    def connect(self,source,target,relation_type=RelationType.ASSOCIATIVE,context_id=None):
        before=self.relation_count;self.backend.ffi_calls+=1;handle=self.backend.engine.add_relation(source-1,target-1,relation_type.value,context_id or 0,.2,.3,0.)
        self.backend.ffi_calls+=1;row=self.backend.engine.relation_state(source-1,handle)
        return NativeRelation(self.backend,row),self.relation_count>before
    def outgoing(self,source):self.backend.ffi_calls+=1;return [NativeRelation(self.backend,r) for r in self.backend.engine.outgoing([source-1])]
    def outgoing_targets(self,source):self.backend.ffi_calls+=1;return [target+1 for target in self.backend.engine.outgoing_targets([source-1])]
    def remove_relation(self,source,target,relation_type=None,context_id=None):
        for relation in self.outgoing(source):
            if relation.target_id==target and (relation_type is None or relation.relation_type is relation_type) and (context_id is None or relation.context_id==context_id):self.backend.engine.remove_relation(relation._handle)
    def remove_cognit(self,cognit_id):
        self.backend.engine.remove_cognit(cognit_id-1)
        self.backend.invalidate_state([cognit_id])
        self.nodes.pop(cognit_id,None)
