from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BodySense:
    """Non-semantic contact/proprioception available to cognition."""
    touch_up: bool = False
    touch_down: bool = False
    touch_left: bool = False
    touch_right: bool = False
    holding: bool = False
    action_resistance: float = 0.0


@dataclass(frozen=True, slots=True)
class SensoryCell:
    relative_x: int
    relative_y: int
    occupied: bool
    state_channel: int
    boundary: bool
    self_present: bool
    appearance_channel: int = 0


@dataclass(frozen=True, slots=True)
class SensoryFrame:
    tick: int
    radius: int
    cells: tuple[SensoryCell, ...]
    body: BodySense = BodySense()

    @property
    def side(self) -> int:
        return self.radius * 2 + 1

    def signature(self) -> tuple[tuple[int, int, int, int, int], ...]:
        return tuple((c.relative_x, c.relative_y, int(c.occupied), c.state_channel, int(c.boundary)) for c in self.cells)

    def summary(self) -> dict[str, int]:
        return {
            "occupied": sum(c.occupied for c in self.cells),
            "boundaries": sum(c.boundary for c in self.cells),
            "state_sum": sum(c.state_channel for c in self.cells),
            "touches": sum((self.body.touch_up,self.body.touch_down,self.body.touch_left,self.body.touch_right)),
            "holding": int(self.body.holding),
            "resistance": int(self.body.action_resistance > 0),
        }
