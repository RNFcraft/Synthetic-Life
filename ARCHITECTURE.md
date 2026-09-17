# Synthetic-Life Architecture

**Current architecture baseline: v0.7.5 FROZEN.**

Этот документ описывает фактическую текущую архитектуру. Исторический контракт
рефакторинга v0.7 находится в
[`docs/V0_7_REFACTOR_CONTRACT.md`](docs/V0_7_REFACTOR_CONTRACT.md), а результаты
доказательного аудита — в
[`docs/V0_7_5_REGRESSION_AUDIT.md`](docs/V0_7_5_REGRESSION_AUDIT.md).

## 1. Архитектурная цель

Synthetic-Life строится как embodied cognitive system с приобретаемыми
внутренними представлениями и причинными связями. Основной learned substrate —
разреженный динамический граф Cognits (`κ`) и Relations (`ρ`).

Ключевые ограничения:

- cognition не получает скрытое World state;
- acquired knowledge не кодируется reward/table lookup;
- WorldTime не зависит от wall clock или FPS;
- production numeric Cognit/Relation state имеет одного native owner;
- neural substrate не знает semantic Action/Goal labels;
- observer причинно инертен;
- persistence обязана продолжать незавершённую causal execution точно.

## 2. Production execution path

```text
main.py
  -> ContinuousRuntime
  -> Simulation(backend="native")
  -> NativeWorldFacade -> C++ WorldRuntime
  -> SyntheticEntityCore -> NativeGraphBackend -> C++ NativeBrainEngine
  -> NeurodynamicSubstrate
  -> EventScheduler
  -> NativeObserver (interactive only)
```

Discrete `Simulation.step()`, Python graph и Python World сохраняются как
reference/compatibility paths и executable oracles. Они не являются normal
production authority.

## 3. Causal boundary

Normal embodied loop:

```text
World
  -> immutable SensoryFrame
  -> SyntheticEntityCore
  -> timestamped ActionIntent
  -> World
```

`SyntheticEntityCore` не получает raw Grid/World object references, physical IDs,
collision IDs, spawn schedule или evaluator labels. Телеметрия может видеть
больше, но не участвует в принятии решений.

## 4. Authority split

### Python authority

Python владеет semantic/research state:

- `CognitPattern` и semantic pattern metadata;
- Goals/subgoals;
- `BeliefScene` и relational interpretation;
- `SpatialMemory` policy/indexing/retrieval semantics;
- perceptual continuity;
- planner sessions, work frontier и semantic scoring;
- language symbol/grounding state;
- high-level cognition orchestration;
- reference/oracle implementations и experiments.

Python может владеть числовым semantic state, но не копией authoritative native
Cognit/Relation numeric arrays.

### C++ authority

Для `backend="native"` C++ владеет:

- numeric Cognit state;
- numeric Relation state;
- sparse Relation storage/lifecycle;
- transition evidence/materialization;
- graph prediction/waves;
- continuous Cognit/Relation materialization;
- native World bodies/objects/interactions/conflicts/fairness;
- `WorldTime` и native scheduler;
- micro-neural state, STDP/homeostasis, Assemblies;
- Assembly -> Cognit bridge mapping/cursor;
- native persistence payloads.

Invariant:

```text
full_graph_sync_calls == 0
```

## 5. Python physical structure

Stable facades и extracted layers после v0.7.2:

```text
consciousness/core.py             SyntheticEntityCore composition facade
consciousness/core_learning.py    prediction/error/Relation-learning methods
consciousness/cognition_types.py  ContinuousCognitionFrontier record

consciousness/language.py         LanguageLexicon + compatibility exports
consciousness/language_types.py   frames/results/grounding context

consciousness/memory.py           SpatialMemory authority/policy
consciousness/memory_types.py     durable memory records
consciousness/memory_matching.py  pure matching transforms

consciousness/planning.py         DeliberativePlanner
consciousness/planning_types.py   Plan/work/session records

simulation/continuous.py          ContinuousRuntime orchestration facade
simulation/runtime_types.py       read-only render records
simulation/simulation.py          composition/discrete compatibility facade
```

Extracted type/data layers не должны импортировать `SyntheticEntityCore`.
Compatibility import path может re-export один и тот же class object, но не
дублировать implementation или state.

## 6. Native physical structure

После v0.7.3:

```text
cpp/src/native_brain_engine.cpp    graph/prediction/evidence/lifecycle/persistence
cpp/src/native_brain_bridge.cpp    Assembly -> Cognit delivery/bridge state
cpp/src/neurodynamic_substrate.cpp micro physics/plasticity/Assemblies/snapshot
cpp/src/neurodynamic_bridge.cpp    bounded bridge-event cursor reads
cpp/src/bindings.cpp               module composition/remaining pybind groups
cpp/src/bindings_scheduler.cpp     scheduler/event bindings
```

`NativeBrainEngine` и `NeurodynamicSubstrate` остаются стабильными facades и
единственными владельцами соответствующего state.

## 7. ID domains

Нельзя смешивать следующие пространства:

```text
Python Cognit ID      1-based
native Cognit index   0-based
RelationHandle        (page, slot, generation)
Assembly ID           native monotonic identity
scheduler event ID    native monotonic sequence
recognition episode   native monotonic identity
```

Преобразование Python Cognit ID <-> native index централизовано в native facade/
backend boundary. `id - 1` и `id + 1` вне этого boundary требуют отдельного
обоснования.

## 8. Time domains

Система использует несколько независимых шкал:

- `WorldTime`: float64 simulated causal time;
- scheduler sequence ID: tie-breaker для одинакового времени;
- cognitive/evidence tick: discrete cognition/evidence domain;
- maintenance ordinal: cadence counter;
- neural time: float64 внутри `NeurodynamicSubstrate`;
- wall clock: только pacing/measurement;
- render frame: только observer/UI.

Scheduler ordering:

```text
(time, id)
```

Одинаковый `WorldTime` не означает произвольный порядок: sequence ID входит в
causal contract.

## 9. Continuous cognition frontier

Обычная decision transaction разбита на event-driven work:

```text
SENSORY_CHANGE
  -> COGNITION_WAKE
  -> RECALL
  -> PROPAGATE
  -> IMAGINE
  -> PLAN_REFINE
  -> QUIESCENT
  -> one action commit
  -> WORLD_ACTION_COMPLETE
```

Внутри одного WorldTime может выполниться несколько cognition events.
Deliberation заканчивается, когда causally justified pending work исчерпана, а
не после фиксированного числа тиков.

`ContinuousCognitionFrontier` — persisted Python authority незавершённой
transaction. Save/load обязан сохранять frontier и pending work.

## 10. Cognit/Relation learning

Transition evidence — bounded learning scaffold, а не параллельное knowledge
store. Evidence наблюдает transitions и материализует/обновляет ordinary
Relations.

Основные relation classes включают:

- `SEQUENTIAL`;
- `SELF_ACTION`;
- `SPATIAL`;
- `ASSOCIATIVE`;
- inhibitory/other graph mechanics where defined by existing contracts.

`SELF_ACTION` support принадлежит точному `(source, action, target)` triple.
Action trial count — denominator, а не support каждого target.

Global live Relation capacity authoritative в native engine. Existing Relations
можно обновлять при cap; новый identity при cap не создаётся. Deletion снова
освобождает capacity.

## 11. Prediction and planner

Runtime prediction читает materialized Relations, а не TransitionEvidence как
скрытую вторую модель.

Planner остаётся Python semantic authority. Native backend выполняет bounded
mechanical prediction/action-effect batches. Все доступные действия проходят
через один обычный planner contract; отдельного neural planner или language
planner нет.

## 12. Language

Language subsystem receptive и grounded:

```text
external token
  -> LANGUAGE_SYMBOL Cognit identity
  -> contrastive embodied grounding
  -> ordinary Relations
  -> relational composition
  -> ordinary Goal/request path
```

Lexicon задаёт identity, но не dictionary meaning. Запрещены:

- pretrained semantic lookup;
- token -> Action mapping;
- raw World label injection;
- direct language -> Action shortcut.

Ordered/relational/request grounding сохраняется через обычный cognition graph и
planner.

## 13. Micro-neurodynamic substrate

`NeurodynamicSubstrate` — отдельный native слой ниже Cognit/Relation graph.

Он включает:

- stable micro-κ IDs;
- micro-ρ source/target/weight/delay/polarity;
- float64 neural time;
- deterministic `(time, sequence)` event queue;
- same-time delivery aggregation;
- membrane/adaptation decay;
- refractory mechanics;
- local STDP traces;
- slow local homeostatic threshold bias;
- Assembly evidence/recognition;
- snapshot/restore.

Same-time spikes оцениваются как одна transaction. Plasticity использует traces
строго до данного timestamp, поэтому spikes одного timestamp не создают
искусственную причинность друг для друга.

## 14. Assemblies and one-way bridge

Assemblies выводятся из recurrent neural evidence, а не задаются семантически.
Membership, directed temporal support, consolidation и recognition являются
native state.

Bridge:

```text
micro activity
  -> Assembly
  -> AssemblyMatch / bridge event
  -> ordinary Cognit
  -> ordinary graph/planner context
```

`NativeBrainEngine` владеет stable AssemblyID -> CognitID mapping и exactly-once
cursor. Recognition episode contribution bounded peak-increment semantics.

Запрещено:

```text
Cognit -> micro-neural mutation
Assembly -> hardcoded Action
Assembly -> semantic Goal
```

## 15. Embodied sensory transduction

При включённом sensory-neural path `SensoryFrame` кодируется bounded
retinotopic/body receptor bank.

Допустимы только raw non-semantic channels:

- relative cell position;
- occupied/boundary/self;
- bounded state/appearance channel values;
- touch;
- holding;
- resistance.

Не передаются object name/type/ID, Goal, action meaning или evaluator label.
Все receptors одного frame используют один timestamp.

## 16. World runtime

Native World отвечает за:

- bodies and objects;
- movement;
- push/grab/release/interact mechanics;
- holding and resistance;
- immutable perception;
- simultaneous conflict classification;
- deterministic fairness;
- spawning;
- causal WorldTime and EventSequence.

Python World остаётся differential oracle.

## 17. Observer

Native SDL3/OpenGL observer получает только value-owned snapshots.

```text
authoritative state
  -> immutable/latest-only snapshot
  -> observer
```

Observer не:

- двигает WorldTime;
- планирует causal events;
- изменяет cognition;
- изменяет RNG;
- мутирует World;
- участвует в persistence authority.

## 18. Persistence

Основные поверхности:

```text
.sebrain v6       durable learned cognition/native brain
.seworld v7       exact World + scheduler + episode/frontiers
native graph v3   binary authoritative numeric graph
```

`.seworld` сохраняет exact continuation, включая pending scheduler/cognition/
language/neural/bridge state. `.sebrain` предназначен для durable learned brain
и может начинать новый episodic context по соответствующему version contract.

Нельзя неявно менять:

- schema/version;
- required sections;
- positional wire rows;
- restore order;
- ID domains;
- class/type path assumptions, если они попадают в persistence.

## 19. Public, compatibility and internal surfaces

### Public / supported

- production CLI `main.py`;
- documented runtime facades;
- documented persistence entrypoints;
- public headers under `cpp/include/se`.

### Compatibility/reference

- historical Python import surfaces;
- discrete simulation;
- Python graph;
- Python World;
- frozen experiment/oracle paths.

### Internal

- extracted `*_types.py`;
- pure matching helpers;
- C++ declarations/translation units under `cpp/src`;
- backend implementation details.

Reference/compatibility code не считается dead code без доказательства отсутствия
callers, persistence role и oracle value.

## 20. Frozen architecture invariants

Architecture guards и acceptance tests защищают минимум:

- no Python authoritative numeric mirror;
- `full_graph_sync_calls == 0`;
- no neural -> Action/Goal semantics;
- no Cognit -> micro feedback;
- no language -> direct Action policy;
- observer snapshot-only causality;
- Python/native Cognit ID conversion boundary;
- deterministic scheduler `(time,id)`;
- host-batching invariance;
- exact pending-state continuation;
- stable persistence/wire contracts.

Полный verification contract:
[`docs/TESTING.md`](docs/TESTING.md).

## 21. v0.8 integration boundary

v0.8 ещё не реализован. Его planned physiology должна встраиваться без нарушения
вышеуказанных boundaries.

Зафиксированное направление:

```text
native physiology (N, E)
  -> non-semantic interoception
  -> neural/cognitive representation
  -> learned action-conditioned consequences
  -> multi-step prediction
  -> homeostatic trajectory valuation
  -> ordinary Action
```

Homeostatic tension не должна становиться semantic shortcut
`hunger -> find_food`. Подробный staged plan находится в `ROADMAP.md`.

## 22. Что считать источником истины

При расхождении документов использовать:

1. executable acceptance/oracle tests;
2. `docs/V0_7_REFACTOR_CONTRACT.md` для frozen v0.7 contracts;
3. этот документ для текущей architecture narrative;
4. `CURRENT_STATUS.md` для актуального acceptance state;
5. `ROADMAP.md` для будущих milestones;
6. historical reports только как историческое evidence.
