#include "se/neurodynamic_substrate.hpp"
#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>

namespace se {
namespace {
bool finite_nonnegative(double value) { return std::isfinite(value) && value >= 0.; }
bool valid_history(double value) { return std::isfinite(value) || value == -INFINITY; }
}

NeurodynamicSubstrate::NeurodynamicSubstrate(double tm,double ta,double rp,double reset,double inc,std::uint64_t guard,double tpre,double tpost,double plus,double minus,double wmin,double wmax,double thomeo,double hinc)
  : tau_membrane_(tm),tau_adaptation_(ta),refractory_period_(rp),reset_potential_(reset),adaptation_increment_(inc),tau_pre_(tpre),tau_post_(tpost),a_plus_(plus),a_minus_(minus),weight_min_(wmin),weight_max_(wmax),tau_homeostasis_(thomeo),homeostasis_spike_increment_(hinc),event_guard_(guard) {
  if (!(tm>0 && ta>0 && rp>=0 && guard>0 && tpre>0 && tpost>0 && thomeo>0 && wmin>=0 && wmax>=wmin && std::isfinite(tm) && std::isfinite(ta) && std::isfinite(rp) && std::isfinite(reset) && std::isfinite(inc) && std::isfinite(tpre) && std::isfinite(tpost) && finite_nonnegative(plus) && finite_nonnegative(minus) && std::isfinite(wmin) && std::isfinite(wmax) && finite_nonnegative(hinc))) throw std::invalid_argument("invalid innate neuro physiology");
}
void NeurodynamicSubstrate::validate_time(double time)const { if (!std::isfinite(time) || time<now_) throw std::invalid_argument("neural time must be finite and monotonic"); }
std::uint32_t NeurodynamicSubstrate::add_micro_kappa(double threshold) {
  if (!std::isfinite(threshold)) throw std::invalid_argument("invalid threshold");
  auto id=(std::uint32_t)potential_.size();
  potential_.push_back(reset_potential_); base_threshold_.push_back(threshold); last_update_.push_back(now_); refractory_until_.push_back(-INFINITY); adaptation_.push_back(0.); last_spike_.push_back(-INFINITY);
  pre_trace_.push_back(0.); post_trace_.push_back(0.); trace_last_update_.push_back(now_); homeostatic_threshold_bias_.push_back(0.); homeostasis_last_update_.push_back(now_); spike_count_.push_back(0);
  outgoing_.emplace_back(); incoming_.emplace_back(); return id;
}
std::uint32_t NeurodynamicSubstrate::add_micro_rho(std::uint32_t source,std::uint32_t target,double weight,double delay,MicroPolarity polarity,bool enabled) {
  if (source>=potential_.size() || target>=potential_.size() || !std::isfinite(weight) || weight<0 || (enabled && (weight<weight_min_ || weight>weight_max_)) || !std::isfinite(delay) || delay<=0 || (polarity!=MicroPolarity::Excitatory && polarity!=MicroPolarity::Inhibitory)) throw std::invalid_argument("invalid micro rho");
  auto id=(std::uint32_t)source_.size(); source_.push_back(source); target_.push_back(target); weight_.push_back(weight); delay_.push_back(delay); polarity_.push_back((std::uint8_t)polarity); plasticity_enabled_.push_back(enabled); outgoing_[source].push_back(id); incoming_[target].push_back(id); return id;
}
void NeurodynamicSubstrate::schedule(std::uint32_t target,double amplitude,double time) { queue_.push({time,next_sequence_++,target,amplitude}); telemetry_.max_queue_depth=std::max<std::uint64_t>(telemetry_.max_queue_depth,queue_.size()); }
void NeurodynamicSubstrate::inject(std::uint32_t target,double amplitude,double time) { validate_time(time); if (target>=potential_.size() || !std::isfinite(amplitude)) throw std::invalid_argument("invalid neural injection"); schedule(target,amplitude,time); }
double NeurodynamicSubstrate::pre_trace_at(std::uint32_t id,double time)const { return pre_trace_[id]*std::exp(-(time-trace_last_update_[id])/tau_pre_); }
double NeurodynamicSubstrate::post_trace_at(std::uint32_t id,double time)const { return post_trace_[id]*std::exp(-(time-trace_last_update_[id])/tau_post_); }
double NeurodynamicSubstrate::homeostatic_bias_at(std::uint32_t id,double time)const { return homeostatic_threshold_bias_[id]*std::exp(-(time-homeostasis_last_update_[id])/tau_homeostasis_); }
void NeurodynamicSubstrate::touch(std::uint32_t id,double time) {
  auto dt=time-last_update_[id]; if (dt<0) throw std::logic_error("neural time travel"); if (dt) { potential_[id]*=std::exp(-dt/tau_membrane_); adaptation_[id]*=std::exp(-dt/tau_adaptation_); last_update_[id]=time; }
  auto homeo_dt=time-homeostasis_last_update_[id]; if (homeo_dt<0) throw std::logic_error("homeostasis time travel"); if (homeo_dt) { homeostatic_threshold_bias_[id]*=std::exp(-homeo_dt/tau_homeostasis_); homeostasis_last_update_[id]=time; }
}
void NeurodynamicSubstrate::touch_traces(std::uint32_t id,double time) { auto dt=time-trace_last_update_[id]; if (dt<0) throw std::logic_error("trace time travel"); if (dt) { pre_trace_[id]*=std::exp(-dt/tau_pre_); post_trace_[id]*=std::exp(-dt/tau_post_); trace_last_update_[id]=time; } }
void NeurodynamicSubstrate::apply_plasticity(double time,const std::vector<std::uint32_t>& spikes) {
  std::map<std::uint32_t,double> deltas;
  for (auto target:spikes) for (auto rho:incoming_[target]) if (plasticity_enabled_[rho]) deltas[rho]+=a_plus_*pre_trace_at(source_[rho],time)*(weight_max_-weight_[rho]);
  for (auto source:spikes) for (auto rho:outgoing_[source]) if (plasticity_enabled_[rho]) deltas[rho]-=a_minus_*post_trace_at(target_[rho],time)*(weight_[rho]-weight_min_);
  for (auto const&[rho,delta]:deltas) { auto before=weight_[rho]; auto after=std::clamp(before+delta,weight_min_,weight_max_); if (after==before) continue; weight_[rho]=after; ++telemetry_.plasticity_updates; if (after>before) ++telemetry_.potentiation_updates; else ++telemetry_.depression_updates; telemetry_.total_abs_weight_change+=std::abs(after-before); }
}
void NeurodynamicSubstrate::deliver(double time,const std::vector<NeuralEvent>& events) {
  std::map<std::uint32_t,std::vector<double>> groups; for (auto const&e:events) groups[e.target].push_back(e.amplitude);
  std::vector<std::uint32_t> spikes;
  for (auto&[id,amplitudes]:groups) {
    std::sort(amplitudes.begin(),amplitudes.end()); double sum{}; for (auto amplitude:amplitudes) sum+=amplitude; touch(id,time);
    if (time<refractory_until_[id]) { telemetry_.refractory_discards+=amplitudes.size(); potential_[id]=reset_potential_; continue; }
    potential_[id]+=sum;
    if (potential_[id]>=base_threshold_[id]+adaptation_[id]+homeostatic_threshold_bias_[id]) { ++spike_count_[id]; last_spike_[id]=time; potential_[id]=reset_potential_; adaptation_[id]+=adaptation_increment_; homeostatic_threshold_bias_[id]+=homeostasis_spike_increment_; refractory_until_[id]=time+refractory_period_; ++telemetry_.total_spikes; if(homeostasis_spike_increment_>0){++telemetry_.homeostatic_updates;telemetry_.max_observed_homeostatic_bias=std::max(telemetry_.max_observed_homeostatic_bias,homeostatic_threshold_bias_[id]);} spikes.push_back(id); }
  }
  // All deltas see traces strictly before this timestamp; same-time spikes cannot cause each other.
  apply_plasticity(time,spikes);
  for (auto id:spikes) { touch_traces(id,time); pre_trace_[id]+=1.; post_trace_[id]+=1.; for (auto rho:outgoing_[id]) schedule(target_[rho],polarity_[rho]==(std::uint8_t)MicroPolarity::Excitatory?weight_[rho]:-weight_[rho],time+delay_[rho]); }
}
void NeurodynamicSubstrate::advance_to(double time) { validate_time(time); telemetry_.last_advance_events_processed=0; while (!queue_.empty() && queue_.top().time<=time) { auto stamp=queue_.top().time; std::vector<NeuralEvent> batch; while (!queue_.empty() && queue_.top().time==stamp) { batch.push_back(queue_.top()); queue_.pop(); if (++telemetry_.last_advance_events_processed>event_guard_) throw std::runtime_error("neural event safety guard exceeded"); } telemetry_.total_events_processed+=batch.size(); deliver(stamp,batch); } now_=time; }
std::vector<std::array<double,10>> NeurodynamicSubstrate::states(const std::vector<std::uint32_t>& ids)const {
  std::vector<std::array<double,10>> out; out.reserve(ids.size()); for (auto id:ids) { if (id>=potential_.size()) throw std::out_of_range("invalid micro kappa"); auto dt=now_-last_update_[id]; if (dt<0) throw std::logic_error("invalid stored neural time"); out.push_back({potential_[id]*std::exp(-dt/tau_membrane_),base_threshold_[id],last_update_[id],refractory_until_[id],adaptation_[id]*std::exp(-dt/tau_adaptation_),last_spike_[id],double(spike_count_[id]),pre_trace_at(id,now_),post_trace_at(id,now_),homeostatic_bias_at(id,now_)}); } return out;
}
NeuroSnapshot NeurodynamicSubstrate::snapshot()const {
  NeuroSnapshot s; s.tau_membrane=tau_membrane_; s.tau_adaptation=tau_adaptation_; s.refractory_period=refractory_period_; s.reset_potential=reset_potential_; s.adaptation_increment=adaptation_increment_; s.tau_pre=tau_pre_; s.tau_post=tau_post_; s.a_plus=a_plus_; s.a_minus=a_minus_; s.weight_min=weight_min_; s.weight_max=weight_max_; s.tau_homeostasis=tau_homeostasis_; s.homeostasis_spike_increment=homeostasis_spike_increment_; s.event_guard=event_guard_; s.now=now_; s.next_sequence=next_sequence_; s.potential=potential_; s.base_threshold=base_threshold_; s.last_update=last_update_; s.refractory_until=refractory_until_; s.adaptation=adaptation_; s.last_spike=last_spike_; s.pre_trace=pre_trace_; s.post_trace=post_trace_; s.trace_last_update=trace_last_update_; s.homeostatic_threshold_bias=homeostatic_threshold_bias_; s.homeostasis_last_update=homeostasis_last_update_; s.spike_count=spike_count_; s.source=source_; s.target=target_; s.weight=weight_; s.delay=delay_; s.polarity=polarity_; s.plasticity_enabled=plasticity_enabled_; s.telemetry=telemetry_; auto queue=queue_; while(!queue.empty()){s.pending.push_back(queue.top());queue.pop();} return s;
}
void NeurodynamicSubstrate::restore(const NeuroSnapshot&s) {
  if (!(s.tau_membrane>0 && s.tau_adaptation>0 && s.refractory_period>=0 && s.event_guard>0 && s.tau_pre>0 && s.tau_post>0 && s.tau_homeostasis>0 && s.weight_min>=0 && s.weight_max>=s.weight_min && std::isfinite(s.tau_membrane) && std::isfinite(s.tau_adaptation) && std::isfinite(s.refractory_period) && std::isfinite(s.reset_potential) && std::isfinite(s.adaptation_increment) && std::isfinite(s.tau_pre) && std::isfinite(s.tau_post) && finite_nonnegative(s.a_plus) && finite_nonnegative(s.a_minus) && std::isfinite(s.weight_min) && std::isfinite(s.weight_max) && finite_nonnegative(s.homeostasis_spike_increment) && std::isfinite(s.now)) || s.potential.size()!=s.base_threshold.size() || s.potential.size()!=s.last_update.size() || s.potential.size()!=s.refractory_until.size() || s.potential.size()!=s.adaptation.size() || s.potential.size()!=s.last_spike.size() || s.potential.size()!=s.pre_trace.size() || s.potential.size()!=s.post_trace.size() || s.potential.size()!=s.trace_last_update.size() || s.potential.size()!=s.homeostatic_threshold_bias.size() || s.potential.size()!=s.homeostasis_last_update.size() || s.potential.size()!=s.spike_count.size() || s.source.size()!=s.target.size() || s.source.size()!=s.weight.size() || s.source.size()!=s.delay.size() || s.source.size()!=s.polarity.size() || s.source.size()!=s.plasticity_enabled.size()) throw std::invalid_argument("invalid neuro snapshot");
  for(std::size_t i=0;i<s.potential.size();++i) if(!std::isfinite(s.potential[i]) || !std::isfinite(s.base_threshold[i]) || !std::isfinite(s.last_update[i]) || s.last_update[i]>s.now || !valid_history(s.refractory_until[i]) || !std::isfinite(s.adaptation[i]) || !valid_history(s.last_spike[i]) || !finite_nonnegative(s.pre_trace[i]) || !finite_nonnegative(s.post_trace[i]) || !std::isfinite(s.trace_last_update[i]) || s.trace_last_update[i]>s.now || !finite_nonnegative(s.homeostatic_threshold_bias[i]) || !std::isfinite(s.homeostasis_last_update[i]) || s.homeostasis_last_update[i]>s.now) throw std::invalid_argument("invalid snapshot micro kappa");
  for(std::size_t i=0;i<s.source.size();++i) if(s.source[i]>=s.potential.size() || s.target[i]>=s.potential.size() || !std::isfinite(s.weight[i]) || s.weight[i]<0 || s.plasticity_enabled[i]>1 || (s.plasticity_enabled[i] && (s.weight[i]<s.weight_min || s.weight[i]>s.weight_max)) || !std::isfinite(s.delay[i]) || s.delay[i]<=0 || (s.polarity[i]!=(std::uint8_t)MicroPolarity::Excitatory && s.polarity[i]!=(std::uint8_t)MicroPolarity::Inhibitory)) throw std::invalid_argument("invalid snapshot rho");
  std::set<std::uint64_t> sequences; for(auto const&e:s.pending) if(e.target>=s.potential.size() || !std::isfinite(e.time) || e.time<s.now || !std::isfinite(e.amplitude) || e.sequence>=s.next_sequence || !sequences.insert(e.sequence).second) throw std::invalid_argument("invalid snapshot event");
  tau_membrane_=s.tau_membrane; tau_adaptation_=s.tau_adaptation; refractory_period_=s.refractory_period; reset_potential_=s.reset_potential; adaptation_increment_=s.adaptation_increment; tau_pre_=s.tau_pre; tau_post_=s.tau_post; a_plus_=s.a_plus; a_minus_=s.a_minus; weight_min_=s.weight_min; weight_max_=s.weight_max; tau_homeostasis_=s.tau_homeostasis; homeostasis_spike_increment_=s.homeostasis_spike_increment; event_guard_=s.event_guard; now_=s.now; next_sequence_=s.next_sequence; potential_=s.potential; base_threshold_=s.base_threshold; last_update_=s.last_update; refractory_until_=s.refractory_until; adaptation_=s.adaptation; last_spike_=s.last_spike; pre_trace_=s.pre_trace; post_trace_=s.post_trace; trace_last_update_=s.trace_last_update; homeostatic_threshold_bias_=s.homeostatic_threshold_bias; homeostasis_last_update_=s.homeostasis_last_update; spike_count_=s.spike_count; source_=s.source; target_=s.target; weight_=s.weight; delay_=s.delay; polarity_=s.polarity; plasticity_enabled_=s.plasticity_enabled; telemetry_=s.telemetry; outgoing_.assign(potential_.size(),{}); incoming_.assign(potential_.size(),{}); while(!queue_.empty())queue_.pop(); for(std::uint32_t i=0;i<source_.size();++i){outgoing_[source_[i]].push_back(i);incoming_[target_[i]].push_back(i);} for(auto const&e:s.pending)queue_.push(e);
}
}
