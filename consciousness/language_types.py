"""Language frames, result records and grounding-context episode state.

This module has no dependency on ``SyntheticEntityCore``.  It is the low-level
data/state layer re-exported by :mod:`consciousness.language` for compatibility.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import exp
import unicodedata

from .relational import RelationalStructure
from .wave import WaveResult


@dataclass(frozen=True, slots=True)
class LanguageFrame:
    message_id: int
    issued_at_world_time: float
    surface: str

    def __post_init__(self):
        object.__setattr__(self, "surface", normalize_token(self.surface))


@dataclass(frozen=True, slots=True)
class LanguageUtteranceFrame:
    message_id: int
    issued_at_world_time: float
    tokens: tuple[str, ...]
    request_target: RelationalStructure | None = None

    def __post_init__(self):
        normalized = tuple(normalize_token(token) for token in self.tokens)
        if not normalized:
            raise ValueError("LanguageUtteranceFrame requires at least one token")
        object.__setattr__(self, "tokens", normalized)


@dataclass(frozen=True, slots=True)
class GroundingContextEntry:
    cognit_id: int
    salience: float


@dataclass(frozen=True, slots=True)
class GroundingContextSnapshot:
    world_time: float
    observation_generation: int
    entries: tuple[GroundingContextEntry, ...]


@dataclass(frozen=True, slots=True)
class HistoricalGroundingContext:
    snapshot: GroundingContextSnapshot
    retired_at_world_time: float


@dataclass(frozen=True, slots=True)
class LanguageProcessingResult:
    symbol_id: int | None
    wave: WaveResult
    grounding_candidates_updated: int
    grounding_relations_materialized: int


@dataclass(frozen=True, slots=True)
class LanguageSemanticSlot:
    token_position: int
    symbol_id: int | None
    retrieved_cognit_ids: tuple[int, ...]
    resolved_cognit_id: int | None


@dataclass(frozen=True, slots=True)
class LanguageRelationalResult:
    ordered_symbol_ids: tuple[int | None, ...]
    semantic_slots: tuple[LanguageSemanticSlot, ...]
    relational_structure: RelationalStructure | None
    confidence: float
    unresolved_slots: tuple[int, ...]
    provenance: tuple[tuple[int, int], ...]


@dataclass(frozen=True, slots=True)
class LanguageRequestResult:
    relational_result: LanguageRelationalResult
    request_confidence: float
    request_cue_symbol_ids: tuple[int, ...]
    desired_structure: RelationalStructure | None
    goal_id: int | None
    provenance: tuple[tuple[int, int], ...]


@dataclass(frozen=True, slots=True)
class LanguageUtteranceResult:
    message_id: int
    world_time: float
    tokens: tuple[str, ...]
    ordered_symbol_ids: tuple[int | None, ...]
    token_results: tuple[LanguageProcessingResult, ...]
    sequence_edges: tuple[tuple[int, int], ...]
    composed_active_ids: frozenset[int]
    token_count: int
    relational_result: LanguageRelationalResult | None = None
    request_result: LanguageRequestResult | None = None


@dataclass(slots=True)
class LanguageUtteranceFrontier:
    frame: LanguageUtteranceFrame
    grounding_context: dict[int, float]
    next_token_index: int = 0
    processed_symbol_ids: list[int | None] | None = None
    token_results: list[LanguageProcessingResult] | None = None
    phase: str = "TOKEN"

    def __post_init__(self):
        if self.processed_symbol_ids is None:
            self.processed_symbol_ids = []
        if self.token_results is None:
            self.token_results = []


def normalize_token(surface: str) -> str:
    token = unicodedata.normalize("NFC", surface.strip())
    if not token or any(character.isspace() for character in token):
        raise ValueError("LanguageFrame requires exactly one non-empty token")
    return token


class GroundingContextTracker:
    """Observational history in WorldTime for 1-based sensory Cognit IDs."""

    def __init__(self, settings):
        self.settings = settings
        self.latest = None
        self.historical = deque(maxlen=settings.language_recent_contexts)
        self.background_mass = {}
        self.total_experience_time = 0.0
        self.accounted_until = None

    @property
    def recent(self):
        return self.historical

    def accrue(self, now):
        if self.accounted_until is None:
            self.accounted_until = float(now)
            return
        if now < self.accounted_until:
            raise ValueError("grounding context time moved backwards")
        dt = float(now) - self.accounted_until
        if dt and self.latest:
            for entry in self.latest.entries:
                self.background_mass[entry.cognit_id] = (
                    self.background_mass.get(entry.cognit_id, 0.0)
                    + entry.salience * dt
                )
            self.total_experience_time += dt
        self.accounted_until = float(now)

    def observe(self, snapshot):
        self.accrue(snapshot.world_time)
        if self.latest is not None:
            self.historical.append(
                HistoricalGroundingContext(self.latest, float(snapshot.world_time))
            )
        self.latest = snapshot

    def eligible(self, now):
        self.accrue(now)
        merged = {}
        horizon = self.settings.language_grounding_horizon_seconds
        tau = self.settings.language_grounding_tau_seconds
        if self.latest is not None:
            for entry in self.latest.entries:
                merged[entry.cognit_id] = max(
                    merged.get(entry.cognit_id, 0.0), entry.salience
                )
        for item in self.historical:
            snapshot = item.snapshot
            age = float(now) - item.retired_at_world_time
            if age < 0 or age > horizon:
                continue
            credit = exp(-age / max(tau, 1e-12))
            for entry in snapshot.entries:
                merged[entry.cognit_id] = max(
                    merged.get(entry.cognit_id, 0.0), entry.salience * credit
                )
        return merged

    @staticmethod
    def _dump(snapshot):
        if snapshot is None:
            return None
        return [
            snapshot.world_time,
            snapshot.observation_generation,
            [[entry.cognit_id, entry.salience] for entry in snapshot.entries],
        ]

    @staticmethod
    def _load(raw):
        if raw is None:
            return None
        return GroundingContextSnapshot(
            float(raw[0]),
            int(raw[1]),
            tuple(GroundingContextEntry(int(i), float(q)) for i, q in raw[2]),
        )

    def durable_dict(self):
        return {
            "background_mass": [
                [i, value] for i, value in sorted(self.background_mass.items())
            ],
            "total_experience_time": self.total_experience_time,
        }

    def episode_dict(self):
        return {
            "latest": self._dump(self.latest),
            "historical": [
                [self._dump(item.snapshot), item.retired_at_world_time]
                for item in self.historical
            ],
            "accounted_until": self.accounted_until,
        }

    def restore_durable(self, data):
        data = data or {}
        self.background_mass = {
            int(i): float(value) for i, value in data.get("background_mass", [])
        }
        self.total_experience_time = float(data.get("total_experience_time", 0.0))

    def restore_episode(self, data):
        data = data or {}
        self.latest = self._load(data.get("latest"))
        rows = data.get("historical")
        if rows is None:
            rows = [
                [self._load(raw), float(self._load(raw).world_time)]
                for raw in data.get("recent", [])
                if self._load(raw) != self.latest
            ]
        else:
            rows = [[self._load(raw), float(retired)] for raw, retired in rows]
        self.historical = deque(
            (HistoricalGroundingContext(snapshot, retired)
             for snapshot, retired in rows),
            maxlen=self.settings.language_recent_contexts,
        )
        self.accounted_until = data.get("accounted_until")


__all__ = [
    "GroundingContextEntry", "GroundingContextSnapshot",
    "GroundingContextTracker", "HistoricalGroundingContext", "LanguageFrame",
    "LanguageProcessingResult", "LanguageRelationalResult",
    "LanguageRequestResult", "LanguageSemanticSlot", "LanguageUtteranceFrame",
    "LanguageUtteranceFrontier", "LanguageUtteranceResult", "normalize_token",
]
