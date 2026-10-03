# v0.9.2 controlled survival-learning experiment

Frozen base: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65` (main).
Project version: 0.9.2. Cognitive v0.8.4 and scenario v0.9.1 contracts remain frozen.

## Pre-run declaration

Canonical protocol SHA-256 (UTF-8 canonical JSON, without final newline):
`87fd4007f3dc4e81a5a12d8e2fedf5747750f2ed37e466a9c9d6b1729bb8c0e9`.
Artifact byte SHA-256 (including the final newline):
`ea443bbcf3b356ea27d0f069ae716402da7c867cfeb5d7cb1da4e4bb68a48314`.
This canonical checksum was published before the first complete research run. Scenario byte
checksums and complete configuration/geometry are in `scenarios/v092/inventory.json`.
No threshold, seed, episode count, cognitive parameter or physics budget is selected
from evaluation outcomes. A failed proof is a valid completed research run.

## Design

Stage 1: North adjacent physical resource; 32 fresh physical episodes, 6 WorldTime
seconds each. Stage 2: resource two cells North, requiring MOVE then INTERACT;
48 episodes of 9 seconds. Stage 3: withheld East/South/West layouts and translated
North, all with different body coordinates and resource IDs, evaluated before any
consolidation. Stage 4: optional declared consolidation, 8 episodes per direction
(32 total), followed by two 30-second scarcity scenarios with production spawning.
Evaluation horizons: 6, 9, 9, 30 seconds. Zero-payload same-appearance counterfactual:
9 seconds, both fresh and experienced controls.

Training seeds: 92001..92008. Evaluation seeds: 92101..92116, disjoint.
Determinism subset: 92101 and 92102, all stages and groups in reversed group order;
independent processes additionally compare PYTHONHASHSEED=1 and 777.
112 training episodes and 512 primary evaluation trials, plus two counterfactuals.
No adaptive stopping, retries, cherry-picking or rescue training.

All episodes begin at E/N/H=45/12/80. Nutritive payload=40, hydration payload=0;
digestion rate=2.5, efficiency=.75, basal body/brain costs=.3/.1, hydration rate=.08,
MOVE/INTERACT costs=.2/.1. Scarcity uses the normal resource spawner, interval=6,
maximum live resources=2. Defaults elsewhere remain historical 25/25.
Existing interoception, homeostatic valuation and delayed prediction are enabled.
All other cognitive settings retain their production defaults.

Only durable `.sebrain` knowledge moves between training episodes. World, resources,
reserves, WorldTime, event sequence, pending action, planner/editor/dialogue state
are recreated. Four groups independently load the same immutable checkpoint:
FRESH_FULL loads none; EXPERIENCED_FULL loads it normally; EXPERIENCED_NO_DELAYED
changes only delayed_homeostatic_prediction_enabled=False at bootstrap;
EXPERIENCED_NO_MOTIVATION changes only homeostatic_valuation_enabled=False.
Interoceptive sensor topology remains enabled in every group. Evaluation learning
is discarded. Brain byte checksums are verified before/after evaluation.

## Read-only measurement

Recorder advances only through production `run_until(next scheduler timestamp)`;
observations never reach core policy. It samples reserves, physical tension, action
completion, pending decision/plan, resources (including held resources), internal
bins, native relation/timing diagnostics and final causal digest. No graph sync.
Consumption requires resource disappearance, successful completed INTERACT and
actual N increase. Failed first consumption has null time/action metrics; censored
time is the full horizon and censored actions are final completed actions.
Energy spent is sum(max(0, E_previous-E_current)), not net energy loss. Brownout
means any E<=0. J is sum(exp(-lambda*(t_i+t_j)/2)*(T_i+T_j)/2*dt), lambda=.02,
using actual Physiology tension. Timing-observation totals sum per-edge counts,
not independent experiences or consumption events. Repeated zero-time observations add zero area.
Internal-bin acquisition evidence counts upward homeostatic bins after consumption,
not unrelated baseline depletion. Supported learned consequence requires native
relation support>=6 and an associated native temporal observation. Actual Stage 2
plan must contain MOVE_UP then INTERACT_UP before first autonomous MOVE, with
physical cost, no immediate N benefit and usable positive delayed diagnostics.

## Locked acceptance

At least 16 paired cases; success cannot worsen; experienced median censored time
AND actions must decrease strictly; paired wins >=75%; practical improvement in
time OR actions >=20%. Paired comparison is lexicographic success, time, actions, J.
Stage 1 additionally requires actual autonomous physical discovery, N benefit,
subsequent upward internal-bin change and supported timed learned consequence.
Stage 2 requires model-chain evidence in >=75% of experienced trials.
Delayed ablation must remove >=50% of time advantage; motivation ablation must
remove >=50% of J advantage (checked for stages 1, 2 and 4). Stage 3 requires the
translated task and all three withheld directions to pass the behavioral gates
separately. Stage 4 additionally requires lower J and >=15% reduction in energy
spent OR actions, or fewer brownouts. Zero-payload counterfactual must never claim
nutritive consumption or external N gain. All core gates must pass for proof PASS.

Static layouts can produce identical trajectories across seeds. These are declared
deterministic paired cases, not independent population statistics. Planner
candidate diagnostics alone cannot establish causal policy attribution; recorded
plans, physical consequences and ablations must agree. Contradiction observations
are preserved in raw learned evidence; absence of contradiction is reported as
absence, never inferred from a failure to consume.

## Reproduction

```powershell
python tools/verify.py --full
python -m experiments.v092.runner --protocol experiments/protocols/v092_survival.securriculum --output results/v092/full
python -m experiments.v092.runner --protocol experiments/protocols/v092_survival.securriculum --output results/v092/full --mode rerun --workers 3
```

After an interrupted evaluation with all training episodes already saved:

```powershell
python -m experiments.v092.resume --protocol experiments/protocols/v092_survival.securriculum --output results/v092/full --workers 3
```

Resume verifies the locked protocol, immutable checkpoints, completed trial
provenance and final horizons before running only missing trials. Existing
traces are preserved. Independent missing evaluations may run in separate
processes; no training, budget, policy or acceptance threshold is changed.
`resume-log.json` records the interruption recovery. The full reverse-order
determinism audit also covers trials completed after recovery.

Rerun workers parallelize independent seed/scenario cases only; each case keeps
its declared reverse group order. The initial primary run is sequential;
interruption recovery may parallelize only missing isolated evaluations. Offline
`python -m experiments.v092.diagnostics --protocol experiments/protocols/v092_survival.securriculum --output results/v092/full --append-report`
adds ablation-effect and contradiction tables without changing acceptance.

Default scientific FAIL exits 0; `--require-proof` exits 2 for FAIL. Infrastructure
errors raise normally. Modes train/evaluate/report support inspection without
rewriting protocol thresholds. Output must be clean for training/full execution.
Full output is local and ignored; tracked results report includes every primary
per-seed/group row, paired effects, gate failures and checkpoint checksums.

Phase A also resets every episode selection on reconnect, respects optional tooltip
toggle across panes, caps edge-budget slider at the actual 2048 edge limit and
repairs v0.9.1 freeze provenance. No cognitive policy implementation was changed.
v0.9.3 remains long-run stability, boundedness and soak-test scope.
