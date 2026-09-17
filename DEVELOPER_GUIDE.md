# Developer Guide

Этот guide — практический вход в frozen v0.7 baseline. Архитектурные нормы и
точные ownership/risk tables находятся в
[`docs/V0_7_REFACTOR_CONTRACT.md`](docs/V0_7_REFACTOR_CONTRACT.md).

## Быстрый старт

Требуются Python 3.11+, C++20 toolchain, CMake и pybind11. На Windows установите
Visual Studio 2022 Build Tools с MSVC v143 и Windows SDK.

```powershell
python -m pip install -r requirements.txt
cmake -S cpp -B cpp/build -A x64
cmake --build cpp/build --config Release
python -m pytest -q
ctest --test-dir cpp/build -C Release --output-on-failure
```

Проверка production entrypoint:

```powershell
python -B -c "import main"
python -B main.py --headless --seconds 0
python main.py --headless --seconds 100 --save run.seworld
python main.py --load run.seworld
```

`--seconds` задаёт абсолютный WorldTime. Wall clock/FPS не является causal time.

## Где вносить изменения

- `simulation/continuous.py` — production event orchestration;
  `simulation/runtime_types.py` — read-only render records.
- `consciousness/core.py` — semantic composition facade;
  `core_learning.py` — transition/error/Relation learning;
  `cognition_types.py` — continuous frontier record.
- `consciousness/memory.py` — memory policy/index authority;
  `memory_types.py` и `memory_matching.py` — durable records и pure matching
  transforms.
- `consciousness/planning.py` — planner implementation; `planning_types.py` —
  Plan/work/session records.
- `consciousness/language.py` — lexicon/learning facade;
  `language_types.py` — frames, results и grounding-context episode state.
- `consciousness/backends.py`/`native_graph.py` — единственная Python/native
  граница Cognit/Relation; здесь централизуются преобразования ID.
- Native graph CRUD, prediction, evidence/materialization, lifecycle and native
  persistence: `cpp/src/native_brain_engine.cpp`; Assembly-to-Cognit bridge:
  `cpp/src/native_brain_bridge.cpp`. The class remains the stable facade/owner.
- Neural physics, plasticity/homeostasis, Assembly observation and snapshot
  validation: `cpp/src/neurodynamic_substrate.cpp`; bounded bridge-event reads:
  `cpp/src/neurodynamic_bridge.cpp`. The substrate remains the sole state owner.
- Pybind module/graph/engine/neural/world/observer wiring:
  `cpp/src/bindings.cpp`; scheduler/event wire group:
  `cpp/src/bindings_scheduler.cpp`. Observer implementation remains
  `cpp/src/observer.cpp` and read-only.
- `world/` и native World — causal physical boundary.
- `persistence/` — versioned containers; не меняйте format неявно.
- Python graph/World implementations — oracle/compatibility, не production copy.

Перед структурным изменением определите owner состояния, ID/time domain,
persistence section, API class и protecting tests по refactor contract.

Старые modules являются compatibility import surface. Новая реализация должна
иметь единственное место определения; facade только импортирует/re-export symbol.
Pure types/state modules не должны импортировать `SyntheticEntityCore`.

## Обязательный цикл проверки

Сначала запускайте ближайший test file, затем:

```powershell
python -m pytest -q tests/test_main_entrypoint.py
python -m pytest -q tests/test_v060_neurodynamic_substrate.py tests/test_v061_local_plasticity.py tests/test_v062_assemblies.py tests/test_v063_assembly_cognit_bridge.py tests/test_v064_sensory_transduction.py tests/test_v065_neural_behavior.py tests/test_v066_long_life.py
python -m pytest -q
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
```

Если имена acceptance files изменились, используйте фактический набор
`tests/test_v06*.py`, не исключая ни один milestone. Для persistence/scheduler
изменений обязательны event-boundary save/load tests; для ordering — hash-seed и
host-batching tests; для native wire — Python tests плюс CTest.

## Правила refactor

- Не смешивайте structural change с новой capability или optimization research.
- Не создавайте Python mirror native numeric state и не вводите full graph sync.
- Не меняйте 1-based Python Cognit IDs / 0-based native indices случайно.
- Не сравнивайте WorldTime, cognitive tick, event ID и wall clock как одну шкалу.
- Не меняйте positional pybind rows без атомарной миграции и тестов обоих концов.
- Не позволяйте neural code импортировать action/Goal semantics.
- Observer и diagnostics остаются read-only.
- При split расширьте source-scanning guards на новые recursive paths до переноса.
- Legacy/reference удаляется только после доказательства отсутствия callers,
  persistence и oracle value.

## Readability conventions

- Не объединяйте независимые mutations и control flow в плотную строку через
  `;`: causal порядок должен быть виден при review.
- Docstring для boundary API описывает owner состояния, ID/time domain, side
  effects и persistence role, а не повторяет имя функции.
- Неочевидный `id - 1`/`id + 1` сопровождается контекстом Python/native domain;
  ambiguous time variables должны называться или комментироваться как
  WorldTime, evidence tick, scheduler ID или neural time.
- Комментарий объясняет, почему нельзя переставлять операции. Sorting, iteration,
  RNG consumption, event insertion и float expression grouping сохраняются даже
  тогда, когда другая запись выглядит короче.

## Persistence и совместимость

Не редактируйте вручную `.sebrain`/`.seworld`. Outer container проверяет magic,
version, required sections и SHA-256; запись атомарна. Restore обязан сохранять
не только durable brain, но и pending scheduler/frontier/neural bridge episode
state. Любое изменение schema требует явной версии, backward tests и отдельного
решения — оно не входит в baseline freeze.

## Диагностика расхождений

При первом divergence сравнивайте в таком порядке: scheduler `(time,id,type,
payload)`, WorldTime/EventSequence, World state, native Cognit/Relation state,
neural snapshot/bridge cursor, semantic state, planner frontier. Не маскируйте
ошибку пересозданием derived state, если оно влияет на causal continuation.
`full_graph_sync_calls` должен оставаться нулём.

Manual long-life workload:

```powershell
python -m experiments.v066_long_life
```

Он не заменяет full suite и должен сравниваться с одинаковыми seed/config/build.
