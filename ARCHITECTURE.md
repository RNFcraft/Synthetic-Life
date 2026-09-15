# Synthetic Entity Architecture — v0.6.3

Synthetic Entity is an experimental embodied cognitive architecture built around a sparse, continuously changing graph of Cognits (`κ`) and Relations (`ρ`). It is not a Transformer/LLM inference loop and does not depend on a frozen policy network. The current system learns through persistent predictive, causal, spatial, and goal-directed state that changes during interaction with the world.

The v0.5.2 runtime remains the frozen compatibility oracle. v0.5.7 retains the
v0.5.3 continuous float64/event-driven architecture and adds receptive embodied
symbol grounding while preserving legacy differential oracles. v0.6.0 adds an
isolated native event-driven micro-neurodynamic substrate below that architecture;
v0.6.1 adds only local plasticity and homeostasis within that substrate;
v0.6.2 adds an observational native assembly-evidence layer; v0.6.3 adds its
first one-way coarse bridge into the existing native Cognit graph.

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

### Isolated micro-neurodynamic substrate (v0.6.0)

`NeurodynamicSubstrate` is owned by the native backend, but is a separate layer:

```text
existing Cognits / Relations
          ^ future assemblies (not implemented)
micro-κ / micro-ρ native event substrate
```

Micro-κ use flat SoA numeric state with stable monotonic IDs. Fixed micro-ρ
edges carry source, target, nonnegative weight, positive delay, and excitatory
or inhibitory polarity. A native priority queue ordered by float64 time then
monotonic sequence propagates all events; same-time deliveries are grouped by
target before a single threshold evaluation. Potential and adaptation decay only
when a touched micro-κ is materialized. Refractory deliveries are discarded and
counted. Thus an empty or silent substrate has no global neural tick and no
periodic per-neuron update.

The membrane/adaptation time constants, refractory period, reset potential, and
adaptation increment are innate physiology, not learned knowledge. Python has a
coarse experiment/control API only (construct, inject, advance, inspect bounded
state/telemetry, snapshot/restore); it receives no callback per neural event or
spike. v0.6.0 deliberately contains no plasticity, STDP, assembly detection,
assembly-to-Cognit conversion, Cognit feedback, sensory/motor populations,
language/Goal integration, or World integration. Normal v0.5.x life therefore
owns an empty inactive substrate and retains its frozen trajectory.

Neural snapshots preserve both dynamic state and the complete innate physiology
configuration, including the event safety guard. Restore validates physiology,
micro-κ state, micro-ρ topology/polarity, and pending event targets, times, and
sequences before replacing native state. Requested state inspection reports
analytically projected potential/adaptation at current neural time without
mutating storage or sweeping silent micro-κ. The v0.6.0 substrate is frozen.

### Local plasticity and homeostasis (v0.6.1)

Micro-ρ polarity is fixed innate topology. Its magnitude remains nonnegative and
is bounded by innate weight limits; `plasticity_enabled` explicitly controls
whether a relation participates. Native incoming/outgoing adjacency supports
pair-based local timing updates without a global graph scan. A source trace read
before a target spike gives causal potentiation; a target trace read before a
source spike gives anti-causal depression. The same-time transaction determines
all spikes before applying any trace increments, preventing ID, relation, or
insertion order from fabricating causality.

Pre/post traces and a slow homeostatic threshold bias are lazy per-micro-κ
state. Homeostatic bias rises on spikes and decays analytically toward zero;
effective threshold is base threshold plus fast adaptation plus slow bias.
These are innate physiology, not learned semantic knowledge. Snapshot/restore
preserves physiology, traces, weights, flags, bias, telemetry, and pending
events. This remains entirely below cognition: no assemblies, Cognit bridge,
World/language/Goal/action coupling, reward, optimizer, or backpropagation.

### Emergent assemblies (v0.6.2)

An assembly is a native evidence record inferred from recurrent real micro-κ
spikes, not a Cognit, semantic class, externally registered group, or connected
component. Bounded timestamp-group episodes accumulate per-assembly member,
normalized activity, occurrence, and directed temporal support. Equal-time
spikes remain unordered; temporal identity uses only strict earlier/later
evidence and therefore tolerates timing jitter without erasing sequence order.

Similarity updates recurrent candidates, evidence ratios reject rare noise and
frequent distractors, and separate records permit overlapping membership and
novel patterns. Consolidated assemblies yield bounded read-only `AssemblyMatch`
records for partial/full recognition. Candidate/recent/temporal/match state is
bounded; lazy elapsed-time decay guides deterministic weak-candidate eviction.
All state and telemetry round-trip through the coarse snapshot API.

Temporal identity is structurally closed over normalized membership. The system
first derives stable members from recurrence and node specificity, then exposes
only supported temporal edges whose source and target are both in that final
set. Restore deterministically rebuilds this derived edge set from authoritative
saved support, preventing stale distractor edges from being resurrected.

Assembly observation occurs after the complete spike transaction and cannot
alter potential, refractory state, STDP, homeostasis, weights, event ordering,
or pending deliveries.

### Assembly-to-Cognit bridge (v0.6.3)

The first upward bridge is native and one-way. Consolidation and recognition
produce bounded coarse events with monotonic identities. `NativeBrainEngine`
owns both the authoritative Cognit graph and the stable AssemblyID-to-CognitID
mapping: consolidation allocates one ordinary Cognit. Recognition episodes are
identified by assembly ID and float64 neural time. Within one assembly window,
only `max(0, confidence - previous_peak)` enters the existing `receive()` rule;
silence longer than that window resets the peak under a new monotonic episode ID.
An explicit bounded drain advances the native cursor exactly once. Python may
adopt `NEURAL_ASSEMBLY` facade metadata at that boundary, but does not inspect or
process individual spikes and does not own numeric bridge state.

Deleting the Cognit invalidates its mapping; later recognition may allocate a
new monotonic Cognit ID. The bridge never creates Relations. Bridge events are
part of the substrate snapshot and mapping/cursor/counters are restored with the
matching engine graph snapshot. The optional micro-neuro runtime is still
outside `.sebrain v6` / `.seworld v7`, avoiding an invalid mapping-only
persistence section. There is no Cognit-to-micro feedback, semantic assignment,
World/language/Goal/planner/action coupling, reward, classifier, or backprop.

The existing continuous event scheduler adds a coarse `NEURAL_BRIDGE` boundary,
independent of World observation. One drain is event-bounded and shares global
`max_cognits` plus the ordinary per-transaction birth limit. Suppressed births
are consumed and counted; a later real recognition may retry after capacity is
freed. Event sequence orders a drain and event time preserves neural causality.

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

### Continuous World scheduling

`CONTINUOUS WORLD COMPLETION` is complete. Spawning uses absolute scheduled
`WORLD_SPAWN` events, lifecycle work uses explicit `MAINTENANCE` events, and
normal continuous behavior has no dependency on `world_tick()` or heartbeat
cadence. The frozen Python World tick schedule remains only as a compatibility oracle.

## 11. Persistence

Persistence is part of deterministic execution, not a presentation layer.

### `.sebrain`

Stores durable learned cognition and the native `NBRN` graph payload.

### `.seworld`

Continuous `.seworld` schema v7 stores the exact execution frontier, including:

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
- absolute spawn and maintenance scheduler frontiers.

Save is observational: saving must not change the future trajectory. v1/v2 continuous snapshots retain explicit compatibility/migration handling.

## 12. Determinism and acceptance invariants

The current accepted v0.5.4 cognition frontier has:

- `ELAPSED-TIME LAZY COGNITION: PASS`;
- `TRUE EVENT-DRIVEN COGNITION FRONTIER: PASS`;
- full pytest: 294 passed;
- CTest Release: 2/2 passed;
- identical deterministic trajectory digest for `PYTHONHASHSEED=1` and `77`;
- `full_graph_sync_calls == 0`;
- normal native Python physical World calls: 0;
- renderer sampling invariance: PASS.

The v0.5.2 benchmark/freeze data remains the performance/compatibility baseline. Long v0.5.5 5K/10K benchmarks have intentionally not been rerun during the correctness migration.

## 13. Observer/rendering architecture

Rendering is intentionally not part of cognition or physics.

The observer path is implemented as:

```text
C++ WorldRuntime
    -> native read-only RenderSnapshot
    -> RenderSnapshotChannel ------------------+
C++ authoritative Cognit/Relation substrate   |
    -> immutable BrainSnapshot                 |
    -> BrainSnapshotChannel -------------------+
                                                -> SDL3 + OpenGL observer
```

The observer never schedules cognitive work, advances WorldTime, or mutates authoritative World state. A native snapshot channel supplies value-owned state to its independent SDL3/OpenGL frame thread; observer lifecycle and frame cadence are trajectory-invariant and are excluded from persistence.

Both channels are latest-state-only C++20 `atomic<shared_ptr<const ...>>`
boundaries: they have no queue, renderer back-pressure, or mutable-state read.
Brain snapshots contain only numeric Cognit/Relation visualization fields;
Goals, planner state, memory and BeliefScene do not cross the boundary.
Publication happens at causal runtime events rather than render FPS. Layout,
birth animation and glow use observer-local presentation state and are neither
persisted nor fed back into the simulation. Python per-frame involvement is
zero. `_native_brain` and `SDL3.dll` are runtime-local build outputs and are not
versioned repository artifacts.

Brain observation is explicitly bounded. The producer emits at most 1024
Cognits and 4096 Relations while retaining total authoritative counts. It scans
raw Cognit priorities and iterates Relations only from the selected source set;
it never creates a complete Relation snapshot. The renderer applies a second
panel-area LOD (128–512 nodes, at most 2048 edges), caches geometry by immutable
snapshot identity and viewport size, and uploads dynamic VBOs only on a cache
miss. Normal frames issue one batched `GL_LINES` edge pass and one circular
`GL_POINTS` node pass. Render cost is therefore bounded independently of total
authoritative graph size.

The production host in `main.py` constructs `ContinuousRuntime`, attaches one native observer, and advances target WorldTime from monotonic host time plus the requested speed multiplier. The observer thread owns SDL polling and rendering; Python performs no per-frame calls. Headless execution uses the identical continuous runtime and differs only by omitting observer creation. The historical Pygame `ui/` package is legacy/debug-only and is not imported by production.

## 14. Receptive embodied symbol grounding

Language Pass 1 is a separate external sensory modality:

```text
external exact token
    -> immutable LanguageFrame
    -> scheduled LANGUAGE_INPUT(message_id)
    -> identity-only LanguageLexicon
    -> ordinary LANGUAGE_SYMBOL Cognit
    -> contrastive support/background/lift evidence
    -> ordinary directed ASSOCIATIVE Relations
    -> existing native activity wave
```

Before recall or planning, each real observation publishes an immutable
`GroundingContextSnapshot` containing only sensory-derived internal Cognit IDs
and salience. A bounded tracker accrues ordinary experiential background mass
over WorldTime. The latest snapshot remains current without attenuation until
replaced; retired snapshots then retain a 1-second eligibility window with a
0.5-second decay tau measured from retirement. Language never reads or
overwrites `core.last_wave`.

At LANGUAGE_INPUT, the core first enters the frame's exact native continuous
time. Python derives deterministic conditional probability/lift parameters and
submits one coarse generic Relation batch; C++ remains only the numeric
authority. Unfinished cognition causes same-time event-ID deferral.

Token identity is supplied; token meaning is learned. Grounding uses only the
entity's current internal Cognit context and never raw World state. The language
transaction neither changes physical EventSequence nor creates an ActionIntent.
`LANG` persists identity and unfinished statistical evidence; semantic effect is
carried by the same native Cognit/Relation graph as all other learned structure.
Real previous-language `.seworld v5` and `.sebrain v4` count schemas migrate
deterministically to v6/v5. Since they lacked elapsed experience time, migration
alone maps one old exposure to one compatibility experience unit and rebuilds
materialized target bookkeeping from persisted ASSOCIATIVE Relations.
This pass implements neither sentences, syntax, commands, production nor a
pretrained linguistic representation.

## 15. Ordered exact-symbol sequence and basic composition

Pass 2 adds immutable externally segmented utterances and a persistable
same-WorldTime execution frontier. Each continuation performs exactly one token
or one final COMPOSE work item. The utterance captures one embodied grounding
context before token processing, preventing earlier token waves from becoming
later-token grounding evidence.

After all constituent waves exist, Python records only adjacent directional
symbol pairs and derives deterministic bounded evidence. The generic native
coarse batch materializes ordinary `SEQUENTIAL` Relations while preserving
global resource limits and native numeric authority. No adjacency crosses an
utterance boundary.

`LanguageUtteranceResult` retains token order, constituent results, observed
adjacency and the union of retrieved non-language Cognits. It creates neither a
phrase Cognit nor phrase-specific meaning. Consequently first-ever combinations
compose from existing constituent ASSOCIATIVE semantics before same-utterance
sequence learning. This is not grammar, syntax induction, commands, or natural
language understanding.

`.seworld v7` persists the active utterance frontier and resumes the next token
exactly once; `.sebrain v6` persists durable sequence evidence. The respective
v6-world and v5-brain migrations preserve frozen Pass-1 state.

Every language continuation revalidates the ordinary cognition frontier, and
maintenance is deferred at the same WorldTime while an utterance is active.
The real Cognit deletion path invokes bounded Python language-bookkeeping
cleanup; it does not scan or reinterpret the native graph.

The observer layout is now `DIALOGUE | WORLD | BRAIN / STATUS`. A native
latest-only `DialogueSnapshotChannel` retains at most 64 immutable UTF-8 lines
and is read only by the render thread. Python publishes one EXTERNAL line when a
language input is actually accepted, never per token continuation or render
frame. ENTITY is a reserved display role only: speech production is not
implemented and the observer invents no entity output. Dialogue presentation
state is excluded from `.seworld` and `.sebrain`.

## 16. Relational compositional grounding

Pass 3 adds a bounded, read-only semantic composition layer after constituent
retrieval. For each token position it intersects the token's materialized
Pass-1 ASSOCIATIVE targets with that token's actual wave, removes dead,
`LANGUAGE_SYMBOL`, and `TARGET` Cognits, then ranks remaining anchors by learned
evidence and Cognit confidence with stable ID tie-breaking. Equal learned
evidence is retained as ambiguity rather than converted into certainty.

An existing `RELATIONAL` token Cognit maps through `core.relational_nodes`; an
existing `BOUND_RELATION` maps through `BeliefScene`. These are the only sources
of `RelationToken`. With one resolved relational anchor and two resolved
non-relational anchors, utterance order binds participants to directed role
indices and creates a normal immutable `RelationalStructure`. The structure is
compatible with `BeliefScene.best_binding`; absent support yields a partial
result with no invented relation.

`LanguageRelationalResult` is transient derived output. It owns no semantic
policy and performs no learning, graph mutation, Goal/ActionIntent creation, or
World mutation. The persisted Pass-2 frontier contains all information needed
to derive the same result after mid-utterance `.seworld v7` continuation;
`.sebrain` remains v6.

`RelationalStructure.source_cognits` is strictly the ordered participant tuple;
the relation Cognit's identity remains in result provenance. `relations` is
canonicalized by the same constructor used for all relational structures, while
`role_edges` retains the observed directed token. `BeliefScene.best_binding`
uses the explicit participant assignment with no geometric transform when the
structure carries exactly one Cognit per role; structures without bound
participants retain the previous permutation/transform search.

The closure experiment learns all three nonce meanings through the standard
native `World -> SensoryFrame -> memory/relational Cognit -> Pass-1 grounding`
path. No semantic Cognit ID is supplied to language grounding. Both the initial
surface labels and a complete nonce-label permutation compose the same held-out
first-occurrence structure.

## 17. Learned grounded requests

Pass 4 adds one generic `COMMUNICATIVE_REQUEST` Cognit and bounded deterministic
per-token request support/trial evidence. External demonstrations supply a
desired relational structure; contrastive non-request utterances provide the
negative denominator. Only thresholded support and conditional probability
materialize an ordinary token-to-concept ASSOCIATIVE Relation. Surface text has
no built-in request semantics.

At COMPOSE, the request concept must occur in the actual wave of a materialized
cue, while every non-cue Pass-3 semantic slot must be resolved. The derived
`LanguageRequestResult` then carries the unchanged `RelationalStructure` into
`SyntheticEntityCore.install_relational_goal`. This creates an ordinary Goal
with `origin="LANGUAGE_REQUEST"`; planner, memory recall, BeliefScene mismatch,
imagination, and action scoring remain the existing generic machinery.

Relational-goal behavior is selected by the presence of a matching ordinary
target structure and target Cognits, never by `Goal.origin`; origin is only
provenance. Therefore a language Goal enters the same target seeding,
progress/action scoring, and relational subgoal management as an external
target. The closure curriculum trains a cue against X and proves first-use
generalization to independently grounded Y, which was never demonstrated with
that cue.

Language interpretation creates no ActionIntent and changes neither physical
World nor EventSequence. Request evidence and concept identity live in the
existing UTF-8 LANG persistence payload (`.seworld v7`, `.sebrain v6`) with
missing fields interpreted as the v0.5.6 no-request state. Token identity is
Unicode NFC only, with no case or script normalization.

Queued v7 utterance rows optionally carry a serialized request target; legacy
three-field inbox rows remain valid. Request relation materialization uses one
deterministic shared `max_new_relations_per_tick` budget across all qualifying
cue symbols and records a cue only after the ordinary Relation exists.

## 18. Current roadmap

```text
v0.5.2 frozen native compatibility baseline                    DONE
    -> elapsed-time lazy cognition                              DONE
    -> true event-driven cognition frontier                     DONE
    -> continuous world completion                              DONE
    -> native C++ SDL3/OpenGL observer                           DONE
    -> bounded GPU brain-view scaling                            DONE
    -> receptive symbol grounding                               DONE
    -> multi-token sequence/basic composition                   DONE
    -> relational compositional grounding                       DONE
    -> grounded requests / language -> goals                    DONE
    -> continuous multi-entity runtime
    -> full 3D World
    -> Entity visual/retina/gaze input
```

v0.5.x LANGUAGE FOUNDATION: FROZEN
