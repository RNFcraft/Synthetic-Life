# v0.9.3b — Adaptive Heterogeneous Compute & GPU-First Workbench

Status: **PARTIAL IMPLEMENTATION / NOT A MILESTONE FREEZE**.
Numeric CMake version remains **0.9.3**. Long-run v0.9.3 remains planned.
v0.9.2 remains EXPERIMENT COMPLETED / PROOF NOT ESTABLISHED; v0.9.3a remains
AUDIT COMPLETE / REPRESENTATIONAL-TRANSFER LIMIT IDENTIFIED.

## Implemented compute boundary

`NativeBrainEngine` materializes relation confidence on its owner thread, builds
immutable target segments, and delegates only independent absence products to
`ComputeDispatcher`. Each target preserves the original order of floating
operations: common absence first, then action-conditioned factors. Results return
in sorted target order and original action order. Planner scores, beam ranking,
ties, physics, physiology, thresholds and curriculum are unchanged.

Prediction and action-effect batches use this path; planner transitions reach it
through their existing batch calls. The six kernel classes are independent policy
slots. Wave, relation analytics and micro-neural execution remain serial; an enum
entry does not mean those kernels have been parallelized or ported to CUDA.

CPU parallel uses a lazy process-wide pool of at most eight persistent workers,
fixed contiguous chunks and output indices. No shared floating reduction, RNG,
completion-order merge or graph access occurs on workers. Independent native
engines serialize access to the shared worker pool; concurrent mutation of one
engine is unsupported. Existing long native pybind calls release the GIL.

The optional CUDA kernel uses FP64 round-to-nearest multiplication and subtraction,
one thread per target, with the same sequential factor order and FMA disabled.
It consumes stateless immutable numeric segments, **not a graph mirror**. Thus
graph-resident CSR/SoA, revisions and graph delta uploads are unnecessary for this
kernel. Device allocations are RAII-owned; no Python semantic objects enter CUDA.
GPU timings used by selection include allocation, transfer and blocking result
readback, rather than just device kernel time. No crossover was found in the
tested range; this strategy has not been expanded into graph-dependent kernels.

## Host policy

Modes: `AUTO`, `FORCE_CPU_SERIAL`, `FORCE_CPU_PARALLEL`, `FORCE_GPU`.
Default AUTO starts conservatively in serial. GPU forcing fails clearly when its
backend/device is unavailable. GPU runtime errors in AUTO fall back to serial;
forced GPU errors propagate. CPU builds require neither CUDA nor OpenGL.

Measured cost EMAs are independent per kernel and backend, within 24 bounded
logarithmic work-size buckets. Unknown sizes retain serial rather than extrapolate
a large-array parallel result into a tiny batch. EMA alpha is 0.2. Switching needs
four consecutive boundary decisions with at least 20% estimated improvement.
One reversal/noisy decision resets the streak. Defaults are conservative host
policy choices, not universal crossover constants. Memory/revision eligibility
overrides GPU selection immediately. `configure_compute_policy` exposes bounded
margin, observation count and memory budget; default budget is 512 MiB.

`calibrate_compute` uses bounded synthetic buffers, checks bit patterns against
serial, and measures all available backends without organism state or RNG. It is
explicit/optional and synchronous before execution. There is no live shadow
cognition. The generic shape contains graph/frontier/planner/delta/transfer/queue
and revision fields, but the implemented cost model primarily uses numeric factor
and output counts plus memory/transfer/sync eligibility. It is **not** the full
multi-feature model requested for future graph-dependent workloads. Free GPU memory
is observed at calibration/forcing time; allocation failure is the live fallback.

Policy, caches, measurements, device memory and presentation preferences are absent
from `.sebrain`, `.seworld`, `.sescenario` and causal digests.
Native graph persistence now explicitly zeroes C++ padding while preserving the
v3/v4 byte layout and every numeric field. Existing files still load. Old artifact
checksums can differ because they included uninitialized padding; this difference
is explicitly classified in the results rather than hidden behind a tolerance.

## Profiling

`telemetry.performance.HostProfiler` is output-only and unattached by default.
The host explicitly wraps instance methods; semantic cognition imports no profiler.
Counters keep count, total, EMA, maximum, work units and a 256-sample recent window
for p50/p95. Profiling uses no RNG, event insertion or graph mutation. Closing
restores original methods. Work units currently count boundary calls, not every
traversed edge or beam leaf. Native materialization/evaluation sub-stages are not
all separately instrumented. Timings overlap hierarchically and must not be summed
as mutually exclusive costs. Native dispatcher timing remains host infrastructure.

## Presentation

The existing dedicated observer thread is retained. It consumes immutable latest
snapshots; the runtime never waits for frame presentation. Automatic publications
return immediately without a subscriber, and are capped at approximately 30 Hz
using a host steady clock. Explicit diagnostic/reconnect publication remains
available regardless of rate cap. This clock only suppresses presentation copies;
it does not enter scheduler decisions or stored graph state.

The OpenGL 3.3 vertex shader calculates hash layout directly from unsigned node ID
and generates edge endpoints from endpoint IDs. Pan/zoom/resize are uniforms;
relation filtering remains GPU-side. The normal renderer calls no CPU layout
helper. Persistent VBOs retain numeric ID/visual fields and upload only differing
contiguous slot ranges. Growth reallocates capacity; unchanged snapshots upload
zero bytes. GPU time uses a four-query ring with availability checks; there is no
blocking timer read. Click picking renders encoded IDs into an RGBA8 framebuffer
and reads one pixel. This is synchronous **only on click**, not per hover/frame.
The compatible ImGui CPU layout renderer remains selectable and is used on GPU
shader initialization failure. Hover picking is not implemented in the GPU path.

Settings / Workbench exposes an optional Performance window, compatible renderer
preference, compute mode and existing visual edge budget. Performance displays
kernel EMAs/selection/reasons/switches, CPU frame preparation, GPU draw latency,
upload bytes, buffer capacity/rebuilds and changed ranges. The mode request passes
through an atomic host channel and is applied at a numeric kernel boundary.

## Remaining acceptance work

This implementation does **not** claim the full GPU-first presentation contract:

- Runtime publication still scans/ranks the graph and sends bounded snapshots.
  There is no native create/update/delete dirty journal, monotonic presentation
  revision stream, delta-gap recovery or graph-wide GPU visibility/LOD.
- Upload deltas are renderer-local slot differences, not causal-graph deltas.
- Hidden/minimized observer and independent pane-activity/rate/detail matrices are
  not complete; explicit 15/30/60 controls and telemetry-driven AUTO FPS are absent.
- Full graph-dependent GPU mirror and its create/update/delete/revision/leak suite
  are not implemented; no such mirror is claimed for the stateless kernel.
- Profiler sub-stage coverage and rich workload feature modeling remain incomplete.
- Performance evidence is synthetic plus a short production episode. No long-run
  boundedness, survival proof or representational-transfer repair is established.

## Reproduction

```powershell
python main.py --headless --seconds 10 --compute-mode AUTO --performance-report runs/profile.json
python main.py --headless --seconds 10 --compute-mode AUTO --calibrate-compute
python tools/benchmark_v093b.py --mode FORCE_CPU_PARALLEL --output runs/parallel.json
python tools/benchmark_v093b.py --observer --mode AUTO --output runs/observer.json
python tools/benchmark_v093b.py --observer --legacy --output runs/legacy.json
cmake -S cpp -B cpp/build-cuda -DSE_ENABLE_CUDA=ON -DSE_BUILD_OBSERVER=OFF
cmake --build cpp/build-cuda --config Release
ctest --test-dir cpp/build-cuda -C Release --output-on-failure
cpp/build-cuda/Release/se_compute_benchmark.exe
cpp/build-verify/Release/se_presentation_gpu_tests.exe
python tools/verify.py --full
```

Set `CMAKE_CUDA_ARCHITECTURES` through standard CMake configuration for deployment.
No GPU model is hardcoded. Graphics tests are explicit because headless CI may have
no OpenGL context. Measurements and acceptance limits are in [results](V0_9_3B_RESULTS.md).
