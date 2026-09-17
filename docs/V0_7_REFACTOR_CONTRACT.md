# v0.7 Refactor Contract

Статус: **authoritative baseline для v0.7.1–v0.7.6**. Зафиксирован относительно
commit `46c53e0a1bd2c98149721a32cc6a8610cde4a217`. Если краткое описание в другом
документе расходится с этим контрактом, в ветке v0.7 действует этот документ и
исполняемый тестовый oracle.

Уточнение v0.7.2: behavioral baseline ниже не изменён. Фактическая Python
реализация физически разделяет facade и существующие responsibility layers:
`core_learning`/`cognition_types`, `language_types`,
`memory_types`/`memory_matching`, `planning_types` и `runtime_types`. Старые
modules сохраняют compatibility re-exports; authoritative state не дублируется.

Уточнение v0.7.3: behavioral baseline также не изменён. C++ member
implementations физически сгруппированы в `native_brain_bridge.cpp`,
`neurodynamic_bridge.cpp` и `bindings_scheduler.cpp`; исходные public classes
остались единственными owners. Внутренний `bindings_scheduler.hpp` не расширяет
public include surface. Python-visible symbols/wire rows, ID domains,
RelationHandle, event order, binary graph v3 и `.seworld` schema не изменены.

Уточнение v0.7.4: repository guardrails теперь исполняются через
`python tools/verify.py`; test taxonomy и artifact classes зафиксированы в
`docs/TESTING.md`. Recursive/AST guards следуют extracted Python/C++ modules и
защищают dependency/causality boundaries. Это tooling-only изменение: frozen
behavioral oracle, ABI, persistence и runtime ownership не изменены.

## 1. Scope and non-goals

v0.7.0 документирует существующую систему перед структурным refactor. Этот pass
не меняет алгоритмы, learned behavior, World, planner, language, neural semantics,
persistence format или performance. Разбиение monolith, перенос packages,
оптимизация и удаление legacy отложены. Обнаруженная ранее порча `main.py` была
pre-existing repository corruption и исправлена отдельным commit `46c53e0` до
freeze; regression `python -B main.py --headless --seconds 0` её закрывает.

## 2. Frozen baseline

Проверенный исходный HEAD: `46c53e0`. На нём: import и нулевой headless run —
PASS; `test_main_entrypoint.py` — 10 passed; объединённый acceptance v0.6.0–v0.6.6
— 96 passed; полный suite — 412 passed; Release native build — PASS; CTest Release
— 2/2. Полный suite включает hash-seed determinism, host batching и save/load
continuation. Production diagnostics сохраняет `full_graph_sync_calls == 0`.

Freeze означает поведенческий oracle, а не обещание сохранить частные имена всех
INTERNAL symbols. Любой refactor сравнивается с этим состоянием.

## 3. Production execution path

```text
main.py
  -> ContinuousRuntime
  -> Simulation(backend="native")
  -> NativeWorldFacade -> C++ WorldRuntime
  -> SyntheticEntityCore -> NativeGraphBackend -> C++ NativeBrainEngine
  -> NeurodynamicSubstrate
  -> EventScheduler
  -> NativeObserver (interactive only, read-only)
```

Scheduler проводит sensory, neural bridge, cognition wake/continue, action
completion, spawn, maintenance и language events. Discrete `Simulation.step()` и
Python graph/world остаются compatibility/reference путями, не production loop.

## 4. Subsystem inventory

| Path | Purpose / category | Authority and mutation | Consumers / API | Persistence / protection / risk |
|---|---|---|---|---|
| `main.py` | production entrypoint | orchestration only | PUBLIC CLI | `.seworld`; entrypoint tests; high |
| `config/` | production policy/config | immutable settings input | PUBLIC/COMPATIBILITY | encoded where causal; broad tests; medium |
| `consciousness/core.py` | semantic integration | Python semantic state writer | INTERNAL stable facade | brain/world snapshots; v0.1–v0.6; high |
| `memory.py`, `planning.py`, `language.py`, `relational.py` | semantic cognition | Python owners of their semantic state | INTERNAL; language entrypoints COMPATIBILITY | JSON sections; language/planner tests; high |
| `backends.py`, `native_graph.py`, `native_engine.py` | native facade | translate IDs, never mirror native authority | INTERNAL wire | `NBRN`; parity/native tests; critical |
| `graph.py`, `cognit.py`, `relation.py`, `wave.py`, `learning.py` | reference/oracle | Python reference state | TEST/ORACLE, compatibility | legacy brain schema; parity tests; high |
| `simulation/continuous.py` | production runtime | owns orchestration/frontier scheduling state | PUBLIC runtime | `.seworld v7`; continuous tests; critical |
| `simulation/simulation.py` | composition + discrete compatibility | owns semantic/world composition | COMPATIBILITY | brain/world adapters; broad suite; high |
| `world/native_world.py` | facade | native World is authority | INTERNAL facade | world state native; parity; high |
| `world/world.py` | Python World | reference authority only | TEST/ORACLE, COMPATIBILITY | Python world payload; parity; medium |
| `cpp/src/native_brain_engine.cpp` | numeric graph engine | sole production Cognit/Relation authority | INTERNAL native API | binary graph v3; native/v0.5+ tests; critical |
| `cpp/src/neurodynamic_substrate.cpp` | micro-neural engine | sole micro-κ/ρ, assembly authority | INTERNAL | neural snapshot; v0.6 tests; critical |
| `cpp/src/world.cpp`, `event_scheduler.cpp` | physical runtime/queue | native authority | INTERNAL | `.seworld`; parity/order tests; critical |
| `cpp/src/bindings.cpp` | pybind wire | conversion only | INTERNAL wire | positional ABI; entire suite; critical |
| `cpp/src/observer.cpp`, `cpp/include/se/observer.hpp` | observer | read-only derived snapshots | OBSERVER/READ-ONLY | none; observer tests; medium |
| `persistence/` | validated containers | serialization boundary | PUBLIC file API / INTERNAL schema | all formats; persistence tests; critical |
| `telemetry/` | diagnostics | samples authorities, no repair | OBSERVER/READ-ONLY | counters in runtime where causal; v0.6.6; low |
| `experiments/` | workloads | experiment orchestration | historical/manual | reports only; acceptance/soak; low |
| `ui/` | unsupported legacy/debug | must not enter production | legacy, safe_to_remove UNKNOWN | none; main source guard; medium |
| `tests/` | immutable protection layer | oracle only | test/fixture | n/a; critical during v0.7 |
| historical reports/runs | historical/generated artifact | no authority | documentation only | reproducibility evidence; low |

## 5. Authority / ownership model

Python owns meaning; C++ does not own all numbers merely because they are
numeric. Native owns production Cognit/Relation mechanics and physical runtime.
Facades may cache bounded observations, but the cache is invalidated on mutation
and is not an authority. Observer and telemetry have no mutation rights.

## 6. State ownership table

| State | Authority; writers | Readers | Persistence / lifetime |
|---|---|---|---|
| Cognit numeric 12-field state | `NativeBrainEngine`; backend native calls | facades/core/planner | `NBRN`; Cognit lifetime |
| Cognit semantic pattern/kind/novelty | Python graph/facade; core | semantic subsystems | `COGN`; Cognit lifetime |
| Relations/type/status/numeric values | native relation store/engine | proxy, planner, observer | native graph; stable handle lifetime |
| TransitionEvidence | native engine | materializer/diagnostics | native graph; bounded 512 observations |
| Goals/goal stack | Python core/state | planner/language | `BELS`/semantic snapshot; goal lifetime |
| Memory/Place meanings and indices | Python memory | core/planner/language | `SPAT`; durable brain |
| BeliefScene | Python relational layer | core/planner | `BELS`; semantic lifetime |
| Percept tracks/composite candidates | Python core | perception/planner | world/runtime snapshot; episode |
| Language lexicon/grounding | Python `LanguageLexicon` | language/core | `LANG`; durable brain |
| Planner session/frontier | Python planner/core | continuous runtime | `CONT`; current cognition transaction |
| World bodies/objects/held state | native `WorldRuntime` in production | facade/observer | `STATE`; world lifetime |
| WorldTime/EventSequence | runtime wrapper + native state kept equal | scheduler/core/observer | `STATE`/`CONT`; world lifetime |
| Scheduler queue/next ID/peak | native `EventScheduler`; runtime schedules | runtime/diagnostics | `CONT`; runtime episode |
| micro-κ/micro-ρ/neural queue | native substrate | coarse API/diagnostics | neural snapshot in `NBRN`/`CONT` |
| Assemblies/candidates/matches | native substrate | bridge/diagnostics | neural snapshot; bounded |
| Assembly→Cognit mapping/cursor | native brain engine | facade/runtime | native bridge state; graph lifetime |
| Telemetry | native/Python component that performs work | diagnostics/observer | causal counters persisted where specified |

## 7. ID domains

| Domain | Base / allocator / reuse | Conversion, persistence, sentinel |
|---|---|---|
| Python Cognit ID | 1-based, native allocator, monotonic; deleted IDs not reused | native `index + 1`; persisted semantic/native |
| native Cognit index | 0-based vector index, monotonic | Python `id - 1`; no ID sentinel at facade |
| Relation source/target | native 0-based | proxy adds 1; persisted native |
| `RelationHandle` | `(page, slot, generation)`; slot reusable | generation rejects stale handles; `UINT32_MAX` is no-slot internally |
| AssemblyID | native uint64, monotonic | mapping stores native Cognit index; persisted |
| micro-κ ID | native 0-based stable vector index | monotonic/no deletion in frozen model; persisted |
| micro-ρ identity | native 0-based record position | stable in snapshot lifetime; persisted |
| World entity/body ID | 0-based native/Python contract | bodies/entities persist; deletion rules are World-owned |
| World object ID | 1-based external contract | allocator/world-owned; persisted |
| Goal ID | Python `next_goal_id`, monotonic | persisted; `None` means absent |
| Place/memory ID | Python monotonic allocator | persisted; lifetime owned by memory |
| language symbol ID | ordinary Python Cognit ID | no separate namespace; token→Cognit persisted |
| scheduler event ID | native uint64 monotonic `next_id` | persisted; orders `(time,id)` |
| EventSequence | monotonic world action/result sequence | persisted; independent of scheduler ID |
| cognition generation/order | Python monotonic generation/tick | persisted in `CONT`; stale generation ignored |
| recognition/episode ID | native monotonic bridge/assembly event identity | persisted; silence opens a new episode |

`context_id == 0` is exposed as Python `None`; action value zero may mean an
unconditioned relation in applicable native APIs. Neural time fields may use
`-inf` as “never”. Conversions `id - 1`/`id + 1` belong at facades/bindings; their
spread elsewhere is refactor debt, not permission to change domains.

## 8. API classification

| Class | Interfaces |
|---|---|
| PUBLIC | `main.py` CLI; `ContinuousRuntime` construction/run/save/load; supported Settings; World action/frame and persistence file entrypoints |
| COMPATIBILITY | `Simulation`, discrete `step`, Python World/graph adapters, `MultiEntitySimulation`, documented historical experiment entrypoints |
| INTERNAL | `SyntheticEntityCore` integration contract; `NativeGraphBackend`; most `NativeBrainEngine`, `NeurodynamicSubstrate`, scheduler and planner internals |
| TEST/ORACLE | Python graph/cognit/relation/wave/learning implementations, fixtures and differential helpers |
| OBSERVER/READ-ONLY | `NativeObserver`, `RenderSnapshot`, diagnostics and snapshot inspection |

Callable pybind methods are not automatically PUBLIC. Language input is a
supported runtime entrypoint; lexicon internals remain INTERNAL.

## 9. Python <-> C++ wire contracts

These positional structures are fragile and require characterization before a
rewrite:

- Cognit full-state flat array repeats 12 fields: `activity`, `threshold`,
  `confidence`, `utility`, `last_activated_cognitive_tick`, `refractory_ticks`,
  `homeostatic_threshold`, `activity_trace`, `target_activity`, `age`,
  `predictive_contribution`, `low_retention_ticks`.
- Relation row: native source, target, relation type, qualifier/context, then
  strength, confidence, prediction probability, support, lift,
  last-evidence tick, status, contradiction evidence, usefulness,
  confirmations, last-used cognitive tick, then `(page,slot,generation)`.
- `RuntimeEvent` is `(float64 time, uint64 id, enum type, uint64 payload)` and is
  ordered by `(time,id)`.
- Assembly public rows carry native AssemblyID, member-ID list, temporal-edge
  list and evidence/status fields. Bridge row positions are: event sequence,
  AssemblyID, native Cognit index, confidence, event kind, born, activated,
  event time, recognition episode ID, contribution, birth-suppressed. Exact
  binding output is the ABI oracle.
- Neural snapshots are validated dictionaries of physiology, SoA node arrays,
  micro-relations, pending events, candidates, assemblies, matches, bridge log
  and telemetry. Array lengths and IDs must agree before mutation.
- World frames/events are immutable coarse values; semantic core must not receive
  raw Grid/World objects or physical/evaluator labels.

Ownership stays with the producer; Python rows are copies/views, not a second
authority. A future named-structure migration needs parity tests at both sides.

## 10. Dependency directions

Allowed flow is `World -> SensoryFrame -> semantic core -> ActionIntent -> World`.
Semantic core may call memory/planning/language and the native graph facade;
native graph owns substrate and bridge; persistence serializes through component
APIs; observer reads snapshots. Tests/experiments may depend on all layers.

Questionable but frozen couplings are core↔planner session orchestration,
`Simulation` reconstruction of multiple owners, and positional bindings. The
parallel Python/native implementations are oracle dependencies, not production
cycles. Forbidden shortcuts: neural→`ActionType`/Goal, sensor label→planner,
observer→simulation mutation, renderer clock→causality, and per-spike Python
callbacks. Current source guards find no such production dependency.

## 11. Time/event domains

| Domain | Comparable with | Not interchangeable with |
|---|---|---|
| WorldTime / scheduler timestamp | each other in continuous runtime | cognitive tick, frame, wall clock |
| scheduler sequence/event ID | tie-break at equal scheduler time | EventSequence, recognition ID |
| EventSequence | ordered world action outcomes | scheduler event count |
| cognitive tick/generation | semantic ordering/stale-work rejection | seconds |
| observation tick | Relation evidence age | maintenance ordinal, seconds |
| maintenance ordinal | maintenance cadence | Relation evidence age |
| neural float64 time | scheduler time at coarse boundary | renderer time |
| Assembly recognition order | native bridge event sequence | Cognit ID |
| render/wall clock | pacing only | every causal domain |

## 12. Same-time ordering invariants

Scheduler order is `(time, sequence/id)`. Same-frame receptors receive one
identical float64 time and are handled as a simultaneous transaction; iteration
order cannot invent temporal evidence. Same-time neural deliveries are grouped
before threshold decisions. A coarse Assembly boundary joins the global queue
and is drained exactly once. Planner frontier revisions reject stale work; one
quiescent cognition commits at most one action. Different host batching must
reach the same causal state and action sequence.

## 13. Persistence contracts

The outer container header is `>8sHHI`, magic `SEBRAIN1`/`SEWORLD1`, container
version 1. Sections are checksummed with SHA-256 and replacement is atomic.
Unknown required sections fail; optional sections may be ignored.

`.sebrain` schema is `synthetic-entity-brain`: version 6 native, version 4
reference. Sections are `COGN RELA PATT SPAT BELS LEAR LANG`, with optional
`NBRN`. Native internal graph binary magic `SEBRAIN` is version 3 with checksum.
It stores durable semantic brain plus authoritative graph, evidence, neural
state, assemblies and bridge mapping. Derived indices/proxies are rebuilt only
after validation.

`.seworld` continuous schema is `synthetic-entity-continuous-world` version 7
with `META STATE CONT NBRN`; discrete native/Python world schemas are version
2/1. `CONT` includes scheduler queue/IDs/peak, ordinals and counters, transition
history, elapsed Cognit/Relation state, dirty sets, frontier/planner state,
homeostasis and language episode/durable state. Native graph is encoded in the
native payload. Restore validates capacities, IDs, event times and cross-state
references before resuming. Restore order is metadata/settings → World/native
brain → semantic owners → runtime counters/frontier → scheduler; no pending
event may be lost or replayed. `max_cognits`, global `max_relations`, bounded
history/candidate/log limits remain hard. Durable brain knowledge is distinct
from episode/runtime queue and frontier state. No format changes are authorized
by v0.7.0.

## 14. Frozen compatibility contracts

- v0.5.2: native graph authority, no Python numeric mirror,
  `full_graph_sync_calls == 0`.
- Continuous runtime: float64 WorldTime, deterministic global event ordering,
  host-batching invariance and exact continuation.
- Native World/observer: physical authority native; observer causally inert.
- Language passes: symbols acquire identity through experience; ordered,
  relational and request grounding use ordinary cognition/Goals.
- v0.6.0: event-driven native micro-neural substrate, no per-spike callback.
- v0.6.1: local plasticity/homeostasis only; same-time transaction semantics.
- v0.6.2: evidence-derived bounded Assemblies, observational to neural physics.
- v0.6.3: one-way Assembly→ordinary Cognit bridge, no reverse feedback.
- v0.6.4: bounded non-semantic World sensory transduction, simultaneous frame.
- v0.6.5: neural-born ordinary Cognit activity enters the existing frontier,
  never maps directly to action semantics.
- v0.6.6: bounded long-life structures, global Relation cap, exact evidence
  statistics and continuation.

## 15. Neural contracts

micro-κ is not Cognit; micro-ρ is not Relation. Assemblies are recurrent evidence,
not semantic classes. Physiology/topology is innate; learned weights remain
bounded and polarity does not change. Event queue is native, ordered by time and
sequence, with no global neural tick. Bridge is native, bounded, exactly-once and
one-way. It may allocate an ordinary Cognit and apply ordinary receive/wave; it
cannot create Relations, Goals or actions. Deleting a mapped Cognit invalidates
the mapping; a later recognition may create a higher ID.

## 16. Language contracts

Tokens map to ordinary Cognits; IDs carry identity, not built-in meaning.
Grounding is learned from legitimate sensory/cognitive context, never from raw
coordinates, `ActionType`, evaluator labels or a command dictionary. Ordered
utterances and relational composition preserve order. A grounded request enters
as an ordinary Goal and remains subject to the existing planner. Language inbox,
continuations, lexicon and grounding context must resume exactly after save/load.

## 17. Observer causality

Observer and renderer consume immutable/read-only snapshots. Snapshot creation
may materialize a view but must not update evidence, freshness, scheduler,
planner, neural state or World. Rendering wall clock controls pacing only;
headless and observed runs share the same causal runtime.

## 18. Architecture invariants

1. `full_graph_sync_calls == 0`; no authoritative Python numeric mirror.
2. Native Relation identity is stable and global live count never exceeds cap.
3. WorldTime is monotonic; scheduler is deterministic; host batching is invariant.
4. Same-frame receptors are simultaneous; no Python callback per spike.
5. micro-κ/ρ remain distinct from Cognit/Relation; Assembly is evidence-derived.
6. Bridge is one-way; no Cognit→neural feedback or neural→direct action mapping.
7. No semantic sensory cheat; observer/renderer are causally inert.
8. Save/load is exact causal continuation, including pending work.
9. One cognition transaction commits at most one action.
10. Language symbols have learned identity; request→ordinary Goal.

## 19. Monolith/refactor candidates

| File (baseline LOC) | Responsibilities / natural boundary | Coupling / risk |
|---|---|---|
| `consciousness/core.py` (511) | perception, semantic integration, lifecycle, continuous frontier; extract orchestration policies | graph/planner/memory; critical |
| `memory.py` (276) | places, retrieval, decay/persistence; split storage from policy | core/persistence; high |
| `language.py` (286) | lexicon, sequence/composition, grounding; split state from passes | graph/goals; high |
| `planning.py` (232) | simulation/scoring and continuous sessions; split session engine | core/backend; high |
| `simulation/continuous.py` (257) | queue orchestration, neural boundaries, persistence; split handlers/codec | all authorities; critical |
| `simulation/simulation.py` (231) | composition, discrete compatibility, snapshots; isolate adapters | World/core; high |
| `native_brain_engine.cpp` (1456) | graph, evidence, lifecycle, time, bridge, persistence; natural service boundaries | binary/wire ABI; critical |
| `neurodynamic_substrate.cpp` (573) | event physiology, plasticity, assemblies, snapshots; isolate codecs/evidence | bridge/bindings; critical |
| `bindings.cpp` (841) | all pybind translation; bind by subsystem | every wire user; critical |
| `observer.cpp` (249) | snapshot projection/render data | World/brain read paths; medium |

LOC is an audit signal, not an instruction to split by line count. Existing tests
listed in sections 22/26 must characterize every extraction first.

## 20. Duplicated responsibilities

Python graph vs native graph and Python World vs native World are intentional
oracle duplication. Discrete vs continuous simulation is compatibility.
Python/native relation materialization and lifecycle implementations support
parity but increase drift risk. Snapshot JSON, chunk containers and native binary
serialization serve different layers. `Simulation.load` and
`ContinuousRuntime.load_world`, observer/semantic snapshot construction,
scattered ID conversions and positional tuple packing are technical debt or
migration residue. None is proven dead in this milestone.

## 21. Reference/legacy candidates

| Path/symbol | Role/callers/tests | Persistence/historical relevance | Safe to remove |
|---|---|---|---|
| Python graph/cognit/relation/wave/learning | differential oracle and reference backend | old/reference brain schema, milestone tests | NO |
| `world/world.py` | reference World/parity tests | Python world schema | NO |
| discrete `Simulation.step` | compatibility and many tests | snapshot compatibility | NO |
| `MultiEntitySimulation` | compatibility/research path | multiworld v1 | UNKNOWN |
| `ui/` pygame code | unsupported debug legacy | no production persistence | UNKNOWN |
| historical experiments/reports | reproduction evidence | milestone history | NO during v0.7 |

No suspicious path has sufficient removal proof at v0.7.0.

## 22. Test taxonomy

Unit tests cover data structures, physiology and codecs; integration tests cover
core/runtime/World/language; reference/oracle tests compare Python/native;
native parity tests cover graph/World/bindings; regression tests include restored
`main.py`; architecture-boundary tests scan forbidden imports/strings; version
acceptance tests are `test_v052_*` through `test_v066_*`; performance/soak lives
in milestone experiments and long-life diagnostics.

During v0.7 the full suite, v0.6.0–v0.6.6 acceptance, main entrypoint, persistence
boundary matrix, deterministic/hash-seed, host batching, observer causality and
native CTest form an immutable protection layer.

Current source-scanning limitations must be fixed before relevant splits:
`test_v04_world.py` scans only top-level `consciousness/*.py`;
`test_v054_language_grounding.py` only `consciousness/language.py`;
`test_v065_neural_behavior.py` checks a fixed neural source list; entrypoint
guards inspect only `main.py`. Moving a forbidden dependency could bypass them.

## 23. Performance baseline

Measured baseline: full pytest 412 passed in 40.51 s; combined v0.6 acceptance
96 passed in 19.93 s; Release CTest 2/2 in 0.05 s. The frozen v0.6.6 production
1000-second workload ended with 337 Cognits, 16,384 Relations (hard cap), 86
Assemblies, 6,666 actions, 54,356 scheduler events, peak queue 3, 25,939 planner
cycles and 312,843 FFI calls; `full_graph_sync_calls=0`. Relation checkpoints at
100…1000 s were `3563, 6434, 7006, 7714, 8298, 12351, 13862, 16384, 16384,
16384`; host windows were `12.521, 26.177, 20.555, 25.537, 25.550, 39.804,
43.938, 45.806, 47.333, 50.685` s. Bounded transition window: n=512,
average candidates before/after `46.6211/37.0508`, maxima `53/46`, average/max
pairs `1728.90625/2340`. Final Relations: SELF_ACTION 13,395; SEQUENTIAL 2,906;
SPATIAL 50; ASSOCIATIVE 33; provisional 11,348, consolidated 5,036.

Controlled recurring 1000-second checkpoints used 153, 191, 199, 226, 273 and
311 Relations, one stable Assembly→Cognit mapping `[(0,11)]`, peak queue 3.
50k soak was not run and must not be implied. These numbers are regression
anchors, not universal budgets; compare like-for-like Release workloads.

## 24. Determinism baseline

Determinism is defined as equal causal state for equal seed/config/input, across
`PYTHONHASHSEED`, host batching and save/load cuts. It includes scheduler state,
World/native graph, semantic snapshot, neural snapshot, bridge mapping/cursor,
frontier, action count and runtime counters—not wall-clock duration, render FPS or
object addresses. Exact float64/event ordering is part of the contract. The
baseline full suite passed the existing subprocess hash-seed test, host-batching
parity and event-by-event continuation matrix.

Зафиксированный 12-second seed-6607 causal SHA-256 digest при
`sensory_neural_enabled=True` и `neural_behavioral_participation=True`:
`7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f`. Он
совпал для `PYTHONHASHSEED=1` и `777`; оба запуска дали
`full_graph_sync_calls=0`.

## 25. Refactor risk register

| Risk | Failure mode | Required mitigation |
|---|---|---|
| ID conversion drift | off-by-one/cross-domain identity | centralize only with wire parity tests |
| positional ABI | silent field swap | characterize rows, migrate both ends atomically |
| authority duplication | stale Python mirror | preserve coarse calls/cache invalidation and sync counter |
| scheduler extraction | same-time reorder/replay | event trace + save-cut matrix |
| persistence reorganization | incompatible/lost pending state | golden old files and exact continuation |
| monolith split | source guard bypass | recursive/package-aware architecture guards first |
| oracle cleanup | loss of independent comparison | removal only with caller/test proof |
| observer factoring | accidental writes | causality differential tests |
| performance regression | finer FFI/per-event callbacks | retain workload counters/baselines |
| neural/language leakage | semantic shortcut | dependency scans plus behavioral ablation |

## 26. Rules for v0.7.1-v0.7.6

1. One structural boundary per change; no capability or learned-behavior change.
2. State authority, ID base, time domain, ordering and persistence semantics stay
   frozen unless a later milestone explicitly replaces this contract.
3. Add characterization before moving code; strengthen source guards before
   package splits; never weaken an acceptance oracle to make refactor pass.
4. Preserve public/compatibility APIs or provide tested adapters. INTERNAL moves
   still require wire and persistence parity.
5. No new Python numeric mirror, full graph sync, per-spike callback, reverse
   neural bridge or observer mutation.
6. Run scoped tests while editing, then full pytest, frozen acceptance, Release
   build/CTest and representative performance/determinism gates at milestone
   closure.
7. Dead-code deletion requires proven zero production/compatibility/persistence/
   historical callers; current default is `safe_to_remove = NO/UNKNOWN`.
8. Record intentional baseline deviations explicitly; unexplained deviation is a
   blocker, not cleanup.
