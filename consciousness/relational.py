from __future__ import annotations
from dataclasses import dataclass,field
from itertools import combinations,permutations
from math import gcd

RelationToken=tuple[int,int,int]

def _token(a,b)->RelationToken:
    dx=int(round(b[0]-a[0]));dy=int(round(b[1]-a[1]));g=max(1,gcd(abs(dx),abs(dy)));return (dx//g,dy//g,min(3,abs(dx)+abs(dy)))

def _canonical(tokens):
    tokens=list(tokens);variants=[]
    for mirror in (1,-1):
        current=[(x*mirror,y,d) for x,y,d in tokens]
        for _ in range(4):
            variants.append(tuple(sorted(current)));current=[(-y,x,d) for x,y,d in current]
    return min(variants,default=())

@dataclass(frozen=True,slots=True)
class RelationalStructure:
    participant_count:int;relations:tuple[RelationToken,...];confidence:float=1.;source_cognits:tuple[int,...]=();role_edges:tuple[tuple[int,int,RelationToken],...]=()

    @classmethod
    def from_points(cls,points,confidence=1.,source_cognits=()):
        points=tuple(sorted(points));edges=tuple((i,j,_token(points[i],points[j])) for i,j in combinations(range(len(points)),2));return cls(len(points),_canonical(e[2] for e in edges),confidence,tuple(source_cognits),edges)

    def match(self,other:"RelationalStructure")->float:
        if not self.relations and not other.relations:return float(self.participant_count==other.participant_count)
        a=list(self.relations);b=list(other.relations);hits=0
        for token in a:
            if token in b:hits+=1;b.remove(token)
        relation=hits/max(1,max(len(self.relations),len(other.relations)));roles=min(self.participant_count,other.participant_count)/max(1,max(self.participant_count,other.participant_count))
        return (.8*relation+.2*roles)*min(self.confidence,other.confidence)

def current_structure(tracks)->RelationalStructure:
    relevant=[t for t in tracks if any(ch in {"occupied","appearance","state"} for ch,_ in t.primitive_signature)]
    return RelationalStructure.from_points((t.centroid for t in relevant),sum(t.confidence for t in relevant)/max(1,len(relevant)),(t.id for t in relevant))

def observed_structure(observation)->RelationalStructure:
    points=sorted({(x,y) for x,y,ch,val,_ in observation if ch=="occupied" and val})
    return RelationalStructure.from_points(points)

def memory_structure(memories)->RelationalStructure:
    memories=tuple(memories);return RelationalStructure.from_points((m.relative_context for m in memories),sum(m.confidence for m in memories)/max(1,len(memories)),(m.cognit_id for m in memories))

@dataclass(slots=True)
class ParticipantBelief:
    cognit_id:int;relative_position:tuple[float,float];place_cognit_id:int;confidence:float;last_seen_world_tick:int;visible:bool=True;episode:int=0

@dataclass(slots=True)
class BoundSpatialRelation:
    cognit_id:int;source_id:int;target_id:int;token:RelationToken;confidence:float;last_observed_world_tick:int;support:int=1;contradictions:int=0;provenance:str="CO_OBSERVED"

@dataclass(frozen=True,slots=True)
class RoleBinding:
    role_to_participant:tuple[int,...];score:float;unresolved_roles:int;satisfied:int=0;violated:int=0;unknown:int=0

def _transform_token(token,index):
    x,y,d=token
    if index>=4:x=-x
    for _ in range(index%4):x,y=-y,x
    return x,y,d

class BeliefScene:
    """Persistent participant-bound relational belief derived only from memory/perception."""
    def __init__(self):self.participants={};self.relations={};self.last_binding=RoleBinding((),0.,0);self.knowledge_uncertainty=1.;self.episode=0
    def new_episode(self):self.episode+=1;self.last_binding=RoleBinding((),0.,0);[setattr(p,"visible",False) for p in self.participants.values()]
    def update(self,memories,current_place_cognit,tick,graph,relational_nodes):
        for participant in self.participants.values():participant.visible=False
        visible=[]
        for m in memories:
            if m.last_confirmed_tick!=tick:continue
            p=self.participants.get(m.cognit_id) or ParticipantBelief(m.cognit_id,m.relative_context,m.place_cognit_id,m.confidence,tick)
            p.relative_position=m.relative_context;p.place_cognit_id=m.place_cognit_id;p.confidence=m.confidence;p.last_seen_world_tick=tick;p.visible=True;p.episode=self.episode;self.participants[p.cognit_id]=p;visible.append(p)
        groups={}
        for p in visible:groups.setdefault(p.place_cognit_id,[]).append(p)
        for group in groups.values():
            for a,b in combinations(sorted(group,key=lambda x:x.cognit_id),2):
                token=_token(a.relative_position,b.relative_position);key=(a.cognit_id,b.cognit_id,token);confidence=min(a.confidence,b.confidence);bound=self.relations.get(key)
                for old_key,old in self.relations.items():
                    if old.source_id==a.cognit_id and old.target_id==b.cognit_id and old.token!=token:
                        old.contradictions+=1;old.confidence*=.8
                if bound is None:
                    from .cognit import Cognit
                    bound=BoundSpatialRelation(graph.add_cognit(Cognit(graph.next_id,kind="BOUND_RELATION",confidence=confidence)).id,a.cognit_id,b.cognit_id,token,confidence,tick);self.relations[key]=bound
                bound.confidence=min(1.,max(bound.confidence,confidence)+.04);bound.support+=1;bound.last_observed_world_tick=tick
                token_id=relational_nodes.get(token)
                if token_id is None:
                    from .cognit import Cognit
                    token_id=graph.add_cognit(Cognit(graph.next_id,kind="RELATIONAL",confidence=confidence)).id;relational_nodes[token]=token_id
                from .relation import RelationType
                relation,_=graph.connect(a.cognit_id,b.cognit_id,RelationType.SPATIAL,token_id);relation.strength=relation.prediction_probability=confidence;relation.confidence=confidence;relation.support+=int(a.visible and b.visible);relation.last_evidence_world_tick=tick
                graph.connect(a.cognit_id,bound.cognit_id,RelationType.ASSOCIATIVE);graph.connect(bound.cognit_id,b.cognit_id,RelationType.SPATIAL,token_id)
        self.knowledge_uncertainty=1-sum(p.confidence for p in self.participants.values())/max(1,len(self.participants))
        return {r.cognit_id for r in self.relations.values() if r.last_observed_world_tick==tick}
    def _known_edge(self,source,target):
        a_current=self.participants.get(source);b_current=self.participants.get(target)
        if a_current and b_current and a_current.episode==self.episode and b_current.episode==self.episode and a_current.last_seen_world_tick==b_current.last_seen_world_tick and a_current.place_cognit_id==b_current.place_cognit_id:
            return _token(a_current.relative_position,b_current.relative_position),min(a_current.confidence,b_current.confidence)
        reverse=source>target;a,b=(target,source) if reverse else (source,target);candidates=[r for r in self.relations.values() if r.source_id==a and r.target_id==b and r.confidence>.1]
        if not candidates:return None
        relation=max(candidates,key=lambda r:(r.confidence,r.support,-r.contradictions,r.last_observed_world_tick));x,y,d=relation.token;return ((-x,-y,d) if reverse else relation.token),relation.confidence
    def best_binding(self,target:RelationalStructure,participant_ids=None,update_last=True)->RoleBinding:
        eligible={i for i,p in self.participants.items() if p.episode==self.episode};n=target.participant_count;participants=sorted((set(participant_ids)&eligible) if participant_ids is not None else eligible)
        if len(participants)<n:
            binding=RoleBinding(tuple(participants),0.,n-len(participants))
            if update_last:self.last_binding=binding
            return binding
        best=RoleBinding((),0.,n)
        edges=target.role_edges or tuple((i,j,t) for (i,j),t in zip(combinations(range(n),2),target.relations))
        for assignment in permutations(participants,n):
            for transform in range(8):
                sat=viol=unknown=0
                for ri,rj,wanted in edges:
                    known=self._known_edge(assignment[ri],assignment[rj])
                    if known is None:unknown+=1
                    elif known[0]==_transform_token(wanted,transform):sat+=1
                    else:viol+=1
                score=sat/max(1,len(edges));candidate=RoleBinding(tuple(assignment),score,0,sat,viol,unknown)
                if (candidate.score,-candidate.unresolved_roles,-candidate.unknown,-candidate.violated,tuple(-x for x in candidate.role_to_participant))>(best.score,-best.unresolved_roles,-best.unknown,-best.violated,tuple(-x for x in best.role_to_participant)):best=candidate
        if update_last:self.last_binding=best
        return best
    def mismatch(self,target):return 1-self.best_binding(target).score
    def predicted_mismatch(self,target,predicted_cognits):
        predicted=[r for r in self.relations.values() if r.cognit_id in predicted_cognits]
        participants={x for r in predicted for x in (r.source_id,r.target_id)}
        if len(participants)<target.participant_count:return self.mismatch(target)
        edges=target.role_edges or tuple((i,j,t) for (i,j),t in zip(combinations(range(target.participant_count),2),target.relations));best=0.
        by_endpoints={}
        for relation in predicted:by_endpoints.setdefault((relation.source_id,relation.target_id),[]).append(relation.token)
        for assignment in permutations(sorted(participants),target.participant_count):
            for transform in range(8):
                hits=0
                for ri,rj,wanted in edges:
                    source,target_id=assignment[ri],assignment[rj];reverse=source>target_id;a,b=(target_id,source) if reverse else (source,target_id)
                    known=by_endpoints.get((a,b),());expected=_transform_token(wanted,transform)
                    if reverse:expected=(-expected[0],-expected[1],expected[2])
                    hits+=expected in known
                best=max(best,hits/max(1,len(edges)))
        return 1-best
    def to_dict(self):
        from dataclasses import asdict
        return {"participants":[asdict(x) for x in self.participants.values()],"relations":[asdict(x) for x in self.relations.values()],"knowledge_uncertainty":self.knowledge_uncertainty,"episode":self.episode}
    def restore(self,data):
        self.participants={x["cognit_id"]:ParticipantBelief(**{**x,"relative_position":tuple(x["relative_position"])}) for x in data.get("participants",[])};self.relations={(x["source_id"],x["target_id"],tuple(x["token"])):BoundSpatialRelation(**{**x,"token":tuple(x["token"])}) for x in data.get("relations",[])};self.knowledge_uncertainty=data.get("knowledge_uncertainty",1.);self.episode=data.get("episode",0)
