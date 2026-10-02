#pragma once
#include <cstdint>
#include "se/workbench_settings.hpp"
#include <deque>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>

namespace se {
enum class WorkbenchCommandKind : std::uint8_t {
  PlaceFood = 1,
  PlaceWater,
  PlaceObject,
  RemoveObject,
  SendDialogue,
  Pause,
  Resume,
  Step,
  ExportScenario,
  ReachScenarioBoundary,
  CreateNewWorld
};
struct WorkbenchCommand {
  std::uint64_t id{};
  WorkbenchCommandKind kind{};
  int x{}, y{};
  std::uint32_t object_id{};
  std::string text;
  std::string scenario_path, scenario_name;
  std::uint64_t scenario_seed{};
  WorkbenchNewWorldConfig new_world;
};
// UI producer / host consumer. No callbacks, GIL, or runtime pointers.
class WorkbenchCommandChannel {
public:
  static constexpr std::size_t capacity = 256, max_text_bytes = 4096;
  std::uint64_t submit(WorkbenchCommandKind kind, int x = 0, int y = 0,
                       std::uint32_t object_id = 0, std::string text = {}) {
    std::lock_guard lock(mutex_);
    if (closed_ || queue_.size() >= capacity || text.size() > max_text_bytes)
      return 0;
    const auto raw = static_cast<unsigned>(kind);
    if (raw < 1 || raw > 11)
      throw std::invalid_argument("invalid workbench command kind");
    if (kind == WorkbenchCommandKind::CreateNewWorld)
      throw std::invalid_argument("use submit_new_world with an explicit configuration");
    const auto id = next_id_++;
    queue_.push_back({id, kind, x, y, object_id, std::move(text)});
    return id;
  }
  std::uint64_t submit_export(std::string path, std::string name,
                              std::uint64_t seed) {
    std::lock_guard lock(mutex_);
    if (closed_ || queue_.size() >= capacity || path.size() > max_text_bytes ||
        name.size() > 256)
      return 0;
    if (seed > INT64_MAX)
      throw std::invalid_argument("invalid scenario seed");
    const auto id = next_id_++;
    queue_.push_back({id,
                      WorkbenchCommandKind::ExportScenario,
                      0,
                      0,
                      0,
                      {},
                      std::move(path),
                      std::move(name),
                      seed});
    return id;
  }
  std::uint64_t submit_new_world(WorkbenchNewWorldConfig config) {
    if (config.seed > INT64_MAX || config.preset < 0 || config.preset > 3)
      throw std::invalid_argument("invalid new-world configuration");
    std::lock_guard lock(mutex_);
    if (closed_ || queue_.size() >= capacity) return 0;
    WorkbenchCommand command;
    command.id = next_id_++;
    command.kind = WorkbenchCommandKind::CreateNewWorld;
    command.new_world = config;
    queue_.push_back(std::move(command));
    return next_id_ - 1;
  }
  std::vector<WorkbenchCommand> drain() {
    std::lock_guard lock(mutex_);
    std::vector<WorkbenchCommand> out(queue_.begin(), queue_.end());
    queue_.clear();
    return out;
  }
  void close() {
    std::lock_guard lock(mutex_);
    closed_ = true;
  }

private:
  std::mutex mutex_;
  std::deque<WorkbenchCommand> queue_;
  std::uint64_t next_id_{1};
  bool closed_{};
};
} // namespace se
