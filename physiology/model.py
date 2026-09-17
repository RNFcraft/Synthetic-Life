from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite

from world.actions import ActionType


@dataclass(frozen=True, slots=True)
class PhysiologySnapshot:
    """Read-only projection; derived hunger/tension are not authoritative state."""

    world_time: float
    energy: float
    nutrients: float
    hydration: float
    hunger: float
    tension: float


class HomeostaticEvaluator:
    """Bounded stability evaluator with no knowledge of objects or actions."""

    def __init__(self, energy_target: float, nutrient_target: float, hydration_target: float) -> None:
        self.targets = (energy_target, nutrient_target, hydration_target)
        if any(not isfinite(value) or value <= 0 for value in self.targets):
            raise ValueError("homeostatic targets must be finite and positive")

    def tension(self, energy: float, nutrients: float, hydration: float) -> float:
        values = (energy, nutrients, hydration)
        if any(not isfinite(value) for value in values):
            raise ValueError("physiology must be finite")
        deficits = [max(0.0, min(1.0, (target - value) / target)) for value, target in zip(values, self.targets)]
        return sum(value * value for value in deficits) / len(deficits)


class Physiology:
    """Single authoritative owner of causal physiological state.

    Updates depend only on WorldTime, explicit action outcomes, and explicit
    external consequences. Planner/observer consumers receive snapshots.
    """

    CONFIG_FIELDS = (
        "physiology_max_energy", "physiology_max_nutrients", "physiology_max_hydration",
        "physiology_initial_energy", "physiology_initial_nutrients", "physiology_initial_hydration",
        "physiology_energy_target", "physiology_nutrient_target", "physiology_hydration_target",
        "physiology_basal_body_rate", "physiology_basal_brain_rate", "physiology_hydration_rate",
        "physiology_digestion_rate", "physiology_digestion_efficiency",
        "physiology_movement_cost", "physiology_interaction_cost",
    )

    def __init__(self, settings) -> None:
        self.settings = settings
        self.energy = float(settings.physiology_initial_energy)
        self.nutrients = float(settings.physiology_initial_nutrients)
        self.hydration = float(settings.physiology_initial_hydration)
        self.world_time = 0.0
        self.evaluator = HomeostaticEvaluator(
            settings.physiology_energy_target,
            settings.physiology_nutrient_target,
            settings.physiology_hydration_target,
        )
        self._validate()

    @staticmethod
    def _clamp(value: float, maximum: float) -> float:
        if not isfinite(value):
            raise ValueError("physiology update must be finite")
        return max(0.0, min(float(maximum), value))

    def _validate(self) -> None:
        for value, maximum in ((self.energy, self.settings.physiology_max_energy), (self.nutrients, self.settings.physiology_max_nutrients), (self.hydration, self.settings.physiology_max_hydration)):
            if not isfinite(value) or not 0.0 <= value <= maximum:
                raise ValueError("physiology state outside configured bounds")
        if not isfinite(self.world_time) or self.world_time < 0:
            raise ValueError("physiology WorldTime must be finite and non-negative")

    @property
    def hunger(self) -> float:
        target = self.settings.physiology_nutrient_target
        return max(0.0, min(1.0, (target - self.nutrients) / target))

    @property
    def tension(self) -> float:
        return self.evaluator.tension(self.energy, self.nutrients, self.hydration)

    def snapshot(self) -> PhysiologySnapshot:
        return PhysiologySnapshot(self.world_time, self.energy, self.nutrients, self.hydration, self.hunger, self.tension)

    def advance_to(self, world_time: float) -> None:
        if not isfinite(world_time) or world_time < self.world_time:
            raise ValueError("physiology WorldTime must be finite and monotonic")
        elapsed = world_time - self.world_time
        digested = min(self.nutrients, self.settings.physiology_digestion_rate * elapsed)
        self.nutrients -= digested
        self.energy = self._clamp(
            self.energy + digested * self.settings.physiology_digestion_efficiency
            - elapsed * (self.settings.physiology_basal_body_rate + self.settings.physiology_basal_brain_rate),
            self.settings.physiology_max_energy,
        )
        self.hydration = self._clamp(
            self.hydration - elapsed * self.settings.physiology_hydration_rate,
            self.settings.physiology_max_hydration,
        )
        self.world_time = float(world_time)
        self._validate()

    def action_cost(self, action: ActionType) -> float:
        if action.name.startswith("MOVE_"):
            return self.settings.physiology_movement_cost
        if action is ActionType.IDLE:
            return 0.0
        return self.settings.physiology_interaction_cost

    def can_begin(self, action: ActionType) -> bool:
        return self.energy >= self.action_cost(action)

    def apply_action(self, action: ActionType, successful: bool) -> None:
        if successful:
            self.energy = self._clamp(self.energy - self.action_cost(action), self.settings.physiology_max_energy)

    def apply_consequence(self, *, nutrients: float = 0.0, hydration: float = 0.0) -> None:
        """World consequence hook; it performs no object recognition or policy."""
        if not isfinite(nutrients) or not isfinite(hydration):
            raise ValueError("physiological consequence must be finite")
        self.nutrients = self._clamp(self.nutrients + nutrients, self.settings.physiology_max_nutrients)
        self.hydration = self._clamp(self.hydration + hydration, self.settings.physiology_max_hydration)

    def to_dict(self) -> dict:
        return {"version": 1, "config": {name: getattr(self.settings, name) for name in self.CONFIG_FIELDS}, **asdict(self.snapshot())}

    def restore(self, data: dict) -> None:
        if data.get("version") != 1:
            raise ValueError("unsupported physiology schema")
        self.world_time = float(data["world_time"])
        self.energy = float(data["energy"])
        self.nutrients = float(data["nutrients"])
        self.hydration = float(data["hydration"])
        self._validate()
