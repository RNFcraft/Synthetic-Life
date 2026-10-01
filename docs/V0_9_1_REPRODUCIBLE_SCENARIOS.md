# v0.9.1 — Reproducible Scenario Infrastructure

База: `0b646931d96c7043a70a6201eecaa20450999f34` на `main`.
v0.8.4 cognition остаётся DONE / FROZEN; v0.9.0 workbench реализован и
стабилизирован. Это infrastructure milestone, не survival proof.

## Motivation

Один файл с физическими начальными условиями обслуживает interactive workbench,
headless запуск и повторную реконструкцию эпизода. Организм не получает сведений
о происхождении мира из файла, имени сценария или предназначении эксперимента.

## Artifact taxonomy

| Artifact | Purpose |
| --- | --- |
| `.sescenario` | reproducible t=0 initial condition |
| `.seworld` | exact ongoing causal continuation |
| `.sebrain` | durable learned cognition |
| `.semanifest` | reproducible single-run invocation |

## Scenario schema

`simulation/scenario.py`: frozen `ScenarioDefinition`, независимая schema v1.
Используется существующий atomic/checksummed container с новым magic `SESCEN01`.
Секции строго `META`, `CONFIG`, `INITIAL`; дополнительные authority fields запрещены.

```text
META: schema=synthetic-life-scenario, version=1, name, description, tags
CONFIG: seed, settings
INITIAL:
  bodies: id, x, y, orientation, appearance
  objects: id, x, y, state, resource_channel, nutrients, hydration
  held_objects: те же поля + owner_id
  physiology: energy, nutrients, hydration
```

Canonical JSON внутри immutable definition сортирует keys; bodies/objects
сортируются по IDs, held objects — по owner/ID. Возвращаемые sections — копии.
Metadata не входит в causal checksum. Artifact SHA256 фиксирует весь файл,
включая metadata; это отдельное понятие от identity причинных условий.

## Initial-condition semantics

`ContinuousRuntime.from_scenario(definition_or_path, brain=None)` создаёт новый
runtime. WorldTime, physical event sequence, physiology clock и counters — нули;
language/editor inbox пусты; action/consequence/frontiers отсутствуют. Scheduler
свежий, с обычным initial `SENSORY_CHANGE` и будущими spawn/maintenance событиями.
Материализация не использует editor commands и не создаёт искусственную историю.

Scenario не содержит RNG continuation, scheduler, pending actions, Cognits,
Relations, learned timing, language memory или micro-neural learned state.

## Settings ownership

`scenario_configuration` и `restore_scenario_settings` живут в существующем
`simulation/persisted_settings.py`. Они переиспользуют `CAUSAL_GROUPS` и
`Physiology.CONFIG_FIELDS`, без независимого scenario field list. Сохраняются
world/runtime/cognitive/neural/resources/interoception/physiology groups целиком.
Отсутствующие fields не восполняются будущими defaults. UI preferences исключены.
Исторический `.seworld` serialized shape не менялся.

## Physiology initialization

Initial Energy/Nutrients/Hydration проверяются относительно сохранённых maxima.
Hunger/Tension вычисляет обычный Physiology owner, они не сохраняются как authority.
Physiology clock начинается с нуля. Сохранённый config и выбранные initial reserves
разделены: export использует текущие физические reserves, не constructor defaults.

## World initialization

NativeWorld получает проверенные initial records напрямую. Случайная геометрия
не строится и затем не перезаписывается. IDs сохраняются; free и held IDs уникальны.
Объект во владении поддерживается, включая resource payload. Native restore и
resource rules остаются физической authority. Free geometry не допускает overlaps.

Текущий continuous runtime использует body 0; schema v1 поддерживает contiguous
body IDs `0..entity_count-1`, до 64 тел. Object IDs `1..2^32-2` оставляют запас
для следующего native ID. Ordinary/resource capacity берётся из Settings.
World ограничен 4096 по стороне, максимум миллионом клеток; generic capacity — 10000.

Resource channel — 1/2, payload — конечные неотрицательные values до 100 с хотя бы
одним ненулевым компонентом. Текущий native restore требует `state == channel`
для resource; ordinary objects могут иметь ту же appearance без payload.
Следовательно, `appearance 1` не означает innate Food. Один resource channel
также может иметь разные физические payload. UI color/PresentationKind не сохраняются.

## RNG/seed contract

Seed обязателен: integer `0..2^63-1`. RNG создаётся из seed до future scheduling.
Сценарная геометрия не вызывает `Random.sample`. Единственный constructor draw
при разрешённом generic spawn — обычный initial spawn interval из Settings.
`object_count` остаётся сохранённым bootstrap/spawn config, но не создаёт geometry.
Смена record order или количества явно заданных records не сдвигает этот RNG stream.
Default non-scenario constructor сохраняет старый sample/spawn draw path.

## Export semantics

`export_scenario(runtime, path, seed=..., name=..., paused=True)` читает current
native physical records, reserves и Settings, нормализуя будущий receiving run
к t=0. Export не продвигает часы, не расходует RNG, не создаёт scheduler event
и не меняет cognition. Он не сохраняет ongoing causal continuation.

Fail-closed gate: paused host; нет in-flight action, pending editor/language input,
active language frontier, uncommitted cognition или pending physical consequence.
Недопустимый path/IO failure отражается в workbench notice.

Pause может оставить физическое действие в полёте. Поэтому popup предлагает
отдельное **Finish action & pause**: явное host-продвижение обычных событий до
безопасной физической границы, перед новым sensory cycle. Это НЕ часть Save.
Симуляция и видимая сцена могут измениться при Finish; последующий Save — inert.
Обычный Step по-прежнему исчерпывает следующий timestamp со всеми continuations.

## Workbench workflow

```text
python main.py --paused
# Создать/изменить physical setup.
# Scenario → при необходимости Finish action & pause → Path, Name, Seed → Save.
python main.py --scenario scenarios/examples/workbench_smoke.sescenario --paused
```

`EXPORT_SCENARIO` — host-only command с producer queue ID, без causal runtime ID.
UI не выполняет scenario filesystem IO. Host сохраняет artifact через существующий
atomic temp/fsync/replace container. Path/name остаются в локальном popup state.
Live hot-load/replacement entire runtime не реализован.

Phase A: `dialogue_error` отделён от `workbench_notice`; runtime dialogue notice
показывается около message input, editor/export notice — в Status. Toolbar немного
компактнее, inactive graph edges слабее, unavailable Active Relations — `—`.
Style/layout philosophy и fonts/dependency versions v0.9.0 сохранены.

## Headless runner

```text
python -m experiments.scenario_runner --scenario scenarios/examples/workbench_smoke.sescenario --seconds .6
python -m experiments.scenario_runner --scenario scenarios/examples/workbench_smoke.sescenario --seconds .6 --result cpp/build-verify/scenario-result.json
```

Runner и main вызывают один factory. `--scenario` и `--load` взаимоисключающие.
Explicit `--seed` с scenario отклоняется: authoritative seed берётся из artifact.
Runner допускает `--brain-in`, `--brain-out`, `--world-out`, `--result`.
Output paths не могут перезаписать inputs или совпасть между собой.

## Experiment manifest

`.semanifest`: checksummed container `SEMANF01`, independent schema v1:

```text
META: schema=synthetic-life-experiment-manifest, version=1
RUN: scenario, seconds, brain_in, brain_out, world_out, result_out
```

Неиспользуемые optional paths представлены `null`. Relative paths разрешаются
относительно manifest directory, не cwd. Unknown fields/hooks/versions запрещены.
Duration конечна, неотрицательна и ограничена миллионом секунд. CLI overrides
при `--manifest` запрещены. Это один запуск, не curriculum/batch engine.

```text
python -m experiments.scenario_runner --manifest experiments/manifests/workbench_smoke.semanifest
```

Result JSON содержит software milestone, artifact/causal checksums, optional
manifest/brain SHA256, seed/horizon, WorldTime, basic counts и final digest.
Declared/resolved paths разделены и не входят в causal digest. Result save atomic.

## Brain overlay workflow

```text
python main.py --scenario scenarios/examples/workbench_smoke.sescenario --brain learned.sebrain
python -m experiments.scenario_runner --scenario scenarios/examples/workbench_smoke.sescenario --brain-in learned.sebrain --seconds .6 --brain-out learned-next.sebrain
```

Receiving organism сначала создаётся из scenario; `.sebrain` применяется через
существующий backend/sensor compatibility preflight. Несовместимость не возвращает
частично построенный runtime. После transfer нет старого action, planner frontier
или language episode. При sensory-neural ON transducer перепривязан к receiving
native authority, а не к старому pre-transfer substrate. Knowledge representation
и brain schema не менялись; curriculum progression не автоматизирован.

## Determinism

`causal_digest` — диагностический helper текущего milestone, не forever ABI.
Он включает physical/config state, graph, physiology, RNG, scheduler, frontier
и language state; исключает metadata, UI/FPS, wall time и filesystem paths.
Две memory-map таблицы, сериализуемые как пары, сортируются по key для hashseed
независимости. Causally ordered sequences не сортируются; cognition не менялась.

Повторный `definition.instantiate()` — deterministic episode reset через fresh
reconstruction, не mutable reset большого старого runtime.

## Validation/security

Без pickle/eval/executable hooks. Проверяются checksums, strict sections/fields,
типы (bool не integer ID/seed), finite values, reserves/maxima, IDs, owners,
geometry, orientation, resource representation и capacities. Artifact максимум
8 MiB; до JSON materialization ограничены 12000 containers и depth 32, чтобы
миллион пустых records не прошёл предварительную проверку. Metadata/path UTF-8
ограничены; directories вместо file paths отклоняются. Native validation остаётся
последней physical authority. Loading создаёт новый runtime, а не мутирует старый.

## Verification

Base: `main`, HEAD `0b646931d96c7043a70a6201eecaa20450999f34`.
Final milestone: **v0.9.1**. Verification date: 2026-10-01, Windows/Release.

Executed gates:

- `python tools/verify.py --full`: Release build, entrypoint import/headless smoke,
  complete Python suite **676 PASS (44.07 seconds)** and native CTest **2/2 PASS**;
  final command result: `verification PASS (full)`.
- Six targeted suites (`test_v091_scenarios`, `test_v090_workbench`,
  `test_v084_delayed_homeostatic_learning`, `test_v083_homeostatic_valuation`,
  `test_main_entrypoint`, `test_architecture_boundaries`): 206 PASS.
  Additional six-suite run including `test_v082_interoception` instead of the
  entrypoint suite: 203 PASS. Scenario-only suite: 60 PASS.
- Observer ON Release CTest: 2/2 PASS; observer OFF isolated build CTest: 1/1 PASS.
  The OFF `.pyd` was loaded explicitly before running the actual scenario runner;
  absence of `NativeObserver` was asserted, not inferred from a build flag.
- Direct, repeated, manifest and OFF runs of the bundled scenario at 0.6 seconds
  produce the same digest:
  `3980b0777819942a37d1725c8f22d75cbdb8469a1ea4f52f2a607f05178a753a`.
  Outputs: 4 completed actions, 24 cognits, 9 relations; these are diagnostic counts,
  not survival scores.
- Real `main.py --scenario` paused and running smokes; runner world/brain/JSON
  output smoke; receiving learned-brain run through 0.6 seconds PASS. Brain overlay
  rebases spatial-memory timestamps to the receiving clock while retaining evidence
  age and confidence; historical discrete-clock brains retain their old handling.
- Native rendered captures inspected at 1100×700, 1440×900 (Scenario popup),
  1920×1080. Popup Save/cancel layout is compact; native interaction tests actually
  click Save and verify its typed host command. Queue-error ownership is tested.
- `git diff --check`: PASS. No commit/push performed.

The user's interactive defaults `object_count=3`, `max_objects=150` are preserved.
Two historical tests now explicitly request their original 25/25 fixture geometry;
this does not change runtime behavior or the frozen cognitive foundation.

Changed areas: `simulation/scenario.py`, shared runtime/bootstrap/persisted settings,
`world/native_world.py`, `main.py`, `experiments/scenario_runner.py`, container magic
registry, host workbench command/status bridge, native toolbar/dialogue/status/world
views and observer audit harness; scenario/architecture/workbench tests and two
historical geometry fixtures; README, status, roadmap, architecture, developer/testing
guides and milestone contracts. Canonical binary examples are repository-source
artifacts under `scenarios/examples/` and `experiments/manifests/`; diagnostic captures
and outputs stay in ignored build directories.

## Known limits

Нет live hot-load, scenario library/browser, automatic curriculum, multi-seed
benchmark, training loop или большой metric framework. Finish boundary не является
бесплатным teleport/reset: оно исполняет реальное pending действие. Контракт IDs
ограничен существующим body-0 runtime. Ресурсная appearance ограничена текущими
native restore rules. Actual Linux/macOS и hardware high-DPI требуют отдельной
manual проверки; synthetic font/layout gates сохранены.

## v0.9.2 boundary

First Survival-Learning Proof: controlled fresh/experienced trials, Stage 1
adjacent discovery и Stage 2 MOVE→INTERACT, ablations и multi-seed statistics.
v0.9.3 — long-run survival stability/freeze. Ни один survival superiority claim
не является результатом v0.9.1.

v0.9.1 adds reproducible experiment initial conditions, not a training algorithm.

A .sescenario is a normalized t=0 physical/configuration artifact, not an ongoing
checkpoint and not learned knowledge.

Food and Water remain human/editor labels for physical resource presets.
Scenario files preserve their physical channels/payloads; cognition receives
only ordinary sensory consequences.

No reward, food-to-action rule, curriculum success signal, survival score,
semantic resource Goal, or scenario-to-cognition shortcut was introduced.

v0.9.2 remains the first milestone allowed to claim a controlled survival-learning experiment.
