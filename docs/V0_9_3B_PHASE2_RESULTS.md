# v0.9.3b Phase 2 — hot path, determinism и незакрытые условия freeze

Дата: 2026-10-03. **PARTIAL / NOT FROZEN**. Это performance infrastructure,
не новый scientific результат и не long-run v0.9.3. v0.9.3c не создаётся.

v0.9.3b Phase 2 improved the measured hot path but did not satisfy all freeze
criteria. The remaining blockers are explicitly identified below. No cognitive
semantics, acceptance threshold or scientific result was changed to obtain a
performance PASS. Исправление доказанной hashseed-зависимости порядка сложения
описано отдельно; старые raw records после этой коррекции не объявляются exact.

## Provenance

Actual base HEAD и freshly fetched `origin/main`:
`774ada8d80050ee5a3e58ea300a037a524ec388e`, исходный working tree clean.
Final HEAD остаётся тем же; реализация Phase 2 — рабочие изменения без commit/push.
Stale provenance исправлена: **YES**.

Phase-1 измерения остаются привязаны к audit/benchmark execution base
`d17328005e6b9ec5b5e76a0b91625261519043d2` с implementation в working tree.
`774ada8` — последующий integration commit, а не execution HEAD тех измерений.
Предыдущие JSON/CSV/logs и неудачные CUDA measurements сохранены.

Новые инструменты записывают execution HEAD, dirty status, SHA256 tracked diff,
untracked files, реально загруженного native module или executable, Python,
platform и hashseed. SHA модуля особенно важен: build не тождественен текущему
содержимому исходников. Intermediate measurements не переименовываются в final.

Оборудование подтверждено: Ryzen 7 5700X, 8 physical / 16 logical cores,
32 GiB RAM; RTX 3060, 12288 MiB, driver 616.92; nvcc 13.2.51; Python 3.11.9,
MSVC 19.50, CMake Release. Workbench действительно создаёт **OpenGL 3.3.0**,
что также записано в observer logs.

Deployment: observer ON / CUDA OFF в `consciousness`; отдельный observer ON /
CUDA ON build в `cpp/build-v093b-cuda/module`. CUDA-измерения загружают именно
отдельный модуль. `SE_ENABLE_CUDA` остаётся optional, default OFF.

## Native planner batch

Owner thread материализует lazy confidence в прежнем порядке state/source/edge.
После этого создаёт immutable numeric rows: common absence и сохранённые FP64
conditioned factors. Один WorkerPool job обрабатывает всю state×action таблицу,
включая target grouping и products. Workers читают только immutable inputs и
пишут заранее выделенные отдельные output rows. Completion order не определяет
выход. Predictions/effects возвращаются с sorted target IDs, state order и
action order запроса; production actions имеют enum order.

GIL освобождён только на native boundary; Python list construction выполняется
после возврата GIL. Callback, Goal, scenario/resource labels в native input нет.
`planner_numeric_launches` проверяет один numeric launch на batch.
Prediction mask позволяет получить effects без повторной materialization
non-action relations, когда predictions уже предоставлены `_imagine`.

Python использует effects из batch; raw timed-successor rows кэшируются только
внутри одного beam layer. Перед следующей native confidence materialization
этот кэш сбрасывается. Homeostatic estimates кэшируются по полному numeric input
в том же layer; diagnostics и счётчики рассмотренных predictions сохраняются.
Score formula, tie rule, beam ranking, Goal meanings и thresholds не менялись.

Golden oracle `_search` извлечён из `774ada8` и хранится в
`tests/fixtures/planner_search_774ada8.py.txt`. Tests сравнивают каждый candidate,
score components, total score, confidence, levels, temporal diagnostics, Plan,
event stream и final causal state для разных beams/horizons, в том числе
controlled acquired delayed-model fixture. Native tests включают empty/single/
dense/large states, serial/parallel и effect-only lazy boundary.

**Незавершённая часть:** output пока содержит predictions/effects, а не всю
таблицу numeric score/model/homeostatic components. Future construction,
epistemic/loop calculations, delayed valuation и semantic candidate objects
ещё выполняются Python. Это не полная миграция требуемого evaluator.

## Cost model и calibration

Planner cost model ограничен 24 work buckets × 4 state-count buckets × 4 active
degree buckets × 3 backends. Work учитывает common targets, conditioned factors
и relations traversed. Telemetry публикует nodes/relations/source visits/states/
actions/pairs/active degree/factors/targets и memory upper bound.
Equal pairs и даже equal derived work с разным degree не используют одну cost
cell; это проверено native test. Без measured serial baseline AUTO возвращается
к serial. Hysteresis и 20% margin сохранены как host policy.

Optional `calibrate_planner_compute()` использует отдельный synthetic numeric
graph, 4096 nodes / degree 16, разные active counts и state counts. Live organism
не читается и не вычисляется в shadow. Exactness проверяется до принятия samples;
GPU учитывается только при доступном backend/device и memory budget. Метод
`calibrate_compute()` теперь калибрует и реализованный planner numeric batch.
Calibration inertness проверена на непустом causal runtime.

## Profiles и native crossings

Forensic profiler явно включается host-инструментом. Он разделяет candidate
generation, state/action expansion, request prep, native call, future-state
construction, score decomposition, loop/epistemic, homeostatic estimate,
candidate creation, beam sorting/ties и request deduplication. Candidate
deduplication в исходном algorithm отсутствует. Count здесь обозначает line
intervals; p50/p95 относятся к последним 256 samples. Nested call time включён.
Такие timings не используются как production throughput.

Сопоставимые before/after:
`runs/v093b-phase2-profile-reference-final.json` и
`runs/v093b-phase2-profile-final.json`. Reference — frozen Python `_search` на
текущем native engine, а не переобозначение старого Phase-1 binary.

На trained brain, 6 WorldTime, 40 decisions / 39 completed actions:

| Metric | Before | After |
|---|---:|---:|
| Native method calls внутри planner / decision | 945.350 | 100.775 |
| Все native method calls / completed action | 1016.256 | 150.026 |
| Backend FFI counter / completed action | 472.949 | 38.077 |

Property reads не входят в method-call count. Backend FFI counter не охватывает
direct timed-successor calls, поэтому эти метрики показаны отдельно.
Все сравнения сохранили causal digest
`ecba58913a6e35f1a33d637442b21179634d84c786b2f8c2f8629efe2ce229d8`.


??? profiles: 40 searches, 1000 states expanded, 17000 state?action pairs.

| Stage | Count before/after | Total ms before/after | p50 ?s before/after | p95 ?s before/after |
|---|---:|---:|---:|---:|
| candidate_generation | 160/160 | 1.335/1.390 | 1.7/2.5 | 21.9/24.1 |
| state_action_expansion | 19160/19160 | 8.806/7.971 | 0.5/0.4 | 0.8/0.7 |
| prediction_request_preparation | 2275/2315 | 0.981/1.088 | 0.3/0.4 | 1.1/1.2 |
| native_batch_call | 279/359 | 50.449/57.323 | 1.1/0.6 | 668.0/649.5 |
| future_state_construction | 20468/20468 | 66.017/65.729 | 1.1/1.0 | 17.1/17.1 |
| score_decomposition | 68373/68373 | 61.130/57.224 | 0.6/0.6 | 2.2/2.9 |
| loop_epistemic | 68040/68040 | 280.367/286.503 | 0.9/0.8 | 1.1/1.4 |
| homeostatic_estimate | 17000/57460 | 1303.559/416.268 | 56.3/0.7 | 328.8/18.7 |
| candidate_object_creation | 17040/17040 | 28.609/26.222 | 1.7/1.5 | 2.7/2.5 |
| beam_sorting_and_ties | 160/160 | 9.717/9.944 | 69.9/69.3 | 92.6/92.6 |
| deduplication | 1000/1000 | 0.595/0.629 | 0.6/0.6 | 1.0/1.1 |
| other | 224724/286948 | 113.859/123.152 | 0.5/0.5 | 1.2/1.4 |

Stage work_units ????? count line intervals; actual states/pairs ????????? ????????.
????? cache branch ??????????? homeostatic line count, ?? ??????? time:
1303.559 ? 416.268 ms. ??? forensic attribution, ?? production wall time.

Production cProfile (?????????, instrumented trial) ?????????? trained `_search`
cumulative 1.673885 ? 1.196740 seconds, share ????? profiled run 55.5% ? 38.7%.
Python hot path ???????? ????????????. ? reference ? final throughput ??????
module provenance ? ????? ?????: ??? ???????????? before/after, ?? matched
historical whole-binary performance acceptance.

## CPU/GPU benchmark scope

Реальный native graph benchmark покрывает 10k/100k/250k/500k/1M nodes,
degree 16/64, вплоть до **64M Relations**, 17 actions, batches 1×8, 4×128,
8×1024 и 32×4096 active IDs. Это 40 workloads. Каждый backend сравнивается
exact с serial; измеряется total native call, включая owner prep. AUTO начинает
с serial incumbent после измерений, чтобы forced-GPU state не исказил crossover.

Intermediate table `runs/v093b-phase2-native-planner-full.csv` содержит:
**40/40 exact**, tiny → serial 10/10, остальные → parallel 30/30. GPU total
проигрывает всем соответствующим CPU alternatives. Это stateless CUDA result;
он не доказывает отсутствие crossover после persistent graph mirror.

CUDA graph-dependent resident kernel: **НЕ РЕАЛИЗОВАН**.
Compute graph mirror / CSR / dirty journal / applied revision: **НЕ РЕАЛИЗОВАНЫ**.
CUDA использует transient allocations, upload, ordered FP64 products, sync и
readback. GPU logical/allocated/high-water/realloc/delta bytes и отдельные
kernel/transfer/sync timings не измерены. 512 MiB — policy budget, не measured
resident usage. Нельзя применять wording «CUDA graph execution supported».

C/D выше — numeric graph benchmarks; full ContinuousRuntime WorldTime/sec для
large graph и large graph + large batch не измерен.

## Production throughput и observer

Final production series: `runs/v093b-phase2-production-default/`, 5 repeats,
A = default small runtime, 10 WorldTime; B = trained checkpoint из нового
22-episode prefix, 6 WorldTime. Все четыре modes, observer OFF/ON, sequential
processes; startup и cProfile trial отделены от throughput.
Optional-calibration series сохранена отдельно в
`runs/v093b-phase2-production/`; AUTO там включал calibration. Она не должна
смешиваться с default AUTO. Declared seed — 6607, hashseed — 1.

`runs/v093b-phase2-stable-trained-reference.json` — frozen Python search
reference, median 4.63778 WorldTime/sec. Это reference конкретного hot path,
не исторический scientific результат.

Current observer всё ещё scan/rank'ит graph на causal thread с bounded cadence.
Presentation dirty journal/revisions/gap recovery: **НЕ РЕАЛИЗОВАНЫ**.
Graph-wide GPU mirror и full-graph GPU visibility/LOD: **НЕ РЕАЛИЗОВАНЫ**.
Rate AUTO/15/30/60 и detail AUTO/LOW/MEDIUM/HIGH: **НЕ РЕАЛИЗОВАНЫ**.
Presentation full rebuild count не измерен; прежний VBO capacity rebuild counter
не является этой метрикой. Minimized/hidden delta catch-up contract не проверен.
Existing ID layout/filtering/click picking и observer thread сохранены.
Observer improvement и отсутствие full graph scan не объявляются PASS.

## Hashseed: test assumption и architecture bug разделены

Original complete prefix на `774ada8`, seeds 1/2/777, реально расходился.
При seed 2 consumption в episodes 15/16/20, при 1/777 — в episode 22.
Base `d173280` воспроизводил seed-2 failure (Phase-1 evidence сохранена).

Для 1 vs 2 первые 9 episodes имели одинаковые causal event traces. В episode
10 первая граница divergence: index **50**, event **52**, `SENSORY_CHANGE`,
WorldTime **1.05**. Начальный complete causal state этого episode exact.
На этой границе различаются current place, memory и propagated wave; позднее
различаются decisions/consumption. Это не только ошибка индекса в test.

`weighted_similarity` суммировал floating weights по set строковых feature
keys. Порядок зависит от hashseed; differences в последних битах влияли на
строгое сравнение похожих place scores. Теперь обе суммы имеют canonical sorted
order. Формула и thresholds прежние. Stability counters также наполняются в
canonical key order, устраняя artifact byte differences от list order.
Это исправление determinism, а не performance knob. Старое случайное поведение
не объявляется равным каноническому; frozen historical results не переписаны.

После коррекции 1/2/777: все 22 records exact и все 22 artifact bytes exact,
episode-10 event streams exact, digest records
`32cc060c0524092e4b92c2126c718dd6cc302147faf14356bcbcd80a43448a30`.
Raw traces/checkpoints находятся в ignored `results/v093b/`; инструменты replay
и audit находятся в `tools/differential_v093b.py`, `tools/audit_hashseed_v093b.py`.

Test теперь проверяет declared 22-episode set, а не lucky last episode. Для
каждого consumption остаются physical IDs/action, positive nutrient gain и
observed internal-bin increase. Production не гарантирует consumption exactly
в episode 22. Condition не ослаблена до наличия произвольного record.

## Determinism, persistence и verification

Новая matrix: 16 cases = 8 tracked scenarios × fresh/trained brain. Serial,
parallel, GPU, AUTO × observer OFF/GPU-first: **128/128 exact** в
`runs/v093b-phase2-matrix-final.json` (hashseed 2). Сравниваются event stream,
final causal digest, artifact bytes hash/size, World, physiology, scheduler.
Все `full_graph_sync_calls` — **0**.

Historical 64-case rerun: **UNAVAILABLE**, frozen `results/v092/full` checkpoint
отсутствует. Protocol/scenarios tracked, но нового trained checkpoint нельзя
выдать за тот historical brain. Новая matrix не заменяет historical results.

Padding regression использует реальные raw native v3/v4 bytes, сохранённые
engine из `d173280`; fixture содержит provenance и SHA256. Load → canonical
save → reload сохраняет stored nodes/relations/timing semantics; повторный save
canonical bytes exact. Serial/parallel full `.sebrain` bytes также exact.
Persistence schema не менялась.

Intermediate full verify hashseed 2: **784 PASS / 2 GPU skips**, CTest 3/3.
После дальнейших changes targeted CPU: **34 PASS / 2 GPU skips**; CUDA CTest
**3/3**. Final full verify, calibrated matrix и final benchmark records
дополняются перед завершением работы.

## Freeze decision

**PARTIAL / NOT FROZEN**. Конкретные незакрытые архитектурные условия:

1. Native evaluator не возвращает полный набор score/model/homeostatic numeric
   components; Python `_search` остаётся существенной частью hot path.
2. Normal presentation publication всё ещё scan/rank entire graph. Нет общего
   bounded native mutation journal, revision stream, gap/rebuild recovery,
   graph-wide persistent GPU presentation mirror и GPU full-graph visibility.
3. Persistent compute mirror и реальный graph-dependent CUDA prototype отсутствуют.
   Статeless CUDA failure сохранён; hardware limitation после residency не доказана.
4. CPU utilization, GPU timing split, mirror/revision metrics, publication CPU
   cost на large graphs и full C/D production throughput не измерены.

Наличие existing causal dirty-relation set нельзя выдавать за presentation
journal: его consumption принадлежит learning/admission. Для UI требуется
отдельная projection boundary с проверкой всех native mutation paths.
Закрывать эти пункты статусом FROZEN или приписывать VBO slots graph-wide mirror
нельзя. Credit assignment, cognition thresholds, World/physiology/scheduler,
v0.9.2 scientific FAIL и v0.9.3a representational-transfer conclusion сохранены.


## Changed files ? reproducibility

Files changed (source/docs/tests/tools; measurement files ??????????? ????????
? final manifest `runs/v093b-phase2-summary.json`):

- `ARCHITECTURE.md`
- `CURRENT_STATUS.md`
- `README.md`
- `ROADMAP.md`
- `consciousness/backends.py`
- `consciousness/memory.py`
- `consciousness/memory_matching.py`
- `consciousness/planning.py`
- `consciousness/temporal_prediction.py`
- `cpp/CMakeLists.txt`
- `cpp/include/se/compute_runtime.hpp`
- `cpp/include/se/native_brain_engine.hpp`
- `cpp/src/bindings.cpp`
- `cpp/src/compute_runtime.cpp`
- `cpp/src/native_brain_engine.cpp`
- `cpp/tests/compute.cpp`
- `cpp/tests/planner_benchmark.cpp`
- `docs/TESTING.md`
- `docs/V0_9_3B_ADAPTIVE_COMPUTE.md`
- `docs/V0_9_3B_PHASE2_RESULTS.md`
- `docs/V0_9_3B_RESULTS.md`
- `telemetry/performance.py`
- `telemetry/planner_profile.py`
- `telemetry/provenance.py`
- `tests/fixtures/native_brain_d173280.json`
- `tests/fixtures/planner_search_774ada8.py.txt`
- `tests/test_v092_survival_learning.py`
- `tests/test_v093b_compute.py`
- `tests/test_v093b_hashseed.py`
- `tests/test_v093b_historical_padding.py`
- `tests/test_v093b_planner_batch.py`
- `tools/audit_hashseed_v093b.py`
- `tools/benchmark_native_v093b.py`
- `tools/benchmark_production_v093b.py`
- `tools/benchmark_v093b.py`
- `tools/determinism_matrix_v093b.py`
- `tools/differential_v093b.py`
- `tools/profile_planner_v093b.py`

`git diff --check`: **PASS**. Final HEAD `774ada8d80050ee5a3e58ea300a037a524ec388e`;
working tree dirty, ????????? ?? committed/pushed. Final manifest ????????
source checksums, actual loaded binary identities ? ?????? ?? ??? checks.

Reproduction (PowerShell; isolated CUDA module path ?????????? ??? GPU):

```powershell
python tools/verify.py --full
ctest --test-dir cpp/build-v093b-cuda -C Release --output-on-failure
cpp/build-verify/Release/se_presentation_gpu_tests.exe
python tools/benchmark_native_v093b.py --executable cpp/build-v093b-cuda/Release/se_planner_benchmark.exe --output runs/new-native.json
python tools/determinism_matrix_v093b.py --brain results/v093b/phase2-final-hash1/brains/episode_022.sebrain --native-module cpp/build-v093b-cuda/module/_native_brain.cp311-win_amd64.pyd --calibrated-auto --output runs/new-matrix.json
$env:PYTHONHASHSEED="2"
python tools/differential_v093b.py --output results/v093b/new-prefix-hash2 --trace-episodes 10
```

Output directories ??? production/prefix/audit ?????? ???? ??????. Native
benchmark ?????? ??????????? ??? ????????????? ?????????/build workload;
forensic ??????? ?? ???????????? ?????? throughput trials. ?????? configs,
binary hashes ? per-trial telemetry ????????? ? ??????????????? JSON.
