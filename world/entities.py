from dataclasses import dataclass


@dataclass(slots=True)
class EntityBody:
    id: int
    x: int
    y: int
    orientation: str = "NORTH"
    held_object_id: int | None = None
    appearance: int = 1

    @property
    def position(self) -> tuple[int, int]:
        return self.x, self.y
