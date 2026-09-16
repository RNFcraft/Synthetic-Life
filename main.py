Работаем над репозиторием:

RNFcraft/Synthetic-Life

Начинаем новый milestone:

v0.6.5 — NEURAL COGNITION -> BEHAVIOR

Сначала самостоятельно изучи актуальный HEAD, git status, README.md,
ARCHITECTURE.md, CURRENT_STATUS.md, ContinuousRuntime, Core, planner,
transition/relation learning, action selection и v0.6.4 sensory-neural path.

Последний известный frozen baseline:

9961a90466142d6ff548e9e6feef9ac941f765e5
update v0.6.4(2)

v0.6.0–v0.6.4 считаются frozen.

НЕ начинать v0.6.6.
НЕ начинать v0.7.0.

==================================================
ГЛАВНАЯ ЦЕЛЬ v0.6.5
==================================================

Сейчас существует causal путь:

World
  ↓
SensoryFrame
  ↓
non-semantic receptors
  ↓
micro-κ / micro-ρ
  ↓
Assembly
  ↓
Assembly-derived ordinary Cognit

Но этот новый neural Cognit пока практически не является полноценной причиной
поведения сущности.

v0.6.5 должен замкнуть путь:

World
  ↓
SensoryFrame
  ↓
micro-neural dynamics
  ↓
Assembly
  ↓
ordinary Cognit
  ↓
ordinary cognitive graph / memory / learned Relations
  ↓
existing planner
  ↓
Action
  ↓
World

Главный acceptance statement:

"Experience-derived neural Cognits can causally participate in ordinary
action selection through the existing cognition/planner mechanisms."

==================================================
КЛЮЧЕВОЙ ПРИНЦИП
==================================================

НЕ создавать новый neural planner.

НЕ делать:

if assembly_id == X:
    MOVE_LEFT

if neural_cognit_active:
    choose_action(...)

НЕ создавать:

Assembly -> ActionType table
sensor -> action mapping
special neural reward
special neural goal
hidden behavior policy

Assembly-derived Cognit должен быть обычным Cognit.

После рождения он отличается от других Cognits только origin/kind metadata,
если это уже нужно observer/facade.

Его activity должна влиять на cognition только через существующие механизмы:

- Cognit activity;
- ordinary Relations;
- transition/action evidence;
- prediction;
- memory/context;
- existing planner scoring;
- existing Goal system.

==================================================
ЧТО НУЖНО СНАЧАЛА ПРОВЕРИТЬ
==================================================

Перед реализацией подробно проследи текущую цепь:

Assembly recognition
    ->
process_continuous_assembly_bridge()
    ->
ordinary Cognit receive/wave
    ->
???

и выясни, почему neural-derived active Cognit сейчас не становится полноценным
контекстом следующего action decision.

Проверь:

- previous_active;
- previous_context;
- continuous_frontier.current;
- planner session input;
- prediction input;
- relation evidence;
- transition evidence;
- action effects;
- dirty Cognits;
- memory/trace ownership;
- cognition_generation;
- timing относительно COGNITION_WAKE / CONTINUE / action commit.

Не дублируй состояние.

Найди минимальный authoritative integration point.

==================================================
CAUSAL SEMANTICS
==================================================

Если Assembly Cognit активируется в t:

    neural recognition @ t
        ->
    ordinary Cognit activation @ t
        ->
    ordinary cognitive consequence @ t

Но нельзя просто менять уже committed action из прошлого.

Если action уже committed до t:

    neural event @ t

может влиять только на следующую causally valid deliberation.

Если neural event приходит во время ещё не завершённой cognition frontier,
нужно определить deterministic semantics:

вариант A:
    neural Cognit входит в текущий still-open cognition context;

или

вариант B:
    invalidates/restarts/refines current deliberation;

или другой архитектурно чистый вариант.

Сначала изучи текущий scheduler/planner lifecycle и выбери минимальную
детерминированную семантику.

Нельзя иметь race:

результат зависит от того, одним большим run_until() или многими маленькими
вызовами прошёл host.

==================================================
НЕ СОЗДАВАТЬ ВТОРУЮ КОГНИТИВНУЮ СИСТЕМУ
==================================================

Запрещено:

neural_active_context
neural_planner
neural_action_scores

как отдельные параллельные authoritative механизмы.

Нейронно возникшие Cognits должны входить в существующий:

Cognit graph
planner input
prediction system
transition learning
trace/context

тем же способом, которым туда входят ordinary Cognits.

Если требуется небольшая metadata отметка источника — допустимо.

==================================================
LEARNING / ACTION-OUTCOME
==================================================

Очень важно:

v0.6.5 НЕ должен вводить новый RL algorithm.

Используй уже существующие:

- transition evidence;
- SelfAction Relations / action-conditioned evidence;
- affordance/effect learning;
- prediction;
- planner.

Если существующая архитектура уже умеет учить:

context + action -> outcome/effect

то Assembly-derived Cognit должен автоматически стать допустимым context
participant.

То есть со временем возможно:

neural Cognit A active
    +
action X
    ->
observed consequence Y
    ->
ordinary evidence strengthens

а затем:

A active again
    ->
planner prediction differs
    ->
behavior can differ.

Никакой заранее заданной ценности A.

==================================================
ДВА УРОВНЯ ACCEPTANCE
==================================================

Нужно доказать отдельно:

A. CAUSAL PARTICIPATION

Assembly-derived Cognit реально входит в cognition/planner context.

B. BEHAVIORAL CONSEQUENCE

При одинаковом внешнем состоянии и одинаковом learned graph наличие/отсутствие
релевантного neural Cognit может причинно изменить existing planner decision.

Но изменение должно происходить через ordinary graph/planner semantics.

==================================================
EXPERIMENT A:
WORLD -> NEURAL COGNIT -> PLANNER CONTEXT
==================================================

Использовать настоящий production path:

World
-> SENSORY_CHANGE
-> SensoryFrame
-> receptor transduction
-> micro dynamics
-> Assembly
-> Cognit

После recognition проверить, что этот Cognit:

- является ordinary live Cognit;
- присутствует в causally appropriate cognitive active/context state;
- может быть traversed обычной wave;
- доступен existing prediction/planner machinery;
- не копируется в Python numeric shadow.

Не inject Cognit напрямую.

==================================================
EXPERIMENT B:
ORDINARY RELATION CAUSALITY
==================================================

Для точного low-level proof допустимо использовать заранее созданную ОБЫЧНУЮ
Relation между уже возникшим neural Cognit и обычным downstream Cognit,
если это нужно изолировать integration semantics.

Но:

- Relation должна быть обычной;
- никакой special neural relation type;
- никакой direct ActionType mapping.

Показать:

neural Cognit recognized
    ->
ordinary Relation traversed
    ->
downstream Cognit changes
    ->
planner-visible state changes.

Ablate/remove Relation:
    effect disappears.

Restore same ordinary Relation:
    effect returns.

Это isolation test, не главный learning proof.

==================================================
EXPERIMENT C:
BEHAVIORAL ABLATION
==================================================

Нужен настоящий Action selection test.

Сделать два deterministic runs с одинаковыми:

- seed;
- World state;
- learned graph;
- Goals;
- scheduler history.

RUN A:
    neural behavioral participation enabled.

RUN B:
    neural sensory/Assembly representation не участвует в planner context
    через чистую экспериментальную ablation.

Нельзя менять World или Goal между runs.

Если learned ordinary Relations делают neural representation поведенчески
релевантной, результат должен показать causal difference:

- action score;
- predicted outcome;
- chosen Action;

хотя бы один из них, а выбранное действие предпочтительно.

Важно:

не hardcode ожидаемый action специально для Assembly ID.

==================================================
EXPERIMENT D:
REAL EXPERIENCE LEARNING
==================================================

Если текущий transition/action-effect machinery позволяет это без создания
нового learning algorithm, ОБЯЗАТЕЛЬНО сделать end-to-end proof:

World sensory context A
    ->
neural Cognit A
    ->
real Action X
    ->
real observable outcome
    ->
existing transition/effect evidence learns

повторить опыт.

Затем снова показать context A.

Проверить, что existing planner's prediction/action score reflects learned
experience.

Контроль:

novel context B
    ->
не получает автоматически тот же learned association.

Это должно быть learned association, а не Assembly identity rule.

Если текущая frozen architecture объективно не способна провести такой тест
без введения нового reinforcement/value subsystem:

НЕ изобретать его в v0.6.5.

Тогда:
- доказать causal planner participation;
- явно записать limitation;
- оставить value/motivation learning будущему milestone.

==================================================
НЕ ПОДМЕНЯТЬ МОТИВАЦИЮ
==================================================

v0.6.5 НЕ про:

- hunger;
- reward;
- pleasure/pain;
- intrinsic reward redesign;
- drives;
- emotions.

Мы пока доказываем только:

neural experience can influence existing decisions.

Если existing Goal необходим для planner experiment — использовать обычный
existing Goal mechanism.

Не давать neural Cognit врождённую положительную/отрицательную ценность.

==================================================
OLD PERCEPTION PATH
==================================================

v0.6.4 оставил:

SensoryFrame
   ├── legacy/current cognitive perception
   └── neural sensory path

Не удалять старый путь в v0.6.5.

Нужно избежать double counting.

Один и тот же sensory event может присутствовать в двух representational paths
на этом переходном этапе, но новый neural path не должен искусственно удваивать:

- reward;
- transition support;
- relation evidence;
- action outcome;
- Goal strength.

Если один physical observation приводит к двум representation types,
каждая может быть context evidence, но physical transition должен учитываться
один раз.

Добавить regression/telemetry test при необходимости.

==================================================
TIMING / EVENT SCHEDULER
==================================================

Сохранить unified timeline из v0.6.3/v0.6.4.

Порядок:

World events
language
sensory input
neural boundary
Assembly bridge
cognition
action
maintenance

должен определяться existing EventScheduler time + sequence.

Нельзя запускать planner прямо из native callback.

Никаких Python callbacks per spike.

Coarse Assembly/Cognit events only.

Host batching invariant:

run_until(10)

и последовательность:

run_until(2)
run_until(5)
run_until(10)

при одинаковой event history должны давать одинаковые:

- neural state;
- Cognit state;
- planner-visible context;
- action sequence;
- final World state.

==================================================
COGNITIVE FRONTIER INVALIDATION / MERGE
==================================================

Особенно проверь случай:

COGNITION_WAKE @ t
planner starts
    ↓
NEURAL_BRIDGE @ same t
    ↓
Cognit becomes active

Что происходит с незавершённым planner session?

Нельзя позволить planner использовать stale state и проигнорировать причинно
предшествовавший/same-time neural event.

Выбери и задокументируй deterministic rule.

Например:

any relevant newly-active Cognit before action commit
    ->
existing deliberation frontier receives/merges it
или
    ->
frontier is deterministically invalidated and rebuilt.

Не делать бесконечный restart loop.

Нужен focused test.

==================================================
NO DIRECT ACTION EFFECT
==================================================

Добавить anti-cheat tests/search assertions, что sensory/neural code не содержит
зависимости от:

ActionType
MOVE_
GRAB_
INTERACT_
Goal target
reward label

кроме generic scheduler/runtime integration там, где технически необходимо.

NeuralSensoryTransducer вообще не должен знать про ActionType.

NeurodynamicSubstrate тоже.

==================================================
DELETION / LIFECYCLE
==================================================

Если Assembly-derived Cognit удаляется ordinary lifecycle:

- planner/context must not retain dangling ID;
- next recognition may create new monotonic Cognit per v0.6.3;
- no learned Relation may silently point to dead Cognit;
- new Cognit does NOT magically inherit old action meaning unless ordinary
  persistence/relearning semantics explicitly imply it.

Добавить focused lifecycle test если текущие regressions не покрывают integration.

==================================================
SNAPSHOT / RESTORE
==================================================

Save may happen after:

neural Cognit recognized
but before action commit.

After restore:

- same pending cognition/planner frontier;
- same neural state;
- same active Cognit/context;
- same eventual Action;
- no duplicate bridge delivery;
- no duplicate relation evidence;
- no duplicate action commit.

Нужен deterministic continuation test.

==================================================
SILENCE / PERFORMANCE
==================================================

When no sensory/neural event:

- no extra planner wake;
- no polling;
- no scan all neural Cognits;
- no scan entire graph just to discover neural activity.

Work scales with actual coarse activity.

Do not introduce periodic "check neural context" loops.

==================================================
FEATURE / ABLATION
==================================================

Нужен чистый research ablation mechanism.

Не обязательно user-facing setting.

Но tests должны иметь возможность сравнить:

neural representation exists and participates

vs

same learned system with neural behavioral contribution suppressed.

Ablation must NOT:

- delete World objects;
- change RNG;
- change Goal;
- reset graph;
- alter unrelated cognition.

Это нужно для доказательства causality.

==================================================
REQUIRED TEST MATRIX
==================================================

Минимум:

A. real World -> neural Cognit -> planner context
B. ordinary Relation propagation from neural Cognit
C. same-time open cognition frontier receives/restarts deterministically
D. neural behavioral ablation changes relevant planner result
E. no direct Assembly -> Action mapping
F. host batching parity including action sequence
G. snapshot/restore before action commit
H. deletion leaves no dangling behavioral context
I. disabled neural sensory baseline unchanged
J. silence creates zero extra behavioral work
K. v0.6.0–v0.6.4 regressions

Если existing learning supports it:

L. actual experience learns context/action consequence
M. novel neural context does not inherit association
N. recurrence improves/reuses learned prediction without duplicate evidence

==================================================
SUCCESS CRITERION
==================================================

Не считать успехом только:

"neural Cognit appears in previous_active"

Нужен observable causal chain:

neural representation
    ->
ordinary cognition
    ->
planner-visible difference
    ->
behavioral consequence

При этом:

NO direct policy mapping.

==================================================
НЕ ДЕЛАТЬ
==================================================

Не реализовывать:

- v0.6.6 long-life stabilization;
- v0.7 engine/UI;
- hunger/thirst;
- new reward system;
- dopamine;
- emotions;
- drives;
- top-down Cognit -> micro-neural feedback;
- attention redesign;
- language redesign;
- internet/browser;
- tool use;
- reproduction;
- multi-agent society;
- v2.0 world.

==================================================
REGRESSION GATES
==================================================

Сохранить frozen invariants:

v0.6.0:
event-driven micro dynamics

v0.6.1:
local plasticity/homeostasis

v0.6.2:
evidence-derived Assemblies

v0.6.3:
Assembly -> Cognit
event-time causality
exactly-once
bounded bridge

v0.6.4:
World -> non-semantic receptors
same-frame simultaneity
bounded receptor bank
retinotopy
production .seworld restore

Также:

full_graph_sync_calls == 0

No Cognit -> neural feedback.

Disabled baseline digest должен остаться прежним, если behavior coupling
feature is inactive/default-compatible.

==================================================
VALIDATION
==================================================

После реализации запустить реальные:

- new v0.6.5 focused tests;
- focused v0.6.0–v0.6.5;
- full pytest;
- Release native build;
- CTest Release;
- deterministic disabled baseline;
- batching parity;
- behavioral ablation;
- open-frontier same-time neural event;
- snapshot/restore before commit;
- lifecycle deletion;
- silent-work test;
- full_graph_sync_calls.

Не копировать старые test counts.

==================================================
v0.6.5 FREEZE GATE
==================================================

Все должны быть PASS:

real neural Cognit enters ordinary cognition        PASS
planner can consume neural-derived context          PASS
ordinary Relations work from neural Cognit          PASS
no special neural planner                           PASS
no direct neural -> ActionType mapping               PASS
neural context can causally alter planner result     PASS
behavioral ablation proves causality                 PASS
same-time frontier semantics deterministic           PASS
host batching parity                                 PASS
snapshot/restore exact before action commit          PASS
deletion/lifecycle safe                              PASS
no duplicate physical evidence                       PASS
silence adds zero work                               PASS
no Cognit -> neural feedback                         PASS
v0.6.0–v0.6.4 regressions                            PASS
full_graph_sync_calls == 0                           PASS

If existing frozen learning already supports real action-outcome learning,
also require:

real experience learning                             PASS
novel context control                                PASS

Если substantive gate не доказан:

v0.6.5: PROVISIONAL

Только если все применимые gates доказаны:

v0.6.5: FROZEN

==================================================
DOCUMENTATION
==================================================

После фактических тестов минимально обновить:

README.md
ARCHITECTURE.md
CURRENT_STATUS.md

Очень важно не писать:

"entity understands objects"
"entity learned survival"
"entity has motivation"

если это не доказано.

Правильная формулировка примерно:

"Experience-derived neural Cognits can now participate causally in ordinary
cognition and existing planner decisions."

==================================================
FINAL REPORT
==================================================

В конце сообщить:

- HEAD before/after;
- почему neural Cognit раньше не влиял полноценно на behavior;
- выбранный authoritative integration point;
- same-time cognition frontier semantics;
- как neural Cognit входит в ordinary planner context;
- как исключён direct action mapping;
- behavioral ablation result;
- learning result, если existing machinery позволил;
- batching parity;
- snapshot/restore;
- deletion/lifecycle;
- files changed;
- focused test count;
- full pytest;
- Release build;
- CTest;
- baseline digest;
- full_graph_sync_calls;
- remaining limitations.

Последняя строка строго:

v0.6.5: FROZEN

или

v0.6.5: PROVISIONAL

После этого STOP.

Не начинать v0.6.6.import argparse
import time
from collections.abc import Callable

from simulation import ContinuousRuntime


OBSERVER_BUILD_HELP = """Native observer is unavailable.
Rebuild with:
    cmake -S cpp -B cpp/build -DSE_BUILD_OBSERVER=ON
    cmake --build cpp/build --config Release"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic Entity continuous native runtime")
    parser.add_argument("--headless", action="store_true", help="run the continuous runtime without a window")
    parser.add_argument("--seconds", type=float, help="simulated seconds to execute (headless default: 100)")
    parser.add_argument("--speed", type=float, default=1.0, help="live simulated-time multiplier")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--save", metavar="PATH", help="write a continuous .seworld snapshot after execution")
    parser.add_argument("--load", metavar="PATH", help="load a continuous .seworld snapshot before execution")
    parser.add_argument("--telemetry", metavar="PATH", help="deprecated legacy tick telemetry; unavailable in production continuous mode")
    args=parser.parse_args(argv)
    if args.seconds is not None and args.seconds<0:parser.error("--seconds must be non-negative")
    if args.speed<=0:parser.error("--speed must be positive")
    if args.telemetry:parser.error("--telemetry is legacy tick-only and is not available in the continuous production entrypoint")
    return args


def create_runtime(seed:int=12345,load_path:str|None=None)->ContinuousRuntime:
    return ContinuousRuntime.load_world(load_path) if load_path else ContinuousRuntime(seed=seed)


def run_headless(runtime:ContinuousRuntime,seconds:float)->ContinuousRuntime:
    if seconds<runtime.world_time:raise ValueError("--seconds precedes the loaded WorldTime")
    runtime.run_until(seconds);return runtime


def drive_live(runtime:ContinuousRuntime,observer,speed:float=1.0,seconds:float|None=None,
               monotonic:Callable[[],float]=time.monotonic,sleep:Callable[[float],None]=time.sleep)->ContinuousRuntime:
    if speed<=0:raise ValueError("speed must be positive")
    if seconds is not None and seconds<0:raise ValueError("seconds must be non-negative")
    if not observer.start():raise RuntimeError("native observer did not start")
    if seconds is not None and seconds<runtime.world_time:raise ValueError("--seconds precedes the loaded WorldTime")
    real_start=monotonic();sim_start=runtime.world_time;deadline=seconds
    try:
        while observer.is_running:
            target=sim_start+max(0.0,monotonic()-real_start)*speed
            if deadline is not None:target=min(target,deadline)
            if target>runtime.world_time:runtime.run_until(target)
            if deadline is not None and runtime.world_time>=deadline:break
            sleep(.005)
    finally:observer.stop()
    return runtime


def create_native_observer(runtime:ContinuousRuntime):
    native=runtime.simulation.world.native
    if not hasattr(native,"create_observer"):raise RuntimeError(OBSERVER_BUILD_HELP)
    try:
        runtime.publish_brain_snapshot()
        return native.create_brain_observer(runtime.simulation.core.backend.engine)
    except (AttributeError,RuntimeError) as error:raise RuntimeError(OBSERVER_BUILD_HELP) from error


def main(argv:list[str]|None=None)->None:
    args=parse_args(argv);runtime=create_runtime(args.seed,args.load);started=time.perf_counter()
    if args.headless:
        seconds=100.0 if args.seconds is None else args.seconds;run_headless(runtime,seconds)
    else:
        observer=create_native_observer(runtime)
        try:drive_live(runtime,observer,args.speed,args.seconds)
        except KeyboardInterrupt:pass
    elapsed=time.perf_counter()-started
    if args.save:runtime.save_world(args.save)
    print(f"world time:           {runtime.world_time:.6f} s")
    print(f"host elapsed:         {elapsed:.3f} s")
    print(f"actions completed:    {runtime.actions_completed}")
    print(f"final cognit count:   {len(runtime.simulation.core.graph.nodes)}")
    print(f"final relation count: {runtime.simulation.core.graph.relation_count}")


if __name__=="__main__":main()
