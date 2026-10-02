#include "se/workbench_brain_gpu.hpp"
#include "se/workbench_ui.hpp"
#include <algorithm>
#include <cmath>
#include <imgui.h>
#include <unordered_map>
namespace se {
BrainDrawData prepare_brain_draw_data(const BrainSnapshot &s, int width,
                                      int height) {
  BrainDrawData out;
  if (width <= 0 || height <= 0)
    return out;
  auto budget = std::clamp<std::size_t>(std::size_t(width) * height / 1800, 128,
                                        512),
       count = std::min(budget, s.nodes.size());
  std::unordered_map<std::uint32_t, std::pair<float, float>> positions;
  for (std::size_t i = 0; i < count; ++i) {
    auto const &n = s.nodes[i];
    auto hash = n.id * 2654435761u + 1013904223u;
    float angle = float(hash % 10000) * .0006283185f,
          ring = .38f + .58f * float((hash >> 16) % 1000) / 999.f;
    float x = width * .5f +
              std::cos(angle) * std::max(8.f, width * .39f) * ring,
          y = height * .5f +
              std::sin(angle) * std::max(8.f, height * .38f) * ring;
    positions[n.id] = {x, y};
    float active = std::clamp(float(n.activity), 0.f, 1.f);
    out.nodes.push_back({n.id, x, y, 3.5f + active * 3, .18f + active * .82f,
                         n.composite,
                         n.last_active_cognitive_tick == s.cognitive_tick &&
                             s.cognitive_tick != 0});
  }
  for (auto const &e : s.edges) {
    if (out.edges.size() >= std::min<std::size_t>(2048, budget * 4))
      break;
    auto a = positions.find(e.source), b = positions.find(e.target);
    if (a == positions.end() || b == positions.end())
      continue;
    out.edges.push_back(
        {e.source, e.target, a->second.first, a->second.second, b->second.first,
         b->second.second,
         float(std::clamp(.2 * e.confidence + .8 * e.activation, 0., 1.)),
         .5f + float(std::clamp(e.strength, 0., 1.)) * 1.5f, e.relation_type});
  }
  return out;
}
void draw_brain_view(WorkbenchUIState &ui,
                     std::shared_ptr<const BrainSnapshot> snapshot) {
  ImGui::TextDisabled("BRAIN");
  ImGui::SameLine();
  if (ImGui::SmallButton("Fit##brain")) {
    ui.brain_zoom = 1;
    ui.brain_pan_x = ui.brain_pan_y = 0;
  }
  ImGui::SameLine();
  ImGui::SetNextItemWidth(std::max(75.f, ImGui::GetContentRegionAvail().x));
  const char *filters[] = {"All", "Active", "Self action", "Sequential"};
  ImGui::Combo("##relations", &ui.relation_filter, filters, 4);
  ImGui::Separator();
  auto origin = ImGui::GetCursorScreenPos(),
       size = ImGui::GetContentRegionAvail();
  float footer = ImGui::GetTextLineHeightWithSpacing() * 2;
  size.y = std::max(1.f, size.y - footer);
  size.x = std::max(1.f, size.x);
  ImGui::InvisibleButton("BrainCanvas", size,
                         ImGuiButtonFlags_MouseButtonLeft |
                             ImGuiButtonFlags_MouseButtonMiddle |
                             ImGuiButtonFlags_MouseButtonRight);
  auto *d = ImGui::GetWindowDrawList();
  d->PushClipRect(origin, {origin.x + size.x, origin.y + size.y}, true);
  d->AddRectFilled(origin, {origin.x + size.x, origin.y + size.y},
                   IM_COL32(14, 19, 24, 255));
  if (snapshot &&
      (snapshot != ui.cached_brain || ui.graph_width != int(size.x) ||
       ui.graph_height != int(size.y) || ui.uploaded_edge_budget != ui.brain_edge_budget)) {
    ui.graph = prepare_brain_draw_data(*snapshot, int(size.x), int(size.y));
    if (ui.graph.edges.size() > std::size_t(ui.brain_edge_budget))
      ui.graph.edges.resize(ui.brain_edge_budget);
    ui.uploaded_edge_budget = ui.brain_edge_budget;
    ui.cached_brain = snapshot;
    ui.graph_width = int(size.x);
    ui.graph_height = int(size.y);
    if (!ui.brain_gpu)
      ui.brain_gpu = std::make_shared<WorkbenchBrainGPU>();
    ui.brain_gpu->upload(ui.graph);
    ++ui.brain_rebuilds;
  }
  if (!snapshot || snapshot->nodes.empty()) {
    d->AddText({origin.x + 12, origin.y + 12}, IM_COL32(148, 162, 174, 255),
               "No learned graph yet");
    d->PopClipRect();
    ImGui::TextDisabled("Snapshots only / no graph editing");
    return;
  }
  auto &io = ImGui::GetIO();
  bool hover = ImGui::IsItemHovered();
  if (hover && io.MouseWheel)
    ui.brain_zoom =
        std::clamp(ui.brain_zoom * std::pow(1.12f, io.MouseWheel), .4f, 6.f);
  if (hover && (ImGui::IsMouseDragging(ImGuiMouseButton_Middle) ||
                ImGui::IsMouseDragging(ImGuiMouseButton_Right))) {
    ui.brain_pan_x += io.MouseDelta.x;
    ui.brain_pan_y += io.MouseDelta.y;
  }
  auto point = [&](float x, float y) {
    return ImVec2{origin.x + size.x * .5f + (x - size.x * .5f) * ui.brain_zoom +
                      ui.brain_pan_x,
                  origin.y + size.y * .5f + (y - size.y * .5f) * ui.brain_zoom +
                      ui.brain_pan_y};
  };
  ui.brain_gpu->enqueue(d, origin, size, ui.brain_zoom, ui.brain_pan_x,
                        ui.brain_pan_y, ui.relation_filter);
  const BrainNodeVisual *hovered = nullptr;
  float closest = 100;
  for (auto const &n : ui.graph.nodes) {
    auto p = point(n.x, n.y);
    float radius = n.radius;
    if (n.appearing)
      d->AddCircle(p, radius + 2, IM_COL32(125, 211, 252, 90), 20);
    if (n.id == ui.selected_node)
      d->AddCircle(p, radius + 3, IM_COL32(231, 237, 242, 240), 20);
    float distance = std::hypot(io.MousePos.x - p.x, io.MousePos.y - p.y);
    if (hover && distance < radius + 5 && distance < closest) {
      closest = distance;
      hovered = &n;
    }
  }
  if (hovered) {
    if (ImGui::IsMouseClicked(ImGuiMouseButton_Left))
      ui.selected_node = hovered->id;
    auto it = std::find_if(snapshot->nodes.begin(), snapshot->nodes.end(),
                           [&](auto &n) { return n.id == hovered->id; });
    if (it != snapshot->nodes.end() && ui.show_tooltips) {
      ImGui::BeginTooltip();
      ImGui::Text("Cognit #%u%s", it->id + 1,
                  it->composite ? " / composite" : "");
      ImGui::Text("Activity %.3f / confidence %.3f", it->activity,
                  it->confidence);
      ImGui::Text("Last active tick %llu", static_cast<unsigned long long>(
                                               it->last_active_cognitive_tick));
      ImGui::EndTooltip();
    }
  }
  d->PopClipRect();
  ImGui::TextDisabled(
      "%zu / %llu nodes   %zu / %llu edges", ui.graph.nodes.size(),
      static_cast<unsigned long long>(snapshot->total_cognits),
      ui.graph.edges.size(),
      static_cast<unsigned long long>(snapshot->total_relations));
  auto selected =
      std::find_if(snapshot->nodes.begin(), snapshot->nodes.end(),
                   [&](auto &n) { return n.id == ui.selected_node; });
  if (selected != snapshot->nodes.end())
    ImGui::Text("#%u  activity %.3f  conf %.3f", selected->id + 1,
                selected->activity, selected->confidence);
  else
    ImGui::TextDisabled("Wheel: zoom / middle drag: pan");
}
} // namespace se
