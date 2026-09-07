# Synthetic Entity v0.4 Experiment Report

## Summary

v0.4 technically establishes a reward-free persistent manipulation laboratory and moves acquired runtime prediction from rolling counters into materialized Relations. Physical manipulation, SELF_ACTION relation formation, action-dependent predicted outcomes, and positive but small AgencyEstimate were observed. These results do not establish semantic object understanding, causality, self-awareness, or intentional structure building.

## Changes from v0.3

- Configurable 30×30 world, zero initial objects, deterministic interval spawn, maximum ten.
- No autonomous object movement or state change.
- Push through MOVE; directional grab; held-slot carry; release along orientation; directional binary-state interaction.
- Immutable non-semantic touch/holding/resistance BodySense decomposed into ordinary primitives.
- Fifteen available motor symbols including legacy INTERACT compatibility.
- TransitionModel restricted to evidence accumulation; runtime prediction and imagination use ρ.
- Provisional/consolidated relation states, contradiction, usefulness, diagnostics, and ablation.
- One-step composite predictive contribution and independent pattern selectivity.
- AgencyEstimate, seven-tab UI, exact fractional speed scheduler, and snapshot v4.

## World redesign

Reference runs started with no objects. Ten objects appeared at seeded logical intervals and remained physically stable unless acted upon. Spawns were ordinary frame changes, with no cognition-side spawn event. External records retained spawn, first observation, first contact, first displacement, and first interaction ticks.

## Action system

MOVE can freely move, push one object, or be resisted. GRAB stores an adjacent object in a held-slot. Movement carries it. RELEASE attempts an orientation-adjacent placement and preserves holding on failure. INTERACT toggles only an adjacent binary primitive state. All directions remain candidates even when physically ineffective.

The seed-123 100K run recorded 679 push attempts/574 successes, 17,824 grab attempts/356 successes, 4,965 release attempts/356 successes, and 19,234 interaction attempts/451 successes. High failure counts are expected because Core is not given physical availability.

## Body sensory system

Touch channels report directional contact without classifying its cause. Resistance reports only a blocked/invalid physical attempt. Holding reports a bodily binary state without identity. Static boundary tests confirm Core receives neither `ActionResult` nor World/Grid/WorldObject imports; all body fields are immutable.

## Relation substrate redesign

Evidence estimates bounded support, baseline lift, and action lift. It materializes or updates graph ρ, after which prediction uses stored strength/probability, confidence, and action context. Provisional ρ can consolidate; confirmation increases confidence and contradiction lowers it. At 100K, 16,384 Relations existed: 15,352 provisional, 1,032 consolidated, and 8,157 SELF_ACTION. Density was 0.00637, far below a complete graph, although the configured cap was reached.

## Relation ablation

A seed-123 10K graph-prediction ablation produced mean prediction error 0.7991 and Brier 0.9997, versus 0.3932 and 0.1468 in the normal 10K run. AgencyEstimate and Controllability both became zero under ablation. The physical trajectories diverged because predictions affect action choice, so this is an end-to-end diagnostic rather than a paired fixed-trajectory estimate.

A synthetic persistence test materialized `A→B`, cleared all TransitionModel evidence, and retained graph prediction. Disabling ρ prediction then returned no prediction. Repeated contradiction lowered confidence and raised contradiction evidence. Thus learned runtime prediction no longer resides in transient counters.

## Object spawn experiment

All reference and multi-seed runs reached ten objects, then stopped spawning. The schedule used only seeded logical time. Objects that had not yet entered the egocentric radius had no first-observed tick; cognition received no schedule or remaining-count field.

## Agency development

Seed-123 rolling 10K windows in the 100K run showed AgencyEstimate 0.0194 at 10K, 0.0148 at 25K, 0.0213 at 50K, and 0.0164 at 100K. Controllability rose from 0.0126 to 0.0256 while prediction error fell from 0.3912 at 10K to 0.2316 in the final window. The trajectory is non-monotonic; agency differentiation did not simply accumulate.

## Manipulation behavior

Persistent displacement, grab/carry/release, and state toggling occurred without rewards or authored object goals. Attempts were much more frequent than successes. This supports only the statement that manipulation behavior occurred and action-conditioned consequences entered the graph.

## Composite usefulness

For each active composite, the realized next observation evaluates prediction with and without its graph contribution. The signed `error_without-error_with` updates Cognit predictive contribution and retention. At 100K there were 252 composites among 1,604 Cognits. The current report does not establish that long-horizon composite usefulness is positive; the estimator is one-step only.

## Pattern selectivity

Seed-123 mean coverage/selectivity/quality were 0.9918/0.5969/0.5927 at 10K, 0.9982/0.6375/0.6366 at 50K, and 0.9991/0.6063/0.6058 at 100K. Coverage near 99.9% therefore no longer stands alone: selectivity indicates that a substantial fraction of match specificity remains below one.

## 10K results — seed 123

- 227.25 ticks/s; 877 κ (699 primitive, 178 composite).
- 5,706 ρ: 5,158 provisional, 548 consolidated, 1,977 SELF_ACTION; density 0.00743.
- Mean prediction error 0.3932; Brier 0.1468.
- Mean AgencyEstimate 0.01927; Controllability 0.01281.
- 221 unique entity positions and 127 object configurations.
- 54 successful pushes, 25 grabs/releases, 36 interactions.
- 227 goals; mean completed lifetime 41.28 ticks.

## 50K results — seed 123

- 94.45 ticks/s; 1,259 κ (1,049 primitive, 210 composite).
- 16,383 ρ: 15,128 provisional, 1,255 consolidated, 5,425 SELF_ACTION; density 0.01034.
- Mean prediction error 0.2881; Brier 0.06646.
- Mean AgencyEstimate 0.01825; Controllability 0.01969.
- 681 unique positions and 764 configurations.
- 360 successful pushes, 200 grabs/releases, 226 interactions.
- 1,201 goals; mean lifetime 37.13 ticks.

## 100K result — seed 123

- 1,382.92 seconds; 72.31 ticks/s.
- 1,604 κ (1,352 primitive, 252 composite).
- 16,384 ρ: 15,352 provisional, 1,032 consolidated, 8,157 SELF_ACTION; density 0.00637.
- Mean prediction error 0.2523; Brier 0.04524.
- Coverage/selectivity/quality 0.9991/0.6063/0.6058.
- Mean AgencyEstimate 0.01648; Controllability 0.02138.
- 614 unique positions and 1,345 configurations.
- 2,448 goals; mean lifetime 36.08 ticks.

The 100K run was started before the final WorldModification correction. Its logged value 116 used displacement plus current binary state, not cumulative state changes, and is retained only as a labelled legacy proxy. No corrected 100K value is fabricated.

## Multi-seed results

The final 10×50K aggregate is recorded in `v04-results-50k.json`. A faster 10×10K checkpoint on final metric semantics measured mean 3,925 Relations (range 1,620–6,721), 942 SELF_ACTION (27–2,605), AgencyEstimate 0.00863, prediction error 0.4194, coverage 0.9915, selectivity 0.6032, WorldModification 42.9, and 100.4 configurations. The very wide SELF_ACTION range demonstrates seed dependence.

## World modification metrics

Final code defines WorldModification as Manhattan displacement from spawn plus cumulative successful state changes. It is external telemetry and never reward. ConfigurationHash is the unordered set of object positions/states, with a held-slot marker. Multi-seed structure telemetry also reports adjacency, lines, connected clusters, and largest cluster; no structure score enters Core.

## Action distribution

Directional movement remained close within each run under symmetry-preserving choice. Motor-class frequency differed because small physical effort costs, prediction confidence, goal alignment, novelty, controllability, and loop risk differed. Invalid manipulation actions were not masked.

## Relations and prediction

Every final 10K seed materialized Relations; none remained at zero ρ. Long runs reached the configured cap, revealing overproduction of provisional candidates rather than graph collapse. Normal prediction improved with experience, but the graph's noisy-or causes are correlated and calibration remains approximate.

## Goals and AgencyEstimate

Goals remained cognitive κ targets. No goal contained an object ID, position, push, grab, interaction, line, or cluster objective. AgencyEstimate remained small and non-monotonic. Passive movement control can also yield action differentiation, so the metric must not be read as manipulation-specific agency.

## Performance

Early profiling identified repeated full action prediction as the dominant cost. v0.4 now scans common state relations once and dispatches action-conditioned deltas while retaining every candidate. A second mature-graph issue—temporary connect/remove plus repeated global relation counts after cap—was replaced with O(1) membership checks and a per-tick count. Relation pruning runs every 64 ticks. Throughput still fell from 227 ticks/s at 10K to 72 ticks/s over the 100K run because κ/ρ and active outgoing work grew.

## Failure modes

- Long runs fill the 16,384-Relation cap; most ρ remain provisional.
- AgencyEstimate is small, seed-dependent, and partly driven by locomotion.
- Final-tick AgencyEstimate can be zero even when lifetime mean is positive.
- Manipulation success is rare relative to blind attempts.
- Coverage remains near one; selectivity helps but its background is only recent online experience.
- Held-slot carrying omits extended-object collision geometry.
- Composite contribution is one-step and can miss delayed value.
- Physical loops, greedy π identity, correlated noisy-or causes, and global O(κ) homeostasis remain.

## Interpretation

The narrow technical result is positive: the world can be persistently modified; BodySense exposes consequences without semantic leakage; SELF_ACTION ρ materialize; graph prediction survives evidence clearing; relation ablation substantially degrades prediction; and imagined futures use those Relations. The scientific result is deliberately weaker: action consequences became differentiated, but the observed small/non-monotonic AgencyEstimate and passive-control behavior do not prove intentional manipulation, causal understanding, or structure formation.
