# Synthetic Entity Architecture v0.5.2

## Authority split

Python owns semantic cognition: CognitPattern meaning, Goals, BeliefScene, memory semantics/retrieval policy, planner semantic scoring, experiments/curriculum, and deterministic spawn RNG.

For `backend="native"`, C++ is the sole numeric brain and physical World authority. It owns float64 Cognit/Relation state, prediction, waves, evidence/materialization, lifecycle, homeostasis, bodies, objects, held state, resistance, simultaneous conflicts, rotating fairness, WorldTime, EventSequence, and native persistence payloads.

Python World is only an executable differential oracle. Normal native execution never steps it. Python telemetry views are coarse snapshots from C++ and cannot drive physics.

## Boundary

```text
World -> immutable SensoryFrame -> SyntheticEntityCore -> timestamped ActionIntent -> World
```

Core receives no World/Grid, coordinates, physical IDs, collision IDs, spawn schedule, evaluator metrics, or semantic action-result labels.

## Brain, planner, and memory

Native behavior-affecting state and intermediate math are float64; extended lockstep passes 1000 ticks. TransitionEvidence remains bounded; long-lived prediction uses materialized Relations. Planner meaning and final scoring remain Python-side while ordered batch mutations and masked reads perform mechanics. SpatialMemory meaning/scoring remain Python-side; incremental indexes return the exact legacy oracle result while limiting work to relevant candidates.

## Native World and persistence

WorldRuntime implements multi-body movement, push, grab/carry/release, interaction, resistance, immutable perception, classify-before-mutate simultaneous resolution, conflicts, fairness, spawning, and time/event ordering. Python RNG supplies only the frozen row-major free-cell choice and interval; C++ performs physical mutation.

`.sebrain` stores durable cognition plus checksummed NBRN v3. `.seworld` stores exact native physical state, RNG, scheduler, fairness, WorldTime, EventSequence, and runtime state. Save reads native authority; load restores it directly.

## Final baseline

`runs/v052-final-freeze.json`: 1K–5K throughput is 21.04 actions/s; 5K–10K throughput is 23.35 actions/s. No continuing catastrophic collapse occurs. All checkpoints have `full_graph_sync_calls=0`.

The full acceptance suite passes: **READY TO FREEZE v0.5.2: YES**.

Asynchronous/event-driven cognition and 3D rendering are outside v0.5.2 scope.
