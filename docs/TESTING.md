# Testing and Repository Verification

**Current implementation: v0.8.3 opt-in learned trajectory valuation; historical audit below.**

v0.8.3 stabilization adds `tests/test_brain_sensor_contract.py`, structured
preflight/metadata guards, a controlled native physical vertical regression,
and coverage of competing-bin marginal normalization. Stabilization verification on 2026-10-01:
**516 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`.
Native Release observer build, import/headless smokes and `git diff --check`
passed. The required targeted suite plus brain compatibility tests passed
**89 tests**:

```
python -m pytest -q tests/test_v081_persistence_security.py tests/test_v081_consumables.py tests/test_v082_interoception.py tests/test_v083_homeostatic_valuation.py tests/test_architecture_boundaries.py tests/test_brain_sensor_contract.py
```

Earlier acceptance counts below are explicitly historical.

The focused tests are `tests/test_v082_interoception.py` and
`tests/test_v083_homeostatic_valuation.py`. Full verification is
`python tools/verify.py --full`; its outcome is separate from the historical
v0.7.5 audit count below.

Historical initial v0.8.3 full verification on 2026-10-01: **491 pytest passed; CTest Release 2/2 passed**.
`python tools/verify.py --full` completed successfully, including native observer
build, import/headless smokes, full pytest and CTest.

Historical initial v0.8.3 targeted verification: 64 passed across v0.8.1 persistence/security, consumables,
v0.8.2 interoception, v0.8.3 valuation and architecture boundaries. Historical
pre-v0.8.3 full run: 465 pytest passed; CTest Release 2/2 passed.

Полный v0.7.5 audit: `422` pytest PASS, CTest Release `2/2` PASS, все `17`
version groups v0.2–v0.6.6 PASS. Подробности:
[`V0_7_5_REGRESSION_AUDIT.md`](V0_7_5_REGRESSION_AUDIT.md).

## Standard commands

`requirements.txt` is the flexible, human-facing setup surface. For a
reproducible audit environment use `python -m pip install -r
requirements-lock.txt`; update that lock intentionally, together with a full
verification run.

```powershell
python tools/verify.py
python tools/verify.py --fast
python tools/verify.py --full
```

Default — `--fast`: production import, zero-second headless smoke,
entrypoint/architecture/tooling tests, Release native build и CTest.

`--full` выполняет те же smokes, полный pytest suite ровно один раз, Release
build и CTest. Оба режима fail-fast, используют активный Python interpreter,
ничего не устанавливают и не требуют network после локального setup.

Если `cpp/build/CMakeCache.txt` отсутствует, verify сначала выполняет CMake
configure. На Windows используется `-A x64`.

`git diff --check` и clean tree — freeze/review gates, но не обязательны для
обычного developer run.

## Test taxonomy

| Files | Primary category | Contract |
|---|---|---|
| `test_cognits.py`, `test_relations.py`, `test_wave.py`, `test_world.py`, `test_perception.py` | unit | core graph/World/perception |
| `test_simulation.py`, `test_main_entrypoint.py` | integration | composed runtime / CLI |
| observer tests | integration / architecture | snapshot-only observer |
| `test_v02*.py` | version acceptance | v0.2 |
| `test_v03*.py` | version acceptance | v0.3 |
| `test_v04*.py` | version acceptance | v0.4 |
| `test_v051*.py` | frozen acceptance / oracle | v0.5.1 |
| `test_v052*.py` | native parity / acceptance | v0.5.2 |
| `test_v053*.py` | continuous runtime regression | v0.5.3 |
| `test_v054*.py` | grounding / architecture | v0.5.4 |
| `test_v055*.py` | language sequence/closure | v0.5.5 |
| `test_v056*.py` | relational language | v0.5.6 |
| `test_v057*.py` | language requests | v0.5.7 |
| `test_v060*.py` | native neural | v0.6.0 |
| `test_v061*.py` | native neural | v0.6.1 STDP/homeostasis |
| `test_v062*.py` | native neural | v0.6.2 Assemblies |
| `test_v063*.py` | native parity/persistence | v0.6.3 bridge |
| `test_v064*.py` | integration | v0.6.4 sensory transduction |
| `test_v065*.py` | architecture/integration | v0.6.5 neural behavior |
| `test_v066*.py` | long-life/performance regression | v0.6.6 |
| `test_v080*.py` | physiology unit/integration | Historical v0.8.0 |
| `test_v081*.py` | security, resource parity and continuation | v0.8.1 |
| `test_architecture_boundaries.py` | architecture | dependency/causal guards |
| `test_verify_tool.py` | tooling unit | verify modes/failure propagation |

C++ `se_equivalence` использует `cpp/fixtures/oracle_v051.txt`.
`se_observer_tests` защищает observer preparation. Поэтому CTest обязателен в
дополнение к pytest.

## v0.7.5 acceptance matrix

| Contract | Tests | Result |
|---|---:|---|
| v0.2 | 6 | PASS |
| v0.3 | 14 | PASS |
| v0.4 | 10 | PASS |
| v0.5.1 | 48 | PASS |
| v0.5.2 | 41 | PASS |
| v0.5.3 | 97 | PASS |
| v0.5.4 | 25 | PASS |
| v0.5.5 | 18 | PASS |
| v0.5.6 | 9 | PASS |
| v0.5.7 | 12 | PASS |
| v0.6.0 | 11 | PASS |
| v0.6.1 | 10 | PASS |
| v0.6.2 | 9 | PASS |
| v0.6.3 | 20 | PASS |
| v0.6.4 | 13 | PASS |
| v0.6.5 | 10 | PASS |
| v0.6.6 | 23 | PASS |

Version groups = `376` tests; полный suite = `422`, включая `46`
non-versioned/core/tooling tests.

v0.8.0 добавляет `9` tests в `test_v080_homeostasis.py`; полный suite = `431`.
Они защищают WorldTime determinism, bounds/finite state, action cost/brownout,
world-consequence hooks, tension, exact persistence/config continuation и
immutable core/planner/observer projections.

The v0.8.1 audit adds resource authority/parity, deterministic scheduler
continuation, secure RNG and malformed container tests. The full suite is
`456` pytest tests; Release CTest is `2/2`. Resource spawning is opt-in, so
the v0.8.0 trajectory remains the disabled-resource baseline.

## Architecture guards

Централизованные guards дополняют historical assertions:

- data/type layers не импортируют `SyntheticEntityCore`;
- `language*.py` не получает direct `ActionType`/World action policy;
- `neurodynamic*.cpp` и public facade header не получают Action/Goal/reward
  semantics;
- observer source/header остаются snapshot-only;
- `native_brain*.cpp` не получает reverse Cognit -> micro injection;
- `full_graph_sync_calls` имеет только zero initialization и не имеет increment
  path.

Data/type guard автоматически обнаруживает `consciousness/*_types.py` и
`simulation/*_types.py`; будущий `physiology_types.py` не может обойти invariant.
Pure helpers без naming convention добавляются в короткий explicit список.

## Determinism contract

Canonical seed: `6607`.

```text
digest
7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f

actions         79
scheduler       655
queue peak      3
Cognits         27
Relations       162
planner cycles  294
FFI calls       2668
Assemblies      6
```

`PYTHONHASHSEED=1` и `777` должны совпадать. `full_graph_sync_calls` должен быть
нулём.

## Persistence and continuation coverage

Обязательные contracts:

- `.sebrain v6`;
- `.seworld v10` with interoception; v8 historical baseline (migration remains covered);
- native graph v3;
- checksum/version validation;
- pending scheduler continuation;
- cognition/planner frontier continuation;
- pending language continuation;
- neural queue continuation;
- bridge cursor/recognition episode continuation;
- host-batching invariance.

В репозитории нет отдельного внешнего archival binary fixture старых
`.sebrain/.seworld`; это documented audit limitation, а не автоматический claim
о byte-level compatibility со всеми внешними файлами.

## Manual performance and soak

`experiments/` — research/reproducibility workloads, не unit tests.

Основной extended runner:

```powershell
python -m experiments.v066_long_life
```

v0.7.5 фактически прогнал 1,000 WorldTime: Relation cap `16,384` был достигнут и
система продолжила bounded execution. 50,000-WorldTime run не выполнялся.

Historical benchmark/profile/lockstep/fixture-export scripts остаются manual,
потому что их стоимость/выход не подходят для каждого edit.

## Repository artifacts

- **Source:** Python packages, `cpp/src`, `cpp/include`, `main.py`, `tools/`.
- **Canonical fixtures:** `cpp/fixtures/oracle_v051.txt` и test-owned fixtures.
- **Historical reproducibility:** tracked `runs/v052-*`, `.prof`, root `.pstats`.
- **Documentation:** current living docs + frozen audit/contract + historical
  reports.
- **Generated local:** caches, build trees, binaries, coverage, temporary
  snapshots, local profiles.

`.gitignore` исключает новые generated instances. Уже tracked historical
artifacts остаются tracked; не удаляйте их только ради hygiene.

## Freeze rule

Перед milestone freeze:

```powershell
python tools/verify.py --full
git diff --check
git status --short
```

Если изменение касается ordering/persistence/native wire, дополнительно
запускаются соответствующие targeted tests/manual audit workloads до freeze.
