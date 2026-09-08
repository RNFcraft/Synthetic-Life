# Synthetic-Life

Synthetic-Life is an experimental embodied cognitive architecture built around a sparse, continuously changing graph of Cognits (`κ`) and Relations (`ρ`). The project is not an LLM/Transformer inference wrapper and does not use a frozen policy network as its learned core. Learning, prediction, memory, goals and action selection evolve during interaction with the World.

The current development line is **v0.5.3a**.

Current accepted gates:

- **v0.5.2 frozen native baseline — PASS**
- **ELAPSED-TIME LAZY COGNITION — PASS**
- **TRUE EVENT-DRIVEN COGNITION FRONTIER — PASS**
- **CONTINUOUS WORLD COMPLETION — NEXT**

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full architecture and [CURRENT_STATUS.md](CURRENT_STATUS.md) for the latest acceptance state.

## Current runtime model

The system is hybrid by design.

**Python** owns semantic cognition: patterns, Goals, BeliefScene, memory meaning/retrieval policy, planner semantics, perceptual continuity and the event-driven cognitive work frontier.

**C++** owns the authoritative native numeric Cognit/Relation substrate and the physical World runtime: graph numeric state, waves, prediction mechanics, relation evidence/materialization, elapsed-time homeostasis, World bodies/objects, conflicts/fairness, event scheduling and native persistence.

Normal native execution keeps:

```text
World
  -> immutable SensoryFrame
  -> SyntheticEntityCore
  -> timestamped ActionIntent
  -> World
```

The cognitive core does not receive raw World/Grid state, physical IDs, collision IDs, spawn schedule or evaluator labels.

## Event-driven cognition

Normal continuous execution no longer performs a complete decision in one hidden cognition loop.

```text
SENSORY_CHANGE
  -> COGNITION_WAKE
  -> RECALL
  -> PROPAGATE
  -> IMAGINE
  -> PLAN_REFINE
  -> pending cognitive work becomes empty
  -> QUIESCENT
  -> one action commit
  -> WORLD_ACTION_COMPLETE
```

Multiple internal cognition events may occur at exactly the same float64 `WorldTime`. `WorldTime`, cognitive operation count, scheduler event IDs and render frames are independent concepts.

Continuous cognition ends because there is no pending causally justified internal work, not because a fixed number of cycles has elapsed.

## Requirements

### Python

Recommended:

- Python 3.11 or newer
- pip

Install Python-side dependencies:

```powershell
python -m pip install -r requirements.txt
```

`requirements.txt` includes the Python packages used by the project and Python-distributed CMake/Ninja helpers. It cannot install an operating-system C++ compiler.

### C++ build toolchain

The native backend is compiled as a C++20/pybind11 extension. A C++ compiler is therefore required on a new machine.

#### Windows

Install **Visual Studio 2022 Build Tools** or Visual Studio 2022 with:

- Desktop development with C++
- MSVC v143 C++ build tools
- Windows 10/11 SDK
- C++ CMake tools for Windows (recommended)

The `cmake` and `ninja` Python packages from `requirements.txt` provide convenient command-line binaries, but they do **not** replace MSVC.

#### Linux

Install a C++20 compiler and Python development headers. For Debian/Ubuntu, for example:

```bash
sudo apt update
sudo apt install build-essential python3-dev
```

CMake/Ninja may be installed either through the system package manager or through `requirements.txt`.

## Clean setup on Windows

From a fresh clone:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cmake -S cpp -B cpp/build
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
python -m pytest -q
```

The CMake configuration locates the active Python interpreter and obtains the pybind11 CMake package via:

```text
python -m pybind11 --cmakedir
```

The Release `_native_brain` module is emitted into the `consciousness/` package by the current CMake configuration.

If CMake reports that no C++ compiler is available on Windows, open a **Developer PowerShell for VS 2022** or install the Visual Studio C++ workload listed above.

## Build and verify

Typical verification:

```powershell
cmake -S cpp -B cpp/build
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
python -m pytest -q
```

Current repository-reported acceptance state for v0.5.3a:

- full pytest: **201 passed**
- CTest Release: **1/1 passed**
- deterministic `PYTHONHASHSEED=1/77` trajectory digest: identical
- `full_graph_sync_calls == 0`
- normal native Python physical World calls: **0**

## Persistence

The project uses two main persistence surfaces:

- `.sebrain` — durable learned cognition/native brain payload;
- `.seworld` — exact continuous World and execution frontier.

Continuous `.seworld` schema v3 includes the scheduler and unfinished cognition frontier, including ordered pending cognitive work. Save/load is intended to be behaviorally observational: no-save, save and save/load continuation must produce the same trajectory.

## Project status and roadmap

```text
v0.5.2 native frozen baseline                    DONE
    -> elapsed-time lazy cognition                DONE
    -> true event-driven cognition frontier       DONE
    -> continuous world completion                NEXT
    -> C++ SDL3/OpenGL native observer
    -> scaling cleanup
    -> continuous multi-entity runtime
    -> full 3D World
    -> Entity visual/retina/gaze input
```

The next gate is **CONTINUOUS WORLD COMPLETION**. Its job is to remove the remaining World heartbeat/tick dependence by scheduling spawning and maintenance directly in absolute continuous time.

After that gate passes, development moves to a native **SDL3 + OpenGL observer**, isolated from cognition and physics so renderer FPS cannot affect the simulated life trajectory.

## Important design invariants

- C++ native mode has no authoritative Python numeric Cognit/Relation mirror.
- `full_graph_sync_calls` must remain zero.
- renderer sampling must not affect behavior.
- save/load must preserve exact future behavior.
- CPU execution speed must not define simulated cognition time.
- legacy v0.5.2 discrete APIs remain compatibility oracles while the continuous runtime evolves.

For implementation details, read:

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CURRENT_STATUS.md](CURRENT_STATUS.md)
- [COGNITIVE_FORMALISM.md](COGNITIVE_FORMALISM.md)
- [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md)
- [V0_5_3_CONTINUOUS_RUNTIME_PLAN.md](V0_5_3_CONTINUOUS_RUNTIME_PLAN.md)
