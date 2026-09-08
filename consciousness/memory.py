from __future__ import annotations
from collections import Counter
from dataclasses import dataclass,field
from math import exp
from .cognit import Cognit
from .relation import RelationStatus,RelationType

def _rotate(sig:tuple,n:int)->tuple:
    out=[]
    for x,y,ch,val in sig:
        for _ in range(n%4):x,y=-y,x
        out.append((x,y,ch,val))
    return tuple(sorted(out))

def _similarity(a:tuple,b:tuple,weights=None)->float:
    a,b=set(a),set(b);u=a|b
    return (sum((weights or {}).get(x,1.) for x in a&b)/max(1e-9,sum((weights or {}).get(x,1.) for x in u))) if u else 1.

@dataclass(slots=True)
class PlaceMemory:
    id:int;cognit_id:int;signature:tuple;confidence:float=.5;visits:int=1;last_confirmed_tick:int=0
    views:list[tuple]=field(default_factory=list);contradictions:int=0;aliases:set[int]=field(default_factory=set)
    last_confirmed_time_seconds:float|None=None

@dataclass(slots=True)
class PersistentStructureMemory:
    id:int;cognit_id:int;feature_signature:tuple;place_cognit_id:int;relative_context:tuple[float,float]
    remembered_state:tuple[int,...];confidence:float=.5;last_confirmed_tick:int=0;contradictions:int=0;reactivations:int=0
    last_recall_strength:float=0.;status:str="UNCERTAIN"
    last_confirmed_time_seconds:float|None=None;last_touch_time_seconds:float|None=None

class SpatialMemory:
    """Evidence-based topology; no world coordinates or object identifiers."""
    def __init__(self,settings)->None:
        self.settings=settings;self.places={};self.structures={};self.place_evidence=Counter();self.transitions=Counter()
        self.feature_seen=Counter();self.feature_change=Counter();self.next_place_id=1;self.next_memory_id=1;self.current_place_id=None
        self.reactivation_count=0;self.confirmation_count=0;self.contradiction_count=0;self.alias_reconciliations=0;self.last_place_scores={};self.last_recalled={}
        self._by_place={};self._by_cognit={};self._by_feature={};self._by_state={};self._index_order={};self._indexed_ids=set();self._nonzero_recall_ids=set()
        self.last_retrieval_candidates=0;self.last_retrieval_total=0
        self.world_time_seconds:float|None=None;self.materialization_work=0
        self.enabled=True

    def set_world_time(self,now:float|None)->None:
        if now is not None and (self.world_time_seconds is not None and now<self.world_time_seconds):raise ValueError("memory time moved backwards")
        self.world_time_seconds=now

    def _materialize(self,m)->None:
        if self.world_time_seconds is None:return
        last=m.last_touch_time_seconds
        if last is None:last=m.last_confirmed_time_seconds if m.last_confirmed_time_seconds is not None else self.world_time_seconds
        dt=self.world_time_seconds-last
        if dt<0:raise ValueError("memory time moved backwards")
        if dt:m.confidence*=self.settings.memory_confidence_decay**dt;m.last_touch_time_seconds=self.world_time_seconds;m.status=self._status(m);self.materialization_work+=1

    def _recency(self,m,tick,scale):
        if self.world_time_seconds is None:return exp(-(tick-m.last_confirmed_tick)/scale)
        last=m.last_confirmed_time_seconds if m.last_confirmed_time_seconds is not None else self.world_time_seconds
        return exp(-(self.world_time_seconds-last)/scale)

    def _rebuild_indexes(self)->None:
        self._by_place={};self._by_cognit={};self._by_feature={};self._by_state={};self._index_order={}
        for order,m in enumerate(self.structures.values()):self._index_order[m.id]=order;self._index_memory(m)
        self._indexed_ids=set(self.structures)

    @staticmethod
    def _add_index(index,key,memory_id)->None:index.setdefault(key,set()).add(memory_id)

    def _index_memory(self,m)->None:
        self._add_index(self._by_place,m.place_cognit_id,m.id);self._add_index(self._by_cognit,m.cognit_id,m.id)
        for feature in set(m.feature_signature):self._add_index(self._by_feature,feature,m.id)
        for position,value in enumerate(m.remembered_state):self._add_index(self._by_state,(position,value),m.id)

    def _ensure_indexes(self)->None:
        # Normal mutation paths maintain indexes incrementally.  The length
        # check only supports tests/importers that replace the public mapping.
        if len(self._indexed_ids)!=len(self.structures):self._rebuild_indexes()

    def remove_structure(self,memory_id)->None:
        m=self.structures.pop(memory_id,None)
        if m is None:return
        for index,key in ((self._by_place,m.place_cognit_id),(self._by_cognit,m.cognit_id)):
            ids=index.get(key);ids.discard(memory_id) if ids else None
        for feature in set(m.feature_signature):
            ids=self._by_feature.get(feature);ids.discard(memory_id) if ids else None
        for position,value in enumerate(m.remembered_state):
            ids=self._by_state.get((position,value));ids.discard(memory_id) if ids else None
        self._indexed_ids.discard(memory_id);self._index_order.pop(memory_id,None);self._nonzero_recall_ids.discard(memory_id)

    def _reindex_state(self,m,old_state)->None:
        if old_state==m.remembered_state:return
        for position,value in enumerate(old_state):
            ids=self._by_state.get((position,value));ids.discard(m.id) if ids else None
        for position,value in enumerate(m.remembered_state):self._add_index(self._by_state,(position,value),m.id)

    @staticmethod
    def place_signature(observation)->tuple:
        # Event/change bits describe the observation process, not place identity.
        return tuple(sorted((x,y,ch,val) for x,y,ch,val,_ in observation if ch!="self" and not ch.startswith("body_") and val))

    def _learn_stability(self,observation)->None:
        for _,_,ch,val,change in observation:
            if ch=="self" or ch.startswith("body_"):continue
            key=(ch,val);self.feature_seen[key]+=1;self.feature_change[key]+=int(bool(change))

    def _weights(self,sig)->dict:
        return {f:.2+.8*(1-self.feature_change[(f[2],f[3])]/max(1,self.feature_seen[(f[2],f[3])])) for f in sig}

    def _match_place(self,sig,previous,action):
        best=None;best_score=0.;self.last_place_scores={};av=action.value if action is not None else None
        for place in self.places.values():
            visual=max((_similarity(sig,_rotate(view,r),self._weights(sig)) for view in (place.views or [place.signature]) for r in range(4)),default=0.)
            expected=self.transitions[(previous,av,place.id)] if previous and av is not None else 0;total=sum(n for (p,a,_),n in self.transitions.items() if p==previous and a==av)
            transition=expected/max(1,total)
            if previous==place.id and action is not None and action.name.startswith("TURN_"):transition=max(.9,transition)
            score=.56*visual+.29*transition+.15*min(1.,place.visits/8);self.last_place_scores[place.id]=score
            if score>best_score:best,best_score=place,score
        return best if best_score>=.52 else None

    def observe(self,observation,tracks,graph,tick:int,previous_action)->set[int]:
        if not self.enabled:return set()
        self._learn_stability(observation);sig=self.place_signature(observation);previous=self.current_place_id;place=self._match_place(sig,previous,previous_action)
        key=(sig,previous,previous_action.value if previous_action is not None else None);self.place_evidence[key]+=1
        evidence=sum(n for (seen,_,_),n in self.place_evidence.items() if seen==sig)
        if place is None and evidence>=self.settings.place_birth_visits:
            node=graph.add_cognit(Cognit(graph.next_id,kind="PLACE",confidence=.55));place=PlaceMemory(self.next_place_id,node.id,sig,.55,1,tick,[sig],last_confirmed_time_seconds=self.world_time_seconds);self.places[place.id]=place;self.next_place_id+=1
        if place:
            if not place.views or all(max(_similarity(sig,_rotate(v,r)) for r in range(4))<.9 for v in place.views):place.views.append(sig)
            place.views=place.views[-8:];place.visits+=1;place.last_confirmed_tick=tick;place.last_confirmed_time_seconds=self.world_time_seconds;place.confidence=min(1.,place.confidence+.04*(1-place.confidence));self.current_place_id=place.id
            if previous and previous_action is not None:
                av=previous_action.value;self.transitions[(previous,av,place.id)]+=1
                if previous!=place.id:
                    rel,_=graph.connect(self.places[previous].cognit_id,place.cognit_id,RelationType.SELF_ACTION,av);rel.support+=1
                    total=sum(n for (p,a,_),n in self.transitions.items() if p==previous and a==av);rel.strength=rel.prediction_probability=self.transitions[(previous,av,place.id)]/max(1,total);rel.confidence=rel.support/(rel.support+4);rel.status=RelationStatus.CONSOLIDATED if rel.support>=4 else RelationStatus.PROVISIONAL
            self._reconcile(place,graph)
        active={place.cognit_id} if place else set();visible=[]
        for track in tracks:
            # Open tracks bridge short occlusions for perceptual continuity, but
            # absence is not a fresh observation and must not confirm a belief.
            if track.missing_ticks:continue
            if not any(ch in {"occupied","state","appearance"} for ch,_ in track.primitive_signature):continue
            features=tuple(sorted(track.primitive_signature));candidate=self._match_structure(features,track.state_signature,place.cognit_id if place else 0,tick,set(visible))
            if candidate:
                self._materialize(candidate);old_state=candidate.remembered_state;candidate.confidence=min(1.,candidate.confidence+.12*(1-candidate.confidence));candidate.last_confirmed_tick=tick;candidate.last_confirmed_time_seconds=self.world_time_seconds;candidate.last_touch_time_seconds=self.world_time_seconds;candidate.relative_context=track.centroid;candidate.remembered_state=track.state_signature;self._reindex_state(candidate,old_state);candidate.reactivations+=1;candidate.status=self._status(candidate);self.reactivation_count+=1;self.confirmation_count+=1;active.add(candidate.cognit_id);visible.append(candidate.id)
            elif place:
                node=graph.add_cognit(Cognit(graph.next_id,kind="MEMORY",confidence=.5));m=PersistentStructureMemory(self.next_memory_id,node.id,features,place.cognit_id,track.centroid,track.state_signature,.5,tick,last_confirmed_time_seconds=self.world_time_seconds,last_touch_time_seconds=self.world_time_seconds);self.structures[m.id]=m;self._index_order[m.id]=len(self._index_order);self._index_memory(m);self._indexed_ids.add(m.id);self.next_memory_id+=1;active.add(node.id);visible.append(m.id)
        if place:
            self._ensure_indexes()
            for memory_id in self._by_place.get(place.cognit_id,()):
                m=self.structures[memory_id]
                if m.place_cognit_id==place.cognit_id and m.id not in visible and tick-m.last_confirmed_tick>1:self._materialize(m);m.confidence*=1-self.settings.memory_contradiction_rate;m.contradictions+=1;m.status=self._status(m);self.contradiction_count+=1
        if self.world_time_seconds is None:
            for m in self.structures.values():m.confidence*=self.settings.memory_confidence_decay;m.status=self._status(m)
        return active

    @staticmethod
    def _status(m)->str:
        return "CONTRADICTED" if m.contradictions and m.confidence<.35 else "CONFIDENT" if m.confidence>=.7 else "UNCERTAIN" if m.confidence>=.35 else "WEAK"

    def _reconcile(self,place,graph)->None:
        for other in self.places.values():
            if other.id==place.id or other.id in place.aliases:continue
            visual=max((_similarity(a,_rotate(b,r)) for a in place.views for b in other.views for r in range(4)),default=0.)
            route=any((p==place.id and q==other.id) or (p==other.id and q==place.id) for p,_,q in self.transitions)
            if visual>.86 and route and min(place.visits,other.visits)>=3:
                place.aliases.add(other.id);other.aliases.add(place.id);self.alias_reconciliations+=1
                for source,target in ((place,other),(other,place)):
                    relation,_=graph.connect(source.cognit_id,target.cognit_id,RelationType.ASSOCIATIVE);relation.strength=relation.prediction_probability=min(source.confidence,target.confidence);relation.confidence=relation.strength

    def _match_structure_legacy(self,features,state,place_id,tick,excluded=None):
        best=None;score=0.;fs=set(features)
        for m in self.structures.values():
            if excluded and m.id in excluded:continue
            feature=len(fs&set(m.feature_signature))/max(1,len(fs|set(m.feature_signature)));state_score=sum(a==b for a,b in zip(state,m.remembered_state))/max(1,max(len(state),len(m.remembered_state)))
            value=.5*feature+.16*state_score+(.18 if m.place_cognit_id==place_id else 0)+.08*exp(-(tick-m.last_confirmed_tick)/128)+.08*m.confidence
            if value>score:best,score=m,value
        return best if best and score>=self.settings.memory_match_threshold+(1-best.confidence)*.08 else None

    def _match_structure(self,features,state,place_id,tick,excluded=None):
        self._ensure_indexes();candidate_ids=set(self._by_place.get(place_id,()))
        for feature in set(features):candidate_ids.update(self._by_feature.get(feature,()))
        for position,value in enumerate(state):candidate_ids.update(self._by_state.get((position,value),()))
        self.last_retrieval_candidates=len(candidate_ids);self.last_retrieval_total=len(self.structures)
        best=None;score=0.;fs=set(features)
        for memory_id in sorted(candidate_ids,key=self._index_order.__getitem__):
            m=self.structures[memory_id]
            self._materialize(m)
            if excluded and m.id in excluded:continue
            feature=len(fs&set(m.feature_signature))/max(1,len(fs|set(m.feature_signature)));state_score=sum(a==b for a,b in zip(state,m.remembered_state))/max(1,max(len(state),len(m.remembered_state)))
            value=.5*feature+.16*state_score+(.18 if m.place_cognit_id==place_id else 0)+.08*self._recency(m,tick,128)+.08*m.confidence
            if value>score:best,score=m,value
        return best if best and score>=self.settings.memory_match_threshold+(1-best.confidence)*.08 else None

    def recall(self,goal_target_ids,graph,tick:int,target_structure=None)->set[int]:
        if not self.enabled:self.last_recalled={};return set()
        self._ensure_indexes();recalled=set();self.last_recalled={};associated=set(goal_target_ids);target_request=target_structure is not None
        for target in goal_target_ids:
            associated.update(graph.outgoing_targets(target) if hasattr(graph,"outgoing_targets") else (r.target_id for r in graph.outgoing(target)))
        if target_request:candidate_ids=set(self.structures)
        else:
            candidate_ids=set()
            for cognit_id in associated:candidate_ids.update(self._by_cognit.get(cognit_id,()));candidate_ids.update(self._by_place.get(cognit_id,()))
        for memory_id in self._nonzero_recall_ids-candidate_ids:self.structures[memory_id].last_recall_strength=0.
        place_groups={place_id:[self.structures[i] for i in sorted(ids,key=self._index_order.__getitem__)] for place_id,ids in self._by_place.items()} if target_request else {}
        structural_by_place={}
        self.last_retrieval_candidates=len(candidate_ids);self.last_retrieval_total=len(self.structures)
        nonzero=set()
        for memory_id in sorted(candidate_ids,key=self._index_order.__getitem__):
            m=self.structures[memory_id]
            self._materialize(m)
            relevance=1. if m.cognit_id in associated else .35 if m.place_cognit_id in associated else 0.
            if target_request:
                from .relational import memory_structure
                group=place_groups[m.place_cognit_id]
                if m.place_cognit_id not in structural_by_place:structural_by_place[m.place_cognit_id]=memory_structure(group).match(target_structure)
                structural=structural_by_place[m.place_cognit_id];role_support=min(1.,len(group)/max(1,target_structure.participant_count));relevance=max(relevance,.1+.65*structural+.25*role_support)
            strength=relevance*m.confidence*(.5+.5*self._recency(m,tick,256));m.last_recall_strength=strength
            if strength:nonzero.add(m.id)
            if strength>=.12:m.reactivations+=1;self.reactivation_count+=1;self.last_recalled[m.id]=strength;recalled|={m.cognit_id,m.place_cognit_id}
        self._nonzero_recall_ids=nonzero
        return recalled

    def recall_legacy_result(self,goal_target_ids,graph,tick:int,target_structure=None):
        associated=set(goal_target_ids)
        for target in goal_target_ids:associated.update(graph.outgoing_targets(target) if hasattr(graph,"outgoing_targets") else (r.target_id for r in graph.outgoing(target)))
        recalled=set();strengths={};target_request=target_structure is not None
        for m in self.structures.values():
            relevance=1. if m.cognit_id in associated else .35 if m.place_cognit_id in associated else 0.
            if target_request:
                from .relational import memory_structure
                group=[x for x in self.structures.values() if x.place_cognit_id==m.place_cognit_id];structural=memory_structure(group).match(target_structure);role_support=min(1.,len(group)/max(1,target_structure.participant_count));relevance=max(relevance,.1+.65*structural+.25*role_support)
            strength=relevance*m.confidence*(.5+.5*exp(-(tick-m.last_confirmed_tick)/256));strengths[m.id]=strength
            if strength>=.12:recalled|={m.cognit_id,m.place_cognit_id}
        return recalled,strengths

    def to_dict(self)->dict:
        from dataclasses import asdict
        places=[]
        for p in self.places.values():d=asdict(p);d["aliases"]=sorted(p.aliases);places.append(d)
        return {"places":places,"structures":[asdict(x) for x in self.structures.values()],"place_evidence":[[list(k[0]),k[1],k[2],v] for k,v in self.place_evidence.items()],"transitions":[[*k,v] for k,v in self.transitions.items()],"feature_seen":[[list(k),v] for k,v in self.feature_seen.items()],"feature_change":[[list(k),v] for k,v in self.feature_change.items()],"next_place_id":self.next_place_id,"next_memory_id":self.next_memory_id,"current_place_id":self.current_place_id,"reactivation_count":self.reactivation_count,"confirmation_count":self.confirmation_count,"contradiction_count":self.contradiction_count,"alias_reconciliations":self.alias_reconciliations,"world_time_seconds":self.world_time_seconds}

    def restore(self,data:dict)->None:
        self.places={x["id"]:PlaceMemory(**{**x,"signature":tuple(tuple(v) for v in x["signature"]),"views":[tuple(tuple(v) for v in view) for view in x.get("views",[x["signature"]])],"aliases":set(x.get("aliases",[]))}) for x in data.get("places",[])}
        self.structures={x["id"]:PersistentStructureMemory(**{**x,"feature_signature":tuple(tuple(v) for v in x["feature_signature"]),"relative_context":tuple(x["relative_context"]),"remembered_state":tuple(x["remembered_state"])}) for x in data.get("structures",[])}
        raw=data.get("place_evidence",[]);self.place_evidence=Counter({(tuple(tuple(v) for v in a),b,c):n for a,b,c,n in raw}) if raw and len(raw[0])==4 else Counter()
        self.transitions=Counter({tuple(x[:3]):x[3] for x in data.get("transitions",[])});self.feature_seen=Counter({tuple(k):v for k,v in data.get("feature_seen",[])});self.feature_change=Counter({tuple(k):v for k,v in data.get("feature_change",[])})
        for key in ("next_place_id","next_memory_id","current_place_id","reactivation_count","confirmation_count","contradiction_count","alias_reconciliations"):setattr(self,key,data.get(key,getattr(self,key)))
        self.world_time_seconds=data.get("world_time_seconds")
        self._rebuild_indexes();self._nonzero_recall_ids={m.id for m in self.structures.values() if m.last_recall_strength}
