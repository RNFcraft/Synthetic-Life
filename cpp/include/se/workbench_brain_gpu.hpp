#pragma once
#include "se/observer.hpp"
#include <memory>
struct ImVec2;
struct ImDrawList;
namespace se {
// Graph VBOs change only when the immutable snapshot/layout changes. Camera
// and filters are shader uniforms, never graph uploads or causal mutations.
class WorkbenchBrainGPU {
public:
  WorkbenchBrainGPU();
  ~WorkbenchBrainGPU();
  void upload(const BrainDrawData &);
  void enqueue(ImDrawList *, const ImVec2 &origin, const ImVec2 &size,
               float zoom, float pan_x, float pan_y, int filter);

private:
  class Impl;
  std::unique_ptr<Impl> impl_;
};
} // namespace se
