#pragma once
#include <array>
#include <cstdint>
#include <functional>
#include <memory>
#include <span>
#include <string>
#include <vector>

namespace se {
// Host infrastructure only. None of these fields are persisted in graph state.
enum class ComputeBackend { CPU_SERIAL, CPU_PARALLEL, GPU };
enum class ComputeMode { AUTO, FORCE_CPU_SERIAL, FORCE_CPU_PARALLEL, FORCE_GPU };
enum class KernelClass { WAVE_PROPAGATION, ACTION_PREDICTION_BATCH, ACTION_EFFECT_BATCH,
                         PLANNER_TRANSITION_BATCH, RELATION_ANALYTICS, MICRO_NEURAL, COUNT };
struct WorkloadShape {
  std::size_t cognits{}, relations{}, frontier{}, states{}, actions{}, pairs{},
      beam{}, horizon{}, dirty_nodes{}, dirty_relations{}, bytes{}, required_revision{}, applied_revision{};
  double average_degree{}, transfer_us{}, synchronization_us{}, queue_us{};
  std::size_t factors{},targets{},traversed_relations{},numeric_units{};
};
struct BackendEstimate { double ema_us{}, units{}; std::uint64_t count{}; };
struct DispatchPolicy { double margin{.20}; unsigned observations{4}; std::size_t memory_budget{512ull<<20}; };
struct KernelTelemetry {
  std::array<BackendEstimate,3> estimates{};
  ComputeBackend selected{ComputeBackend::CPU_SERIAL}, candidate{ComputeBackend::CPU_SERIAL};
  unsigned streak{}; std::uint64_t switches{}; std::string reason{"uncalibrated: CPU serial"};
  double last_us{},last_units{};
  WorkloadShape last_shape{};
};
struct ReductionBatch;
class ComputeDispatcher {
public:
  ComputeMode mode{ComputeMode::AUTO};
  DispatchPolicy policy{};
  bool gpu_available{};
  std::size_t gpu_free_bytes{};
  ComputeBackend select(KernelClass, const WorkloadShape&);
  void sample(KernelClass, ComputeBackend, double us, double units, const WorkloadShape* shape=nullptr);
  void calibrate(KernelClass, const ReductionBatch&);
  const KernelTelemetry& telemetry(KernelClass k) const { return kernels_[std::size_t(k)]; }
private:
  std::array<KernelTelemetry,std::size_t(KernelClass::COUNT)> kernels_{};
  std::array<std::array<std::array<BackendEstimate,3>,24>,std::size_t(KernelClass::COUNT)> costs_{};
  // Bounded work x state-count x active-degree model for the real planner.
  std::array<std::array<std::array<BackendEstimate,3>,16>,24> planner_costs_{};
};
class WorkerPool {
public:
  explicit WorkerPool(unsigned workers=0);
  ~WorkerPool();
  void run(std::size_t count, const std::function<void(std::size_t)>&);
private:
  class Impl; std::unique_ptr<Impl> impl_;
};
WorkerPool& numeric_workers();
// One independent output per segment; multiplication order within a segment is fixed.
struct ReductionBatch {
  std::vector<double> initial, factors;
  std::vector<std::uint64_t> offsets{0};
};
std::vector<double> reduce_absence(const ReductionBatch&, ComputeBackend);
bool cuda_compute_available(std::size_t& free_bytes);
std::vector<double> cuda_reduce_absence(const ReductionBatch&);
}
