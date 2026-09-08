# Synthetic Entity v0.5.3 — Current Status

## CONTINUOUS WORLD COMPLETION

CONTINUOUS WORLD COMPLETION: FAIL (verification pending)

The implementation branch schedules `WORLD_SPAWN` and `MAINTENANCE` at
absolute `WorldTime`, and normal `ContinuousRuntime` no longer dispatches
`NativeWorld.world_tick()`. The frozen legacy `world_tick()` API remains.
`RuntimeEvent.id` is now retained solely for scheduler ordering; physical
World mutations allocate their own `Simulation.event_sequence` at execution.
Maintenance passes its absolute deadline through the established continuous
time entry point before bounded lifecycle work.
The native environment is configured with CMake 4.4.3, Ninja 1.13.2, pytest
9.1.1, and MSVC. A clean Release native build, focused continuous-world tests
(6 passed), focused continuous runtime/frontier/elapsed tests (75 passed),
full pytest (207 passed), and CTest equivalence (1/1 passed) now run. A small
`PYTHONHASHSEED=1/77` continuous trajectory digest is identical. The gate
remains FAIL until its wider explicit acceptance/persistence matrix is added.

## TRUE EVENT-DRIVEN COGNITION FRONTIER

TRUE EVENT-DRIVEN COGNITION FRONTIER: PASS

## ARCHITECTURE

    SENSORY_CHANGE
      -> bounded observation / new cognition generation
      -> COGNITION_WAKE
      -> COGNITION_CONTINUE x N at the same WorldTime
      -> QUIESCENT
      -> one decision commit
      -> WORLD_ACTION_COMPLETE at WorldTime + 0.15

- Normal `ContinuousRuntime` uses dedicated continuous core/planner APIs and calls neither legacy `SyntheticEntityCore.step()` nor `DeliberativePlanner.deliberate()`.
- One `COGNITION_CONTINUE` consumes at most one explicit pending cognitive work item.
- `cognitive_tick`, planner `internal_tick`, and `total_cycles` increment once per continuation; EventSequence and float64 WorldTime remain independent.
- External sensory evidence is applied once in the observation transaction. Predictions, trace, previous action/context, active homeostasis, planner commit, and action are committed once after quiescence.
- Wake/continue payloads carry a monotonically increasing generation. Stale events are deterministic no-ops.

## QUIESCENCE MODEL

`QUIESCENT` iff a valid candidate exists, `pending_work` is empty, no deduplicated invalidation key remains pending, and the session is not finalized. There is no stable-count, repetition count, numeric epsilon, elapsed-time, timeout, minimum-cycle, or maximum-cycle stopping rule. The diagnostic guard reports generation, WorldTime, pending kinds, recent work history, and Goal ID, then raises without forcing an action.

## COGNITIVE WORK TYPES

- `RECALL`: seeded by a new sensory episode or a changed Goal/cue/revision; performs retrieval and exactly one recall stimulation.
- `PROPAGATE`: caused by a recall/internal activation and carries explicit seed Cognits.
- `IMAGINE`: caused by a new/invalidated working-state and Goal input.
- `PLAN_REFINE`: caused by new futures; runs one existing bounded `_search`. A Goal/subgoal change invalidates the candidate and creates a new recall chain.

## CAUSAL WORK CHAIN

    RECALL
      -> PROPAGATE
      -> IMAGINE
      -> PLAN_REFINE
      -> EMPTY
      -> QUIESCENT

The internally changed-Goal fixture produces two such chains before quiescence.

## RECALL SEMANTICS

Recall may repeat only when its exact semantic key `(Goal ID, target IDs, working revision)` changes. Pending work identities are deduplicated. Repeated scheduler events alone cannot rerun recall or stimulate a Cognit: **NO**.

## CONTINUOUS BUDGET

`max_deliberation_cycles` participates in continuous behavior: **NO**. The frozen legacy `deliberate()` retains its original budget. With the continuous maximum set to 1, the tested session still naturally performs three cycles and matches a maximum of 12.

## FRONTIER PERSISTENCE

Continuous `.seworld` schema version 3 persists cognition generation/phase, ordered pending work and keys, working revision, last recall key/result, work history, current candidate, working IDs, semantic caches, planner counters/finalized state, pending action/commit flag, and exact scheduler frontier. Event-by-event continuation passes at all seven required work boundaries. No consumed v3 work replays after load. v1 retains its explicit legacy pending-wake adapter; v2 unfinished stable-counter sessions migrate conservatively into one causal recall chain and never resume `stable>=2` semantics.

## HOMEOSTATIC EVENT SEMANTICS

- Passive Cognit/Relation/memory/Goal evolution remains lazy elapsed-time behavior.
- Recall stimulation, waves, and final active homeostasis remain causal activation operations. Same-time continuations invent no elapsed `dt`.

## DETERMINISM

- `PYTHONHASHSEED=1`: `f527b2d204acb87a7279e53783e66d3640086eba1bb70577653d855f21da2685`
- `PYTHONHASHSEED=77`: `f527b2d204acb87a7279e53783e66d3640086eba1bb70577653d855f21da2685`
- Renderer sampling and arbitrary host work between continuation events are observational.

## CONTINUATION COUNTS

- Small deterministic simple/Goal-invalidation sample: **min 4 / mean 6.0 / max 8** continuation events.
- Ordinary 20-decision sample: **min 4 / mean 4.0 / max 4**; these values are observations, not invariants.
- Ordinary sample mean native FFI calls per continuation: **15.16**.
- Session-local working state and semantic caches persist across events and save/load.
- `full_graph_sync_calls == 0`: **PASS**.
- Normal native Python physical World calls: **0 / PASS**.

## FRONTIER TESTS

- Event-driven cognition frontier focused module: **18 passed**.
- Frontier plus continuous runtime modules: **31 passed**.
- Elapsed/native/causal/legacy compatibility selection: **81 passed**.
- Full pytest: **201 passed**.
- CTest Release: **1/1 passed**.
- Long 5K/10K benchmarks were not run.

## FIRST FAILURE

None.

## NEXT GATE

**CONTINUOUS WORLD COMPLETION**

Not started. It covers `WORLD_SPAWN` absolute-time scheduling, maintenance timers, and removal of the remaining heartbeat dependency.

## FRONTIER MODIFIED FILES

- consciousness/planning.py
- simulation/continuous.py
- tests/test_v053_continuous_runtime.py
- tests/test_v053_cognition_frontier.py
- CURRENT_STATUS.md

## ELAPSED-TIME LAZY COGNITION

ELAPSED-TIME LAZY COGNITION: PASS

## CORRECTIVE PASS

Blocker 1 — homeostatic clamp and save invariance:

- Continuous Cognits preserve an unclamped float64 latent homeostatic threshold.
- The behavior-visible threshold remains clamped to the configured minimum/maximum.
- Intermediate reads no longer discard latent motion beyond either clamp boundary.
- Split versus one-shot evolution passes for 0.1+0.2, 0.25+0.75, 1+9, and 1000 seconds at both clamps.
- Reading every 0.01 seconds matches one touch after 10 seconds.
- Continuous save_graph no longer performs its legacy all-Cognit catch-up.
- No-save, save-without-load, and save/load branches converge to identical behavior-affecting Cognit and latent state.
- Continuous .seworld capture now snapshots semantic state before capturing the matching native/frontier payload.

## BLOCKER 2 — TARGET MEMORY

**PASS**

- Candidate discovery is conservative: exact relation-token hits and directly associated places are always admitted.
- Zero-token-overlap candidates use participant-count plus 0.001-wide maximum-confidence buckets.
- For participant counts n/m and bucket upper confidence c, the admissible bound is:
  - roles = min(n,m) / max(n,m)
  - role_support = min(1,n/m)
  - structural_upper = 0.2 * roles * min(c,target_confidence)
  - strength_upper = (0.1 + 0.65 * structural_upper + 0.25 * role_support) * c
- Recency is bounded by 1. Group mean confidence and every member confidence cannot exceed the bucket upper bound, so a place whose exact zero-overlap score can reach 0.12 cannot be excluded.
- Exact relation-token matches bypass the zero-overlap bound; direct associations bypass all structural pruning.
- Existing memory_structure.match, relevance, recency, and final threshold scoring remain authoritative after admission.
- Adversarial high-confidence/no-token-overlap recall: **PASS**.
- Low-confidence final rejection: **PASS**.
- Participant-count, stale/fresh, and direct-association cases: **PASS**.
- Deterministic randomized differential: **80 worlds passed; 0 false negatives**.
- Full-scan oracle is test-only and is not called by runtime.
- Strengthened scaling result:
  - total memories: **10,000**
  - total places: **5,000**
  - exact-token matching places: **2**
  - zero-token/high-confidence recallable places: **2**
  - candidate places: **4**
  - candidate memories: **8**
  - memories materialized: **8**

Blocker 3 — causal Goal persistence:

- Passive waiting applies only goal_decay raised to elapsed simulated seconds.
- Understanding is applied exactly once at the cognitive event that produced it.
- A new observation never changes decay over the preceding silent interval.
- Low-before/high-after and high-before/low-after causal-order scenarios pass.
- Ten observations at exact one-second cadence match the frozen per-observation multiplicative formula.
- Goal age remains a causal/event count.
- Continuous save/load preserves Goal time anchors and exact continuation.

## TIME SEMANTICS

Elapsed-time state:

- Cognit activity, utility, inactive trace, latent/visible homeostatic threshold, last touch, and last activation time
- Relation passive confidence and separate confidence/evidence time frontiers
- memory confidence, confirmation time, recency, and idle duration
- Goal passive persistence, creation time, unavailable duration, and cooldown timestamp

Event/count state retained:

- EventSequence, event IDs, cognitive_tick, and last_activated_cognitive_tick
- evidence windows, support, confirmations, contradictions, and prototype evidence
- prototype occurrences and explained_sum
- percept observation age and missing_ticks
- wave/refractory steps
- Cognit age and low_retention_ticks
- planner depth, expansions, tie cursors, and subgoal attempt cooldown
- Goal age, attempts, interventions, completions, and causal observations

## COMPLEXITY

- Native dormant Cognits: **100,000**
- Elapsed jump: **1,000 seconds**
- Materialized before touch: **0**
- Materialized after touching {7, 19}: **2**
- Target memories: **10,000**
- Target candidate/materialized memories: **8 / 8**
- No time-advance graph scan and no target full-memory scan remain in the continuous path.

## PERSISTENCE

- Clamp-crossing latent frontier: **PASS**
- Save is behaviorally observational: **PASS**
- No-save == save == save/load: **PASS**
- Exact .seworld continuation at 12.001, 12.149, 12.437, and 12.999 seconds: **PASS**
- Relation semantic-identity frontier restore: **PASS**
- Memory and Goal elapsed anchors: **PASS**

## TESTS

- Corrective elapsed, target-memory, and continuous acceptance set: **51 passed**
- Elapsed-time focused module: **32 passed**
- Target-memory adversarial/randomized/scaling module: **6 passed**
- Continuous runtime module: **13 passed**
- v0.5.2 native/causal compatibility subset: **43 passed**
- Full pytest: **183 passed**
- CTest: **1/1 passed**
- Release native rebuild: **PASS**
- full_graph_sync_calls == 0: **PASS**
- Normal native Python physical World calls: **0 / PASS**
- Render sampling invariance: **PASS**
- Long 5K/10K benchmarks were not run.
