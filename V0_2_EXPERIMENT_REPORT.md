# Synthetic Entity v0.2 Experiment Report

## Environment

Runs were performed on 2026-09-02 in Windows using CPython 3.11.9, NumPy 2.4.3 and Pygame 2.6.1. The requested target remains Python 3.12+, but the implementation and tests also ran successfully on the available 3.11 interpreter. All experiments were CPU-only and headless. Configuration is the checked-in `Settings`; world ticks occur every ten consciousness ticks.

## Experiments and seeds

Three validation layers were used:

1. Unit/integration suite: 17 tests, including homeostasis, energy conservation, lift, adaptive prediction, action conditioning, loop detection, boundary isolation and snapshot continuation.
2. Long run: seed 123, 100,000 ticks, full JSONL telemetry and schema-v2 snapshot.
3. Multi-seed behavior run: seeds 0–9, 50,000 ticks each (500,000 total), four parallel workers. Raw summaries are in `v02-results.json`.

The 10K checkpoint used seed 123. External physical-position metrics were computed by telemetry/experiment code; no absolute position entered `SyntheticEntityCore`.

## Performance

The seed-123 10K run completed in 11.82 seconds (~846 ticks/sec during that checkpoint). The 100K run completed in 144.88 seconds (690 ticks/sec) while retaining 100K records and writing JSONL. Under four-process contention, multi-seed workers averaged 326 ticks/sec (range 161–606). v0.2 is slower than the approximately 11K ticks/sec v0.1 small-graph baseline because each tick now maintains event patterns, six imagined futures, statistical evidence, goals and trace analysis.

## 10K results (seed 123)

- Cognits: 174
- Relations: 63
- Relation density: 0.0021
- Final active ratio: 0.046
- Final mean activity: 0.026
- Final maximum activity: 0.322
- Final wave energy: 1.779
- Unique external positions: 81
- Goals generated: 55

This checkpoint used the final sliding-evidence/statistical relation implementation. It no longer resembles the near-complete graph or saturated activity regime.

## 100K results (seed 123)

- Cognits: 237
- Relations: 125
- Relation density: 0.002235
- Peak active Cognits: 23
- Final maximum activity stayed finite; final active set happened to be empty.
- Final prediction error: 0.394
- Final novelty/internal tension: 1.000/0.150 (an unrepresented/empty-activation tick)
- Unique external positions: 107
- Throughput: 690 ticks/sec
- NaN/Inf scan: none found

Two independently loaded copies of the 100K snapshot produced identical world and graph state after 100 additional ticks.

## Multi-seed aggregate (10 × 50K)

| Metric | Mean | Min | Max |
|---|---:|---:|---:|
| Unique positions | 146.8 | 116 | 198 |
| Longest detected physical loop | 57.0 | 35 | 87 |
| Cognits | 478.0 | 290 | 611 |
| Relations | 123.9 | 98 | 173 |
| Relation density | 0.000639 | 0.000295 | 0.001384 |
| Mean active ratio | 0.00955 | 0.00706 | 0.01310 |
| p95 active ratio | 0.03465 | 0.02222 | 0.05556 |
| Early prediction error | 0.58799 | 0.44940 | 0.69384 |
| Late prediction error | 0.53017 | 0.39377 | 0.67464 |
| Mean wave energy | 0.71412 | 0.51031 | 1.17999 |
| Mean internal loop score | 0.08021 | 0.05321 | 0.10756 |
| Goals generated | 512.7 | 342 | 752 |
| Average goal lifetime | 101.7 | 64.1 | 143.2 |

Prediction error improved on average, but not for every seed: seeds 1 and 9 had higher late error, which indicates regime/environment dependence and incomplete model calibration.

## Cognit and Relation growth

Cognit counts varied substantially because primitive event diversity depends on trajectories and object changes. Counts remained far below the 2,048 safety cap. Relation counts remained near 100 despite hundreds of Cognits; density was three to four orders below a complete directed graph. The v0.1 problem report described about 113κ/6,806ρ at 10K (density approximately 0.54 if self-edges are excluded). Final v0.2 checkpoints measured 174κ/63ρ at 10K and 237κ/125ρ at 100K.

The main causes of the change are support+lift gating, action lift against the state conditional baseline, and a 512-transition evidence window. Safety caps were not the controlling mechanism.

## Activity and wave behavior

The multi-seed mean active ratio was 0.955%, with p95 3.465%. In the 10K checkpoint the largest node activity was 0.322 rather than persistent 1.0 saturation. The fan-out acceptance test demonstrates equal total transmitted energy for one and 100 identical outgoing Relations. Observed wave energy remained finite in all logged runs.

## Prediction, novelty and goals

Predictions are learned from observed κ transitions and conditioned action counts. Breaking a learned A→B regularity increases error, while a sustained new regime displaces evidence from the rolling window. Novelty uses rarity, actual prediction error and representation coverage. Goals were generated in every long seed and persisted for about 64–143 ticks on average, confirming inertia rather than per-tick goal replacement.

## Loop behavior and position exploration

The synthetic A→B→A→B regression trace produces a high internal loop score while a nonrepeating A→B→C→D→E trace does not. Imagined futures that reproduce trace periodicity receive a loop-risk deduction; no direction is prescribed.

External runs visited 116–198 of 625 physical cells over 50K ticks. Longest physical periodic runs were 35–87 ticks under the experiment's simple detector. This is a clear improvement over the reported approximately four-cell/6,000-tick v0.1 behavior, but not proof that all pathological loops are resolved. Internal and physical loop definitions differ deliberately.

## Action distribution

Across 500K ticks:

- MOVE_UP: 273,174 (54.6%)
- MOVE_DOWN: 48,412 (9.7%)
- MOVE_LEFT: 47,780 (9.6%)
- MOVE_RIGHT: 45,352 (9.1%)
- IDLE: 43,520 (8.7%)
- INTERACT: 41,762 (8.4%)

The strong MOVE_UP bias is an observed failure mode. When imagined scores are equal or nearly equal, stable enum-order tie-breaking favors the first movement after IDLE's higher intrinsic cost. The behavior remains deterministic and internally scored, but tie handling needs a symmetry-preserving deterministic mechanism in a future version.

## Observed failure modes and limitations

- Directional tie bias remains large.
- Some seeds show worsening late prediction error.
- Prediction error can be harsh on empty-activation ticks, producing novelty/tension spikes.
- Cognit counts vary widely and node forgetting is conservative.
- Local patterns lack tolerant spatial/temporal composition and object permanence.
- Loop similarity uses active κ sets; stored action/error/goal fields are not yet included in distance.
- Physical periodic runs still occur, though not the original multi-thousand-tick four-cell lock.
- SELF_ACTION prediction is statistically action-conditioned, but materialized graph edges are only a sparse explanatory projection.
- Runtime is substantially lower than v0.1 and global κ/stale-ρ lifecycle scans remain.

## Interpretation

The observed behavior supports the narrow engineering claims of v0.2: activity is homeostatically sparse, wave fan-out conserves energy, relation evidence is baseline-corrected, predictions/errors are operational, cognitive-space goals persist, and choice uses imagined action consequences plus internal loop risk. It does not establish consciousness, life, semantic understanding, optimal exploration, or complete elimination of behavioral loops.

