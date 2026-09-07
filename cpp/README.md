# Synthetic Entity v0.5.2 C++ engine

This is a hybrid runtime, not a rewrite of the Python intelligence layer. Python owns semantic Cognit patterns, goals, memory policy, BeliefScene, planner scoring and experiments. In `backend="native"`, the in-process pybind11 `NativeBrainEngine` is the sole continuously changing numeric graph authority.

Implemented native responsibilities include Cognit structure-of-arrays state; permanent deletion tombstones; sparse versioned Relation handles; provisional/consolidated payloads; wave and batch prediction; bounded factorized TransitionEvidence; lazy quota-aware materialization; native relation outcomes/lifecycle; exact lazy homeostasis; and checksummed binary graph persistence. Normal runtime has no full Python/native graph synchronization.

The module also exposes a `WorldRuntime` foundation covering single-entity movement, pushing, grab/carry/release, interaction, turning, resistance, SensoryFrame mechanics, continuous `double` WorldTime and independent EventSequence validation. A 1000-action differential test passes against Python World. Python remains the normal authoritative World until native seeded spawning and multi-entity conflict resolution are complete.

Build and verify:

```powershell
cmake --build cpp/build --config Release
ctest --test-dir cpp/build -C Release --output-on-failure
python -m pytest -q
python -m experiments.v052_lockstep --seed 77 --steps 100
```

`runs/v052-native-scaling.csv` contains kernel scaling measurements through one million Cognits. `runs/v052-entity-benchmark-10k.json` contains the real growing Entity run: 25.43 s at 1K and 332.01 s at 10K, with the final 5K window sustaining 29.28 actions/s. See `V0_5_2_HYBRID_REPORT.md` for acceptance status.
