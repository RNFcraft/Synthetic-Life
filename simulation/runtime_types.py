"""Read-only rendering records exported by the continuous runtime facade."""
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RenderBody:
    id: int
    x: int
    y: int
    orientation: str
    held_object_id: int | None


@dataclass(frozen=True, slots=True)
class RenderObject:
    id: int
    x: int
    y: int
    state: int


@dataclass(frozen=True, slots=True)
class RenderSnapshot:
    """Read-only observer projection; renderer wall clock is not causal."""

    world_time: float
    bodies: tuple[RenderBody, ...]
    objects: tuple[RenderObject, ...]


__all__ = ["RenderBody", "RenderObject", "RenderSnapshot"]
