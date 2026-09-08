from collections import deque
from dataclasses import dataclass,field
from functools import lru_cache
from world.actions import ActionType


@dataclass(slots=True)
class Goal:
    id:int;target_cognit_ids:tuple[int,...];activation_direction:float;intensity:float;confidence:float
    age:int=0;persistence:float=0.85;origin_tension:float=0.0;target_last_seen:int=0;unavailable_ticks:int=0;status:str="ACTIVE"
    parent_id:int|None=None;depth:int=0;origin:str="INTRINSIC";target_signature:tuple=()
    created_time_seconds:float|None=None;last_touch_time_seconds:float|None=None;unavailable_since_seconds:float|None=None;cooldown_until_seconds:float|None=None


@dataclass(frozen=True,slots=True)
class FutureEstimate:
    probabilities:dict[int,float];confidence:float;expected_novelty:float;goal_alignment:float
    information_gain:float;controllability_gain:float;loop_risk:float;score:float=0.0


@dataclass(frozen=True,slots=True)
class TraceEntry:
    tick:int;active:tuple[tuple[int,float],...];action:ActionType;prediction:tuple[tuple[int,float],...]
    prediction_error:float;goal_id:int|None;internal_tension:float;percept_ids:tuple[int,...]=();representation_error:float=0.0
    @property
    def signature(self)->frozenset[int]:return _trace_signature(self.active)

@lru_cache(maxsize=8192)
def _trace_signature(active:tuple[tuple[int,float],...])->frozenset[int]:return frozenset(i for i,_ in active)


class WorkingTrace:
    def __init__(self,capacity:int)->None:self.entries:deque[TraceEntry]=deque(maxlen=capacity);self._loop_cache={}
    def append(self,entry:TraceEntry)->None:self.entries.append(entry);self._loop_cache.clear()
    @staticmethod
    def similarity(a:TraceEntry,b:TraceEntry)->float:
        cognit=len(a.signature&b.signature)/max(1,len(a.signature|b.signature));percepts_a=set(a.percept_ids);percepts_b=set(b.percept_ids)
        if cognit==0.0:return 0.0
        percept=len(percepts_a&percepts_b)/max(1,len(percepts_a|percepts_b)) if percepts_a or percepts_b else 1.0
        action=float(a.action is b.action);goal=float(a.goal_id==b.goal_id);error=max(0.,1-abs(a.prediction_error-b.prediction_error));representation=max(0.,1-abs(a.representation_error-b.representation_error));tension=max(0.,1-abs(a.internal_tension-b.internal_tension))
        return .35*cognit+.15*percept+.15*action+.10*goal+.075*error+.075*representation+.10*tension
    def loop_score(self,candidate:frozenset[int]|TraceEntry|None=None,max_period:int=8,min_repeats:int=3)->float:
        key=(candidate,max_period,min_repeats)
        cached=self._loop_cache.get(key)
        if cached is not None:return cached
        entries=list(self.entries)
        if isinstance(candidate,TraceEntry):entries.append(candidate)
        elif candidate is not None:
            entries.append(TraceEntry(-1,tuple((i,1.) for i in candidate),entries[-1].action if entries else ActionType.IDLE,(),0.,None,0.))
        best=0.0
        for period in range(1,min(max_period,len(entries)//min_repeats)+1):
            comparisons=[]
            for repeat in range(1,min_repeats):
                a=entries[-1-repeat*period];b=entries[-1-(repeat-1)*period]
                comparisons.append(self.similarity(a,b))
            if comparisons:best=max(best,sum(comparisons)/len(comparisons))
        self._loop_cache[key]=best
        return best


@dataclass(slots=True)
class ConsciousnessState:
    prediction_error:float=0.0;prediction_error_valid:bool=False;representation_coverage:float=0.0;representation_error:float=0.0
    continuity_error:float=0.0;overall_surprise:float=0.0;brier_score:float=0.0;ece:float=0.0
    novelty:float=0.0;uncertainty:float=1.0;controllability:float=0.0
    agency_estimate:float=0.0;pattern_selectivity:float=0.0;representation_quality:float=0.0
    internal_tension:float=0.0;loop_score:float=0.0;goal:Goal|None=None
    predictions:dict[int,float]=field(default_factory=dict);futures:dict[ActionType,FutureEstimate]=field(default_factory=dict)
    action_scores:dict[ActionType,float]=field(default_factory=dict);goals_generated:int=0;completed_goal_lifetimes:list[int]=field(default_factory=list)
    tie_count:int=0;tie_set:tuple[ActionType,...]=();tie_resolution_method:str="NONE";goals_retired:int=0;goals_suspended:int=0
    subgoals_created:int=0;subgoals_completed:int=0;subgoals_failed:int=0;max_goal_depth:int=0;parent_resumptions:int=0
