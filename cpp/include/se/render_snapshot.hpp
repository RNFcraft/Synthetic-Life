#pragma once
#include <cstdint>
#include <vector>
#include <memory>
#include <mutex>
namespace se {
struct RenderBodyState { std::uint32_t id{}; int x{},y{}; char orientation{}; std::uint16_t appearance{}; std::uint32_t held_object_id{}; };
struct RenderObjectState { std::uint32_t id{}; int x{},y{},state{}; };
struct RenderHeldObjectState { std::uint32_t owner_body_id{},object_id{}; int state{}; };
struct RenderSnapshot { double world_time{}; std::uint64_t event_sequence{}; int world_width{},world_height{}; std::vector<RenderBodyState>bodies; std::vector<RenderObjectState>objects; std::vector<RenderHeldObjectState>held_objects; };
class RenderSnapshotChannel {
public:
  void publish(RenderSnapshot snapshot){auto value=std::make_shared<const RenderSnapshot>(std::move(snapshot));std::lock_guard<std::mutex> lock(mutex_);latest_=std::move(value);}
  std::shared_ptr<const RenderSnapshot> latest()const{std::lock_guard<std::mutex> lock(mutex_);return latest_;}
private: mutable std::mutex mutex_;std::shared_ptr<const RenderSnapshot> latest_;
};
}
