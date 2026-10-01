# v0.8.3 Learned trajectory-level homeostatic valuation

The target of homeostasis is innate.
The action model is learned.

The organism knows what internal states are closer to its physiological
operating range, but it does not know which world objects or actions will
produce those states until experience provides evidence.

## Implemented now

Production observations run World consequence -> Physiology ->
InteroceptiveTransducer -> ordinary sensory singleton Cognits -> existing
TransitionModel evidence -> materialized SELF_ACTION Relations. Native World
and native graph remain authoritative; Python World/graph are differential
oracles. No additional transition learner or numeric graph mirror exists.
The predictor is `NativeGraphBackend.action_effects` (native `SelfAction` rho)
or the equivalent Python graph query in `DeliberativePlanner.homeostatic_effects`.
Both multiply acquired prediction probability by Relation confidence. Learning
requires the existing provisional support/lift thresholds; outcome updates
reduce confidence under contradiction. General temporal transitions remain
available for ordinary future-state search.

Runtime converts configured physiological targets through the same bounded
transducer quantization as observations. Planner receives only the neutral
`homeostatic_target_levels` tuple, observed sensory bins, and predicted Cognit
IDs/probabilities. It never reads reserves, physical consequence payloads,
resource channels, or food/water labels. Structural `internal_*` membership
identifies the non-spatial sensor domain. Singleton predictions avoid counting
composites as independent internal measurements. Competing predictions for the
same bin take their maximum; distributions with mass above one are normalized.

For each channel, with target bin t, current bin l, and confidence-weighted
prediction masses q(b):

```
D(current) = |l - t| / (bins - 1)
E[D(next)] = (1 - sum(q)) * D(current) + sum(q(b) * D(b))
progress = mean_channels(D(current) - E[D(next)])
```

Unpredicted mass means unchanged state. Without action-conditioned internal
evidence, progress is exactly zero. The estimate carries expected bins down
the candidate trajectory. Existing beam search multiplies each subsequent
increment by prefix prediction confidence; cumulative progress is clamped to
[-1, 1]. One bounded planner term is `0.8 * cumulative_progress`. Search adds
only the change in that term at each expansion, preserving the existing
cognitive formula and deterministic tie order. Thus learned worsening can
reduce rank, and imagined improvement cannot become an unconditional action
bonus. This is a coarse mean-state approximation, not a full joint distribution.

`internal_tension` remains cognitive intrinsic novelty/prediction tension.
Physiological homeostatic deviation is a separate quantity.

## Settings and persistence ownership

`simulation/persisted_settings.py` owns explicit `WORLD_CAUSAL_FIELDS`,
`RUNTIME_CAUSAL_FIELDS`, `NEURAL_CAUSAL_FIELDS`, `COGNITIVE_CAUSAL_FIELDS`, and
resource/interoception groups. Physiology config retains its existing owner.
`restore_settings()` merges these once before constructing native World and
rejects incompatible explicit Settings or conflicting saved sources.

| Classification | Fields / ownership |
| --- | --- |
| Causal persisted | perception_radius, width/height, max_objects, entity_count, object_count (constructor topology), spawn min/max; world_tick_interval and maintenance cadence; physiology rates/maxima/targets and initial constructor configuration; resources; internal/neural topology; cognitive learning, quotas, memory, language, choice and planning parameters; valuation ablation flag |
| Episode state | actual bodies/objects/resources, RNG, reserves, WorldTime, next spawn, sensory history, active Cognits, plans and scheduler/frontier; existing state sections |
| Observation/debug only | telemetry_history, simulation_speeds; not causal configuration |
| Historical/legacy | world_event_weights; autonomous random-event API disabled |

`causal_config` is an optional additive configuration field in the existing
snapshot envelope. No binary layout or required section changes: snapshot v7,
continuous interoceptive .seworld v10, discrete v4, .sebrain v6 and native graph
v3 stay unchanged. Older artifacts missing this field retain the historical
restore/default behavior: exact continuation with non-default unrecorded
settings requires the original explicit Settings. Such values cannot be
recovered from legacy artifacts. Existing world/resource/neural config sources
still participate in conflict detection.

Valuation has no independent learned state. World artifacts save ordinary
Relations, transition evidence, sensory history and planner candidate/session
state. Beam expansion is atomic; pending PLAN_REFINE work recomputes from the
restored graph and bins. Planner diagnostics persist with its episode state.
Brain artifacts transfer acquired Cognits/Relations, but omit current bins,
reserves, deficits, diagnostics, plan and session state. A transferred brain
needs a new sensory observation before valuation can operate.

## v0.8.3 stabilization fix: brain sensor compatibility

Current version remains v0.8.3. This is a stabilization fix, not a new milestone.

Brain META now includes `internal_sensor_contract` when the transferred
structured graph/pattern data contains internal-domain knowledge. Detection
uses `is_internal_primitive()` on Cognit pattern participants, primitive pattern
nodes and durable proto-pattern participants. Prototypes are included because
they can later materialize internal Cognits. No serialized-text search is used.

```json
{
  "schema": 1,
  "encoding": "reserve-ratio-floor-v1",
  "channels": ["internal_0", "internal_1", "internal_2"],
  "bins": 8
}
```

The encoding identifier fixes reserve/max normalization, floor-and-clamp
quantization and the engineering channel order (energy, nutrients, hydration).
Bin meaning is a normalized interval, so maxima in absolute reserve units do
not belong in this representation contract. Targets express the receiving
organism's operating range and are not transferred either. Enabled flags are
ablations, not encoding topology. Metadata contains no current reserves,
levels, deficit, time, activation or plan/session state.

The optional field fits the existing META dictionary. Native brain v6,
reference brain v4, container v1 and native graph v3 remain unchanged. Current
readers validate compatibility before building/loading the learned graph;
legacy readers ignore this added field and do not provide the new safety check.
No values are rescaled or remapped.

| Brain knowledge | Saved contract | Receiving topology | Result |
| --- | --- | --- | --- |
| Internal Cognits/prototypes | 8 bins | 8 bins, same order/encoding | Transfer |
| Internal Cognits/prototypes | 8 bins | 4 bins | Reject before graph activation |
| Internal Cognits/prototypes | 4 bins | 8 bins | Reject even if bin IDs fit |
| Internal knowledge | Different version/order/encoding or malformed metadata | Any | Reject |
| Legacy internal knowledge | Missing | Any | Reject: topology unverifiable |
| External-only knowledge | Missing or irrelevant contract | Any bins | Transfer |

Historical interoception allowed configurable 2-32 bins, so legacy brain
version alone cannot prove the encoding. External-only legacy brains remain
loadable. Compatible transfer retains learned Relations but resets internal
sensory history, activation, planner/session and diagnostics; the receiving
body keeps its own state. A fresh ordinary observation makes transferred
knowledge usable. Both interoception and valuation still default OFF.

The new physical vertical regression uses NativeWorld, successful physical
INTERACT, the real consequence-to-Physiology path, the transducer and core.step
with ordinary learning/materialization. Repeated controlled trials reset the
initial hydration fixture, hold placement fixed and alternate interaction with
IDLE background observations. No final Relation probabilities or sensor
Cognits are manually constructed. It checks acquired internal SELF_ACTION
evidence; it makes no autonomous survival or delayed-credit-assignment claim.

Competing internal-state predictions are a coarse marginal approximation,
not a calibrated joint distribution. Regression fixes the existing behavior:
maximum probability for duplicate bins, normalization when competing mass
exceeds one, and unchanged-state mass when evidence is incomplete. No simple
normalization correctness bug was found; calibration remains v0.8.4 scope.

## Ablation and diagnostics

`homeostatic_valuation_enabled=False` is the default. With interoception OFF,
there are no internal primitives and the dedicated component is zero even if
valuation is requested. With interoception ON and valuation OFF, ordinary
learning continues with the existing planner formula. With both ON, supported
internal consequence predictions can change beam ranking. Internal primitives
never enter translation normalization; mixed-domain co-occurrence remains an
ordinary non-spatial candidate.

Read-only research diagnostics are available through
`planner.homeostatic_diagnostics()`: `homeostatic_predictions_considered`,
`homeostatic_prediction_confidence` (maximum channel-averaged predicted mass
considered during search), and `homeostatic_plan_component` (selected plan).
The returned dictionary is detached from planner state. TickMetrics/UI have
not been expanded.

Controlled tests exercise the complete core.step observation-to-ranking slice
on both backends and a two-action learned intermediate trajectory. They also
cover reversed learned histories on native and Python,
weak/repeated/contradictory evidence, identical physical resource channel with
changed hydration payload and next-observation encoding, OFF ablation,
non-default config/frontier continuation, learned world/brain transfer,
non-spatial mixed evidence and PYTHONHASHSEED 1/777. Dependency/AST guards
protect physiological/resource policy boundaries and observer inertness.

## Explicitly not implemented

- General delayed credit assignment beyond ordinary observation-to-observation
  learning and bounded short trajectories.
- Semantic hunger/thirst concepts or innate food/water knowledge.
- Reinforcement reward or global utility maximization.
- Full joint internal trajectory distributions or long-horizon survival guarantee.
- Neural interoception, a world redesign, or observer UI redesign.

A possible v0.8.4 scope is controlled multi-observation delay experiments,
calibration of competing internal-state predictions, and longer physical
training/ablation protocols. This milestone does not claim improved survival.

## Stabilization verification and changed files

On 2026-10-01, `python tools/verify.py --full` passed: **516 pytest passed;
CTest Release 2/2 passed**. Release native/observer build and import/headless
smokes passed. Required targeted suites plus `tests/test_brain_sensor_contract.py`
passed **89 tests**. `git diff --check` passed; new files were independently
checked for whitespace/conflict markers as well. The preserved v0.8.3 suite
includes reversed learned histories, Python/native parity, weak/repeated and
contradictory evidence, no-evidence/OFF ablations, two-step trajectories,
PYTHONHASHSEED=1/777, exact .seworld continuation and full_graph_sync_calls=0.

Changed production files: `physiology/interoception.py`,
`simulation/simulation.py`; new `simulation/brain_sensor_contract.py`.
Changed tests: `tests/test_v083_homeostatic_valuation.py`,
`tests/test_architecture_boundaries.py`; new `tests/test_brain_sensor_contract.py`.
Documentation: `README.md`, `CURRENT_STATUS.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
`docs/TESTING.md`, `docs/V0_8_2_INTEROCEPTION.md`, this document. Total: 13 files.

No planner/valuation numeric implementation or defaults changed. No schema bump
was required: topology is optional META metadata. Legacy internal knowledge
without that metadata cannot safely migrate and is rejected; external-only
legacy knowledge still loads. Physical plumbing and coarse marginal behavior
are covered without adding a new probabilistic model or functional milestone.
v0.8.4 remains planned for multi-observation delay, competing-bin calibration,
longer physical curricula and learned-knowledge ablations.

## Historical initial v0.8.3 verification and changed files

Full verification on 2026-10-01: 491 pytest passed, CTest Release 2/2 passed.
The native Release observer build and both import/headless smokes passed.
Targeted command (64 passed):

```
python -m pytest -q tests/test_v081_persistence_security.py tests/test_v081_consumables.py tests/test_v082_interoception.py tests/test_v083_homeostatic_valuation.py tests/test_architecture_boundaries.py
python tools/verify.py --full
```

The hashseed experiment ran in separate processes with PYTHONHASHSEED=1/777.
For the native controlled history (12 examples per action):

| History | Valuation | Selected test action | Plan score | Homeostatic component |
| --- | --- | --- | --- | --- |
| B improves internal bin | OFF | A (IDLE) | 0.345 | 0 |
| B improves internal bin | ON | B (MOVE_UP) | 0.45928571428571424 | 0.11428571428571428 |
| A improves internal bin | ON | A (IDLE) | 0.45928571428571424 | 0.11428571428571428 |

These arbitrary candidate names are test interventions, not built-in knowledge
about which action restores a reserve. The counterfactual physical resource
experiment separately changes payload while keeping the visible channel fixed.

Changed/new production files:
`config/settings.py`, `consciousness/patterns.py`, `consciousness/sensory.py`,
`consciousness/planning.py`, `consciousness/valuation.py`,
`physiology/interoception.py`, `simulation/persisted_settings.py`,
`simulation/simulation.py`.
Tests: `tests/test_v083_homeostatic_valuation.py`,
`tests/test_architecture_boundaries.py`.
Documentation: `README.md`, `CURRENT_STATUS.md`, `ARCHITECTURE.md`,
`docs/TESTING.md`, `docs/V0_8_2_INTEROCEPTION.md`, this document.

The original source workspace initially had no Git history, so verification
included an independent whitespace/conflict-marker scan of all 16 changed/new
files. Publication subsequently compared the source with upstream main
(336e51d), preserved tracked historical artifacts, and placed these 16 files
in a commit on that history. The staged `git diff --check` passed.
