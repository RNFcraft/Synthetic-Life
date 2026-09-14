# Synthetic-Life

Synthetic-Life is an experimental embodied cognitive architecture built around a sparse, continuously changing graph of Cognits (`κ`) and Relations (`ρ`). The project is not an LLM/Transformer inference wrapper and does not use a frozen policy network as its learned core. Learning, prediction, memory, goals and action selection evolve during interaction with the World.

The current development line is **v0.5.7**.

Current accepted gates:

- **v0.5.2 frozen native baseline — PASS**
- **ELAPSED-TIME LAZY COGNITION — PASS**
- **TRUE EVENT-DRIVEN COGNITION FRONTIER — PASS**
- **CONTINUOUS WORLD COMPLETION — PASS**
- **NATIVE C++ SDL3/OPENGL OBSERVER — PASS**

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

## Production entrypoint

```text
python main.py
    -> ContinuousRuntime
    -> authoritative C++ WorldRuntime
    -> NativeObserver
    -> SDL3/OpenGL
```

```powershell
python main.py
python main.py --speed 10
python main.py --headless --seconds 100
python main.py --headless --seconds 100 --save run.seworld
python main.py --load run.seworld
```

`--seconds` is an absolute target WorldTime. Interactive wall-clock time is only a pacing source; renderer FPS never advances simulation. Headless mode uses the same `ContinuousRuntime` without an observer. Pygame is no longer a production dependency; `ui/` remains unsupported legacy/debug code and requires a separately installed Pygame if used manually.

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

cmake -S cpp -B cpp/build -DSE_BUILD_OBSERVER=ON
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
python -m pytest -q
```

The CMake configuration locates the active Python interpreter and obtains the pybind11 CMake package via:

```text
python -m pybind11 --cmakedir
```

The Release `_native_brain` module is emitted into the `consciousness/` package by the current CMake configuration.
When the observer is enabled, its runtime `SDL3.dll` is copied beside the module. Both files are local build outputs and are intentionally excluded from Git.

If CMake reports that no C++ compiler is available on Windows, open a **Developer PowerShell for VS 2022** or install the Visual Studio C++ workload listed above.

## Build and verify

Typical verification:

```powershell
cmake -S cpp -B cpp/build -DSE_BUILD_OBSERVER=ON
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
python -m pytest -q
```

Current repository-reported acceptance state for v0.5.7:

- full pytest: **315 passed**
- CTest Release: **2/2 passed**
- deterministic `PYTHONHASHSEED=1/77` trajectory digest: identical
- `full_graph_sync_calls == 0`
- normal native Python physical World calls: **0**

The native observer is a dark research dashboard: the physical World occupies
the left viewport and a live Cognit/Relation graph plus compact status readout
occupies the right. Authoritative native cognition publishes immutable,
latest-only `BrainSnapshot` values at cognitive event boundaries. Node layout,
birth pulses and glow are ephemeral observer state. The renderer performs no
Python callback and cannot affect cognition, WorldTime, EventSequence, or RNG.
For large brains, its immutable view is capped at 1024 Cognits/4096 Relations
and then reduced by screen-space LOD. Visible/total counts remain explicit.
Cached dynamic OpenGL batches replace per-frame layout rebuilding and the old
per-pixel Relation drawing.

## Receptive embodied symbol grounding

The first language gate learns meanings for one exact external nonce token at a
time. `runtime.inject_language("dax")` creates or reuses a normal
`LANGUAGE_SYMBOL` Cognit, records contrastive co-occurrence with the entity's
currently active internal Cognits, and after repeated evidence learns directed
ordinary ASSOCIATIVE Relations. Re-presenting the symbol then cues the learned
experience through the existing native wave.

The lexicon supplies identity only—not a dictionary. There are no pretrained
models, embeddings, word/action mappings, syntax, language production, or raw
World labels in this pass. Language inputs are deterministic external cognitive
events and do not mutate the physical World or commit actions.

The accepted v0.5.4 proof uses real `World → SensoryFrame → Cognit` contexts.
Context is captured before recall/planning and contributes to a
language-independent experiential background. The latest percept remains
current at full salience until another real observation replaces it; only then
does it decay from its exact retirement WorldTime through the bounded history.
Nonce-label permutation swaps learned retrieval accordingly, and a first word
can be learned without any competing second token. Language waves remain
separate from ordinary cognition waves.

## Persistence

The project uses two main persistence surfaces:

- `.sebrain` — durable learned cognition/native brain payload;
- `.seworld` — exact continuous World and execution frontier.

Continuous `.seworld` schema v7 includes the scheduler, unfinished cognition
frontier, absolute spawn/maintenance frontiers, exact grounding frontier,
pending ordered utterances, and a resumable token cursor. It migrates v6
single-token worlds. `.sebrain` v6 stores durable grounding and bounded
SEQUENTIAL adjacency evidence while starting a clean episode; v5 Pass-1 brains
migrate with no invented sequence evidence.

## Ordered utterances and basic composition

Pass 2 accepts externally segmented exact-token tuples such as
`("dax", "wug")`. All tokens retain one external WorldTime and one frozen
embodied context, but execute as separate resumable cognitive work items. After
constituent retrieval, a final work item records adjacent directional
LANGUAGE_SYMBOL `SEQUENTIAL` evidence.

The composed result is only the union of non-language Cognits retrieved through
the constituents' already learned ASSOCIATIVE Relations. Thus a first-ever
combination can retrieve both learned meanings before its first adjacency is
recorded. This proves ordered exact-symbol processing and basic constituent
composition—not grammar, syntax induction, phrase concepts, commands, or
general natural-language understanding.

Ordinary cognition and maintenance cannot interleave inside an active language
frontier: both language continuation and maintenance use same-WorldTime
deterministic deferral. Sequence bookkeeping is cleaned when Cognits are really
deleted, so a later reborn token cannot inherit a forgotten symbol's edges.

The native observer uses a responsive `DIALOGUE | WORLD | BRAIN / STATUS`
layout. Its left panel reads a latest-only immutable native snapshot containing
at most 64 event-boundary lines. Incoming EXTERNAL utterances appear once. The
ENTITY role is only a channel foundation for a future real SPEAK gate; no entity
speech production, echo, or fabricated response exists in v0.5.5.
Save/load remains behaviorally observational.

## Relational compositional grounding

Pass 3 resolves each constituent only through the intersection of its learned,
materialized Pass-1 grounding targets and its actual retrieval wave. Resolution
is bounded and deterministic, excludes language/target Cognits, and preserves
unresolved alternatives when learned evidence is tied.

When exactly one resolved constituent denotes an existing `RELATIONAL` or
`BOUND_RELATION` Cognit and two other constituents resolve to participants, the
runtime emits an immutable `LanguageRelationalResult` containing a real
`RelationalStructure`. Participant order supplies directed role indices; no
surface word has a hard-coded role or meaning. A held-out triple therefore
composes on its first occurrence, while reversing its two participant tokens
changes the binding. Without a learned relational anchor the result remains
partial and unbound.

This composition is read-only retrieval. It does not create phrase Cognits,
semantic Relations, Goals, ActionIntents, or World mutations. `BeliefScene`
consumes the resulting structure through its existing binding API. Persistence
schemas remain `.seworld v7` and `.sebrain v6`.

The frozen acceptance proof uses two perceptually distinct objects in the real
native World. Ordinary perception and memory create participant Cognits and
ordinary relational cognition creates the relation anchor; standard Pass-1
exposures ground nonce labels without injecting semantic IDs. The first unseen
triple composes immediately, including under a permutation of every surface
label. `source_cognits` contains only the two participants, canonical
`relations` retain ordinary structural matching, and directed `role_edges`
allow generic `BeliefScene` scoring to distinguish correct and reversed roles.

## Learned grounded requests

Pass 4 learns request intent from contrastive external desired-state
demonstrations. An arbitrary exact NFC token may acquire an ASSOCIATIVE link to
the generic `COMMUNICATIVE_REQUEST` Cognit; neither that concept nor the token
encodes an action. A retrieved request cue plus a complete Pass-3 structure
produces `LanguageRequestResult` and installs the structure through the ordinary
Goal system with `origin="LANGUAGE_REQUEST"`. The existing planner then sees the
same `core.target_structure` used by other relational goals.

The same grounded structure without a learned cue remains a description and
creates no Goal. Incomplete/ambiguous structures also remain non-operative.
Language interpretation never selects an ActionType, emits an ActionIntent, or
mutates World/EventSequence. The acceptance curriculum proves this with real
World-derived meanings, a held-out first-ever requested combination, arbitrary
request-label permutation, and an untrained command-looking control.

External text is UTF-8 and Python identity is exact Unicode after NFC only.
There is no lowercasing, case folding, transliteration, language detection, or
morphology. Request evidence is durable in the existing `.seworld v7` and
`.sebrain v6` LANG payloads; v0.5.6 data loads with no invented request cues.

The closure proof trains a cue only with structure X, independently grounds Y,
and then accepts the first-ever `cue + Y` as Goal(Y); bare Y remains a
description. Goal provenance never selects planner mechanics: any relational
Goal with the ordinary target state enters existing target-progress/action
scoring and subgoal management. Queued request demonstrations retain their
target across save/load, including legacy three-field v7 inbox rows. Request
Relation births share one deterministic global per-tick budget.

## Project status and roadmap

```text
v0.5.2 native frozen baseline                    DONE
    -> elapsed-time lazy cognition                DONE
    -> true event-driven cognition frontier       DONE
    -> continuous world completion                DONE
    -> C++ SDL3/OpenGL native observer             DONE
    -> bounded GPU brain-view scaling              DONE
    -> receptive symbol grounding                  DONE
    -> multi-token sequence/basic composition      DONE
    -> relational compositional grounding          DONE
    -> grounded requests / language -> goals       DONE
    -> continuous multi-entity runtime
    -> full 3D World
    -> Entity visual/retina/gaze input
```

v0.5.x LANGUAGE FOUNDATION: FROZEN

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
