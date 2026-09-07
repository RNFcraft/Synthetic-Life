#include "se/cognitive_graph.hpp"
#include <algorithm>
#include <cmath>

namespace se {
std::uint32_t CognitiveGraph::add_cognit(double a,double t,double c){auto id=(std::uint32_t)activity.size();activity.push_back(a);threshold.push_back(t);homeostatic_threshold.push_back(t);confidence.push_back(c);utility.push_back(0);activity_trace.push_back(0);target_activity.push_back(.08);predictive_contribution.push_back(0);last_active_cognitive_tick.push_back(0);age.push_back(0);low_retention_ticks.push_back(0);refractory.push_back(0);flags.push_back(0);relations.resize_nodes(activity.size());return id;}
std::unordered_map<std::uint32_t,double> CognitiveGraph::predict(std::span<const std::uint32_t> active,ActionType action)const{std::unordered_map<std::uint32_t,double> absent;for(auto s:active)for_each_outgoing(s,[&](const Edge&e,RelationHandle){if(e.type==RelationType::SelfAction&&e.action!=(std::uint8_t)action)return;double probability=e.prediction>0?e.prediction:e.strength;double q=std::clamp(activity[s]*probability*e.confidence,0.,1.);auto&p=absent[e.target];p=1-(1-p)*(1-q);});return absent;}
}
