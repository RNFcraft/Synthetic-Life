from dataclasses import dataclass
from enum import Enum, auto


class ActionType(Enum):
    IDLE = auto()
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    GRAB_UP = auto()
    GRAB_DOWN = auto()
    GRAB_LEFT = auto()
    GRAB_RIGHT = auto()
    RELEASE = auto()
    INTERACT_UP = auto()
    INTERACT_DOWN = auto()
    INTERACT_LEFT = auto()
    INTERACT_RIGHT = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    # Retained for v0.1-v0.3 snapshot/test compatibility; acts in orientation.
    INTERACT = auto()


class ActionResult(Enum):
    SUCCESS = auto()
    BLOCKED = auto()
    INVALID = auto()


@dataclass(frozen=True, slots=True)
class Action:
    kind: ActionType
