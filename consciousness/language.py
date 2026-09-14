"""Receptive exact-symbol identity grounded in embodied Cognit provenance."""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from math import exp
import unicodedata
from .cognit import Cognit
from .wave import WaveResult

@dataclass(frozen=True,slots=True)
class LanguageFrame:
    message_id:int;issued_at_world_time:float;surface:str
    def __post_init__(self):object.__setattr__(self,"surface",normalize_token(self.surface))
@dataclass(frozen=True,slots=True)
class LanguageUtteranceFrame:
    message_id:int;issued_at_world_time:float;tokens:tuple[str,...]
    def __post_init__(self):
        normalized=tuple(normalize_token(x) for x in self.tokens)
        if not normalized:raise ValueError("LanguageUtteranceFrame requires at least one token")
        object.__setattr__(self,"tokens",normalized)
@dataclass(frozen=True,slots=True)
class GroundingContextEntry:cognit_id:int;salience:float
@dataclass(frozen=True,slots=True)
class GroundingContextSnapshot:world_time:float;observation_generation:int;entries:tuple[GroundingContextEntry,...]
@dataclass(frozen=True,slots=True)
class HistoricalGroundingContext:snapshot:GroundingContextSnapshot;retired_at_world_time:float
@dataclass(frozen=True,slots=True)
class LanguageProcessingResult:symbol_id:int|None;wave:WaveResult;grounding_candidates_updated:int;grounding_relations_materialized:int
@dataclass(frozen=True,slots=True)
class LanguageUtteranceResult:
    message_id:int;world_time:float;tokens:tuple[str,...];ordered_symbol_ids:tuple[int|None,...];token_results:tuple[LanguageProcessingResult,...];sequence_edges:tuple[tuple[int,int],...];composed_active_ids:frozenset[int];token_count:int
@dataclass(slots=True)
class LanguageUtteranceFrontier:
    frame:LanguageUtteranceFrame;grounding_context:dict[int,float];next_token_index:int=0;processed_symbol_ids:list[int|None]=None;token_results:list[LanguageProcessingResult]=None;phase:str="TOKEN"
    def __post_init__(self):
        if self.processed_symbol_ids is None:self.processed_symbol_ids=[]
        if self.token_results is None:self.token_results=[]

def normalize_token(surface:str)->str:
    token=unicodedata.normalize("NFC",surface.strip())
    if not token or any(ch.isspace() for ch in token):raise ValueError("LanguageFrame requires exactly one non-empty token")
    return token

class GroundingContextTracker:
    """Observational WorldTime-weighted history of sensory-derived Cognit IDs."""
    def __init__(self,settings):self.settings=settings;self.latest=None;self.historical=deque(maxlen=settings.language_recent_contexts);self.background_mass={};self.total_experience_time=0.;self.accounted_until=None
    @property
    def recent(self):return self.historical
    def accrue(self,now):
        if self.accounted_until is None:self.accounted_until=float(now);return
        if now<self.accounted_until:raise ValueError("grounding context time moved backwards")
        dt=float(now)-self.accounted_until
        if dt and self.latest:
            for e in self.latest.entries:self.background_mass[e.cognit_id]=self.background_mass.get(e.cognit_id,0.)+e.salience*dt
            self.total_experience_time+=dt
        self.accounted_until=float(now)
    def observe(self,snapshot):
        self.accrue(snapshot.world_time)
        if self.latest is not None:self.historical.append(HistoricalGroundingContext(self.latest,float(snapshot.world_time)))
        self.latest=snapshot
    def eligible(self,now):
        self.accrue(now);merged={};h=self.settings.language_grounding_horizon_seconds;tau=self.settings.language_grounding_tau_seconds
        if self.latest is not None:
            for e in self.latest.entries:merged[e.cognit_id]=max(merged.get(e.cognit_id,0.),e.salience)
        for item in self.historical:
            snapshot=item.snapshot;age=float(now)-item.retired_at_world_time
            if age<0 or age>h:continue
            credit=exp(-age/max(tau,1e-12))
            for e in snapshot.entries:merged[e.cognit_id]=max(merged.get(e.cognit_id,0.),e.salience*credit)
        return merged
    @staticmethod
    def _dump(s):return None if s is None else [s.world_time,s.observation_generation,[[e.cognit_id,e.salience] for e in s.entries]]
    @staticmethod
    def _load(raw):return None if raw is None else GroundingContextSnapshot(float(raw[0]),int(raw[1]),tuple(GroundingContextEntry(int(i),float(q)) for i,q in raw[2]))
    def durable_dict(self):return {"background_mass":[[i,v] for i,v in sorted(self.background_mass.items())],"total_experience_time":self.total_experience_time}
    def episode_dict(self):return {"latest":self._dump(self.latest),"historical":[[self._dump(x.snapshot),x.retired_at_world_time] for x in self.historical],"accounted_until":self.accounted_until}
    def restore_durable(self,data):data=data or {};self.background_mass={int(i):float(v) for i,v in data.get("background_mass",[])};self.total_experience_time=float(data.get("total_experience_time",0.))
    def restore_episode(self,data):
        data=data or {};self.latest=self._load(data.get("latest"));rows=data.get("historical")
        if rows is None:rows=[[self._load(x),float(self._load(x).world_time)] for x in data.get("recent",[]) if self._load(x)!=self.latest]
        else:rows=[[self._load(x),float(t)] for x,t in rows]
        self.historical=deque((HistoricalGroundingContext(x,t) for x,t in rows),maxlen=self.settings.language_recent_contexts);self.accounted_until=data.get("accounted_until")

class LanguageLexicon:
    """Identity and bounded evidence only; Relations carry learned meaning."""
    def __init__(self,core):self.core=core;self.symbols={};self.exposures={};self.grounded_trials={};self.evidence={};self.materialized={};self.sequence_support={};self.sequence_trials={};self.sequence_materialized={};self.total_exposures=0;self.grounding_relations_materialized=0;self.sequence_relations_materialized=0;self.last_language_symbol_id=None;self.last_language_wave_active_ids=frozenset();self.outgoing_scans=0;self.native_relation_batch_calls=0;self.native_sequence_batch_calls=0
    def symbol(self,surface):
        node_id=self.symbols.get(surface)
        if node_id is not None and node_id not in self.core.graph.nodes:self.symbols.pop(surface,None);self.exposures.pop(surface,None);self.grounded_trials.pop(surface,None);self.evidence.pop(surface,None);self.materialized.pop(surface,None);node_id=None
        if node_id is None:
            if len(self.core.graph.nodes)>=self.core.settings.max_cognits:return None
            node=self.core.graph.add_cognit(Cognit(self.core.graph.next_id,kind="LANGUAGE_SYMBOL"));node_id=node.id;self.symbols[surface]=node_id
        return node_id
    def learn(self,frame,context,tracker):
        token=normalize_token(frame.surface);symbol=self.symbol(token);self.last_language_symbol_id=symbol;self.total_exposures+=1;self.exposures[token]=self.exposures.get(token,0)+1
        if symbol is None:return None,0,0
        filtered={target:q for target,q in sorted(context.items()) if target!=symbol and target in self.core.graph.nodes and self.core.graph.nodes[target].kind not in {"LANGUAGE_SYMBOL","TARGET"}}
        rows=self.evidence.get(token)
        if not filtered:return symbol,0 if rows is None else len(rows),0
        if rows is None:rows=self.evidence.setdefault(token,{})
        for target in tuple(rows):
            if target not in self.core.graph.nodes:rows.pop(target);self.materialized.setdefault(token,set()).discard(target)
        self.grounded_trials[token]=self.grounded_trials.get(token,0)+1
        for target,q in filtered.items():
            count,mass=rows.get(target,(0,0.));rows[target]=(count+1,mass+q)
        self._bound(token,tracker);updates=self._relation_rows(token,tracker);previous=self.materialized.setdefault(token,set())
        made=0
        if updates:
            self.core.backend.ffi_calls+=1;self.core.backend.language_relation_batch_calls+=1;self.native_relation_batch_calls+=1
            created=self.core.backend.engine.upsert_relation_states_batch(symbol-1,updates,self.core.settings.max_new_relations_per_tick,self.core.settings.max_relations);created={int(i)+1 for i in created};made=len(created);self.grounding_relations_materialized+=made;previous.update(created)
        return symbol,len(rows),made
    def _metrics(self,token,target,tracker):
        count,mass=self.evidence[token][target];conditional=mass/max(1,self.grounded_trials.get(token,0));background=tracker.background_mass.get(target,0.)/max(tracker.total_experience_time,1e-12);return count,conditional,conditional/max(background,1e-9)
    def _bound(self,token,tracker):
        rows=self.evidence[token];cap=self.core.settings.language_max_provisional_candidates_per_symbol;known=self.materialized.setdefault(token,set());ranked=sorted((i for i in rows if i not in known),key=lambda i:(-self._metrics(token,i,tracker)[0],-rows[i][1],-self._metrics(token,i,tracker)[2],i))
        for target in ranked[cap:]:rows.pop(target,None)
    def _relation_rows(self,token,tracker):
        s=self.core.settings;known=self.materialized.setdefault(token,set());ranked=[]
        for target in self.evidence[token]:
            count,conditional,lift=self._metrics(token,target,tracker);existing=target in known
            if not existing and (tracker.total_experience_time<s.language_min_background_seconds or count<s.language_min_support or lift<s.language_min_lift):continue
            lift_score=max(0.,min(1.,(lift-1.)/max(s.language_lift_saturation-1.,1e-9)));strength=max(0.,min(1.,conditional*lift_score));confidence=count/(count+s.language_confidence_k);ranked.append((target,1,0,strength,confidence,strength,count,lift))
        ranked.sort(key=lambda r:(r[0] not in known,-r[6],-r[7],-r[3],r[0]));new_budget=min(s.max_new_relations_per_tick,max(0,s.max_relations-self.core.graph.relation_count));out=[]
        for row in ranked:
            if row[0] in known:out.append(row)
            elif new_budget:out.append(row);new_budget-=1
        return out
    def learn_sequence(self,symbol_ids):
        pairs=[]
        for source,target in zip(symbol_ids,symbol_ids[1:]):
            if source is None or target is None:continue
            pairs.append((source,target));self.sequence_trials[source]=self.sequence_trials.get(source,0)+1;rows=self.sequence_support.setdefault(source,{});rows[target]=rows.get(target,0)+1
        touched=sorted(set(source for source,_ in pairs));all_updates=[]
        for source in touched:
            rows=self.sequence_support[source];known=self.sequence_materialized.setdefault(source,set());cap=self.core.settings.language_max_sequence_candidates_per_symbol
            ranked=sorted((target for target in rows if target not in known),key=lambda target:(-rows[target],-(rows[target]/self.sequence_trials[source]),target))
            for target in ranked[cap:]:rows.pop(target,None)
            updates=[]
            for target in sorted(rows):
                support=rows[target];probability=support/max(1,self.sequence_trials[source]);confidence=support/(support+self.core.settings.language_sequence_confidence_k)
                if target not in known and support<self.core.settings.language_sequence_min_support:continue
                updates.append((target,2,0,probability*confidence,confidence,probability,support,1.))
            if updates:all_updates.append((source,updates))
        made=0
        for source,updates in all_updates:
            available=max(0,self.core.settings.max_new_relations_per_tick-made)
            if not available and not any(row[0] in self.sequence_materialized[source] for row in updates):continue
            self.core.backend.ffi_calls+=1;self.core.backend.language_relation_batch_calls+=1;self.native_relation_batch_calls+=1;self.native_sequence_batch_calls+=1
            created={int(i)+1 for i in self.core.backend.engine.upsert_relation_states_batch(source-1,updates,available,self.core.settings.max_relations)};made+=len(created);self.sequence_materialized[source].update(created)
        self.sequence_relations_materialized+=made
        return tuple(pairs),made
    @property
    def language_symbol_count(self):return len(self.symbols)
    @property
    def language_exposures(self):return self.total_exposures
    @property
    def grounding_candidates(self):return sum(map(len,self.evidence.values()))
    @property
    def sequence_candidates(self):return sum(map(len,self.sequence_support.values()))
    def to_dict(self):return {"symbols":dict(sorted(self.symbols.items())),"exposures":dict(sorted(self.exposures.items())),"grounded_trials":dict(sorted(self.grounded_trials.items())),"evidence":{k:[[i,n,m] for i,(n,m) in sorted(v.items())] for k,v in sorted(self.evidence.items())},"materialized":{k:sorted(v) for k,v in sorted(self.materialized.items())},"sequence_support":[[s,t,n] for s,rows in sorted(self.sequence_support.items()) for t,n in sorted(rows.items())],"sequence_trials":[[s,n] for s,n in sorted(self.sequence_trials.items())],"sequence_materialized":[[s,sorted(v)] for s,v in sorted(self.sequence_materialized.items())],"total_exposures":self.total_exposures,"grounding_relations_materialized":self.grounding_relations_materialized,"sequence_relations_materialized":self.sequence_relations_materialized}
    @classmethod
    def from_dict(cls,core,data):
        obj=cls(core);data=data or {};obj.symbols={str(k):int(v) for k,v in data.get("symbols",{}).items()};obj.exposures={str(k):int(v) for k,v in data.get("exposures",{}).items()};legacy="support" in data and "evidence" not in data
        obj.grounded_trials=({k:int(obj.exposures.get(k,0)) for k in obj.symbols} if legacy else {str(k):int(v) for k,v in data.get("grounded_trials",{}).items()})
        if legacy:obj.evidence={str(k):{int(i):(int(n),float(n)) for i,n in rows} for k,rows in data.get("support",{}).items()}
        else:obj.evidence={str(k):{int(i):(int(n),float(m)) for i,n,m in rows} for k,rows in data.get("evidence",{}).items()}
        obj.materialized={str(k):set(map(int,v)) for k,v in data.get("materialized",{}).items()};obj.sequence_support={};
        for s,t,n in data.get("sequence_support",[]):obj.sequence_support.setdefault(int(s),{})[int(t)]=int(n)
        obj.sequence_trials={int(s):int(n) for s,n in data.get("sequence_trials",[])};obj.sequence_materialized={int(s):set(map(int,v)) for s,v in data.get("sequence_materialized",[])};obj.total_exposures=int(data.get("total_exposures",0));obj.grounding_relations_materialized=int(data.get("grounding_relations_materialized",0));obj.sequence_relations_materialized=int(data.get("sequence_relations_materialized",0));obj._legacy_grounding=({"background_mass":[[int(i),float(n)] for i,n in data.get("background",[])],"total_experience_time":float(data.get("total_exposures",0))} if legacy else None)
        if legacy or "materialized" not in data:
            for token,source in obj.symbols.items():obj.materialized[token]={r.target_id for r in core.graph.outgoing(source) if r.relation_type.name=="ASSOCIATIVE"}
        if "sequence_materialized" not in data:
            for source in obj.symbols.values():
                targets={r.target_id for r in core.graph.outgoing(source) if r.relation_type.name=="SEQUENTIAL" and r.target_id in obj.symbols.values()}
                if targets:obj.sequence_materialized[source]=targets
        return obj
    def restore_legacy_grounding(self,tracker):
        if getattr(self,"_legacy_grounding",None) is not None:tracker.restore_durable(self._legacy_grounding)
