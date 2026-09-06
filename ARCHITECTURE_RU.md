# ARCHITECTURE_RU.md — архитектура Synthetic Entity понятным языком

## Зачем нужен этот документ

Оригинальный `ARCHITECTURE.md` написан как инженерный документ. Этот файл объясняет те же принципы так, чтобы было понятно **что происходит внутри системы и зачем каждая часть вообще существует**.

# 1. В системе есть мир, мозг и строгая граница между ними

Базовая схема:

```text
WORLD
  ↓
SensoryFrame
  ↓
SyntheticEntityCore
  ↓
ActionIntent
  ↓
WORLD
```

World содержит полную физическую истину. Core не имеет права читать её напрямую.

Это критично. Если Core сможет спросить у World:

```text
где куб?
какой у него ID?
куда идти?
успешно ли сработал push?
```

то мы уже не исследуем возникновение внутреннего понимания — мы просто подсовываем готовый ответ.

Поэтому всё знание Entity должно появляться через субъективный опыт.

# 2. SensoryFrame — единственный вход физического мира

Сейчас Entity получает локальное визуальное поле и BodySense.

BodySense — это очень примитивные телесные сигналы:

```text
touch_up/down/left/right
holding
action_resistance
```

Они специально не говорят причину.

`touch_right=1` означает «справа есть контакт», а не «справа куб».

Такой дизайн сохраняет чистую причинную границу.

# 3. Сенсорный поток превращается во внутренние структуры

SensoryFrame разбивается на небольшие sensory events.

Повторяющиеся события могут породить primitive Cognits.

Повторяющиеся комбинации и последовательности могут породить Composite Cognits.

Поэтому архитектура допускает постепенную лестницу представлений:

```text
сырое изменение
→ локальный признак
→ устойчивая структура
→ объектоподобная структура
→ ситуация
→ более сложная композиция
```

Ни один уровень не обязан заранее называться «объектом» или «понятием».

# 4. PersistentPercept пытается сохранить непрерывность восприятия

Камера каждый момент выдаёт новый кадр. Без дополнительного механизма одна и та же видимая вещь каждый раз выглядела бы как полностью новый опыт.

PersistentPercept (π) — внутренняя кратковременная гипотеза:

```text
«эта структура сейчас, вероятно, та же, что была мгновение назад»
```

Она использует признаки, положение, время и learned sensorimotor shifts.

Это не object ID из World и поэтому может ошибаться.

# 5. Sensorimotor transforms учатся из собственного движения

Entity не получает жёсткое правило «MOVE_RIGHT сдвигает изображение влево».

Она наблюдает:

```text
сделала действие
→ PersistentPercepts сместились
```

и накапливает статистику таких сдвигов.

Таким образом даже простая геометрическая связь между собственным действием и изменением ощущений частично приобретается опытом.

# 6. CognitiveGraph — долговременный субстрат знаний

Внутренний мозг — sparse graph:

```text
Cognit --Relation--> Cognit
```

Sparse означает, что связи существуют только там, где система реально получила основания их создать.

Это необходимо для масштабирования: полный граф из миллиона Cognit был бы практически невозможен.

Желаемая стоимость одного когнитивного события:

```text
O(затронутые Cognits + реально пройденные Relations)
```

а не:

```text
O(весь мозг)
```

# 7. Почему numeric brain живёт в C++

У Cognit есть много постоянно меняющихся чисел:

- activity;
- threshold;
- confidence;
- utility;
- activity trace;
- refractory state;
- predictive contribution;
- и другие.

Если каждый Cognit является тяжёлым Python object, большая система тратит огромное количество памяти и времени только на инфраструктуру Python.

Поэтому C++ хранит числовое состояние компактно, в массивах и специализированных структурах.

Python хранит смысловые метаданные и исследовательскую логику.

# 8. Native Authority означает один настоящий numeric brain

Раньше существовала промежуточная архитектура:

```text
Python graph
↕ синхронизация
C++ graph
```

Это было плохо: дорого и опасно для корректности.

Теперь native mode устроен так:

```text
C++ NativeBrainEngine = единственный изменяемый numeric state
Python = semantic/research layer
```

Полного зеркала больше нет:

```text
full_graph_sync_calls = 0
```

# 9. Почему используется float64

До текущего этапа C++ хранил часть brain state в float32, а frozen Python oracle использовал float64.

Маленькие ошибки накапливались и впервые проявлялись на tick 149.

В такой системе маленькая ошибка опасна не сама по себе, а тем, что может изменить дискретное решение:

```text
activity < threshold
vs
activity > threshold
```

После этого две реализации уже могут создать разные волны, Relations, composites и выбрать разные Actions.

Поэтому behavior-affecting state теперь переведён на float64.

Результат:

```text
extended lockstep 1000/1000 PASS
```

Native persistence format стал `NBRN v3`.

# 10. Activity Wave — распространение внутреннего контекста

Активный Cognit может возбуждать другие Cognit через Relations.

Эта волна позволяет текущему восприятию активировать:

- связанные воспоминания;
- ожидаемые последствия;
- goal-related structures;
- более сложные composites.

Энергия волны сохраняется: source делит бюджет между связями, а не копирует его по каждой связи.

# 11. Homeostasis — автоматическая регулировка чувствительности

Если Cognit активируется постоянно, система постепенно повышает его порог.

Это мешает одной часто встречающейся структуре захватить всю активность.

В native runtime homeostasis работает лениво: неактивные Cognit не обновляются каждую секунду. Их состояние догоняется при следующем обращении.

Это важнейшая причина, почему огромный dormant brain может оставаться дешёвым.

# 12. TransitionEvidence — кратковременные доказательства

Перед созданием Relation система смотрит на статистику переходов:

```text
как часто B появляется после A?
насколько это выше обычной частоты B?
зависит ли B от конкретного Action?
```

Эта статистика живёт в bounded event ring и нужна только для формирования/обновления Relations.

Она не должна становиться параллельной системой предсказания.

# 13. Relation lifecycle

Новая Relation сначала ненадёжна:

```text
PROVISIONAL
```

Если она многократно подтверждается, становится:

```text
CONSOLIDATED
```

Если начинает противоречить реальности, confidence падает, contradiction растёт, Relation может ослабнуть или исчезнуть.

То есть знания мозга не являются вечными таблицами — они могут адаптироваться.

# 14. Prediction строится только по графу

Активные Cognit и их Relations дают ожидаемые будущие Cognit.

SELF_ACTION Relations позволяют строить разные ожидания для разных Actions.

Поэтому система может сравнивать:

```text
что, вероятно, будет после MOVE_LEFT?
что после MOVE_RIGHT?
что после GRAB?
```

Это основа planning без скрытого world simulator.

# 15. Prediction error возвращает систему к реальности

После действия приходит новый SensoryFrame.

Система сравнивает:

```text
ожидалось
vs
произошло
```

Ошибка влияет на novelty, uncertainty, tension и обучение Relations.

Поэтому cognition образует замкнутый цикл:

```text
предсказание → действие → проверка → изменение знания
```

# 16. Intrinsic tension создаёт внутреннюю причину действовать

Напряжение растёт при редкости, ошибке, неопределённости и потенциальной управляемости ситуации.

Это заменяет внешний reward.

Цель проекта — чтобы Entity исследовала мир не потому, что ей выдали «+1», а потому что непонятные, потенциально контролируемые ситуации сами создают внутреннюю необходимость разобраться.

# 17. Goals живут в когнитивном пространстве

Goal не содержит World coordinates и object IDs.

Он описывает желаемую внутреннюю структуру.

Planner должен найти физический способ приблизить мир к этой структуре через приобретённые Relations.

# 18. BeliefScene хранит конкретных внутренних участников

Есть разница между:

```text
тип отношения LEFT_OF
```

и

```text
конкретный Participant A LEFT_OF конкретного Participant B
```

BeliefScene хранит второе.

Participant IDs принадлежат внутреннему мозгу, а не World.

Это позволяет сохранять endpoint identity и строить action-conditioned predictions для конкретной ситуации.

# 19. Anonymous role binding

Target задаёт роли, но не назначает им физические объекты.

Core сам ищет, какие внутренние participants лучше соответствуют ролям.

Это позволяет проверять перенос знания на:

- другую позицию сцены;
- другой порядок появления;
- distractors;
- новые конкретные объекты.

# 20. Planner разделён на смысл и механику

Python отвечает за смысл:

- Goal alignment;
- semantic mismatch;
- role reasoning;
- memory relevance;
- финальную оценку варианта.

C++ должен отвечать за тяжёлую механику:

- graph prediction;
- relation traversal;
- wave expansion;
- action-conditioned numeric transitions.

Сейчас Planner всё ещё вызывает C++ примерно 503 раза на один physical action. Это следующий performance blocker.

Цель — batch API: передавать много состояний/действий одним крупным вызовом.

# 21. Что такое FFI и почему оно дорого

FFI — граница Python/C++.

Один вызов дешёвый, сотни мелких вызовов — уже нет.

Хорошая архитектура:

```text
Python: вот пакет задач
C++: вот пакет результатов
Python: семантически оцениваю
```

Плохая:

```text
Python→C++ за одним числом
Python→C++ за следующим
Python→C++ за следующим
... 500 раз
```

# 22. Memory остаётся смысловой системой Python

Это намеренно.

Но retrieval не должен проверять всю историю.

Сейчас `SpatialMemory` всё ещё содержит горячие full-history scans.

Следующая оптимизация — индексы:

```text
participant → memories
place → memories
relation type → memories
episode → memories
```

Тогда смысл recall останется тем же, но количество кандидатов станет ограниченным.

# 23. C++ WorldRuntime — будущий физический движок

Он уже умеет single-entity:

- movement;
- turning;
- push;
- grab/carry/release;
- interact;
- resistance;
- perception;
- continuous WorldTime.

Он специально не связан с Pygame и renderer.

Это важно для будущего 3D мира.

# 24. Почему Python World пока не удаляется

Python World — oracle.

Любая ошибка в физике изменит sensory experience, а значит и всё последующее обучение.

Поэтому C++ World включается feature-by-feature только после differential lockstep.

Single-entity 1000 random actions уже проходят.

# 25. Что осталось перенести в WorldRuntime

Нужно добиться parity для:

- seeded initialization;
- spawning;
- exact RNG continuation;
- multiple bodies;
- simultaneous intents;
- body/body conflicts;
- shared-object conflicts;
- rotating fairness.

После этого normal native runtime сможет сделать C++ World authoritative.

# 26. Multi-entity sequencing

Все Entity должны наблюдать один и тот же snapshot мира.

Правильный порядок:

```text
S_t
→ Observe_all
→ Think_all
→ Commit_all
→ ResolveWorld
→ S_{t+1}
```

Нельзя позволять Entity B видеть мир уже после того, как Entity A успела его изменить в том же логическом моменте.

# 27. Независимость мозгов

У каждой Entity отдельные:

- Cognits;
- Relations;
- memory;
- Goals;
- history.

Они не делятся hidden state.

Взаимодействие возможно только через World и будущую коммуникацию.

# 28. WorldTime и EventSequence

`WorldTime` — физическое simulated time в секундах.

`EventSequence` — только причинный порядковый номер.

Пример:

```text
12.274 s, event 150
12.610 s, event 151
```

Время говорит «когда», EventSequence говорит «в каком порядке».

Они специально разделены.

# 29. Почему integer cognitive ticks не должны быть временем

В будущем сложная ситуация может требовать много внутренних операций, а простая — мало.

Количество размышлений не должно автоматически двигать физическое время.

Поэтому следующий runtime будет event-driven и опираться на continuous WorldTime.

Текущий v0.5.2 только закладывает фундамент, без threading/async scheduler.

# 30. Persistence

## `.sebrain`

Переносимая долговременная когнитивная система.

## `.seworld`

Полное состояние конкретной продолжающейся жизни.

Native numeric graph сохраняется бинарно, без экспорта всех Relations в Python.

Текущий native формат — `NBRN v3`.

# 31. Почему Human Renderer и Entity Vision должны быть разными

В будущем 3D renderer сможет рисовать картинку для человека-наблюдателя и отдельно — для глаз Entity.

Эти камеры имеют разные задачи.

Нельзя использовать engine metadata как зрение.

Правильный путь:

```text
3D Scene
→ rendering from Entity eye
→ retinal image/events
→ Cognits
```

а не:

```text
engine knows «duck»
→ Core receives «duck»
```

# 32. Будущий 3D runtime будет специально маленьким

Не нужен аналог Unreal.

Нужно только:

- low-poly scene;
- transforms;
- simple lighting;
- Z-buffer;
- collisions;
- dynamic objects;
- GLB loading;
- observer camera;
- Entity eye cameras.

Blender может оставаться внешним редактором карт.

# 33. Будущее зрение

Entity должна получать субъективную картинку.

План:

```text
широкая периферия низкой детализации
+
центральная fovea высокой детализации
```

Обсуждаемая верхняя детальность fovea — примерно 512×512.

Позже два глаза позволят учить глубину через disparity, motion parallax и собственное движение, а не получать depth buffer как подарок.

# 34. Будущий язык

Язык должен войти в тот же сенсорный цикл.

Ввод:

```text
Unicode symbols
→ sensory events
→ temporal composites
→ word-like structures
→ grounding с другими Cognits
```

Слово приобретает смысл через совместный опыт, а не через заранее загруженный embedding.

# 35. Генерация языка

Целевой принцип:

```text
коммуникативное намерение
→ semantic message
→ linguistic plan
→ последовательность символов
```

Prediction продолжения языка может существовать, но не является всей природой языка.

# 36. Что доказано сейчас

Мы уже имеем доказательства следующих узких утверждений:

- sparse κ/ρ substrate работает;
- graph prediction переживает очистку TransitionEvidence;
- causal-rho ablation удаляет приобретённую способность;
- Experienced 5/5 быстрее Fresh 5/5 в узком pair test;
- native brain больше не является зеркалом Python;
- float64 migration убрала старый tick-149 drift и дала 1000/1000 lockstep;
- single-entity C++ World совпадает с Python World на 1000 random actions;
- 10K run больше не показывает прежний продолжающийся catastrophic slowdown.

# 37. Что не доказано

Пока нельзя честно утверждать наличие:

- сознания;
- самосознания;
- AGI;
- человеческого понимания;
- универсального causal reasoning;
- универсальной object permanence;
- общего construction skill;
- языка;
- полноценного 3D cognition;
- social intelligence.

# 38. Текущий статус v0.5.2

Закрыто:

```text
Native Authority ✅
full_graph_sync = 0 ✅
Relation proxy hot path ✅
10K sustained scaling ✅
native causal proof ✅
NBRN persistence ✅
float64 parity ✅
extended lockstep 1000/1000 ✅
```

Осталось:

```text
Priority 2: Planner FFI batching
Priority 3: SpatialMemory indexing
Priority 4: Native World spawn/RNG/multi parity
```

После этого можно делать финальную проверку и freeze v0.5.2.

# 39. Архитектура целиком

```text
                 WORLD
                   │
                   │ SensoryFrame
                   ▼
        ┌───────────────────────┐
        │   Python semantics    │
        │                       │
        │ BeliefScene           │
        │ memory policy         │
        │ Goals                 │
        │ role binding          │
        │ planner meaning       │
        └──────────┬────────────┘
                   │ IDs / batches
                   ▼
        ┌───────────────────────┐
        │     C++ substrate     │
        │                       │
        │ numeric Cognits       │
        │ Relations             │
        │ waves                 │
        │ prediction            │
        │ evidence              │
        │ lifecycle             │
        │ homeostasis           │
        │ persistence           │
        └──────────┬────────────┘
                   │
                   ▼
            predicted futures
                   │
                   ▼
          Python semantic score
                   │
                   ▼
             ActionIntent
                   │
                   ▼
              WorldRuntime
                   │
                   └────→ новый SensoryFrame
```

# 40. Самая важная мысль

Архитектура пытается сделать так, чтобы интеллект возникал из одного непрерывного процесса:

```text
опыт
→ внутренняя структура
→ связь
→ ожидание
→ ошибка
→ изменение знания
→ цель
→ действие
→ новый опыт
```

То есть система не должна существовать в режиме:

```text
обучение закончилось
теперь только инференс
```

В идеале её вычисление, обучение и жизнь — это один и тот же непрерывный процесс.
