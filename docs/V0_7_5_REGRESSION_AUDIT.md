# v0.7.5 full regression and performance audit

## Verdict and scope

Audit baseline: `e97a7b769c0742300bb007d0ad132337de41253d` (v0.7.0).
Audited implementation: `2f9c0e311c9b0266d076c59636a5aa2c2585aca5`
(v0.7.4). The working tree was clean before measurement. No runtime, test, or
tooling implementation was changed during this audit.

Verdict: **PASS / FROZEN**. No semantic, numeric, causal, persistence, ABI, ID,
RelationHandle or structural-counter divergence was found. Changes from v0.7.0
through v0.7.4 classify as documented readability, Python extraction, C++
translation-unit extraction, and repository/tooling work.

## Environment and commands

- Microsoft Windows 11 Pro
- Python 3.11.9; pytest 9.0.2
- CMake 4.3.1; MSVC 19.50.35727; Release configuration
- Git 2.53.0.windows.2

Primary commands:

```powershell
python tools/verify.py --full
python -B -m pytest -q tests/test_v02*.py        # repeated per version group
python -B -m experiments.v066_long_life --duration 1000 --windows 10 --seed 6606
git worktree add --detach <temporary-path> e97a7b769c0742300bb007d0ad132337de41253d
cmake -S <temporary-path>/cpp -B <temporary-path>/cpp/build -A x64
cmake --build <temporary-path>/cpp/build --config Release
```

The canonical 12-WorldTime workload was run seven times in each worktree with
seed 6607. `se_benchmark.exe` was run three times per worktree. The temporary
detached worktree was clean and removed after measurement.

## Full verification

`python tools/verify.py --full` ran both production smokes, pytest once, Release
build, and Release CTest. Result: 422 passed in 36.23 s; complete workflow 40.40
s; build PASS; CTest 2/2 PASS. Inspection of `tools/verify.py` confirms these are
the declared full gates, with fail-fast propagation.

## Version acceptance matrix

| Contract | Protecting files | Tests | Result |
|---|---|---:|---|
| v0.2 | `test_v02*.py` | 6 | PASS |
| v0.3 | `test_v03*.py` | 14 | PASS |
| v0.4 | `test_v04*.py` | 10 | PASS |
| v0.5.1 | `test_v051*.py` | 48 | PASS |
| v0.5.2 | `test_v052*.py` | 41 | PASS |
| v0.5.3 | `test_v053*.py` | 97 | PASS |
| v0.5.4 | `test_v054*.py` | 25 | PASS |
| v0.5.5 | `test_v055*.py` | 18 | PASS |
| v0.5.6 | `test_v056*.py` | 9 | PASS |
| v0.5.7 | `test_v057*.py` | 12 | PASS |
| v0.6.0 | `test_v060*.py` | 11 | PASS |
| v0.6.1 | `test_v061*.py` | 10 | PASS |
| v0.6.2 | `test_v062*.py` | 9 | PASS |
| v0.6.3 | `test_v063*.py` | 20 | PASS |
| v0.6.4 | `test_v064*.py` | 13 | PASS |
| v0.6.5 | `test_v065*.py` | 10 | PASS |
| v0.6.6 | `test_v066*.py` | 23 | PASS |

The groups overlap neither each other nor the non-versioned core/tooling tests.
Their sum is 376; the complete suite adds 46 non-versioned tests.

## Determinism and structural equivalence

For `PYTHONHASHSEED=1` and `777`, current output was:

```text
digest  7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f
actions 79; scheduler events 655; queue peak 3
Cognits 27; Relations 162; full_graph_sync_calls 0
```

All seven v0.7.0 and seven current performance runs produced that same digest.
They also matched exactly on planner cycles (294), FFI calls (2668), the full
native neural telemetry tuple, and Assembly records (6). There was no seed,
run, or baseline/current counter deviation.

## Causal, parity, and persistence evidence

- Python/native graph prediction and evidence: `test_v052_native_engine.py`;
  C++ oracle fixture: Release `se_equivalence` against
  `cpp/fixtures/oracle_v051.txt`.
- World differential behavior, RNG, conflicts, multi-entity ordering and
  continuation: `test_v052_native_world_parity.py` and
  `test_v053_continuous_world.py`.
- `(time,id)` ordering, same-time physical/cognition/language/neural ordering:
  `test_v053_continuous_runtime.py`, `test_v053_continuous_world.py`,
  `test_v054_embodied_grounding.py`, `test_v055_language_closure.py`, and
  `test_v063_assembly_cognit_bridge.py`.
- Host batching: `test_v063_assembly_cognit_bridge.py`,
  `test_v065_neural_behavior.py`, and `test_v066_long_life.py`.
- Pending scheduler/cognition/planner/language/neural/bridge continuation:
  `test_v053_cognition_frontier.py`, `test_v053_continuous_runtime.py`,
  `test_v055_language_sequence.py`, `test_v057_language_requests.py`, and
  `test_v063_assembly_cognit_bridge.py`.
- `.sebrain`, `.seworld`, checksum/version migration, native graph v3 and
  capacity restore: `test_v051_persistence.py`, `test_v052_authority.py`,
  `test_v052_native_engine.py`, `test_v053_continuous_world.py`,
  `test_v063_assembly_cognit_bridge.py`, and `test_v066_long_life.py`.
- Observer OFF/ON trajectory and persistence inertness:
  `test_live_native_observer.py`, `test_brain_observer.py`, and CTest observer
  preparation. PASS.
- Language grounding, ordering, composition, relations, requests, permutation,
  persistence and hash determinism: v0.5.4-v0.5.7 groups. PASS.
- Neural physics, same-time aggregation, pre-timestamp STDP traces,
  homeostasis, Assemblies, one-way bridge, sensory transduction, ordinary
  planner participation and lifecycle: v0.6.0-v0.6.6 groups. PASS.

The v0.7.4 architecture suite passed all six guards. Manual scope review
confirmed its globs include both current `neurodynamic*.cpp` files, all current
`native_brain*.cpp` files, both `language*.py` files, observer source/header,
and the complete current extracted type/data-module list. Coverage is complete
for the present v0.7.4 tree; future automatic discovery of new type modules is
explicitly deferred to v0.7.6.

## Long-life audit

The automated v0.6.6 suite passed 23 tests. The existing manual runner completed
1,000 WorldTime in ten validated windows (548.725 host seconds):

| Metric | Final/peak |
|---|---:|
| actions | 6,666 |
| scheduler events | 54,363 |
| scheduler queue / lifetime peak | 2 / 3 |
| Cognits | 593 |
| Relations | 16,384 (global cap) |
| Assemblies | 87 |
| bounded Assembly candidates | 32 |
| bridge log | 256 (cap) |
| neural events | 95,129 |
| planner cycles / pending work | 25,329 / 0 |
| full graph sync calls | 0 |

Relations reached exactly 16,384 by WorldTime 300 and stayed there through
WorldTime 1,000 while actions, scheduler/neural events, cognition and Assemblies
continued updating. Every window passed `validate_long_life_state`: no NaN/Inf,
negative/invalid counters, past scheduler work, capacity overflow or runaway.
Repeated save/load near saturation is separately covered by
`test_v066_long_life.py`.

## Performance comparison

Same machine, Python, seed, settings and Release compiler were used. v0.7.0 was
built in a detached worktree; current used its Release build.

| Canonical end-to-end workload | Runs | Median | Range | Current delta |
|---|---:|---:|---:|---:|
| v0.7.0 `e97a7b7` | 7 | 0.282944 s | 0.276895-0.293184 s | baseline |
| current `2f9c0e3` | 7 | 0.278439 s | 0.272324-0.289722 s | -1.59% |

The difference is below 5% and classified as wall-clock noise. More
importantly, every semantic/work counter listed in the determinism section was
identical.

The three-run native benchmark had identical workload sizes and exact
logical/reserved bytes. Representative medians:

| Native case | v0.7.0 | current | Delta |
|---|---:|---:|---:|
| 100k Cognits / 400k Relations / frontier 1000 | 3255.95 us | 3430.83 us | +5.37% |
| 1m Cognits / 4m Relations / frontier 1000 | 4132.91 us | 4229.43 us | +2.34% |
| growing 100k / 6.4m Relations | 248.67 us | 243.99 us | -1.88% |

The isolated +5.37% row was investigated: adjacent sizes move in both
directions, the larger case is +2.34%, the dense growing case is faster, memory
counts are exact, and end-to-end runs are -1.59%. It is classified as noisy
measurement, not a repeatable unexplained regression. No optimization was made.

## Source audit and deviations

- v0.7.1 (`b2bf4c9`): readability/comments/docs; no intended behavior change.
- v0.7.2 (`efd057f`): Python responsibility extraction and compatibility
  re-exports; no duplicate state authority.
- v0.7.3 (`faf800a`): C++ member implementations split by translation unit;
  stable classes and ABI retained.
- v0.7.4 (`2f9c0e3`): tests, guards, verification tooling, documentation and
  ignore policy only.

Observed differences were structural source layout, additional tests/tooling,
documentation, ignored generated patterns, and noisy wall time. Each is an
expected non-semantic structural or measurement difference. Semantic/runtime
deviations: **none**. Unexplained feature creep: **none**. Blockers: **none**.

## Explicit audit limits

- The default 50,000-WorldTime manual experiment was not run. The measured
  1,000-WorldTime run already took 548.725 s and included 700 WorldTime after
  relation-cap saturation; the repository contract makes the extended manual
  workload conditional on practicality.
- There is no archived external `.sebrain`/`.seworld` binary fixture in the
  repository. Compatibility evidence is the existing schema-migration,
  checksum, native v3, roundtrip and exact-continuation tests.

Neither limit hides a failed required automated gate. v0.8 implementation: NO.
