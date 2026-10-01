# v0.9.0 — Experimental Workbench & Observer Redesign

Historical milestone contract. Current project v0.9.1 adds
[reproducible scenarios](V0_9_1_REPRODUCIBLE_SCENARIOS.md) and stabilization:
separate dialogue/editor notices, compact Scenario popup and host-only export.
READ remains snapshots; causal WRITE remains scheduler commands; host WRITE
exports a normalized scenario without changing causal state. Historical counts
below refer to the v0.9.0 acceptance, not current full-suite totals.

The cognitive foundation is v0.8.4 DONE / FROZEN. v0.9.0 provides a native
experimental desktop for inspecting and intervening in that organism. Survival
curriculum moved behind this prerequisite: v0.9.1 scenario infrastructure,
v0.9.2 first survival-learning proof, v0.9.3 long-run stability remain planned.

## Architecture and ownership

READ: World / Physiology / Cognition / Planner → detached immutable value
snapshots → native workbench. Existing world, brain and dialogue channels stay
latest-only; status uses its own atomic shared immutable value. Python status
records are frozen and native publication copies their values. No owner pointer
is handed to the renderer. Brain snapshots remain bounded and are produced by
the native numeric authority; `full_graph_sync_calls == 0` remains required.

WRITE: Human input → bounded thread-safe `WorkbenchCommandChannel` → host poll
→ runtime acceptance at current WorldTime → scheduler `EXTERNAL_INPUT` → native
World or existing language input → ordinary perception/cognition. UI threads
have no Python callbacks or GIL requirement. Native command IDs order the
producer queue; runtime command IDs and scheduler IDs order accepted inputs.
There is no render-frame or wall-clock timestamp in an accepted causal command.

The host and runtime own different state. Pause/Run/Step affect host advancement;
place/remove/send become explicit causal interventions. The queue never blocks:
256 commands, at most 4096 UTF-8 bytes per dialogue message, overflow rejects
without losing the typed input. Accepted runtime inboxes are also bounded.

`observer.cpp` owns SDL/OpenGL/ImGui lifecycle and thread shutdown. Layout,
World canvas, brain canvas/GPU cache, status and dialogue are separate sources.
`simulation/workbench.py` owns the runtime command adapter and status projection.
Cognition does not import or consume any workbench presentation records.

## Editor and physical presets

Select is local. Food places a resource with channel 1 and nutrient payload from
Settings; Water uses channel 2 and configured hydration payload. Orange squares
and cyan squares distinguish these human presets. Object places an ordinary
non-resource native object, within the configured generic-object capacity.
Erase removes a free native world object by ID. Held objects cannot be erased.
Native authority rejects invalid positions, occupancy, capacity and IDs before
mutation; rejected operations leave physical sequence and RNG unchanged.

UI "Food" ≠ cognitive FOOD concept. Payload-derived `PresentationKind` and raw
payload values are privileged observer metadata only. They never enter
`SensoryFrame`. The same numeric appearance with different/no nutritive payload
remains possible for counterfactual experiments. Existing interaction physics
consumes resources and delivers a consequence through Simulation.

One click issues one command; drag painting is not enabled. The world camera
supports fit, wheel zoom and middle/right drag pan. Selection, hover and cameras
are local presentation state. Entities are circles with an orientation marker;
held objects use their snapshot's actual preset color.

## Runtime control and transaction safety

Pause stops host advancement without advancing WorldTime or scheduling a
cognition input. Resume resets the host pacing anchor and continues the exact
frontier; elapsed paused wall time is not caught up. Step, while paused, executes
the next scheduler timestamp and all its zero-time continuations, using the
existing runaway guard. It is not a fixed number of milliseconds or a chosen
organism action.

Edits while paused drain only the current timestamp. A not-yet-committed
cognition or language transaction finishes before an intervention is applied.
A committed physical action remains queued; an edit does not commit a second
action. Its ordinary completion observation sees the changed world. Otherwise
successful world edits deduplicate an ordinary sensory-change event. Same-time
command, maintenance and action events keep normal scheduler insertion order.

## Inspectors

Physiology shows Energy/Nutrients/Hydration and configured maxima, Hunger,
Tension and derived zero-energy depletion. No separate Brownout behavior is
invented when the physiology owner does not export one. These are detached
physical debug values.
Interoception shows the last frame actually observed by cognition, its coarse
bins, target bins and observation WorldTime. It does not fabricate a new sensed
frame from the latest physical drift; disabled or not-yet-observed is explicit.

Cognition shows real live Cognits, Relations, active Cognits, micro Cognits,
micro Relations and consolidated Assemblies. The consolidated count comes from
a native read-only getter, not an assembly or graph export to Python. Active
Relation count is marked not exported rather than invented. Planner shows the last completed action,
actual plan actions/score/confidence, homeostatic component and confidence,
delayed prediction enablement, and available passive depth, elapsed predicted
delay and ambiguity. Unknown temporal evidence is labelled unavailable.
Runtime shows WorldTime, physical sequence, actions, pending events and UI FPS;
UI FPS is explicitly a wall-clock presentation metric.

Brain layout is a stable ID-derived function without simulation RNG. Bounded
node/edge geometry and dedicated GL buffers rebuild only when the snapshot or
panel size changes. Zoom/pan and relation filters are shader uniforms. Active
nodes are brighter, composites square, inactive edges restrained. Hover/select
shows ID, activity, confidence and last active tick. Graph editing is absent.

Dialogue is a bounded scrolling transcript of actual External/Entity lines.
No textual thoughts are manufactured. Send/Enter submits `SEND_DIALOGUE`; the
host converts whitespace-delimited text into explicit utterance tokens and
uses the existing language pipeline. Autoscroll follows new input only while
the reader is already at the bottom. Empty messages are ignored locally.

## Persistence and compatibility

Continuous worlds with accepted editor history use `.seworld` META v11.
`CONT.scheduler.workbench_commands` schema 1 stores the next runtime command ID,
pending inbox (kind, ID, acceptance WorldTime and payload), with its normal
`EXTERNAL_INPUT` scheduler events. Restore validates inbox/event correspondence.
Completed edits are already part of native World state. Old v8–v10 worlds load
with an empty editor inbox; command-free runs retain their existing version.
Semantic snapshot versions and the durable `.sebrain` contract are unchanged.
No editor queue, window layout, pause state, camera or selection enters a brain.

Legacy native render snapshot positional tuples remain unchanged. Extended
object presentation is internal to the rebuilt native renderer; the new status
channel has its own typed surface. Native code and its bindings are rebuilt
together; there is no attempt to load old struct ABI into the new module.

## Build, fonts and visual design

`SE_BUILD_OBSERVER=ON` alone brings SDL 3.2.8, OpenGL and Dear ImGui v1.91.9b
(pinned tag). `se_engine` has no UI dependency. Observer OFF needs none of those
libraries or font assets. Initial observer setup may fetch the pinned sources;
subsequent configured verification is offline.

Roboto Medium from the pinned ImGui source is rasterized by its TrueType font
atlas, with Cyrillic glyphs. CMake deploys the single font beside the binaries,
alongside Apache 2.0 license/notice. The pinned source is the deterministic
developer fallback; missing font assets fail with an explicit error instead of
silently switching to bitmap debug text. SDL display scale and framebuffer
scale govern fonts/controls and GPU clipping; display changes reload the atlas.

The explicit WorkbenchStyle uses graphite panes, cool separators, near-white
text, modest 3px frames, 4/8/12/16 spacing and restrained blue/orange/cyan
accents. Proportional pane sizes keep the world dominant. Status/transcript
scroll and canvas clipping handle small windows. The tool strip can scroll at
high DPI. The layout helper is tested at 1100×700, 1440×900 and 1920×1080 with
1×/1.5×/2× scale. Pane resizing uses proportional layout, not draggable splitters.

Run `python main.py --paused` for live editing. The static presentation fixture:

```
cpp/build-verify/Release/se_observer_demo.exe --width 1440 --height 900
```

For a reproducible visual capture of the fixture, add
`--seconds 2 --capture <path.bmp>`. Fixture diagnostics are illustrative
presentation data and are explicitly not a survival or cognition result.

## Verification and limits

Acceptance executed on Windows/MSVC/OpenGL, 2026-10-01:

| Gate | Actual result |
| --- | --- |
| `python tools/verify.py --full` | 613 pytest PASS; Release CTest 2/2 PASS; import/headless smokes PASS |
| Required five targeted suites below | 154 PASS |
| Workbench pytest cases | 28; included in full/targeted gates |
| Observer-OFF native engine and oracle | Release build PASS; CTest 1/1 PASS |
| Native fixture at three required window sizes | Opened, framebuffer captured and visually inspected |
| Layout/font scale 1×, 1.5×, 2× | Native PASS, including Cyrillic glyph rasterization |
| Native ImGui interaction | Placement, Run, Step, text focus, shortcut suppression and Enter send PASS |
| Determinism | Hash seeds 1/777, observer cadence, RNG, pending checkpoint continuation PASS |

Commands actually executed (repository root):

```text
cmake -S cpp -B cpp/build-verify -DSE_BUILD_OBSERVER=ON
cmake --build cpp/build-verify --config Release
python tools/verify.py --full
python -B -m pytest -q tests/test_v083_homeostatic_valuation.py tests/test_brain_sensor_contract.py tests/test_v084_delayed_homeostatic_learning.py tests/test_v090_workbench.py tests/test_architecture_boundaries.py --tb=short
ctest --test-dir cpp/build-verify -C Release --output-on-failure
cmake -S cpp -B cpp/build-headless-v090 -DSE_BUILD_OBSERVER=OFF
cmake --build cpp/build-headless-v090 --config Release --target se_equivalence
ctest --test-dir cpp/build-headless-v090 -C Release --output-on-failure
cpp/build-verify/Release/se_observer_demo.exe --seconds 2 --width 1100 --height 700 --capture D:/projects/synth_life/cpp/build-verify/workbench-1100.bmp
cpp/build-verify/Release/se_observer_demo.exe --seconds 2 --width 1440 --height 900 --capture D:/projects/synth_life/cpp/build-verify/workbench-final-1440.bmp
cpp/build-verify/Release/se_observer_demo.exe --seconds 2 --width 1920 --height 1080 --capture D:/projects/synth_life/cpp/build-verify/workbench-1920.bmp
git diff --check
```

The captures show the static, explicitly labelled presentation fixture, not
learned survival behavior. The real organism's window is separately covered by
live-observer/workbench inertness tests. The observer-OFF gate builds the native
authority and oracle only, without overwriting the installed observer-enabled
Python extension. Cross-platform packaging of that extension is not claimed.

Visual polish/layout pass checked hierarchy, font legibility, muted grid,
Food/Water contrast, world dominance and non-overlapping panes. Small-window
status uses normal scrolling; the transcript keeps its input anchored. A long
input hint was changed to wrapped text after the small-window inspection.

### Changed files and responsibility

- Versioning/contracts: `ROADMAP.md`, `README.md`, `CURRENT_STATUS.md`,
  `ARCHITECTURE.md`, `DEVELOPER_GUIDE.md`, `docs/TESTING.md`, this document.
- Runtime/host: `main.py`, `simulation/workbench.py`,
  `simulation/continuous.py`, `simulation/runtime_types.py`, `world/native_world.py`.
- Native boundary: `cpp/include/se/world.hpp`, `cpp/src/world.cpp`,
  `cpp/include/se/render_snapshot.hpp`, `cpp/include/se/workbench_commands.hpp`,
  `cpp/include/se/workbench_snapshot.hpp`, `cpp/src/bindings_workbench.*`,
  `cpp/src/bindings.cpp`. The only substrate addition is a const consolidated
  assembly-count getter in `cpp/include/se/neurodynamic_substrate.hpp`.
- Desktop: `cpp/include/se/observer.hpp`, `cpp/src/observer.cpp`,
  `cpp/include/se/workbench_{ui,style,brain_gpu}.hpp`,
  `cpp/src/workbench_{ui,style,world_view,brain_view,brain_gpu,status_view,dialogue_view}.cpp`.
- Build/assets: `cpp/CMakeLists.txt`, `.gitignore`,
  `cpp/assets/fonts/{LICENSE-Roboto.txt,NOTICE-Roboto.txt}`.
- Regression/demo: `cpp/tests/observer.cpp`, `cpp/tests/observer_demo.cpp`,
  `tests/test_v090_workbench.py`, `tests/test_architecture_boundaries.py`.

The workbench suite covers detached status, observer cadence/RNG inertness,
native preset consequences, erase/rejection, transaction safety, pending-command
continuation, host pause/step, language input and brain exclusion. Architecture
guards exclude UI dependencies from engine/cognition and forbid command-path
graph/physiology mutation. Native tests cover layout, stable graph positions,
bounded queue and retained immutable status. Existing v0.8.3/v0.8.4 suites remain
the cognitive-policy regression gates.

No complete scenario format, curriculum library, episode statistics framework,
batch runner or multi-seed survival benchmark is implemented in this milestone.
Native font/input behavior across Linux/macOS and actual hardware at 150–200%
DPI still need platform-specific manual testing beyond synthetic layout gates.

v0.9.0 changes the experimental workbench, not the learned cognitive policy.

"Food" and "Water" are human/editor labels for physical resource presets.
They are not innate cognitive concepts.

No reward, food-to-action rule, resource semantic shortcut, raw physiology
planner access, or observer-to-cognition mutation was introduced.

Observer presence without explicit commands remains causally inert.
