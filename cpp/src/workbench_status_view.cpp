#include "se/workbench_ui.hpp"
#include <algorithm>
#include <cstdio>
#include <imgui.h>
namespace se {
namespace {
void metric(const char *label, const char *value) {
  ImGui::TableNextRow();
  ImGui::TableSetColumnIndex(0);
  ImGui::TextDisabled("%s", label);
  ImGui::TableSetColumnIndex(1);
  ImGui::TextUnformatted(value);
}
void number(const char *label, double value) {
  char out[64];
  std::snprintf(out, sizeof(out), "%.3f", value);
  metric(label, out);
}
void count(const char *label, std::uint64_t value) {
  auto out = std::to_string(value);
  metric(label, out.c_str());
}
void bar(const char *label, double value, double maximum, ImVec4 color) {
  ImGui::TextDisabled("%s", label);
  ImGui::SameLine();
  char text[64];
  std::snprintf(text, sizeof(text), "%.1f / %.1f", value, maximum);
  float width = ImGui::CalcTextSize(text).x;
  ImGui::SameLine(std::max(ImGui::GetCursorPosX(),
                           ImGui::GetWindowContentRegionMax().x - width));
  ImGui::TextUnformatted(text);
  ImGui::PushStyleColor(ImGuiCol_PlotHistogram, color);
  ImGui::ProgressBar(
      float(std::clamp(value / std::max(1., maximum), 0., 1.)),
      {ImGui::GetContentRegionAvail().x, ImGui::GetFontSize() * .5f}, "");
  ImGui::PopStyleColor();
}
} // namespace
void draw_status_view(const WorkbenchStatusSnapshot *s,
                      const WorkbenchUIState &ui, const RenderSnapshot &world) {
  if (!s) {
    ImGui::TextDisabled("STATUS");
    ImGui::TextWrapped(
        "Attach a runtime status channel to inspect physiology and planning.");
    return;
  }
  if (ImGui::CollapsingHeader("PHYSIOLOGY", ImGuiTreeNodeFlags_DefaultOpen)) {
    bar("Energy", s->energy, s->energy_max, {.18f, .62f, .85f, 1});
    bar("Nutrients", s->nutrients, s->nutrients_max, {1, .48f, .10f, 1});
    bar("Hydration", s->hydration, s->hydration_max, {.26f, .72f, .85f, 1});
    if (ImGui::BeginTable("Derived", 2, ImGuiTableFlags_SizingStretchProp)) {
      number("Hunger", s->hunger);
      number("Tension", s->tension);
      metric("Energy state", s->energy_depleted ? "DEPLETED" : "AVAILABLE");
      ImGui::EndTable();
    }
  }
  if (ImGui::CollapsingHeader("INTEROCEPTION",
                              ImGuiTreeNodeFlags_DefaultOpen)) {
    if (!s->interoception_enabled)
      ImGui::TextDisabled("Disabled in runtime Settings");
    else {
      ImGui::Text("Bins: %d / %d / %d  (0..%d)", s->bins[0], s->bins[1],
                  s->bins[2], s->bin_count - 1);
      ImGui::TextDisabled("Targets: %d / %d / %d", s->target_bins[0],
                          s->target_bins[1], s->target_bins[2]);
      ImGui::TextDisabled("Last sensed: %.3f s", s->internal_observed_at);
    }
  }
  if (ImGui::CollapsingHeader("COGNITION")) {
    if (ImGui::BeginTable("CognitiveMetrics", 2,
                          ImGuiTableFlags_SizingStretchProp)) {
      count("Cognits", s->cognits);
      count("Relations", s->relations);
      count("Active Cognits", s->active_cognits);
      metric("Active Relations", "not exported");
      count("Micro Cognits", s->micro_cognits);
      count("Micro Relations", s->micro_relations);
      count("Assemblies", s->assemblies);
      ImGui::EndTable();
    }
  }
  if (ImGui::CollapsingHeader("PLANNER", ImGuiTreeNodeFlags_DefaultOpen)) {
    if (ImGui::BeginTable("Planning", 2, ImGuiTableFlags_SizingStretchProp)) {
      metric("Last completed", s->current_action.c_str());
      metric("Delayed prediction",
             s->delayed_prediction_enabled ? "ON" : "OFF");
      if (s->has_plan) {
        number("Plan score", s->plan_score);
        number("Plan confidence", s->plan_confidence);
      } else
        metric("Plan", "none");
      number("Homeostatic component", s->homeostatic_component);
      number("Prediction confidence", s->prediction_confidence);
      if (s->has_temporal_prediction) {
        count("Passive depth", s->passive_depth);
        number("Predicted delay (s)", s->predicted_delay);
        number("Ambiguity", s->ambiguity);
      } else
        metric("Timing evidence", "unavailable");
      ImGui::EndTable();
    }
    if (!s->planned_actions.empty()) {
      ImGui::TextDisabled("Current plan");
      for (auto const &action : s->planned_actions)
        ImGui::TextUnformatted(action.c_str());
    }
  }
  if (ImGui::CollapsingHeader("RUNTIME")) {
    if (ImGui::BeginTable("Runtime", 2, ImGuiTableFlags_SizingStretchProp)) {
      metric("WorldTime", format_world_time(s->world_time).c_str());
      count("Event sequence", s->event_sequence);
      count("Actions", s->actions_completed);
      count("Pending events", s->pending_events);
      number("UI FPS (wall clock)", ImGui::GetIO().Framerate);
      ImGui::EndTable();
    }
  }
  if (!s->last_command_result.empty()) {
    ImGui::Separator();
    ImGui::TextWrapped("%s", s->last_command_result.c_str());
  }
  if (ui.selected_object || ui.body_selected) {
    ImGui::Separator();
    ImGui::TextDisabled("SELECTION / PHYSICAL DEBUG");
    for (auto const &o : world.objects)
      if (o.id == ui.selected_object) {
        const char *kind =
            o.presentation_kind == PresentationKind::Food    ? "Food"
            : o.presentation_kind == PresentationKind::Water ? "Water"
            : o.presentation_kind == PresentationKind::OtherResource
                ? "Resource"
                : "Neutral";
        ImGui::Text("%s #%u / %d, %d", kind, o.id, o.x, o.y);
        ImGui::Text("Appearance %d", o.state);
        ImGui::Text("Payload N %.1f / H %.1f", o.nutrients, o.hydration);
      }
    for (auto const &b : world.bodies)
      if (ui.body_selected && b.id == ui.selected_body) {
        ImGui::Text("Entity #%u / %d, %d / %c", b.id, b.x, b.y, b.orientation);
        ImGui::Text("Holding object #%u", b.held_object_id);
      }
  }
}
} // namespace se
