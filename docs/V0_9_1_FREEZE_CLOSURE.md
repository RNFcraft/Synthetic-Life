# v0.9.1 stabilization / freeze closure

Verification date: 2026-10-02, Windows x64, Python 3.12, MSVC Release.

## Repository and version

- Base HEAD: `19e558ecd5a029d08a64ddc8de973f24235dc086`.
- Freeze implementation commit: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65`.
- Freeze base HEAD for v0.9.2: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65`; v0.9.2 implementation follows from this frozen base.
- Branch: `main`. CMake/project version remains **0.9.1**.
- v0.9.1: **DONE / FROZEN**. v0.9.2 First Survival-Learning Proof: **PLANNED**.
- Existing user whitespace edit to `entity_count` and the prior shader correction were preserved.

## Historical baseline and presets

`Settings()` again uses **25 initial / 25 maximum objects**, including default GUI startup.
Opening the observer or Settings dialog never selects or applies a sparse configuration.
A literal canonical-seed regression freezes body position (6,14), the complete initial world
(including all 25 object positions), and the initial RNG state for seed 12345. Expected digests
are constants, not derived dynamically from current defaults.

| Built-in preset | Initial objects | Maximum objects | Other causal fields |
|---|---:|---:|---|
| Classic Baseline | 25 | 25 | Engine defaults |
| Workbench Sparse | 3 | 150 | Engine defaults |
| Empty Experiment | 0 | 150 | Engine defaults |

Current restores the running episode's editable configuration into the draft. Presets and reset
change only the draft; the chosen seed remains explicit. Current also preserves noneditable episode
configuration when constructing a new world. Built-in presets reset noneditable fields to engine defaults.

## Settings / New World

A compact toolbar button opens a desktop dialog, with bounded fields and scrollable advanced controls.
The dialog separates **Causal - requires New World** from **Workbench - applies immediately**.

- World: dimensions, initial/max objects, seed; advanced entity count and perception radius.
- Resources: existing spawning flag, interval, live-resource cap and nutrient/hydration payloads.
- Physiology: initial stores; advanced maximum stores, targets, basal body/brain/hydration rates,
  digestion rate/efficiency and physical movement/interaction costs.
- Cognition: interoception/bins, homeostatic valuation, delayed prediction; advanced planning horizon,
  beam width, passive depth, prediction horizon, discount and temporal probability floor.
- Workbench: UI scale, grid, tooltips and brain edge visual budget. These are session-only presentation
  values, have no simulation owner, and are not written to any artifact.

Buttons: Reset to Engine Defaults, Cancel, Apply & New World. A learned/advanced episode requires
compact confirmation before sending the reset command. Config errors appear in Settings or Status,
never Dialogue. There is no live causal-settings application path.

## Runtime replacement and observer safety

The UI sends `CREATE_NEW_WORLD` with a detached `WorkbenchNewWorldConfig` of bounded primitives.
The generic submit API rejects this command without an explicit payload. FFI rejects primitive type
coercion; Python validates exact fields, seed 0..2^63-1, standard scenario Settings limits, world area,
object capacity, physiology and planning bounds before constructing `ContinuousRuntime(seed, settings)`.
Invalid input preserves the current episode.

Main owns replacement: stop/join render thread, close old command channel, reconnect shared snapshot
sources, attach new status/command channels, publish fresh snapshots and restart the observer.
The observer object is reused with a controlled SDL/OpenGL window restart. Value-owned shared channels
keep snapshots alive without retaining or dereferencing the old native World/brain. Old commands after
reset are discarded. Workbench preferences survive restart; selections and camera offsets are reset.

New runtime starts paused at WorldTime 0, event sequence 0, with the selected seed, fresh RNG and fresh
cognition. Cognits/Relations, plans, old WorldTime and episode inputs are not transferred. Ordinary initial
sensory observation remains scheduled through the production path. The main loop returns the replacement;
saving and Ctrl+C reporting use the active runtime. CREATE_NEW_WORLD is a host operation, never an
EXTERNAL_INPUT or scheduler event. Same draft/seed matches direct production construction.

## Scenario export and artifact hardening

Sparse New World -> Save Scenario -> headless reload preserves effective 3/150 Settings, seed,
physiology and physical geometry. Export contains no preset identity. Two independent replays have
identical causal digests. Scenarios remain normalized initial conditions with fresh RNG; they do not
continue the RNG state consumed during procedural geometry generation. Exact continuation remains
`.seworld`'s purpose.

Generic container inspection/loading validates all section ranges and checksums, including unknown
optional sections, in table order. It rejects overlaps, gaps, reordered ranges and trailing bytes.
Validation and decoding use the same byte buffer. The writer and all existing schemas are unchanged:
brain, world, scenario and manifest version 1 retain compatibility with canonical historical artifacts.

Scenario validation checks free/held object IDs against remaining ordinary/resource capacity and reserves
uint32 sentinel space (`max_id + max(1, remaining_capacity) < UINT32_MAX`). Near-exhausted IDs fail closed;
`scenarios/examples/workbench_smoke.sescenario` still loads. This is an admission guard, not an engine
redesign or a claim of unlimited identifier reuse over arbitrarily long episodes.

## Actual verification

| Executed verification | Result |
|---|---|
| `python tools/verify.py --full` | PASS; **711 passed**, Release build and CTest **2/2** |
| Six targeted Python suites | **217 passed** |
| Observer ON native CTest | **2/2 passed** |
| Observer OFF isolated Release build | PASS; deployed separately from the production module |
| Observer OFF targeted Python | **103 passed, 2 GUI tests deselected** |
| Observer OFF native CTest | **1/1 passed** |
| `python main.py --headless --seconds 0 --seed 12345` | PASS; historical defaults |
| `git diff --check` | PASS |

Targeted suites actually executed: `test_main_entrypoint.py`, `test_v090_workbench.py`,
`test_v091_scenarios.py`, `test_v084_delayed_homeostatic_learning.py`,
`test_architecture_boundaries.py`, `test_v091_stabilization.py`.

Native ImGui input tests open Settings, select Workbench Sparse through the combo, verify 3/150,
press Apply, and verify the command payload. A learned episode requires confirmation before submission.
Native preference changes emit no commands and preserve detached physical time/sequence values.
Python integration verifies real observer reconnection, rendered frames, distinct new channels,
closed old channel, fresh cognition and main-loop ownership. Scenario/brain/world continuation,
hashseed determinism and full_graph_sync_calls == 0 checks pass in the full suite.

## Visual verification and limits

[Settings dialog, 1440x900](settings-new-world-1440x900.png) was captured by the observer demo and inspected.
All five tab names, initial/max object fields, seed and footer buttons are readable at this machine's
high DPI. The dialog retains the existing Workbench palette, compact controls and desktop styling.
The demo supports `--settings-popup 1` for reproducible captures. Existing layout tests also cover
1100x700 and 1920x1080; additional Settings screenshots at those sizes were not captured.

Preferences and drafts are session-only. There is no profile manager, automatic seed generation,
direct Save Configuration button or implicit learned-brain reuse. Controlled observer restart can
briefly recreate the window. Explicit scenario + `.sebrain` remains the durable knowledge workflow.

## Changed files

- `ARCHITECTURE.md`
- `CURRENT_STATUS.md`
- `README.md`
- `ROADMAP.md`
- `config/settings.py`
- `cpp/CMakeLists.txt`
- `cpp/include/se/observer.hpp`
- `cpp/include/se/workbench_commands.hpp`
- `cpp/include/se/workbench_snapshot.hpp`
- `cpp/include/se/workbench_ui.hpp`
- `cpp/src/bindings.cpp`
- `cpp/src/bindings_workbench.cpp`
- `cpp/src/observer.cpp`
- `cpp/src/workbench_brain_gpu.cpp`
- `cpp/src/workbench_brain_view.cpp`
- `cpp/src/workbench_ui.cpp`
- `cpp/src/workbench_world_view.cpp`
- `cpp/tests/observer.cpp`
- `cpp/tests/observer_demo.cpp`
- `docs/V0_9_1_REPRODUCIBLE_SCENARIOS.md`
- `main.py`
- `persistence/container.py`
- `simulation/scenario.py`
- `simulation/workbench.py`
- `cpp/include/se/workbench_settings.hpp`
- `cpp/src/workbench_settings_ui.cpp`
- `docs/settings-new-world-1440x900.png`
- `simulation/workbench_settings.py`
- `tests/test_v091_stabilization.py`
- `docs/V0_9_1_FREEZE_CLOSURE.md`

## Milestone boundary

v0.9.1 remains the current version. The historical engine baseline is again 25 initial objects /
25 maximum objects. The 3 / 150 configuration is preserved as an explicit Workbench Sparse preset,
not as a hidden change to the default causal trajectory.

Causal Settings are immutable during an episode. Applying a different causal configuration constructs
a fresh runtime at WorldTime 0. Workbench-only presentation settings may change live because they are
not simulation inputs.

No reward, survival curriculum, semantic Food policy, planner shortcut, or scenario/preset-to-cognition
path was introduced. No cognitive algorithms were changed. v0.9.2 remains the first survival-learning
proof milestone: controlled fresh-vs-experienced survival experiments, success metrics and multi-seed
research remain planned rather than implemented here.
