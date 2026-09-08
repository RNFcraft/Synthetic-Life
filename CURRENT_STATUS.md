# Synthetic Entity v0.5.3 — Current Status

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

## FIRST FAILURE

None.

## NEXT GATE

**TRUE EVENT-DRIVEN COGNITION FRONTIER**

That gate has not been started.

## MODIFIED FILES

- consciousness/memory.py
- tests/test_v053_elapsed_corrections.py
- V0_5_3_CONTINUOUS_RUNTIME_PLAN.md
- CURRENT_STATUS.md
