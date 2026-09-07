from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Grid:
    width: int
    height: int

    def contains(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

