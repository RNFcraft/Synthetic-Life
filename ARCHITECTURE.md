# Synthetic Entity Architecture — v0.5.3a

Synthetic Entity is an experimental embodied cognitive architecture built around a sparse, continuously changing graph of Cognits (`κ`) and Relations (`ρ`). It is not a Transformer/LLM inference loop and does not depend on a frozen policy network. The current system learns through persistent predictive, causal, spatial, and goal-directed state that changes during interaction with the world.

The v0.5.2 runtime remains the frozen compatibility oracle. v0.5.3a adds continuous float64 time, lazy elapsed-time state and a true scheduler-visible event-driven cognition frontier while preserving the legacy discrete APIs for differential testing.

## 1. Authority split

The implementation is intentionally hybrid.

### Python owns semantic cognition

Python owns behavior-level meaning and research logic:

- `CognitPattern` semantics and matching;
- Goals and subgoals;
- `BeliefScene` and relational interpretation;
- SpatialMemory semantics, indexing and retrieval policy;
- planner semantics and final scoring;
- perceptual continuity and prototype/composite semantics;
- affordance evidence;
- experiments, diagnostics and compatibility oracles;
- the continuous cognition work frontier.

Python may contain behavior-affecting numeric semantic state. Therefore C++ should not be described as the authority for every numeric value in the brain.

### C++ owns the authoritative native numeric substrate

For `backend="native"`, C++ is the sole authoritative numeric Cognit/Relation substrate and physical World runtime. It owns:

- float64 Cognit state;
- float64 Relation state;
- sparse relation storage and lifecycle;
- waves and propagation mechanics;
- transition evidence and relation materialization;
- native graph prediction/action-effect mechanics;
- lazy elapsed-time Cognit/Relation materialization;
- native homeostasis mechanics;
- bodies, objects, held state and resistance;
- movement/push/grab/release/interaction mechanics;
- simultaneous conflicts and rotating fairness;
- native `WorldTime` and `EventSequence` state;
- the deterministic native event scheduler;
- native persistence payloads.

There is no authoritative Python mirror of the native Cognit/Relation numeric state in normal native execution. `full_graph_sync_calls == 0` remains an invariant.

## 2. Causal boundary

The core boundary remains:

```text
World
  -> immutable SensoryFrame
  -> SyntheticEntityCore
  -> timestamped ActionIntent
  -> World
```

The cognitive core does not receive the World/Grid object, absolute physical coordinates, physical object IDs, collision IDs, spawn schedule, evaluator metrics or semantic action-result labels.

Learning must remain grounded in what the Entity can infer from sensory change and its own committed actions.

## 3. Time model

The architecture now separates four notions that must never be conflated:

```text
WorldTime.seconds
    != cognitive operation ordinal
    != EventSequence / scheduler event_id
    != render frames
```

### WorldTime

`WorldTime.seconds` is monotonic float64 simulated life time. It is the time basis for continuous physical events and elapsed-time state.

### EventSequence / event_id

Integer IDs provide deterministic causal ordering. Events at the same float64 timestamp are ordered by event ID.

### cognitive_tick

`cognitive_tick` is retained as a causal/operation ordinal for compatibility and event-count semantics. It is not seconds.

### Renderer time

Future renderer frame cadence is observational only. FPS must never advance WorldTime or mutate cognition.

## 4. Continuous event scheduler

The native scheduler orders events by:

```text
(time, event_id)
```

Current event vocabulary includes world, sensory and cognitive work such as:

- `SENSORY_CHANGE`;
- `COGNITION_WAKE`;
- `COGNITION_CONTINUE`;
- `WORLD_ACTION_COMPLETE`;
- `WORLD_SPAWN`;
- `MEMORY_TIMER`;
- `RELATION_TIMER`;
- `MAINTENANCE`;
- `EXTERNAL_INPUT`.

Not every event type is behavior-authoritative in the current runtime yet. In particular, continuous world spawning/maintenance completion is the next gate.

## 5. True event-driven cognition frontier

Normal `ContinuousRuntime` no longer performs a whole decision through the legacy monolithic `SyntheticEntityCore.step()` + `DeliberativePlanner.deliberate()` path.

The current continuous chain is:

```text
SENSORY_CHANGE
  -> bounded observation transaction
  -> COGNITION_WAKE
  -> COGNITION_CONTINUE x N at the same WorldTime
  -> QUIESCENT
  -> one decision commit
  -> WORLD_ACTION_COMPLETE at WorldTime + action duration
```

A single `COGNITION_CONTINUE` consumes at most one explicit pending cognitive work item.

The implemented cognitive work types are:

```text
RECALL
  -> PROPAGATE
  -> IMAGINE
  -> PLAN_REFINE
```

Additional work appears only when a cognitive operation creates a real semantic invalidation, for example an internally changed Goal/subgoal causing a new recall chain.

### Natural quiescence

Continuous cognition does not stop because a fixed number of cycles elapsed, because a coarse state signature repeated, because a numeric epsilon was reached or because wall-clock time expired.

The rule is causal:

```text
QUIESCENT iff
    a valid candidate decision exists
    and pending cognitive work is empty
    and no deduplicated invalidation key remains pending
    and the session is not finalized
```

Equivalently, cognition stops because there is no remaining justified internal work.

The runtime event guard is diagnostic only. If a real causal internal loop fails to terminate, the guard raises an error and must not force an action.

## 6. Observation and action commit semantics

A `SENSORY_CHANGE` applies external evidence exactly once for that SensoryFrame. Internal continuation events are not additional observations.

Prototype occurrences, perception observation counters, memory confirmation/contradiction evidence and Relation transition evidence therefore remain sensory/causal counts rather than cognition-loop counts.

Internal recall may occur more than once only when its semantic recall key changes. Repeated scheduler execution alone is not a reason to stimulate the same recalled Cognits again.

The final action is committed exactly once after quiescence. Decision-derived state such as final predictions, trace action, `previous_action`, planner commit and final active homeostasis is committed only at that boundary.

## 7. Elapsed-time lazy cognition

Passive behavior in continuous mode is analytically evolved by elapsed `WorldTime` instead of replaying artificial ticks.

### Cognits

Native Cognits use a continuous epoch plus per-Cognit float64 touch/activation frontiers. Passive activity, utility, activity trace and homeostatic evolution are materialized only when relevant Cognits are touched.

Homeostatic threshold evolution preserves a separate unclamped latent threshold so intermediate observation/save/materialization cannot change future behavior at clamp boundaries.

### Relations

Relations keep separate passive-confidence and evidence-time frontiers. Support, confirmations, contradictions and evidence membership remain causal event counts.

All behavior consumers in continuous mode use the same effective elapsed Relation confidence semantics.

### SpatialMemory

Memory confidence and recency use elapsed seconds in continuous mode. Retrieval is lazy and indexed. Target-structure recall performs conservative place admission and then runs the exact semantic scorer only on candidate places/memories.

The large-memory acceptance fixture retains 10,000 memories across 5,000 places while materializing only the small conservative candidate set.

### Goals

Goal passive persistence uses elapsed-time decay between cognitive events. Understanding is applied causally at the event that produced it, never retroactively over a silent interval.

`Goal.age`, attempts, interventions and completion counters remain causal/event-count state.

## 8. Brain and learning substrate

The durable learned substrate is the sparse graph of Cognits and Relations.

A Cognit carries learned/behavioral state such as activity, threshold, retention/utility and semantic pattern association. Meaning is not stored in one label; it emerges from structure, Relations and history.

Relations can express associative, sequential, causal, inhibitory, self-action and spatial structure. Transition evidence is bounded and supports materialization into persistent Relations. Normal graph prediction uses materialized Relations rather than a separate learned policy/value network.

No Q-learning, PPO, policy-gradient or backpropagation policy is part of the architecture.

## 9. Planner

Planner meaning remains Python-side. Native prediction/action-effect batches provide mechanical graph queries, while Python performs semantic goal, uncertainty, memory, epistemic, structural-progress and loop-risk scoring.

Legacy `DeliberativePlanner.deliberate()` remains bounded for v0.5.2 compatibility.

Continuous planning is different: it owns a persistent `DeliberationSession` with ordered pending cognitive work. `max_deliberation_cycles` does not determine continuous behavior.

The bounded `_search()` operator may still use planning horizon/beam width as an algorithmic search bound; that is distinct from using a hidden fixed number of cognition cycles to decide when thought ends.

## 10. Native World

`WorldRuntime` is the physical authority in normal native execution. It implements:

- immutable perception;
- movement and turning;
- pushing;
- grab/carry/release;
- object interaction/state changes;
- resistance;
- simultaneous resolution;
- conflict handling;
- rotating fairness;
- world time/event ordering;
- physical persistence.

The Python World remains a frozen differential oracle and compatibility implementation. Normal native runtime must not step Python physics.

### Remaining world-continuity work

The next gate is `CONTINUOUS WORLD COMPLETION`:

- move spawning to absolute scheduled `WORLD_SPAWN` events;
- move periodic maintenance/lifecycle work to explicit timers/events;
- remove remaining behavior dependence on `world_tick()` / heartbeat cadence;
- preserve the frozen Python World tick schedule only as a compatibility oracle.

Until that gate passes, the cognition side is event-driven but the World still contains compatibility heartbeat/tick mechanisms.

## 11. Persistence

Persistence is part of deterministic execution, not a presentation layer.

### `.sebrain`

Stores durable learned cognition and the native `NBRN` graph payload.

### `.seworld`

Continuous `.seworld` schema v3 stores the exact execution frontier, including:

- scheduler time, IDs and pending events;
- native World state;
- WorldTime/EventSequence state;
- native elapsed Cognit/Relation frontiers;
- transition/homeostasis/lifecycle state;
- previous SensoryFrame and cognitive semantic frontier;
- cognition generation and phase;
- ordered pending cognitive work and deduplication keys;
- working revision and last recall state;
- current candidate plan and planner semantic caches required for exact continuation;
- pending/committed action state.

Save is observational: saving must not change the future trajectory. v1/v2 continuous snapshots retain explicit compatibility/migration handling.

## 12. Determinism and acceptance invariants

The current accepted v0.5.3a cognition frontier has:

- `ELAPSED-TIME LAZY COGNITION: PASS`;
- `TRUE EVENT-DRIVEN COGNITION FRONTIER: PASS`;
- full pytest: 201 passed;
- CTest Release: 1/1 passed;
- identical deterministic trajectory digest for `PYTHONHASHSEED=1` and `77`;
- `full_graph_sync_calls == 0`;
- normal native Python physical World calls: 0;
- renderer sampling invariance: PASS.

The v0.5.2 benchmark/freeze data remains the performance/compatibility baseline. Long v0.5.3 5K/10K benchmarks have intentionally not been rerun during the correctness migration.

## 13. Observer/rendering architecture

Rendering is intentionally not part of cognition or physics.

The current Python `RenderSnapshot` is a proof surface. The planned post-world-completion renderer is:

```text
C++ WorldRuntime
    -> native read-only RenderSnapshot
    -> SDL3 + OpenGL observer
```

The observer must never schedule cognitive work, advance WorldTime or mutate authoritative World state. High FPS must not create high-frequency Python FFI traffic in the final native observer path.

## 14. Current roadmap

```text
v0.5.2 frozen native compatibility baseline                    DONE
    -> elapsed-time lazy cognition                              DONE
    -> true event-driven cognition frontier                     DONE
    -> continuous world completion                              NEXT
    -> native C++ SDL3/OpenGL observer
    -> scaling cleanup
    -> continuous multi-entity runtime
    -> full 3D World
    -> Entity visual/retina/gaze input
```

The immediate development target is `CONTINUOUS WORLD COMPLETION`. The renderer should not begin until that gate passes.
