#pragma once
#include "types.hpp"
#include "relation_store.hpp"
#include <span>
#include <unordered_map>

namespace se {
class CognitiveGraph {
public:
  std::uint32_t add_cognit(double activity=0,double threshold=.25,double confidence=.5);
  Edge& connect(std::uint32_t source,std::uint32_t target,RelationType type,std::uint32_t action=0){return relations.connect(source,target,type,action).first;}
  template<class F>void for_each_outgoing(std::uint32_t source,F&&f){relations.for_each(source,std::forward<F>(f));}
  template<class F>void for_each_outgoing(std::uint32_t source,F&&f)const{relations.for_each(source,std::forward<F>(f));}
  std::size_t cognit_count()const{return activity.size();} std::size_t relation_count()const{return relations.size();}
  std::unordered_map<std::uint32_t,double> predict(std::span<const std::uint32_t> active,ActionType action)const;
  std::vector<double> activity,threshold,homeostatic_threshold,confidence,utility,activity_trace,target_activity,predictive_contribution;std::vector<std::uint64_t> last_active_cognitive_tick;std::vector<std::uint32_t> age,low_retention_ticks;std::vector<std::uint16_t> refractory;std::vector<std::uint8_t> flags;
  RelationStore relations;
};
}
