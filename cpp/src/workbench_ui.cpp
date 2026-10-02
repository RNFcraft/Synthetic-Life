#include "se/workbench_ui.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <imgui.h>
namespace se {
WorkbenchLayout workbench_layout(float w, float h, float scale, float left,
                                 float right) {
  w = std::max(1.f, w);
  h = std::max(1.f, h);
  float gap = 4.f * scale, top = std::min(56.f * scale, h * .18f),
        body = std::max(1.f, h - top - gap);
  left = std::clamp(left, .16f, .30f);
  right = std::clamp(right, .20f, .32f);
  float lw = w * left, rw = w * right,
        cw = std::max(1.f, w - lw - rw - 2 * gap), rx = w - rw;
  return {{0, 0, w, top},
          {0, top + gap, lw, body},
          {lw + gap, top + gap, cw, body},
          {rx, top + gap, rw, body * .40f},
          {rx, top + gap + body * .40f + gap, rw,
           std::max(1.f, body * .60f - gap)}};
}
std::string format_world_time(double value) {
  auto ms = static_cast<long long>(std::max(0., value) * 1000);
  char out[64];
  std::snprintf(out, sizeof(out), "%02lld:%02lld:%02lld.%03lld", ms / 3600000,
                (ms / 60000) % 60, (ms / 1000) % 60, ms % 1000);
  return out;
}
namespace {
constexpr auto flags = ImGuiWindowFlags_NoTitleBar | ImGuiWindowFlags_NoMove |
                       ImGuiWindowFlags_NoResize | ImGuiWindowFlags_NoCollapse |
                       ImGuiWindowFlags_NoSavedSettings;
void pane(const char *name, const PaneRect &r) {
  ImGui::SetNextWindowPos({r.x, r.y});
  ImGui::SetNextWindowSize({r.width, r.height});
  ImGui::Begin(name, nullptr, flags);
}
void tooltip(const char *text) {
  if (ImGui::IsItemHovered(ImGuiHoveredFlags_DelayShort))
    ImGui::SetTooltip("%s", text);
}
void send_host(WorkbenchUIState &ui, WorkbenchCommandChannel *commands,
               WorkbenchCommandKind kind) {
  if (!commands->submit(kind))
    ui.workbench_notice = "Workbench command queue full";
  else
    ui.workbench_notice.clear();
}
} // namespace
void draw_workbench(WorkbenchUIState &ui, const RenderSnapshot &world,
                    std::shared_ptr<const BrainSnapshot> brain,
                    std::shared_ptr<const DialogueSnapshot> dialogue,
                    std::shared_ptr<const WorkbenchStatusSnapshot> status,
                    WorkbenchCommandChannel *commands, float scale) {
  auto &io = ImGui::GetIO();
  io.FontGlobalScale = ui.ui_scale;
  scale *= ui.ui_scale;
  auto layout = workbench_layout(io.DisplaySize.x, io.DisplaySize.y, scale,
                                 ui.left_fraction, ui.right_fraction);
  if (!io.WantTextInput && !ImGui::IsAnyItemActive() && !ImGui::IsPopupOpen(nullptr, ImGuiPopupFlags_AnyPopupId)) {
    const ImGuiKey keys[] = {ImGuiKey_1, ImGuiKey_2, ImGuiKey_3, ImGuiKey_4,
                             ImGuiKey_5};
    for (int i = 0; i < 5; ++i)
      if (ImGui::IsKeyPressed(keys[i]))
        ui.tool = i;
    if (ImGui::IsKeyPressed(ImGuiKey_Escape)) {
      ui.tool = 0;
      ui.selected_object = 0;
      ui.body_selected = false;
      ui.selected_node = UINT32_MAX;
    }
    if (commands && status && ImGui::IsKeyPressed(ImGuiKey_Space))
      send_host(ui, commands,
                status->paused ? WorkbenchCommandKind::Resume
                               : WorkbenchCommandKind::Pause);
    if (commands && status && status->paused &&
        (ImGui::IsKeyPressed(ImGuiKey_Period) ||
         ImGui::IsKeyPressed(ImGuiKey_N)))
      send_host(ui, commands, WorkbenchCommandKind::Step);
  }
  pane("Toolbar", layout.toolbar);
  ImGui::BeginChild("Tools", {0, 0}, ImGuiChildFlags_None,
                    ImGuiWindowFlags_HorizontalScrollbar);
  ImGui::AlignTextToFramePadding();
  ImGui::TextDisabled("WORLD EDITOR");
  ImGui::SameLine(0, 16 * scale);
  const char *names[] = {"Select", "Food", "Water", "Object", "Erase"};
  const char *tips[] = {"Select an entity or object (1)",
                        "Place nutritive resource from runtime Settings (2)",
                        "Place hydration resource from runtime Settings (3)",
                        "Place ordinary physical object (4)",
                        "Remove a free world object (5)"};
  const ImVec4 colors[] = {{.49f, .83f, .99f, 1},
                           {1, .48f, .10f, 1},
                           {.26f, .72f, .85f, 1},
                           {.65f, .70f, .74f, 1},
                           {.85f, .38f, .38f, 1}};
  for (int i = 0; i < 5; ++i) {
    bool enabled = i == 0 || commands;
    if (i == 1 && status)
      enabled = status->food_payload > 0;
    if (i == 2 && status)
      enabled = status->water_payload > 0;
    ImGui::BeginDisabled(!enabled);
    bool selected = ui.tool == i;
    if (selected)
      ImGui::PushStyleColor(ImGuiCol_Button, ImVec4{.16f, .29f, .37f, 1});
    ImGui::PushStyleColor(ImGuiCol_Text, colors[i]);
    if (ImGui::Button(names[i]))
      ui.tool = i;
    ImGui::PopStyleColor();
    if (selected)
      ImGui::PopStyleColor();
    tooltip(tips[i]);
    ImGui::EndDisabled();
    ImGui::SameLine();
  }
  ImGui::Dummy({12 * scale, 1});
  ImGui::SameLine();
  ImGui::BeginDisabled(!commands || !status);
  if (ImGui::Button(status && status->paused ? "Run" : "Pause"))
    send_host(ui, commands,
              status && status->paused ? WorkbenchCommandKind::Resume
                                       : WorkbenchCommandKind::Pause);
  tooltip(
      "Space: pause host advancement; causal clocks stay at their frontier");
  ImGui::SameLine();
  ImGui::BeginDisabled(!status || !status->paused);
  if (ImGui::Button("Step"))
    send_host(ui, commands, WorkbenchCommandKind::Step);
  tooltip("N / . : next scheduler timestamp, including its zero-time "
          "continuations");
  ImGui::EndDisabled();
  ImGui::EndDisabled();
  ImGui::SameLine(0, 16 * scale);
  ImGui::AlignTextToFramePadding();
  ImGui::TextColored(status && status->paused ? ImVec4{.87f, .69f, .29f, 1}
                                              : ImVec4{.49f, .83f, .99f, 1},
                     "%s", status && status->paused ? "PAUSED" : "RUNNING");
  ImGui::SameLine();
  ImGui::TextUnformatted(format_world_time(world.world_time).c_str());
  ImGui::SameLine(0, 16 * scale);
  ImGui::SameLine();
  if (ImGui::Button("Settings") || (ui.open_settings_popup && ImGui::GetFrameCount() >= 3)) {
    ui.open_settings_popup = false;
    ui.settings_draft = status ? status->configuration : WorkbenchNewWorldConfig{};
    ImGui::OpenPopup("SETTINGS / NEW WORLD");
  }
  ImGui::SameLine();
  if (ImGui::Button("Scenario") || (ui.open_scenario_popup && ImGui::GetFrameCount() >= 3)) {
    ui.open_scenario_popup = false;
    if (status)
      ui.scenario_seed = status->seed;
    ImGui::OpenPopup("Save Scenario");
  }
  ImGui::SetNextWindowSize({420 * scale, 0}, ImGuiCond_Always);
  if (ImGui::BeginPopup("Save Scenario")) {
    ImGui::TextDisabled("NORMALIZED INITIAL CONDITION / t = 0");
    ImGui::SetNextItemWidth(340 * scale);
    ImGui::InputTextWithHint("Path", "case.sescenario", ui.scenario_path.data(),
                             ui.scenario_path.size());
    ImGui::SetNextItemWidth(260 * scale);
    ImGui::InputText("Name", ui.scenario_name.data(), ui.scenario_name.size());
    ImGui::SetNextItemWidth(180 * scale);
    ImGui::InputScalar("Seed", ImGuiDataType_U64, &ui.scenario_seed);
    ImGui::TextWrapped("Physical scene + physiology + Settings. No checkpoint "
                       "or learned brain.");
    ImGui::BeginDisabled(!commands || !status || !status->paused);
    if (ImGui::Button("Finish action & pause")) {
      if (!commands->submit(WorkbenchCommandKind::ReachScenarioBoundary))
        ui.workbench_notice = "Workbench command queue full";
    }
    tooltip("Explicitly advances ordinary events to a safe physical boundary. "
            "Save itself never advances time.");
    if (ImGui::Button("Save")) {
      if (ui.scenario_seed > INT64_MAX)
        ui.workbench_notice = "Invalid scenario seed";
      else if (!commands->submit_export(ui.scenario_path.data(),
                                        ui.scenario_name.data(),
                                        ui.scenario_seed))
        ui.workbench_notice = "Scenario export queue full; path retained";
      else {
        ui.workbench_notice.clear();
        ImGui::CloseCurrentPopup();
      }
    }
    ImGui::EndDisabled();
    ImGui::SameLine();
    if (ImGui::Button("Cancel"))
      ImGui::CloseCurrentPopup();
    if (!status || !status->paused)
      ImGui::TextDisabled("Pause to export the scenario");
    ImGui::EndPopup();
  }
  draw_settings_dialog(ui, status.get(), commands, scale);
  ImGui::EndChild();
  ImGui::End();
  pane("Dialogue", layout.dialogue);
  ImGui::TextDisabled("DIALOGUE");
  ImGui::Separator();
  draw_dialogue_view(ui, dialogue.get(), commands,
                     status ? status->dialogue_notice : "");
  ImGui::End();
  pane("World", layout.world);
  ImGui::TextDisabled("WORLD");
  ImGui::SameLine();
  ImGui::TextDisabled("%d x %d", world.world_width, world.world_height);
  ImGui::SameLine();
  if (ImGui::SmallButton("Fit")) {
    ui.world_zoom = 1;
    ui.world_pan_x = ui.world_pan_y = 0;
  }
  ImGui::Separator();
  draw_world_view(ui, world, commands);
  ImGui::End();
  pane("Brain", layout.brain);
  draw_brain_view(ui, std::move(brain));
  ImGui::End();
  pane("Status", layout.status);
  draw_status_view(status.get(), ui, world);
  ImGui::End();
}
} // namespace se
