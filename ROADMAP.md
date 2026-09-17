# Synthetic-Life Roadmap

Synthetic-Life — экспериментальная embodied cognitive architecture, построенная вокруг динамического графа Cognits (`κ`) и Relations (`ρ`) и постепенно расширенная непрерывным event-driven runtime и собственным нейродинамическим субстратом.

Этот документ фиксирует развитие проекта по версиям.  
Статусы будущих этапов будут добавляться по мере планирования.

### Язык кода и документации

Новые и существенно обновляемые комментарии в коде, архитектурные пояснения и внутренняя документация проекта по возможности пишутся на русском языке. Английский сохраняется там, где он является частью программного интерфейса, имени типа/функции/протокола, внешнего формата, стандартного технического термина или где перевод ухудшает однозначность. Исторические документы не переписываются только ради смены языка.

---

## v0.1 — Initial κ/ρ Prototype

**Status: DONE**

Первая экспериментальная реализация основной идеи Synthetic-Life.

Базовое внутреннее состояние было построено вокруг:

- Cognits (`κ`);
- Relations (`ρ`);
- распространяющейся активности;
- сенсорного входа;
- выбора действий;
- взаимодействия с World.

Версия доказала техническую возможность существования динамического κ/ρ-графа, но одновременно выявила фундаментальные проблемы первоначальной архитектуры.

К 10K шагов наблюдалось примерно:

- 113 Cognits;
- 6,806 Relations;
- очень высокая плотность графа;
- длительные циклические траектории;
- слабая масштабируемость такого способа образования Relations.

Эти ограничения стали основой для полного пересмотра механизмов активности и обучения в v0.2.

---

## v0.2 — Stable Adaptive Cognition

**Status: DONE**

v0.2 превратила первый прототип в устойчивую sparse cognitive architecture.

Реализованы:

- homeostatic excitability;
- adaptive Cognit thresholds;
- refractory attenuation;
- activity traces;
- conserved propagation energy;
- sparse statistical Relation formation;
- bounded transition evidence;
- support and lift gating;
- action-conditioned evidence;
- prediction from acquired experience;
- prediction error;
- representation-independent novelty;
- internal tension;
- persistent cognitive Goals;
- internal loop detection;
- imagined action evaluation;
- deterministic persistence and continuation.

Relations больше не создавались из простой совместной активности. Для материализации требовались статистически подтверждённые зависимости.

В результате граф перестал стремиться к почти полной связности: финальные эксперименты сохраняли сотни Cognits и порядка сотни Relations даже на длительных запусках.

Также была устранена постоянная saturation активности: homeostasis и сохранение энергии волны сделали распространение bounded.

---

## v0.3 — Perception, Continuity and Composite Cognits

**Status: DONE**

v0.3 расширила κ/ρ-систему от отдельных sensory events к структурам восприятия.

Реализованы:

- symmetry-preserving action tie resolution;
- разделение prediction error и representation error;
- representation coverage;
- `LocalPercept`;
- внутренние `PersistentPercept (π)` tracks;
- кратковременная perceptual continuity;
- learned sensorimotor displacement statistics;
- sensorimotor geometry без заранее заданных пространственных преобразований;
- anchored structural patterns;
- translation-tolerant structural patterns;
- recursive Composite Cognits;
- graph-shaped Cognit patterns;
- dependency-safe retention;
- richer internal loop state;
- prediction calibration diagnostics;
- scheduled retention/deletion candidates.

PersistentPercept дал повторяющейся структуре краткоживущую внутреннюю идентичность без World object ID и абсолютных координат.

Пространственное ожидание начало строиться из приобретённых action-conditioned displacement statistics.

Повторяющиеся короткие последовательности Cognits получили возможность образовывать новые Composite Cognits и затем участвовать в том же графе, что и обычные κ.

---

## v0.4 — Embodied Agency

**Status: DONE**

v0.4 превратила World в persistent manipulation environment и связала cognition с физическими последствиями собственных действий.

Реализованы:

- persistent physical objects;
- deterministic object spawning;
- pushing;
- directional grab;
- carrying;
- release;
- directional interaction;
- non-semantic BodySense;
- directional touch;
- holding state;
- resistance;
- расширенный motor action set;
- action-conditioned `SELF_ACTION` Relations;
- provisional Relations;
- consolidated Relations;
- contradiction evidence;
- confidence adaptation;
- Relation usefulness;
- graph-native runtime prediction;
- composite predictive contribution;
- pattern selectivity;
- AgencyEstimate diagnostic.

Ключевым архитектурным изменением стало разделение:

```text
TransitionEvidence = временное доказательство
Relation ρ        = долговременное приобретённое знание
```

TransitionEvidence используется только для обучения и материализации Relations.

После создания Relation runtime prediction и imagination используют уже сам κ/ρ-граф.

Это было подтверждено тестом, где evidence очищалось после обучения, но graph prediction сохранялась; отключение Relations уничтожало этот prediction path.

---

## v0.5.1 — Memory, BeliefScene and Causal Learning Reference

**Status: DONE / FROZEN PYTHON REFERENCE**

v0.5.1 значительно расширила high-level cognition.

Реализованы:

- evidence-based persistent memory;
- Place hypotheses;
- multi-view egocentric memory;
- persistent object re-identification;
- confidence-based memory states;
- functional recall;
- `BeliefScene`;
- participant-bound Relations;
- endpoint-preserving relational memory;
- internal deliberation cycles;
- cognition без обязательного World step;
- bounded multi-step planning;
- hierarchical Goals;
- planner-generated subgoals;
- relational target structures;
- cognitive target mismatch;
- epistemic affordance information;
- multi-entity physical conflict resolution;
- persistence boundaries между durable brain и текущим episode.

После correctness pass был закрыт узкий causal-learning proof:

```text
physical action
→ action-conditioned evidence
→ materialized SELF_ACTION ρ
→ evidence removed
→ prediction survives
→ acquired Relation changes first action
```

В paired held-out experiment:

- experienced: 5/5, правильное действие первым;
- fresh: 5/5, требовалось три действия;
- causal-ρ ablation: 0/5.

v0.5.1 была заморожена как стабильный Python research reference для последующей native-миграции.

---

## v0.5.2 — Native Cognitive Engine Migration

**Status: DONE / FROZEN BASELINE**

v0.5.2 начала перенос критической численной части cognition из Python в C++.

В ходе этапа были реализованы и стабилизированы:

- native Cognit numeric state;
- native Relation storage;
- native wave propagation;
- native prediction kernels;
- native transition evidence;
- native Relation lifecycle;
- native outcomes;
- native tombstone deletion;
- lazy homeostasis;
- lazy Relation materialization;
- native graph persistence;
- authoritative native numeric ownership;
- устранение полного Python mirror;
- устранение full-graph synchronization;
- deterministic Python/native lockstep validation.

Первоначальная hybrid-реализация всё ещё содержала duplicate ownership и полную синхронизацию Python → C++, что вызывало performance collapse.

Финальная архитектура устранила этот путь:

```text
Python:
semantic cognition / orchestration

C++:
authoritative numeric cognition
```

`full_graph_sync_calls == 0` стал постоянным архитектурным invariant для следующих версий.

---

## v0.5.x — Continuous Runtime

**Status: DONE**

После native migration система была переведена от исторической tick-oriented модели к непрерывному event-driven runtime.

Были разделены разные понятия времени:

- simulated elapsed time;
- causal event ordering;
- cognitive operation ordering;
- maintenance scheduling;
- renderer timing.

Реализованы:

- monotonic float64 `WorldTime`;
- deterministic `(time, sequence)` event ordering;
- absolute-time scheduler;
- sub-second actions;
- independent action completion events;
- lazy elapsed-time Cognit state;
- lazy Relation aging;
- lazy memory aging;
- elapsed-time Goal persistence;
- scheduled maintenance;
- resumable execution frontier;
- deterministic save/load continuation.

Cognition также перестала выполняться как одна скрытая операция на каждом tick.

Основной frontier стал выглядеть как:

```text
SENSORY_CHANGE
→ COGNITION_WAKE
→ RECALL
→ PROPAGATE
→ IMAGINE
→ PLAN_REFINE
→ QUIESCENT
→ action commit
```

Внутренние cognitive events могут происходить на одном и том же `WorldTime`, сохраняя отдельный causal order.

---

## v0.5.x — Continuous Native World and Observer

**Status: DONE**

Physical World также был переведён на continuous execution.

Реализованы:

- absolute-time World events;
- scheduled World spawning;
- scheduled maintenance;
- independent sensory changes;
- independent action completion;
- отказ production runtime от обязательного `world_tick()`;
- deterministic conflict resolution;
- native C++ World runtime.

Renderer был отделён от simulation causality.

Реализован native SDL3/OpenGL observer:

```text
simulation state
→ immutable snapshot
→ observer
```

Renderer:

- не двигает WorldTime;
- не создаёт cognitive events;
- не изменяет RNG;
- не влияет на результаты simulation;
- работает независимо от headless runtime.

Wall-clock используется только для pacing интерактивного отображения.

---

## v0.5.x — Grounded Language Foundation

**Status: DONE / FROZEN**

В v0.5.x была добавлена первая языковая система Synthetic-Life.

Она построена поверх существующего κ/ρ substrate и не является отдельной языковой моделью.

### Language Pass 1 — Receptive Symbol Grounding

Реализованы:

- exact external symbols;
- `LANGUAGE_SYMBOL` Cognits;
- embodied grounding context;
- contrastive co-occurrence learning;
- обычные `ASSOCIATIVE` Relations;
- retrieval приобретённого значения через существующую graph wave.

Lexicon предоставляет только identity символа и не содержит словаря значений.

### Language Pass 2 — Ordered Utterances and Basic Composition

Реализованы:

- externally segmented multi-token utterances;
- persistent utterance frontier;
- ordered token processing;
- directional `SEQUENTIAL` evidence между language symbols;
- compositional retrieval из уже приобретённых constituent meanings.

Первое появление новой комбинации может использовать ранее изученные значения её частей.

### Language Pass 3 — Relational Compositional Grounding

Реализованы:

- `LanguageRelationalResult`;
- bounded semantic slots;
- grounded participants;
- existing relational Cognits как relational anchors;
- directed participant roles;
- создание `RelationalStructure` из приобретённых значений.

Surface word не содержит hardcoded semantic role.

### Language Pass 4 — Grounded Requests → Goals

Реализованы:

- contrastively learned request intent;
- `COMMUNICATIVE_REQUEST` Cognit;
- learned arbitrary request cue;
- language-derived relational target structure;
- установка обычного persistent Goal через существующий Goal path.

Язык не выбирает Action напрямую.

Путь:

```text
utterance
→ acquired grounding
→ relational structure
→ ordinary Goal
→ existing cognition/planner
```

---

# v0.6 — Neurodynamic Substrate

v0.6 открыла новую архитектурную линию проекта: под существующим κ/ρ cognitive graph появился отдельный event-driven neural substrate.

---

## v0.6.0 — Native Event-Driven Micro-Neurodynamic Substrate

**Status: DONE / FROZEN**

Добавлен отдельный native `NeurodynamicSubstrate`.

Реализованы:

- `micro-κ` nodes;
- `micro-ρ` edges;
- SoA native state;
- monotonic neural IDs;
- continuous float64 neural time;
- deterministic neural event queue;
- delayed propagation;
- signed excitatory/inhibitory edges;
- same-time aggregation;
- membrane potential;
- lazy leak;
- adaptation;
- refractory handling;
- exact snapshot/restore;
- neural-state validation;
- zero periodic work для silent substrate.

Важно:

```text
micro-κ ≠ Cognit
micro-ρ ≠ Relation
```

В v0.6.0 substrate намеренно был полностью изолирован от World, cognition, Goals, language и behavior.

---

## v0.6.1 — Local Plasticity and Homeostasis

**Status: DONE / FROZEN**

Добавлено локальное обучение micro-level.

Реализованы:

- plastic micro-ρ;
- immutable synaptic polarity;
- bounded mutable weight magnitude;
- pair-based STDP;
- pre/post spike traces;
- pre→post potentiation;
- post→pre depression;
- same-time spike isolation;
- local incoming/outgoing adjacency;
- slow threshold homeostasis;
- threshold bias;
- lazy trace decay;
- lazy homeostatic decay;
- persistence plastic neural state.

Same-time spikes обрабатываются одной transaction относительно traces до данного timestamp, чтобы порядок обработки не создавал ложную causal связь.

Обучение затрагивает только локально активные элементы; глобального neural sweep нет.

---

## v0.6.2 — Emergent Assemblies

**Status: DONE / FROZEN**

Добавлено автоматическое выделение устойчивых distributed assemblies из recurring micro-neural activity.

Реализованы:

- recurring activity episodes;
- bounded assembly candidates;
- evidence-derived membership;
- member participation support;
- activity-normalized specificity;
- occurrence support;
- directed temporal evidence;
- temporal identity;
- same-time unordered coactivation;
- jitter-tolerant earlier/later structure;
- distractor rejection;
- noise rejection;
- overlapping assemblies;
- novelty separation;
- consolidation;
- `AssemblyMatch`;
- partial recognition;
- bounded recent/candidate/match state;
- lazy candidate aging;
- deterministic persistence.

Assembly membership не задаётся вручную и не приходит из classifier.

Финальная temporal identity строится только между узлами, оставшимися в stable membership после normalization.

---

## v0.6.3 — Assembly → Cognit Bridge

**Status: DONE / FROZEN**

Создан первый causal bridge между micro-neural substrate и существующим κ/ρ cognitive graph.

Реализовано:

```text
Assembly consolidation
→ exactly one ordinary Cognit
```

и:

```text
Assembly recognition
→ activation of the same Cognit
```

Дополнительно реализованы:

- stable `AssemblyID → CognitID` mapping;
- monotonic bridge events;
- exactly-once delivery;
- bounded bridge log;
- per-Assembly recognition episodes;
- incremental peak-confidence contribution;
- native event timestamps;
- scheduler integration;
- normal Cognit `receive()` semantics;
- ordinary downstream κ/ρ wave propagation;
- save/load bridge frontier;
- lifecycle invalidation после удаления Cognit.

В этой версии bridge остаётся односторонним:

```text
micro
→ Assembly
→ Cognit
```

---

## v0.6.4 — Embodied Sensory Transduction

**Status: DONE / FROZEN**

Реальный `SensoryFrame` впервые был подключён непосредственно к neural substrate.

Production path:

```text
World
→ SensoryFrame
→ deterministic receptor bank
→ native batch injection
→ micro-neural dynamics
→ STDP / homeostasis
→ Assembly
→ Cognit
```

Receptor bank получает только bounded non-semantic информацию:

- retinotopic position;
- occupied;
- boundary;
- self;
- state/appearance channel values;
- touch;
- holding;
- resistance.

Через transducer не проходят:

- object IDs;
- object names/types;
- Goals;
- evaluator labels;
- action meanings;
- Assembly IDs;
- Cognit IDs.

Все receptors одного SensoryFrame получают один и тот же `WorldTime`, исключая ложную temporal structure из-за порядка iteration.

Одиночный stimulus не обязан создавать Cognit.

Повторяющийся реальный опыт способен сформировать стабильный Assembly и соответствующий Cognit.

---

## v0.6.5 — Neural Cognition → Behavior

**Status: DONE / FROZEN**

v0.6.5 впервые замкнула causal путь от реального neural experience до обычного поведения системы.

Полный production chain:

```text
World
→ SENSORY_CHANGE
→ SensoryFrame
→ receptors
→ micro-neural dynamics
→ Assembly
→ Cognit
→ ordinary cognition frontier
→ planner
→ Action
```

Experience-derived Assembly Cognits теперь могут участвовать в обычной cognition так же, как остальные Cognits.

Реализованы:

- neural Cognit contribution в `ContinuousCognitionFrontier`;
- merge neural context в текущую deliberation;
- invalidation stale planner work при новом relevant neural event;
- повторный запуск обычной цепочки:

```text
PROPAGATE
→ IMAGINE
→ PLAN_REFINE
```

- immutable already-committed Actions;
- deterministic neural/planner wake ordering;
- одинаковое поведение scheduler при разном host batching;
- save/load перед action commit;
- lifecycle cleanup;
- silent interval handling;
- research-only behavioral participation ablation.

Ablation сохраняет тот же:

- World;
- neural representation;
- Assembly/Cognit identity;
- Relation;
- Goal;

но отключает именно участие neural Cognit в cognition frontier.

Разница в prediction, action score и выбранном Action поэтому возникает через обычное context participation, а не через специальную neural policy.

В v0.6.5 всё ещё отсутствуют:

- neural planner;
- Assembly→Action lookup table;
- reward/value system;
- специальный neural Goal;
- Cognit→micro feedback.

Таким образом, v0.6.5 закрывает первый полный causal путь:

```text
physical experience
→ neural representation
→ Cognit
→ existing cognition
→ behavior
```

без отдельного neural action system.

---

## v0.6.6 — Long-Life Stabilization

**Status: DONE / FROZEN**

v0.6.6 посвящена проверке того, что накопленная к этому моменту архитектура способна стабильно существовать длительное время без нарушения причинности, разрушения persistence или неконтролируемого роста внутренних структур.

На текущем этапе реализованы и проверены:

- long-running production execution;
- deterministic replay;
- irregular host batching;
- neural numeric validation;
- micro-ρ weight bounds;
- neural event chronology;
- one-action commit invariant;
- scheduler stability;
- repeated `.seworld` save/load continuation;
- persistence neural state;
- persistence Assembly state;
- persistence cognition/planner state;
- persistence World and scheduler frontier;
- lifecycle cleanup удалённых neural Cognits;
- invalidation устаревшего `AssemblyID → CognitID` mapping;
- monotonic rebirth Cognit IDs после реального повторного recognition;
- bounded representation reuse;
- bounded Assembly candidate state;
- Relation lifecycle aging correction.

Текущий production soak достиг:

- 100 simulated seconds;
- 666 completed actions;
- 5,445 scheduler events;
- 8,512 neural events;
- 182 Cognits;
- 8,490 Relations;
- 74 consolidated Assemblies.

Три последовательных цикла save/load сохраняют causal, neural, Assembly, planner, scheduler, World и action state.

Был обнаружен и исправлен lifecycle defect: continuous Relation maintenance сравнивал evidence observation ticks с maintenance ordinal из другого временного домена. Aging Relations теперь использует соответствующий `SensoryFrame.tick`.

### Current blocker

Функциональная и causal стабильность уже подтверждается текущими тестами, однако версия пока не заморожена из-за performance drift на стандартной workload.

При последовательных 20-second simulation windows наблюдалось увеличение host execution time примерно:

```text
0.39 s
→ 1.11 s
→ 2.98 s
→ 6.57 s
→ 8.04 s
```

одновременно с ростом Relations:

```text
461
→ ...
→ 8,490
```

Рост остаётся внутри существующих graph limits, но показывает существенное структурное замедление.

Поэтому текущий freeze gate v0.6.6:

```text
long-life correctness        PASS
deterministic continuation   PASS
persistence                  PASS
lifecycle integrity          PASS
bounded representation       PASS

default-workload performance NOT YET CLOSED
```

Расширенный `50,000 simulated seconds / 10,000 actions` soak пока не является закрытым acceptance gate.

После устранения performance blocker и финальной endurance-проверки v0.6.6 должна быть переведена из `IN PROGRESS / PROVISIONAL` в `DONE / FROZEN`.

---

# v0.7 — Architecture Stabilization and Repository Refactor

**Status: PLANNED**

v0.7 не является этапом добавления новой интеллектуальной способности. Это отдельная инженерная ветка между исследовательскими этапами, предназначенная для приведения накопившейся архитектуры к состоянию, в котором её можно безопасно развивать дальше.

К началу v0.7 в репозитории одновременно существуют несколько исторических слоёв:

```text
historical / reference implementation
+
Python semantic cognition
+
native C++ authoritative runtime
+
v0.6 neurodynamic substrate
```

Само это разделение является допустимым и во многих местах намеренным, но его границы недостаточно очевидны из текущей структуры файлов. Основная цель v0.7 — сделать ownership, responsibility, production/reference/legacy status и архитектурные invariants видимыми непосредственно из структуры проекта и документации.

Главное ограничение ветки:

> Если изменение делает Synthetic-Life функционально способнее, намеренно меняет learned behavior, вводит новый cognitive mechanism, меняет World model, расширяет language capabilities или добавляет neural capability, оно не относится к v0.7.

В пределах v0.7 разрешены только изменения структуры, читаемости, документации, tooling, тестовой организации, repository hygiene и доказанное удаление dead code при сохранении существующей семантики.

Дополнительное правило для всей ветки: новые и существенно обновляемые комментарии в Python/C++ и внутренняя документация должны по возможности объяснять архитектуру на русском языке. Английский остаётся для имён API, типов, протоколов, внешних форматов и общепринятых терминов, где перевод ухудшает точность.

---

## v0.7.0 — Baseline and Full Audit Freeze

**Status: FROZEN.** Baseline commit `46c53e0` was validated before documentation:
production smoke, full 412-test suite, combined v0.6 acceptance, Release build
and CTest all pass. The previous corrupted-entrypoint blocker is closed.

The authoritative audit output is
[`docs/V0_7_REFACTOR_CONTRACT.md`](docs/V0_7_REFACTOR_CONTRACT.md), with developer
workflow in [`DEVELOPER_GUIDE.md`](DEVELOPER_GUIDE.md). It freezes production
path, subsystem/authority/ID/API/wire/time/persistence maps, compatibility and
architecture invariants, monolith/duplication/legacy inventories, test taxonomy,
performance/determinism baselines and the risk/rules for v0.7.1–v0.7.6. No
runtime behavior or persistence format was changed.

Цель — зафиксировать исходное состояние перед любым крупным структурным refactor.

Необходимо:

- классифицировать каждый subsystem и существенный файл как `production`, `semantic`, `native authority`, `facade`, `reference/oracle`, `legacy`, `historical`, `fixture` или `generated artifact`;
- зафиксировать Python ↔ C++ ownership boundary;
- описать ID domains и преобразования между Python и native слоями;
- определить public, compatibility и internal APIs;
- зафиксировать persistence contracts `.sebrain` и `.seworld`;
- зафиксировать event-ordering, same-time и continuous-time invariants;
- зафиксировать frozen v0.5.2 compatibility contracts;
- зафиксировать v0.5.x language contracts;
- зафиксировать v0.6.x neural contracts;
- снять performance baselines;
- сохранить deterministic/hash-seed baselines;
- сохранить существующие full-suite acceptance results;
- составить карту dependency directions;
- составить список monoliths, duplicated responsibilities, legacy paths и потенциального dead code.

На этом этапе не выполняется архитектурное перемещение логики. Его результат — документированный refactor contract, относительно которого проверяются все последующие этапы.

---

## v0.7.1 — Readability and Documentation Foundation

**Status: FROZEN READABILITY BASELINE.** Dense boundary declarations and
initialization paths were expanded in place; ownership, ID/time, causal ordering,
one-way bridge and positional pybind contracts are documented next to the code.
No responsibility/package movement, API/ABI, algorithm, numeric or persistence
change was made. Frozen digest, full regression and native gates pass.

Цель — сделать существующий код читаемым до его физического перемещения.

Основные задачи:

- нормализовать форматирование Python и C++;
- убрать чрезмерно плотные однострочные конструкции там, где это не меняет порядок вычислений;
- улучшить naming локальных переменных и внутренних helper-функций без изменения public API;
- добавить type hints там, где они не меняют runtime semantics;
- добавить docstrings;
- добавить комментарии к сложным причинным, временным и ownership invariants;
- в новых комментариях объяснять прежде всего причину ограничения, а не очевидное действие строки;
- комментарии и внутренняя документация преимущественно пишутся на русском;
- сохранить английские имена symbols/API и стандартные технические термины там, где это необходимо для точности;
- не выполнять алгоритмическое «упрощение» одновременно с readability cleanup.

Документация должна быть разведена по ролям:

```text
README              — короткий вход в проект
ARCHITECTURE         — актуальная архитектура
DEVELOPER GUIDE      — структура кода, ownership и правила разработки
CURRENT STATUS       — текущий acceptance state
ROADMAP              — история и будущие этапы
docs/history         — исторические планы и решения
experiment reports   — неизменяемые научные артефакты
```

Исторические experiment reports не переписываются под текущую архитектуру и не переводятся только ради единообразия.

---

## v0.7.2 — Python Structural Refactor

**Status: FROZEN.** Existing responsibilities were extracted into explicit
Python data/state, matching and core-learning modules. Stable facades and old
import paths remain; no algorithm, scheduler, persistence, native ABI or C++
structural change was made. Full behavioral/determinism gates pass. v0.7.3
remains PLANNED.

Цель — декомпозировать крупные Python-файлы по существующим responsibilities без изменения cognitive behavior.

Основные кандидаты:

- `consciousness/core.py`;
- `consciousness/memory.py`;
- `consciousness/language.py`;
- `consciousness/planning.py`;
- `simulation/continuous.py`;
- `simulation/simulation.py`.

`SyntheticEntityCore` может остаться верхнеуровневым facade, но внутренние responsibilities должны стать отдельными компонентами.

Предпочтительное направление разделения:

```text
SyntheticEntityCore
├── perception
├── cognition
├── memory
├── learning
├── planning
├── language
└── lifecycle
```

Для language subsystem должны быть физически различимы уже существующие области ответственности: frames, grounding, lexicon, sequence learning, composition, relational composition, requests и persistence.

Для memory subsystem должны быть различимы Place memory, structure memory, indexes, matching/re-identification, recall и graph materialization.

Критическое правило: `extract != rewrite algorithm`.

В частности нельзя потерять:

- incremental memory indexes;
- conservative candidate admission;
- deterministic iteration/order contracts;
- existing continuous frontier ordering;
- frozen reference paths;
- zero full-graph synchronization.

Python reference/oracle code должен быть явно отделён от production semantic runtime, но сохраняться до тех пор, пока он участвует в differential/regression validation.

---

## v0.7.3 — C++ Structural Refactor

**Status: DONE / FROZEN**

Completed as an extraction-only pass: Assembly/Cognit bridge ownership,
bounded neural bridge-event access, and scheduler/event binding registration
were moved to responsibility-named translation units. Stable facades, wire
shape, persistence and the deterministic oracle are unchanged. v0.7.4 remains
PLANNED.

Цель — разгрузить крупные native translation units без изменения внешнего поведения и numeric semantics.

Основные кандидаты:

- `cpp/src/native_brain_engine.cpp`;
- `cpp/src/neurodynamic_substrate.cpp`;
- `cpp/src/bindings.cpp`;
- внутренности observer implementation.

`NativeBrainEngine` должен сохраняться как стабильный внешний facade, но graph CRUD, prediction, evidence/materialization, lifecycle, persistence, neural bridge и publication могут быть физически разделены на внутренние компоненты.

`NeurodynamicSubstrate` также сохраняет внешний API, но реализация может быть разнесена на существующие responsibility domains:

```text
micro-neural physics
plasticity / homeostasis
assembly observation
recognition / bridge event production
snapshot / restore / validation
telemetry
```

`bindings.cpp` необходимо разнести по функциональным binding groups, не меняя Python-visible API без отдельной compatibility необходимости.

Python ↔ C++ wire-format должен быть явно документирован. Использование tuple/array positions и преобразований ID не должно оставаться неявным знанием разработчика.

Запрещено одновременно с физической декомпозицией менять:

- numeric equations;
- порядок float operations без доказанной эквивалентности;
- event ordering;
- ID allocation;
- Relation handle generation semantics;
- persistence representation;
- bridge semantics;
- observer causality.

---

## v0.7.4 — Repository, Tests and Developer Tooling

**Status: DONE / FROZEN**

Test taxonomy, recursive architecture/dependency guards, repository artifact
policy and a portable fast/full verification command are now authoritative.
Historical acceptance and research artifacts remain in place; runtime behavior,
ABI and persistence are unchanged. v0.7.5 remains PLANNED.

Цель — организовать repository так, чтобы новый технический долг не накапливался снова автоматически.

Необходимо классифицировать tests по назначению:

```text
unit
integration
reference/oracle
native parity
regression
architecture boundary
version acceptance
performance / soak
```

Существующие versioned tests сначала сохраняются как immutable refactor protection layer. Их массовый stylistic rewrite допускается только после доказанной parity новой структуры.

Source-scanning architecture guards должны стать recursive и следовать новой package structure. Простое перемещение запрещённого dependency в подпапку не должно обходить anti-cheat или semantic-boundary tests.

Repository artifacts необходимо разделить на:

```text
source code
canonical fixtures
historical reproducibility artifacts
generated local artifacts
profiling output
```

Исторические benchmark/result artifacts не удаляются только ради чистоты репозитория, если они являются источником воспроизводимости экспериментальных отчётов.

Developer tooling должен включать единый воспроизводимый verification workflow для Python и C++. Предпочтительно иметь один верхнеуровневый developer command/script, запускающий необходимые format/static/build/test checks.

Также вводятся правила против повторного образования AI-generated monoliths:

- новый код обязан иметь очевидный subsystem owner;
- крупный facade не должен получать новую unrelated responsibility без архитектурного обоснования;
- dependency direction должен быть документирован;
- public/internal API должны различаться;
- сложный causal invariant должен иметь комментарий и regression test;
- изменение architecture boundary должно обновлять соответствующую документацию;
- generated artifacts не должны случайно попадать в source tree.

---

## v0.7.5 — Full Regression and Performance Audit

**Status: PLANNED**

Цель — повторить аудит после рефакторинга и доказать, что уборка не изменила Synthetic-Life.

Проверяются:

- полный pytest suite;
- CTest Release;
- frozen Python/native compatibility oracles;
- `full_graph_sync_calls == 0`;
- deterministic `PYTHONHASHSEED` digests;
- continuous scheduler ordering;
- same-time semantics;
- save/load continuation;
- `.sebrain` и `.seworld` compatibility/migration;
- World differential behavior;
- observer causal inertness;
- language passes;
- v0.6 neural substrate invariants;
- Assembly/Cognit bridge;
- embodied sensory transduction;
- neural cognition → behavior;
- v0.6.6 long-life/lifecycle suites;
- anti-semantic and anti-cheat architecture guards;
- baseline performance до и после refactor.

Любая разница должна быть классифицирована как:

```text
expected non-semantic structural difference
bug in refactor
pre-existing bug exposed by audit
measurement/tooling difference
```

Намеренное изменение поведения ради «улучшения» в этом этапе запрещено.

---

## v0.7.6 — Architecture Freeze and Future-Proofing

**Status: PLANNED**

Финальный этап генеральной уборки.

После повторного аудита необходимо:

- удалить только доказанный dead code;
- удалить или архивировать действительно ненужные compatibility adapters;
- окончательно маркировать legacy/reference subsystems;
- проверить отсутствие циклических и запрещённых dependencies;
- проверить соответствие документации реальной структуре кода;
- проверить clean clone → dependencies → Release build → CTest → pytest → production run;
- проверить public/internal API boundaries;
- проверить persistence contracts;
- проверить структуру historical documentation и research artifacts;
- зафиксировать правила добавления новых subsystem в будущих версиях;
- зафиксировать архитектурные guardrails в automated checks там, где это возможно.

Финальный критерий v0.7:

> Разработчик, который раньше не видел Synthetic-Life, должен иметь возможность открыть репозиторий, понять назначение проекта, пройти от README к актуальной архитектуре, определить владельца нужного state, найти соответствующую реализацию, собрать проект, запустить проверки и безопасно начать изменение системы без необходимости восстанавливать архитектуру по истории коммитов, старым experiment reports или внешним чатам.

Закрытие v0.7 означает, что функционально это всё ещё тот же Synthetic-Life, который был заморожен перед refactor, но его кодовая база стала читаемой, модульной, документированной и защищённой от повторного накопления хаотичного технического долга.

---

# v0.8 — Homeostatic Motivation and First Survival Learning

**Status: PLANNED**

v0.8 открывает первую ветку, в которой у Synthetic-Life появляется собственное непрерывное физиологическое состояние и впервые возникает внутренний критерий функциональной полезности последствий поведения.

Центральный исследовательский вопрос:

> Сможет ли Synthetic-Life самостоятельно обнаружить, что определённый внешний объект и последовательность действий уменьшают его внутренний физиологический дисбаланс, затем сохранить это как приобретённое causal knowledge и использовать его в multi-step prediction для более эффективного поведения?

Ключевой запрет всей ветки:

```text
НЕ:
food -> reward
hunger -> find_food
food detector -> Goal
edible object -> fixed action bonus
consume -> reward += constant

А:
physiology defines desirable state
+
experience learns consequences
+
planner evaluates predicted trajectories
```

Врожденной является только физиология, её допустимые ranges и функция оценки внутреннего дисбаланса. Какой объект помогает, какое действие нужно совершить и какая последовательность к нему приводит, организм должен приобрести из опыта.

Базовая causal architecture:

```text
                 NATIVE PHYSIOLOGY
                 ┌──────────────┐
Food ─consume──→ │ N            │
                 │ E            │
                 └──────┬───────┘
                        │
           ┌────────────┴─────────────┐
           │                          │
           ▼                          ▼
   interoceptive receptors      derived T(N,E)
           │                          │
           ▼                          │
        neural                       │
           │                          │
           ▼                          │
        Cognits                       │
           │                          │
           ├──── learned κ/ρ ─────────┤
           │      prediction          │
           ▼                          ▼
              multi-step planner
                       │
              predicted trajectory
                       │
                       ▼
               discounted T integral
                       │
                       ▼
                    Action
```

Главная архитектурная формула ветки:

> Physiology определяет, какие внутренние состояния устойчивы; experience учит причинные пути между состояниями; planner выбирает действие через предсказанную траекторию, а не через врождённое знание о пище.

### Authority и representation contract

Authoritative physiology должна жить в native/runtime physical state, рядом с causal World/entity state, а не в Python semantic mirror.

Минимальная authority:

```text
N — nutrient / stomach reserve
E — available energy
```

`H` и `T` являются derived values:

```text
H = f(N)
T = f(N, E, target ranges)
```

Они не должны иметь второй authoritative copy и не обязаны сохраняться отдельно, если exact restore однозначно восстанавливает их из `N`, `E` и configuration.

`T` НЕ является:

- Cognit;
- Goal;
- BeliefScene entity;
- reward variable;
- action policy.

Она принадлежит отдельному read-only по отношению к поведению `HomeostaticEvaluator`, который может только оценить фактический или imagined physiological state. Он не выбирает Action и не знает семантику пищи.

При этом организм чувствует physiology через другой путь — non-semantic interoception. Таким образом, существуют два принципиально разных канала:

```text
physiology
├── interoceptive receptors -> neural -> Cognits -> learned prediction
└── HomeostaticEvaluator -> scalar evaluation of predicted physiology
```

Первый канал является опытом организма. Второй — врождённой функцией устойчивости организма. Их нельзя объединять в shortcut `hunger -> action`.

### Planner valuation contract

Planner не должен оптимизировать только immediate `ΔT`, потому что это создаёт близорукое поведение.

Основная objective v0.8:

```text
J = Σ γ^k * Δt_k * T_k
    + γ^n * τ_terminal * T_terminal
```

где planner предпочитает меньший `J`.

Это bounded discounted integral homeostatic tension по imagined trajectory. Каждый переход учитывает собственную causal duration.

Такой objective делает значимыми:

- время, проведённое в дефиците;
- длительность пути;
- лишние действия;
- metabolic cost движения;
- отложенное восстановление energy;
- terminal state при ограниченном planning horizon.

На первом проходе используется существующий bounded multi-step planner. Не вводится infinite-horizon RL, TD-learning или отдельный value network.

---

## v0.8.0 — Metabolic and Homeostatic Substrate

**Status: PLANNED**

Цель — добавить минимальную deterministic physiology, существующую только в causal simulation time.

Authoritative variables:

```text
0 <= N <= N_max
0 <= E <= E_max
```

Предпочтительная модель:

- successful consumption сразу увеличивает `N`;
- digestion постепенно переводит `N` в `E`;
- базовый body metabolism расходует `E` по `WorldTime`;
- базовый brain metabolism расходует `E` по `WorldTime`;
- movement имеет дополнительный deterministic cost;
- physical interaction имеет небольшой deterministic cost;
- расход не зависит от FPS, wall-clock, Python call count, FFI call count или host execution time.

Например физиологический deficit может быть bounded:

```text
dE = clamp((E_target - E) / E_target, 0, 1)
dN = clamp((N_target - N) / N_target, 0, 1)

T = wE * dE^2 + wN * dN^2
```

Точная функция и параметры выбираются экспериментально до freeze, но обязательны свойства:

```text
0 <= T <= T_max
finite(T)
monotonic worsening under growing deficit
no singularity at E = 0 or N = 0
```

### Energy exhaustion / brownout semantics

В v0.8 смерть ещё не вводится. Поэтому `E = 0` означает metabolic brownout, а не отрицательную energy и не смерть.

Если voluntary Action требует больше energy, чем доступно, Action физически не может начаться.

Пример:

```text
MOVE cost = C_move
E < C_move
→ MOVE cannot start
```

То же относится к дорогим motor/interaction actions.

При этом сохраняются passive процессы:

- passage of WorldTime;
- digestion;
- sensory input;
- scheduler processing;
- минимально необходимая cognition;
- WAIT / inactivity semantics.

Если `N > 0`, digestion может восстановить `E` после brownout.

Недопустимы:

- negative `E`;
- negative `N`;
- NaN/Inf physiology;
- бесконечный `T`;
- продолжение любых действий при отсутствии требуемой energy.

### Brain metabolism

Первый implementation layer должен быть консервативным:

```text
brain_cost = basal_brain_rate * ΔWorldTime
```

Activity-dependent neural cost НЕ является обязательным для первого acceptance и не должен мешать доказательству основной food-learning цепочки.

Если он добавляется позже в этой ветке, единственный допустимый initial signal — deterministic simulated micro-neural activity, предпочтительно emitted micro-spike count:

```text
ΔE_neural = C_spike * emitted_micro_spike_count
```

Этот расход должен быть bounded на causal interval и оставаться малой долей общей metabolism.

Запрещено считать brain cost из:

- FFI calls;
- planner cycles как host operations;
- CPU time;
- C++ function calls;
- renderer work;
- wall-clock milliseconds.

Идея «думать тоже стоит энергии» остаётся допустимым исследованием, но только после того, как базовый homeostatic learning работает без activity-cost domination.

Persistence должна сохранять exact physiological continuation.

---

## v0.8.1 — Consumable World Objects and External Food Spawn

**Status: PLANNED**

Цель — добавить простейший физический источник nutrient reserve.

Первый consumable object остаётся обычным кубиком World, но получает физическое свойство nutrient content. Это свойство принадлежит World physics и не передаётся cognition как слова `food`, `edible`, `nutrition`, `reward` или evaluator label.

Физический путь:

```text
visible/touchable cube
→ ordinary movement / interaction
→ successful consume event
→ cube disappears or becomes consumed
→ N rises immediately
→ digestion later converts N into E
```

Immediate изменение `N` намеренно создаёт наблюдаемый причинный физиологический consequence самого consumption, тогда как energy restoration остаётся отложенной. Это не reward shortcut: `N` является частью физического организма и также участвует в homeostatic state.

Для интерактивного curriculum observer/editor должен позволять создавать consumable cube нажатием на клетку, но UI не мутирует World или physiology напрямую.

Допустимый путь:

```text
mouse click / experiment command
→ explicit external World command
→ EventScheduler
→ deterministic FOOD_SPAWN / object-spawn event
→ native World mutation
→ ordinary sensory consequence
```

Spawn должен иметь causal timestamp/sequence и участвовать в deterministic replay/save-load semantics.

---

## v0.8.2 — Non-Semantic Interoception

**Status: PLANNED**

Цель — дать организму возможность чувствовать собственную physiology без загрузки готового значения этих ощущений.

Минимальные bounded channels могут отражать:

- energy level;
- nutrient reserve;
- hunger/deficit magnitude;
- coarse homeostatic deviation при необходимости.

Но через sensory boundary никогда не передаются semantic labels:

```text
I_AM_HUNGRY
FOOD_NEEDED
LOW_ENERGY_MEANS_FIND_FOOD
THIS_OBJECT_RESTORES_ENERGY
```

Предпочтительный production path:

```text
native physiology
→ bounded non-semantic interoceptive receptors
→ neural substrate
→ Assembly
→ ordinary Cognit
```

Interoception следует тем же принципам, что v0.6.4 sensory transduction:

- stable receptor identity;
- bounded topology;
- same-time deterministic injection;
- no object IDs;
- no Action semantics;
- no direct Goal creation;
- no direct planner score injection.

Interoceptive Cognits являются ordinary learned representations и могут участвовать в context, memory, TransitionEvidence, Relations и prediction так же, как другие experience-derived Cognits.

---

## v0.8.3 — Homeostatic Motivation and Planner Valuation

**Status: PLANNED**

Цель — сделать физиологическую устойчивость общей мотивационной функцией, не превращая её в hardcoded policy.

`HomeostaticEvaluator` получает только physiological state или predicted physiological state и возвращает bounded `T`.

Он НЕ должен:

- видеть object type `FOOD`;
- выбирать Action;
- создавать Goal на конкретный object;
- искать еду;
- читать coordinates;
- назначать reward;
- изменять learned graph.

Planner получает homeostatic contribution только после того, как существующий prediction/imagination path построил predicted internal state.

Правильный шов:

```text
Action candidate
→ ordinary learned prediction
→ predicted interoceptive / physiological consequence
→ HomeostaticEvaluator(predicted state)
→ T_k
→ trajectory objective J
→ ordinary planner comparison
```

Неправильный шов:

```text
hunger
→ special HOMEOSTATIC Goal pointing to food
→ hardcoded action
```

В v0.8 homeostatic drive не моделируется как специальный `HOMEOSTATIC Goal`, если для этого требуется встроенное знание способа удовлетворения потребности. Existing Goals могут продолжать существовать для других задач, но physiology предоставляет общий valuation layer для imagined consequences.

Основная planner objective:

```text
J = Σ γ^k * Δt_k * T_k
    + γ^n * τ_terminal * T_terminal
```

Planner предпочитает меньший expected `J` среди доступных predicted trajectories.

---

## v0.8.4 — Learned Homeostatic Consequences

**Status: PLANNED**

Цель — связать существующее causal learning с внутренними physiological outcomes без отдельной HomeostaticMemory и без нового reward-learning subsystem.

Долгосрочное знание должно жить в обычном κ/ρ graph.

Interoceptive experience создаёт ordinary Cognits, поэтому learning path имеет вид:

```text
external context Cognits
+
interoceptive Cognits
+
Action
→ TransitionEvidence
→ ordinary action-conditioned Relations / SELF_ACTION evidence
→ later external and interoceptive Cognits
```

Например после реального опыта система может приобрести knowledge вида:

```text
visual/context A
+ low-reserve interoceptive representation
+ INTERACT
→ high-reserve interoceptive representation
```

Но сама Relation не содержит label `good`, `food` или числовой reward. Её значение для поведения возникает только тогда, когда prediction приводит к physiological state с меньшим `T`.

### Persistence of physiological knowledge

Долговременная память о последствиях не создаётся отдельным `food_value` или `HomeostaticMemory` store.

После materialization learned causal knowledge является обычными Relations и сохраняется тем же durable brain persistence, что и остальные приобретённые Relations.

Episode memory при необходимости может помогать recall/context, но не является единственным authoritative carrier значения пищи.

### Delayed consequence / multi-step credit contract

v0.8 НЕ вводит temporal-difference reward backpropagation.

Отдалённая полезность раннего действия появляется через уже существующую model-based multi-step imagination.

Опыт отдельно учит переходы:

```text
State A + MOVE_RIGHT
→ State B

State B + INTERACT
→ N rises
```

Затем planner способен imagined trajectory:

```text
A
↓ MOVE_RIGHT
B
↓ INTERACT
N ↑
↓ digestion
E ↑
T ↓
```

и оценивает всю траекторию через discounted integral `J`.

Таким образом, первому MOVE не присваивается искусственный delayed reward. Оно становится предпочтительным, если learned transition model показывает, что через него достижимо последующее состояние с меньшей homeostatic cost.

Первоначальный bounded horizon должен быть достаточен для Stage 2 curriculum. Если текущий planner не способен связать даже короткую двух- или трёхшаговую цепочку без нового RL subsystem, это фиксируется как architecture blocker, а не маскируется immediate reward hack.

### Required ablations

Нужны разные ablation, потому что они доказывают разные звенья causal chain.

#### Primary — homeostatic consequence knowledge ablation

Сохраняются:

- World knowledge;
- perception;
- memory;
- ordinary non-homeostatic Relations;
- interoception;
- physiology;
- HomeostaticEvaluator;
- planner.

Отключается только использование learned action-conditioned prediction, которое ведёт к interoceptive/physiological outcomes.

То есть organism по-прежнему может знать геометрию и внешний мир, но перестаёт знать, какие действия приводят к улучшению внутреннего состояния.

Это главный causal proof v0.8.

#### Secondary — motivation ablation

Learned prediction полностью сохраняется, включая knowledge:

```text
INTERACT/context → N rises
```

но homeostatic valuation выключается:

```text
homeostatic planner weight = 0
```

Это проверяет, что одно знание consequence без intrinsic physiological valuation не объясняет acquired preference.

#### Diagnostic — broad prediction ablation

Дополнительно допустимо отключить весь learned prediction path, но это слишком широкая ablation и не является главным доказательством homeostatic learning.

Главные controls:

```text
FRESH
EXPERIENCED
EXPERIENCED + homeostatic-consequence ablation
EXPERIENCED + motivation ablation
```

---

## v0.8.5 — First Training Curriculum and Survival-Learning Proof

**Status: PLANNED**

Цель — впервые начать систематическое обучение организма на repeated embodied experience и проверить всю цепочку целиком.

### Stage 1 — Discovery beside the organism

Consumable cube появляется непосредственно рядом.

Организм исследует обычные Actions. Successful interaction физически увеличивает `N`; затем interoception фиксирует изменение.

До опыта не должно существовать association между appearance кубика, Action и physiological consequence.

### Stage 2 — One-step approach

Еда находится так, что требуется минимум:

```text
MOVE
→ INTERACT
```

Проверяется model-based multi-step mechanism:

```text
current state
→ predicted movement consequence
→ predicted interact consequence
→ lower trajectory homeostatic cost
```

Первый MOVE должен становиться полезным не из-за reward propagation, а потому что learned model позволяет planner увидеть последующую полезную consequence.

### Stage 3 — Directional variation

Consumable object появляется в разных направлениях/позициях.

Проверяется перенос acquisition без:

- hardcoded coordinates;
- object ID shortcut;
- fixed direction policy;
- food-specific action table.

### Stage 4 — Scarcity and energy economy

Пища появляется реже. Movement и interaction имеют физический energy cost; basal metabolism продолжает работать.

Проверяется, начинает ли acquired model сокращать бесполезные действия и время высокого `T`, а не просто максимизировать число consumptions.

Primary metric — не immediate reward, а качество physiological trajectory.

Главный эксперимент проводится при одинаковых seed/scenario conditions:

```text
FRESH
vs
EXPERIENCED
vs
EXPERIENCED + homeostatic-consequence ablation
vs
EXPERIENCED + motivation ablation
```

Измерять:

- success rate;
- time-to-consume;
- action count;
- energy spent;
- brownout incidence;
- `T(t)` trajectory;
- discounted integral homeostatic cost `J`;
- predicted physiological outcomes;
- planner score/choice differences;
- reproducibility across deterministic seeds/scenarios.

Один удачный эпизод не является доказательством обучения.

Acceptance требует repeated advantage experienced organism над fresh control и причинного исчезновения этого преимущества в соответствующих ablations.

---

## v0.8.6 — Long-Run Metabolic Stability and Freeze

**Status: PLANNED**

Финальный этап проверяет, что physiology/motivation/learning не разрушили causality и long-life stability.

Минимальные gates:

- deterministic replay;
- host-batching invariance;
- exact save/load continuation physiology;
- exact continuation learned physiological Relations;
- bounded `N`, `E`, `H`, `T`;
- no negative/NaN/infinite physiology;
- deterministic brownout behavior;
- no action starts without required energy;
- no wall-clock-dependent metabolism;
- no direct food/reward semantic shortcut;
- no hunger→Action lookup;
- bounded interoceptive/neural representation;
- homeostatic evaluator does not select Actions;
- learned behavior survives normal persistence;
- fresh/experienced/ablation experiment reproducible;
- delayed two-step curriculum works through model-based prediction;
- existing v0.5/v0.6 frozen contracts remain valid;
- `full_graph_sync_calls == 0` remains invariant.

Activity-dependent neural metabolism, если включена, дополнительно должна доказать:

- deterministic cost from simulated neural events;
- bounded cost per causal interval;
- no dependency on CPU/FFI/host metrics;
- no collapse of cognition solely because accounting coefficient dominates total energy budget.

v0.8 намеренно НЕ включает на первом проходе:

- смерть;
- размножение;
- жажду;
- сон;
- сложную биохимию;
- социальные drives;
- эмоции;
- генетическое наследование;
- отдельный reinforcement-learning subsystem;
- TD reward propagation;
- отдельную learned value network.

Эти механизмы имеют смысл только после доказательства базовой цепочки:

```text
physiological need
→ non-semantic interoception
→ learned internal representation
→ ordinary causal experience
→ durable Relations
→ multi-step prediction
→ homeostatic trajectory evaluation
→ Action
→ physical/physiological consequence
→ changed future behavior
```

Если эта цепочка не демонстрирует устойчивого learned advantage относительно fresh и targeted ablated controls, расширять physiology дальше преждевременно.

---

## v0.9.0 — **STAGE IN PLANNIG**

---

## v1.0.0 — **STAGE IN PLANNING**
