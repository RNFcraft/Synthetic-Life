# Synthetic-Life

Current milestone: **v0.9.3a — Homeostatic Credit Assignment & Exact Determinism Audit**
(numeric build version 0.9.3; audit status, not the long-run stability release).
See [the forensic design and evidence](docs/V0_9_3A_HOMEOSTATIC_CREDIT_AUDIT.md).
See [the fixed curriculum and reproduction command](docs/V0_9_2_SURVIVAL_LEARNING_PROOF.md).
See [scenario schema, export and runner workflows](docs/V0_9_1_REPRODUCIBLE_SCENARIOS.md).
See [the workbench contract](docs/V0_9_0_EXPERIMENTAL_WORKBENCH.md).
Historical v0.9.1 freeze acceptance: **711 pytest PASS; Release CTest 2/2 PASS**.
Historical v0.9.0 acceptance: **613 pytest PASS; Release CTest 2/2 PASS**.
v0.8.4 homeostatic learning remains the current cognitive foundation, DONE / FROZEN.
v0.9.0 changes experimental interaction/observation infrastructure, not the intelligence mechanism.
v0.8.0 = frozen physiology; v0.8.1 = consumables; v0.8.2 = interoception;
v0.8.3 = learned trajectory valuation; v0.8.4 = learned passive delays and calibration.
Interoception, valuation and delayed prediction default OFF. v0.9.0 workbench is
implemented; v0.9.1 adds normalized t=0 `.sescenario` and single-run `.semanifest`.
v0.9.2 status: **EXPERIMENT COMPLETED / PROOF NOT ESTABLISHED**. Evidence is recorded in
[the complete research report](docs/V0_9_2_RESULTS.md). v0.9.3 long-run stability remains planned.

```text
python main.py --paused
# Scenario → Finish action & pause if needed → Save
python main.py --scenario scenarios/examples/workbench_smoke.sescenario --paused
python -m experiments.scenario_runner --scenario scenarios/examples/workbench_smoke.sescenario --seconds .6
python -m experiments.scenario_runner --manifest experiments/manifests/workbench_smoke.semanifest
```

`.sescenario` = reproducible initial condition; `.seworld` = exact ongoing causal
continuation; `.sebrain` = durable cognition. Optional `--brain-in/--brain-out`
supports future experienced trials without implementing a training loop.

Historical v0.8.4 stabilization/freeze closure verified on 2026-10-01: **583 pytest passed;
CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted
suites: **156 passed**. Separate production/runtime freeze gates: **10 passed**.
Native Release/observer build, import/headless smokes and `git diff --check` passed.
That cognitive freeze remains **v0.8.4 — DONE / FROZEN**.

v0.8.4 stabilization fix / freeze closure preserves ordinary predictions,
observes passive internal bin changes through production maintenance events,
contradicts stale failed-action hypotheses and retains external context.
Its previously planned v0.8.5 survival scope is now planned v0.9.2.

Historical initial v0.8.4 verification on 2026-10-01: **549 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted suites: **122 passed**. Native Release/observer build, import/headless smokes and `git diff --check` passed.

v0.8.3 stabilization fix adds fail-closed brain internal sensor topology
compatibility. Learned knowledge transfers only with a matching encoding
contract; current body and episode state do not transfer. See
[the stabilization contract](docs/V0_8_3_HOMEOSTATIC_VALUATION.md#v083-stabilization-fix-brain-sensor-compatibility).

Synthetic-Life — экспериментальная embodied cognitive architecture на основе
динамического графа Cognits (`κ`) и Relations (`ρ`). Проект не является
LLM/Transformer-обёрткой и не использует frozen policy network как основной
обучаемый механизм: представления, Relations, память, prediction, Goals и выбор
действий изменяются во время взаимодействия с World.

## Historical v0.8.0 acceptance

**Historical v0.8.0 — HOMEOSTATIC FOUNDATION — FROZEN.**

Первый этап v0.8 реализует bounded runtime physiology, deterministic WorldTime
metabolism, action costs, read-only projections и exact persistence:

- full suite: `431` passed (`422` frozen/legacy + `9` v0.8.0);
- CTest Release: `2/2` PASS;
- deterministic digest: `8dfb1595eb4bd704f7d0b8780f1e58d725f7ae6b50df47f43937efc45797580c`;
- `.seworld v10` with interoception (historical baseline v8), `.sebrain v6`, native graph v3.

Consumables, interoception and learned valuation are implemented in v0.8.1-v0.8.4. Design:
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
python main.py --paused
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
  -> Native Workbench (immutable snapshots + explicit command queue)
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
- `.seworld v10` with interoception (historical baseline v8) — exact continuous World + physiology + scheduler/frontiers/pending episode;
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

### World configuration (v0.9.1 stabilization)

`Settings()` and default `python main.py` retain the historical **25 initial / 25 maximum objects** baseline.
For interactive editing use **Settings -> Workbench Sparse -> Apply & New World** (3 / 150), or
**Empty Experiment** (0 / 150). **Classic Baseline** restores engine defaults.
Presets edit a local draft. Applying causal settings creates a fresh world at t=0 with the chosen seed
and fresh cognition. Workbench grid, tooltips, UI scale and brain edge budget apply immediately;
these session preferences never enter artifacts or simulation inputs.
