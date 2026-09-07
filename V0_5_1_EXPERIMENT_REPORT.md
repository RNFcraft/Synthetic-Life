# Synthetic Entity v0.5.1 Stabilization

## Summary

Evidence-based memory, real internal cycles, cognitive target input, bounded graph planning, N-body feedback/conflicts, and persistence boundaries are integrated. The version is not yet behaviorally complete enough to be the Python reference: construction tasks failed.

## Problems Found in Initial v0.5.1

Place identity was an exact frame signature; recall ignored confidence; deliberation did not recompute decisions; targets existed only in an evaluator; subgoals were scaffolding; body feedback was global; multi-intents were order-sensitive; `.sebrain` retained transient episode state.

## Place Memory Redesign

Matching combines rotation-tolerant views, learned feature stability, self-action transition evidence and visit history. Places retain multiple egocentric views and may form confidence-gated alias links or competing hypotheses. No World coordinate is stored. Bounded validation reported mean fragmentation 1.0 and aliasing 1.0, but this is not broad-map evidence.

## Persistent Object Memory

Re-identification uses features, state, Place context, relative context, elapsed time and confidence. `CONFIDENT`, `UNCERTAIN`, `WEAK` and `CONTRADICTED` states affect use without immediate deletion.

## Functional Recall

Retrieval strength is relevance × confidence × support and enters ordinary graph activation. Memory-enabled: one memory created, 104 reactivations, reacquisition at tick 15. Disabled: zero reactivations and no reacquisition within 120 ticks. The proximity-based `return_attempted` metric stayed false, so this is reacquisition—not proof of intentional return navigation.

## Internal Deliberation

Cycles can retrieve memory, change activation, propagate waves, update predictions/uncertainty, rebuild plans and recompute action scores without a World step. Stable rankings/plans or the configured bound stop deliberation.

## Multi-Step Planning

Bounded beam search uses acquired SELF_ACTION Place relations. Score includes Goal alignment, prediction and memory confidence, loop risk and action cost. Plans are rebuilt/revalidated after observation.

## Hierarchical Goals

Planner-created child Goals use intermediate cognitive states and can complete and resume a parent. Focused tests demonstrate the lifecycle. The behavioral curriculum runs created zero subgoals because relevant object/place memory was not acquired.

## Curriculum Integration

Targets become translation-tolerant target Cognits and persistent Goals describing only desired relative structure. They contain no object IDs, assignments, chosen location, route or World coordinates.

## Blind Manipulation

Empty-context GRAB/INTERACT counters are explicit. Both 120-step comparisons recorded zero blind actions because neither action was selected. The stopped endurance run reached 10,000 ticks: 0 GRAB, 0 INTERACT, 1,000 push attempts, 11 successful pushes. No declining blind rate can be claimed; lack of manipulation diversity is the stronger failure.

## Multi-Entity Corrections

Resistance/outcome/holding/sensing are per body. Destination and resource conflicts are classified from one pre-commit state. Same-cell entry, body occupancy/swap, shared object actions and release destinations resolve deterministically with rotating fairness. Push/release cannot enter another body.

## Social Memory Foundation

Another body remains an ordinary appearance/motion structure. The N=2 run recorded 240 mutual-visibility events and 843/719 structure reactivations. This is not evidence of cooperation or agent modelling.

## Persistence

Multi `.seworld` includes all cores, bodies, held objects, RNG, clock, fairness, goals, memory, planners and traces with deterministic continuation. `.sebrain` v2 separates `COGN`, `RELA`, `PATT`, `SPAT`, `LEAR`, optional `LANG`; transfer clears tracks, Goal, trace, active state and plan cursor.

## Behavioral Experiments

Memory reacquisition succeeded only with memory enabled. `pair` and `line3` both failed within 120 actions for persistent and fresh brains, with zero object movement. N=2 produced no conflicts or joint interactions despite mutual visibility.

## Ablations

Minimal deliberation: 120 cycles, 83.11 actions/s, 23 plan revisions. Adaptive: 366 cycles, 18.13 actions/s, 55.29 cognitive cycles/s, 44 revisions. Both made zero World modification, so no task benefit was demonstrated. Memory ablation failed where enabled memory reacquired.

## Performance

Bounded: minimal 83.11 physical actions/s; adaptive 18.13 physical actions/s and 55.29 cognitive cycles/s. The 10K endurance checkpoint took 822.44 s (12.16 actions/s), showing serious graph-growth degradation.

## Known Failures

- No `pair` or `line3` construction and no measured object movement.
- No GRAB/INTERACT exploration in measured runs.
- No naturally reached planner subgoals in curriculum runs.
- No demonstrated task-progress benefit from additional deliberation.
- No spontaneous N=2 conflicts or joint object effects in the bounded run.
- Long-run performance degrades substantially.

## Scientific Interpretation

The controlled result supports persistent representation and confidence-weighted retrieval. It does not establish object permanence, reliable return navigation, construction competence, cooperation, or useful adaptive deliberation.

## Readiness for v0.5.2

**NO.** Technical integration is stronger, but behavioral acceptance requires useful manipulation and pair/line3 progress driven by planning/subgoals. Those requirements remain unmet.

## FINAL BEHAVIORAL COMPLETION PASS

### Relational Grounding and Target Mismatch

Current perception, persistent arrangements and targets now use the same anonymous pairwise relation tokens (direction class and distance class). Matching is translation, rotation and reflection invariant for the present curriculum. The Core computes mismatch without calling the external evaluator. Controlled complete/far/partial inputs ordered correctly. TARGET Cognits connect to the same RELATIONAL Cognits activated by observation.

### Affordance Learning and Goal-Relevant Recall

Action-context evidence generalizes by overlap of active Cognits. Unknown contexts have epistemic value; repeated no-effect trials reduce it; effectful contexts retain distinct consequence/progress evidence. This evidence controls exploration uncertainty while durable consequence prediction remains graph-native rho. Recall no longer receives a generic target constant: relevance comes from relational match and unresolved participant support at remembered Places.

### Subgoals and Place Aliases

Planner value now includes acquired contextual mismatch reduction. Alias hypotheses create confidence-weighted graph links usable by recall and planning. In the final runs, pair created/completed 29 intermediate Goals; line3 created 247 and completed 246. The high rate indicates subgoal churn rather than efficient hierarchy.

### Internal Clock and Persistence Fixes

`cognitive_tick` is monotonic across physical observation and internal cycles, while memory decay and contradiction remain on experience/world ticks. `.seworld` persists the cognitive clock and action context for deterministic continuation. Brain transfer preserves historical Places but explicitly resets `current_place_id` and transient localization.

### Social Metrics

External telemetry correlates appearance signatures with the specific persistent memory Cognit; it no longer labels global reactivation as social recall. Joint interaction requires two entities to address the same physical object within a bounded window. A 60-step controlled run measured 34 encounters, 7 reidentifications and 2 joint-object interaction events.

### Performance

Profiling attributed 75.9/81.9 profiled seconds to repeated `loop_score` calls from planning, including repeated Trace signature construction. Caching immutable signatures and repeated predicted-state loop scores reduced an ordinary 120-step run to 3.48 seconds. The 1000-action curriculum run still slowed to 6.70 physical actions/s and 31.81 cognitive cycles/s as state grew, so scaling remains unresolved.

### Behavioral Results

Pair, 500 actions: failure; mismatch 1.0 to minimum 0.9; 56 GRAB/1 success, 11 RELEASE/1 success, 2 push attempts/2 success, 264 INTERACT/0 success, 29 subgoals. Net World modification returned to 0.0.

Line3, subsequent 500 actions with the same brain: failure; mismatch 1.0 to minimum/final 0.9333; World modification 41; 105 GRAB/1 success, 26 RELEASE/1 success, 12 pushes/12 success, 114 INTERACT/0 success, 247 subgoals.

The action-collapse defect is removed, but exploration now overuses blind INTERACT (264 and 114 trials). Structural progress is measurable but weak and did not produce either target.

### Remaining Failures

- Pair and line3 still fail.
- Context generalization is too coarse: blind INTERACT remains excessive.
- Subgoal lifecycle thrashes instead of maintaining a useful hierarchy.
- Learned mismatch reduction is not yet strong enough to guide reliable manipulation.
- Long-run planner performance remains below reference quality.

### Final Reference Decision

**NO.** Shared relational grounding, meaningful mismatch, autonomous manipulation discovery, selective recall, real behavioral subgoals, clock correctness and precise social telemetry now exist. Reliable goal-directed progress, exploration calibration, hierarchical stability and sustained performance still block reference status.

## PARTICIPANT-BOUND DEVELOPMENT PASS

### Relational Belief Model

The former relation-token multiset was replaced by a persistent `BeliefScene`. Every participant is a persistent internal memory Cognit; every bound spatial belief preserves source Cognit, target Cognit, relation token, confidence and observation time. A bound-relation Cognit connects both endpoints in rho. Participants and relations persist outside FOV. An episode tag prevents historical participants transferred through `.sebrain` from being treated as localized in a new World before re-observation.

### Anonymous Role Binding

Target matching now searches deterministic participant subsets rather than comparing the complete camera scene. Role assignment is independent of participant insertion order, translation, configured rotation/reflection, and unrelated extra participants. The best binding records specific internal participant Cognits and unresolved role count.

### Prediction and Affordance Boundary

Affordance evidence retains contextual trial/effect uncertainty but always returns zero target progress. Predicted target progress is computed from action-conditioned graph rho predictions of endpoint-bound relation Cognits and then compared with the anonymous target. Camera-only mismatch change is no longer stored as action value.

### Subgoal and Time Corrections

Child Goals derive from an unresolved binding and a specific unbound remembered participant. Equivalent children receive a 16-world-tick hysteresis period. Internal-cycle active state is replaced by each new propagation result plus current recall instead of monotonically unioning all prior nodes. Cognitive timestamps govern activation/refractory processing; world timestamps govern memory and relational observation age.

### Experiment Harness

`World.initialize_controlled_objects` validates unique in-bounds positions, assigns unique IDs, resets held state, sets `next_object_id`, creates spawn/baseline records and disables spawning. The development artifact contains settings, initial configurations, full mismatch histories, actions/effects, subgoals, memory, graph size and performance for every episode.

### Development Experiment

Three 60-action pair episodes accumulated one durable brain. Three held-out placements then compared copies of that brain with fresh and relational/action-ablated controls.

- Experienced: 0/3 success, mean minimum mismatch 0.2842, mean World modification 1.3333, mean blind INTERACT 4.6667.
- Fresh: 0/3 success, mean minimum mismatch 0.6959, World modification 0, mean blind INTERACT 15.3333.
- Ablated: 0/3 success, mean minimum mismatch 0.0600, World modification 0, mean blind INTERACT 14.0.

The experienced brain changed the World and outperformed fresh mismatch/blind-action metrics. However, ablation achieved still lower mismatch without physical change. Therefore the experiment does **not** demonstrate a reusable causal capability: observation/re-identification can still create favorable believed bindings without learned manipulation knowledge.

### Current Performance Profile

60 profiled steps took 3.83 seconds. Cumulative hotspots: deliberation 3.10 s, planner search 2.18 s, imagination 0.998 s, graph action predictions 0.969 s, physical cognitive step 0.686 s, loop score 0.574 s. No additional large endurance run was justified.

### Reference Decision

**NO.** Participant-bound belief, anonymous role assignment, graph-owned target prediction, persistence boundaries and a valid development experiment now exist. Reference status is blocked because experienced cognition did not beat the knowledge ablation, no held-out pair completed, and belief correction can still lower mismatch without corresponding physical structural change.

## Correctness and causal-learning pass (2026-09-04)

The earlier negative conclusion was used as a gate, not hidden. The pass corrected simultaneous co-observation, endpoint identity, disappearance-as-participant errors, fully violated role binding, relation-state subgoals, and relation-materialization quota starvation. Structural progress is now an intervention query over materialized action-conditioned `SELF_ACTION` rho; ordinary temporal succession cannot make every action appear equally causal.

Focused proof: repeated physical `MOVE_UP` pushes changed the bound pair relation from Manhattan distance 2 to 1 and materialized a bound relation-effect rho (support 20). After clearing all temporary `TransitionModel` evidence, the graph still predicted the effect. The single-action trace records mismatch 1.0→0.0, physical distance 2→1, and predicted progress 0.8.

The reduced paired held-out development test used one seed, five training episodes, five translated pair evaluations per group, and a 30-action cap. Experienced completed 5/5 in one action (mean first useful action 0); fresh completed 5/5 in three actions (mean first useful action 2); causal-rho ablation completed 0/5. All groups had zero unnecessary physical modifications. Full raw data and trace are in `runs/v051-causal/result.json`.

The exact broken link found during this pass was **graph effect → action discrimination**: unconditioned `SEQUENTIAL` rho initially gave every action the same predicted progress. Restricting structural progress to matching action-conditioned rho repaired that link. Within the deliberately narrow translated-pair scope, the reusable causal capability now beats fresh by latency and beats causal-rho ablation by external success. This clears the correctness pass for moving to v0.5.2; it is not evidence of general construction ability across shapes or orientations.

## v0.5.1 FINAL PYTHON REFERENCE

**Status: STABLE PYTHON RESEARCH REFERENCE.** The implementation is frozen as the executable oracle for v0.5.2. It demonstrates participant-bound simultaneous spatial belief, endpoint-preserving binding and prediction for pair/line3/L/square/plus, distinct world/cognitive clock fields, frozen-world evolving deliberation, and the acquired causal pair chain: physical push → action-conditioned evidence → materialized SELF_ACTION rho → evidence cleared → graph prediction survives → first action changes. The paired result is experienced 5/5 in one action, fresh 5/5 in three actions, and causal-rho ablation 0/5 under a 30-action cap.

Final generalization boundary (`runs/v051-generalization/result.json`): translated vertical and vertical-with-distractor transfer on action 1; distance 3 completes in two interventions; horizontal/mirrored approach and opposite body orientation fail 0/30. No hardcoded rotation/action remapping was added. This does **not** demonstrate general shape construction, orientation-equivariant action knowledge, language, 3D cognition, or a complete intelligent agent. Growing Python graph/planner throughput remains the principal engineering limitation; further optimization moves to C++.
