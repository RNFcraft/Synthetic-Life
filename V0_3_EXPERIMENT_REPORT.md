# Synthetic Entity v0.3 Experiment Report

## Summary

v0.3 removed fixed-order directional bias, separated missing representation from known prediction failure, implemented short-horizon perceptual continuity and learned sensorimotor shifts, and introduced graph-shaped temporal composite Cognits. All 32 tests pass. The graph remained sparse and activity remained homeostatic. These results describe observed adaptive dynamics and do not establish object understanding, object permanence, abstract reasoning, consciousness, or life.

## Changes from v0.2

- Epsilon-set `SymmetryPreservingTieResolver` with bounded balanced history.
- `prediction_error_valid`, representation coverage/error and continuity error.
- LocalPercept and internal PersistentPercept π tracks.
- Per-action Welford sensorimotor displacement statistics.
- Anchored and translation-tolerant structural patterns.
- PatternNode/PatternRelation graph structures and recursive composite κ.
- Richer loop state including π, Action, Goal and error/tension values.
- Goal target availability and retirement.
- Rolling Brier/ECE calibration diagnostics.
- Snapshot schema v3 and a five-tab UI.
- Retention score and scheduled dependency-aware deletion candidates.

## Environment and protocol

Experiments ran CPU-only on Windows with CPython 3.11.9. Required production target remains Python 3.12+. The final suite used:

- synthetic exact-tie sequence: 10,000 decisions;
- symmetric immutable sensory frame: 10,000 ticks;
- seed 123: 10,000 and 100,000 ticks;
- seeds 0–9: 50,000 ticks each using four workers;
- schema-v3 save/load/continue and Pygame dummy-display smoke tests.

Absolute positions and physical loops were measured only by external Simulation telemetry/experiment code.

## Directional bias experiment

The symmetric sensory run produced:

| Action | Count |
|---|---:|
| MOVE_UP | 2,434 |
| MOVE_RIGHT | 2,434 |
| MOVE_DOWN | 2,433 |
| MOVE_LEFT | 2,433 |
| IDLE | 134 |
| INTERACT | 132 |

The direct exact-score test also balanced 10,000 ties with maximum directional difference one. A score advantage larger than epsilon was selected on every test iteration.

Across the ordinary 10-seed runs (500,000 ticks), movement totals were UP 107,245; RIGHT 107,251; DOWN 107,112; LEFT 106,952. The maximum difference was 299, or 0.07% of 428,560 movement actions. This replaces v0.2's measured MOVE_UP share of approximately 54.6%.

Tie resolution across ten runs: 281,026 ties; LEAST_USED 160,339, OLDEST_USED 120,657, ROTATING_CURSOR 30. The cursor was therefore only a final exact-symmetry fallback.

## Empty-active-set experiment

An unknown symmetric frame with no matched κ produced high representation error, neutral known prediction error, `prediction_error_valid=False`, finite tension, and no NaN/Inf. Repeating the observation accumulated ProtoPattern support; after κ birth, coverage rose and representation error fell. Missing representation no longer forces known prediction error or novelty to exactly one.

## Perceptual continuity experiment

Unit tests showed that a compatible one-cell pattern displaced by one egocentric cell retained the same π ID. A compatible pattern missing for one or two ticks resumed its π; absence beyond the configured window closed it. An incompatible nearby channel/state pattern created a different track. No LocalPercept or PersistentPercept field contains world object identity, World, Grid, or absolute coordinates.

Across 10×50K, tracks created averaged 5,262.8 (2,246–7,013) and completed track lifetime averaged 14.04 ticks (13.23–14.45). Tracks are removed from active storage after closure, so runtime does not rescan historical π objects.

## Sensorimotor learning experiment

All action transform statistics began at zero support and zero mean. Seed-123 at 100K learned:

| Previous action | Mean observed egocentric shift |
|---|---:|
| MOVE_RIGHT | (-0.398, -0.009) |
| MOVE_LEFT | (+0.377, -0.002) |
| MOVE_UP | (-0.003, +0.403) |
| MOVE_DOWN | (-0.004, -0.369) |
| IDLE | (+0.011, -0.015) |
| INTERACT | (+0.011, +0.002) |

The expected opposite egocentric displacement emerged from matched π transitions; it was not encoded by action rules. Magnitudes below one reflect missing/ambiguous percepts, object motion and matching noise.

## Composite Cognit experiment

Repeated synthetic A→B→C produced a CompositeCandidate and, after configured support, a composite κ. A single occurrence did not. Shuffled A/B/C sequences with identical marginal frequency did not build the same support. The born composite activated when its sequence recurred. A composite plus another κ formed a depth-two pattern in the recursive test. Dependency protection prevented deletion of referenced children.

World runs produced many depth-one composites: 189 of 466κ at 10K, 420 of 1,638κ at 100K, and a multi-seed mean of 396.8 composites. Deeper abstraction did not arise in the reference world runs; only the controlled test demonstrates the recursive mechanism.

## 10K results — seed 123

- Runtime: 8.26 s; 1,210 ticks/sec.
- Cognits: 466 total; 277 primitive; 189 composite.
- Relations: 0; density 0.
- Mean active ratio: 0.00517; p95 0.01736.
- Mean wave energy: 0.2926.
- Mean representation coverage: 0.9815.
- Mean known prediction error: 0.5070.
- Mean continuity error: 0.0842.
- Mean Brier score: 0.2556.
- Mean internal loop score: 0.0501.
- π created/closed: 375/374; mean closed lifetime 12.73.
- Goals generated/retired: 262/46.
- Unique external positions: 165; longest physical loop: 38.
- Movement counts: UP 2,328; RIGHT 2,330; DOWN 2,324; LEFT 2,323.

## 100K results — seed 123

- Runtime: 498.47 s; 200.6 ticks/sec.
- Cognits: 1,638 total; 1,218 primitive; 420 composite.
- Relations: 95; density `3.54×10⁻⁵`.
- Mean active ratio: 0.00269; p95 0.01068.
- Mean wave energy: 1.1242.
- Mean representation coverage: 0.9970.
- Mean known prediction error: 0.3827.
- Mean continuity error: 0.1550.
- Mean Brier score: 0.1610.
- Mean loop score: 0.1064.
- π created/closed: 10,320/10,318; mean lifetime 14.10.
- Goals generated/retired: 2,694/1,285.
- Unique external positions: 617/625; longest physical loop: 50.
- Movement counts: UP 21,539; RIGHT 21,625; DOWN 21,626; LEFT 21,534.
- Tie count: 57,632.

The 100K run was completed before the final scheduled-retention bookkeeping patch. That patch does not alter action, percept, composite, wave or prediction equations, and its 10K regression remained deterministic; nevertheless this provenance is stated explicitly.

## Ten-seed aggregate — 10 × 50K

| Metric | Mean | Min | Max |
|---|---:|---:|---:|
| Throughput per worker | 191.97 | 111.31 | 314.81 |
| Cognits | 1,325.7 | 1,040 | 1,579 |
| Primitive Cognits | 928.9 | 692 | 1,096 |
| Composite Cognits | 396.8 | 172 | 547 |
| Relations | 38.3 | 0 | 222 |
| Relation density | 0.000020 | 0 | 0.000105 |
| Mean active ratio | 0.00623 | 0.00176 | 0.01469 |
| p95 active ratio | 0.01225 | 0.00894 | 0.01406 |
| Mean wave energy | 1.1346 | 0.4334 | 1.6312 |
| Known prediction error | 0.3945 | 0.3475 | 0.4899 |
| Representation coverage | 0.99295 | 0.99201 | 0.99437 |
| Continuity error | 0.1673 | 0.07399 | 0.20763 |
| Brier score | 0.2053 | 0.1065 | 0.4640 |
| Internal loop score | 0.1222 | 0.05397 | 0.16769 |
| Track lifetime | 14.04 | 13.23 | 14.45 |
| Unique external positions | 463.5 | 321 | 530 |
| Longest physical loop | 47.5 | 26 | 65 |

Goal generation averaged 1,347.2 and unavailable-target retirement averaged 700.8 per seed. External exploration increased relative to v0.2's 116–198 positions, but this was neither rewarded nor visible to the core and is not itself an optimization claim.

## Prediction and calibration

Known prediction error and calibration vary substantially between seeds. Mean Brier ranged from 0.107 to 0.464. High representation coverage does not imply calibrated future prediction. Noisy-or still double-counts correlated sources, and binary active observations can make error sharp. ECE is available per tick/UI/JSONL but was not aggregated by the multi-seed summary, so no aggregate ECE claim is made.

## Loop behavior

The richer test distinguishes identical κ sets with changing actions/goals from a fully repeated internal A↔B sequence. Multi-seed mean internal LoopScore was 0.122. Physical loop runs remained 26–65 ticks. The physical metric is external and not used by action selection.

## Performance and profiling

A 3K profile attributed the largest early cost to six imagined futures, transition predictions and controllability queries. A full-pattern redundancy scan and historical closed-track scan were found and removed. Remaining long-run degradation is dominated by growing κ and O(κ) homeostatic work. Composite candidate work is bounded to recent windows and at most 1,024 candidates; π matching uses only open tracks.

v0.3's 100K throughput (200.6 ticks/sec) is below v0.2's 690 ticks/sec. Correctness and observability were prioritized, but global homeostasis must become lazy/scheduled before large-scale graph work.

## Ablation context

A full runtime-toggle ablation was not added because maintaining two divergent core loops would compromise the stable architecture. Available comparison:

- v0.2 ordinary 500K movements: MOVE_UP 273,174 versus roughly 42–48K for each other move.
- v0.3 tie resolver plus full continuity/composition: four movements all near 107K.
- v0.3 symmetric frame: exact balance within one.

This comparison establishes removal of the fixed-order artifact, but it does not isolate every downstream effect of continuity and composites.

## Observed failure modes

- Long-run throughput falls as κ grows because homeostasis remains globally updated.
- Several seeds materialized zero Relations under conservative support/lift evidence.
- Representation coverage near 99% may indicate over-general translation-tolerant patterns.
- Composite birth is prolific, while reference runs remained depth one.
- Composite prediction gain is a proxy rather than held-out counterfactual improvement.
- Greedy π assignment can swap identities under similar crossing observations.
- Learned transforms combine ego-motion, object motion and assignment noise.
- Goal retirement is frequent; suspended-goal resumption is absent.
- Calibration varies widely by seed.
- Short physical loops remain.

## Interpretation

The measured results support the limited technical conclusions that fixed enum-order bias disappeared, missing representation is no longer misreported as maximal known prediction failure, recurrent sensory structures can retain short-lived internal identity, sensorimotor displacement statistics can be learned without hardcoded geometry, and repeated κ sequences can create ordinary higher-depth graph nodes. They do not show semantic object concepts, general object permanence, abstract reasoning, or consciousness.

