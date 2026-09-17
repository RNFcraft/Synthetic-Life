# v0.7.6 Architecture Freeze

## Verdict

**FROZEN.** v0.7.6 closes the v0.7 cleanup line without changing behavior,
numeric equations, scheduler order, persistence formats, ABI, or wire layouts.
It is the architecture baseline for v0.8; no v0.8 capability is implemented.

## Baselines and changes

- behavioral oracle: `e97a7b769c0742300bb007d0ad132337de41253d`;
- frozen regression audit: `26b1308f3e61ca1d9fe573e693748021831a816d`;
- documentation-normalized starting HEAD: `7c0e16a48bb7e74695d35db4447fefea32c45e6e`;
- candidate guard commit: `97b3e0f55d4495a07a22248e27741c427785c6c8`.

The intervening `26b1308..7c0e16a` diff is documentation-only. The only code
change in v0.7.6 makes the data-layer architecture test discover all current
and future `consciousness/*_types.py` and `simulation/*_types.py` modules,
while explicitly including the pure `memory_matching.py` helper. This closes
the known `physiology_types.py` escape route. No source file or adapter was
removed: no candidate met the complete dead-code proof.

## Repository classification

| Category | Paths / surfaces |
|---|---|
| PRODUCTION | `main.py`, `simulation/runtime.py`, native `Simulation`, `NativeWorldFacade`, `SyntheticEntityCore`, `NativeGraphBackend`, C++ engine/world/scheduler/neurodynamic sources |
| PUBLIC | CLI in `main.py`, documented runtime entrypoints, public C++ headers and supported native bindings |
| COMPATIBILITY | package re-exports, discrete `Simulation.step()`, Python/native facades, supported persistence migrations |
| INTERNAL | `*_types.py`, matching/helpers, `cpp/src`, private binding declarations and caches |
| REFERENCE / ORACLE | Python graph and World, differential/parity paths, historical acceptance implementations |
| LEGACY / UNSUPPORTED | `ui/` Python debug renderer; non-production and no Pygame production dependency |
| TEST | `tests/`, `cpp/tests/` |
| EXPERIMENT | `experiments/` and experiment entrypoints |
| CANONICAL FIXTURE | tracked persistence/parity fixtures used by tests |
| HISTORICAL EVIDENCE | tracked reports, result JSON/JSONL, snapshots and profiles retained for reproducibility |
| DOCUMENTATION | living root documents and `docs/`; frozen/historical roles follow `docs/DOCUMENTATION.md` |
| GENERATED / LOCAL | build trees, native binaries, caches, coverage, temporary snapshots and local profiles; ignored, never evidence by default |

The verified production path is:

```text
main.py -> ContinuousRuntime -> Simulation(backend="native")
  -> NativeWorldFacade -> C++ WorldRuntime
  -> SyntheticEntityCore -> NativeGraphBackend -> C++ NativeBrainEngine
  -> NeurodynamicSubstrate -> EventScheduler
```

`NativeObserver` is interactive and read-only. Search of actual callers shows
that `Simulation.step()` is still used by tests, experiments, multi-simulation,
and the legacy renderer. Python graph/World participate in parity and reference
tests. These surfaces therefore remain intentionally available.

## API and dependency audit

Public, compatibility, internal, reference, and legacy surfaces above are
classification boundaries, not a promotion of internal symbols. No import
path or `__all__` was changed. Compatibility adapters retained are the Python
graph/World, discrete Simulation API, extracted-module package re-exports, and
native facades; their callers and frozen contracts make removal unsafe.

An AST import-graph audit found no forbidden production dependency cycle. The
apparent `consciousness` component is benign package initialization: the
package re-exports `SyntheticEntityCore`, while `core` lazily imports the
native backend inside native construction, and the backend imports the native
extension facade. It does not create parallel authority or a data-layer to
facade edge. Existing pattern-based language, neurodynamic, native-brain,
observer, and full-graph-sync guards already cover newly added relevant files,
so they were not rewritten.

## Persistence audit

Accepted surfaces remain `.sebrain v6`, `.seworld v7`, and native graph v3.
Tests cover outer magic/version/checksum, required-section validation, atomic
replacement, migrations, round trips, and exact continuation. Restore includes
pending scheduler events, cognition frontier, planner/session, language
frontier, neural pending state, and Assembly bridge cursor/episodes. No version,
field order, module path, restore order, or wire representation changed.

## Documentation and artifact audit

Living documents answer production ownership, semantic ownership, World,
memory/planner/language location, reference and legacy status, ID/time domains,
persistence, build/verification, subsystem-extension rules, prohibited
boundaries, and the planned v0.8 scope. Frozen evidence and historical reports
remain distinct. All 19 tracked Markdown files were checked: zero broken local
links. Generated SDL documentation inside local build trees is outside the
tracked documentation set. Tracked experiment results, snapshots, and profiles
remain historical reproducibility evidence; generated local equivalents remain
ignored artifacts.

## Clean-clone and final verification

Candidate `97b3e0f` was cloned outside the working repository on Windows. Before
building it contained no build tree, native module, SDL build, cache, or
untracked snapshot. A fresh `.venv` installed `requirements.txt`; CMake/MSVC
configured and built Release with the observer enabled, producing its own
native module. `tools/verify.py --full` then passed:

```text
production import / zero-second smoke  PASS
pytest                                 422 passed in 38.01s
Release build                          PASS
CTest                                  2/2 passed in 0.15s
```

The main working tree full gate also passes. The canonical workload with seed
`6607` is identical for `PYTHONHASHSEED=1` and `777`:

```text
digest                 7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f
actions                79
scheduler events       655
queue peak               3
Cognits                27
Relations             162
planner cycles        294
FFI calls            2668
Assemblies               6
full_graph_sync_calls    0
```

## Known limitations

- Old persistence migrations have executable fixtures/tests but no separately
  archived external binary fixture collection.
- The bounded soak evidence is 1,000 WorldTime, not 50,000; the former required
  548.725 seconds.
- `ui/` remains useful for legacy/debug work but is unsupported and outside the
  production dependency set.

## Contract for every new subsystem

Before behavior code, define: **STATE OWNER, INPUTS, OUTPUTS, CAUSAL DIRECTION,
TIME DOMAIN, ID DOMAIN, PERSISTENCE RESPONSIBILITY, PUBLIC/INTERNAL API,
BOUNDEDNESS, TEST ORACLE, and ARCHITECTURE GUARDS**. State has one authoritative
owner; a second representation must be a documented snapshot, cache, or
reference. Dependencies stay explicit—no global service registry, giant
context, mutable singleton, or new God Object. Wall clock is never simulated
causal time. State that affects future behavior is persisted or reconstructed
by a proven exact deterministic rule. Every new causal boundary gets a
regression test, and structurally bypassable isolation rules get a guard.
