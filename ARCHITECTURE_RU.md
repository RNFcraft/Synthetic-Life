# Архитектура Synthetic Entity v0.5.3a

Python владеет semantic cognition: CognitPattern, Goals, BeliefScene, смыслом и retrieval policy памяти, semantic scoring Planner, experiments/curriculum и deterministic spawn RNG.

В `backend="native"` C++ — единственный numeric Brain authority и physical World authority. Он владеет float64 Cognit/Relation, prediction, waves, evidence/materialization, lifecycle, homeostasis, bodies, objects, held state, resistance, simultaneous conflicts, rotating fairness, WorldTime, EventSequence и native persistence payloads.

Python World — только executable differential oracle. Normal native execution его не запускает; telemetry views являются coarse snapshots из C++.

```text
World -> immutable SensoryFrame -> SyntheticEntityCore -> timestamped ActionIntent -> World
```

Core не получает World/Grid, координаты, physical IDs, collision IDs, spawn schedule, evaluator metrics или semantic result labels.

Planner meaning/scoring остаются в Python, mechanical work использует ordered batching и masked reads. SpatialMemory semantics остаются в Python, incremental indexes дают точный legacy-oracle результат по relevant candidates.

WorldRuntime реализует multi-body movement, push, grab/release, interaction, resistance, immutable perception, classify-before-mutate conflicts, fairness, spawning и time/event order. Python RNG передаёт только frozen row-major free-cell choice и interval; C++ выполняет физическую мутацию.

`.sebrain` хранит cognition и NBRN v3. `.seworld` schema v4 сохраняет native physical state, RNG, scheduler, fairness, WorldTime, EventSequence, незавершённый cognition frontier и абсолютные spawn/maintenance timers.

Continuous runtime не зависит от `world_tick()` heartbeat: `WORLD_SPAWN` и `MAINTENANCE` планируются по абсолютному WorldTime. Внутренняя cognition завершается только при пустой очереди причинно обусловленной работы.

Опциональный native observer получает value-owned `RenderSnapshot` через C++ snapshot channel и отображает мир в отдельном SDL3/OpenGL frame loop. Observer не меняет World, scheduler, cognition или persistence state.

Финальный baseline: 21.04 actions/s в окне 1K–5K и 23.35 actions/s в 5K–10K. Continuing catastrophic collapse отсутствует; `full_graph_sync_calls=0`.

**READY TO FREEZE v0.5.2: YES**
