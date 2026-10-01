# v0.8.4 Delayed and calibrated homeostatic consequence learning

Current version remains v0.8.4. This is a stabilization/freeze closure, not a
new milestone. Production delayed-observation acceptance and full verification pass:
**v0.8.4 DONE / FROZEN**. v0.8.5 survival curriculum remains planned.
Interoception, homeostatic valuation and delayed prediction all default OFF.

## Fixed / innate versus learned

Fixed / innate: internal sensor encoding and channel order, configured homeostatic
target bins, the engineered temporal discount formula, concentration aggregation
and bounded search limits. None of these encode resource identity or action policy.

Learned: action-conditioned and passive state transitions, observed delay estimates,
internal future-state predictions and confidence/contradiction evidence. These are
acquired from the same ordinary sensory experience as external state transitions.

Delayed value is obtained by model-based prediction through learned state transitions,
not by propagating reward backward to earlier actions.

The physiology dynamics are physical and engineered.
The cognitive model of their sensory consequences is learned.

## Representation and acquisition

There is no new Relation type or parallel probability learner. Existing
`SELF_ACTION` expresses A + action -> B, and ordinary `SEQUENTIAL` expresses
B -> C. Native C++ remains the numeric authority. The Python reference uses
the same evidence rules; no native graph mirror is maintained during cognition.

Timing sufficient statistics annotate existing transition evidence, keyed by
source, target and action (zero means passive). They contain observation count,
mean WorldTime interval and Welford M2. They contain neither reward nor value.
Moments accumulate across episodes; probability/support remain in existing rho
and the existing bounded observation window. The timing map is capped at four
times the configured relation capacity. Admission is deterministic.

An actual completed action supplies its kind and success to acquisition.
Failed actions provide contradiction evidence but never positive consequence evidence.
An unsuccessful attempt updates existing SELF_ACTION outcomes and records an empty
target trial in the existing evidence window. Confidence and effective q fall; later
success can recover them. Neither an unrelated improving observation nor a failed
trial creates target timing or materializes positive rho. SEQUENTIAL hypotheses are
not contradicted merely because the action failed.

Action attempts preserve their observed source IDs and start time across intermediate
internal observations. Completion evidence is consumed by the actual full observation.
Sentinel 0 means passive/no completed action; every real ActionType value is positive.
IDLE remains a real action with its own SELF_ACTION timing. It is no longer duplicated
into passive channel 0. Passive observations are learned independently.

Only directly matched sensor patterns and observed semantic context become
timed learning endpoints. Propagated guesses and recalled internal states do
not become confirming sensory evidence. Controlled trial resets explicitly
clear the episode boundary rather than learning transitions across resets.
No later target is manually attached to the earlier action.

## Prediction, calibration and time

`successors` is a generic graph API for either action-conditioned or passive
prediction. It handles external and internal Cognits identically. A link uses:

```
q = prediction_probability * confidence * (1 - contradiction_evidence)
    / (1 + sample_delay_variance / max(1e-9, mean_delay ** 2))
chain_q = source_q * q
arrival_time = source_arrival_time + mean_delay
```

Minimum timing support is the existing provisional relation support. A passive
step requires passive timing evidence, so an action-only SEQUENTIAL link is
insufficient. Each chain multiplies probabilities and sums observed simulated
time. No wall clock enters cognition. Duplicate witnesses to one target use
the strongest probability, breaking ties by earlier arrival; they are not
combined as independent trials. Cycles, depth, arrival time and probability
are bounded. The planner follows an action projection, zero or more passive
steps, then another candidate action from the projected state. Arrival time
continues across actions in the beam.

Delayed prediction refines ordinary model-based state prediction;
absence of timing evidence never deletes the baseline prediction.
Ordinary action prediction and immediate learned valuation are computed first.
No usable timed root (absent support, floor or horizon filtering) keeps the exact
v0.8.3 state/estimate/confidence convention, including transferred legacy rho.
Unknown timing is not fabricated. Supported timing supplies a bounded refinement
and replaces known root timing instead of counting the same untimed effect twice.

Passive transitions preserve unmodified external cognitive context conservatively.
`merge_projected_state` retains prior external Cognits, adds supported targets and
replaces only affected internal channels. Stale mixed patterns carrying those
channels are removed; their separately represented external context remains.
Competing supported singleton bins enter calibration. No external disappearance
is inferred from a missing outgoing edge, and no new absence model is introduced.
A second action acquired from external B remains available after B -> internal C.

For each internal channel, singleton Cognits form a coarse bin marginal.
Duplicate Cognits for the same bin use maximum evidence. Let `m` be total bin
mass, `w_b = q_b / m` and `c = sum(w_b ** 2)`. Effective bin mass is
`q_b / max(1, m) * c`. A consistent single bin has concentration one; equally
plausible two-bin alternatives have concentration one half. Contradictions
also reduce link confidence. Missing mass means unchanged current state.
Support, predictive confidence, ambiguity and desirability are separate.

Bin-distance progress keeps the v0.8.3 normalization by `(bins - 1) * channels`,
bounded to [-1, 1], with each bin's contribution discounted by
`exp(-planning_time_discount * cumulative_arrival_time)`. The beam component
keeps the existing weight 0.8. Earlier equal improvements rank higher.

The endpoint marginal replaces earlier predictions when a channel changes.
Direct and indirect predictions of the same bin retain one strongest witness.
Valuation uses endpoint change, not a sum of bonuses for every passive node.
This prevents counting the same improvement at ingestion, digestion and a
duplicated endpoint. It does not model a full joint distribution of trajectories.

## Settings and compatibility

| Setting | Default | Valid range |
| --- | --- | --- |
| `delayed_homeostatic_prediction_enabled` | false | boolean |
| `planning_passive_prediction_depth` | 3 | integer 0..8 |
| `planning_prediction_time_horizon` | 30 seconds | finite (0, 10000] |
| `planning_time_discount` | 0.1 per second | finite [0, 100] |
| `planning_temporal_probability_floor` | 0.01 | finite (0, 1] |

All five belong to persisted causal runtime configuration. Explicit receiver
mismatches reject before construction. The complete pre-v0.8.4 runtime group
migrates to the new defaults; partially missing new groups fail closed. OFF
uses the original v0.8.3 acquisition and valuation path. Old knowledge without
timing evidence retains its immediate valuation and ordinary state; no learned delay is invented.

`.seworld` restores timing moments, native transition history, actual observed
endpoint/time, attempted action context and pending completion, alongside the existing scheduler,
cognition frontier and planning session. Exact continuous continuation is
tested before an internal change, with its same-time event queued, after the passive
observation and mid-deliberation after a later actual action. Last coarse frame and
optional internal observation count survive checkpoints. Existing world v10 and
native graph v3/v4 formats remain; no event enum or additional cadence setting is needed.

`.sebrain` transfers materialized graph and timing knowledge but no observation
window, pending action, last sensory time, active state, plan or body reserves.
Supported timing transfer is native -> native and Python -> Python. Cross-backend
brain transfer is unsupported and fails closed on META numeric_backend before any
graph activation; missing legacy metadata identifies the historical Python backend.
Python -> native and native -> Python cannot silently lose timing. Durable timing
survives an OFF receiver saving its brain again. Internal sensor topology validation
remains unchanged and fail-closed.
Native binary graph v4 appends timing rows to the v3 payload; v3 remains readable
and is still written when no timing knowledge exists. Outer brain v6/reference
v4 and continuous world v10 container schemas remain unchanged. Python timings
use an optional LEAR field; explicit native snapshot exports are persistence
data, not live numeric mirrors.

Diagnostics are detached: homeostatic component/confidence plus passive depth,
cumulative elapsed time, ambiguity, witness count and projected Cognit IDs.
There are no planner reads of raw Physiology, resource payload or object policy.

## Production interoceptive observation

Passive physiological changes are observed by the production runtime
when the coarse interoceptive representation changes.

With delayed prediction enabled, MAINTENANCE uses the existing
`continuous_maintenance_interval_seconds`. Simulation owns Physiology/transducer
sampling; runtime compares `last_internal.levels` to the sampled coarse levels.
Raw drift within a bin produces no event. A change queues ordinary SENSORY_CHANGE
with payload 1, deduplicated against pending sensory events. The handler rechecks
levels, uses the cached external frame with a fresh observation ordinal and calls
ordinary `_observe` in observation-only mode. It performs sensory pattern learning,
materialization and generic prediction without generating an action frontier.

No World movement, RNG consumption or neural transduction is introduced. The closed
frontier receives the updated observation state and retains its committed action and
session; an in-flight physical action remains unique. Active deliberation/language
boundaries defer internal processing in deterministic scheduler order. At same-time
physical completion, the actual full observation owns completion evidence; an
internal event never consumes it against a stale cached external frame.

## Controlled production physical freeze acceptance

`production_physical` runs ContinuousRuntime with NativeWorld for 32 interleaved
INTERACT/IDLE interventions beside an identically placed resource. One real scheduled
physical action is permitted per trial, then further physical actions are held while
the production scheduler runs. Placement, initial reserves, actions and trial resets
are controlled; no delayed phase calls core.step, samples a manual cognition frame,
or initializes Relation probabilities.

Initial energy is 15, nutrients zero and hydration 80. The nutritive resource supplies
60 nutrients and one hydration unit. Real INTERACT completes at trial time +0.15 s;
its ordinary observation has bins `(1,4,6)`, with energy unchanged. The engineered
fixture digestion rate is 1500 units/s, efficiency one and basal/cost rates zero.
At the next 0.05 s maintenance boundary, real digestion has raised energy to 75 and
bins become `(6,0,6)`. The observed passive interval is learned, not encoded in
cognition. Production maintenance generates exactly 16 internal observations, one
for each nutritive interaction; 32 real action completions occur.

The counterfactual uses the same appearance/channel/placement and hydration payload,
but zero nutrients. World forbids an entirely empty resource; one hydration unit
stays within the same coarse bin. Energy stays at bin 1 and the runtime generates
zero additional internal observations. Learned delayed progress exceeds control.
With the same acquired graph, delayed prediction selects INTERACT_UP; passive depth
zero selects IDLE. Delayed OFF and delayed ON without timing produce identical
ordinary plans. The latter retains baseline knowledge without inventing delayed value.

An independent in-flight test observes exactly one internal change while preserving
one action event and one committed frontier, with neural sensory frame count and RNG
unchanged. A same-time maintenance/action-completion regression preserves the actual
external resource-disappearance observation. The earlier manual Simulation/core.step
fixture remains a historical plumbing regression; it is not the production freeze gate.

Additional tests cover weak/consistent/50-50/contradictory evidence, failures and
recovery, direct/indirect deduplication, preserved external second-action context,
untimed legacy brains, horizon/floor fallback, passive/IDLE separation, canonical
Python/native timing ownership, backend preflight, sensor incompatibility, exact
checkpoint phases and production hash seeds 1/777. Existing architecture guards
remain; new AST guards constrain owned internal sampling and forbid physical,
resource, action-policy, reward and neural-injection shortcuts.

## Limits

Delay means summarize observation intervals rather than estimating an exact
event-time hazard. Timing moments are cumulative while probability evidence
uses a sliding window; timing adaptation to a changed process is gradual.
Admission stops at the timing capacity. Passive projection follows bounded
supported successors, not exhaustive alternatives over every wait duration.
Conservative external persistence can retain stale context until later ordinary observation; full absence/object persistence is outside this closure. Per-channel concentration is conservative coarse calibration, not Bayesian
joint inference or a proven reliability guarantee. No survival curriculum,
reward/TD propagation, semantic food/water rules or raw physiological planner
simulation was introduced.

## Verification

Stabilization/freeze closure verified on 2026-10-01: **583 pytest passed;
CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted
suites: **156 passed**. Separate production/runtime freeze gates: **10 passed**.
Native Release/observer build, import/headless smokes and `git diff --check` passed.
Current version remains **v0.8.4 ? DONE / FROZEN**; this is not a new milestone.

The stabilized delayed suite has **63 passing cases**. Required commands were executed:

```
python tools/verify.py --full
python -B -m pytest -q tests/test_v084_delayed_homeostatic_learning.py -k "production or one_internal_change or exact_world_continuation or same_time_action"
git diff --check
```

Historical initial v0.8.4 verification on 2026-10-01: **549 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted suites: **122 passed**. Native Release/observer build, import/headless smokes and `git diff --check` passed.

The initial v0.8.4 suite had 32 cases. Stabilization extends that same test file with production runtime and integration regressions.

```
python -B -m pytest -q tests/test_v081_persistence_security.py tests/test_v081_consumables.py tests/test_v082_interoception.py tests/test_v083_homeostatic_valuation.py tests/test_brain_sensor_contract.py tests/test_v084_delayed_homeostatic_learning.py tests/test_architecture_boundaries.py
```

Controlled native examples with default discount 0.1:

| Experience | Progress | Effective confidence | Ambiguity |
| --- | ---: | ---: | ---: |
| Consistent, arrival 2.2 s | 0.107480 | 0.187500 | 0 |
| 50/50 competing bins, arrival 2.2 s | 0.013272 | 0.059631 | 0.499809 |
| Same consistent improvement, arrival 12.2 s | 0.039540 | 0.187500 | 0 |

Physical bins follow `(1,0,6) -> (1,4,6) -> (6,0,6)` with nutrients; the
counterfactual remains `(1,0,6)`. Historical manual-fixture delayed physical progress was 0.086552 versus
zero in the counterfactual. Native planner chooses INTERACT_UP with passive
prediction and IDLE with depth zero, retaining the acquired external knowledge.
These values describe the fixed acceptance protocol, not population survival statistics.

## Historical initial v0.8.4 changed files

- Configuration: `config/settings.py`, `simulation/persisted_settings.py`.
- Acquisition and prediction: `consciousness/core.py`, `consciousness/core_learning.py`,
  `consciousness/learning.py`, `consciousness/backends.py`, `consciousness/planning.py`,
  new `consciousness/temporal_prediction.py`.
- Native evidence/persistence: `cpp/include/se/native_brain_engine.hpp`,
  `cpp/src/native_brain_engine.cpp`, `cpp/src/bindings.cpp`.
- Runtime/persistence: `simulation/simulation.py`, `simulation/continuous.py`.
- Tests: new `tests/test_v084_delayed_homeostatic_learning.py`,
  `tests/test_architecture_boundaries.py`.
- Documentation: `README.md`, `CURRENT_STATUS.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
  `docs/TESTING.md`, `docs/V0_8_1_CONSUMABLES.md`, `docs/V0_8_2_INTEROCEPTION.md`,
  `docs/V0_8_3_HOMEOSTATIC_VALUATION.md`, `docs/V0_8_HOMEOSTASIS_DESIGN.md`, this document.

Total: 25 files, including three new files. Existing immediate valuation and
brain sensor compatibility production helpers remain unchanged.

## Stabilization changed files

- Acquisition/state/planning: `consciousness/backends.py`, `consciousness/core.py`,
  `consciousness/core_learning.py`, `consciousness/learning.py`,
  `consciousness/planning.py`, `consciousness/temporal_prediction.py`.
- Native outcome reuse: `cpp/include/se/native_brain_engine.hpp`,
  `cpp/src/native_brain_engine.cpp`, `cpp/src/bindings.cpp`.
- Owned runtime/persistence: `simulation/continuous.py`, `simulation/simulation.py`.
- Regressions/guards: `tests/test_v084_delayed_homeostatic_learning.py`,
  `tests/test_architecture_boundaries.py`.
- Documentation: `README.md`, `CURRENT_STATUS.md`, `ARCHITECTURE.md`, `ROADMAP.md`,
  `docs/TESTING.md`, this document.

No new settings, test-file milestone, reward learner, survival curriculum or schema
version was added by stabilization. Current version remains v0.8.4.

Stabilization changes **19 existing files**, introduces no new file or milestone, and leaves v0.8.5 planned.
