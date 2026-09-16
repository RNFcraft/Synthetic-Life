# Synthetic-Life

Synthetic-Life is an experimental embodied cognitive architecture built around a sparse, continuously changing graph of Cognits (`κ`) and Relations (`ρ`). The project is not an LLM/Transformer inference wrapper and does not use a frozen policy network as its learned core. Learning, prediction, memory, goals and action selection evolve during interaction with the World.

The current development line is **v0.6.6**.

Current accepted gates:

- **v0.5.2 frozen native baseline — PASS**
- **ELAPSED-TIME LAZY COGNITION — PASS**
- **TRUE EVENT-DRIVEN COGNITION FRONTIER — PASS**
- **CONTINUOUS WORLD COMPLETION — PASS**
- **NATIVE C++ SDL3/OPENGL OBSERVER — PASS**

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full architecture and [CURRENT_STATUS.md](CURRENT_STATUS.md) for the latest acceptance state.

## v0.6.6 long-life stabilization

v0.6.6 adds no intelligence capability. It adds read-only long-life diagnostics,
numeric corruption checks, exact scheduler workload counters, CI soak and
repeated-persistence tests, plus a manual extended-soak runner. The existing
embodied neural-cognitive-action loop is validated for deterministic bounded
execution over the CI soak and repeated save/load windows.

The first endurance pass also fixed a continuous lifecycle clock-domain bug:
Relations record evidence in observation ticks, but maintenance previously
compared those values with its slower maintenance ordinal, so their apparent
age could remain negative indefinitely. Maintenance now uses the current
observation tick for relation lifecycle decisions.

The milestone remains provisional: the measured default 100-second production
run completed 666 actions without corruption, but graph growth caused a clear
host-time increase across equal simulated-time windows. The manual 50,000-second
extended soak has not been run.

## v0.6.5 neural cognition to behavior

Experience-derived Assembly Cognits can now participate causally in ordinary
cognition and existing planner decisions. A coarse bridge event is propagated
through ordinary Relations and merged into the single continuous cognition
frontier. If deliberation is already open, its stale candidate is invalidated
and the normal propagation/imagination/search work chain is rebuilt. An action
that is already committed is never revised.

For sensory-neural runs, planner wake occurs just after that frame's neural
frontier, making the ordering independent of host `run_until` batching. The
research-only `neural_behavioral_participation` ablation keeps the same World,
neural representation, graph and Goal while suppressing only this frontier
contribution. There is no Assembly-to-action table, neural planner, reward,
Goal, or Cognit-to-neural feedback. The feature remains inert when
`sensory_neural_enabled=False`.

## v0.6.4 embodied sensory transduction

With `sensory_neural_enabled=True`, each real `SensoryFrame` is encoded by a
fixed bounded retinotopic/body receptor bank and submitted through one native
batch injection. Raw position, occupied/boundary/self signals, bounded
state/appearance channel numbers, touch, holding and resistance are the only
inputs. Ordinary micro-neural dynamics and the existing Assembly/Cognit bridge
do the remaining work. No object identity, label, Goal or action meaning enters
the encoder.

This milestone does **not** provide object understanding or innate neural
action meaning. A resulting Assembly is an experience-derived representation with no
innate semantic meaning. The feature is disabled by default to preserve the
frozen baseline. All receptors from one frame share its exact timestamp, so
Python cell order cannot create temporal evidence. v0.6.4 focused tests are
13/13, v0.6.0–v0.6.4 focused tests are 63/63, and the full suite is 378/378.

## v0.6.0 micro-neurodynamic substrate

The native backend now owns an isolated `NeurodynamicSubstrate`: event-driven
micro-κ nodes and fixed micro-ρ edges below the existing Cognit/Relation
system. Micro-κ / micro-ρ are **not** existing Cognits/Relations, and there is
no causal connection to cognition, language, Goals, World, or the observer in
this version.

It has float64 continuous neural time, deterministic `(time, sequence)` event
ordering, delayed signed fixed-weight delivery, same-time aggregation, lazy
membrane/adaptation decay, refractory handling, and snapshot/restore for
research experiments. Its physiology constants are innate substrate physics,
not learned knowledge. A normal runtime owns an empty substrate, so it does no
periodic neural update or neural work when inactive. There is no plasticity,
STDP, assembly detection, or Cognit coupling in v0.6.0.

Snapshots contain both dynamic state and innate physiology, so restoring into a
substrate constructed with different defaults reproduces its exact continuation.
Inspection projects potential and adaptation analytically to the substrate's
current time only for requested IDs; it does not materialize or sweep silent
micro-κ. v0.6.0 closure is frozen.

## v0.6.1 local plasticity and homeostasis

The isolated native substrate now supports local pair-based spike-timing
plasticity. Micro-ρ polarity is innate and immutable; only a bounded,
nonnegative weight magnitude can change, and only when that edge explicitly
enables plasticity. Incoming/outgoing local adjacency avoids graph-wide scans.
Same-time spikes are evaluated as one transaction against traces from before the
timestamp, so they create no fake causal learning.

Slow local homeostatic threshold bias is separate from fast adaptation. Both it
and pre/post traces decay lazily when an affected micro-κ is touched or
inspected. They are innate physiology, not semantic knowledge. There remains no
assembly/Cognit bridge and no World, language, Goal, action, reward, or
backpropagation coupling.

## v0.6.2 emergent assemblies

The native micro-substrate can now infer persistent distributed assemblies from
recurrent emitted spikes. Membership is evidence-derived and normalized by
individual activity; directed temporal evidence is part of identity. Same-time
spikes are unordered, while jittered earlier/later activity reinforces the same
temporal structure. Assemblies may overlap and carry no semantic label.

Consolidated records emit bounded native `AssemblyMatch` summaries for full and
partial recurrence. Candidate/recent/match state is bounded, weak candidates use
lazy elapsed-time decay during capacity pressure, and snapshot/restore preserves
exact continuation. The detector is observational: it does not alter spikes,
STDP weights, homeostasis, or pending events. An assembly is not itself a
Cognit; v0.6.3 supplies the separate one-way consolidation/recognition bridge.
Final temporal edges are derived after stable membership normalization, so both
edge endpoints must be stable members. Snapshot restore rebuilds this derived
view from saved temporal evidence. v0.6.2 is frozen.

## v0.6.3 assembly-to-Cognit bridge

The native engine now provides a one-way coarse assembly bridge. Consolidation
births exactly one ordinary Cognit in the existing authoritative numeric graph;
recognition activates that same Cognit through normal `receive()` semantics.
Incremental observations in one native recognition episode contribute only the
increase in peak confidence; after silence longer than the assembly window, a
new episode may contribute its own bounded peak. `NativeBrainEngine` owns the
stable AssemblyID-to-CognitID mapping and exactly-once cursor. Python only adopts
the `NEURAL_ASSEMBLY` facade metadata at an explicit coarse drain—there is no
per-spike callback or shadow numeric graph.

Bridge events live in the substrate snapshot; mapping/cursor live in the matching
engine bridge snapshot. A `.seworld v7` scheduler snapshot also retains optional
pending neural state and its requested frontier for exact causal continuation;
the schema version and `.sebrain v6` remain unchanged. No
reverse Cognit-to-micro path, automatic Relations, semantics, or
World/language/Goal/planner coupling is introduced. v0.6.3 is frozen.

The existing continuous scheduler carries one bounded `NEURAL_BRIDGE` boundary
at a time, ordered with World/language/cognitive events by time then sequence.
Each recognition performs ordinary receive and propagation at its event time,
so it can reach cognition between World observations. Births share the
ordinary global Cognit capacity and per-transaction birth budget; deterministic
suppression advances the cursor and is counted without creating a deferred
queue.

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

Current repository-reported acceptance state for v0.6.0:

- focused v0.6.0–v0.6.3 micro-neurodynamic suite: **50 passed**
- full pytest: **365 passed**
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
