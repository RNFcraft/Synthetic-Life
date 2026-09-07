#pragma once
#include "cognitive_graph.hpp"
#include "activity_wave.hpp"
#include <unordered_map>
#include <deque>
#include <unordered_set>
#include <tuple>
#include <array>
#include <string>
#include <stdexcept>

namespace se {
struct MaterializedRelation{std::uint32_t source,target,support;std::uint8_t action;double probability,confidence,lift;};
struct PlannerTransition{std::vector<std::vector<std::pair<std::uint32_t,double>>> predictions,effects;};
struct EvidenceConfig{std::uint32_t minimum_support{3},consolidated_support{20};double minimum_lift{1},confidence_k{8},consolidated_confidence{.68};};
class NativeBrainEngine{
public:
  explicit NativeBrainEngine(std::size_t evidence_window=512):evidence_window_(evidence_window){}
  std::uint32_t add_cognit(double activity=0,double threshold=.25,double confidence=.5){auto id=graph_.add_cognit(activity,threshold,confidence);resize_scratch();return id;}
  std::uint32_t add_cognits(std::uint32_t count,double activity=0,double threshold=.25,double confidence=.5){auto first=(std::uint32_t)graph_.cognit_count();for(std::uint32_t i=0;i<count;++i)graph_.add_cognit(activity,threshold,confidence);resize_scratch();return first;}
  void set_activity(std::uint32_t id,double value){catch_up_homeostasis(id);if(!cognit_alive(id))throw std::out_of_range("dead or invalid Cognit");graph_.activity.at(id)=value;++state_revision_;}
  void set_refractory(std::uint32_t id,std::uint16_t value){catch_up_homeostasis(id);if(!cognit_alive(id))throw std::out_of_range("dead or invalid Cognit");graph_.refractory.at(id)=value;++state_revision_;}
  bool receive(std::uint32_t id,double energy,std::uint64_t cognitive_tick,bool wave_step,double refractory_attenuation,std::uint16_t refractory_wave_steps);
  std::vector<std::uint8_t> receive_batch(std::span<const std::uint32_t>ids,std::span<const double>energies,std::uint64_t cognitive_tick,bool wave_step,double refractory_attenuation,std::uint16_t refractory_wave_steps);
  std::uint64_t state_revision()const{return state_revision_;}
  void prepare(){resize_scratch();}
  bool cognit_alive(std::uint32_t id)const{return id<graph_.flags.size() && !(graph_.flags[id]&1);}
  bool remove_cognit(std::uint32_t id);
  std::size_t live_cognit_count()const{return cognit_count()-dead_cognits_;}
  RelationHandle add_relation(std::uint32_t source,std::uint32_t target,RelationType type,std::uint32_t action,double strength,double confidence,double probability);
  std::vector<std::pair<RelationHandle,PersistedRelation>> outgoing(std::span<const std::uint32_t>sources)const;PersistedRelation relation_state(std::uint32_t source,RelationHandle h)const{return graph_.relations.state(source,h);}void update_relation(RelationHandle h,const PersistedRelation&r){graph_.relations.update(h,r);}
  std::vector<std::uint32_t> outgoing_targets(std::span<const std::uint32_t>sources)const;
  bool remove_relation(RelationHandle handle){return graph_.relations.erase(handle);}bool relation_handle_valid(RelationHandle handle)const{return graph_.relations.valid(handle);}
  static constexpr std::size_t provisional_relation_bytes(){return RelationStore::provisional_record_bytes();}static constexpr std::size_t consolidated_relation_bytes(){return RelationStore::consolidated_record_bytes();}
  std::vector<std::pair<std::uint32_t,double>> predict(std::span<const std::uint32_t> active,std::uint8_t action);
  std::vector<std::vector<std::pair<std::uint32_t,double>>> predict_actions_batch(std::span<const std::uint32_t> active,std::span<const std::uint8_t> actions);
  std::vector<std::vector<std::pair<std::uint32_t,double>>> predict_actions_batch_at(std::span<const std::uint32_t> active,std::span<const std::uint8_t> actions,std::uint64_t world_tick,double confidence_decay);
  std::vector<std::pair<std::uint32_t,double>> action_effects(std::span<const std::uint32_t> active,std::uint8_t action,double probability_floor);
  std::vector<std::vector<std::pair<std::uint32_t,double>>> action_effects_batch(std::span<const std::uint32_t>active,std::span<const std::uint8_t>actions,double probability_floor);
  std::vector<PlannerTransition> planner_transition_batch(const std::vector<std::vector<std::uint32_t>>&states,std::span<const std::uint8_t>actions,std::uint64_t world_tick,double confidence_decay,double probability_floor);
  WaveResult propagate(std::span<const std::uint32_t> seeds,std::uint64_t cognitive_tick,std::uint32_t max_steps=8,double retention=.72,double refractory_attenuation=.2,std::uint16_t refractory_wave_steps=2);
  std::vector<double> cognit_state(std::span<const std::uint32_t> ids)const;
  std::vector<double> cognit_state_full(std::span<const std::uint32_t> ids)const;
  void set_cognit_states(std::span<const std::uint32_t>ids,std::span<const double>values);
  void set_cognit_fields(std::span<const std::uint32_t>ids,std::span<const std::uint8_t>fields,std::span<const double>values);
  std::vector<double> cognit_state_masked(std::span<const std::uint32_t>ids,std::uint16_t field_mask)const;
  void homeostatic_step(std::span<const std::uint32_t>active,double trace_decay,double learning_rate,double threshold_min,double threshold_max,double activity_decay,double utility_decay);
  void update_transition_evidence(std::span<const std::uint32_t> before,std::uint8_t action,std::span<const std::uint32_t> after);
  std::vector<MaterializedRelation> materialize_relations(const EvidenceConfig&,std::uint64_t world_tick);
  std::vector<MaterializedRelation> materialize_current(const EvidenceConfig&,std::uint64_t world_tick,std::span<const std::uint32_t>before,std::uint8_t action,std::span<const std::uint32_t>after,std::uint32_t max_new,std::uint32_t max_relations,double confidence_decay);
  void clear_transition_evidence();
  std::vector<std::tuple<std::vector<std::uint32_t>,std::uint8_t,std::vector<std::uint32_t>>> transition_history()const;
  void restore_transition_history(const std::vector<std::tuple<std::vector<std::uint32_t>,std::uint8_t,std::vector<std::uint32_t>>>&);
  std::tuple<std::uint64_t,std::vector<std::array<double,7>>,std::vector<std::uint64_t>> homeostasis_runtime_state()const;
  void restore_homeostasis_runtime_state(std::uint64_t,const std::vector<std::array<double,7>>&,const std::vector<std::uint64_t>&);
  std::vector<std::array<std::uint32_t,4>> dirty_relation_state()const;
  void restore_dirty_relation_state(const std::vector<std::array<std::uint32_t,4>>&);
  void set_evidence_window(std::size_t n);
  std::tuple<std::uint64_t,std::uint64_t,std::uint64_t,std::size_t> evidence_stats()const{return{source_events_,target_events_,candidate_pair_updates_,evidence_reserved_bytes()};}
  std::tuple<std::uint32_t,double,double,double,double,std::uint32_t> transition_metrics(std::uint32_t source,std::uint32_t target,std::uint8_t action)const;
  std::vector<std::uint32_t> action_trials(std::span<const std::uint32_t>sources,std::span<const std::uint8_t>actions)const;
  void update_outcomes(std::span<const std::uint32_t>before,std::span<const std::uint32_t>current,int action,std::uint64_t tick,double confirmation,double contradiction,double utility,double consolidated_confidence);
  std::pair<std::uint32_t,std::uint32_t> lifecycle_step(std::uint64_t world_tick,std::uint64_t max_idle,double death_threshold,double confidence_decay);
  void save_graph(const std::string&path)const;void load_graph(const std::string&path);
  std::size_t cognit_count()const{return graph_.cognit_count();}std::size_t relation_count()const{return graph_.relation_count();}std::size_t reserved_bytes()const;
  std::size_t provisional_count()const{return graph_.relations.provisional_count();}std::size_t consolidated_count()const{return graph_.relations.consolidated_count();}
  std::size_t logical_bytes()const{return graph_.relations.logical_bytes()+graph_.activity.size()*8*sizeof(double)+graph_.last_active_cognitive_tick.size()*sizeof(std::uint64_t)+graph_.age.size()*2*sizeof(std::uint32_t)+graph_.refractory.size()*sizeof(std::uint16_t)+graph_.flags.size();}
  CognitiveGraph& graph(){return graph_;}
private:
  struct HomeostasisPolicy{std::uint64_t first;double lam,rate,tmin,tmax,activity_decay,utility_decay;};
  std::uint64_t homeostasis_tick_{};
  std::vector<HomeostasisPolicy>homeostasis_policies_;
  mutable std::vector<std::uint64_t>homeostasis_applied_;
  void catch_up_homeostasis(std::uint32_t id)const;
  void evolve_homeostasis(std::uint32_t id,bool active,const HomeostasisPolicy&)const;
  std::size_t dead_cognits_{};
  std::uint64_t state_revision_{};
  struct ActionSourceKey{std::uint32_t s;std::uint8_t a;bool operator==(const ActionSourceKey&)const=default;};
  struct ASHash{std::size_t operator()(const ActionSourceKey&x)const{return(std::size_t(x.s)<<8)^x.a;}};
  using SlotMask=std::vector<std::uint64_t>;
  struct Experience{std::vector<std::uint32_t>before,after;std::uint8_t action{};bool occupied{};};
  mutable CognitiveGraph graph_;std::uint64_t evidence_steps_{},source_events_{},target_events_{},candidate_pair_updates_{};std::size_t evidence_window_{512},evidence_cursor_{};std::vector<Experience>evidence_slots_;std::unordered_map<std::uint32_t,std::uint32_t>source_counts_,target_counts_;std::unordered_map<ActionSourceKey,std::uint32_t,ASHash>action_source_counts_;std::unordered_map<std::uint32_t,SlotMask>before_slots_,after_slots_;std::unordered_map<ActionSourceKey,SlotMask,ASHash>before_action_slots_;
  std::vector<double>incoming_,absence_,frontier_energy_,next_energy_;std::vector<std::uint32_t>incoming_gen_,absence_gen_,visited_gen_,frontier_ids_,next_ids_,touched_,candidate_targets_;std::vector<std::uint32_t>candidate_gen_;std::array<std::vector<std::pair<std::uint32_t,double>>,256>conditioned_scratch_;std::vector<RelationHandle>dirty_relations_;std::uint32_t generation_{1};void resize_scratch();std::uint32_t next_generation();void evict_slot(std::size_t);std::size_t evidence_reserved_bytes()const;std::uint32_t support(std::uint32_t,std::uint32_t)const;std::uint32_t action_support(std::uint32_t,std::uint8_t,std::uint32_t)const;void discover_targets(const SlotMask&,std::vector<std::uint32_t>&)const;static bool mask_empty(const SlotMask&);
  std::vector<std::uint64_t>relation_confidence_cache_tick_;std::vector<double>relation_confidence_cache_base_,relation_confidence_cache_decay_,relation_confidence_cache_value_;
};
}
