"""Durable records owned by :mod:`consciousness.memory`."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PlaceMemory:
    id: int
    cognit_id: int
    signature: tuple
    confidence: float = .5
    visits: int = 1
    last_confirmed_tick: int = 0
    views: list[tuple] = field(default_factory=list)
    contradictions: int = 0
    aliases: set[int] = field(default_factory=set)
    last_confirmed_time_seconds: float | None = None


@dataclass(slots=True)
class PersistentStructureMemory:
    id: int
    cognit_id: int
    feature_signature: tuple
    place_cognit_id: int
    relative_context: tuple[float, float]
    remembered_state: tuple[int, ...]
    confidence: float = .5
    last_confirmed_tick: int = 0
    contradictions: int = 0
    reactivations: int = 0
    last_recall_strength: float = 0.
    status: str = "UNCERTAIN"
    last_confirmed_time_seconds: float | None = None
    last_touch_time_seconds: float | None = None


__all__ = ["PersistentStructureMemory", "PlaceMemory"]
