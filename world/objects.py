from dataclasses import dataclass


@dataclass(slots=True)
class WorldObject:
    id: int
    x: int
    y: int
    type: str = "generic"
    state: int = 0
    passable: bool = False

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y

