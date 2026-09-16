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