#pragma once
#include "types.hpp"
#include <optional>
#include <span>
#include <string>
#include <utility>
#include <vector>

namespace se {
struct Object { std::uint32_t id{}; int x{},y{},state{}; };
struct Body { int x{},y{}; char orientation{'N'};std::uint32_t held_object_id{};std::uint16_t appearance{1};std::uint32_t id{}; };
class World {
public:
  World(int width=30,int height=30,int radius=4):width_(width),height_(height),radius_(radius){}
  void initialize(Body body,std::vector<std::pair<int,int>> positions);
  void initialize_multi(std::vector<Body> bodies,std::vector<Object> objects);
  void restore(std::vector<Body> bodies,std::vector<Object> objects,std::vector<std::pair<std::uint32_t,Object>> held,
    std::vector<double> resistance,std::uint64_t world_tick,std::optional<std::uint64_t> next_tick,std::uint32_t next_id,
    std::uint32_t conflict_cursor,std::uint64_t conflict_count,std::vector<std::uint64_t> fairness_wins,
    double world_time,std::uint64_t event_sequence,std::uint32_t max_objects);
  void set_body_state(std::uint32_t id,int x,int y,char orientation);
  SensoryFrame perceive(std::uint64_t tick,std::uint32_t body_id=0) const;
  ActionResult apply(ActionType action,std::uint32_t body_id=0);
  std::vector<ActionResult> resolve_intents(std::span<const std::uint32_t>body_ids,std::span<const std::uint8_t>actions);
  ActionResult apply_intent(ActionType action,double issued_at_world_time,std::uint64_t event_id);
  void advance_world_time(double seconds);
  void configure_spawning(std::uint32_t max_objects,std::optional<std::uint64_t>next_tick,std::uint32_t next_id){max_objects_=max_objects;next_spawn_tick_=next_tick;next_object_id_=next_id;}
  std::string world_tick(std::optional<std::pair<int,int>>spawn_position,std::optional<std::uint64_t>next_tick);
  std::optional<std::uint32_t> apply_spawn_event(std::optional<std::pair<int,int>>spawn_position,double event_time,std::uint64_t event_id);
  double world_time()const noexcept{return world_time_;}std::uint64_t event_sequence()const noexcept{return event_sequence_;}
  std::uint64_t world_tick_count()const noexcept{return world_tick_count_;}std::optional<std::uint64_t>next_spawn_tick()const noexcept{return next_spawn_tick_;}std::uint32_t next_object_id()const noexcept{return next_object_id_;}
  const std::vector<Object>& objects() const noexcept{return objects_;}const std::vector<Body>& bodies()const noexcept{return bodies_;}
  const Body& body() const noexcept{return bodies_.front();}const std::vector<std::optional<Object>>& held_objects()const noexcept{return held_;}
  double resistance(std::uint32_t id=0)const noexcept{return resistance_.at(id);}std::uint32_t conflict_cursor()const{return conflict_cursor_;}std::uint64_t conflict_count()const{return conflict_count_;}const std::vector<std::uint64_t>&fairness_wins()const{return fairness_wins_;}
  const std::vector<double>& resistances()const noexcept{return resistance_;}
private:
  int width_,height_,radius_;std::vector<Body>bodies_{Body{}};std::vector<Object>objects_;std::vector<std::optional<Object>>held_{1};std::vector<double>resistance_{0.};
  std::uint32_t conflict_cursor_{},next_object_id_{1},max_objects_{};std::uint64_t conflict_count_{},world_tick_count_{};std::vector<std::uint64_t>fairness_wins_{0};std::optional<std::uint64_t>next_spawn_tick_;
  double world_time_{};std::uint64_t event_sequence_{};
  Object* at(int x,int y);const Object* at(int x,int y)const;Body* body_by_id(std::uint32_t);const Body* body_by_id(std::uint32_t)const;
  bool occupied_by_body(int x,int y,std::uint32_t except)const;bool contains(int x,int y)const{return x>=0&&y>=0&&x<width_&&y<height_;}
};
}
