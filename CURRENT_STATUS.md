# Synthetic Entity v0.6.3 — Current Status

## v0.6.3 — ASSEMBLY -> COGNIT

**PASS — the one-way native assembly-to-Cognit bridge is accepted.**

**v0.6.3: FROZEN**

- Consolidation emits one monotonic coarse event and births one ordinary Cognit
  in the authoritative `NativeBrainEngine` graph. Candidates and one-shot
  activity birth nothing. The engine owns the stable `AssemblyID -> CognitID`
  mapping; overlap/novelty produces distinct monotonic Cognit IDs and no
  Relations.
- Recognition confidence is clamped to `[0, 1]` and passed as energy through
  ordinary native `receive()`. The frozen order remains full > partial >
  reversed. Python only adopts facade metadata `kind="NEURAL_ASSEMBLY"` at the
  coarse boundary; it never processes individual spikes or owns numeric state.
- Exactly-once delivery uses persisted monotonic event identities and a native
  cursor. The event log is bounded to 256 and each drain to 64 by default; cursor
  overflow is a hard error. Consumed events do not replay and pending events
  deliver once after restore.
- Cognit deletion immediately invalidates the mapping. Later recognition births
  a new monotonic ID; dead IDs are not reused.
- Substrate snapshot/restore preserves bridge events and their future timing;
  engine bridge state preserves mapping/cursor/counters alongside the matching
  graph snapshot. `.sebrain v6` and `.seworld v7` remain unchanged because they
  do not own the optional micro-neuro runtime; persisting its mapping alone would
  be invalid half-state.
- No reverse Cognit→micro path, semantic assignment, automatic Relations,
  World/language/Goal/planner/action coupling, reward, classifier or backprop was
  added. Silent/default substrates emit zero bridge events.
- Focused v0.6.0–v0.6.3: **37 passed**; full pytest: **352 passed**; Release
  build: **PASS**; CTest Release: **2/2 passed**. No-language digest remains
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  `full_graph_sync_calls == 0`.

Next: not started.

## v0.6.2 — EMERGENT ASSEMBLIES

**PASS — native evidence-derived assemblies accepted.**

**v0.6.2: FROZEN**

- Assembly membership is inferred only from recurring emitted micro-κ spikes.
  Per-assembly member participation, normalized individual activity, occurrence
  support, and directed temporal support determine stable core membership; no
  membership lists, labels, classifiers, or semantic hints enter the detector.
- Final temporal identity is membership-closed: temporal support is filtered
  only after stable membership normalization, and every persisted/exposed edge
  has both endpoints in the final member set. Restore rebuilds this derived edge
  view from authoritative support, so stale excluded-node edges cannot return.
- Activity episodes preserve timestamp groups. Spikes at the same float64 time
  contribute unordered coactivation but never a directed edge; temporal support
  requires strictly earlier/later groups and tolerates timing jitter.
- Deterministic similarity updates compatible candidates instead of creating an
  exact-timestamp record per occurrence. One-shot records cannot consolidate;
  recurrent evidence crosses candidate and consolidation thresholds. Rare noise
  and frequent distractors do not enter the stable core. Overlapping and novel
  assemblies remain independent.
- Consolidated assemblies produce bounded native `AssemblyMatch` summaries.
  Correct full recurrence scores above correct partial recurrence, which scores
  above reversed order. Recognition does not edit synapses or neural physics.
- Recent activity, members, temporal edges, candidate count, consolidated count,
  and recent matches are bounded. Weak/old candidates use lazy elapsed-time
  decay for deterministic capacity eviction; silent time performs no assembly
  work.
- Ordinary Python `snapshot()/restore()` now preserves assembly physiology,
  IDs, recent spikes, candidate/consolidated evidence, normalized node support,
  recent matches, and telemetry for exact continuation. `.sebrain v6` and
  `.seworld v7` remain unchanged.
- Tracking enabled/disabled runs have exact neural-state parity. There is no
  Python per-spike processing, Cognit creation, assembly↔Cognit bridge, World,
  language, Goal, planner, action, or motor coupling.
- The adversarial closure makes frequent X fire globally and inside three
  A→X→B→C windows. Raw X temporal support reaches at least 3, yet specificity
  excludes X from membership and membership-closed filtering removes every X
  edge while preserving A/B/C temporal structure.
- Focused v0.6.0–v0.6.2 tests: **30 passed**; full pytest: **345 passed**;
  Release build: **PASS**; CTest Release: **2/2 passed**. Silent 10,000 micro-κ /
  50,000 micro-ρ assembly work: **0**. No-language digest remains
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  `full_graph_sync_calls == 0`.

v0.6.2 remains frozen beneath the accepted v0.6.3 bridge.

## v0.6.1 — LOCAL PLASTICITY + HOMEOSTASIS

**PASS — local native plasticity and homeostasis accepted.**

**v0.6.1 — LOCAL PLASTICITY + HOMEOSTASIS: FROZEN**

- Micro-ρ has an immutable innate polarity, bounded mutable nonnegative weight
  magnitude, and explicit `plasticity_enabled` control. Native incoming and
  outgoing adjacency limits learning work to a spiking node's local degree.
- Frozen v0.6.0 fixed edges preserve their original domain: every finite
  nonnegative magnitude is valid when `plasticity_enabled == false`, including
  values outside v0.6.1 learning bounds. Bounds apply only to plastic edges in
  both creation and snapshot validation; STDP still clamps every plastic update.
- A native two-phase same-time spike transaction applies pair-based STDP from
  traces strictly before the timestamp. Pre→post pairs potentiate, post→pre
  pairs depress, and simultaneous spikes create no artificial causal learning.
  There is no Python callback per spike or plasticity update.
- Per-micro-κ pre/post traces and slow threshold bias are analytically lazy.
  Homeostasis is innate physiology, separate from fast adaptation: spiking raises
  bias, elapsed quiet time projects it toward zero, and silent networks receive
  no global neural/homeostatic update.
- All plasticity/homeostasis physiology, relation flags/weights, traces, bias,
  timestamps, queue, and telemetry are native snapshot state and restore exactly
  into an instance constructed with different defaults. `.sebrain v6` and
  `.seworld v7` remain deliberately unchanged.
- The substrate remains isolated: no assembly detection, micro↔Cognit bridge,
  World, language, Goal, action, reinforcement, or backpropagation coupling.
- Focused v0.6.0/v0.6.1 tests: **21 passed**; full pytest: **336 passed**;
  Release build: **PASS**; CTest Release: **2/2 passed**. No-language digest
  remains `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  `full_graph_sync_calls == 0`.

v0.6.1 remains frozen under the accepted v0.6.2 observational assembly layer.

## v0.6.0 — NATIVE EVENT-DRIVEN MICRO-NEURODYNAMIC SUBSTRATE

**PASS — isolated native substrate accepted.**

**v0.6.0 CLOSURE: PASS**

**v0.6.0 — NATIVE EVENT-DRIVEN MICRO-NEURODYNAMIC SUBSTRATE: FROZEN**

- Native `NeurodynamicSubstrate` supplies SoA micro-κ state, stable monotonic
  IDs, fixed delayed signed micro-ρ edges, float64 continuous neural time, and
  a deterministic `(time, sequence)` native event queue. Same-time events are
  deterministically aggregated per target; lazy leak/adaptation touches only
  affected micro-κ; refractory deliveries are discarded and counted.
- It is owned by `NativeBrainEngine` and is empty by default. It has no global
  neural tick, Python per-event callback, Cognit/Relation coupling, plasticity,
  STDP, assemblies, World, language, Goal, motor, or sensory integration.
  Physiology constants are innate substrate physics. Snapshot/restore exactly
  preserves neural continuation, including all innate physiology and event guard,
  even when restored into an instance built with different defaults. Snapshot
  validation rejects invalid physiology, state, micro-ρ topology/polarity, and
  pending event targets/times/sequences. `.sebrain v6` and `.seworld v7` are
  intentionally unchanged.
- `states(ids)` projects potential and adaptation analytically at current neural
  time for requested IDs without mutating lazy storage or sweeping the network.
- Focused native/Python micro-neurodynamic tests: **11 passed** — analytical lazy
  leak, excitation, inhibition/same-time aggregation, delayed chain,
  refractory, adaptation, deterministic replay, physiology-safe
  snapshot/restore, invalid snapshot validation, and silent 10,000 micro-κ /
  50,000 micro-ρ zero-event-work check.
- No-language deterministic baseline remains
  `e334137aab48aac629c9ac0d4dbc77ea8ec7f51203acda0c970a9bb647c3d731`;
  `full_graph_sync_calls == 0`.
- Verification: full pytest **326 passed**; Release native build **PASS**;
  CTest Release **2/2 passed**.

No v0.6.1 work has started.

## LANGUAGE PASS 4 — GROUNDED REQUESTS / LANGUAGE -> GOALS

LANGUAGE PASS 4 — GROUNDED REQUESTS / LANGUAGE -> GOALS: PASS

LANGUAGE PASS 4: FROZEN

LANGUAGE PASS 4 CLOSURE: PASS

LANGUAGE PASS 4 — GROUNDED REQUESTS / LANGUAGE -> GOALS: FROZEN

- Request intent is learned contrastively from externally demonstrated desired
  structures. An arbitrary NFC token can acquire an ordinary ASSOCIATIVE link
  to one generic `COMMUNICATIVE_REQUEST` Cognit; no spelling or command is
  hard-coded and the concept contains no ActionType semantics.
- Immutable `LanguageRequestResult` records the Pass-3 result, retrieved cue
  symbols, confidence, desired structure, Goal ID, and provenance. A Goal is
  installed only when the learned cue is retrieved and all non-cue Pass-3 roles
  form a complete relational structure.
- `SyntheticEntityCore.install_relational_goal` is the shared ordinary Goal
  path. Language preserves canonical relations, directed role edges and bound
  participant Cognits with `origin="LANGUAGE_REQUEST"`; the existing
  BeliefScene/planner machinery consumes `core.target_structure`.
- Description controls create the same Pass-3 structure without a Goal.
  Ambiguous or incomplete requests create no Goal. Language never chooses an
  action and does not mutate World, EventSequence, or ActionIntent state.
- The embodied acceptance path uses real World-derived participant/relation
  Cognits, normal Pass-1 grounding, a learned nonce request cue, and a held-out
  first request. Request-label permutation and an untrained `take` control prove
  that surface spelling supplies no intent.
- Request-cue generalization is now held out: `mip` is demonstrated only with
  structure X, while independently grounded structure Y is never paired with
  `mip` until its first successful requested Goal. The same Y remains a
  description without the cue.
- Relational Goal behavior is generic: provenance is not used to select planner
  mechanics. Any active Goal whose target Cognits and `target_structure` agree
  enters target seeding, progress/action scoring, and relational subgoal
  management; this includes `LANGUAGE_REQUEST`.
- Queued request utterances persist their target structure in backward-compatible
  v7 inbox rows; old three-field rows still load. One global deterministic
  `max_new_relations_per_tick` budget spans all qualifying request cues, and a
  cue is marked materialized only after its actual ASSOCIATIVE Relation exists.
- Language identity is Unicode `str`, normalized by NFC only. Cyrillic/Latin
  confusables, case, CJK, Greek, emoji, and arrows remain exact distinct tokens;
  canonically equivalent accented forms share one symbol. Containers encode
  JSON as UTF-8 without ASCII escaping.
- Request evidence/concept identity/materialized cue bookkeeping persist in the
  existing LANG payload. Previous v0.5.6 payloads migrate with no request cues;
  schemas remain `.seworld v7` and `.sebrain v6`.
- Focused Pass-4 closure tests: **12 passed**; focused Pass-1–4: **50 passed**;
  full pytest: **315 passed**; Release build: **PASS**; CTest: **2/2**;
  `full_graph_sync_calls == 0`; `PYTHONHASHSEED=1/77`: identical.

## LANGUAGE PASS 3 — RELATIONAL COMPOSITIONAL GROUNDING

LANGUAGE PASS 3 — RELATIONAL COMPOSITIONAL GROUNDING: PASS

LANGUAGE PASS 3: FROZEN

- Immutable `LanguageRelationalResult` exposes ordered symbol IDs, bounded
  semantic slots, a real `RelationalStructure` when supported, confidence,
  unresolved positions, and Cognit provenance.
- A slot can use only a live, non-language, non-target Cognit that is both a
  materialized Pass-1 grounding target and active in that token's actual
  retrieval wave. Candidate ranking and ambiguity handling are bounded and
  deterministic; equal learned evidence remains unresolved.
- Relational meaning comes only from existing `RELATIONAL` token Cognits or
  existing `BOUND_RELATION` beliefs. Two non-relational participants are bound
  in utterance order to directed roles `(0, 1)`; no relation is invented when
  a relational anchor is absent.
- Held-out first-occurrence triples compose immediately from constituent
  meanings, and reversing participant order reverses the participant binding.
  The result is directly consumable by `BeliefScene`.
- The closure curriculum uses only real native World observations: two
  perceptually distinct objects produce memory participants and ordinary
  relational Cognits; normal Pass-1 exposures ground three nonce words. The
  first unseen triple composes immediately, and a full surface-label
  permutation preserves the learned semantics.
- `RelationalStructure.source_cognits` contains participants only. Its
  `relations` use the ordinary canonical representation, while `role_edges`
  preserve direction. Generic `BeliefScene` binding respects explicit bound
  participant IDs without changing free binding for unbound structures, so a
  correct scene scores above a role-reversed scene.
- Composition is read-only interpretation: it creates no phrase Cognit,
  ASSOCIATIVE meaning, Goal, ActionIntent, World mutation, or evidence refresh.
  Frozen Pass-2 sequence learning remains unchanged.
- Persistence remains `.seworld v7` / `.sebrain v6`; an unfinished utterance
  resumes to the identical derived relational result.
- Focused Pass-3 tests: **9 passed**; frozen Pass-1/2 plus Pass-3 tests:
  **38 passed**; full pytest: **303 passed**; Release build: **PASS**;
  CTest: **2/2**; `full_graph_sync_calls == 0`; `PYTHONHASHSEED=1/77`: identical.

v0.5.x LANGUAGE FOUNDATION: FROZEN

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
