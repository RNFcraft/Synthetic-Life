# TASK.md — v0.5.2 Final Blocker Pass

## Context

Continue from the **CURRENT working tree**.

Do **not** perform a repository-wide audit.
Do **not** restate project architecture.
Do **not** redo already passing migration work.
Do **not** touch language, 3D rendering, async scheduling, or unrelated cleanup.

Current verified baseline:

- `NativeBrainEngine` is the sole numeric brain authority in native mode.
- `full_graph_sync_calls == 0`.
- 120 pytest passed.
- CTest 1/1 passed.
- 3 × 100-step brain lockstep scenarios pass.
- Native causal proof:
  - Experienced 5/5
  - Fresh 5/5
  - Causal-rho ablated 0/5
- 1000-action Python/C++ single-entity World lockstep passes.
- `.sebrain` / `.seworld` have native binary `NBRN` sections without Relation export to Python.
- 10K Entity benchmark completes without continuing throughput collapse.
- Relation proxies are effectively removed from hot runtime paths.

Current performance:

| checkpoint | wall time |
|---:|---:|
| 100 | 1.10 s |
| 1K | 25.43 s |
| 5K | 161.23 s |
| 10K | 332.01 s |

Sustained throughput:
- 1K–5K: 29.46 action/s
- 5K–10K: 29.28 action/s

Current remaining blockers:

1. float32/float64 brain drift begins at tick 149;
2. planner still generates ~503 FFI calls/action;
3. `SpatialMemory` still performs hot full-history scans;
4. Native `WorldRuntime` still lacks spawning/RNG continuation and multi-entity conflict parity.

The goal of this task is to close these blockers with the smallest necessary changes.

---

# PRIORITY 1 — Exact numeric parity

The frozen Python oracle evolves behavior-affecting Cognit/Relation numeric state in float64.

Native storage currently uses float32 in places and extended lockstep first diverges at:

- tick: 149
- Cognit: 2
- field: activity
- Python: `0.6429510648`
- Native: `0.6438011527`

Do not hide this with a wider tolerance.

## Required work

Audit all behavior-affecting numeric brain state crossing Python/native boundaries.

Unless there is a concrete proof that a field cannot affect behavior, use float64 for runtime state that participates in:

- Cognit activity
- thresholds
- homeostatic threshold
- confidence
- utility
- activity trace
- target activity
- predictive contribution
- wave math
- Relation strength/confidence/prediction/lift/contradiction/usefulness
- prediction accumulation
- homeostasis
- planner-visible prediction values
- any branch/threshold comparison.

Keep compact integer/status fields compact.

Update pybind bindings and persistence format as required.

Do not introduce approximation or quantization in v0.5.2.

## Gate

Run the existing extended Python/native lockstep.

Find the first divergence if one remains.

Target:
- no structural divergence;
- no behavior-affecting numeric divergence over a substantially longer run than 149 ticks.

Use a focused lockstep test first.
Do not run the entire suite after every edit.

If this gate is not solved cleanly, stop and report the exact first differing field.

---

# PRIORITY 2 — Collapse planner FFI volume

Only proceed after Priority 1 is stable.

Current final-window runtime still performs roughly:

`503 FFI calls / physical action`

The remaining calls are mainly repeated planner prediction / numeric semantic-view boundaries.

Python keeps planner **meaning and scoring**.

C++ should perform planner **mechanical graph work** in coarse batches.

## Required work

Profile/count the current planner boundary and identify repeated per-branch/per-action calls.

Create the minimum coarse native API needed to batch repeated work, for example conceptually:

`planner_transition_batch(states, actions, params)`

or equivalent.

The API may return compact arrays/POD data containing only what Python semantic scoring actually needs.

Do not port these into C++:

- Goal semantics
- Target semantics
- BeliefScene meaning
- role reasoning
- final semantic planner score
- exploration policy.

Do move/batch:

- repeated graph prediction
- action-conditioned deltas
- mechanical wave expansion
- repeated relation traversal
- duplicated state/action numeric queries.

Avoid one FFI call per Relation, Cognit, action branch, or beam node.

## Gate

Measure:
- FFI calls/action before
- FFI calls/action after
- planner wall time before
- planner wall time after
- 100-step behavior equivalence.

Target:
- major reduction from ~503 calls/action;
- preferably `<100`;
- do not change beam width, horizon, cognition, learning, or planner semantics to hit the target.

---

# PRIORITY 3 — Remove SpatialMemory full-history hot scans

Only proceed if enough session budget remains.

Current audit:

`Python SpatialMemory = HOT = O(total retained semantic memories)`

This is incompatible with a long-lived Entity.

## Required work

Do not rewrite memory semantics.

Keep Python as owner of memory meaning/policy.

Replace repeated full-history retrieval scans with incremental/indexed candidate retrieval.

Use only indexes justified by the actual current query patterns.

Possible indexes include:

- participant Cognit → memory entries
- Place hypothesis → entries
- relation type → entries
- current episode → entries
- confidence/state bucket → entries
- recent/dirty entries
- goal-relevant participant set.

Do not add speculative complexity that current code does not use.

The retrieval result must remain semantically equivalent to the current implementation.

Maintain indexes incrementally on:
- memory birth
- update
- contradiction/state change
- deletion
- load/transfer.

## Gate

Add differential tests:
- indexed retrieval == previous full-scan retrieval on the same state.

Profile:
- retrieval time
- candidate count
- total retained memories.

Normal retrieval cost should depend primarily on relevant candidates, not all historical memories.

---

# PRIORITY 4 — Complete Native World parity

Only proceed after priorities above, or if they are already complete.

`WorldRuntime` already passes 1000 random single-entity actions for:
- movement
- push
- grab/carry/release
- interact
- turn
- resistance
- SensoryFrame
- sub-second `WorldTime`.

Missing:

- seeded initialization parity
- spawning
- exact RNG continuation
- multiple bodies
- simultaneous intents
- body/body conflict resolution
- shared-object/resource conflicts
- release conflicts
- deterministic rotating fairness.

## Rules

Python World remains the oracle until parity is proven.

Do not expose physical truth to cognition.

Preserve:

`World -> immutable SensoryFrame -> Core -> ActionIntent -> World`

Core must never receive:
- object IDs
- World/Grid objects
- absolute coordinates
- collision IDs
- semantic action results
- spawn schedule.

## Gate

Differential Python/native tests using identical seeds and action traces.

Required:
- seeded initialization parity
- spawning parity
- save/load RNG continuation parity
- at least 1000 single-entity random actions
- deterministic multi-entity conflict traces
- multi-entity fairness parity
- SensoryFrame parity.

Only after these pass may native World become the normal backend.

---

# TEST STRATEGY — IMPORTANT FOR QUOTA

Use quota efficiently.

During implementation:
1. run only the smallest directly relevant test;
2. then the relevant test module;
3. run full pytest/CTest only after a priority gate is complete.

Do not repeatedly run 5K/10K benchmarks during development.

Performance ladder:
- focused micro/profile
- 100 actions
- 1K actions
- only after all blockers are closed: 5K/10K final verification.

Do not recursively reread the repository unless a failing test requires following a dependency.

---

# NO PERFORMANCE CHEATING

Forbidden:

- reducing beam width/horizon
- reducing evidence window
- lowering relation caps
- disabling composites
- disabling memory
- disabling planning
- disabling learning
- reducing deliberation only for native mode
- Top-K/MAX_ACTIVE shortcuts
- changing curriculum
- silently dropping telemetry
- weakening lockstep tolerance to hide numeric drift.

Optimization must come from representation, indexing, batching, and runtime architecture.

---

# FINAL VERIFICATION

When all implemented priorities are complete:

1. Release rebuild.
2. `pytest`.
3. CTest.
4. three existing 100-step brain lockstep scenarios.
5. extended brain lockstep beyond previous tick-149 failure.
6. native causal regression.
7. World lockstep including new functionality.
8. persistence continuation.
9. benchmark 100 / 1K.
10. if healthy, benchmark 5K / 10K.

Record:
- wall time
- actions/s by windows
- FFI calls/action
- Relation proxies/action
- live Cognits
- Relations
- memory count / retrieval candidate count
- `full_graph_sync_calls`.

---

# STOP / HANDOFF RULE

Before the session ends, always write/update `CURRENT_STATUS.md`.

Keep it short:

## DONE
Exact items completed in this session.

## CURRENT GATE
First failing or unfinished gate.

## FIRST FAILURE
Exact test / tick / field / numbers if applicable.

## NEXT ACTION
One concrete next implementation step.

## TESTS
Only actual results.

## BENCHMARK
Only actual results.

## MODIFIED FILES
List only.

Do not spend remaining quota writing a long narrative.

---

# FINAL ACCEPTANCE

Freeze only if all four blockers are resolved and verification passes.

Then report:

`READY TO FREEZE v0.5.2: YES`

Otherwise:

`READY TO FREEZE v0.5.2: NO`

and list only concrete remaining blockers.

Most important:

**Do not re-audit the project. Continue from the current tree and attack the first unfinished gate directly.**
