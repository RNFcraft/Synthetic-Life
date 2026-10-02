# Synthetic-Life — Current Status

## Current implementation: v0.9.1

Cognitive foundation: **v0.8.4 DONE / FROZEN**.
Experimental workbench: **v0.9.0 DONE**.
Reproducible scenario infrastructure: **v0.9.1 DONE / FROZEN**.
Current freeze acceptance: **711 pytest PASS; Release CTest 2/2 PASS;
observer-OFF CTest 1/1 PASS; six targeted suites 217 PASS** (2026-10-02).
Survival proof: **v0.9.2 PLANNED**; long-run stability/freeze: **v0.9.3 PLANNED**.
Canonical scenario v1, single-run manifest v1, clean RNG bootstrap, host-only
workbench export and the shared interactive/headless factory are described in
[the v0.9.1 contract](docs/V0_9_1_REPRODUCIBLE_SCENARIOS.md).

Historical v0.9.0 acceptance on 2026-10-01: **613 pytest passed; Release CTest 2/2 passed**
via `python tools/verify.py --full`; required targeted suites **154 passed**.
Observer-OFF native engine/oracle build and CTest **1/1 passed**. Native visual
fixture inspected at 1100×700, 1440×900 and 1920×1080; font/layout tests cover
1×/1.5×/2× scale. Actual hardware at high DPI remains a manual platform gate.
Native ImGui desktop, World editor, physical presets, physiology/interoception,
planner and brain inspectors, dialogue input, deterministic command boundary
and pending-command `.seworld` v11 continuation are described in
[the workbench contract](docs/V0_9_0_EXPERIMENTAL_WORKBENCH.md).
The following counts document the historical cognitive freeze.

Stabilization/freeze closure verified on 2026-10-01: **583 pytest passed;
CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted
suites: **156 passed**. Separate production/runtime freeze gates: **10 passed**.
Native Release/observer build, import/headless smokes and `git diff --check` passed.
The cognitive foundation remains **v0.8.4 — DONE / FROZEN**.

v0.8.4 stabilization fix / freeze closure preserves ordinary predictions,
observes passive internal bin changes through production maintenance events,
contradicts stale failed-action hypotheses and retains external context.
The old v0.8.5 scope is planned v0.9.2; see the roadmap revision.

Historical initial v0.8.4 verification on 2026-10-01: **549 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted suites: **122 passed**. Native Release/observer build, import/headless smokes and `git diff --check` passed.

v0.8.3 stabilization fix adds fail-closed brain internal sensor topology
compatibility. Learned knowledge transfers only with a matching encoding
contract; current body and episode state do not transfer. See
[the stabilization contract](docs/V0_8_3_HOMEOSTATIC_VALUATION.md#v083-stabilization-fix-brain-sensor-compatibility).

v0.8.4 adds learned WorldTime delay moments to existing SELF_ACTION/SEQUENTIAL
evidence, bounded passive projection between actions, confidence composition,
competing-bin calibration and temporal discount. Native physical digestion and
its same-appearance counterfactual verify acquisition through planner ranking.
All three feature flags default OFF. v0.9.2 survival curriculum remains planned.
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

## v0.9.1 stabilization / freeze closure

- Historical engine defaults restored: 25 initial / 25 maximum objects.
- Settings / New World dialog with World, Resources, Physiology, Cognition and Workbench tabs.
- Built-in Classic Baseline, Workbench Sparse (3/150), Empty Experiment (0/150) drafts.
- Host-owned fresh runtime replacement at WorldTime 0, selected seed, no learned-brain transfer.
- Strict contiguous artifact section validation, including unaccounted trailing-byte rejection.
- Scenario object-ID exhaustion guard reserves future capacity within the uint32 domain.
- Workbench preferences remain session-only presentation state; causal settings are immutable during an episode.

See [freeze verification](docs/V0_9_1_FREEZE_CLOSURE.md) for actual executed results.
v0.9.2 First Survival-Learning Proof remains PLANNED.
