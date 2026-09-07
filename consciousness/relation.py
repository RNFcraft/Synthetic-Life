from dataclasses import dataclass
from enum import Enum, auto


class RelationType(Enum):
    ASSOCIATIVE = auto(); SEQUENTIAL = auto(); CAUSAL = auto(); INHIBITORY = auto(); SELF_ACTION = auto(); SPATIAL = auto()


class RelationStatus(Enum):
    PROVISIONAL = auto()
    CONSOLIDATED = auto()


@dataclass(slots=True)
class Relation:
    source_id: int
    target_id: int
    strength: float = 0.2
    confidence: float = 0.3
    delay: int = 0
    relation_type: RelationType = RelationType.ASSOCIATIVE
    context_id: int | None = None
    age: int = 0
    last_used_cognitive_tick: int | None = None
    support: int = 0
    lift: float = 1.0
    last_evidence_world_tick: int = 0
    status: RelationStatus = RelationStatus.PROVISIONAL
    prediction_probability: float = 0.0
    uncertainty: float = 1.0
    contradiction_evidence: float = 0.0
    usefulness: float = 0.0
    confirmations: int = 0

    def effective_confidence(self, tick: int, decay: float) -> float:
        return self.confidence * decay ** (tick-self.last_evidence_world_tick)

    def materialize_decay(self, tick: int, decay: float) -> None:
        self.confidence = self.effective_confidence(tick, decay)
        if tick<self.last_evidence_world_tick:raise ValueError("world clock moved backwards")
        self.age += tick-self.last_evidence_world_tick
        self.last_evidence_world_tick = tick

    def update_outcome(self, confirmed: bool, confirmation_rate: float, contradiction_rate: float) -> None:
        if confirmed:
            self.confirmations += 1
            self.confidence += confirmation_rate * (1.0-self.confidence)
            self.contradiction_evidence *= 1.0-contradiction_rate
        else:
            self.contradiction_evidence += contradiction_rate * (1.0-self.contradiction_evidence)
            self.confidence *= 1.0-contradiction_rate
        self.confidence=max(0.0,min(1.0,self.confidence));self.uncertainty=1.0-self.confidence
