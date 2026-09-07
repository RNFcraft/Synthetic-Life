from collections import defaultdict
from config import Settings
from world.perception import SensoryFrame
from .patterns import CognitPattern, PrimitiveKey, ProtoPattern, SensoryEventKind, SensoryPrimitive


class SensoryEventLayer:
    def __init__(self) -> None:
        self.previous: dict[tuple[int,int],tuple[bool,int,bool,int]] = {}
        self.previous_body: dict[str,int] = {}

    def decompose(self, frame: SensoryFrame) -> tuple[SensoryPrimitive,...]:
        events=[]
        for cell in frame.cells:
            pos=(cell.relative_x,cell.relative_y); prev=self.previous.get(pos,(False,0,False,0))
            if cell.occupied:
                kind=SensoryEventKind.OCCUPIED_APPEARED if not prev[0] else SensoryEventKind.OCCUPIED_PRESENT
                events.append(SensoryPrimitive(*pos,"occupied",1,int(prev[0]),kind))
            elif prev[0]: events.append(SensoryPrimitive(*pos,"occupied",0,1,SensoryEventKind.OCCUPIED_DISAPPEARED))
            if cell.state_channel != prev[1]: events.append(SensoryPrimitive(*pos,"state",cell.state_channel,prev[1],SensoryEventKind.STATE_CHANGED))
            if cell.boundary: events.append(SensoryPrimitive(*pos,"boundary",1,int(prev[2]),SensoryEventKind.BOUNDARY_PRESENT))
            if cell.appearance_channel:events.append(SensoryPrimitive(*pos,"appearance",cell.appearance_channel,prev[3],SensoryEventKind.STATE_CHANGED if cell.appearance_channel!=prev[3] else SensoryEventKind.OCCUPIED_PRESENT))
            if cell.self_present: events.append(SensoryPrimitive(*pos,"self",1,1,SensoryEventKind.SELF_CHANNEL))
            self.previous[pos]=(cell.occupied,cell.state_channel,cell.boundary,cell.appearance_channel)
        body_values={"touch_up":int(frame.body.touch_up),"touch_down":int(frame.body.touch_down),"touch_left":int(frame.body.touch_left),
                     "touch_right":int(frame.body.touch_right),"holding":int(frame.body.holding),"resistance":int(frame.body.action_resistance>0)}
        for channel,value in body_values.items():
            previous=self.previous_body.get(channel,0)
            # Body channels are ordinary primitives and never name physical causes.
            events.append(SensoryPrimitive(0,0,f"body_{channel}",value,previous,SensoryEventKind.STATE_CHANGED if value!=previous else SensoryEventKind.OCCUPIED_PRESENT))
        self.previous_body=body_values
        return tuple(events)


class SensoryPatternTracker:
    """Indexes small local event structures; whole-frame signatures are debug-only."""
    def __init__(self, settings: Settings) -> None:
        self.settings=settings; self.layer=SensoryEventLayer(); self.prototypes:dict[tuple[tuple[PrimitiveKey,...],bool],ProtoPattern]={}
        self.legacy_last_frame: object|None=None
        self.last_events:tuple[SensoryPrimitive,...]=()

    def observe(self,frame:SensoryFrame,known_coverage:float,predicted:dict[int,float])->tuple[frozenset[PrimitiveKey],list[tuple[ProtoPattern,float]]]:
        primitives=self.layer.decompose(frame);self.last_events=primitives;observation=frozenset(p.structural_key() for p in primitives)
        candidates:set[tuple[tuple[PrimitiveKey,...],bool]]={((key,),False) for key in observation}
        by_anchor:dict[tuple[int,int],list[PrimitiveKey]]=defaultdict(list)
        for key in observation: by_anchor[(key[0],key[1])].append(key)
        for values in by_anchor.values():
            if len(values)>1:candidates.add((tuple(sorted(values))[:3],False))
        movable=sorted(k for k in observation if k[2] not in {"self","boundary"})
        if movable:
            ax,ay=movable[0][:2];normalized=tuple((x-ax,y-ay,ch,val,change) for x,y,ch,val,change in movable[:3])
            candidates.add((normalized,True))
        results=[]
        # Candidate semantics are set-like, but birth quotas and floating
        # evidence updates make traversal order behavior-affecting.
        for signature,tolerant in sorted(candidates,key=lambda item:(item[1],item[0])):
            proto=self.prototypes.setdefault((signature,tolerant),ProtoPattern(signature,translation_tolerant=tolerant)); proto.occurrences+=1; proto.stable_observations+=1
            proto.explained_sum+=known_coverage; proto.prediction_trials+=1
            proto.predicted_hits+=max(predicted.values(),default=0.0) if all(x in observation for x in signature) else 0.0
            proto.last_tick=frame.tick
            frequency=min(1.0,proto.occurrences/self.settings.proto_min_occurrences)
            prediction_gain=1.0-proto.predictive_value; compression=min(1.0,(len(signature)*proto.occurrences)/12.0)
            score=(self.settings.pattern_frequency_weight*frequency+self.settings.pattern_stability_weight*proto.stability+
                self.settings.pattern_prediction_weight*prediction_gain+self.settings.pattern_compression_weight*compression-
                self.settings.pattern_redundancy_weight*proto.redundancy)
            results.append((proto,max(0.0,min(1.0,score))))
        self.legacy_last_frame=frame.signature()
        return observation,results
