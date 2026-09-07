# Synthetic Entity v0.5.3 — Current Status

## ELAPSED-TIME LAZY COGNITION: FAIL

The analytical elapsed-time model and focused reference tests are complete, but the model is not yet connected to the behavior-authoritative runtime. This gate therefore cannot be marked PASS.

## Completed in this pass

- Classified real-duration fields separately from causal/event counters in `V0_5_3_CONTINUOUS_RUNTIME_PLAN.md`.
- Added closed-form, composable reference evolution for passive Cognit activity, utility, inactive activity trace, and homeostatic threshold.
- Added reference lazy decay/aging for Relation confidence, memory confidence/recency, and Goal persistence/unavailable/cooldown durations.
- Used only absolute simulated `WorldTime.seconds`; no wall-clock source is used.
- Verified composition at sub-second, integer, long, and 1000-second intervals.
- Verified Relation touch-frequency invariance and sub-second Goal durations.
- Verified a 100,000-Cognit quiescent time jump performs zero materializations and subsequently touches only two requested Cognits.

## First concrete semantic blocker

`ContinuousRuntime` does not yet pass its event timestamps into these elapsed-time primitives, and native `NativeBrainEngine` Cognit/Relation state has no authoritative persisted `last_touch_time` frontier. Its existing homeostasis and passive decay paths still advance from cognition/event ticks. Python SpatialMemory and Goal consumers likewise still use their frozen tick-based fields.

Consequently, the current implementation does **not** yet prove that a touch at 12.300 evolves state from the actual preceding touch time, nor that save/load preserves that evolution. The new module is an executable formula oracle only; it is not presented as native authority.

## Required next action

Add a feature-gated float64 `last_touch_time` SoA/frontier to native Cognit and Relation state, materialize only touched IDs at the current `WorldTime.seconds`, and persist those frontiers. Wire the same event timestamp through SpatialMemory and elapsed Goal fields. Enable this path only from `ContinuousRuntime` so the frozen v0.5.2 discrete APIs remain the compatibility oracle. Then add actual-runtime timestamp, save/load, integer-compatibility, and deterministic schedule tests.

## Deliberately retained event/count semantics

- `EventSequence` and `cognitive_tick`
- evidence/support/confirmation/contradiction counts
- prototype occurrences and `explained_sum`
- percept missing/observation counts
- wave and refractory steps
- planner depth/expansions and deterministic tie cursors
- Goal deliberation attempts and completion/intervention counts

## Verification performed

- Elapsed-time reference tests: **8 passed**.
- Elapsed-time plus continuous runtime modules: **21 passed**.
- Focused v0.5.2 native/causal compatibility subset: **43 passed**.
- CTest: **1/1 passed**.
- Long benchmarks were not run.

## Previous gate

CONTINUOUS COGNITIVE CONTINUATION: **PASS**.

SDL3/OpenGL observer work has not started.

## Files added or updated for this gate

- `consciousness/elapsed_time.py`
- `tests/test_v053_elapsed_time.py`
- `V0_5_3_CONTINUOUS_RUNTIME_PLAN.md`
- `CURRENT_STATUS.md`
