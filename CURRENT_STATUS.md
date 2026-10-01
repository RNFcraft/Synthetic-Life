# Synthetic-Life — Current Status

## Current implementation: v0.8.3

v0.8.0 is the frozen physiological foundation; v0.8.1 physical consumables,
v0.8.2 non-semantic interoception, and v0.8.3 learned trajectory-level
homeostatic valuation are implemented. Valuation defaults OFF. Supported
SELF_ACTION Relations predict internal sensory bins; bounded predicted
change in target-bin deviation contributes to beam ranking. No resource or
physiological action rule exists. See [v0.8.3](docs/V0_8_3_HOMEOSTATIC_VALUATION.md).
Snapshot v7 / continuous .seworld v10 apply with interoception;
.sebrain v6 and native graph v3 are unchanged. Additive causal configuration
restores non-default topology, cadence and cognitive settings before construction.

Full verification on 2026-10-01: **491 pytest passed; CTest Release 2/2 passed**.
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
