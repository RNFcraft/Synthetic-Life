from collections import defaultdict
from typing import Any, Iterable
from .cognit import Cognit
from .relation import Relation, RelationType


class CognitiveGraph:
    def __init__(self) -> None:
        self.nodes:dict[int,Cognit]={}; self.adjacency:dict[int,dict[tuple[int,RelationType,int|None],Relation]]=defaultdict(dict); self.next_id=1
    @property
    def relation_count(self)->int: return sum(map(len,self.adjacency.values()))
    def add_cognit(self,cognit:Cognit|None=None)->Cognit:
        node=cognit or Cognit(self.next_id); self.nodes[node.id]=node; self.next_id=max(self.next_id,node.id+1); return node
    def connect(self,source:int,target:int,relation_type:RelationType=RelationType.ASSOCIATIVE,context_id:int|None=None)->tuple[Relation,bool]:
        key=(target,relation_type,context_id);existing=self.adjacency[source].get(key)
        if existing:return existing,False
        relation=Relation(source,target,relation_type=relation_type,context_id=context_id);self.adjacency[source][key]=relation;return relation,True
    def outgoing(self,source:int)->Iterable[Relation]:return self.adjacency.get(source,{}).values()
    def remove_cognit(self,cognit_id:int)->None:
        self.nodes.pop(cognit_id,None); self.adjacency.pop(cognit_id,None)
        for edges in self.adjacency.values():
            for key in [k for k in edges if k[0]==cognit_id]:edges.pop(key,None)
    def remove_relation(self,source:int,target:int,relation_type:RelationType|None=None,context_id:int|None=None)->None:
        edges=self.adjacency.get(source,{})
        for key in [k for k in edges if k[0]==target and (relation_type is None or k[1] is relation_type) and (context_id is None or k[2]==context_id)]:edges.pop(key,None)
    def to_dict(self)->dict[str,Any]:
        return {"next_id":self.next_id,"nodes":[{"id":n.id,"activity":n.activity,"threshold":n.threshold,"confidence":n.confidence,
          "utility":n.utility,"age":n.age,"last_activated_cognitive_tick":n.last_activated_cognitive_tick,"homeostatic_threshold":n.homeostatic_threshold,
          "activity_trace":n.activity_trace,"target_activity":n.target_activity,"refractory_ticks":n.refractory_ticks,"novelty":n.novelty,
          "predictive_contribution":n.predictive_contribution,"low_retention_ticks":n.low_retention_ticks,"kind":n.kind,
          "pattern":None if n.pattern is None else {"participants":n.pattern.participants,"relative_relationships":n.pattern.relative_relationships,
          "temporal_order":n.pattern.temporal_order,"tolerance":n.pattern.tolerance,"occurrence_count":n.pattern.occurrence_count,
          "stability":n.pattern.stability,"predictive_value":n.pattern.predictive_value,
          "nodes":[{"participant_type":x.participant_type.name,"reference":x.reference,"role":x.role} for x in n.pattern.nodes],
          "relations":[{"source":x.source,"target":x.target,"relation_type":x.relation_type.name,"expected_delta_t":x.expected_delta_t,
          "time_tolerance":x.time_tolerance,"spatial_mean":x.spatial_mean,"spatial_variance":x.spatial_variance} for x in n.pattern.relations],
          "compression_gain":n.pattern.compression_gain,"redundancy":n.pattern.redundancy,"abstraction_depth":n.pattern.abstraction_depth,
          "is_translation_tolerant":n.pattern.is_translation_tolerant,"positive_match_mean":n.pattern.positive_match_mean,
          "background_match_mean":n.pattern.background_match_mean,"selectivity_trials":n.pattern.selectivity_trials}} for n in self.nodes.values()],
          "relations":[{"source_id":r.source_id,"target_id":r.target_id,"strength":r.strength,"confidence":r.confidence,"delay":r.delay,
          "relation_type":r.relation_type.name,"context_id":r.context_id,"age":r.age,"last_used_cognitive_tick":r.last_used_cognitive_tick,"support":r.support,
          "lift":r.lift,"last_evidence_world_tick":r.last_evidence_world_tick,"status":r.status.name,"prediction_probability":r.prediction_probability,
          "uncertainty":r.uncertainty,"contradiction_evidence":r.contradiction_evidence,"usefulness":r.usefulness,
          "confirmations":r.confirmations} for edges in self.adjacency.values() for r in edges.values()]}
