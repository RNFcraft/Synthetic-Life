# v0.9.3a — Homeostatic Credit Assignment & Exact Determinism Audit

**AUDIT COMPLETE / REPRESENTATIONAL-TRANSFER LIMIT IDENTIFIED.**
The credit path is localized without a valid general repair. The proven
selectivity ordering bug is fixed: declared reverse-order **64/64 exact**,
expanded hashseed **6/6 exact**. See [complete results](V0_9_3A_RESULTS.md).

Base: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65`, main, with existing
uncommitted v0.9.2 implementation. The frozen v0.9.2 FAIL and thresholds remain
unchanged. This audit is separate from planned v0.9.3 long-run stability.

## Pre-implementation design note

1. Native World consumption removes the resource and queues its physical payload;
   `ContinuousRuntime._process` transfers the consequence into
   `Physiology.apply_consequence` at WORLD_ACTION_COMPLETE.
2. `InteroceptiveTransducer.sample` floors reserve/max ratios into sensor bins.
   Full SENSORY_CHANGE samples them; maintenance schedules a passive observation
   only on a coarse change, retaining the external frame.
3. `record_action_attempt` retains observed source IDs/time/action;
   `record_action_outcome` supplies success. `_learn_timed_observation` consumes
   this context at the actual completion observation, otherwise learns passively.
4. `_acquire_timed_transition` updates outcomes, window evidence, timing moments,
   then native `materialize_current` considers source/target pairs.
5. Native window counts determine probability/lift/support; confidence is
   support/(support+confidence_k). Timing uses cumulative Welford moments.
6. Admission checks minimum support/lift, self-edge exclusion, per-step creation
   quota and graph capacity. Consolidation separately checks support/confidence.
7. Core lifecycle pruning removes weak/stale knowledge; native relation slots are
   reused by generation. Pattern/composite identity and deletion affect endpoints.
8. `.sebrain` saves materialized graph, semantic patterns, timing moments, durable
   memory/beliefs/language. It deliberately omits transition window, pending action,
   last observation, active state, body reserves and planner session.
9. `homeostatic_effects` queries SELF_ACTION; `successors` requires matching type,
   action, timing support, probability floor, depth and horizon.
10. `_search` adds 0.8 times confidence-weighted progress toward target bins.
    Positive means improvement; highest total score wins. Other existing terms
    include alignment, confidence, memory, epistemic, target progress, loop and depth.
11. `homeostatic_valuation_enabled=False` disables internal estimates and their
    score/refinement path, including temporal projection within that path.
12. Thus NO_MOTIVATION may also preserve a different projected state/confidence,
    which can change later beam candidates; it is not just removal of one bonus.
13. Python sets, dicts built from sets, native unordered containers, relation slot
    traversal and restoration order require investigation, not blanket sorting.
14. Prediction products, mean errors/calibration, wave sums and planner confidence
    can depend on floating-point reduction order. No rounding is permitted.
15. Scheduler total order is `(WorldTime, monotonically increasing event id)`;
    there is no priority or pointer tie-break. Same-time batches retain ID order.
16. Scheduler/World/Cognit/goal/percept counters are instance-owned. Native static
    state and observer contamination remain hypotheses until differential evidence.
17. Cognit IDs are allocated by insertion; relation handles by slot/generation;
    percept and goal IDs by instance counters, event IDs by scheduling order.
18. Compare graph numeric/semantic state, calibration window, transition history,
    frontier/session, RNG, scheduler and physiology before blaming final digest.
19. A generic optional event observer receives before/after notifications around
    the existing handler. Default is None, with no experiment import. The sink
    reads existing APIs only, streams JSONL and keeps one prior state. Metadata
    never enters graph, equality, planning, persistence or the simulation RNG.
20. Compare OFF/ON action sequence, trajectory, physiology, graph and final digest,
    RNG and scheduler, with zero full graph sync. Snapshot reads must first pass
    a repeated-read inertness check; diagnostic reads cannot assume purity.

## Predeclared controlled protocol

Single episode: frozen adjacent training scenario, seed 92001, horizon 6 seconds.
Repeated audit: exactly 8 episodes with the same geometry and seeds 92001..92008,
carrying only `.sebrain`; no forced actions. A second diagnostic episode uses the
frozen Stage-1 experienced checkpoint to observe an autonomous consumption without
rescue training. Stage-2 FULL/NO_MOTIVATION uses the same frozen Stage-2 brain,
scenario and seed 92101. Stage-1/2 scientific reruns require micro acceptance.
No Stage-3/4 behavioral evaluation is authorized by this audit; the declared
64-case determinism subset is a separate reproducibility check.

If cumulative timing survives but pair support is lost at fresh-episode reset,
do not substitute timing count for support: it lacks the negative-trial denominator.
That would change the formalism, not repair a demonstrated implementation omission.

## Completed acceptance

Frozen v0.9.2 FAIL/results/thresholds preserved. Trace is causally inert in fresh
and transferred episodes, including a full Stage-2 brain/seed pair; graph sync
count is zero. Normal/full verification: **754 pytest PASS**, focused **203 PASS**,
forensic/architecture **29 PASS**, Release CTest **2/2**, observer-OFF CTest **1/1**
and observer-OFF Python **164 PASS**. `git diff --check` passes.
Stage-1/2 scientific reruns stop at failed micro acceptance; Stage-3/4 broad
survival reruns and long-run soak were not run. The declared reproducibility
subset and specific scarcity_b divergence reproduction remain separate audits.
