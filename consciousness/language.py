"""Receptive exact-symbol identity grounded in embodied Cognit provenance."""
from __future__ import annotations
from .cognit import Cognit
from .relational import RelationalStructure
from .language_types import (
    GroundingContextEntry, GroundingContextSnapshot, GroundingContextTracker,
    HistoricalGroundingContext, LanguageFrame, LanguageProcessingResult,
    LanguageRelationalResult, LanguageRequestResult, LanguageSemanticSlot,
    LanguageUtteranceFrame, LanguageUtteranceFrontier, LanguageUtteranceResult,
    normalize_token,
)

class LanguageLexicon:
    """Владеет identity и bounded evidence; learned meaning живёт в Relations."""
    def __init__(self,core):
        self.core=core
        self.symbols={}
        self.exposures={}
        self.grounded_trials={}
        self.evidence={}
        self.materialized={}
        self.sequence_support={}
        self.sequence_trials={}
        self.sequence_materialized={}
        self.request_concept_id=None
        self.request_support={}
        self.request_trials={}
        self.request_materialized=set()
        self.total_exposures=0
        self.grounding_relations_materialized=0
        self.sequence_relations_materialized=0
        self.last_language_symbol_id=None
        self.last_language_wave_active_ids=frozenset()
        self.outgoing_scans=0
        self.native_relation_batch_calls=0
        self.native_sequence_batch_calls=0
    def symbol(self,surface):
        surface=normalize_token(surface)
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
    def compose_relational(self,tokens,symbol_ids,token_results):
        """Resolve only meanings both learned by Pass 1 and retrieved by this token wave."""
        reverse_tokens={node_id:token for token,node_id in self.core.relational_nodes.items()}
        reverse_bound={relation.cognit_id:relation.token for relation in self.core.belief_scene.relations.values()}
        slots=[]
        for position,(token,symbol,result) in enumerate(zip(tokens,symbol_ids,token_results)):
            materialized=self.materialized.get(token,set());active=result.wave.active_ids
            candidates=[]
            for node_id in materialized & active:
                node=self.core.graph.nodes.get(node_id)
                if node is None or node.kind in {"LANGUAGE_SYMBOL","TARGET"}:continue
                count,conditional,lift=self._metrics(token,node_id,self.core.grounding_context)
                candidates.append((node_id,count,conditional,lift,node.confidence))
            candidates.sort(key=lambda row:(-row[1],-row[2],-row[3],-row[4],row[0]))
            candidates=candidates[:self.core.settings.language_max_semantic_anchors_per_token]
            resolved=None
            if candidates:
                first=candidates[0]
                if len(candidates)==1 or first[1:4]!=candidates[1][1:4]:resolved=first[0]
            ids=tuple(row[0] for row in candidates)
            slots.append(LanguageSemanticSlot(position,symbol,ids,resolved))
        relation_candidates=[]
        for slot in slots:
            for node_id in slot.retrieved_cognit_ids:
                if node_id in reverse_tokens:relation_candidates.append((slot.token_position,node_id,reverse_tokens[node_id],0))
                elif node_id in reverse_bound:relation_candidates.append((slot.token_position,node_id,reverse_bound[node_id],1))
        relation_slots=[];tokens_found={row[2] for row in relation_candidates}
        if len(tokens_found)==1:
            token=next(iter(tokens_found));positions={row[0] for row in relation_candidates if row[2]==token}
            if len(positions)==1:
                chosen=min((row for row in relation_candidates if row[2]==token),key=lambda row:(row[3],row[1]));relation_slots=[chosen[:3]]
                position,node_id,_=relation_slots[0];slot=slots[position];slots[position]=LanguageSemanticSlot(position,slot.symbol_id,slot.retrieved_cognit_ids,node_id)
        participant_ids=set(self.core.belief_scene.participants)
        for position,slot in enumerate(slots):
            if relation_slots and position==relation_slots[0][0]:continue
            embodied=tuple(i for i in slot.retrieved_cognit_ids if i in participant_ids)
            if len(embodied)==1:slots[position]=LanguageSemanticSlot(position,slot.symbol_id,slot.retrieved_cognit_ids,embodied[0])
        unresolved=[slot.token_position for slot in slots if slot.resolved_cognit_id is None]
        provenance=[(slot.token_position,slot.resolved_cognit_id) for slot in slots if slot.resolved_cognit_id is not None]
        structure=None;confidence=0.
        if len(relation_slots)==1:
            relation_position,relation_id,relation_token=relation_slots[0]
            participants=[slot for slot in slots if slot.token_position!=relation_position and slot.resolved_cognit_id is not None and slot.resolved_cognit_id not in reverse_tokens and slot.resolved_cognit_id not in reverse_bound]
            if len(participants)>=2:
                participants=participants[:2];participant_ids=tuple(slot.resolved_cognit_id for slot in participants)
                values=[self.core.graph.nodes[i].confidence for i in participant_ids+(relation_id,)]
                confidence=min(values)
                structure=RelationalStructure.from_role_edges(participant_ids,((0,1,relation_token),),confidence)
        return LanguageRelationalResult(tuple(symbol_ids),tuple(slots),structure,confidence,tuple(unresolved),tuple(provenance))
    def learn_request(self,tokens,demonstrated):
        for token in tokens:self.request_trials[token]=self.request_trials.get(token,0)+1
        if not demonstrated:return 0
        if self.request_concept_id is None:
            if len(self.core.graph.nodes)>=self.core.settings.max_cognits:return 0
            self.request_concept_id=self.core.graph.add_cognit(Cognit(self.core.graph.next_id,kind="COMMUNICATIVE_REQUEST",confidence=1.)).id
        for token in tokens:self.request_support[token]=self.request_support.get(token,0)+1
        updates=[];s=self.core.settings
        for token in sorted(set(tokens)):
            support=self.request_support[token];trials=self.request_trials[token];probability=support/max(1,trials);confidence=support/(support+s.language_request_confidence_k)
            if support>=s.language_request_min_support and probability>=s.language_request_min_probability:
                symbol=self.symbols.get(token)
                if symbol is not None:updates.append((symbol,probability,confidence,support))
        made=0;remaining=self.core.settings.max_new_relations_per_tick
        for symbol,probability,confidence,support in updates:
            existing=any(r.target_id==self.request_concept_id and r.relation_type.name=="ASSOCIATIVE" for r in self.core.graph.outgoing(symbol))
            if existing:
                self.request_materialized.add(symbol);continue
            if remaining<=0:continue
            self.core.backend.ffi_calls+=1;self.core.backend.language_relation_batch_calls+=1;self.native_relation_batch_calls+=1
            created=self.core.backend.engine.upsert_relation_states_batch(symbol-1,[(self.request_concept_id,1,0,probability*confidence,confidence,probability,support,1.)],remaining,self.core.settings.max_relations)
            if created:made+=1;remaining-=1
            if any(r.target_id==self.request_concept_id and r.relation_type.name=="ASSOCIATIVE" for r in self.core.graph.outgoing(symbol)):self.request_materialized.add(symbol)
        return made
    def compose_request(self,relational,token_results):
        cues=[]
        if self.request_concept_id is not None:
            for result in token_results:
                if result.symbol_id in self.request_materialized and self.request_concept_id in result.wave.active_ids:cues.append(result.symbol_id)
        cues=tuple(sorted(set(cues)));confidence=0.
        for symbol in cues:
            token=next(k for k,v in self.symbols.items() if v==symbol);support=self.request_support[token];probability=support/max(1,self.request_trials[token]);confidence=max(confidence,probability*support/(support+self.core.settings.language_request_confidence_k))
        cue_positions={slot.token_position for slot in relational.semantic_slots if slot.symbol_id in cues}
        complete=relational.relational_structure is not None and not any(position not in cue_positions for position in relational.unresolved_slots)
        desired=relational.relational_structure if cues and complete else None;goal=None
        if desired is not None:goal=self.core.install_relational_goal(desired,confidence,"LANGUAGE_REQUEST")
        provenance=tuple((symbol,self.request_concept_id) for symbol in cues)
        return LanguageRequestResult(relational,confidence,cues,desired,None if goal is None else goal.id,provenance)
    @property
    def language_symbol_count(self):return len(self.symbols)
    @property
    def language_exposures(self):return self.total_exposures
    @property
    def grounding_candidates(self):return sum(map(len,self.evidence.values()))
    @property
    def sequence_candidates(self):return sum(map(len,self.sequence_support.values()))
    def to_dict(self):return {"symbols":dict(sorted(self.symbols.items())),"exposures":dict(sorted(self.exposures.items())),"grounded_trials":dict(sorted(self.grounded_trials.items())),"evidence":{k:[[i,n,m] for i,(n,m) in sorted(v.items())] for k,v in sorted(self.evidence.items())},"materialized":{k:sorted(v) for k,v in sorted(self.materialized.items())},"sequence_support":[[s,t,n] for s,rows in sorted(self.sequence_support.items()) for t,n in sorted(rows.items())],"sequence_trials":[[s,n] for s,n in sorted(self.sequence_trials.items())],"sequence_materialized":[[s,sorted(v)] for s,v in sorted(self.sequence_materialized.items())],"request_concept_id":self.request_concept_id,"request_support":dict(sorted(self.request_support.items())),"request_trials":dict(sorted(self.request_trials.items())),"request_materialized":sorted(self.request_materialized),"total_exposures":self.total_exposures,"grounding_relations_materialized":self.grounding_relations_materialized,"sequence_relations_materialized":self.sequence_relations_materialized}
    @classmethod
    def from_dict(cls,core,data):
        obj=cls(core);data=data or {};obj.symbols={str(k):int(v) for k,v in data.get("symbols",{}).items()};obj.exposures={str(k):int(v) for k,v in data.get("exposures",{}).items()};legacy="support" in data and "evidence" not in data
        obj.grounded_trials=({k:int(obj.exposures.get(k,0)) for k in obj.symbols} if legacy else {str(k):int(v) for k,v in data.get("grounded_trials",{}).items()})
        if legacy:obj.evidence={str(k):{int(i):(int(n),float(n)) for i,n in rows} for k,rows in data.get("support",{}).items()}
        else:obj.evidence={str(k):{int(i):(int(n),float(m)) for i,n,m in rows} for k,rows in data.get("evidence",{}).items()}
        obj.materialized={str(k):set(map(int,v)) for k,v in data.get("materialized",{}).items()};obj.sequence_support={};
        for s,t,n in data.get("sequence_support",[]):obj.sequence_support.setdefault(int(s),{})[int(t)]=int(n)
        obj.sequence_trials={int(s):int(n) for s,n in data.get("sequence_trials",[])};obj.sequence_materialized={int(s):set(map(int,v)) for s,v in data.get("sequence_materialized",[])};obj.request_concept_id=data.get("request_concept_id");obj.request_support={str(k):int(v) for k,v in data.get("request_support",{}).items()};obj.request_trials={str(k):int(v) for k,v in data.get("request_trials",{}).items()};obj.request_materialized=set(map(int,data.get("request_materialized",[])));obj.total_exposures=int(data.get("total_exposures",0));obj.grounding_relations_materialized=int(data.get("grounding_relations_materialized",0));obj.sequence_relations_materialized=int(data.get("sequence_relations_materialized",0));obj._legacy_grounding=({"background_mass":[[int(i),float(n)] for i,n in data.get("background",[])],"total_experience_time":float(data.get("total_exposures",0))} if legacy else None)
        if legacy or "materialized" not in data:
            for token,source in obj.symbols.items():obj.materialized[token]={r.target_id for r in core.graph.outgoing(source) if r.relation_type.name=="ASSOCIATIVE"}
        if "sequence_materialized" not in data:
            for source in obj.symbols.values():
                targets={r.target_id for r in core.graph.outgoing(source) if r.relation_type.name=="SEQUENTIAL" and r.target_id in obj.symbols.values()}
                if targets:obj.sequence_materialized[source]=targets
        return obj
    def restore_legacy_grounding(self,tracker):
        if getattr(self,"_legacy_grounding",None) is not None:tracker.restore_durable(self._legacy_grounding)
    def on_cognit_deleted(self,cognit_id):
        dead_tokens=[token for token,symbol in self.symbols.items() if symbol==cognit_id]
        for token in dead_tokens:
            self.symbols.pop(token,None);self.exposures.pop(token,None);self.grounded_trials.pop(token,None);self.evidence.pop(token,None);self.materialized.pop(token,None);self.request_support.pop(token,None);self.request_trials.pop(token,None);self.request_materialized.discard(cognit_id)
        if self.request_concept_id==cognit_id:self.request_concept_id=None;self.request_materialized.clear()
        self.sequence_support.pop(cognit_id,None);self.sequence_trials.pop(cognit_id,None);self.sequence_materialized.pop(cognit_id,None)
        for source in tuple(self.sequence_support):
            self.sequence_support[source].pop(cognit_id,None)
            if not self.sequence_support[source]:self.sequence_support.pop(source,None)
        for source in tuple(self.sequence_materialized):
            self.sequence_materialized[source].discard(cognit_id)
            if not self.sequence_materialized[source]:self.sequence_materialized.pop(source,None)
        for token in tuple(self.evidence):
            self.evidence[token].pop(cognit_id,None);self.materialized.setdefault(token,set()).discard(cognit_id)


__all__ = [
    "GroundingContextEntry", "GroundingContextSnapshot",
    "GroundingContextTracker", "HistoricalGroundingContext", "LanguageFrame",
    "LanguageLexicon", "LanguageProcessingResult", "LanguageRelationalResult",
    "LanguageRequestResult", "LanguageSemanticSlot", "LanguageUtteranceFrame",
    "LanguageUtteranceFrontier", "LanguageUtteranceResult", "normalize_token",
]
