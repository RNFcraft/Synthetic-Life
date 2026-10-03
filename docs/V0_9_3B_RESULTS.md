# v0.9.3b measured results

Date: 2026-10-03. Status: **PARTIAL / NOT FROZEN**.
This is performance infrastructure evidence, not survival or long-run proof.

## Provenance and machine

Phase-1 audit/benchmark execution base: `d17328005e6b9ec5b5e76a0b91625261519043d2`.
The implementation existed as an uncommitted working-tree diff during those
measurements. Its subsequent repository integration commit is
`774ada8d80050ee5a3e58ea300a037a524ec388e`; this does **not** relabel the
earlier measurements as runs on that commit. The Phase-1 fetch failed then.
Phase 2 began with a clean tree at `774ada8`; a successful fresh fetch on
2026-10-03 confirmed that actual `origin/main` matches it. New measurements
record their execution HEAD and working-tree state separately.

AMD Ryzen 7 5700X, 8 physical cores / 16 logical threads; NVIDIA RTX 3060,
12288 MiB VRAM, driver 616.92; CUDA Toolkit/runtime 13.2.51; MSVC 19.50.35727;
Visual Studio 18 2026 generator; Python 3.11.9. Workbench actually reports
**OpenGL 3.3.0 NVIDIA 616.92 / NVIDIA GeForce RTX 3060/PCIe/SSE2**.
All native measurements use Release. Numeric CMake version remains 0.9.3.

Implementation files cover `cpp/include/se/{compute_runtime,native_brain_engine,
brain_snapshot,observer,workbench_brain_gpu,workbench_ui}.hpp`, native dispatch/
CUDA/bindings/observer/workbench sources, CMake, compute and graphics tests,
`telemetry/performance.py`, `main.py`, observer-only publication calls in
`simulation/continuous.py`, architecture/compute tests and host benchmark tools.
README, CURRENT_STATUS, ROADMAP, ARCHITECTURE and TESTING link the partial scope.
No cognitive Settings, thresholds, planner formulas, World/physiology rules,
curriculum or historical scientific results were changed.

## Production throughput

Seed 6607, 10 simulated seconds, five fresh-runtime repeats, startup excluded,
unprofiled median. Baseline was rebuilt from the exact base commit in an isolated
worktree with the same cached SDL3/ImGui source dependencies and compiler.
The small episode completes 66 actions and 478 scheduler events. Observer means
a visible native Workbench with its Brain pane active. Profiled trials are separate.

| Configuration | WorldTime / wall second | Range | Relative to base headless |
|---|---:|---:|---:|
| Base headless | 46.3474 | 44.1779–46.8403 | 1.0000 |
| Base visible Workbench / Brain | 45.8167 | 44.5960–46.0842 | 0.9886 |
| Final forced serial | 47.4560 | 45.8143–47.6097 | 1.0239 |
| Final AUTO | 47.3750 | 46.9712–47.6677 | 1.0222 |
| Final forced parallel | 38.8456 | 38.4400–39.5157 | 0.8381 |
| Final AUTO + Workbench / Brain | 45.9993 | 45.5480–47.0977 | 0.9925 |
| Final AUTO + compatible renderer | 45.8616 | 33.8723–46.6462 | 0.9895 |
| Final calibrated AUTO (three repeats) | 46.2908 | 44.0399–46.4411 | 0.9988 |
| Final forced CUDA (three repeats) | 22.8159 | 22.5603–22.9277 | 0.4923 |

Headless AUTO change: **+2.22%**, small and not a universal speedup claim.
Visible Workbench change: **+0.40%**, within short-run variability. Relative
observer overhead is 1.14% before and 2.90% after; **dramatic overhead reduction
is not established**. Tiny batches do not benefit from forced CPU parallel or CUDA.
AUTO correctly retains serial for this episode, with zero backend switches.
These short measurements do not establish performance stability on large brains.

The pre-implementation native graph matrix is retained in
[`v093b-baseline-native.csv`](../runs/v093b-baseline-native.csv): 10k/100k/1M Cognits,
frontiers 8/100/1000, plus a 100k-Cognit graph grown to 6.4M relations.
Hidden/minimized observer and separate inactive-Brain-pane matrix were **not run**.
There is no claim that small live episodes exercise those large synthetic graphs.

## Profiling evidence

Baseline cProfile identifies Python beam search as the principal CPU cost, not
GPU rasterization. In the final separately profiled 10-second episode `_search`
takes 0.2324 s cumulative, observation 0.1970 s, and full runtime 0.5608 s.
cProfile overhead is substantial; those seconds are not throughput denominators.

The output-only profiler's independent host report is
[`v093b-profile.json`](../runs/v093b-profile.json). Representative cumulative
boundary times: beam refinement 88.60 ms, prediction batch 8.63 ms, native planner
batch boundary 6.15 ms, sensory decomposition 5.79 ms, physical action completion
4.47 ms, relation materialization 2.98 ms, wave 2.06 ms. Scheduler dispatch totals
202.14 ms and includes child work. Samples are bounded; p50/p95/count/EMA/max/work
units are retained. Native sub-stages and traversed-edge work counts are incomplete.
Zero calls for a stage mean it was not exercised, not zero execution cost.

## Numeric crossover

Independent absence outputs, fixed factor order, five timed samples after warmup;
GPU total includes allocation, upload and result synchronization/readback.
All rows are synthetic numeric workloads, not whole planner latency.

| Outputs | Factors/output | Serial µs | Parallel µs | GPU total µs | AUTO | Switches |
|---:|---:|---:|---:|---:|---|---:|
| 8 | 4 | 0.023 | 38.824 | 452.097 | serial | 0 |
| 8 | 32 | 0.200 | 44.276 | 442.037 | serial | 0 |
| 128 | 4 | 0.290 | 34.829 | 484.992 | serial | 0 |
| 128 | 32 | 1.787 | 32.830 | 425.057 | serial | 0 |
| 4096 | 4 | 7.854 | 39.861 | 456.786 | serial | 0 |
| 4096 | 32 | 44.145 | 52.253 | 513.730 | serial | 0 |
| 100000 | 4 | 222.563 | 116.073 | 1401.150 | parallel | 1 |
| 100000 | 32 | 1264.870 | 426.702 | 3963.650 | parallel | 1 |
| 1000000 | 4 | 3181.600 | 2401.070 | 8120.770 | parallel | 1 |
| 1000000 | 32 | 14105.900 | 8048.430 | 32086.600 | parallel | 1 |

CPU parallel provides a useful crossover on these large arrays. **CUDA BACKEND
IMPLEMENTED / NO BENEFICIAL CROSSOVER OBSERVED IN TESTED RANGE**. AUTO never
selects CUDA in this matrix. No threshold was lowered to manufacture GPU activity.
Separate CUDA kernel-only and transfer-only timing was not collected. GPU graph
mirror bytes: **0 (stateless kernel)**. GPU scratch/transfer rate and VRAM high-water
mark: **not instrumented**, not a fabricated zero. Raw data:
[`v093b-crossover-cuda.csv`](../runs/v093b-crossover-cuda.csv).

## Presentation evidence

GPU layout, endpoint calculation and relation filters work on OpenGL 3.3. The
explicit graphics test validates known-ID picking against the established CPU
hash layout, empty pick, resize, one changed-node upload and unchanged-snapshot
zero upload. A one-pixel read happens on click. It does not claim nonblocking hover.

Final observer telemetry, median last sample across five repeats: UI preparation
**0.0575 ms**, upload CPU **0.0005 ms**, GPU draw **0.001024 ms** (driver timer
granularity applies). Median allocated VBO capacity **12576 bytes**; cumulative
upload **36312 bytes**, five buffer growth rebuilds, 38 changed ranges. These are
small-episode presentation samples, not large-graph acceptance. Upload totals also
include observer startup, so dividing by simulation-only elapsed time would be
misleading. Baseline native UI/GPU timing was not instrumented; before/after CPU
geometry ms and transfer bytes/sec are **not established**.

The runtime still performs graph scan/ranking when publishing a bounded snapshot,
at a host cap instead of every event. Renderer slot differences are not a native
graph dirty journal. GPU visibility/LOD, presentation revisions/gap recovery and
rich rate/detail controls remain open. **GPU-first Workbench: PARTIAL**.

## Exactness and regression gates

The production episode has the same exact causal digest in baseline, serial,
parallel, CUDA, AUTO, calibrated AUTO, observer OFF, observer GPU renderer and
observer compatible renderer:

`10a27313f2f244befe148e7aea3f40ee941caa8a9c8cd889a74e12efdbc918a0`

Event-boundary tests compare complete boundary streams for AUTO/parallel/CUDA
against serial. Native CUDA tests compare FP64 bit patterns, not rounded values.
Observer/profiler tests verify inertness. All cases retain `full_graph_sync_calls=0`.
GPU cases are explicitly skipped on a CPU-only module and run against an isolated
CUDA module. No silent numerical tolerance is introduced.

During base/current 22-episode differential measurement with `PYTHONHASHSEED=2`,
the first raw-record difference was episode 1 `brain_checksum`. All 22 records
match exactly except explicitly classified brain checksums. All logical brain
sections match; raw NBRN differs at C++ `PersistedRelation` padding and resulting
header checksum bytes. Persistence now writes zero padding with unchanged v3/v4
layout; a new test demands byte-identical `.sebrain` across serial/parallel.
Historical binary checksums cannot be retroactively called identical.
The classified first divergence is in
[`v093b-hash2-base-differential.json`](../runs/v093b-hash2-base-differential.json).

An existing production training regression is **not universally green**: with
hashseed 2, the fixed prefix has consumption in episodes 15, 16 and 20 but not 22.
The existing test indexes episode 22's empty consumption list. The exact same
outcome occurs with base native engine d173280. Seeds 1, 777 and 42 pass that test.
No scenario, threshold, criterion or historical conclusion was changed to hide it.
The unrestricted-hashseed full run records **1 failed, 761 passed, 2 skipped**;
the failure is the existing `test_reduced_autonomous_training_observes_physical_consumption_and_bins`.
An earlier pre-final run passed 760 cases with one GPU skip. This does not override
the subsequent failure. Final fixed-seed validation is recorded separately below.

Historical 64-case reverse/expanded frozen-brain audits could not be rerun because
`results/v092/full/results.json` and its frozen brains are absent from this checkout.
Existing forensic/hashseed/serialized-order tests run in the ordinary suite; this
is not a substitute for the unavailable historical artifact matrix.

Build/test matrix:

- Release observer ON, CUDA OFF: build; native CTest **3/3 PASS**.
- Release observer OFF, CUDA OFF: build; native CTest **2/2 PASS**.
- Release observer OFF, CUDA ON: build; native CTest **2/2 PASS**.
- Explicit real-OpenGL graphics test: **PASS**.
- CUDA compute/architecture/v0.9.3a targeted suites before padding correction:
  **39 PASS**, including the actual 30-second-onset hashseed regression.
- The same CUDA suites after padding correction: **40 PASS**, including exact
  brain artifact bytes across CPU execution modes.
- CPU compute/persistence/forensic/architecture after padding correction:
  **50 PASS / 2 explicit GPU skips**.
- Final full verify with explicitly fixed `PYTHONHASHSEED=1`:
  **763 PASS / 2 explicit GPU skips**, CTest **3/3 PASS**; see
  [`fixed-seed log`](../runs/v093b-full-verify-hash1.log). This does not erase the
  unrestricted-hashseed failure recorded in [`its log`](../runs/v093b-full-verify.log).

Final status is independent by area: CPU parallel **PASS for implemented numeric
segments**; GPU compute **IMPLEMENTED BUT NOT BENEFICIAL**; GPU-first Workbench
**PARTIAL**; supported-backend causal equivalence **PASS in declared tests**;
complete milestone acceptance **NOT ESTABLISHED**, including the existing
hashseed-sensitive production regression and missing presentation dirty stream.
v0.9.2 remains EXPERIMENT COMPLETED / PROOF NOT ESTABLISHED. v0.9.3a remains
AUDIT COMPLETE / REPRESENTATIONAL-TRANSFER LIMIT IDENTIFIED. Long-run v0.9.3 is
PLANNED; no stability or representational-transfer repair claim is made.


## Phase 2 ? 2026-10-03

See [Phase 2 evidence and remaining freeze blockers](V0_9_3B_PHASE2_RESULTS.md).
Native planner prediction/effect rows now use a single immutable state-action
worker-pool job, with bounded shape-specific measured costs and per-layer exact
numeric caches. Historical Phase-1 measurements above retain their execution
provenance. Full score migration, resident compute graph and presentation delta
stream/full GPU graph mirror remain incomplete: **PARTIAL / NOT FROZEN**.
