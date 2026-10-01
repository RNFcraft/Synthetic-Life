# v0.8.4 Delayed and calibrated homeostatic consequence learning

Implemented on the v0.8.3 stabilization baseline. This is a controlled
model-based learning milestone; v0.8.5 survival curriculum remains planned.
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
Unsuccessful actions skip that observation transition. A later passive
observation cannot retroactively attach an unrelated improvement to the failed
action. Successful IDLE also provides passive timing evidence. Observations
without a newly completed action provide passive evidence directly.

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
timing evidence supplies no delayed bonus.

`.seworld` restores timing moments, native transition history, actual observed
endpoint/time and pending completed action, alongside the existing scheduler,
cognition frontier and planning session. Exact continuous continuation is
tested with non-default parameters at multiple frontier phases.

`.sebrain` transfers materialized graph and timing knowledge but no observation
window, pending action, last sensory time, active state, plan or body reserves.
Internal sensor topology validation remains unchanged and fail-closed.
Native binary graph v4 appends timing rows to the v3 payload; v3 remains readable
and is still written when no timing knowledge exists. Outer brain v6/reference
v4 and continuous world v10 container schemas remain unchanged. Python timings
use an optional LEAR field; explicit native snapshot exports are persistence
data, not live numeric mirrors.

Diagnostics are detached: homeostatic component/confidence plus passive depth,
cumulative elapsed time, ambiguity, witness count and projected Cognit IDs.
There are no planner reads of raw Physiology, resource payload or object policy.

## Controlled physical acceptance

The native fixture repeats 32 interleaved interaction/IDLE trials with a resource
next to the body. Initial energy is 15, nutrients zero. Real successful INTERACT
adds 60 nutrients but does not immediately raise the energy bin. After two
WorldTime seconds, real Physiology digestion raises energy to 75. Both immediate
and delayed frames pass through the real transducer, `core.step`, ordinary
pattern births and relation materialization. Probabilities are never initialized
by the test.

The counterfactual has the same appearance and position but no nutrient payload.
Both resources carry one unit of hydration because World forbids an entirely
empty resource. Hydration starts at 80, so this payload does not cross a sensor
bin. Only the nutritive case learns positive delayed energy progress and changes
planner ranking. Setting passive depth to zero removes its positive valuation;
there is no direct SELF_ACTION shortcut to the delayed energy improvement.
Fixture rates, actions, placement and trial resets are controlled. This proves
the physical-to-model-to-choice slice, not autonomous discovery or survival.

Additional tests cover weak/consistent/50-50/contradictory evidence, failed
actions, duplicates, unknown mass, temporal horizon, chain confidence, equal
improvement at different delays, passive propagation before another action,
OFF equivalence, settings migration, Python/native parity, hash seeds 1/777,
brain transfer and exact continuous persistence. Architecture guards prohibit
physical and resource access in the new predictor and homeostatic semantics
in the native temporal evidence code.

## Limits

Delay means summarize observation intervals rather than estimating an exact
event-time hazard. Timing moments are cumulative while probability evidence
uses a sliding window; timing adaptation to a changed process is gradual.
Admission stops at the timing capacity. Passive projection follows bounded
supported successors, not exhaustive alternatives over every wait duration.
Per-channel concentration is conservative coarse calibration, not Bayesian
joint inference or a proven reliability guarantee. No survival curriculum,
reward/TD propagation, semantic food/water rules or raw physiological planner
simulation was introduced.

## Verification

Verified on 2026-10-01: **549 pytest passed; CTest Release 2/2 passed** via `python tools/verify.py --full`. Required targeted suites: **122 passed**. Native Release/observer build, import/headless smokes and `git diff --check` passed.

The new delayed suite contains 32 passing cases; the added temporal architecture guard also passes.

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
counterfactual remains `(1,0,6)`. Delayed physical progress is 0.086552 versus
zero in the counterfactual. Native planner chooses INTERACT_UP with passive
prediction and IDLE with depth zero, retaining the acquired external knowledge.
These values describe the fixed acceptance protocol, not population survival statistics.

## Changed files

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
