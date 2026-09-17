# Synthetic-Life Developer Guide

Практический guide для текущей **v0.7.6 FROZEN** architecture.

Перед архитектурными изменениями прочитайте:

- [`ARCHITECTURE.md`](ARCHITECTURE.md);
- [`docs/V0_7_REFACTOR_CONTRACT.md`](docs/V0_7_REFACTOR_CONTRACT.md);
- [`docs/TESTING.md`](docs/TESTING.md);
- [`CURRENT_STATUS.md`](CURRENT_STATUS.md).

## 1. Setup

Требуются Python 3.11+, C++20, CMake и pybind11.

Windows:

- Visual Studio 2022 Build Tools / Visual Studio 2022;
- MSVC v143;
- Windows 10/11 SDK.

```powershell
python -m pip install -r requirements.txt
cmake -S cpp -B cpp/build -A x64
cmake --build cpp/build --config Release
```

Production smoke:

```powershell
python -B -c "import main"
python -B main.py --headless --seconds 0
```

## 2. Standard verification

Fast developer gate:

```powershell
python tools/verify.py
```

Full release gate:

```powershell
python tools/verify.py --full
```

`verify.py`:

- fail-fast;
- использует текущий Python interpreter;
- не устанавливает dependencies;
- не требует network после setup;
- при необходимости конфигурирует `cpp/build`;
- запускает Release build и CTest.

Test taxonomy и manual workloads:
[`docs/TESTING.md`](docs/TESTING.md).

## 3. Production path

```text
main.py
  -> ContinuousRuntime
  -> Simulation(backend="native")
  -> NativeWorldFacade -> C++ WorldRuntime
  -> SyntheticEntityCore -> NativeGraphBackend -> C++ NativeBrainEngine
  -> NeurodynamicSubstrate
  -> EventScheduler
```

Observer — только read-only consumer snapshots.

## 4. Где менять код

### Semantic cognition

- `consciousness/core.py` — `SyntheticEntityCore` composition facade;
- `consciousness/core_learning.py` — transition/error/Relation learning;
- `consciousness/cognition_types.py` — cognition frontier record;
- `consciousness/memory.py` — `SpatialMemory` authority;
- `consciousness/memory_types.py` — durable records;
- `consciousness/memory_matching.py` — pure matching transforms;
- `consciousness/planning.py` — `DeliberativePlanner`;
- `consciousness/planning_types.py` — planner records/session/work;
- `consciousness/language.py` — `LanguageLexicon`/learning facade;
- `consciousness/language_types.py` — language frames/results/context.

### Python/native boundary

- `consciousness/backends.py`;
- `consciousness/native_graph.py`;
- `consciousness/native_engine.py`.

Здесь должны оставаться Cognit ID conversions и wire translation. Не
распространяйте `id - 1` / `id + 1` по semantic code.

### Continuous runtime

- `simulation/continuous.py` — production event orchestration;
- `simulation/runtime_types.py` — read-only render records;
- `simulation/simulation.py` — composition/discrete compatibility facade.

### Native brain

- `cpp/src/native_brain_engine.cpp` — graph/prediction/evidence/lifecycle/persistence;
- `cpp/src/native_brain_bridge.cpp` — Assembly -> Cognit bridge;
- `cpp/src/neurodynamic_substrate.cpp` — neural physics/STDP/Assemblies/snapshot;
- `cpp/src/neurodynamic_bridge.cpp` — bounded bridge-event reads.

### Bindings

- `cpp/src/bindings.cpp`;
- `cpp/src/bindings_scheduler.cpp`.

Не меняйте positional wire shape без atomic migration обоих концов.

### World

- native `WorldRuntime` — production physical authority;
- Python World — differential oracle/compatibility.

### Observer

- `cpp/src/observer.cpp` и facade header;
- только snapshot consumption, никаких causal mutation APIs.

## 5. State ownership rule

Перед новой stateful responsibility ответьте письменно:

1. кто authoritative owner;
2. кто только читает;
3. кто мутирует;
4. какой ID/time domain;
5. участвует ли state в persistence;
6. какие tests защищают continuation;
7. public это surface или internal.

Нельзя создавать два authoritative copies одного state.

Facade может orchestration/delegation, но не должен превращаться в новый
god-object.

## 6. Frozen architecture invariants

Не нарушать:

```text
Python Cognit ID      1-based
native Cognit index   0-based
RelationHandle        page/slot/generation

scheduler order       (WorldTime, event id)
full_graph_sync_calls 0
```

Также:

- no neural -> Action/Goal semantic shortcut;
- no Cognit -> micro injection;
- no language -> direct Action policy;
- no observer -> World/scheduler/cognition mutation;
- no hidden wall-clock/FPS causal dependence;
- no silent persistence schema change;
- no test weakening вместо исправления причины.

## 7. Time discipline

Не смешивайте:

- `WorldTime`;
- scheduler sequence ID;
- cognitive/evidence tick;
- maintenance ordinal;
- neural time;
- wall clock;
- render frame.

Если variable name двусмыслен, имя или комментарий должен указывать domain.

Same-time order — часть causal behavior, а не implementation detail.

## 8. Structural refactor rule

`EXTRACT != REWRITE`.

При переносе implementation сохраняйте:

- sorting/iteration order;
- RNG consumption;
- scheduler insertion order;
- float expression grouping;
- mutation order;
- exception behavior;
- return/data identity where externally observed;
- persistence/wire shape.

Сначала расширьте architecture guard на новый path, затем переносите код.

## 9. Persistence

Не редактируйте snapshot files вручную.

Accepted surfaces:

```text
.sebrain v6
.seworld v7
native graph v3
```

Изменение persistence требует:

- явного version bump или documented migration;
- backward/migration tests;
- checksum/required-section validation;
- pending-state continuation tests;
- отдельного design decision.

Save/load должен продолжать pending scheduler/frontier/language/neural/bridge
state, а не только durable brain.

## 10. Диагностика divergence

При первом mismatch сравнивайте в таком порядке:

```text
scheduler (time,id,type,payload)
WorldTime / EventSequence
World state
native Cognit state
native Relation state / handles
neural snapshot / bridge cursor
Python semantic state
planner frontier/session
```

Не «чините» divergence пересозданием derived state, если это меняет exact
continuation.

## 11. Tests по типу изменения

- language: `test_v054*`–`test_v057*` + architecture guards;
- neural physics/STDP: `test_v060*`, `test_v061*`;
- Assemblies/bridge: `test_v062*`, `test_v063*`;
- sensory/neural behavior: `test_v064*`, `test_v065*`;
- long-life/lifecycle/persistence: `test_v066*`;
- native World: v0.5.2 parity + continuous World tests;
- persistence/scheduler: pending-boundary continuation tests;
- wire/bindings: Python parity + CTest.

После targeted tests всегда выполняйте `python tools/verify.py --full` перед
freeze.

## 12. Manual long-life

```powershell
python -m experiments.v066_long_life
```

Manual soak не заменяет automated suite. Сравнивайте одинаковые
seed/config/build и отдельно записывайте WorldTime и host time.

## 13. Repository hygiene

Не коммитить generated local output:

- build trees/binaries;
- caches;
- coverage;
- temporary `.sebrain`/`.seworld`;
- local profiles.

Historical reproducibility artifacts и canonical fixtures не удаляются как
«мусор». Policy: [`docs/TESTING.md`](docs/TESTING.md).

## 14. Documentation policy

У каждого живого документа одна роль:

- `README.md` — entrypoint;
- `CURRENT_STATUS.md` — только текущий accepted state;
- `ARCHITECTURE.md` — текущая architecture;
- `DEVELOPER_GUIDE.md` — практический workflow;
- `ROADMAP.md` — milestones/future plan;
- `docs/TESTING.md` — verification;
- `docs/V0_7_REFACTOR_CONTRACT.md` — frozen v0.7 contract;
- `docs/V0_7_5_REGRESSION_AUDIT.md` — frozen audit evidence.
- `docs/V0_7_6_ARCHITECTURE_FREEZE.md` — final architecture freeze evidence.

Не копируйте длинный version history в `README` или `CURRENT_STATUS`.
Historical documents не переписываются для «актуализации»; вместо этого
помечайте их роль в [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md).

## 15. Contract for a new subsystem

До написания behavior logic явно определите: **STATE OWNER, INPUTS, OUTPUTS,
CAUSAL DIRECTION, TIME DOMAIN, ID DOMAIN, PERSISTENCE RESPONSIBILITY,
PUBLIC/INTERNAL API, BOUNDEDNESS, TEST ORACLE и ARCHITECTURE GUARDS**.

У state ровно один authoritative owner. Вторая representation допустима только
как документированный read-only snapshot/cache/reference. Dependencies должны
быть явными: не добавляйте global service registry, giant context, mutable
singleton или новый God Object. Wall clock не является simulated causal time.
State, влияющий на будущее поведение, сохраняется либо точно и детерминированно
восстанавливается с доказательством. Новый causal boundary требует regression
test; структурно обходимое isolation rule требует architecture guard.
