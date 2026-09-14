# Synthetic Entity v0.5.5 — Current Status

## LANGUAGE PASS 2 — MULTI-TOKEN SEQUENCE + BASIC COMPOSITIONAL RETRIEVAL

LANGUAGE PASS 2 — MULTI-TOKEN SEQUENCE + BASIC COMPOSITIONAL RETRIEVAL: PASS

LANGUAGE PASS 2 CLOSURE: PASS — FROZEN

- Immutable `LanguageUtteranceFrame` accepts only externally segmented exact
  NFC symbols, with a maximum of **16** tokens. A string is not treated as a
  tokenized utterance; the frozen single-token API delegates to Pass 1.
- Multi-token work uses one persistable `LanguageUtteranceFrontier`. Each token
  consumes one continuation/cognitive tick, followed by one COMPOSE
  continuation/tick, all at the utterance's unchanged WorldTime. Utterances do
  not interleave.
- Every `LANGUAGE_CONTINUE` rechecks the ordinary cognition transaction and
  reschedules at the same WorldTime when it is unfinished. Maintenance likewise
  performs no lifecycle work while a language frontier is active.
- One embodied context is frozen at utterance arrival and reused for every
  token. Token waves cannot become grounding input for later tokens. Pure
  multi-token retrieval leaves Pass-1 embodied evidence unchanged.
- Python maintains bounded directional adjacency evidence (minimum support
  **2**, confidence k **3.0**, at most **64** candidates/source). A finalization
  batch materializes ordinary LANGUAGE_SYMBOL `SEQUENTIAL` Relations under the
  existing global Cognit/Relation budgets.
- Composition is the deterministic union of non-language Cognits retrieved by
  constituent token waves. There are no phrase Cognits, phrase dictionaries,
  grammar roles, command mappings, Goals, or ActionIntents.
- First-ever pair retrieval, real embodied constituent composition, unseen
  combination generalization, order permutation, duplicate/unknown tokens,
  frozen-context isolation, capacity pressure and evidence order invariance:
  **PASS**.
- `.seworld` schema **v7** persists pending utterances and exact mid-utterance
  execution state; real v6 single-token worlds migrate without graph mutation.
  `.sebrain` schema **v6** transfers sequence evidence/materialized bookkeeping;
  real Pass-1 v5 brains migrate with empty sequence evidence.
- Language sequence/evidence dictionaries follow real Cognit deletion through
  `LanguageLexicon.on_cognit_deleted`; forgotten tokens are reborn under a new
  monotonic ID without inheriting stale sequence state.
- The native SDL3/OpenGL observer has a bounded left **DIALOGUE** panel backed by
  a latest-only immutable 64-line native channel. Accepted EXTERNAL utterances
  publish once at event boundaries. ENTITY is reserved for future real speech;
  entity language production is not implemented and no fake response is shown.
- Focused closure/UI tests: **27 passed**; focused Pass-2 tests: **13 passed**;
  frozen Pass-1 tests: **25 passed**; critical regressions: **115 passed**;
  full pytest: **294 passed**; Release
  native build: **PASS**; CTest: **2/2**.
- `full_graph_sync_calls == 0`; no-language digest remains
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  utterance curriculum is identical under `PYTHONHASHSEED=1/77`.

## LANGUAGE PASS 1.1 — EMBODIED GROUNDING HARDENING

LANGUAGE PASS 1.1 — EMBODIED GROUNDING HARDENING: PASS

- `GroundingContextSnapshot` is captured inside the real observation transaction
  from matched sensory Cognits, perceptual/memory-active Cognits, and current
  relational/bound Cognits, before recall and planning propagation.
- Grounding never reads ordinary `core.last_wave`. A language wave is returned as
  `LanguageProcessingResult` and does not overwrite the ordinary wave.
- `GroundingContextTracker` keeps the latest embodied context current, at full
  salience, until a real observation replaces it. Replaced contexts retire at
  that exact WorldTime and then use a **1.0 s** horizon and **0.5 s** exponential
  tau measured from retirement; duplicate salience merges by deterministic max.
- Experiential background mass accrues from ordinary embodied contexts over
  elapsed WorldTime. It is independent of language event count and render FPS;
  minimum background before Relation birth is **0.5 s**.
- Relation strength/confidence are deterministic functions of accumulated
  support mass, grounded trials, experiential background and lift. Curriculum
  order invariance passes.
- Pure symbol retrieval is Relation use, not grounding evidence. With no valid
  filtered embodied context it increments exposure diagnostics and propagates
  the symbol wave, but performs no grounded trial, evidence mutation, language
  Relation batch, or learner-driven Relation evidence/touch-time refresh.
- LANGUAGE_INPUT enters exact native continuous time before mutation, consumes
  one cognitive tick, and defers at the same WorldTime behind unfinished
  cognition. An action already in flight is neither cancelled nor duplicated.
- Vocabulary respects `max_cognits`; Relation creation respects `max_relations`
  and `max_new_relations_per_tick`. Unmaterialized evidence is capped at **256**
  candidates per symbol.
- Language performs **0 outgoing scans in normal learning** and one generic
  coarse native Relation batch when updates exist. The batch returns exact
  created targets and updates only its owned numeric fields, preserving all
  other existing Relation metadata. Python retains meaning policy; C++ mutates
  numeric Relation state. `full_graph_sync_calls == 0`.
- Real embodied nonce grounding, embodied label permutation, first-word-only
  grounding, temporal delay/expiry, last-wave isolation, deferral, exact time,
  resource bounds, order invariance, and real legacy migration: **PASS**.
- `.seworld` schema **v6** persists durable background plus the exact
  current/historical retirement frontier and inbox. Real previous-language
  `.seworld v5` state migrates to v6. `.sebrain` schema **v5** transfers durable
  grounding but no episode context or pending utterance; real previous-language
  `.sebrain v4` migrates to v5. Legacy count background uses an explicit
  one-exposure/one-compatibility-unit normalization because elapsed time was not
  present, and materialized targets are reconstructed from the persisted graph.
- Focused language tests: **25 passed**; critical regressions: **145 passed**;
  full pytest: **276 passed**; Release native build: **PASS**; CTest: **2/2**.
- No-language `PYTHONHASHSEED=1/77` trajectory remains deterministic with digest
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  the real embodied curriculum is also identical under both hash seeds.

The earlier association-only Pass 1 proof is superseded by this embodied gate.
LANGUAGE PASS 1 — RECEPTIVE SYMBOL GROUNDING: PASS

## BRAIN VIEW SCALING OPTIMIZATION

BRAIN VIEW SCALING OPTIMIZATION: PASS

- Producer limits are named observer constants: **1024 Cognits / 4096 Relations**.
  Snapshots also carry exact total/visible/active counts and truncation state.
- Deterministic selection prioritizes active, recent, and newly created Cognits.
  Relations are top-K ranked from visible sources by current use/activity,
  strength and confidence; both endpoints must be visible.
- Normal publication performs **no** `RelationStore::snapshot()` or other full
  Relation-vector copy. It reads raw observational fields and does not touch lazy
  time, confidence, use markers, RNG, revisions, or lifecycle.
- Panel-area LOD is **128–512 nodes** and at most `min(nodes*4, 2048)` edges.
  The tested desktop panel displays **128 / 10000 Cognits** and at most
  **512 / 50000 Relations**.
- `NativeObserver` caches snapshot identity, viewport dimensions and CPU/GPU
  geometry. Repeated frames do not rebuild unchanged graph geometry.
- Edges use one dynamic `GL_LINES` VBO draw; Cognits use one circular
  `GL_POINTS` VBO draw. The previous CPU pixel-walk/scissor Relation renderer
  is removed.
- Presentation history is bounded: current cached geometry is LOD-bounded and
  Cognit birth identity uses a compact monotonic-ID frontier rather than an
  unbounded per-Cognit map.
- 10,000-Cognit/50,000-unique-Relation fixture: snapshot **1024 / 4096**,
  publication **1.809 ms** observed locally; exact selection is repeatable.
- Focused observer/continuous regression: **41 passed**; full pytest:
  **251 passed**; observer-enabled Release build: **PASS**; CTest: **2/2**.
- Real Windows window smoke and resize-safe rendering: **PASS**.
- Python calls per render frame: **0**; `full_graph_sync_calls`: **0**;
  exact trajectory invariance: **PASS**. Established `PYTHONHASHSEED=1/77`
  digest remains `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`.


## NATIVE OBSERVER VISUAL UI + BRAIN GRAPH

NATIVE OBSERVER VISUAL UI + BRAIN GRAPH: PASS

- The SDL3/OpenGL window now uses a 72/28 research layout: polished physical
  viewport left, Brain and Status panels right.
- Native Cognits render as activity-scaled nodes; primitive/composite state has
  a secondary mark. Native Relations render as typed, strength/confidence-scaled
  edges and highlight only from observed current use/activity.
- New Cognit IDs acquire observer-local birth time and fade/scale in. Stable
  deterministic ID hashing retains layout across snapshots without simulation RNG.
- `BrainSnapshotChannel` is an immutable latest-only
  `atomic<shared_ptr<const BrainSnapshot>>`. Snapshot production reads the sole
  authoritative native graph and occurs once at causal runtime boundaries, not
  per render frame.
- The render thread reads only `RenderSnapshotChannel` and
  `BrainSnapshotChannel`. Python callbacks per frame: **0**.
- Graph/status DTOs and presentation state are excluded from `.sebrain` and
  `.seworld`; publication leaves `full_graph_sync_calls == 0`.
- Focused brain/native observer/continuous regression: **53 passed**.
- Full pytest: **250 passed**. Observer-enabled Release build: **PASS**.
- CTest Release: **2/2 passed**.
- Real Windows graphical smoke: **PASS** (resize-safe split viewport, live graph,
  clean timed close).
- `PYTHONHASHSEED=1/77` established trajectory digest remains
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`.

## PRODUCTION NATIVE UI MIGRATION

PRODUCTION NATIVE UI MIGRATION: PASS

    python main.py
      -> ContinuousRuntime
      -> authoritative native WorldRuntime
      -> immutable RenderSnapshotChannel
      -> NativeObserver thread
      -> SDL3/OpenGL

- Default execution contains no Pygame import and never calls `Simulation.step()` per frame.
- Live target WorldTime comes only from monotonic host time multiplied by `--speed`; observer frames never define simulation progress.
- `--headless --seconds T` runs the same `ContinuousRuntime` without an observer and advances to absolute WorldTime `T`.
- `--save` uses `.seworld`; `--load` restores through `ContinuousRuntime.load_world()` before observer attachment.
- `--ticks` was removed. Legacy tick telemetry is explicitly rejected instead of reintroducing the discrete runtime.
- Observer shutdown, Ctrl+C, and exceptions execute idempotent `observer.stop()` cleanup.
- The old `ui/` package remains legacy/debug-only. Pygame was removed from production requirements.
- Focused entrypoint **9 passed**; live observer **5 passed**; continuous-world **28 passed**; render snapshot/observer **4 passed**.
- Full pytest **247 passed**; observer-enabled Release build **PASS**; CTest Release **2/2 passed**.
- Established `PYTHONHASHSEED=1/77` digest remains `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`.

## NATIVE C++ SDL3 / OPENGL OBSERVER

NATIVE C++ SDL3 / OPENGL OBSERVER: PASS

PASS 1 — NATIVE RENDER SNAPSHOT BOUNDARY: PASS

PASS 2 — SDL3 / OPENGL NATIVE 2D RENDERER: PASS

The optional `SE_BUILD_OBSERVER` CMake target fetches pinned SDL 3.2.8 and
builds a native OpenGL observer plus deterministic demo. Its native frame loop
accepts only value-owned `RenderSnapshot` values through `SnapshotSource`; it
does not invoke Python or mutate `World`. Renderer geometry preparation is
unit-testable without a window. Live attachment uses the native snapshot channel
owned by the same authoritative `WorldRuntime`; lifecycle, trajectory invariance,
post-stop continuation, and persistence exclusion are covered by tests.

Observer closure details:

- `RenderSnapshotChannel` is a latest-state-only C++20 `atomic<shared_ptr<const RenderSnapshot>>`; production code contains no mutex, lock guard, queue, condition variable, or spin lock.
- Public `World::apply()` mutates through `apply_internal()` and publishes exactly one fresh immutable snapshot without changing EventSequence.
- `World::apply_intent()` and `World::resolve_intents()` use the same non-publishing helper; multi-body resolution publishes one coherent snapshot only after the complete batch.
- Previously retained snapshots remain immutable and safe while newer snapshots are published concurrently.
- Observer sampling causes zero Python per-frame calls, scheduler/World events, EventSequence increments, or cognition work. Renderer wall-clock has no path into WorldTime, scheduler, RNG, or cognition.
- The observer now includes the separate right-side Cognit/Relation visualization
  described above; it remains wholly downstream of authoritative cognition.
- `_native_brain` and `SDL3.dll` are runtime-local build outputs. Neither is tracked; `cpp/build*`, `CMakeFiles`, CMake cache files, and pip build logs are also excluded.
- Repository cleanup: **PASS**.

Current verification after a fresh observer-enabled Release build: focused
live observer **5 passed**, continuous-world **28 passed**, render snapshot/observer **4 passed**; full pytest **247 passed**;
CTest Release **2/2 passed**.

## CONTINUOUS WORLD COMPLETION

CONTINUOUS WORLD COMPLETION: PASS

The implementation branch schedules `WORLD_SPAWN` and `MAINTENANCE` at
absolute `WorldTime`, and normal `ContinuousRuntime` no longer dispatches
`NativeWorld.world_tick()`. The frozen legacy `world_tick()` API remains.
`RuntimeEvent.id` is now retained solely for scheduler ordering; physical
World mutations allocate their own `Simulation.event_sequence` at execution.
Maintenance passes its absolute deadline through the established continuous
time entry point before bounded lifecycle work.
Final verification: continuous-world focused tests 28 passed; focused
runtime/frontier/elapsed selection 97 passed; full pytest 247 passed; clean
observer-enabled Release native build PASS; CTest 2/2 PASS. `PYTHONHASHSEED=1/77` digest:
`e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`.
Normal continuous `world_tick` calls, native Python physical World calls, and
`full_graph_sync_calls` are all zero.

## TRUE EVENT-DRIVEN COGNITION FRONTIER

TRUE EVENT-DRIVEN COGNITION FRONTIER: PASS

## ARCHITECTURE

    SENSORY_CHANGE
      -> bounded observation / new cognition generation
      -> COGNITION_WAKE
      -> COGNITION_CONTINUE x N at the same WorldTime
      -> QUIESCENT
      -> one decision commit
      -> WORLD_ACTION_COMPLETE at WorldTime + 0.15

- Normal `ContinuousRuntime` uses dedicated continuous core/planner APIs and calls neither legacy `SyntheticEntityCore.step()` nor `DeliberativePlanner.deliberate()`.
- One `COGNITION_CONTINUE` consumes at most one explicit pending cognitive work item.
- `cognitive_tick`, planner `internal_tick`, and `total_cycles` increment once per continuation; EventSequence and float64 WorldTime remain independent.
- External sensory evidence is applied once in the observation transaction. Predictions, trace, previous action/context, active homeostasis, planner commit, and action are committed once after quiescence.
- Wake/continue payloads carry a monotonically increasing generation. Stale events are deterministic no-ops.

## QUIESCENCE MODEL

`QUIESCENT` iff a valid candidate exists, `pending_work` is empty, no deduplicated invalidation key remains pending, and the session is not finalized. There is no stable-count, repetition count, numeric epsilon, elapsed-time, timeout, minimum-cycle, or maximum-cycle stopping rule. The diagnostic guard reports generation, WorldTime, pending kinds, recent work history, and Goal ID, then raises without forcing an action.

## COGNITIVE WORK TYPES

- `RECALL`: seeded by a new sensory episode or a changed Goal/cue/revision; performs retrieval and exactly one recall stimulation.
- `PROPAGATE`: caused by a recall/internal activation and carries explicit seed Cognits.
- `IMAGINE`: caused by a new/invalidated working-state and Goal input.
- `PLAN_REFINE`: caused by new futures; runs one existing bounded `_search`. A Goal/subgoal change invalidates the candidate and creates a new recall chain.

## CAUSAL WORK CHAIN

    RECALL
      -> PROPAGATE
      -> IMAGINE
      -> PLAN_REFINE
      -> EMPTY
      -> QUIESCENT

The internally changed-Goal fixture produces two such chains before quiescence.

## RECALL SEMANTICS

Recall may repeat only when its exact semantic key `(Goal ID, target IDs, working revision)` changes. Pending work identities are deduplicated. Repeated scheduler events alone cannot rerun recall or stimulate a Cognit: **NO**.

## CONTINUOUS BUDGET

`max_deliberation_cycles` participates in continuous behavior: **NO**. The frozen legacy `deliberate()` retains its original budget. With the continuous maximum set to 1, the tested session still consumes its four causally pending work items and matches a maximum of 12.

## FRONTIER PERSISTENCE

Continuous `.seworld` schema version 4 persists the schema-v3 cognition frontier plus absolute spawn and maintenance scheduling state. Event-by-event continuation passes at all seven required cognitive work boundaries. No consumed work replays after load. v1 retains its explicit legacy pending-wake adapter; v2 unfinished stable-counter sessions migrate conservatively into one causal recall chain; v3 snapshots deterministically reconstruct the new World timers.

## HOMEOSTATIC EVENT SEMANTICS

- Passive Cognit/Relation/memory/Goal evolution remains lazy elapsed-time behavior.
- Recall stimulation, waves, and final active homeostasis remain causal activation operations. Same-time continuations invent no elapsed `dt`.

## DETERMINISM

- `PYTHONHASHSEED=1`: `f527b2d204acb87a7279e53783e66d3640086eba1bb70577653d855f21da2685`
- `PYTHONHASHSEED=77`: `f527b2d204acb87a7279e53783e66d3640086eba1bb70577653d855f21da2685`
- Renderer sampling and arbitrary host work between continuation events are observational.

## CONTINUATION COUNTS

- Small deterministic simple/Goal-invalidation sample: **min 4 / mean 6.0 / max 8** continuation events.
- Ordinary 20-decision sample: **min 4 / mean 4.0 / max 4**; these values are observations, not invariants.
- Ordinary sample mean native FFI calls per continuation: **15.16**.
- Session-local working state and semantic caches persist across events and save/load.
- `full_graph_sync_calls == 0`: **PASS**.
- Normal native Python physical World calls: **0 / PASS**.

## FRONTIER GATE CHECKPOINT TESTS

Focused frontier counts are retained; repository-wide counts reflect the current observer-enabled build:

- Event-driven cognition frontier focused module: **18 passed**.
- Frontier plus continuous runtime modules: **31 passed**.
- Elapsed/native/causal/legacy compatibility selection: **81 passed**.
- Full pytest: **237 passed**.
- CTest Release: **2/2 passed**.
- Long 5K/10K benchmarks were not run.

## FIRST FAILURE

None.

## NEXT GATE

**SCALING / NATIVE-BOUNDARY CLEANUP**

Not started. Continuous World completion and the native SDL3/OpenGL observer are complete.

## FRONTIER MODIFIED FILES

- consciousness/planning.py
- simulation/continuous.py
- tests/test_v053_continuous_runtime.py
- tests/test_v053_cognition_frontier.py
- CURRENT_STATUS.md

## ELAPSED-TIME LAZY COGNITION

ELAPSED-TIME LAZY COGNITION: PASS

## CORRECTIVE PASS

Blocker 1 — homeostatic clamp and save invariance:

- Continuous Cognits preserve an unclamped float64 latent homeostatic threshold.
- The behavior-visible threshold remains clamped to the configured minimum/maximum.
- Intermediate reads no longer discard latent motion beyond either clamp boundary.
- Split versus one-shot evolution passes for 0.1+0.2, 0.25+0.75, 1+9, and 1000 seconds at both clamps.
- Reading every 0.01 seconds matches one touch after 10 seconds.
- Continuous save_graph no longer performs its legacy all-Cognit catch-up.
- No-save, save-without-load, and save/load branches converge to identical behavior-affecting Cognit and latent state.
- Continuous .seworld capture now snapshots semantic state before capturing the matching native/frontier payload.

## BLOCKER 2 — TARGET MEMORY

**PASS**

- Candidate discovery is conservative: exact relation-token hits and directly associated places are always admitted.
- Zero-token-overlap candidates use participant-count plus 0.001-wide maximum-confidence buckets.
- For participant counts n/m and bucket upper confidence c, the admissible bound is:
  - roles = min(n,m) / max(n,m)
  - role_support = min(1,n/m)
  - structural_upper = 0.2 * roles * min(c,target_confidence)
  - strength_upper = (0.1 + 0.65 * structural_upper + 0.25 * role_support) * c
- Recency is bounded by 1. Group mean confidence and every member confidence cannot exceed the bucket upper bound, so a place whose exact zero-overlap score can reach 0.12 cannot be excluded.
- Exact relation-token matches bypass the zero-overlap bound; direct associations bypass all structural pruning.
- Existing memory_structure.match, relevance, recency, and final threshold scoring remain authoritative after admission.
- Adversarial high-confidence/no-token-overlap recall: **PASS**.
- Low-confidence final rejection: **PASS**.
- Participant-count, stale/fresh, and direct-association cases: **PASS**.
- Deterministic randomized differential: **80 worlds passed; 0 false negatives**.
- Full-scan oracle is test-only and is not called by runtime.
- Strengthened scaling result:
  - total memories: **10,000**
  - total places: **5,000**
  - exact-token matching places: **2**
  - zero-token/high-confidence recallable places: **2**
  - candidate places: **4**
  - candidate memories: **8**
  - memories materialized: **8**

Blocker 3 — causal Goal persistence:

- Passive waiting applies only goal_decay raised to elapsed simulated seconds.
- Understanding is applied exactly once at the cognitive event that produced it.
- A new observation never changes decay over the preceding silent interval.
- Low-before/high-after and high-before/low-after causal-order scenarios pass.
- Ten observations at exact one-second cadence match the frozen per-observation multiplicative formula.
- Goal age remains a causal/event count.
- Continuous save/load preserves Goal time anchors and exact continuation.

## TIME SEMANTICS

Elapsed-time state:

- Cognit activity, utility, inactive trace, latent/visible homeostatic threshold, last touch, and last activation time
- Relation passive confidence and separate confidence/evidence time frontiers
- memory confidence, confirmation time, recency, and idle duration
- Goal passive persistence, creation time, unavailable duration, and cooldown timestamp

Event/count state retained:

- EventSequence, event IDs, cognitive_tick, and last_activated_cognitive_tick
- evidence windows, support, confirmations, contradictions, and prototype evidence
- prototype occurrences and explained_sum
- percept observation age and missing_ticks
- wave/refractory steps
- Cognit age and low_retention_ticks
- planner depth, expansions, tie cursors, and subgoal attempt cooldown
- Goal age, attempts, interventions, completions, and causal observations

## COMPLEXITY

- Native dormant Cognits: **100,000**
- Elapsed jump: **1,000 seconds**
- Materialized before touch: **0**
- Materialized after touching {7, 19}: **2**
- Target memories: **10,000**
- Target candidate/materialized memories: **8 / 8**
- No time-advance graph scan and no target full-memory scan remain in the continuous path.

## PERSISTENCE

- Clamp-crossing latent frontier: **PASS**
- Save is behaviorally observational: **PASS**
- No-save == save == save/load: **PASS**
- Exact .seworld continuation at 12.001, 12.149, 12.437, and 12.999 seconds: **PASS**
- Relation semantic-identity frontier restore: **PASS**
- Memory and Goal elapsed anchors: **PASS**

## TESTS

- Corrective elapsed, target-memory, and continuous acceptance set: **51 passed**
- Elapsed-time focused module: **32 passed**
- Target-memory adversarial/randomized/scaling module: **6 passed**
- Continuous runtime module: **13 passed**
- v0.5.2 native/causal compatibility subset: **43 passed**
- Full pytest: **183 passed**
- CTest: **1/1 passed**
- Release native rebuild: **PASS**
- full_graph_sync_calls == 0: **PASS**
- Normal native Python physical World calls: **0 / PASS**
- Render sampling invariance: **PASS**
- Long 5K/10K benchmarks were not run.
