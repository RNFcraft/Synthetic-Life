"""Stable plan and continuous-deliberation records.

The planning implementation lives in :mod:`consciousness.planning`; this module
contains only its data/session layer and therefore does not import the core.
"""
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

from world.actions import ActionType


@dataclass(frozen=True, slots=True)
class Plan:
    actions: tuple[ActionType, ...]
    predicted_states: tuple[frozenset[int], ...]
    score: float
    confidence: float
    goal_alignment: float
    uncertainty: float
    loop_risk: float
    created_tick: int
    revision: int = 0


class CognitiveWorkKind(Enum):
    RECALL = "RECALL"
    PROPAGATE = "PROPAGATE"
    IMAGINE = "IMAGINE"
    PLAN_REFINE = "PLAN_REFINE"


@dataclass(frozen=True, slots=True)
class CognitiveWork:
    kind: CognitiveWorkKind
    key: tuple
    payload: tuple[int, ...] = ()


@dataclass(slots=True)
class DeliberationSession:
    tick: int
    current: frozenset[int]
    working: set[int]
    candidate: Plan | None = None
    semantic_cache: tuple[dict, dict, dict] | None = None
    cycles: int = 0
    quiescent: bool = False
    finalized: bool = False
    working_revision: int = 0
    last_recall_key: tuple | None = None
    last_recalled: frozenset[int] = frozenset()
    pending_work: deque[CognitiveWork] = field(default_factory=deque)
    pending_keys: set[tuple] = field(default_factory=set)
    work_history: list[str] = field(default_factory=list)


__all__ = ["CognitiveWork", "CognitiveWorkKind", "DeliberationSession", "Plan"]
