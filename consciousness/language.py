"""Receptive exact-symbol identity and experience-grounded association learning."""
from __future__ import annotations
from dataclasses import dataclass
import unicodedata

from .cognit import Cognit
from .relation import RelationType


@dataclass(frozen=True,slots=True)
class LanguageFrame:
    message_id:int
    issued_at_world_time:float
    surface:str

    def __post_init__(self):
        normalized=normalize_token(self.surface)
        if normalized!=self.surface:object.__setattr__(self,"surface",normalized)


def normalize_token(surface:str)->str:
    token=unicodedata.normalize("NFC",surface.strip())
    if not token or any(ch.isspace() for ch in token):raise ValueError("LanguageFrame requires exactly one non-empty token")
    return token


class LanguageLexicon:
    """Surface identity plus contrastive counts; semantic meaning stays in Relations."""
    def __init__(self,core):
        self.core=core;self.symbols:dict[str,int]={};self.exposures:dict[str,int]={}
        self.support:dict[str,dict[int,int]]={};self.background:dict[int,int]={};self.total_exposures=0
        self.grounding_relations_materialized=0;self.last_language_symbol_id=None;self.last_language_wave_active_ids=frozenset()

    def _symbol(self,surface:str)->int:
        node_id=self.symbols.get(surface)
        if node_id is not None and node_id not in self.core.graph.nodes:
            self.symbols.pop(surface,None);self.exposures.pop(surface,None);self.support.pop(surface,None);node_id=None
        if node_id is None:
            node=self.core.graph.add_cognit(Cognit(self.core.graph.next_id,kind="LANGUAGE_SYMBOL"))
            node_id=node.id;self.symbols[surface]=node_id
        return node_id

    def process(self,frame:LanguageFrame,context:set[int]):
        token=normalize_token(frame.surface);symbol=self._symbol(token);self.last_language_symbol_id=symbol
        context={i for i in context if i!=symbol and i in self.core.graph.nodes and self.core.graph.nodes[i].kind!="LANGUAGE_SYMBOL"}
        self.total_exposures+=1;self.exposures[token]=self.exposures.get(token,0)+1;counts=self.support.setdefault(token,{})
        for node_id in sorted(context):self.background[node_id]=self.background.get(node_id,0)+1;counts[node_id]=counts.get(node_id,0)+1
        for node_id in tuple(counts):
            if node_id not in self.core.graph.nodes:counts.pop(node_id,None);self.background.pop(node_id,None)
        for node_id in sorted(counts):self._update_relation(symbol,node_id,counts[node_id],self.exposures[token])
        self.core.cognitive_tick+=1;tick=self.core.cognitive_tick;s=self.core.settings
        self.core.backend.receive(symbol,s.language_symbol_activation,tick,s)
        wave=self.core._propagate({symbol},tick);self.core.last_wave=wave;self.last_language_wave_active_ids=wave.active_ids
        return wave

    def _update_relation(self,symbol,target,support,exposures):
        s=self.core.settings;background=self.background.get(target,0)/max(1,self.total_exposures);conditional=support/max(1,exposures);lift=conditional/max(background,1e-9)
        existing=next((r for r in self.core.graph.outgoing(symbol) if r.target_id==target and r.relation_type is RelationType.ASSOCIATIVE),None)
        if existing is None and (support<s.language_min_support or lift<s.language_min_lift):return
        relation=existing
        if relation is None:relation,_=self.core.graph.connect(symbol,target,RelationType.ASSOCIATIVE);self.grounding_relations_materialized+=1
        selectivity=min(1.,lift/max(s.language_min_lift,1e-9));desired=conditional*selectivity
        relation.support=support;relation.lift=lift
        if existing is None:relation.strength=s.language_relation_initial_strength*desired;relation.confidence=s.language_relation_initial_strength
        elif target in self.support.get(next((k for k,v in self.symbols.items() if v==symbol),""),{}):
            rate=s.language_relation_confirmation_rate if conditional>=relation.strength else s.language_relation_contradiction_rate
            relation.strength=max(0.,min(1.,relation.strength+rate*(desired-relation.strength)))
            relation.confidence=max(0.,min(1.,relation.confidence+rate*((support/(support+s.language_confidence_k))-relation.confidence)))
        relation.prediction_probability=relation.strength

    @property
    def language_symbol_count(self):return len(self.symbols)
    @property
    def language_exposures(self):return self.total_exposures
    @property
    def grounding_candidates(self):return sum(map(len,self.support.values()))

    def to_dict(self):
        return {"symbols":dict(sorted(self.symbols.items())),"exposures":dict(sorted(self.exposures.items())),"support":{k:[[i,n] for i,n in sorted(v.items())] for k,v in sorted(self.support.items())},"background":[[i,n] for i,n in sorted(self.background.items())],"total_exposures":self.total_exposures,"grounding_relations_materialized":self.grounding_relations_materialized}

    @classmethod
    def from_dict(cls,core,data):
        obj=cls(core);data=data or {};obj.symbols={str(k):int(v) for k,v in data.get("symbols",{}).items()};obj.exposures={str(k):int(v) for k,v in data.get("exposures",{}).items()};obj.support={str(k):{int(i):int(n) for i,n in rows} for k,rows in data.get("support",{}).items()};obj.background={int(i):int(n) for i,n in data.get("background",[])};obj.total_exposures=int(data.get("total_exposures",0));obj.grounding_relations_materialized=int(data.get("grounding_relations_materialized",0));return obj
