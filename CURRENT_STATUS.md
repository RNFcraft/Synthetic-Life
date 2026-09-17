# Synthetic-Life — Current Status

## v0.7.6 — ARCHITECTURE FREEZE — FROZEN

The v0.7 cleanup line is complete. The accepted production path, ownership,
causal boundaries, time/ID domains, persistence formats, compatibility paths,
and reference oracles are frozen as the baseline for future research work.
v0.7.6 changed no runtime semantics, numeric equations, scheduler ordering,
persistence schema, or pybind wire shape.

## Acceptance snapshot

```text
pytest                    422 passed
CTest Release             2/2 passed
canonical digest          7d80bffa82cfbabf8d11373883d03056b26b27eb53a4cbe9246a666e079fbb0f
actions                    79
scheduler events          655
queue peak                  3
Cognits                    27
Relations                 162
planner cycles            294
FFI calls                2668
Assemblies                   6
full_graph_sync_calls        0
```

`PYTHONHASHSEED=1` and `777` produce the same digest and counters. A separate
Windows clean clone, fresh virtual environment, fresh Release native build,
CTest, full pytest, import smoke, and zero-second production smoke all pass.

## Frozen architecture

- Python owns semantic cognition, memory/planner/language policy, and the
  cognition frontier.
- C++ owns the authoritative numeric Cognit/Relation graph, physical World,
  scheduler, neurodynamic substrate, Assemblies, and one-way bridge.
- Python graph/World and discrete `Simulation.step()` remain reference and
  compatibility surfaces; `ui/` remains legacy/unsupported/non-production.
- Persistence remains `.sebrain v6`, `.seworld v7`, and native graph v3.

Full evidence: [`docs/V0_7_6_ARCHITECTURE_FREEZE.md`](docs/V0_7_6_ARCHITECTURE_FREEZE.md).

## Known limitations

- No separately archived external binary fixtures exist for old
  `.sebrain`/`.seworld` versions; migrations are protected by executable tests.
- The measured long-life audit is 1,000 WorldTime; the proposed 50,000 soak was
  not run because the shorter run took 548.725 seconds.
- The Python UI is retained as an unsupported debug tool and is not installed
  by production requirements.

## Next work

v0.8 — Homeostatic Motivation and First Survival Learning — is **PLANNED**, not
implemented. Its design is recorded in [`ROADMAP.md`](ROADMAP.md).
