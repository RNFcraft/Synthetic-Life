"""Continuous simulated time and causal order for future event scheduling.

v0.5.2 retains its legacy integer scheduler. Event IDs never measure elapsed
time; durable aging APIs should eventually consume differences in seconds.
"""
from dataclasses import dataclass
from math import floor,isfinite
from .actions import Action


@dataclass(frozen=True,slots=True)
class WorldTime:
    seconds:float=0.0

    def __post_init__(self):
        if not isfinite(self.seconds) or self.seconds<0:raise ValueError('invalid world time')

    @property
    def world_tick(self)->int:return floor(self.seconds)


@dataclass(slots=True)
class EventSequence:
    """Ordering/debug identifier, independent of simulated elapsed time."""
    value:int=0
    def next(self)->int:
        self.value+=1
        return self.value


@dataclass(frozen=True,slots=True)
class ActionIntent:
    action:Action
    issued_at_world_time:WorldTime
    event_id:int
