# Testing and repository verification

This is the developer-facing index for the test suite. Historical versioned
files keep their names and locations because those paths are part of the frozen
acceptance record.

## Standard commands

```powershell
python tools/verify.py
python tools/verify.py --fast
python tools/verify.py --full
```

The default is `--fast`: import and zero-second production smokes, entrypoint,
architecture/tooling tests, Release native build, and Release CTest. `--full`
runs the same smokes, the complete pytest suite exactly once, Release build,
and CTest. Both modes are fail-fast, use the active Python interpreter, run
from the repository root, install nothing, and require no network access once
the documented dependencies and native build inputs are present. A missing
`cpp/build/CMakeCache.txt` causes a normal local CMake configure first.

`git diff --check` and a clean tree are freeze/review checks, not requirements
for an ordinary developer verification run.

## Taxonomy and inventory

Categories describe intent, not directory layout. Many integration tests also
serve as regressions; the primary classification is listed here.

| Files | Primary category | Contract protected |
|---|---|---|
| `test_cognits.py`, `test_relations.py`, `test_wave.py`, `test_world.py`, `test_perception.py` | unit | core records, graph operations, wave, World and perception |
| `test_simulation.py`, `test_main_entrypoint.py` | integration | composed runtime and production CLI |
| `test_brain_observer.py`, `test_live_native_observer.py`, `test_native_render_snapshot.py` | integration / architecture boundary | immutable observer snapshot path and native rendering |
| `test_v02_dynamics.py` | version acceptance / reference | v0.2 dynamics |
| `test_v03_choice.py`, `test_v03_composites.py`, `test_v03_loop.py`, `test_v03_perception.py` | version acceptance / reference | v0.3 choice, composition and loop |
| `test_v04_relations.py`, `test_v04_scheduler.py`, `test_v04_world.py` | version acceptance / regression | v0.4 relation, scheduling and World behavior |
| `test_v051_*.py` (11 files) | frozen version acceptance / oracle | v0.5.1 belief, causal, memory, planning, multi-entity, persistence and vision contracts |
| `test_v052_native_engine.py`, `test_v052_native_world.py`, `test_v052_native_world_parity.py` | native parity / oracle | Python/native numeric and World equivalence |
| `test_v052_authority.py`, `test_v052_memory_index.py` | architecture boundary / regression | native authority and bounded memory indexing |
| `test_v053_*.py` (5 files) | version acceptance / regression | continuous runtime, cognition frontier, World and elapsed-time corrections |
| `test_v054_*.py` | version acceptance / architecture boundary | embodied grounding and recursive language anti-semantic guard |
| `test_v055_*.py`, `test_v056_relational_language.py`, `test_v057_language_requests.py` | version acceptance / integration | ordered, relational and request grounding |
| `test_v060_neurodynamic_substrate.py` | version acceptance / native | micro-neural event physics |
| `test_v061_local_plasticity.py` | version acceptance / native | STDP, traces and homeostasis |
| `test_v062_assemblies.py` | version acceptance / native | Assembly evidence and recognition |
| `test_v063_assembly_cognit_bridge.py` | version acceptance / native parity | one-way bridge, cursor and persistence |
| `test_v064_sensory_transduction.py` | version acceptance / integration | non-semantic embodied neural input |
| `test_v065_neural_behavior.py` | version acceptance / architecture boundary | ordinary planner participation and neural anti-semantic guard |
| `test_v066_long_life.py` | version acceptance / performance/soak regression | boundedness, determinism, batching, lifecycle and save/load continuation |
| `test_architecture_boundaries.py` | architecture boundary | recursive dependency and causal-direction guards |
| `test_verify_tool.py` | tooling unit | mode selection, configure plan and failure propagation |

The C++ `se_equivalence` test is a native oracle against
`cpp/fixtures/oracle_v051.txt`; `se_observer_tests` protects read-only observer
preparation. CTest is therefore required in addition to pytest.

## Architecture guards

The centralized guards supplement, rather than replace, historical assertions.
They recursively cover extracted modules so moving forbidden code cannot bypass
the check:

- data/type layers do not import `SyntheticEntityCore`;
- `language*.py` has no direct `ActionType`/World action dependency;
- every `neurodynamic*.cpp` file and its public facade header has no action,
  Goal, reward-label or named-action semantics;
- observer implementation/header depend on value-owned snapshots, not World,
  scheduler or native brain mutation APIs;
- every `native_brain*.cpp` file has no Cognit-to-micro injection path;
- `full_graph_sync_calls` has only its zero initialization and no increment path.

Guard failures name the file or forbidden boundary. AST import/name inspection
is used where formatting-independent structure matters; narrow C++ token checks
are limited to the subsystem that owns the invariant.

## Manual performance and soak work

`experiments/` contains research/reproducibility workloads, not unit tests.
Notably, `python -m experiments.v066_long_life` runs the extended long-life
workload. The `v052_*benchmark.py`, profiling, lockstep and fixture-export
programs support historical native cutover measurements. They are manual
because their cost or output is unsuitable for every edit; run the relevant
workload before a release that changes its protected runtime area.

## Repository artifacts

- Source: Python packages, `cpp/src`, `cpp/include`, `main.py` and `tools`.
- Canonical fixtures: `cpp/fixtures/oracle_v051.txt` and test-owned fixtures.
- Historical reproducibility artifacts: tracked `runs/v052-*`, `.prof` and
  root `.pstats` files. These remain intentionally preserved.
- Documentation: root design/status documents and `docs/`.
- Generated local artifacts: caches, CMake build trees, binaries, coverage,
  profiles, temporary snapshots and `.sebrain`/`.seworld` runs; `.gitignore`
  excludes new instances.

Tracked historical artifacts remain tracked even when their extension is now
ignored. Do not delete or regenerate them as repository hygiene. A new artifact
belongs in Git only when it is a canonical fixture or documented reproducibility
record.
