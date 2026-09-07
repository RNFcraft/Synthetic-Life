# v0.5.2 Hybrid Runtime — Final Report

**READY TO FREEZE v0.5.2: YES**

## Architecture

Python owns semantic cognition: CognitPattern meaning, Goals, BeliefScene, memory semantics/retrieval policy, planner semantic scoring, experiments/curriculum, and the deterministic RNG service preserving the frozen spawn sequence.

In `backend="native"`, C++ is the sole numeric brain and physical World authority. It owns float64 Cognit/Relation state, prediction, waves, evidence, lifecycle, homeostasis, bodies, objects, held state, conflicts, rotating fairness, WorldTime, EventSequence, and native persistence sections.

Python World is retained only as an executable differential oracle. It is not constructed or stepped during normal native execution. Telemetry views are refreshed from coarse native state and never drive physics.

## Acceptance

Clean Release rebuild passed; pytest **132 passed**; CTest **1/1 passed**; all 100-step and 1000-step brain locksteps passed. Native causal results: Experienced 5/5, Fresh 5/5, causal-rho ablated 0/5. World differential/conflict/fairness, 1000-step multi-entity trace, SensoryFrame, `.sebrain`, `.seworld`, RNG, scheduler, fairness, WorldTime and EventSequence continuation all pass. `full_graph_sync_calls=0`; normal native Python physical World calls are zero.

## Canonical performance

Seed 123, ordinary native Simulation with telemetry. Artifact: `runs/v052-final-freeze.json`.

| checkpoint | wall | window actions/s | live Cognits | Relations | provisional/consolidated | FFI/action | proxies/action | memory/candidates |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1.156 s | 86.52 | 50 | 363 | 315/48 | 145.440 | 0.0200 | 1 / 1 |
| 1K | 33.672 s | 27.68 | 128 | 9,835 | 6,454/3,381 | 207.718 | 0.2240 | 4 / 4 |
| 5K | 223.803 s | 21.04 | 132 | 14,045 | 5,025/9,020 | 229.530 | 0.0482 | 4 / 0 |
| 10K | 437.953 s | 23.35 | 137 | 13,409 | 3,590/9,819 | 238.894 | 0.0263 | 4 / 0 |

The 5K–10K window is about 11% faster than 1K–5K. The former continuing catastrophic throughput collapse does not return.

