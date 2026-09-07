# Synthetic Entity v0.5.2 — Hybrid Native Runtime

Synthetic Entity is a CPU-first research environment built around a sparse dynamic graph of Cognits and Relations. It is not an LLM, Transformer, reinforcement-learning agent, or conventional neural network.

**READY TO FREEZE v0.5.2: YES**

## Final architecture

Python owns semantic CognitPattern meaning, Goals, BeliefScene, memory semantics and indexed retrieval policy, planner semantic scoring, experiments/curriculum, and the deterministic RNG service for the frozen spawn sequence.

In `backend="native"`, C++ is the sole float64 numeric brain authority and sole physical World authority. It owns Cognit/Relation state, prediction, waves, evidence, lifecycle, homeostasis, bodies, objects, conflicts, fairness, WorldTime, EventSequence, and native persistence sections.

Python World is a differential/reference oracle only and is not executed during normal native life. Telemetry reads lightweight views refreshed from coarse C++ state.

```text
World -> immutable SensoryFrame -> SyntheticEntityCore -> ActionIntent -> World
```

Core receives no coordinates, World/Grid objects, physical IDs, collision IDs, spawn schedule, or semantic success labels.

## Verification

Clean Release, **132 pytest**, **1/1 CTest**, brain lockstep through 1000 ticks, causal regression, explicit World conflicts/fairness, 1000-step multi-entity trace, and exact persistence continuation pass. `full_graph_sync_calls=0`; normal native Python physical calls are zero.

## Canonical benchmark

| checkpoint | wall | window actions/s | Cognits | Relations | FFI/action |
|---:|---:|---:|---:|---:|---:|
| 100 | 1.156 s | 86.52 | 50 | 363 | 145.440 |
| 1K | 33.672 s | 27.68 | 128 | 9,835 | 207.718 |
| 5K | 223.803 s | 21.04 | 132 | 14,045 | 229.530 |
| 10K | 437.953 s | 23.35 | 137 | 13,409 | 238.894 |

The 5K–10K window is about 11% faster than 1K–5K; continuing catastrophic collapse is absent. Full metrics: `runs/v052-final-freeze.json`.

Build: `cmake --build cpp/build --config Release`; verify: `python -m pytest -q` and `ctest --test-dir cpp/build -C Release --output-on-failure`.

