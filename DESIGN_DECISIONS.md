# Design Decisions — v0.5.2

## Native mechanics, Python meaning

**Decision:** C++ owns large repetitive numeric and physical mechanics; Python owns semantic interpretation and research policy. **Reason:** graph size and world event volume must not force Python object creation proportional to stored life history. **Consequences:** native APIs return compact IDs/arrays, while semantic code evaluates only relevant participants. `NativeRelation` remains a debug/rare-query compatibility view.

## World migration remains differential

**Decision:** Keep Python World as the executable oracle while enabling C++ `WorldRuntime` feature-by-feature. **Reason:** physical changes can silently alter learned cognition even when the graph is correct. **Consequences:** single-entity action/perception parity is tested over 1000 random actions; normal runtime does not switch until seeded spawning and multi-entity conflict traces match.

## Time and causal order are distinct

**Decision:** WorldTime is continuous float64 seconds and EventSequence is a monotonic ordering identifier. **Reason:** future actions and sensory events may occur between integer one-second heartbeats. **Consequences:** ActionIntent carries both values; EventSequence is never interpreted as elapsed time.

v0.5.1 uses egocentric multi-view topology instead of hidden coordinates, a shared anonymous relational language for experience/memory/targets, deterministic epistemic exploration rather than randomness, cognitive-state subgoals, pre-mutation N-body conflict classification, and a durable-brain versus exact-episode persistence boundary. Failed behavioral results remain explicit rather than being hidden by a procedural solver.

Participant-bound correction: relation type and relation instance are separate. A reusable RELATIONAL Cognit identifies the acquired relation type; a BOUND_RELATION Cognit and SPATIAL rho retain specific internal source/target participants. Affordance evidence is restricted to exploration uncertainty/effect frequency and cannot store target progress. Brain transfer starts a new belief episode without deleting historical cognition.

The first section records the v0.2 foundation retained by v0.3. Later v0.3
entries supersede historical choices where explicitly noted, especially action
tie resolution and snapshot schema.

## Immutable sensory/action boundary

**Decision:** `SyntheticEntityCore` receives only `SensoryFrame` and returns only `Action`. **Reason:** internal dynamics must not exploit simulator truth. **Alternatives:** World/Grid references, object IDs, absolute or unvisited coordinates. **Consequences:** behavioral position metrics exist only in external telemetry.

## Local structural events instead of whole frames

**Decision:** Frames decompose into primitive local channel/change events; exact whole-frame identity remains debug-only. **Reason:** κ should represent reusable local structure. **Alternatives:** frame hashes, embeddings. **Consequences:** matching is transparent but currently limited to exact primitive membership and small same-cell composites.

## Homeostatic excitability

**Decision:** Each κ maintains activity trace, adaptive threshold and refractory state; recurrent input is attenuated by its own trace. **Reason:** frequently active structure must become harder to excite. **Alternatives:** global top-K or hard active-count caps. **Consequences:** activity is locally regulated without a router, though coefficients remain experimental.

## Conserved wave energy

**Decision:** A source divides `available × retention` among outgoing excitatory ρ in normalized proportion; inhibitory edges receive a separate suppression budget. **Reason:** fan-out must not create energy. **Alternatives:** sending the full source activity to every neighbor. **Consequences:** a 100-edge source transmits the same total positive budget as a one-edge source.

## Statistical relation evidence

**Decision:** SEQUENTIAL ρ requires minimum support and lift over target baseline. SELF_ACTION additionally requires conditioned probability to exceed the state-only conditional probability. Evidence uses a 512-transition sliding window. **Reason:** frequency and mere co-activation are not dependency. **Alternatives:** previous-active × current-active edge creation and permanent cumulative counts. **Consequences:** the graph remains sparse and adapts when regimes change.

## Predictions are noisy-or estimates

**Decision:** Per-source empirical conditional probabilities, support confidence, and optional action conditioning combine as `1 - product(1-p_i)`. **Reason:** prediction must arise solely from active κ and observed transitions. **Alternatives:** world simulation, learned dense model. **Consequences:** unseen outcomes are uncertain; correlated causes are not yet de-duplicated.

## Intrinsic tension, not reward

**Decision:** novelty combines rarity, prediction error, and representation error; tension multiplies novelty by error/uncertainty and a controllability baseline. **Reason:** poorly understood potentially controllable experience should generate internal goals without reward. **Alternatives:** exploration bonuses and coordinate novelty. **Consequences:** values are interpretable current-state quantities and are not backpropagated.

## Persistent cognitive goals

**Decision:** goals target κ IDs, inherit tension, blend intensity with inertia, and decay as their neighborhood becomes familiar/predictable. **Reason:** objectives must live in cognitive space and persist across ticks. **Alternatives:** target coordinates or per-tick argmax goals. **Consequences:** measured goals last about 102 ticks on average in the reference experiment.

## Deterministic imagined choice

**Decision:** all six actions are scored by goal alignment, information gain, novelty, controllability, loop risk, and intrinsic cost; stable argmax chooses. **Reason:** actions should follow internal predicted consequences without an RL policy. **Alternatives:** random walk and physical heuristics. **Consequences:** reproducibility is exact, but near-tie ordering currently produces a MOVE_UP bias.

## Bounded working trace and loop score

**Decision:** retain 64 compact internal states and compare periodic Jaccard recurrence for periods 1–8. **Reason:** repeated cognitive experience must reduce predicted-loop attractiveness. **Alternatives:** physical position history inside core. **Consequences:** loop risk is cognitive only; no full episodic memory is implemented.

## Lazy relation confidence

**Decision:** ρ stores `last_update_tick`; effective confidence applies exponential elapsed-time decay only on access. **Reason:** future billion-edge graphs cannot be globally decayed each tick. **Alternatives:** scanning all ρ. **Consequences:** stale deletion still performs a baseline graph scan once per tick and remains a scaling limitation.

## Snapshot schema v2

**Decision:** serialize world, exact RNG state, graph, transition window, sensory previous values, working trace, goal and action state. Reject all other schema versions. **Reason:** continuation must be deterministic and silent corruption is unacceptable. **Consequences:** files are trusted experiment artifacts; RNG tuple encoding uses isolated base64 pickle bytes.

## v0.3: symmetry is resolved after scoring

**Decision:** Build an epsilon tie set and balance it from bounded choice history, oldest use, then a tie-only cursor. **Reason:** direction ordering is an implementation artifact, while a genuine score advantage must remain authoritative. **Alternatives:** direction bonuses, randomness, coordinate exploration, fixed argmax. **Consequences:** scores retain their meaning and exact movement ties balance to within one choice.

## v0.3: prediction and representation errors remain separate

**Decision:** Known prediction error is valid only over known predicted/matched κ; primitive coverage independently determines representation error. **Reason:** recognizing nothing is not evidence that known predictions were maximally wrong. **Alternatives:** forcing empty prediction error to one. **Consequences:** empty experiences produce finite uncertainty/representation tension without a fake error spike.

## v0.3: percept identity is an internal short-lived hypothesis

**Decision:** Link local event groups into bounded π tracks using feature, learned spatial, structural, state and temporal evidence. **Reason:** recurrent sensory structures need continuity without world IDs. **Alternatives:** world-object identity, long-term maps, no continuity. **Consequences:** tracks bridge motion and short absence but may swap under ambiguity.

## v0.3: sensorimotor geometry is learned

**Decision:** Maintain per-action Welford statistics for observed π centroid shifts, initialized with zero support and broad variance. **Reason:** egocentric transforms must emerge from action-conditioned experience. **Alternatives:** hardcoded opposite-direction shifts. **Consequences:** learned means also contain external-motion and matching noise.

## v0.3: anchored and tolerant hypotheses coexist

**Decision:** Generate exact-offset and translation-normalized pattern candidates under the same evidence machinery. **Reason:** invariance should compete rather than be declared universally. **Alternatives:** global position ignoring or embeddings. **Consequences:** basic translation matching works; model-selection calibration remains incomplete.

## v0.3: composites are ordinary Cognits

**Decision:** Encode composites as graph-shaped CognitPatterns referencing κ and temporal relations. **Reason:** recursive abstraction should reuse graph activation, prediction and lifecycle. **Alternatives:** a separate higher-level engine. **Consequences:** κ recursively compose up to a configured depth and dependencies require protection.

## v0.3: dependency reference protection

**Decision:** Child κ referenced by live composites cannot be deleted. **Reason:** deletion must never leave dangling pattern references. **Alternatives:** atomic cascade or graceful partial patterns. **Consequences:** integrity is deterministic, but stale composites can retain weak children.

## v0.3: bounded observed-sequence discovery

**Decision:** Composite candidates arise only from short recent active sequences with at most four unique participants. **Reason:** full κ combinations are computationally and epistemically unjustified. **Alternatives:** pairwise or combinatorial scans. **Consequences:** repeated short structure is discoverable; long/interleaved structure is missed.

## v0.3: richer loop distance

**Decision:** Compare κ overlap, π identity, action, goal, prediction/representation errors and tension. **Reason:** equal active sets with different intentions/actions are not the same experience. **Alternatives:** κ Jaccard alone or physical position. **Consequences:** loop evidence is more specific and remains internal.

## v0.3: schema replacement

**Decision:** Require snapshot v3 and explicitly reject v2. **Reason:** percept, composite, tie and calibration state are required for deterministic continuation. **Alternatives:** silent partial defaults. **Consequences:** old snapshots need deliberate migration.

## v0.3: scheduled retention candidates

**Decision:** Compute utility/confidence/predictive/recency retention over bounded rotating batches and use a deletion queue while protecting composite dependencies. **Reason:** lifecycle must be gradual and avoid mass deletion. **Alternatives:** delete rare κ or globally select weak nodes. **Consequences:** candidate work is bounded, though homeostasis is still O(κ) per tick.

## v0.4: persistent manipulation laboratory

**Decision:** Default to a configurable 30×30 world with zero initial objects, deterministic interval spawning up to ten, and no autonomous object motion or state changes. **Reason:** persistent change must be attributable to entity action or the isolated spawn process. **Alternatives:** moving scenery and game objectives. **Consequences:** intervention-like evidence is interpretable.

## v0.4: physical action composition

**Decision:** MOVE naturally pushes; directional GRAB uses an abstract held-slot; movement carries; RELEASE places along orientation; directional INTERACT toggles binary state. **Reason:** a small rule set yields persistent action consequences without semantic motor labels. **Alternatives:** PUSH/PULL actions or extended carried-body geometry. **Consequences:** holding is sensed explicitly; carried-object collision geometry is simplified.

## v0.4: non-semantic BodySense

**Decision:** Immutable touch, holding, and resistance channels are decomposed as ordinary primitives. **Reason:** bodily consequences are necessary evidence, while wall/object/outcome labels would leak World semantics. **Alternatives:** semantic result enums inside reasoning or a hardcoded body module. **Consequences:** multimodal structure can emerge from the shared κ/ρ substrate.

## v0.4: evidence is not knowledge

**Decision:** TransitionModel only accumulates bounded evidence for materialization; runtime prediction and imagination exclusively traverse ρ. **Reason:** accurate prediction with zero ρ contradicts the κ+ρ hypothesis. **Alternatives:** rolling counters as a parallel predictor. **Consequences:** clearing evidence preserves acquired prediction and relation ablation removes it.

## v0.4: provisional, consolidated, and contradicted ρ

**Decision:** One Relation lifecycle begins PROVISIONAL, can consolidate through support/confidence, and weakens through explicit contradictory outcomes. **Reason:** v0.1 overproduced edges while v0.3 sometimes produced none; decay alone cannot represent counterevidence. **Alternatives:** one hard birth threshold or two memory systems. **Consequences:** graph knowledge can strengthen, adapt, demote, and gradually disappear.

## v0.4: shared graph prediction for all actions

**Decision:** Compute common causes once and dispatch SELF_ACTION contributions by candidate action, while scoring every action. **Reason:** independent full scans scale poorly with fifteen motor symbols. **Alternatives:** top-k pruning or redundant prediction. **Consequences:** mathematical results are preserved without a hidden router.

## v0.4: agency remains diagnostic

**Decision:** AgencyEstimate is the mean graph-prediction spread across actions; physical manipulations never add value directly. **Reason:** activity count is not learned agency. **Alternatives:** push/grab/interact rewards. **Consequences:** small or non-monotonic agency is a valid experimental result.

## v0.4: empirical composite usefulness and pattern selectivity

**Decision:** Composite retention uses one-step `error_without-error_with`; patterns report positive minus recent-background match separately from coverage. **Reason:** compression proxies and near-perfect coverage can preserve useless/general patterns. **Alternatives:** full replay or World-labelled negatives. **Consequences:** diagnostics are more discriminating but remain short-horizon online estimates.

## v0.4: scheduler isolation and schema v4

**Decision:** Speed is a wall-clock scheduler concern with 1×=1 tick/s, fractional credit, PAUSE/STEP/MAX; persistence requires schema v4. **Reason:** speed must not alter cognition, and deterministic continuation needs physical/spawn/body/enriched-relation state. **Alternatives:** ticks per rendered frame and partial snapshot defaults. **Consequences:** v3 snapshots are explicitly rejected and UI preference is not scientific state.
