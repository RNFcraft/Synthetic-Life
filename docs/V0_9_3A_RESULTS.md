# v0.9.3a forensic results

## Repository, scope and scientific status

Base and final HEAD: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65`, `main`.
Implementation remains in the working tree; no commit was created. Existing
uncommitted v0.9.2 implementation, observer changes and research artifacts were
preserved. Human milestone: **v0.9.3a**; numeric CMake version: **0.9.3**.
Persistence schema versions are unchanged. Long-run v0.9.3 is still **PLANNED**.

Frozen v0.9.2 baseline preserved: **YES**. Protocol remains
`87fd4007f3dc4e81a5a12d8e2fedf5747750f2ed37e466a9c9d6b1729bb8c0e9`.
Old thresholds changed: **NO**. Old results changed: **NO**.
Durable learned state demonstrably changes behavior, but the declared
delayed-homeostatic causal mechanism was not established in v0.9.2.

v0.9.3a localized the homeostatic credit-assignment failure but did not establish
a valid architecture-general repair. The frozen v0.9.2 result remains unchanged.
No reward signal, policy shortcut or post-hoc acceptance change was introduced.
The audit identifies a concrete representational/transfer limit rather than
claiming that learning generally cannot work.

## Instrumentation

`experiments/v093a/credit_trace.py` streams JSONL from optional generic production
callbacks around events, ordinary temporal acquisition, matched selectivity and
beam expansion. `determinism.py` streams compact subsystem digests and replays a
single first-difference boundary in detail. `report.py` owns fixed episodes,
persistence checks, separate FULL/NO_MOTIVATION runs, independent hashseed probes
and fresh forward/reverse comparisons. Production imports no experiment module.

Observers are None by default. No simulation RNG draw, event scheduling, numeric
setter, forced action or graph synchronization occurs in the sink. Physical IDs
are measurement-only. Existing native numeric getters materialize lazy state;
the new `diagnostic_stored_nodes` API explicitly copies storage without doing so.
The sink retains a stream/count, not an episode history. A candidate batch is
bounded by configured graph/observation capacities; raw JSONL may be large.
Full-state replay retains one boundary, not duplicated state at every event.

Endpoint traces include sensory primitives, prototype occurrence/birth score,
IDs/kinds/patterns, observed endpoint membership, actual action context, exact
delay, window counts/support/lift, thresholds, relation confidence/contradiction,
existence and timing moments. Planner traces contain each actual expansion's
source/projected state, actions, confidence, estimate and exact existing score
terms. They do not recompute or introduce scoring.

`admitted` means an existing materialized relation at that observation, not that
the current window admitted it anew. Its durable support is reported separately
from current-window support. Insufficient support/lift and endpoint birth reasons
are explicit. A threshold-eligible missing edge whose internal quota/lifecycle
history is not available is explicitly marked unresolved; the demonstrated credit
failure does not rely on such a case. No unobserved eviction/merge is invented.

## Single consumption and first broken credit boundary

The frozen adjacent scenario, frozen Stage-1 brain and seed 92001 produce an
autonomous orientation-relative **INTERACT**, completed at **t=0.15 s**.
The physical resource disappears and nutrients increase **12 → 51.625**.
The full sensory observation at the same WorldTime reports bins **(3,4,6)**
instead of **(3,0,6)**. Action attribution uses its actual attempt at t=0,
completion at t=0.15, success=true and observed delay=0.15. No attribution window
was increased. A fresh untrained single episode consumes nothing in its fixed
six-second horizon; it is retained as an observation, not retried until success.

The **first demonstrated lost internal consequence** is the endpoint admission
boundary. Primitive `(0,0,"internal_1",4,STATE_CHANGED)` is physically observed,
but its singleton prototype has **6 occurrences**, required minimum **4**, and
birth score **0.6329224986108895 < 0.66**. No Cognit ID exists for that singleton;
it is absent from `_learn_timed_observation` targets. Thus no INTERACT-to-this-bin
candidate/timing can be formed at that completion. This is an observed current
birth rule, not proof of a sign error, graph exhaustion or lost physical payload.

Root-cause localization: **PROVEN** for this missing endpoint. Valid credit bug
repair: **NOT ESTABLISHED**. Lowering its birth threshold or admitting a special
internal/resource pattern would change acceptance/representation, not repair a
demonstrated implementation omission. No such change was made.

## Eight fixed fresh episodes and transfer limit

The pre-run lock fixes **8** episodes, seeds **92001..92008**, six seconds each,
starting from the frozen Stage-1 brain and carrying only `.sebrain` thereafter.
Consumption counts are **[1,0,0,0,1,1,1,0]**. This is an evidence audit, not a
behavioral acceptance statistic. No resource replenishment or action intervention
is used within these episodes.

| Episode with consumption | Observed changed nutrient bin | Cognit | Birth score | Result |
|---|---:|---:|---:|---|
| 1 | 4 | absent | 0.6329224986108895 | birth score below threshold |
| 5 | 4 | absent | 0.6530265692267344 | birth score below threshold |
| 6 | 4 | 307 | 0.6661804849288302 | endpoint created; support below threshold |
| 7 | 3 | absent | 0.5806386167996135 | different observed bin, birth score below threshold |

Episode 6 exposes the next boundary: the endpoint can exist, but its relevant
action-conditioned candidate has **support 1**, required **6**. For example,
native/Python-mapped source 2 → target 307 with action 17 has timing
`(count=1, mean=0.15, M2=0)`. After save and fresh reload, the same target identity
and timing remain, while candidate support is **0** and no such supported relation
exists. Across all eight roundtrips, durable relation fields and timing moments
match exactly; the window goes from **39 observations to 0** each time.

This is not a persistence omission relative to the current `.sebrain` contract.
The durable representation transfers materialized rho and timing, but cannot
carry the subthreshold positive/negative sufficient statistics needed to admit
rare cross-episode hypotheses. Timing counts are not support denominators: failed
trials have no positive target timing, and lift needs competing observations.
Substituting cumulative timing counts would introduce an unsupported estimator.
The prototype and window requirements therefore impose a concrete acquisition
limit on this evidence path. A durable candidate-evidence representation requires
a separate scoped milestone and explicit transfer/reset semantics.

No supported timed beneficial relation appears in this controlled audit. There
is consequently no legitimate relation to test as surviving pruning, becoming
planner-usable or contributing beneficial homeostatic value. These downstream
gates are **NOT ESTABLISHED**, not fabricated PASS. Save/reload of existing
materialized knowledge works. Identity fragmentation and graph capacity are not
established as the cause of the demonstrated missing singleton; the exact
singleton signature and later target 307 survive transfer.

## Stage-2 motivation audit and score decomposition

Frozen Stage-2 brain, original one-move scenario and seed 92101 were independently
loaded for FULL and NO_MOTIVATION. First two actions agree. The first action
divergence is decision **index 2, t=0.3 s**, with identical body position and
reserves: FULL chooses **MOVE_LEFT**; NO_MOTIVATION chooses **GRAB_DOWN**.
FULL still fails consumption; NO_MOTIVATION succeeds. This is a diagnostic paired
run, not a new Stage-2 proof or changed acceptance gate.

At cognitive tick 15, the best FULL expansion is
`MOVE_LEFT, INTERACT_UP, INTERACT_DOWN, INTERACT_DOWN`, score
**0.6098027395012777**, confidence **0.005801768216719984**.
NO_MOTIVATION's best is `GRAB_DOWN, IDLE, TURN_RIGHT, MOVE_LEFT`, score
**0.6118931249584402**, confidence **0.008305702268198507**.

| Final expansion term | FULL winner | NO_MOTIVATION winner |
|---|---:|---:|
| prior accumulated score | 0.48811692117500177 | 0.4733331713172247 |
| alignment | 0.057427952881410525 | 0.05829450602007465 |
| confidence term | 0.03184453310634664 | 0.03254599283364236 |
| memory term | 0.11984802621606988 | 0.11984802621606988 |
| epistemic term | 0.059693877551020416 | 0.075 |
| target-progress term | 0 | 0 |
| loop term | -0.05712857142857143 | -0.05712857142857143 |
| depth term | -0.09 | -0.09 |
| homeostatic increment | 0 | 0 |

These are different candidate chains, so subtracting their final homeostatic term
alone cannot explain the choice. A shared first-action expansion, MOVE_DOWN,
already shows the mechanism: its immediate score is identical
**0.1381437903415777**, but FULL's usable temporal projection contains **34**
Cognits versus **22** with motivation OFF. Its estimated progress is zero.
The motivation flag gates the call to delayed estimation and therefore external
projection and subsequent confidence/beam branches, not merely an additive
desirability term. The winning chains consequently are not both in both beams.
The exact changing terms include later epistemic/alignment/confidence and prior
accumulation. No mathematically demonstrated sign inversion was found or repaired.
The first shared expansion with a different score is `MOVE_LEFT, IDLE`:
**0.32011770185694877 FULL versus 0.3222393887924778 OFF**.
More directly, the common two-step ordering reverses: `MOVE_LEFT, INTERACT_UP`
scores **0.3364311028487257 FULL versus 0.31797947198258336 OFF**, while
`GRAB_DOWN, IDLE` scores **0.3244900227888592 in both**. The changing terms for
the MOVE_LEFT/INTERACT_UP expansion are epistemic
**0.059693877551020416 versus 0.041666666666666664**, confidence contribution
**0.030564854359544643 versus 0.030149362949184567**, and loop contribution
**-0.05712857142857143 versus -0.057137499999999994**. Alignment, prior, memory,
depth, target progress and homeostatic increment match. The preceding MOVE_LEFT
projection is 26 versus 17 Cognits and cumulative confidence is
**0.1871838054463636 versus 0.2481072126066471**. This records the actual score
ordering mechanism without attributing the inversion to a nonzero desirability
bonus or changing score polarity.
Physical costs remain actual World/Physiology costs; the beam's depth cost is a
separate existing search term. No raw reserves/resource payload enter the planner.

Stage-1 targeted scientific rerun: **NOT RUN**, micro acceptance failed.
Stage-2 targeted scientific rerun: **NOT RUN**, Stage-1 causal chain unconfirmed.
Stage-3/4 survival benchmark rerun: **NOT RUN**. The already declared determinism
subset includes Stage-3/4, and one scarcity_b reproduction diagnoses determinism;
neither is a broad survival-proof rerun or changes original results.

## Exact determinism: first divergence, cause and minimal fix

Expanded independent-process reproduction uses the original scarcity_b scenario,
fresh brain, seed 92101, horizon 30 and **PYTHONHASHSEED=1 versus 777**.
Before the fix, scientific metrics, decisions and trajectory match, but final
digest differs. Event-by-event comparison identifies the first different boundary:

* zero-based event index **1240**;
* event ID **1243**, **SENSORY_CHANGE**, payload 0;
* WorldTime **25.949999999999932**;
* World, physiology, RNG, scheduler, node/relation storage, action and planner
  digests match; selectivity accumulator and state fields differ.

Detailed operation replay proves the cause inside `_match_and_birth`:
`candidate_ids` is built by traversing a hash-ordered primitive observation.
Even integer-ID sets can have different collision layouts depending on insertion.
The unsorted matched dict preserves that order, and `_selectivity_sum` subtracts
old/adds new per-Cognit selectivity in it. Individual Cognit values and deltas are
identical; the initial sum is **4.732369091110645** in both runs. IDs include
**3,4,6,...,33,36,...** in one traversal and **33,3,36,37,6,4,...** in the other.
The final sums are **4.726480672754907** and **4.7264806727549065**; exported
pattern selectivity is **0.14770252102359085** versus **0.14770252102359083**.
Representation quality inherits it and the causal digest correctly differs.

Root cause: **PROVEN**. Minimal architecture-general fix: construct `matched`
by sorted Cognit IDs before its reductions and receive batches. No score,
threshold, float value, physical process or identity is rounded or special-cased.
The actual old physical failure has a hashseed integration regression.
After the fix the same 30-second pair has **exact full-record equality and every
event boundary equal**. A same-process independently reloaded Stage-2 differential
trial also matches every boundary and the full record.

Declared reverse-order comparison: **64/64 exact canonical artifact equality**.
Every JSON field and every sequence is included, including final digest,
decisions, trajectory and planner diagnostics. No host or numeric field was
excluded, rounded or reordered for acceptance. The runner uses the existing JSON
contract for Python tuple/JSON array transport equivalence; the two saved artifacts
are also byte-identical. Its earlier Python-container comparison manifest is
retained separately, rather than mistaken for a causal mismatch.
Expanded independent-process hashseed 1/777 suite: **5/5 full-record matches**
(Stage-1 NO_MOTIVATION and all four Stage-2 groups), plus **1/1** full-record
and every-event match for the previously failing fresh scarcity_b trial.
Historical v0.9.2 digests
remain frozen; they are not expected to be rewritten to the repaired traversal.

## Final validation — 2026-10-03

| Check | Result |
|---|---|
| `python tools/verify.py --full` | PASS: Release build, import/headless smokes, pytest, CTest |
| Normal pytest | **754 passed** |
| Instrumentation + architecture guards | **29 passed** |
| Nine focused physiology/persistence/learning/research/guard suites | **203 passed** |
| Release observer-ON CTest | **2/2 passed** |
| Rebuilt observer-OFF CTest | **1/1 passed** |
| Observer-OFF module: scenario, survival, delayed and forensic suites | **164 passed** |
| Forward/reverse declared subset | **64/64 exact artifacts** |
| Expanded hashseed 1/777 records | **6/6 exact pairs** |
| Previously failing scarcity_b event differential | **all boundaries exact** |
| Independent Stage-2 reload event differential | **all boundaries/full record exact** |
| Stage-2 FULL trace OFF/ON, same brain/seed/scenario | **full record and stored state exact** |
| Trace OFF/ON Stage-2 final digest | `00604ddd686db8310b617e76941100cd8781a24a3ae214a057cae08b8d882508` both |
| `full_graph_sync_calls` | **0** |
| `git diff --check` | **PASS** |

The eight controlled roundtrips preserve existing materialized relation fields
and timing exactly. Their failure is admission/fresh-episode evidence retention,
not a falsely claimed successful credit repair. No 10-hour soak, expanded
survival benchmark, remote CI or exhaustive all-platform determinism is claimed.

## Artifacts, reproduction and remaining limits

Local machine evidence is under `results/v093a/` (gitignored), including
`credit_v2/`, `single_complete/`, `stage2/`, `determinism/first-*`,
`determinism/fixed-hash-*`, `determinism/expanded-hash-*`,
`determinism/differential_fixed/` and `determinism/reverse_fixed/`.
Earlier instrumentation revisions are retained in separate output directories;
they are not silently overwritten. Source code, this report, design and regression
tests are tracked/reviewable; raw traces and transferred brains are local artifacts.

```powershell
python -B -m experiments.v093a.report --mode credit --output results/v093a/new_credit
python -B -m experiments.v093a.report --mode stage2 --output results/v093a/new_stage2
python -B -m experiments.v093a.report --mode differential --output results/v093a/new_differential
python -B -m experiments.v093a.report --mode reverse --workers 3 --output results/v093a/new_reverse
$env:PYTHONHASHSEED='1'
python -B -m experiments.v093a.report --mode hashsuite --output results/v093a/new_hash1
$env:PYTHONHASHSEED='777'
python -B -m experiments.v093a.report --mode hashsuite --output results/v093a/new_hash777
python -B -m pytest -q
```

No credit foundation repair, survival proof or long-run stability claim is made.
The determinism checks cover declared cases and representative independent-process
probes, not every possible scenario/hashseed or platform. Observer-OFF build
validation does not replace a whole alternate-backend research experiment.
Long-run v0.9.3 still needs boundedness, resource/graph lifecycle and soak work.

Files added for v0.9.3a: four `experiments/v093a` modules, forensic tests, design
and this results document. Production changes: generic observer hooks in
`simulation/continuous.py`, `core_learning.py`, `core.py`, `planning.py`, canonical
matched construction, and the native stored-state binding. `.gitignore`, numeric
CMake version, architecture guards, README, CURRENT_STATUS, ROADMAP and TESTING
are updated. Existing v0.9.2/observer working-tree changes remain separate in the
combined diff and were not rolled back.
