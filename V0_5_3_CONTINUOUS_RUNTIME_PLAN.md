# v0.5.3 Continuous Runtime Migration Plan

This audit freezes v0.5.2 tick behavior as the compatibility oracle. A name containing `tick` is not automatically elapsed time.

| Current use | Class | v0.5.3 treatment |
|---|---|---|
| `SimulationClock.tick`, `SensoryFrame.tick`, trace/event-log ticks | D — historical/debug counter | Retain as compatibility observation/cognition ordinal; never advance WorldTime. |
| `EventSequence`, event IDs, ordered trace entries | B — causal ordering | Keep integer and independent of seconds. Same-time queue events order by this ID. |
| `WorldTime.seconds`, ActionIntent issue time | A — elapsed time | Sole external/life time; monotonic float64. |
| `world_tick_count`, `world_tick_interval` | C/D — maintenance and compatibility heartbeat | Keep optional; action, sensing, cognition and learning must not depend on it. |
| `next_spawn_tick`, spawn records | A in continuous runtime; D in frozen World oracle | Continuous scheduler uses absolute `WORLD_SPAWN` time. Frozen Python World retains tick schedule unchanged. |
| `cognitive_tick`, `last_activated_cognitive_tick` | B/D — cognitive operation order | Retain as cognition/event ordinal for v0.5.2 semantic compatibility; do not interpret as seconds. |
| evidence windows/support counts | B — causal event-count evidence | Retain event-count semantics. |
| wave steps and `refractory_wave_steps` | B — propagation order | Retain wave-step semantics; not elapsed time. |
| Cognit activity/homeostasis decay | A — elapsed-time behavior | Add lazy `last_touch_time` evolution in continuous path; preserve frozen tick API as adapter. |
| Relation confidence/lifecycle idle decay | A where configured as aging; B for support/confirmations | Add lazy absolute-time materialization; do not convert evidence counts. |
| memory confidence decay, recency and idle age | A — elapsed time | Continuous APIs consume `now`/delta lazily on touched/relevant candidates. |
| percept `age`, `missing_ticks`, prototype occurrence counters | B — observation-event counts | Keep event-count semantics. |
| Goal `age`, unavailable duration, cooldown | Mixed A/B | Persistence/urgency duration moves to elapsed time; deliberation attempts and completion counts remain event counts. |
| pruning/lifecycle cursors and quotas per tick | C — periodic maintenance | Schedule low-priority `MAINTENANCE`; quotas apply per maintenance/event transaction. |
| telemetry sample tick | D; timestamp is A | Record both causal/sample ordinal and `world_time_seconds`. |
| renderer frame/update timing | E — observer scheduling | Wall-clock/frame cadence only; never mutates runtime or advances simulated time. |

## Minimal migration order

1. Add deterministic native absolute-time event queue with `(time,event_id)` ordering and persistence.
2. Add a Python orchestration facade that wakes cognition from sensory/action events and drains ready work to quiescence with a debug-only loop guard.
3. Schedule sub-second action completion and sensory wake independently of the optional heartbeat.
4. Add lazy elapsed-time APIs one subsystem at a time, retaining event-count fields where meaning is causal.
5. Add read-only `RenderSnapshot`; observer cadence may sample it but never schedule runtime work.
6. Add optional SDL3/OpenGL observer target isolated from brain code.

## Compatibility gates

Every phase retains v0.5.2 Python/native lockstep, causal boundary, native authority, persistence, cognition settings, and zero full-graph synchronization. Renderer-disabled and multiple sampling frequencies must produce byte-equivalent runtime snapshots.

## Continuous save/load execution frontier

The first continuation investigation found the first causal mismatch before the first post-load `SENSORY_CHANGE`: `ConsciousnessState.representation_coverage` restored as 0 instead of 2/3. Consequently every prototype candidate missed one 2/3 `explained_sum` contribution. This was a missing update (case A), not floating drift.

Behavior-affecting and therefore persisted:

- previous SensoryFrame when a cognition wake is pending;
- last active WaveResult/frontier;
- last decomposed sensory primitives;
- representation/prediction/error/uncertainty/tension state used by the next observation or deliberation;
- action scores, FutureEstimates, tie set and tie state;
- native transition BEFORE/AFTER history;
- native lazy-homeostasis policy/applied frontier;
- dirty Relation lifecycle frontier;
- scheduler wake reason/type/payload and explicit ordering IDs;
- prototype accumulators, perception baselines/tracks, planner state, previous active/context/action, Goals and deterministic cursors already carried by the semantic snapshot.

Derived/non-behavioral and not persisted:

- native scratch arrays/generation marks rebuilt before graph operations;
- Python numeric-view caches invalidated after native restore;
- memory `last_retrieval_candidates/total` diagnostic counters;
- renderer snapshots and frame timing;
- telemetry presentation caches.

Canonical ordering is required when set semantics feed behavior-affecting quotas or accumulation. Prototype candidate traversal is now sorted by `(translation_tolerant, signature)` rather than Python hash iteration order.

## Elapsed-time formula classification

- Cognit passive activity, utility, inactive activity-trace recovery, homeostatic threshold adaptation, and real-time inactivity/recency are elapsed-time state.
- Relation passive confidence decay and expiry duration are elapsed-time state; support, confirmations, contradictions and evidence membership remain event counts.
- Memory passive confidence, recency and idle duration are elapsed-time state; visits, observations, recalls, reactivations and contradictions remain event counts.
- Goal created/persistence duration, unavailable duration and cooldown deadline are elapsed-time state. Deliberation attempts, successful interventions, completion counts and causal observations remain counts. `Goal.age` remains the frozen attempt/event count until consumers are migrated explicitly; it is not mechanically reinterpreted.
- `cognitive_tick`, prototype occurrences/`explained_sum`, percept observation age/missing count, wave/refractory steps, planner depth/expansions and tie cursors remain causal counts.

The closed-form inactive Cognit extension uses powers of the frozen per-unit factors. The homeostatic trace geometric sum is analytically composed, so partitioning the same duration does not change state (away from an actual clamp boundary). No wall-clock API is used.

## Elapsed-time integration decisions

- `ContinuousRuntime` passes each exact `SENSORY_CHANGE` event time explicitly to `SyntheticEntityCore.step(..., world_time=now)`. The frozen `step(frame)` API remains discrete.
- Native Cognits use a global continuous epoch plus per-live-Cognit `last_touch_time_seconds` and `last_active_time_seconds`. Advancing the clock changes no Cognit arrays; access materializes only touched IDs.
- Native Relations keep separate passive-confidence and last-evidence elapsed frontiers. Runtime handles remain an implementation detail; `.seworld` persists Relation frontiers by stable `(source,target,type,action)` identity because graph restore may compact handles.
- Continuous SpatialMemory maps one frozen per-observation decay factor to one simulated-second factor: `confidence(t+dt)=confidence(t)*memory_confidence_decay**dt`. Recency uses the existing 128/256 constants as seconds, reproducing the frozen formula at integer-second sampling. Only indexed candidates, observed matches, and explicit contradiction candidates materialize.
- Target-structure recall uses conservative place admission. Exact relation-token hits and direct associations are unconditional candidates. For zero-overlap places, participant-count and 0.001-wide maximum-confidence buckets provide `c_upper`; admission uses `roles=min(n,m)/max(n,m)`, `role_support=min(1,n/m)`, `structural_upper=0.2*roles*min(c_upper,target_confidence)`, and `strength_upper=(0.1+0.65*structural_upper+0.25*role_support)*c_upper`. Recency is bounded by 1. Because group mean confidence and every member confidence are no greater than `c_upper`, this cannot underestimate the exact zero-overlap score. Places with an exact shared token bypass this zero-overlap bound. Broad admission is therefore used only when the frozen role/confidence terms mathematically permit recall despite no relation overlap.
- Goal `age`, attempts, interventions, and completion counts remain causal counts. Between events persistence applies only `goal_decay**dt`; the understanding factor is applied exactly once at the new cognitive event, so new evidence is never integrated retroactively. Created/unavailable/cooldown timestamps are separate float64 fields.
- Planner `subgoal_cooldown_until` is deliberately retained as a deliberation-attempt cooldown: all consumers compare it with the planner/cognitive ordinal, and no source-level behavior treats it as external waiting time.
- Continuous elapsed frontiers are stored in the continuous `.seworld` `CONT` section alongside the scheduler frontier. The native `NBRN` graph payload remains format version 3 because it is still the frozen v0.5.2 graph artifact; no old integer field is reinterpreted during loading.
