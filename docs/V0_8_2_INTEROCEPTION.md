# v0.8.2 Non-Semantic Interoception

Implemented as an opt-in ordinary sensory path. `interoception_enabled=False`
preserves prior behavior. At `SENSORY_CHANGE`, physiology advances to WorldTime,
then external and internal frames are captured at the same causal instant.
The pure transducer quantizes three reserve/max ratios into numeric levels
`0..bins-1`; `interoception_bins` is 2–32 (default 8). The cognitive boundary
receives no raw reserves, hunger labels, object identities, or advice.

`SensoryEventLayer` emits neutral `internal_0` through `internal_2` primitives.
They use ordinary pattern, Cognit, transition, and relation learning. Spatial
perception and place memory receive only external primitives. Neural
micro-receptors remain external-only in this first slice.

The internal temporal state and pending frame persist in semantic snapshot v7,
discrete `.seworld` v4, and continuous `.seworld` v10. Older artifacts still
load. Physiology, resource,
interoception, world topology and neural sensory settings merge once before
constructing the runtime; incompatible explicit Settings are rejected.
`.sebrain` remains v6: learned Cognits may transfer, current body reserves and
episode interoceptive activation do not.

Ablation uses the same seed and world with the feature OFF versus ON. OFF has
no internal primitives; ON has bounded sensory evidence. Neither mode gains a
direct physiological action rule. Improved survival is not claimed.

v0.8.2 does not score actions by physiological need.

interoception is sensory evidence, not reward.

v0.8.3 may introduce learned trajectory-level homeostatic valuation; it is not
implemented here.
