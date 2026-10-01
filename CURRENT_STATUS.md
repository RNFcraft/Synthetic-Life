# Synthetic-Life — Current Status

## Current implementation: v0.8.4

Stabilization/freeze closure verified on 2026-10-01: **583 pytest passed;
CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted
suites: **156 passed**. Separate production/runtime freeze gates: **10 passed**.
Native Release/observer build, import/headless smokes and `git diff --check` passed.
Current version remains **v0.8.4 ? DONE / FROZEN**; this is not a new milestone.

v0.8.4 stabilization fix / freeze closure preserves ordinary predictions,
observes passive internal bin changes through production maintenance events,
contradicts stale failed-action hypotheses and retains external context.
The version remains v0.8.4; v0.8.5 remains planned.

Historical initial v0.8.4 verification on 2026-10-01: **549 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted suites: **122 passed**. Native Release/observer build, import/headless smokes and `git diff --check` passed.

v0.8.3 stabilization fix adds fail-closed brain internal sensor topology
compatibility. Learned knowledge transfers only with a matching encoding
contract; current body and episode state do not transfer. See
[the stabilization contract](docs/V0_8_3_HOMEOSTATIC_VALUATION.md#v083-stabilization-fix-brain-sensor-compatibility).

v0.8.4 adds learned WorldTime delay moments to existing SELF_ACTION/SEQUENTIAL
evidence, bounded passive projection between actions, confidence composition,
competing-bin calibration and temporal discount. Native physical digestion and
its same-appearance counterfactual verify acquisition through planner ranking.
All three feature flags default OFF. v0.8.5 survival curriculum remains planned.
See [v0.8.4](docs/V0_8_4_DELAYED_HOMEOSTATIC_LEARNING.md).

v0.8.0 is the frozen physiological foundation; v0.8.1 physical consumables,
v0.8.2 non-semantic interoception, and v0.8.3 learned trajectory-level
homeostatic valuation are implemented. Valuation defaults OFF. Supported
SELF_ACTION Relations predict internal sensory bins; bounded predicted
change in target-bin deviation contributes to beam ranking. No resource or
physiological action rule exists. See [v0.8.3](docs/V0_8_3_HOMEOSTATIC_VALUATION.md).
Snapshot v7 / continuous .seworld v10 apply with interoception;
.sebrain v6 is unchanged; native graph v4 adds timing rows when present and still reads/writes v3 without them. Additive causal configuration
restores non-default topology, cadence and cognitive settings before construction.

Historical v0.8.3 stabilization full verification on 2026-10-01: **516 pytest passed; CTest Release 2/2 passed**.
`python tools/verify.py --full` completed successfully, including native observer
build, import/headless smokes, full pytest and CTest.
Details: [testing](docs/TESTING.md).

## v0.8.0 — HOMEOSTATIC FOUNDATION — FROZEN

Synthetic-Life now has its first causal internal organism state. A separate
runtime-owned physiology subsystem is authoritative for bounded energy,
nutrient reserve, and hydration. Hunger and homeostatic tension are derived,
finite read-only projections rather than reward or policy variables.

Physiology advances exclusively by simulation WorldTime. Basal metabolism,
digestion, hydration loss, successful action costs, and zero-energy brownout
are deterministic. Core/planner and observer receive immutable projections and
cannot mutate physiology or turn tension into an action shortcut.

## Historical v0.8.0 acceptance

```text
full pytest                 431 passed
legacy/frozen tests         422 passed
new v0.8.0 tests              9 passed
CTest Release               2/2 passed
v0.8.0 digest               8dfb1595eb4bd704f7d0b8780f1e58d725f7ae6b50df47f43937efc45797580c
.seworld                     v8
.sebrain                     v6 (unchanged)
native graph                 v3 (unchanged)
```

The v0.7.6 behavioral oracle remains protected by its original tests. Runtime
behavior is intentionally extended by metabolism/action costs, and persistence
schema changes only by adding exact physiological continuation. Older
`.seworld` snapshots migrate deterministically.

The v0.8.0 digest matches for `PYTHONHASHSEED=1` and `777`; the canonical run
still completes `79` actions and `655` scheduler events.

Design and boundaries:
[`docs/V0_8_HOMEOSTASIS_DESIGN.md`](docs/V0_8_HOMEOSTASIS_DESIGN.md).

## Not implemented yet

General delayed credit assignment, semantic hunger/thirst, innate food/water
knowledge, neural interoception and long-horizon survival guarantees remain
outside this milestone. See the v0.8.3 limitations and proposed v0.8.4 scope.

## Frozen foundation

The v0.7.6 architecture freeze remains the structural foundation. No neural,
Assembly, Relation, language, scheduler-order, brain persistence, or native
graph contract was changed.
