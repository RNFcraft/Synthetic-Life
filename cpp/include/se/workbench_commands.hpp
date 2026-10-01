#pragma once
#include <cstdint>
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
  Step
};
struct WorkbenchCommand {
  std::uint64_t id{};
  WorkbenchCommandKind kind{};
  int x{}, y{};
  std::uint32_t object_id{};
  std::string text;
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
    if (raw < 1 || raw > 8)
      throw std::invalid_argument("invalid workbench command kind");
    const auto id = next_id_++;
    queue_.push_back({id, kind, x, y, object_id, std::move(text)});
    return id;
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
