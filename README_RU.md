# Synthetic Entity v0.5.2 — итоговое описание

Synthetic Entity — CPU-first исследовательская среда на разреженном динамическом графе Cognit и Relation. Это не LLM, Transformer или RL-агент.

**READY TO FREEZE v0.5.2: YES**

Python отвечает за semantic cognition, Goals, BeliefScene, смысл и retrieval policy памяти, semantic scoring Planner, experiments/curriculum и deterministic RNG service frozen spawn sequence.

В `backend="native"` C++ — единственный владелец float64 numeric Brain state и physical World state: Cognit/Relation, prediction, waves, evidence, lifecycle, homeostasis, bodies, objects, conflicts, fairness, WorldTime, EventSequence и native persistence.

Python World остаётся только differential/reference oracle и не исполняется в normal native runtime. Telemetry читает coarse C++ views и не управляет физикой.

Пройдены clean Release, 132 pytest, 1/1 CTest, 1000-step brain lockstep, causal regression, explicit World conflicts/fairness, 1000-step multi-entity trace и exact persistence continuation. `full_graph_sync_calls=0`, Python physical World calls = 0.

| checkpoint | wall | window actions/s | Cognits | Relations | FFI/action |
|---:|---:|---:|---:|---:|---:|
| 100 | 1.156 s | 86.52 | 50 | 363 | 145.440 |
| 1K | 33.672 s | 27.68 | 128 | 9,835 | 207.718 |
| 5K | 223.803 s | 21.04 | 132 | 14,045 | 229.530 |
| 10K | 437.953 s | 23.35 | 137 | 13,409 | 238.894 |

Окно 5K–10K примерно на 11% быстрее 1K–5K; продолжающийся catastrophic collapse отсутствует.

