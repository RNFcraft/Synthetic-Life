#include "se/workbench_ui.hpp"
#include <algorithm>
#include <imgui.h>
namespace se {
namespace {
const char *presets[] = {"Current", "Classic Baseline", "Workbench Sparse", "Empty Experiment"};
void integer(const char *label, int &value, int low, int high) {
  ImGui::SetNextItemWidth(150);
  if (ImGui::InputInt(label, &value)) value = std::clamp(value, low, high);
}
void number(const char *label, double &value, double low, double high) {
  ImGui::SetNextItemWidth(150);
  if (ImGui::InputDouble(label, &value, 0, 0, "%.4g")) value = std::clamp(value, low, high);
}
bool submit(WorkbenchUIState &ui, WorkbenchCommandChannel *commands) {
  auto &c = ui.settings_draft;
  if (c.seed > INT64_MAX || c.object_count > c.max_objects ||
      std::int64_t(c.world_width) * c.world_height > 1000000 ||
      c.object_count + c.entity_count > std::int64_t(c.world_width) * c.world_height) {
    ui.workbench_notice = "Invalid seed, world dimensions or object capacity";
    return false;
  }
  if (!commands || !commands->submit_new_world(c)) {
    ui.workbench_notice = "New-world command queue unavailable";
    return false;
  }
  ui.workbench_notice.clear();
  return true;
}
}
void select_settings_preset(WorkbenchUIState &ui, int preset) {
  auto seed = ui.settings_draft.seed;
  ui.settings_draft = WorkbenchNewWorldConfig{};
  ui.settings_draft.seed = seed;
  ui.settings_draft.preset = preset;
  if (preset == 2 || preset == 3) {
    ui.settings_draft.object_count = preset == 2 ? 3 : 0;
    ui.settings_draft.max_objects = 150;
  }
}
void draw_settings_dialog(WorkbenchUIState &ui, const WorkbenchStatusSnapshot *status,
                          WorkbenchCommandChannel *commands, float scale) {
  auto display = ImGui::GetIO().DisplaySize;
  ImGui::SetNextWindowSize({std::min(620.f * std::min(scale, 1.15f), display.x - 32),
                            std::min(560.f * std::min(scale, 1.25f), display.y - 48)}, ImGuiCond_Always);
  ImGui::SetNextWindowPos({display.x * .5f, display.y * .5f}, ImGuiCond_Always, {.5f, .5f});
  if (!ImGui::BeginPopup("SETTINGS / NEW WORLD")) return;
  ImGui::SetWindowFontScale(std::min(1.f, 1.25f / scale));
  auto &c = ui.settings_draft;
  ImGui::TextDisabled("SETTINGS / NEW WORLD");
  ImGui::Separator();
  ImGui::SetNextItemWidth(220 * scale);
  int selected = c.preset;
  if (ImGui::Combo("Preset", &selected, presets, 4)) {
    if (selected == 0 && status) c = status->configuration;
    else select_settings_preset(ui, selected);
  }
  ImGui::TextWrapped("Causal - requires New World. Workbench - applies immediately.");
  ImGui::BeginChild("Configuration fields", {0, -110 * scale});
  if (ImGui::BeginTabBar("Settings categories")) {
    if (ImGui::BeginTabItem("World")) {
      integer("World width", c.world_width, 1, 4096);
      integer("World height", c.world_height, 1, 4096);
      integer("Initial objects", c.object_count, 0, 10000);
      integer("Max objects", c.max_objects, 0, 10000);
      ImGui::SetNextItemWidth(220);
      ImGui::InputScalar("Seed", ImGuiDataType_U64, &c.seed);
      if (ImGui::CollapsingHeader("Advanced")) {
        integer("Entity count", c.entity_count, 1, 64);
        integer("Perception radius", c.perception_radius, 0, 4096);
      }
      ImGui::EndTabItem();
    }
    if (ImGui::BeginTabItem("Resources")) {
      ImGui::Checkbox("Resource spawning enabled", &c.resource_spawning_enabled);
      number("Spawn interval (seconds)", c.resource_spawn_interval_seconds, .001, 1000000);
      integer("Max live resources", c.resource_max_live, 0, 1024);
      number("Food nutrient payload", c.resource_nutrient_payload, 0, 100);
      number("Water hydration payload", c.resource_hydration_payload, 0, 100);
      ImGui::EndTabItem();
    }
    if (ImGui::BeginTabItem("Physiology")) {
      number("Initial Energy", c.physiology_initial_energy, 0, c.physiology_max_energy);
      number("Initial Nutrients", c.physiology_initial_nutrients, 0, c.physiology_max_nutrients);
      number("Initial Hydration", c.physiology_initial_hydration, 0, c.physiology_max_hydration);
      if (ImGui::CollapsingHeader("Advanced")) {
        number("Max energy", c.physiology_max_energy, .001, 1000000);
        number("Max nutrients", c.physiology_max_nutrients, .001, 1000000);
        number("Max hydration", c.physiology_max_hydration, .001, 1000000);
        number("Energy target", c.physiology_energy_target, 0, 1000000);
        number("Nutrient target", c.physiology_nutrient_target, 0, 1000000);
        number("Hydration target", c.physiology_hydration_target, 0, 1000000);
        number("Basal Body Rate", c.physiology_basal_body_rate, 0, 1000000);
        number("Basal Brain Rate", c.physiology_basal_brain_rate, 0, 1000000);
        number("Hydration Rate", c.physiology_hydration_rate, 0, 1000000);
        number("Digestion Rate", c.physiology_digestion_rate, 0, 1000000);
        number("Digestion Efficiency", c.physiology_digestion_efficiency, 0, 1);
        number("Movement Cost", c.physiology_movement_cost, 0, 1000000);
        number("Interaction Cost", c.physiology_interaction_cost, 0, 1000000);
      }
      ImGui::EndTabItem();
    }
    if (ImGui::BeginTabItem("Cognition")) {
      ImGui::Checkbox("Interoception", &c.interoception_enabled);
      if (c.interoception_enabled) integer("Bins", c.interoception_bins, 2, 32);
      ImGui::Checkbox("Homeostatic valuation", &c.homeostatic_valuation_enabled);
      ImGui::Checkbox("Delayed prediction", &c.delayed_homeostatic_prediction_enabled);
      if (ImGui::CollapsingHeader("Advanced")) {
        integer("Planning horizon", c.planning_horizon, 1, 64);
        integer("Beam width", c.planning_beam_width, 1, 256);
        integer("Passive prediction depth", c.planning_passive_prediction_depth, 0, 8);
        number("Prediction horizon (seconds)", c.planning_prediction_time_horizon, .001, 10000);
        number("Time discount", c.planning_time_discount, 0, 100);
        number("Temporal probability floor", c.planning_temporal_probability_floor, .000001, 1);
      }
      ImGui::EndTabItem();
    }
    if (ImGui::BeginTabItem("Workbench")) {
      ImGui::TextDisabled("Presentation only / session preferences");
      ImGui::SliderFloat("UI scale", &ui.ui_scale, .75f, 1.5f, "%.2f");
      ImGui::Checkbox("Show world grid", &ui.show_grid);
      ImGui::Checkbox("Show tooltips", &ui.show_tooltips);
      ImGui::Checkbox("Show performance", &ui.show_performance);
      if(ImGui::Checkbox("Compatible CPU brain layout",&ui.legacy_brain_renderer))ui.cached_brain.reset();
      ImGui::SliderInt("Brain edge visual budget", &ui.brain_edge_budget, 0, WorkbenchUIState::max_brain_edges);
      ImGui::EndTabItem();
    }
    ImGui::EndTabBar();
  }
  ImGui::EndChild();
  ImGui::Separator();
  if (!ui.workbench_notice.empty()) ImGui::TextWrapped("%s", ui.workbench_notice.c_str());
  else if (status && !status->last_command_result.empty())
    ImGui::TextWrapped("%s", status->last_command_result.c_str());
  if (ImGui::Button("Reset to Engine Defaults")) select_settings_preset(ui, 1);
  if (ImGui::Button("Cancel")) ImGui::CloseCurrentPopup();
  ImGui::SameLine();
  ImGui::BeginDisabled(!commands);
  if (ImGui::Button("Apply & New World")) {
    if (status && (status->world_time > 0 || status->cognits > 0))
      ImGui::OpenPopup("Start a new world?");
    else if (submit(ui, commands)) ImGui::CloseCurrentPopup();
  }
  ImGui::EndDisabled();
  if (ImGui::BeginPopupModal("Start a new world?", nullptr, ImGuiWindowFlags_AlwaysAutoResize)) {
    ImGui::TextUnformatted("Current episode state will be discarded.");
    ImGui::TextUnformatted("Durable brain is not transferred automatically.");
    if (ImGui::Button("Start New World") && submit(ui, commands)) {
      ImGui::CloseCurrentPopup();
      // Close settings on the next frame by host restart; the draft remains local.
    }
    ImGui::SameLine();
    if (ImGui::Button("Keep Current World")) ImGui::CloseCurrentPopup();
    ImGui::EndPopup();
  }
  ImGui::EndPopup();
}
} // namespace se
