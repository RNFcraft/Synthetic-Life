# Synthetic-Life

Synthetic-Life — экспериментальная embodied cognitive architecture на основе
динамического графа Cognits (`κ`) и Relations (`ρ`). Проект не является
LLM/Transformer-обёрткой и не использует frozen policy network как основной
обучаемый механизм: представления, Relations, память, prediction, Goals и выбор
действий изменяются во время взаимодействия с World.

## Текущий статус

**v0.7.5 — FROZEN.**

Текущая ветка v0.7 — архитектурная уборка без намеренного изменения поведения.
Полный regression/performance audit подтвердил эквивалентность v0.7.0 и
рефакторированной системы:

- `422` pytest — PASS;
- CTest Release — `2/2` PASS;
- canonical digest:
  `7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f`;
- canonical structural counters: `79` actions, `655` scheduler events,
  queue peak `3`, `27` Cognits, `162` Relations;
- `full_graph_sync_calls == 0`;
- seven canonical runs of v0.7.0 and seven runs of v0.7.5 matched exactly on
  digest and semantic/work counters;
- 1,000-WorldTime long-life audit reached the global Relation cap `16,384` and
  remained bounded while cognition, actions, neural events and Assemblies kept
  updating.

Полные доказательства: [`docs/V0_7_5_REGRESSION_AUDIT.md`](docs/V0_7_5_REGRESSION_AUDIT.md).

Следующий cleanup milestone — **v0.7.6 Architecture Freeze and Future-Proofing**.
После него запланирован **v0.8 Homeostatic Motivation and First Survival Learning**.

## Быстрый старт

Требования:

- Python 3.11+;
- C++20 toolchain;
- CMake;
- pybind11;
- на Windows — Visual Studio 2022 Build Tools / MSVC v143 + Windows SDK.

```powershell
python -m pip install -r requirements.txt
cmake -S cpp -B cpp/build -A x64
cmake --build cpp/build --config Release
python tools/verify.py --full
```

Production smoke:

```powershell
python -B -c "import main"
python -B main.py --headless --seconds 0
```

Обычный запуск:

```powershell
python main.py
python main.py --speed 10
python main.py --headless --seconds 100
python main.py --headless --seconds 100 --save run.seworld
python main.py --load run.seworld
```

`--seconds` — абсолютная цель по `WorldTime`. Wall clock и renderer FPS не
являются causal time.

## Production architecture

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

Главный causal boundary:

```text
World
  -> immutable SensoryFrame
  -> SyntheticEntityCore
  -> timestamped ActionIntent
  -> World
```

Python владеет semantic cognition: patterns, Goals, BeliefScene, memory policy,
planner semantics, perceptual continuity, language state и cognition frontier.
C++ владеет authoritative numeric Cognit/Relation substrate, native World,
scheduler и micro-neurodynamic substrate. В normal native execution нет
authoritative Python mirror numeric graph state.

Neural path однонаправленный:

```text
SensoryFrame
  -> bounded non-semantic receptors
  -> micro-neural dynamics
  -> Assemblies
  -> ordinary Cognit
  -> ordinary graph/planner context
```

Запрещён обратный Cognit -> micro feedback и прямой neural -> Action/Goal shortcut.

## Persistence

Основные форматы:

- `.sebrain v6` — durable learned cognition / native brain payload;
- `.seworld v7` — exact continuous World + scheduler/frontiers/pending episode;
- native binary graph v3 — внутренний persisted numeric graph.

Изменение формата требует явной версии и backward/migration tests. Нельзя
неявно менять positional pybind wire rows, ID domains или restore order.

## Проверка

Быстрая developer-проверка:

```powershell
python tools/verify.py
```

Полный release gate:

```powershell
python tools/verify.py --full
```

Taxonomy тестов, architecture guards, manual soak и artifact policy:
[`docs/TESTING.md`](docs/TESTING.md).

## Документация

Начинать лучше с [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md). Кратко:

- [`CURRENT_STATUS.md`](CURRENT_STATUS.md) — только актуальное состояние;
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — текущая архитектура и invariants;
- [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md) — практическая разработка;
- [`ROADMAP.md`](ROADMAP.md) — история milestones и будущие планы;
- [`docs/TESTING.md`](docs/TESTING.md) — verification contract;
- [`docs/V0_7_REFACTOR_CONTRACT.md`](docs/V0_7_REFACTOR_CONTRACT.md) —
  frozen контракт рефакторинга v0.7;
- [`docs/V0_7_5_REGRESSION_AUDIT.md`](docs/V0_7_5_REGRESSION_AUDIT.md) —
  фактический audit v0.7.5.

`V0_*_EXPERIMENT_REPORT.md`, `V0_5_3_CONTINUOUS_RUNTIME_PLAN.md`,
`DESIGN_DECISIONS.md` и `COGNITIVE_FORMALISM.md` — исторические/
фундаментальные материалы. Они не являются источником текущего status, если
расходятся с живой документацией выше.
