from dataclasses import dataclass,field
from math import exp,sqrt
from world.actions import ActionType
from .patterns import SensoryPrimitive


@dataclass(frozen=True,slots=True)
class LocalPercept:
    internal_temp_id:int
    participants:tuple[tuple[int,int,str,int,int],...]
    centroid:tuple[float,float]
    spatial_extent:tuple[int,int]
    primitive_signature:frozenset[tuple[str,int]]
    state_signature:tuple[int,...]
    confidence:float


@dataclass(slots=True)
class PersistentPercept:
    id:int;participants:tuple[tuple[int,int,str,int,int],...];centroid:tuple[float,float]
    primitive_signature:frozenset[tuple[str,int]];state_signature:tuple[int,...];confidence:float
    age:int=1;missing_ticks:int=0;last_seen_tick:int=0;closed:bool=False


@dataclass(slots=True)
class OnlineShift:
    mean_dx:float=0.;mean_dy:float=0.;m2_dx:float=0.;m2_dy:float=0.;support:int=0
    def update(self,dx:float,dy:float)->None:
        self.support+=1;ddx=dx-self.mean_dx;ddy=dy-self.mean_dy;self.mean_dx+=ddx/self.support;self.mean_dy+=ddy/self.support
        self.m2_dx+=ddx*(dx-self.mean_dx);self.m2_dy+=ddy*(dy-self.mean_dy)
    @property
    def variance(self)->float:return (self.m2_dx+self.m2_dy)/max(1,2*(self.support-1)) if self.support>1 else 4.0


class SensorimotorTransformModel:
    def __init__(self,min_support:int,prior_variance:float)->None:
        self.min_support=min_support;self.prior_variance=prior_variance;self.stats={a:OnlineShift() for a in ActionType}
    def update(self,action:ActionType|None,dx:float,dy:float)->None:
        if action is not None:self.stats[action].update(dx,dy)
    def estimate(self,action:ActionType|None)->tuple[float,float,float,float]:
        if action is None:return 0.,0.,self.prior_variance,0.
        stat=self.stats[action];confidence=stat.support/(stat.support+self.min_support)
        return stat.mean_dx,stat.mean_dy,max(stat.variance,0.05),confidence
    def to_dict(self)->dict:
        return {a.name:{"mean_dx":s.mean_dx,"mean_dy":s.mean_dy,"m2_dx":s.m2_dx,"m2_dy":s.m2_dy,"support":s.support} for a,s in self.stats.items()}
    def restore(self,data:dict)->None:
        for name,raw in data.items():self.stats[ActionType[name]]=OnlineShift(**raw)


class PerceptualContinuityEngine:
    def __init__(self,settings)->None:
        self.settings=settings;self.transforms=SensorimotorTransformModel(settings.sensorimotor_min_support,settings.sensorimotor_prior_variance)
        self.tracks:dict[int,PersistentPercept]={};self.next_track_id=1;self.created_total=0;self.closed_total=0;self.last_created=0;self.last_closed=0
        self.last_local:tuple[LocalPercept,...]=();self.last_continuity_error=0.;self.last_match_count=0;self.completed_lifetimes:list[int]=[]

    def local_percepts(self,events:tuple[SensoryPrimitive,...])->tuple[LocalPercept,...]:
        carriers=[e for e in events if e.channel in {"occupied","appearance"}]
        occupied_positions={(e.relative_x,e.relative_y) for e in carriers if e.value}
        if not carriers:occupied_positions={(e.relative_x,e.relative_y) for e in events}
        relevant=[e for e in events if (e.relative_x,e.relative_y) in occupied_positions and e.channel not in {"self","boundary"}]
        # Spatially adjacent occupied structures are separate persistent participants;
        # channels at the same sensory position remain one local percept.
        positions={(e.relative_x,e.relative_y) for e in relevant};groups=[{position} for position in sorted(positions)]
        result=[]
        for index,group in enumerate(sorted(groups,key=lambda g:min(g))):
            members=tuple(e for e in relevant if (e.relative_x,e.relative_y) in group);xs=[e.relative_x for e in members];ys=[e.relative_y for e in members]
            result.append(LocalPercept(index,tuple(e.structural_key() for e in members),(sum(xs)/len(xs),sum(ys)/len(ys)),
              (max(xs)-min(xs)+1,max(ys)-min(ys)+1),frozenset((e.channel,e.value) for e in members),tuple(sorted(e.value for e in members)),1.0))
        self.last_local=tuple(result);return self.last_local

    def continuity_score(self,track:PersistentPercept,local:LocalPercept,action:ActionType|None)->float:
        union=track.primitive_signature|local.primitive_signature;feature=len(track.primitive_signature&local.primitive_signature)/max(1,len(union))
        structure=min(len(track.participants),len(local.participants))/max(1,max(len(track.participants),len(local.participants)))
        state=sum(a==b for a,b in zip(track.state_signature,local.state_signature))/max(1,max(len(track.state_signature),len(local.state_signature)))
        if feature==0.0 and state==0.0:return 0.0
        dx,dy,var,confidence=self.transforms.estimate(action);expected=(track.centroid[0]+dx,track.centroid[1]+dy)
        distance=sqrt((local.centroid[0]-expected[0])**2+(local.centroid[1]-expected[1])**2);scale=self.settings.percept_spatial_scale+sqrt(var)*(1-confidence)
        spatial=exp(-distance/max(scale,1e-6));temporal=exp(-track.missing_ticks/max(1,self.settings.percept_persistence_window))
        return (self.settings.percept_feature_weight*feature+self.settings.percept_spatial_weight*spatial+
          self.settings.percept_structure_weight*structure+self.settings.percept_state_weight*state+self.settings.percept_temporal_weight*temporal)

    def update(self,events:tuple[SensoryPrimitive,...],tick:int,previous_action:ActionType|None)->tuple[PersistentPercept,...]:
        self.last_created=self.last_closed=0;locals_=self.local_percepts(events);open_tracks=[t for t in self.tracks.values() if not t.closed]
        pairs=sorted(((self.continuity_score(t,o,previous_action),t,o) for t in open_tracks for o in locals_),key=lambda x:x[0],reverse=True)
        used_tracks:set[int]=set();used_locals:set[int]=set();scores=[]
        for score,track,local in pairs:
            if score<self.settings.percept_continuity_threshold or track.id in used_tracks or local.internal_temp_id in used_locals:continue
            old=track.centroid;self.transforms.update(previous_action,local.centroid[0]-old[0],local.centroid[1]-old[1])
            track.participants=local.participants;track.centroid=local.centroid;track.primitive_signature=local.primitive_signature;track.state_signature=local.state_signature
            track.confidence=min(1.,.8*track.confidence+.2*score);track.age+=1;track.missing_ticks=0;track.last_seen_tick=tick
            used_tracks.add(track.id);used_locals.add(local.internal_temp_id);scores.append(score)
        for track in open_tracks:
            if track.id not in used_tracks:
                track.missing_ticks+=1;track.age+=1;track.confidence*=self.settings.percept_confidence_decay
                if track.missing_ticks>self.settings.percept_persistence_window:
                    track.closed=True;self.closed_total+=1;self.last_closed+=1;self.completed_lifetimes.append(track.age)
                    self.tracks.pop(track.id,None)
        for local in locals_:
            if local.internal_temp_id in used_locals:continue
            track=PersistentPercept(self.next_track_id,local.participants,local.centroid,local.primitive_signature,local.state_signature,local.confidence,last_seen_tick=tick)
            self.tracks[track.id]=track;self.next_track_id+=1;self.created_total+=1;self.last_created+=1
        self.last_match_count=len(scores);self.last_continuity_error=1-sum(scores)/len(scores) if scores else (0. if not locals_ and not open_tracks else .5)
        return tuple(t for t in self.tracks.values() if not t.closed)
