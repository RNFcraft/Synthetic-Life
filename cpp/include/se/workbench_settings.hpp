#pragma once
#include <cstdint>
// Detached primitive draft: no runtime pointers.
#define SE_NEW_WORLD_FIELDS(X) \
  X(int, world_width, 30) \
  X(int, world_height, 30) \
  X(int, object_count, 25) \
  X(int, max_objects, 25) \
  X(int, entity_count, 1) \
  X(int, perception_radius, 4) \
  X(bool, resource_spawning_enabled, false) \
  X(double, resource_spawn_interval_seconds, 10.0) \
  X(int, resource_max_live, 4) \
  X(double, resource_nutrient_payload, 20.0) \
  X(double, resource_hydration_payload, 20.0) \
  X(double, physiology_initial_energy, 80.0) \
  X(double, physiology_initial_nutrients, 60.0) \
  X(double, physiology_initial_hydration, 80.0) \
  X(double, physiology_max_energy, 100.0) \
  X(double, physiology_max_nutrients, 100.0) \
  X(double, physiology_max_hydration, 100.0) \
  X(double, physiology_energy_target, 75.0) \
  X(double, physiology_nutrient_target, 55.0) \
  X(double, physiology_hydration_target, 75.0) \
  X(double, physiology_basal_body_rate, 0.01) \
  X(double, physiology_basal_brain_rate, 0.005) \
  X(double, physiology_hydration_rate, 0.008) \
  X(double, physiology_digestion_rate, 0.02) \
  X(double, physiology_digestion_efficiency, 0.75) \
  X(double, physiology_movement_cost, 0.05) \
  X(double, physiology_interaction_cost, 0.02) \
  X(bool, interoception_enabled, false) \
  X(int, interoception_bins, 8) \
  X(bool, homeostatic_valuation_enabled, false) \
  X(bool, delayed_homeostatic_prediction_enabled, false) \
  X(int, planning_horizon, 4) \
  X(int, planning_beam_width, 8) \
  X(int, planning_passive_prediction_depth, 3) \
  X(double, planning_prediction_time_horizon, 30.0) \
  X(double, planning_time_discount, 0.1) \
  X(double, planning_temporal_probability_floor, 0.01)
namespace se {
struct WorkbenchNewWorldConfig {
#define FIELD(type, name, value) type name{value};
  SE_NEW_WORLD_FIELDS(FIELD)
#undef FIELD
  std::uint64_t seed{12345};
  // Presentation profile only: Current, Classic, Sparse, Empty.
  int preset{};
};
} // namespace se
