#pragma once
#include <array>
#include <cstdint>
#include <map>
#include <queue>
#include <vector>

namespace se {
enum class MicroPolarity : std::uint8_t { Excitatory=0, Inhibitory=1 };
struct NeuralEvent { double time{}; std::uint64_t sequence{}; std::uint32_t target{}; double amplitude{}; };
struct AssemblyRecord {
  std::uint64_t id{}; std::vector<std::uint32_t> members; std::vector<std::array<std::uint32_t,2>> temporal_edges;
  std::vector<std::array<double,2>> member_support; std::vector<std::array<double,3>> temporal_support;
  std::uint32_t support{}; double decayed_support{},first_seen{},last_seen{}; bool candidate{},consolidated{};
};
struct AssemblyMatch { std::uint64_t assembly_id{}; double confidence{},completeness{},temporal_match{},time{}; std::vector<std::uint32_t> matched_members; };
struct NeuroTelemetry {
  std::uint64_t total_events_processed{},total_spikes{},refractory_discards{},max_queue_depth{},last_advance_events_processed{};
  std::uint64_t plasticity_updates{},potentiation_updates{},depression_updates{},homeostatic_updates{};
  std::uint64_t assembly_candidates_created{},assemblies_consolidated{},assembly_matches{},assembly_evidence_updates{},max_recent_activity_size{},assembly_prunes{};
  double total_abs_weight_change{},max_observed_homeostatic_bias{};
};
struct NeuroSnapshot {
  double tau_membrane{},tau_adaptation{},refractory_period{},reset_potential{},adaptation_increment{};
  double tau_pre{},tau_post{},a_plus{},a_minus{},weight_min{},weight_max{},tau_homeostasis{},homeostasis_spike_increment{};
  double now{}; std::uint64_t next_sequence{},event_guard{};
  std::vector<double> potential,base_threshold,last_update,refractory_until,adaptation,last_spike;
  std::vector<double> pre_trace,post_trace,trace_last_update,homeostatic_threshold_bias,homeostasis_last_update;
  std::vector<std::uint64_t> spike_count;
  std::vector<std::uint32_t> source,target; std::vector<double> weight,delay; std::vector<std::uint8_t> polarity,plasticity_enabled;
  bool assembly_tracking_enabled{}; double assembly_window{},assembly_decay_tau{},assembly_member_ratio_threshold{},assembly_candidate_similarity_threshold{},assembly_temporal_similarity_threshold{};
  std::uint32_t assembly_min_support{},assembly_min_members{},assembly_max_members{},assembly_consolidation_support{},max_assembly_candidates{},max_consolidated_assemblies{},max_temporal_edges{},max_recent_spikes{}; std::uint64_t next_assembly_id{};
  std::vector<NeuralEvent> recent_spikes; std::vector<AssemblyRecord> assemblies; std::vector<AssemblyMatch> recent_matches; std::vector<std::uint64_t> node_activity_support;
  std::vector<NeuralEvent> pending; NeuroTelemetry telemetry;
};
class NeurodynamicSubstrate {
public:
  // All parameters are innate substrate physiology, not learned knowledge.
  explicit NeurodynamicSubstrate(double tau_membrane=10.,double tau_adaptation=100.,double refractory_period=1.,double reset_potential=0.,double adaptation_increment=.1,std::uint64_t event_guard=1'000'000,double tau_pre=20.,double tau_post=20.,double a_plus=.1,double a_minus=.1,double weight_min=0.,double weight_max=10.,double tau_homeostasis=1'000.,double homeostasis_spike_increment=0.,bool assembly_tracking_enabled=false,double assembly_window=5.,std::uint32_t assembly_min_support=2,std::uint32_t assembly_min_members=3,std::uint32_t assembly_max_members=8,std::uint32_t assembly_consolidation_support=3,double assembly_decay_tau=1000.,double assembly_member_ratio_threshold=.6,double assembly_candidate_similarity_threshold=.6,double assembly_temporal_similarity_threshold=.5,std::uint32_t max_assembly_candidates=64,std::uint32_t max_consolidated_assemblies=64,std::uint32_t max_temporal_edges=64,std::uint32_t max_recent_spikes=64);
  std::uint32_t add_micro_kappa(double base_threshold=1.);
  std::uint32_t add_micro_rho(std::uint32_t source,std::uint32_t target,double weight,double delay,MicroPolarity polarity,bool plasticity_enabled=false);
  void inject(std::uint32_t target,double amplitude,double time);
  void advance_to(double time);
  NeuroSnapshot snapshot()const; void restore(const NeuroSnapshot&);
  // Rows retain the v0.6.0 seven fields, then projected pre/post trace and slow bias.
  std::vector<std::array<double,10>> states(const std::vector<std::uint32_t>& ids)const;
  std::vector<AssemblyRecord> assemblies()const{return assemblies_;}
  std::vector<AssemblyMatch> recent_assembly_matches()const{return recent_matches_;}
  NeuroTelemetry telemetry()const{return telemetry_;}
  std::size_t micro_kappa_count()const{return potential_.size();} std::size_t micro_rho_count()const{return source_.size();} std::size_t pending_events()const{return queue_.size();} double now()const{return now_;} std::uint64_t next_sequence()const{return next_sequence_;}
private:
  struct Compare { bool operator()(const NeuralEvent&a,const NeuralEvent&b)const{return a.time>b.time||(a.time==b.time&&a.sequence>b.sequence);} };
  double tau_membrane_,tau_adaptation_,refractory_period_,reset_potential_,adaptation_increment_;
  double tau_pre_,tau_post_,a_plus_,a_minus_,weight_min_,weight_max_,tau_homeostasis_,homeostasis_spike_increment_,now_{};
  bool assembly_tracking_enabled_{}; double assembly_window_{},assembly_decay_tau_{},assembly_member_ratio_threshold_{},assembly_candidate_similarity_threshold_{},assembly_temporal_similarity_threshold_{}; std::uint32_t assembly_min_support_{},assembly_min_members_{},assembly_max_members_{},assembly_consolidation_support_{},max_assembly_candidates_{},max_consolidated_assemblies_{},max_temporal_edges_{},max_recent_spikes_{}; std::uint64_t next_assembly_id_{};
  std::uint64_t next_sequence_{},event_guard_{};
  std::vector<double> potential_,base_threshold_,last_update_,refractory_until_,adaptation_,last_spike_;
  std::vector<double> pre_trace_,post_trace_,trace_last_update_,homeostatic_threshold_bias_,homeostasis_last_update_;
  std::vector<std::uint64_t> spike_count_;
  std::vector<std::uint32_t> source_,target_; std::vector<double> weight_,delay_; std::vector<std::uint8_t> polarity_,plasticity_enabled_;
  std::vector<std::vector<std::uint32_t>> outgoing_,incoming_;
  std::priority_queue<NeuralEvent,std::vector<NeuralEvent>,Compare> queue_; NeuroTelemetry telemetry_{};
  std::vector<NeuralEvent> recent_spikes_; std::vector<AssemblyRecord> assemblies_; std::vector<AssemblyMatch> recent_matches_; std::vector<std::uint64_t> node_activity_support_;
  void validate_time(double time)const; void touch(std::uint32_t id,double time); void touch_traces(std::uint32_t id,double time);
  void schedule(std::uint32_t target,double amplitude,double time); void deliver(double time,const std::vector<NeuralEvent>& events);
  double pre_trace_at(std::uint32_t id,double time)const; double post_trace_at(std::uint32_t id,double time)const; double homeostatic_bias_at(std::uint32_t id,double time)const;
  void apply_plasticity(double time,const std::vector<std::uint32_t>& spikes);
  void observe_assemblies(double time,const std::vector<std::uint32_t>& spikes);
};
}
