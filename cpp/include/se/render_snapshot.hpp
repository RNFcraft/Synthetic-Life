#pragma once
#include <cstdint>
#include <vector>
#include <atomic>
#include <memory>
namespace se {
struct RenderBodyState { std::uint32_t id{}; int x{},y{}; char orientation{}; std::uint16_t appearance{}; std::uint32_t held_object_id{}; };
struct RenderObjectState { std::uint32_t id{}; int x{},y{},state{}; };
struct RenderHeldObjectState { std::uint32_t owner_body_id{},object_id{}; int state{}; };
struct RenderSnapshot { double world_time{}; std::uint64_t event_sequence{}; int world_width{},world_height{}; std::vector<RenderBodyState>bodies; std::vector<RenderObjectState>objects; std::vector<RenderHeldObjectState>held_objects; };
class RenderSnapshotChannel {
public:
  void publish(RenderSnapshot snapshot){latest_.store(std::make_shared<const RenderSnapshot>(std::move(snapshot)),std::memory_order_release);}
  std::shared_ptr<const RenderSnapshot> latest()const{return latest_.load(std::memory_order_acquire);}
private: std::atomic<std::shared_ptr<const RenderSnapshot>> latest_;
};
}
