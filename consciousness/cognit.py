from dataclasses import dataclass
from config import Settings
from .patterns import CognitPattern


@dataclass(slots=True)
class Cognit:
    id: int
    activity: float = 0.0
    threshold: float = 0.25
    confidence: float = 0.5
    utility: float = 0.0
    age: int = 0
    last_activated_cognitive_tick: int | None = None
    pattern: CognitPattern | None = None
    homeostatic_threshold: float = 0.25
    activity_trace: float = 0.0
    target_activity: float = 0.08
    refractory_ticks: int = 0
    novelty: float = 1.0
    predictive_contribution: float = 0.0
    low_retention_ticks: int = 0
    kind: str = "GENERAL"

    def retention_score(self,tick:int,settings:Settings)->float:
        from math import exp
        idle=tick-(self.last_activated_cognitive_tick if self.last_activated_cognitive_tick is not None else 0);recency=exp(-idle/max(1,settings.cognit_death_age))
        return (settings.retention_utility_weight*self.utility+settings.retention_confidence_weight*self.confidence+
          settings.retention_prediction_weight*self.predictive_contribution+settings.retention_recency_weight*recency)

    @property
    def effective_threshold(self) -> float: return max(self.threshold, self.homeostatic_threshold)

    def receive(self, energy: float, tick: int, settings: Settings, wave_step: bool = False) -> bool:
        if self.refractory_ticks > 0 and wave_step: energy *= settings.refractory_attenuation
        self.activity = min(1.0, max(0.0, self.activity + energy))
        active = self.activity >= self.effective_threshold
        if active:
            self.last_activated_cognitive_tick = tick
            self.utility = min(1.0, self.utility + 0.01)
            self.confidence = min(1.0, self.confidence + 0.002)
            if self.activity >= 0.75: self.refractory_ticks = settings.refractory_wave_steps
        return active

    def activate(self, energy: float, tick: int) -> bool:
        self.activity = min(1.0, max(0.0, self.activity + energy))
        if self.activity >= self.effective_threshold: self.last_activated_cognitive_tick = tick; return True
        return False

    def homeostatic_step(self, was_active: bool, settings: Settings) -> None:
        self.age += 1
        sample = 1.0 if was_active else 0.0
        lam = settings.homeostasis_trace_decay
        self.activity_trace = lam*self.activity_trace + (1-lam)*sample
        self.homeostatic_threshold = min(settings.threshold_max, max(settings.threshold_min,
            self.homeostatic_threshold + settings.homeostasis_learning_rate*(self.activity_trace-self.target_activity)))
        self.activity *= settings.cognit_activity_decay
        self.utility *= 0.999
        self.refractory_ticks = max(0, self.refractory_ticks-1)

    def decay(self, factor: float) -> None:
        self.age += 1; self.activity *= factor
