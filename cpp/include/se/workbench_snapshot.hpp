#pragma once
#include <array>
#include "se/workbench_settings.hpp"
#include <atomic>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace se {
// Detached presentation values. No owner pointer or policy API.
struct WorkbenchStatusSnapshot {
  double world_time{}, energy{}, energy_max{}, nutrients{}, nutrients_max{},
      hydration{}, hydration_max{}, hunger{}, tension{};
  std::uint64_t event_sequence{}, actions_completed{}, pending_events{},
      cognits{}, relations{}, active_cognits{}, micro_cognits{},
      micro_relations{}, assemblies{};
  bool paused{}, energy_depleted{}, interoception_enabled{},
      delayed_prediction_enabled{}, has_plan{}, has_temporal_prediction{};
  int bin_count{}, passive_depth{};
  std::array<int, 3> bins{}, target_bins{};
  double internal_observed_at{}, plan_score{}, plan_confidence{},
      homeostatic_component{}, prediction_confidence{}, predicted_delay{},
      ambiguity{};
  double food_payload{}, water_payload{};
  std::string current_action, last_command_result, dialogue_notice;
  std::uint64_t seed{};
  WorkbenchNewWorldConfig configuration;
  std::vector<std::string> planned_actions;
};
class WorkbenchStatusChannel {
public:
  void publish(WorkbenchStatusSnapshot value) {
    latest_.store(
        std::make_shared<const WorkbenchStatusSnapshot>(std::move(value)),
        std::memory_order_release);
  }
  std::shared_ptr<const WorkbenchStatusSnapshot> latest() const {
    return latest_.load(std::memory_order_acquire);
  }

private:
  std::atomic<std::shared_ptr<const WorkbenchStatusSnapshot>> latest_;
};
} // namespace se
