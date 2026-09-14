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
class GroundingContextEntry:cognit_id:int;salience:float
@dataclass(frozen=True,slots=True)
class GroundingContextSnapshot:world_time:float;observation_generation:int;entries:tuple[GroundingContextEntry,...]
@dataclass(frozen=True,slots=True)
class LanguageProcessingResult:symbol_id:int|None;wave:WaveResult;grounding_candidates_updated:int;grounding_relations_materialized:int

def normalize_token(surface:str)->str:
    token=unicodedata.normalize("NFC",surface.strip())
    if not token or any(ch.isspace() for ch in token):raise ValueError("LanguageFrame requires exactly one non-empty token")
    return token

class GroundingContextTracker:
    """Observational WorldTime-weighted history of sensory-derived Cognit IDs."""
    def __init__(self,settings):self.settings=settings;self.latest=None;self.recent=deque(maxlen=settings.language_recent_contexts);self.background_mass={};self.total_experience_time=0.;self.accounted_until=None
    def accrue(self,now):
        if self.accounted_until is None:self.accounted_until=float(now);return
        if now<self.accounted_until:raise ValueError("grounding context time moved backwards")
        dt=float(now)-self.accounted_until
        if dt and self.latest:
            for e in self.latest.entries:self.background_mass[e.cognit_id]=self.background_mass.get(e.cognit_id,0.)+e.salience*dt
            self.total_experience_time+=dt
        self.accounted_until=float(now)
    def observe(self,snapshot):self.accrue(snapshot.world_time);self.latest=snapshot;self.recent.append(snapshot)
    def eligible(self,now):
        self.accrue(now);merged={};h=self.settings.language_grounding_horizon_seconds;tau=self.settings.language_grounding_tau_seconds
        for snapshot in self.recent:
            age=float(now)-snapshot.world_time
            if age<0 or age>h:continue
            credit=exp(-age/max(tau,1e-12))
            for e in snapshot.entries:merged[e.cognit_id]=max(merged.get(e.cognit_id,0.),e.salience*credit)
        return merged
    @staticmethod
    def _dump(s):return None if s is None else [s.world_time,s.observation_generation,[[e.cognit_id,e.salience] for e in s.entries]]
    @staticmethod
    def _load(raw):return None if raw is None else GroundingContextSnapshot(float(raw[0]),int(raw[1]),tuple(GroundingContextEntry(int(i),float(q)) for i,q in raw[2]))
    def durable_dict(self):return {"background_mass":[[i,v] for i,v in sorted(self.background_mass.items())],"total_experience_time":self.total_experience_time}
    def episode_dict(self):return {"latest":self._dump(self.latest),"recent":[self._dump(x) for x in self.recent],"accounted_until":self.accounted_until}
    def restore_durable(self,data):data=data or {};self.background_mass={int(i):float(v) for i,v in data.get("background_mass",[])};self.total_experience_time=float(data.get("total_experience_time",0.))
    def restore_episode(self,data):data=data or {};self.latest=self._load(data.get("latest"));self.recent=deque((self._load(x) for x in data.get("recent",[])),maxlen=self.settings.language_recent_contexts);self.accounted_until=data.get("accounted_until")

class LanguageLexicon:
    """Identity and bounded evidence only; Relations carry learned meaning."""
    def __init__(self,core):self.core=core;self.symbols={};self.exposures={};self.grounded_trials={};self.evidence={};self.materialized={};self.total_exposures=0;self.grounding_relations_materialized=0;self.last_language_symbol_id=None;self.last_language_wave_active_ids=frozenset();self.outgoing_scans=0;self.native_relation_batch_calls=0
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
        rows=self.evidence.setdefault(token,{})
        for target in tuple(rows):
            if target not in self.core.graph.nodes:rows.pop(target);self.materialized.setdefault(token,set()).discard(target)
        if context:
            self.grounded_trials[token]=self.grounded_trials.get(token,0)+1
            for target,q in sorted(context.items()):
                if target==symbol or target not in self.core.graph.nodes or self.core.graph.nodes[target].kind in {"LANGUAGE_SYMBOL","TARGET"}:continue
                count,mass=rows.get(target,(0,0.));rows[target]=(count+1,mass+q)
        self._bound(token,tracker);updates=self._relation_rows(token,tracker);previous=self.materialized.setdefault(token,set());new_targets=[row[0] for row in updates if row[0] not in previous]
        made=0
        if updates:
            self.core.backend.ffi_calls+=1;self.core.backend.language_relation_batch_calls+=1;self.native_relation_batch_calls+=1
            made=self.core.backend.engine.upsert_relation_states_batch(symbol-1,updates,self.core.settings.max_new_relations_per_tick,self.core.settings.max_relations);self.grounding_relations_materialized+=made;previous.update(new_targets[:made])
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
    @property
    def language_symbol_count(self):return len(self.symbols)
    @property
    def language_exposures(self):return self.total_exposures
    @property
    def grounding_candidates(self):return sum(map(len,self.evidence.values()))
    def to_dict(self):return {"symbols":dict(sorted(self.symbols.items())),"exposures":dict(sorted(self.exposures.items())),"grounded_trials":dict(sorted(self.grounded_trials.items())),"evidence":{k:[[i,n,m] for i,(n,m) in sorted(v.items())] for k,v in sorted(self.evidence.items())},"materialized":{k:sorted(v) for k,v in sorted(self.materialized.items())},"total_exposures":self.total_exposures,"grounding_relations_materialized":self.grounding_relations_materialized}
    @classmethod
    def from_dict(cls,core,data):
        obj=cls(core);data=data or {};obj.symbols={str(k):int(v) for k,v in data.get("symbols",{}).items()};obj.exposures={str(k):int(v) for k,v in data.get("exposures",{}).items()};obj.grounded_trials={str(k):int(v) for k,v in data.get("grounded_trials",{}).items()};obj.evidence={str(k):{int(i):(int(n),float(m)) for i,n,m in rows} for k,rows in data.get("evidence",{}).items()};obj.materialized={str(k):set(map(int,v)) for k,v in data.get("materialized",{}).items()};obj.total_exposures=int(data.get("total_exposures",0));obj.grounding_relations_materialized=int(data.get("grounding_relations_materialized",0));return obj
