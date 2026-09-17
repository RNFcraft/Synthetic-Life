# Synthetic-Life

Synthetic-Life — экспериментальная embodied cognitive architecture на основе
динамического графа Cognits (`κ`) и Relations (`ρ`). Проект не является
LLM/Transformer-обёрткой и не использует frozen policy network как основной
обучаемый механизм: представления, Relations, память, prediction, Goals и выбор
действий изменяются во время взаимодействия с World.

## Текущий статус

**v0.8.0 — HOMEOSTATIC FOUNDATION — FROZEN.**

Первый этап v0.8 реализует bounded runtime physiology, deterministic WorldTime
metabolism, action costs, read-only projections и exact persistence:

- full suite: `431` passed (`422` frozen/legacy + `9` v0.8.0);
- CTest Release: `2/2` PASS;
- deterministic digest: `8dfb1595eb4bd704f7d0b8780f1e58d725f7ae6b50df47f43937efc45797580c`;
- `.seworld v8`, `.sebrain v6`, native graph v3.

Consumable objects, interoception и planner valuation остаются следующими
v0.8.x этапами. Design:
[`docs/V0_8_HOMEOSTASIS_DESIGN.md`](docs/V0_8_HOMEOSTASIS_DESIGN.md).
Frozen v0.7 evidence остаётся в
[`docs/V0_7_6_ARCHITECTURE_FREEZE.md`](docs/V0_7_6_ARCHITECTURE_FREEZE.md).

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
- `.seworld v8` — exact continuous World + physiology + scheduler/frontiers/pending episode;
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
