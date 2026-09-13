#pragma once
#include <atomic>
#include <cstdint>
#include <memory>
#include <vector>

namespace se {
inline constexpr std::size_t kMaxBrainSnapshotNodes=1024;
inline constexpr std::size_t kMaxBrainSnapshotEdges=4096;
struct BrainNodeState {
  std::uint32_t id{};
  double activity{}, threshold{}, confidence{};
  bool composite{}, alive{true};
  std::uint64_t last_active_cognitive_tick{};
};
struct BrainEdgeState {
  std::uint32_t source{}, target{};
  std::uint8_t relation_type{};
  double strength{}, confidence{}, activation{};
};
struct BrainSnapshot {
  double world_time{};
  std::uint64_t cognitive_tick{}, cognition_generation{};
  std::uint64_t total_cognits{},total_relations{};
  std::uint32_t active_cognits{};
  bool truncated{};
  std::vector<BrainNodeState> nodes;
  std::vector<BrainEdgeState> edges;
};
class BrainSnapshotChannel {
public:
  void publish(BrainSnapshot value) { latest_.store(std::make_shared<const BrainSnapshot>(std::move(value)), std::memory_order_release); }
  std::shared_ptr<const BrainSnapshot> latest() const { return latest_.load(std::memory_order_acquire); }
private:
  std::atomic<std::shared_ptr<const BrainSnapshot>> latest_;
};
}
