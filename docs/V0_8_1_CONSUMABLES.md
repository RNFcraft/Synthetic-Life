# v0.8.1 Physical Consumables

## Implemented now

`Settings.resource_spawning_enabled` is off by default. When enabled,
`ContinuousRuntime` schedules resource events on the existing native
`WORLD_SPAWN` scheduler type with payload `1`; payload `0` retains the generic
spawn contract. The interval is in simulated WorldTime seconds. Scheduler IDs
order ties, and the existing simulation RNG chooses a free cell and a bounded
numeric resource channel. The optional settings set the interval, maximum live
resources, and nutrient/hydration payloads. Both World implementations reject
invalid payloads and capacity overflow.

World owns resource channel and payload. Production C++ `WorldRuntime` owns
spawn, occupancy validation, interaction, removal, pending consequence and
restoration. `NativeWorld` exposes views only. Python `World` is the reference
oracle. Cognition sees the existing bounded numeric state channel, never the
payload or a resource semantic label. Existing `INTERACT_*` is the physical
consumption primitive. A successful interaction removes the object, and
Simulation drains one World consequence into the abstract
`Physiology.apply_consequence(nutrients=..., hydration=...)` seam. A failed or
repeated interaction produces no consequence. Generic object toggling remains
unchanged.

Snapshots with enabled resources or live resource state use semantic snapshot
v6; continuous `.seworld` uses v9. Baseline v5/v8 remains valid when resources
are disabled. Resource configuration, payload, pending consequence, RNG state,
native WorldTime and event sequence, and pending scheduler events are saved.
The physical resource and physiology state is absent from `.sebrain`.
Legacy pickle encoded RNG snapshots are rejected by normal loaders. They
require a separately reviewed trusted migration; the loader never executes
the pickle. Container framing remains version 1.

## Planned later

v0.8.2 now adds [bounded nonsemantic interoception](V0_8_2_INTEROCEPTION.md).
v0.8.3 action valuation remains planned. The current core has no resource
reward, resource action rule, or delayed physiological consequence model.

`BeliefScene.best_binding()` currently enumerates `m!/(m-n)!` participant
assignments and up to eight transforms per assignment. Larger scenes can
therefore spend factorial time in relational binding. A future optimization
needs admissible pruning that preserves score, tie order and exact binding.
`CompositeTracker.observe()` also deduplicates temporal sequences with
`dict.fromkeys`, losing repeated Cognit IDs and their positions. Repairing
that semantic representation requires separate design and regression tests.
