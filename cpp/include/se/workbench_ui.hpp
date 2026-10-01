#pragma once
#include "se/observer.hpp"
#include <array>
#include <string>
namespace se {
class WorkbenchBrainGPU;
struct PaneRect {
  float x{}, y{}, width{}, height{};
};
struct WorkbenchLayout {
  PaneRect toolbar, dialogue, world, brain, status;
};
WorkbenchLayout workbench_layout(float width, float height, float scale = 1.f,
                                 float left = .23f, float right = .25f);
struct WorkbenchUIState {
  int tool{}, selected_x{-1}, selected_y{-1};
  std::uint32_t selected_object{}, selected_body{}, selected_node{UINT32_MAX};
  bool body_selected{};
  float world_zoom{1.f}, world_pan_x{}, world_pan_y{}, brain_zoom{1.f},
      brain_pan_x{}, brain_pan_y{};
  float left_fraction{.23f}, right_fraction{.25f};
  int relation_filter{};
  std::array<char, 4097> input{};
  std::string dialogue_error, workbench_notice;
  std::array<char, 4097> scenario_path{"scenarios/my_case.sescenario"};
  std::array<char, 257> scenario_name{"My scenario"};
  std::uint64_t scenario_seed{};
  bool open_scenario_popup{};
  std::shared_ptr<const BrainSnapshot> cached_brain;
  BrainDrawData graph;
  int graph_width{}, graph_height{};
  std::shared_ptr<WorkbenchBrainGPU> brain_gpu;
  std::uint64_t brain_rebuilds{}, dialogue_revision{};
};
void draw_workbench(WorkbenchUIState &, const RenderSnapshot &,
                    std::shared_ptr<const BrainSnapshot>,
                    std::shared_ptr<const DialogueSnapshot>,
                    std::shared_ptr<const WorkbenchStatusSnapshot>,
                    WorkbenchCommandChannel *, float scale);
void draw_world_view(WorkbenchUIState &, const RenderSnapshot &,
                     WorkbenchCommandChannel *);
void draw_brain_view(WorkbenchUIState &, std::shared_ptr<const BrainSnapshot>);
void draw_status_view(const WorkbenchStatusSnapshot *, const WorkbenchUIState &,
                      const RenderSnapshot &);
void draw_dialogue_view(WorkbenchUIState &, const DialogueSnapshot *,
                        WorkbenchCommandChannel *,
                        const std::string &notice = {});
std::string format_world_time(double seconds);
} // namespace se
