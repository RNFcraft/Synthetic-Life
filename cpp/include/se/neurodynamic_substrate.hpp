#pragma once
#include <cstdint>
#include <vector>
#include <queue>
#include <map>
#include <array>

namespace se {
enum class MicroPolarity : std::uint8_t { Excitatory=0, Inhibitory=1 };
struct NeuralEvent { double time{}; std::uint64_t sequence{}; std::uint32_t target{}; double amplitude{}; };
struct NeuroTelemetry { std::uint64_t total_events_processed{},total_spikes{},refractory_discards{},max_queue_depth{},last_advance_events_processed{}; };
struct NeuroSnapshot {
  double now{};std::uint64_t next_sequence{};
  std::vector<double> potential,base_threshold,last_update,refractory_until,adaptation,last_spike;
  std::vector<std::uint64_t> spike_count;
  std::vector<std::uint32_t> source,target;std::vector<double> weight,delay;std::vector<std::uint8_t> polarity;
  std::vector<NeuralEvent> pending;NeuroTelemetry telemetry;
};
class NeurodynamicSubstrate {
public:
  // Innate substrate physiology, not learned knowledge.
  explicit NeurodynamicSubstrate(double tau_membrane=10.,double tau_adaptation=100.,double refractory_period=1.,double reset_potential=0.,double adaptation_increment=.1,std::uint64_t event_guard=1'000'000);
  std::uint32_t add_micro_kappa(double base_threshold=1.);
  std::uint32_t add_micro_rho(std::uint32_t source,std::uint32_t target,double weight,double delay,MicroPolarity polarity);
  void inject(std::uint32_t target,double amplitude,double time);
  void advance_to(double time);
  NeuroSnapshot snapshot()const;void restore(const NeuroSnapshot&);
  std::vector<std::array<double,7>> states(const std::vector<std::uint32_t>&ids)const;
  NeuroTelemetry telemetry()const{return telemetry_;}
  std::size_t micro_kappa_count()const{return potential_.size();}std::size_t micro_rho_count()const{return source_.size();}std::size_t pending_events()const{return queue_.size();}double now()const{return now_;}std::uint64_t next_sequence()const{return next_sequence_;}
private:
  struct Compare { bool operator()(const NeuralEvent&a,const NeuralEvent&b)const{return a.time>b.time||(a.time==b.time&&a.sequence>b.sequence);} };
  double tau_membrane_,tau_adaptation_,refractory_period_,reset_potential_,adaptation_increment_,now_{};std::uint64_t next_sequence_{},event_guard_{};
  std::vector<double>potential_,base_threshold_,last_update_,refractory_until_,adaptation_,last_spike_;std::vector<std::uint64_t>spike_count_;
  std::vector<std::uint32_t>source_,target_;std::vector<double>weight_,delay_;std::vector<std::uint8_t>polarity_;std::vector<std::vector<std::uint32_t>>outgoing_;
  std::priority_queue<NeuralEvent,std::vector<NeuralEvent>,Compare>queue_;NeuroTelemetry telemetry_{};
  void validate_time(double time)const;void touch(std::uint32_t id,double time);void schedule(std::uint32_t target,double amplitude,double time);void deliver(double time,const std::vector<NeuralEvent>&events);
};
}
