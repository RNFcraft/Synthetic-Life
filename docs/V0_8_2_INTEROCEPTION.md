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

Historical v0.8.2 did not add valuation. Current v0.8.3 implements an opt-in
learned trajectory component; see [its contract](V0_8_3_HOMEOSTATIC_VALUATION.md).
The stabilization pass excludes internal primitives from spatial anchors and
translation matching while retaining singleton and mixed non-spatial evidence.
Explicit causal field groups now also save perception radius, maintenance and
spawn cadence, and cognitive settings independent of neural enablement.


The v0.8.3 stabilization fix also persists a versioned internal sensor contract
in brain META when internal Cognits or proto-pattern knowledge transfer. The
receiving encoding must match bins and channel order/version before graph
activation. Legacy external-only brains load; legacy internal brains with no
contract fail closed. Brain v6 stays unchanged; no current internal levels or
body state enter this metadata. See [v0.8.3](V0_8_3_HOMEOSTATIC_VALUATION.md).
