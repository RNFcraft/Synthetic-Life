"""Pure, nonsemantic sensory encoding of the three authoritative reserves."""
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class InteroceptiveFrame:
    world_time: float
    levels: tuple[int, int, int]


class InteroceptiveTransducer:
    def __init__(self, settings):
        self.bins = settings.interoception_bins
        self.targets = (settings.physiology_energy_target, settings.physiology_nutrient_target, settings.physiology_hydration_target)
        self.maximums = (settings.physiology_max_energy, settings.physiology_max_nutrients, settings.physiology_max_hydration)
        if any(not isfinite(x) or x <= 0 for x in self.maximums):
            raise ValueError("interoception maxima must be finite and positive")

    @property
    def target_levels(self):
        return tuple(min(self.bins - 1, max(0, int(x / maximum * self.bins)))
                     for x, maximum in zip(self.targets, self.maximums))

    def sample(self, snapshot):
        values = (snapshot.energy, snapshot.nutrients, snapshot.hydration)
        if any(not isfinite(x) for x in values):
            raise ValueError("interoception reserves must be finite")
        levels = tuple(min(self.bins - 1, max(0, int(x / maximum * self.bins))) for x, maximum in zip(values, self.maximums))
        return InteroceptiveFrame(snapshot.world_time, levels)
