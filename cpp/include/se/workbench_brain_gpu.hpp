#pragma once
#include "se/observer.hpp"
#include <memory>
struct ImVec2;
struct ImDrawList;
namespace se {
struct BrainGPUTelemetry {
  std::uint64_t uploaded_bytes{}, buffer_rebuilds{}, delta_updates{}, picks{}, gpu_samples{}, buffer_bytes{};
  double upload_cpu_us{},gpu_draw_us{};
};
// Graph VBOs change only when the immutable snapshot/layout changes. Camera
// and filters are shader uniforms, never graph uploads or causal mutations.
class WorkbenchBrainGPU {
public:
  WorkbenchBrainGPU();
  ~WorkbenchBrainGPU();
  void upload(const BrainSnapshot &, std::size_t node_budget, std::size_t edge_budget);
  std::uint32_t pick(float x, float y);
  BrainGPUTelemetry telemetry() const;
  void enqueue(ImDrawList *, const ImVec2 &origin, const ImVec2 &size,
               float zoom, float pan_x, float pan_y, int filter);

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};
} // namespace se
