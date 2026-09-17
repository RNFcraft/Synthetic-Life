# v0.8 Homeostasis Design

## Goal and non-goals

v0.8 introduces the first causal internal organism state. The intended loop is
physiology → non-semantic experience → ordinary learned prediction → planner →
Action → World consequence → physiology. Physiology defines stable ranges; it
does not encode which object or action restores them.

This design does not introduce language, social behavior, a reward variable,
hardcoded food seeking, direct brain writes, planner bypasses, TD learning, an
LLM policy, or activity-dependent CPU/FFI costs.

## v0.8.0 model and authority

`Simulation.physiology` is the single authoritative owner of organism state.
It is a separate subsystem, not state inside `SyntheticEntityCore` or the
planner. The authoritative bounded variables are:

```text
0 <= energy     <= max_energy
0 <= nutrients  <= max_nutrients
0 <= hydration  <= max_hydration
```

Hunger and homeostatic tension are exact derived projections and are not
persisted as independent authority. `HomeostaticEvaluator` knows only state and
target ranges. For each variable it computes a clamped normalized deficit;
total tension is the mean squared deficit and therefore remains finite in
`[0, 1]`.

Updates use monotonically increasing simulation `WorldTime` only. Basal body
and brain metabolism consume energy, hydration decays, and bounded digestion
converts nutrient reserve into energy. Successful movement and interaction
have deterministic costs. No cost depends on FPS, wall clock, CPU work,
planner cycles, FFI calls, or renderer activity. At insufficient energy a
voluntary action becomes `IDLE`; time, digestion, sensation, and cognition can
continue. Zero energy is brownout, not death.

## Boundaries

The core/planner and observer receive an immutable `PhysiologySnapshot` with
energy, nutrients, hydration, derived hunger, tension, and WorldTime. They
cannot mutate the authoritative subsystem. v0.8.0 does not yet use tension to
score actions. That belongs to v0.8.3 after non-semantic interoception and
learned consequence prediction exist.

`apply_consequence(nutrients=..., hydration=...)` is the explicit future World
consequence seam. It is deliberately unaware of food, water, coordinates,
objects, Actions, Goals, or policy. Consumable objects and scheduled external
spawn belong to v0.8.1/v0.8.2 and must call this seam only after a real physical
transition.

## Persistence

Physiology payload v1 stores only authoritative energy, nutrients, hydration,
and last processed WorldTime. Semantic snapshot schema is v5 and continuous
`.seworld` is v8. Loading older snapshots deterministically creates configured
initial physiology and advances it to saved WorldTime. `.sebrain` remains v6:
transferring learned cognition does not transfer the current organism body.

Save/load tests cover exact physiological continuation alongside the existing
scheduler, cognition, planner, language, neural, and Assembly continuation.

The accepted v0.8.0 canonical digest is
`8dfb1595eb4bd704f7d0b8780f1e58d725f7ae6b50df47f43937efc45797580c` for
both `PYTHONHASHSEED=1` and `777`. The workload retains `79` actions and `655`
scheduler events; the digest changes intentionally because physiology and its
configuration are now persisted causal state.

## Learning hooks and future milestones

The consequence seam plus immutable before/after projections provides the
future evidence boundary:

```text
Action → physical World transition → physiology delta → ordinary evidence
```

No separate food-value memory is introduced. Later learned physiological
knowledge must use ordinary interoceptive Cognits and action-conditioned
Relations. Delayed consequences remain model-based multi-step prediction, not
reward backpropagation.

- v0.8.1: physical consumables and deterministic external spawn;
- v0.8.2: bounded non-semantic interoception;
- v0.8.3: trajectory-level homeostatic planner valuation;
- v0.8.4: learned homeostatic consequences and ablations;
- v0.8.5: resource constraints and curriculum;
- v0.8.6: long-life stability;
- v0.8.7: observation and experiments;
- v0.8.8: freeze audit.
