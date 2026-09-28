from .actions import Action, ActionResult, ActionType
from .world import World
from .perception import BodySense, SensoryFrame
from .time import ActionIntent, EventSequence, WorldTime

def __getattr__(name: str):
    if name == "NativeWorld":
        from .native_world import NativeWorld
        return NativeWorld
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Action", "ActionIntent", "ActionResult", "ActionType", "BodySense", "EventSequence", "NativeWorld", "SensoryFrame", "World", "WorldTime"]

