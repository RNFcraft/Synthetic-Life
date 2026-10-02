#include "se/observer.hpp"

#include <chrono>
#include <string>
#include <thread>
// Static presentation fixture, explicitly not a learning/survival experiment.
int main(int argc, char **argv) {
  int width = 1440, height = 900;
  double seconds = 0;
  std::string capture;
  bool scenario_popup = false, settings_popup = false;
  for (int i = 1; i + 1 < argc; i += 2) {
    std::string arg = argv[i];
    if (arg == "--width")
      width = std::stoi(argv[i + 1]);
    else if (arg == "--height")
      height = std::stoi(argv[i + 1]);
    else if (arg == "--seconds")
      seconds = std::stod(argv[i + 1]);
    else if (arg == "--capture")
      capture = argv[i + 1];
    else if (arg == "--settings-popup")
      settings_popup = std::stoi(argv[i + 1]) != 0;
    else if (arg == "--scenario-popup")
      scenario_popup = std::stoi(argv[i + 1]) != 0;
  }
  auto worlds = std::make_shared<se::RenderSnapshotChannel>();
  auto brains = std::make_shared<se::BrainSnapshotChannel>();
  auto dialogue = std::make_shared<se::DialogueSnapshotChannel>();
  auto statuses = std::make_shared<se::WorkbenchStatusChannel>();
  auto commands = std::make_shared<se::WorkbenchCommandChannel>();
  se::RenderSnapshot world;
  world.world_width = 16;
  world.world_height = 16;
  world.world_time = 74.25;
  world.event_sequence = 418;
  world.bodies = {{0, 6, 8, 'E', 1, 0}};
  world.objects = {{1, 9, 8, 1, se::PresentationKind::Food, 20, 0},
                   {2, 11, 5, 2, se::PresentationKind::Water, 0, 20},
                   {3, 4, 4, 0, se::PresentationKind::Neutral}};
  worlds->publish(world);
  se::BrainSnapshot brain;
  brain.world_time = 74.25;
  brain.cognitive_tick = 240;
  brain.total_cognits = 96;
  brain.total_relations = 164;
  brain.active_cognits = 9;
  for (unsigned i = 0; i < 96; ++i) {
    brain.nodes.push_back(
        {i, i < 9 ? .8 : .07, .3, .65, i % 13 == 0, true, i < 9 ? 240u : 180u});
    if (i)
      brain.edges.push_back(
          {i - 1, i, std::uint8_t(i % 4 + 1), .6, .7, i < 9 ? .8 : .04});
  }
  brains->publish(brain);
  dialogue->publish(12., se::DialogueRole::External, "dax");
  dialogue->publish(26., se::DialogueRole::External, "zup dax");
  dialogue->publish(72., se::DialogueRole::External,
                    "Presentation fixture: this transcript contains external "
                    "inputs only. No internal thought narration is generated.");
  se::WorkbenchStatusSnapshot status;
  status.world_time = 74.25;
  status.event_sequence = 418;
  status.paused = true;
  status.seed = 9100;
  status.actions_completed = 91;
  status.pending_events = 3;
  status.energy = 72;
  status.energy_max = 100;
  status.nutrients = 43;
  status.nutrients_max = 100;
  status.hydration = 81;
  status.hydration_max = 100;
  status.hunger = .22;
  status.tension = .08;
  status.interoception_enabled = true;
  status.bin_count = 8;
  status.bins = {5, 3, 6};
  status.target_bins = {6, 4, 6};
  status.internal_observed_at = 74.25;
  status.cognits = 96;
  status.relations = 164;
  status.active_cognits = 9;
  status.micro_cognits = 288;
  status.micro_relations = 960;
  status.assemblies = 12;
  status.current_action = "INTERACT_UP";
  status.has_plan = true;
  status.planned_actions = {"MOVE_RIGHT", "INTERACT_UP"};
  status.plan_score = .42;
  status.plan_confidence = .62;
  status.homeostatic_component = .08;
  status.prediction_confidence = .62;
  status.delayed_prediction_enabled = true;
  status.has_temporal_prediction = true;
  status.passive_depth = 2;
  status.predicted_delay = 1.4;
  status.ambiguity = .04;
  status.food_payload = status.water_payload = 20;
  status.last_command_result = "Static presentation fixture / no live organism";
  statuses->publish(status);
  se::NativeObserver observer(worlds, brains, dialogue, width, height);
  observer.attach_workbench(statuses, commands);
  if (!capture.empty())
    observer.capture_next_frame(capture, scenario_popup, settings_popup);
  observer.start();
  auto started = std::chrono::steady_clock::now();
  while (observer.is_running() &&
         (seconds <= 0 || std::chrono::duration<double>(
                              std::chrono::steady_clock::now() - started)
                                  .count() < seconds)) {
    for (auto const &command : commands->drain()) {
      if (command.kind == se::WorkbenchCommandKind::Pause)
        status.paused = true;
      else if (command.kind == se::WorkbenchCommandKind::Resume)
        status.paused = false;
      else if (command.kind == se::WorkbenchCommandKind::SendDialogue)
        dialogue->publish(world.world_time, se::DialogueRole::External,
                          command.text);
      else
        status.last_command_result =
            "Fixture only: use main.py --paused for real editing";
      statuses->publish(status);
    }
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }
  observer.stop();
  return observer.frames_rendered() > 0 ? 0 : 1;
}
