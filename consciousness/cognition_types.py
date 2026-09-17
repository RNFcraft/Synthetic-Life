"""Semantic continuous-cognition records shared by core and runtime."""
from __future__ import annotations

from dataclasses import dataclass

from world.actions import ActionType
from world.perception import SensoryFrame
from .planning_types import DeliberationSession


@dataclass(slots=True)
class ContinuousCognitionFrontier:
    """Persisted Python-authority of an unfinished cognition transaction."""

    generation: int
    world_time: float
    frame: SensoryFrame
    current: set[int]
    track_ids: tuple[int, ...]
    session: DeliberationSession | None = None
    phase: str = "OBSERVED"
    action: ActionType | None = None
    committed: bool = False


__all__ = ["ContinuousCognitionFrontier"]
