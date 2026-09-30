from dataclasses import dataclass
from math import isfinite


@dataclass(slots=True)
class WorldObject:
    id: int
    x: int
    y: int
    type: str = "generic"
    state: int = 0
    passable: bool = False
    resource_channel: int = 0
    nutrients: float = 0.0
    hydration: float = 0.0

    def __post_init__(self) -> None:
        if type(self.resource_channel) is not int or self.resource_channel not in (0, 1, 2):
            raise ValueError("resource channel must be 0, 1 or 2")
        if any(not isfinite(value) or not 0 <= value <= 100 for value in (self.nutrients, self.hydration)):
            raise ValueError("resource payload must be finite and bounded")
        if self.resource_channel == 0 and (self.nutrients or self.hydration):
            raise ValueError("generic objects cannot carry a resource payload")
        if self.resource_channel and not (self.nutrients or self.hydration):
            raise ValueError("consumable must carry a payload")
        if self.resource_channel and self.state != self.resource_channel:
            raise ValueError("consumable state channel is invalid")

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y
