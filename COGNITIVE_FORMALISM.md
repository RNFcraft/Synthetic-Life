# Synthetic Entity v0.4 — Cognitive Formalism

## Memory and internal time

A Place hypothesis combines view similarity, feature stability, self-action transitions and history. Retrieval strength is relevance x confidence x support. Relational targets become kappa structures and persistent Goals. Internal cycles update cognition without advancing World time.

For relational structures R and target T, internal mismatch is `1 - structural_match(R,T)`. Action value may include acquired predicted mismatch reduction and epistemic value from under-sampled generalized cognitive contexts. This is consistency/error reduction, not reward learning.

The current belief is a graph `(P,E)` where `P` are persistent memory Cognits and each `e=(source,target,relation,confidence,experience_tick)` preserves endpoints. Target matching maximizes structural consistency over injective anonymous-role assignments into subsets of current-episode `P`. Goal progress is computed only from rho-predicted bound-relation Cognits; affordance statistics provide uncertainty but no stored target value.

## Observations and substrate

Let `X_t` be the immutable egocentric visual field, `B_t` immutable non-semantic BodySense, and

```text
O_t = (X_t, B_t).
```

Body primitives encode directional contact, holding, and resistance without physical cause labels. `κ_i` is a primitive or composite Cognit, `ρ_ij` a sparse learned Relation, `π_h` a short-lived percept hypothesis, `A_t` an Action, `G_t` a cognitive target, and `D_t` internal tension. The persistent cognitive substrate is `κ+ρ`; neither World state nor transition counters belong to the entity's acquired knowledge representation.

## Homeostasis and conserved waves

For activation indicator `z_i`, trace `h_i`, threshold `θ_i`, and activity `a_i`:

```text
h_i(t+1) = λ_h h_i(t) + (1-λ_h)z_i(t)
θ_i(t+1) = clamp(θ_i(t)+η_h(h_i(t+1)-h*), θ_min, θ_max)
a_i(t+1) = λ_a a_i(t).
```

For positive outgoing relevance `r_ij`, source energy `E_i`, and retention `λ_w`:

```text
B_i = λ_w E_i
E_ij = B_i r_ij / Σ_k r_ik
Σ_j E_ij ≤ B_i.
```

Negative influence has a separately normalized budget. Refractory attenuation and finite propagation are stabilizers.

## Transition evidence is not knowledge

The bounded evidence window stores observations

```text
E_ij(t) = {count(i), count(j), count(i→j), count(i,a), count(i,a→j)}.
```

It estimates

```text
P_E(j|i)   = count(i→j)/count(i)
Lift_E     = P_E(j|i)/P_E(j)
P_E(j|i,a) = count(i,a→j)/count(i,a)
ActionLift = P_E(j|i,a)/P_E(j|i).
```

`TransitionEvidence_t` is a learning scaffold:

```text
accumulate observations → estimate dependence → materialize/update ρ.
```

It may be cleared after consolidation. Runtime cognition does not call evidence prediction. A learned Relation continues to predict after evidence removal. This is the defining v0.4 distinction: evidence supports knowledge formation; materialized ρ is knowledge.

## Relation lifecycle and consolidation

A materialized Relation stores strength `s`, confidence `c`, support `n`, lift, action context, prediction probability `pρ`, uncertainty, contradiction `d`, usefulness `u`, and timestamps.

```text
PROVISIONAL  -- repeated support/confidence --> CONSOLIDATED.
```

For confirmation indicator `y∈{0,1}`:

```text
y=1: c' = c + η+(1-c),    d' = (1-η-)d
y=0: c' = (1-η-)c,        d' = d + η-(1-d).
```

Utility receives a bounded signed update from `y-s`. Sufficient contradiction can demote consolidated ρ; stale weak provisional ρ may die. This is adaptation, not semantic causal inference.

## Graph-native prediction

For active source `i`, candidate action `a`, and applicable Relation:

```text
q_ij^a = a_i · pρ_ij · effective_confidence_ij · context_match(ρ_ij,a)
p_j(S_t,a) = 1 - Π_i(1-q_ij^a).
```

SEQUENTIAL ρ has context match one for every action. SELF_ACTION `ρ_ij^a` matches only its stored action. Common state contributions are computed once and action-conditioned contributions are dispatched by context; this is mathematically equivalent to evaluating every action and does not prune candidates.

Known prediction error is

```text
ε_known = mean_{j∈K}|y_j-p_j|,
K = predicted κ ∪ observed active κ.
```

When `K` is empty, error is neutral and invalid rather than forced to one. Calibration reports rolling Brier and binned ECE.

## Effective agency and controllability

For graph-supported outcome `j`:

```text
C_j(S) = max_a p_j(S,a) - min_a p_j(S,a)
AgencyEstimate(S) = mean_j C_j(S).
```

Confidence is already contained in `q`. AgencyEstimate is an internal research diagnostic, never reward. It measures differentiated predicted consequences, not physical manipulation count. Current Controllability averages `C_j` over active/considered outcomes.

## Representation coverage and selectivity

For observed primitives `Ω_t` and primitives covered by matched patterns `C_t`:

```text
Coverage_t = |C_t|/max(1,|Ω_t|)
RepresentationError_t = 1-Coverage_t.
```

For each pattern:

```text
Selectivity = clamp(E[positive match]-E[recent background match],0,1)
RepresentationQuality = Coverage × MeanPatternSelectivity.
```

Background samples are recent observations without World labels. Quality is telemetry, not an optimization reward.

## Percepts and learned transforms

Local primitives form LocalPercepts. A prior `π_h` and current local percept `o` match by

```text
C(h,o)=w_f Feature+w_s Spatial+w_struct Structure+w_state State+w_t Temporal.
```

Spatial expectation uses the learned action shift `μ_Δ(A_{t-1})`. Means and variances update with Welford recurrence from matched egocentric displacement; no direction transform is predeclared. π persists across a bounded missing window and has internal identity only.

## Composite Cognits

Observed short sequences propose composites through

```text
Birth(P)=w_f Frequency+w_s Stability+w_p PredictionProxy+w_c Compression
        -w_r Redundancy-w_x Complexity.
```

After birth, actual one-step predictive contribution is

```text
Δε_composite = ε_without_composite - ε_with_composite.
```

The same realized observation evaluates both predictions. Positive rolling contribution raises retention; non-positive contribution lowers relative retention. This is a cheap counterfactual-like ablation, not full replay.

## Novelty, tension, goals, and action value

With rarity `r`, valid prediction surprise `e`, representation error `R`, and pattern instability `u`:

```text
Novelty = 1-(1-r)^wr(1-e)^we(1-R)^wR(1-u)^wu
D_t = clamp(Novelty_t(ε_known+Uncertainty_t)(K0+Controllability_t),0,1).
```

Goals are persistent cognitive targets generated from tension, never authored manipulation objectives. Every available action is compared using its graph-predicted future:

```text
V(a)=w_g GoalAlignment+w_i InformationGain+w_n ExpectedNovelty
    +w_c ControllabilityGain-w_l LoopRisk-w_cost PhysicalEffort.
```

No return, reward, policy-gradient, backpropagation, or learned action router exists. Poorly experienced actions have low confidence/high epistemic uncertainty; they receive no push/grab/interact bonus.

## Symmetry and loop state

An epsilon tie set

```text
T={a|max_b V(b)-V(a)≤ε_tie}
```

is resolved from bounded least-use, oldest-use, then a rotating cursor. Scores are unchanged. WorkingTrace loop similarity combines κ overlap, π overlap, action, goal, prediction/representation error, and tension; physical position is excluded.

## General v0.4 formulation

```text
O_t=(X_t,B_t)
→ sensory primitives
→ LocalPercepts and π
→ primitive/composite κ
→ conserved propagation over ρ
→ graph prediction p(S_t,a)
→ error, uncertainty, selectivity, controllability
→ D_t → G_t
→ imagine every Action through ρ
→ symmetry-preserving choice
→ physical consequence
→ TransitionEvidence
→ materialize/confirm/contradict ρ
→ repeat.
```

Engineering safeguards include bounded evidence, graph/candidate caps, finite waves, clamps, scheduled pruning, snapshot validation, and deterministic RNG. Research hypotheses include emergent κ, acquired ρ, percept continuity, intrinsic tension/goals, graph-native imagined consequences, composite contribution, and AgencyEstimate. Passing tests establishes implementation properties, not consciousness or semantic understanding.
