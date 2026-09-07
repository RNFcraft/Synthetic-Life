#pragma once
#include <cstdint>
#include <queue>
#include <vector>

namespace se {
enum class RuntimeEventType:std::uint8_t { WorldActionComplete=1,WorldSpawn,SensoryChange,CognitionWake,CognitionContinue,MemoryTimer,RelationTimer,Maintenance,ExternalInput };
struct RuntimeEvent { double time{};std::uint64_t id{};RuntimeEventType type{};std::uint64_t payload{}; };
class EventScheduler {
 public:
  std::uint64_t schedule(double time,RuntimeEventType type,std::uint64_t payload=0);
  std::vector<RuntimeEvent> pop_ready(double through_time);
  std::vector<RuntimeEvent> snapshot()const;
  void restore(double now,std::uint64_t next_id,const std::vector<RuntimeEvent>&events);
  double now()const noexcept{return now_;}std::uint64_t next_id()const noexcept{return next_id_;}std::size_t size()const noexcept{return queue_.size();}
 private:
  struct Later {bool operator()(const RuntimeEvent&a,const RuntimeEvent&b)const noexcept{return a.time>b.time||(a.time==b.time&&a.id>b.id);}};
  double now_{};std::uint64_t next_id_{1};std::priority_queue<RuntimeEvent,std::vector<RuntimeEvent>,Later>queue_;
};
}
