#include "se/native_brain_engine.hpp"
#include <algorithm>
#include <limits>
#include <set>
#include <stdexcept>
namespace se {
std::vector<AssemblyCognitBridgeResult> NativeBrainEngine::process_assembly_bridge(std::uint64_t tick, std::size_t max_events,std::size_t max_cognits,std::size_t max_births) {
  std::vector<AssemblyCognitBridgeResult> out;
  std::size_t births_this_drain{};
  for (auto const &event : neurodynamic_.assembly_bridge_events_after(assembly_bridge_cursor_, max_events)) {
    auto found = assembly_cognits_.find(event.assembly_id);
    bool born = false;
    if (found != assembly_cognits_.end() && !cognit_alive(found->second)) { assembly_cognits_.erase(found); found = assembly_cognits_.end(); }
    if (found == assembly_cognits_.end()) {
      if(live_cognit_count()<max_cognits&&births_this_drain<max_births){auto id = add_cognit(0., .25, .5);found = assembly_cognits_.emplace(event.assembly_id, id).first;born = true;++births_this_drain;++assembly_cognit_births_;}
    }
    bool activated = false;
    bool suppressed=found==assembly_cognits_.end();
    if(suppressed)++assembly_cognit_births_suppressed_;
    if (!suppressed&&event.kind == AssemblyBridgeEventKind::Recognized&&event.contribution>0.) {
      auto energy = std::clamp(event.contribution, 0., 1.); activated = receive(found->second, energy, tick, false, .2, 2); ++assembly_cognit_activations_;
    }
    assembly_bridge_cursor_ = event.sequence;
    out.push_back({event.sequence, event.assembly_id, suppressed?std::numeric_limits<std::uint32_t>::max():found->second, event.confidence, (std::uint8_t)event.kind, born, activated,event.time,event.recognition_episode_id,event.contribution,suppressed});
  }
  return out;
}
std::vector<std::pair<std::uint64_t, std::uint32_t>> NativeBrainEngine::assembly_cognit_mapping() const {
  std::vector<std::pair<std::uint64_t, std::uint32_t>> out;
  for (auto const &row : assembly_cognits_) if (cognit_alive(row.second)) out.push_back(row);
  return out;
}
std::tuple<std::uint64_t, std::vector<std::pair<std::uint64_t, std::uint32_t>>, std::uint64_t, std::uint64_t,std::uint64_t> NativeBrainEngine::assembly_bridge_state() const { return {assembly_bridge_cursor_, assembly_cognit_mapping(), assembly_cognit_births_, assembly_cognit_activations_,assembly_cognit_births_suppressed_}; }
void NativeBrainEngine::restore_assembly_bridge_state(std::uint64_t cursor, const std::vector<std::pair<std::uint64_t, std::uint32_t>> &mapping, std::uint64_t births, std::uint64_t activations,std::uint64_t suppressed) {
  auto neural = neurodynamic_.snapshot();
  if (cursor >= neural.next_bridge_sequence) throw std::invalid_argument("invalid assembly bridge cursor");
  std::map<std::uint64_t, std::uint32_t> checked;std::set<std::uint32_t> cognits;
  for (auto const &[assembly, cognit] : mapping) {
    auto row = std::find_if(neural.assemblies.begin(), neural.assemblies.end(), [&](auto const &a) { return a.id == assembly && a.consolidated; });
    if (row == neural.assemblies.end() || !cognit_alive(cognit) || !checked.emplace(assembly, cognit).second||!cognits.insert(cognit).second) throw std::invalid_argument("invalid assembly Cognit mapping");
  }
  if((!checked.empty()&&!cursor)||births<checked.size())throw std::invalid_argument("invalid assembly bridge counters");
  assembly_bridge_cursor_ = cursor; assembly_cognits_ = std::move(checked); assembly_cognit_births_ = births; assembly_cognit_activations_ = activations; assembly_cognit_births_suppressed_=suppressed;
}
}
