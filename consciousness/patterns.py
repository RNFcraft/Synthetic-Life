from dataclasses import dataclass
from enum import Enum, auto


class SensoryEventKind(Enum):
    OCCUPIED_PRESENT = auto()
    OCCUPIED_APPEARED = auto()
    OCCUPIED_DISAPPEARED = auto()
    STATE_CHANGED = auto()
    BOUNDARY_PRESENT = auto()
    SELF_CHANNEL = auto()


@dataclass(frozen=True, slots=True, order=True)
class SensoryPrimitive:
    relative_x: int
    relative_y: int
    channel: str
    value: int
    previous_value: int
    change: SensoryEventKind

    def structural_key(self) -> tuple[int, int, str, int, int]:
        return self.relative_x, self.relative_y, self.channel, self.value, self.change.value


PrimitiveKey = tuple[int, int, str, int, int]


@dataclass(slots=True)
class OnlineSpatialConstraint:
    mean:float=0.;m2:float=0.;support:int=0
    def update(self,value:float)->None:
        self.support+=1;delta=value-self.mean;self.mean+=delta/self.support;self.m2+=delta*(value-self.mean)
    @property
    def variance(self)->float:return self.m2/max(1,self.support-1)
    def match(self,value:float,epsilon:float=.25)->float:
        from math import exp,sqrt
        return exp(-abs(value-self.mean)/max(sqrt(self.variance),epsilon))


class PatternParticipantType(Enum):
    PRIMITIVE=auto();COGNIT=auto();PERCEPT_ROLE=auto()


class PatternRelationType(Enum):
    SAME_TIME=auto();BEFORE=auto();AFTER=auto();SPATIAL_OFFSET=auto();PERSISTENCE=auto();ACTION_CONTEXT=auto()


@dataclass(frozen=True,slots=True)
class PatternNode:
    participant_type:PatternParticipantType;reference:object;role:str|None=None


@dataclass(frozen=True,slots=True)
class PatternRelation:
    source:int;target:int;relation_type:PatternRelationType;expected_delta_t:int=0;time_tolerance:int=0
    spatial_mean:tuple[float,float]=(0.,0.);spatial_variance:float=0.


@dataclass(slots=True)
class CognitPattern:
    participants: tuple[PrimitiveKey, ...]
    relative_relationships: tuple[tuple[int, int], ...] = ()
    temporal_order: tuple[int, ...] = ()
    tolerance: float = 0.25
    occurrence_count: int = 1
    stability: float = 0.5
    predictive_value: float = 0.0
    nodes: tuple[PatternNode,...] = ()
    relations: tuple[PatternRelation,...] = ()
    compression_gain: float = 0.0
    redundancy: float = 0.0
    abstraction_depth: int = 0
    is_translation_tolerant: bool = False
    positive_match_mean: float = 0.0
    background_match_mean: float = 0.0
    selectivity_trials: int = 0

    @property
    def signature(self) -> tuple[PrimitiveKey, ...]: return self.participants
    @property
    def occurrences(self) -> int: return self.occurrence_count
    @occurrences.setter
    def occurrences(self, value: int) -> None: self.occurrence_count = value

    def match(self, observation: frozenset[PrimitiveKey]) -> float:
        if not self.is_translation_tolerant:return sum(p in observation for p in self.participants)/max(1,len(self.participants))
        if not self.participants:return 0.0
        observed=list(observation);best=0.0
        for anchor in observed:
            first=self.participants[0]
            if anchor[2:]!=first[2:]:continue
            dx,dy=anchor[0]-first[0],anchor[1]-first[1]
            hits=sum((p[0]+dx,p[1]+dy,*p[2:]) in observation for p in self.participants);best=max(best,hits/len(self.participants))
        return best

    @property
    def match_selectivity(self) -> float:
        return max(0.0,min(1.0,self.positive_match_mean-self.background_match_mean))

    def observe_selectivity(self, positive: float, background: float) -> None:
        self.selectivity_trials+=1;n=self.selectivity_trials
        self.positive_match_mean+=(positive-self.positive_match_mean)/n
        self.background_match_mean+=(background-self.background_match_mean)/n



@dataclass(slots=True)
class ProtoPattern:
    participants: tuple[PrimitiveKey, ...]
    occurrences: int = 0
    stable_observations: int = 0
    predicted_hits: float = 0.0
    prediction_trials: int = 0
    explained_sum: float = 0.0
    last_tick: int | None = None
    translation_tolerant: bool = False

    @property
    def stability(self) -> float: return self.stable_observations / max(1, self.occurrences)
    @property
    def predictive_value(self) -> float: return self.predicted_hits / max(1, self.prediction_trials)
    @property
    def redundancy(self) -> float: return self.explained_sum / max(1, self.occurrences)
