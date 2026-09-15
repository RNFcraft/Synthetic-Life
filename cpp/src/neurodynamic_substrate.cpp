#include "se/neurodynamic_substrate.hpp"
#include <algorithm>
#include <cmath>
#include <set>
#include <stdexcept>

namespace se {
namespace {
bool finite_nonnegative(double value) { return std::isfinite(value) && value >= 0.; }
bool valid_history(double value) { return std::isfinite(value) || value == -INFINITY; }
} // namespace

NeurodynamicSubstrate::NeurodynamicSubstrate(double tm, double ta, double rp, double reset, double inc, std::uint64_t guard, double tpre, double tpost, double plus, double minus, double wmin, double wmax, double thomeo, double hinc, bool tracking, double awindow, std::uint32_t amin_support, std::uint32_t amin_members, std::uint32_t amax_members, std::uint32_t aconsolidation, double adecay, double member_ratio, double candidate_similarity, double temporal_similarity, std::uint32_t max_candidates, std::uint32_t max_consolidated, std::uint32_t max_edges, std::uint32_t max_recent) : tau_membrane_(tm), tau_adaptation_(ta), refractory_period_(rp), reset_potential_(reset), adaptation_increment_(inc), tau_pre_(tpre), tau_post_(tpost), a_plus_(plus), a_minus_(minus), weight_min_(wmin), weight_max_(wmax), tau_homeostasis_(thomeo), homeostasis_spike_increment_(hinc), assembly_tracking_enabled_(tracking), assembly_window_(awindow), assembly_decay_tau_(adecay), assembly_member_ratio_threshold_(member_ratio), assembly_candidate_similarity_threshold_(candidate_similarity), assembly_temporal_similarity_threshold_(temporal_similarity), assembly_min_support_(amin_support), assembly_min_members_(amin_members), assembly_max_members_(amax_members), assembly_consolidation_support_(aconsolidation), max_assembly_candidates_(max_candidates), max_consolidated_assemblies_(max_consolidated), max_temporal_edges_(max_edges), max_recent_spikes_(max_recent), event_guard_(guard) {
  if (!(tm > 0 && ta > 0 && rp >= 0 && guard > 0 && tpre > 0 && tpost > 0 && thomeo > 0 && wmin >= 0 && wmax >= wmin && awindow > 0 && adecay > 0 && amin_support > 0 && amin_members > 1 && amax_members >= amin_members && aconsolidation >= amin_support && member_ratio > 0 && member_ratio <= 1 && candidate_similarity > 0 && candidate_similarity <= 1 && temporal_similarity >= 0 && temporal_similarity <= 1 && max_candidates > 0 && max_consolidated > 0 && max_edges > 0 && max_recent >= amin_members && std::isfinite(tm) && std::isfinite(ta) && std::isfinite(rp) && std::isfinite(reset) && std::isfinite(inc) && std::isfinite(tpre) && std::isfinite(tpost) && finite_nonnegative(plus) && finite_nonnegative(minus) && std::isfinite(wmin) && std::isfinite(wmax) && finite_nonnegative(hinc)))
    throw std::invalid_argument("invalid innate neuro physiology");
}
void NeurodynamicSubstrate::validate_time(double time) const {
  if (!std::isfinite(time) || time < now_)
    throw std::invalid_argument("neural time must be finite and monotonic");
}
std::uint32_t NeurodynamicSubstrate::add_micro_kappa(double threshold) {
  if (!std::isfinite(threshold))
    throw std::invalid_argument("invalid threshold");
  auto id = (std::uint32_t)potential_.size();
  potential_.push_back(reset_potential_);
  base_threshold_.push_back(threshold);
  last_update_.push_back(now_);
  refractory_until_.push_back(-INFINITY);
  adaptation_.push_back(0.);
  last_spike_.push_back(-INFINITY);
  pre_trace_.push_back(0.);
  post_trace_.push_back(0.);
  trace_last_update_.push_back(now_);
  homeostatic_threshold_bias_.push_back(0.);
  homeostasis_last_update_.push_back(now_);
  spike_count_.push_back(0);
  node_activity_support_.push_back(0);
  outgoing_.emplace_back();
  incoming_.emplace_back();
  return id;
}
std::uint32_t NeurodynamicSubstrate::add_micro_rho(std::uint32_t source, std::uint32_t target, double weight, double delay, MicroPolarity polarity, bool enabled) {
  if (source >= potential_.size() || target >= potential_.size() || !std::isfinite(weight) || weight < 0 || (enabled && (weight < weight_min_ || weight > weight_max_)) || !std::isfinite(delay) || delay <= 0 || (polarity != MicroPolarity::Excitatory && polarity != MicroPolarity::Inhibitory))
    throw std::invalid_argument("invalid micro rho");
  auto id = (std::uint32_t)source_.size();
  source_.push_back(source);
  target_.push_back(target);
  weight_.push_back(weight);
  delay_.push_back(delay);
  polarity_.push_back((std::uint8_t)polarity);
  plasticity_enabled_.push_back(enabled);
  outgoing_[source].push_back(id);
  incoming_[target].push_back(id);
  return id;
}
void NeurodynamicSubstrate::schedule(std::uint32_t target, double amplitude, double time) {
  queue_.push({time, next_sequence_++, target, amplitude});
  telemetry_.max_queue_depth = std::max<std::uint64_t>(telemetry_.max_queue_depth, queue_.size());
}
void NeurodynamicSubstrate::inject(std::uint32_t target, double amplitude, double time) {
  validate_time(time);
  if (target >= potential_.size() || !std::isfinite(amplitude))
    throw std::invalid_argument("invalid neural injection");
  schedule(target, amplitude, time);
}
void NeurodynamicSubstrate::inject_batch(std::span<const std::uint32_t> targets, std::span<const double> amplitudes, std::span<const double> times) {
  if (targets.size() != amplitudes.size() || targets.size() != times.size())
    throw std::invalid_argument("sensory injection batch size mismatch");
  for (std::size_t i = 0; i < targets.size(); ++i) {
    validate_time(times[i]);
    if (targets[i] >= potential_.size() || !std::isfinite(amplitudes[i]))
      throw std::invalid_argument("invalid sensory injection");
  }
  for (std::size_t i = 0; i < targets.size(); ++i)
    schedule(targets[i], amplitudes[i], times[i]);
}
double NeurodynamicSubstrate::pre_trace_at(std::uint32_t id, double time) const { return pre_trace_[id] * std::exp(-(time - trace_last_update_[id]) / tau_pre_); }
double NeurodynamicSubstrate::post_trace_at(std::uint32_t id, double time) const { return post_trace_[id] * std::exp(-(time - trace_last_update_[id]) / tau_post_); }
double NeurodynamicSubstrate::homeostatic_bias_at(std::uint32_t id, double time) const { return homeostatic_threshold_bias_[id] * std::exp(-(time - homeostasis_last_update_[id]) / tau_homeostasis_); }
void NeurodynamicSubstrate::touch(std::uint32_t id, double time) {
  auto dt = time - last_update_[id];
  if (dt < 0)
    throw std::logic_error("neural time travel");
  if (dt) {
    potential_[id] *= std::exp(-dt / tau_membrane_);
    adaptation_[id] *= std::exp(-dt / tau_adaptation_);
    last_update_[id] = time;
  }
  auto homeo_dt = time - homeostasis_last_update_[id];
  if (homeo_dt < 0)
    throw std::logic_error("homeostasis time travel");
  if (homeo_dt) {
    homeostatic_threshold_bias_[id] *= std::exp(-homeo_dt / tau_homeostasis_);
    homeostasis_last_update_[id] = time;
  }
}
void NeurodynamicSubstrate::touch_traces(std::uint32_t id, double time) {
  auto dt = time - trace_last_update_[id];
  if (dt < 0)
    throw std::logic_error("trace time travel");
  if (dt) {
    pre_trace_[id] *= std::exp(-dt / tau_pre_);
    post_trace_[id] *= std::exp(-dt / tau_post_);
    trace_last_update_[id] = time;
  }
}
void NeurodynamicSubstrate::apply_plasticity(double time, const std::vector<std::uint32_t> &spikes) {
  std::map<std::uint32_t, double> deltas;
  for (auto target : spikes)
    for (auto rho : incoming_[target])
      if (plasticity_enabled_[rho])
        deltas[rho] += a_plus_ * pre_trace_at(source_[rho], time) * (weight_max_ - weight_[rho]);
  for (auto source : spikes)
    for (auto rho : outgoing_[source])
      if (plasticity_enabled_[rho])
        deltas[rho] -= a_minus_ * post_trace_at(target_[rho], time) * (weight_[rho] - weight_min_);
  for (auto const &[rho, delta] : deltas) {
    auto before = weight_[rho];
    auto after = std::clamp(before + delta, weight_min_, weight_max_);
    if (after == before)
      continue;
    weight_[rho] = after;
    ++telemetry_.plasticity_updates;
    if (after > before)
      ++telemetry_.potentiation_updates;
    else
      ++telemetry_.depression_updates;
    telemetry_.total_abs_weight_change += std::abs(after - before);
  }
}
void NeurodynamicSubstrate::emit_bridge_event(std::uint64_t assembly_id, double time, double confidence, AssemblyBridgeEventKind kind) {
  std::uint64_t episode_id{};double contribution{};
  if(kind==AssemblyBridgeEventKind::Recognized){
    auto episode=std::find_if(recognition_episodes_.begin(),recognition_episodes_.end(),[&](auto const&row){return row.assembly_id==assembly_id;});
    if(episode==recognition_episodes_.end()){recognition_episodes_.push_back({assembly_id,next_recognition_episode_id_++,time,0.});episode=std::prev(recognition_episodes_.end());}
    else if(time-episode->last_time>assembly_window_){episode->episode_id=next_recognition_episode_id_++;episode->peak_confidence=0.;}
    episode->last_time=time;episode_id=episode->episode_id;contribution=std::max(0.,confidence-episode->peak_confidence);episode->peak_confidence=std::max(episode->peak_confidence,confidence);
  }
  bridge_events_.push_back({next_bridge_sequence_++, assembly_id, episode_id, time, confidence, contribution, kind});
  if (bridge_events_.size() > bridge_event_capacity)
    bridge_events_.erase(bridge_events_.begin(), bridge_events_.begin() + (bridge_events_.size() - bridge_event_capacity));
}
std::vector<AssemblyBridgeEvent> NeurodynamicSubstrate::assembly_bridge_events_after(std::uint64_t cursor, std::size_t limit) const {
  if (!limit)
    return {};
  if (!bridge_events_.empty() && cursor + 1 < bridge_events_.front().sequence)
    throw std::runtime_error("assembly bridge cursor fell behind bounded event log");
  std::vector<AssemblyBridgeEvent> out;
  out.reserve(std::min(limit, bridge_events_.size()));
  for (auto const &e : bridge_events_)
    if (e.sequence > cursor) {
      out.push_back(e);
      if (out.size() == limit)
        break;
    }
  return out;
}
void NeurodynamicSubstrate::observe_assemblies(double time, const std::vector<std::uint32_t> &spikes) {
  if (!assembly_tracking_enabled_ || spikes.empty())
    return;
  recent_spikes_.erase(std::remove_if(recent_spikes_.begin(), recent_spikes_.end(), [&](const NeuralEvent &e) { return time - e.time > assembly_window_; }), recent_spikes_.end());
  std::vector<NeuralEvent> episode = recent_spikes_;
  for (auto id : spikes) {
    episode.push_back({time, 0, id, 0.});
    ++node_activity_support_[id];
  }
  std::vector<std::uint32_t> members;
  for (auto const &e : episode)
    if (std::find(members.begin(), members.end(), e.target) == members.end())
      members.push_back(e.target);
  std::sort(members.begin(), members.end());
  if (members.size() > assembly_max_members_)
    members.resize(assembly_max_members_);
  std::vector<std::array<std::uint32_t, 2>> edges;
  for (auto const &a : episode)
    for (auto const &b : episode)
      if (a.time < b.time && a.target != b.target && std::binary_search(members.begin(), members.end(), a.target) && std::binary_search(members.begin(), members.end(), b.target)) {
        std::array<std::uint32_t, 2> edge{a.target, b.target};
        if (std::find(edges.begin(), edges.end(), edge) == edges.end())
          edges.push_back(edge);
      }
  std::sort(edges.begin(), edges.end());
  if (edges.size() > max_temporal_edges_)
    edges.resize(max_temporal_edges_);
  auto intersections = [](auto const &a, auto const &b) {
    std::size_t n{};
    for (auto const &v : a)
      if (std::find(b.begin(), b.end(), v) != b.end())
        ++n;
    return n;
  };
  // Read-only recognition of every consolidated assembly, including partial
  // episodes.
  for (auto const &a : assemblies_)
    if (a.consolidated && !members.empty()) {
      std::vector<std::uint32_t> matched;
      for (auto id : members)
        if (std::find(a.members.begin(), a.members.end(), id) != a.members.end())
          matched.push_back(id);
      if (matched.empty())
        continue;
      double completeness = double(matched.size()) / a.members.size();
      double temporal = a.temporal_edges.empty() ? (edges.empty() ? 1. : 0.) : double(intersections(edges, a.temporal_edges)) / a.temporal_edges.size();
      double confidence = .25 * completeness + .75 * temporal;
      recent_matches_.push_back({a.id, confidence, completeness, temporal, time, matched});
      emit_bridge_event(a.id, time, confidence, AssemblyBridgeEventKind::Recognized);
      ++telemetry_.assembly_matches;
    }
  if (recent_matches_.size() > 32)
    recent_matches_.erase(recent_matches_.begin(), recent_matches_.begin() + (recent_matches_.size() - 32));
  if (members.size() >= assembly_min_members_) {
    AssemblyRecord *best{};
    double best_score{};
    for (auto &a : assemblies_) {
      double mi = intersections(members, a.members), mu = members.size() + a.members.size() - mi, member_score = mu ? mi / mu : 0.;
      double ei = intersections(edges, a.temporal_edges), eu = edges.size() + a.temporal_edges.size() - ei, edge_score = eu ? ei / eu : 1.;
      if (member_score >= assembly_candidate_similarity_threshold_ && edge_score >= assembly_temporal_similarity_threshold_) {
        double score = member_score + edge_score;
        if (!best || score > best_score || (score == best_score && a.id < best->id)) {
          best = &a;
          best_score = score;
        }
      }
    }
    if (best) {
      ++best->support;
      best->decayed_support = best->support;
      best->last_seen = time;
      for (auto id : members) {
        auto row = std::find_if(best->member_support.begin(), best->member_support.end(), [&](auto const &r) { return (std::uint32_t)r[0] == id; });
        if (row == best->member_support.end())
          best->member_support.push_back({double(id), 1.});
        else
          ++(*row)[1];
      }
      for (auto edge : edges) {
        auto row = std::find_if(best->temporal_support.begin(), best->temporal_support.end(), [&](auto const &r) { return (std::uint32_t)r[0] == edge[0] && (std::uint32_t)r[1] == edge[1]; });
        if (row == best->temporal_support.end())
          best->temporal_support.push_back({double(edge[0]), double(edge[1]), 1.});
        else
          ++(*row)[2];
      }
      best->members.clear();
      for (auto const &r : best->member_support) {
        auto id = (std::uint32_t)r[0];
        double recurrence = r[1] / best->support, specificity = r[1] / std::max<std::uint64_t>(1, node_activity_support_[id]);
        if (recurrence >= assembly_member_ratio_threshold_ && recurrence * specificity >= .3)
          best->members.push_back(id);
      }
      std::sort(best->members.begin(), best->members.end());
      best->temporal_edges.clear();
      for (auto const &r : best->temporal_support) {
        auto source = (std::uint32_t)r[0], target = (std::uint32_t)r[1];
        if (r[2] / best->support >= assembly_temporal_similarity_threshold_ && std::binary_search(best->members.begin(), best->members.end(), source) && std::binary_search(best->members.begin(), best->members.end(), target))
          best->temporal_edges.push_back({source, target});
      }
      std::sort(best->temporal_edges.begin(), best->temporal_edges.end());
      ++telemetry_.assembly_evidence_updates;
      if (!best->candidate && best->support >= assembly_min_support_) {
        best->candidate = true;
        ++telemetry_.assembly_candidates_created;
      }
      std::size_t consolidated = std::count_if(assemblies_.begin(), assemblies_.end(), [](auto const &a) { return a.consolidated; });
      if (best->candidate && !best->consolidated && best->support >= assembly_consolidation_support_ && consolidated < max_consolidated_assemblies_) {
        best->consolidated = true;
        emit_bridge_event(best->id, time, 1., AssemblyBridgeEventKind::Consolidated);
        ++telemetry_.assemblies_consolidated;
      }
    } else {
      std::size_t candidates = std::count_if(assemblies_.begin(), assemblies_.end(), [](auto const &a) { return !a.consolidated; });
      if (candidates >= max_assembly_candidates_) {
        auto victim = std::min_element(assemblies_.begin(), assemblies_.end(), [&](auto const &a, auto const &b) {
          if (a.consolidated)
            return false;
          if (b.consolidated)
            return true;
          double ad = a.support * std::exp(-(time - a.last_seen) / assembly_decay_tau_), bd = b.support * std::exp(-(time - b.last_seen) / assembly_decay_tau_);
          return ad < bd || (ad == bd && (a.last_seen < b.last_seen || (a.last_seen == b.last_seen && a.id < b.id)));
        });
        if (victim != assemblies_.end() && !victim->consolidated) {
          assemblies_.erase(victim);
          ++telemetry_.assembly_prunes;
        }
      }
      AssemblyRecord record;
      record.id = next_assembly_id_++;
      record.members = members;
      record.temporal_edges = edges;
      record.support = 1;
      record.decayed_support = 1.;
      record.first_seen = record.last_seen = time;
      for (auto id : members) record.member_support.push_back({double(id), 1.});
      for (auto edge : edges) record.temporal_support.push_back({double(edge[0]), double(edge[1]), 1.});
      assemblies_.push_back(std::move(record));
    }
  }
  recent_spikes_ = std::move(episode);
  if (recent_spikes_.size() > max_recent_spikes_)
    recent_spikes_.erase(recent_spikes_.begin(), recent_spikes_.begin() + (recent_spikes_.size() - max_recent_spikes_));
  telemetry_.max_recent_activity_size = std::max<std::uint64_t>(telemetry_.max_recent_activity_size, recent_spikes_.size());
}
void NeurodynamicSubstrate::deliver(double time, const std::vector<NeuralEvent> &events) {
  std::map<std::uint32_t, std::vector<double>> groups;
  for (auto const &e : events) groups[e.target].push_back(e.amplitude);
  std::vector<std::uint32_t> spikes;
  for (auto &[id, amplitudes] : groups) {
    std::sort(amplitudes.begin(), amplitudes.end());
    double sum{};
    for (auto amplitude : amplitudes) sum += amplitude;
    touch(id, time);
    if (time < refractory_until_[id]) {
      telemetry_.refractory_discards += amplitudes.size();
      potential_[id] = reset_potential_;
      continue;
    }
    potential_[id] += sum;
    if (potential_[id] >= base_threshold_[id] + adaptation_[id] + homeostatic_threshold_bias_[id]) {
      ++spike_count_[id];
      last_spike_[id] = time;
      potential_[id] = reset_potential_;
      adaptation_[id] += adaptation_increment_;
      homeostatic_threshold_bias_[id] += homeostasis_spike_increment_;
      refractory_until_[id] = time + refractory_period_;
      ++telemetry_.total_spikes;
      if (homeostasis_spike_increment_ > 0) {
        ++telemetry_.homeostatic_updates;
        telemetry_.max_observed_homeostatic_bias = std::max(telemetry_.max_observed_homeostatic_bias, homeostatic_threshold_bias_[id]);
      }
      spikes.push_back(id);
    }
  }
  // All deltas see traces strictly before this timestamp; same-time spikes
  // cannot cause each other.
  apply_plasticity(time, spikes);
  observe_assemblies(time, spikes);
  for (auto id : spikes) {
    touch_traces(id, time);
    pre_trace_[id] += 1.;
    post_trace_[id] += 1.;
    for (auto rho : outgoing_[id]) schedule(target_[rho], polarity_[rho] == (std::uint8_t)MicroPolarity::Excitatory ? weight_[rho] : -weight_[rho], time + delay_[rho]);
  }
}
void NeurodynamicSubstrate::advance_to(double time) {
  validate_time(time);
  telemetry_.last_advance_events_processed = 0;
  while (!queue_.empty() && queue_.top().time <= time) {
    auto stamp = queue_.top().time;
    std::vector<NeuralEvent> batch;
    while (!queue_.empty() && queue_.top().time == stamp) {
      batch.push_back(queue_.top());
      queue_.pop();
      if (++telemetry_.last_advance_events_processed > event_guard_)
        throw std::runtime_error("neural event safety guard exceeded");
    }
    telemetry_.total_events_processed += batch.size();
    deliver(stamp, batch);
  }
  now_ = time;
}
bool NeurodynamicSubstrate::advance_to_bridge_boundary(double time, std::size_t max_new_bridge_events) {
  validate_time(time);
  if (!max_new_bridge_events)
    throw std::invalid_argument("bridge advance limit must be positive");
  telemetry_.last_advance_events_processed = 0;
  auto first_bridge_sequence = next_bridge_sequence_;
  while (!queue_.empty() && queue_.top().time <= time) {
    auto stamp = queue_.top().time;
    std::vector<NeuralEvent> batch;
    while (!queue_.empty() && queue_.top().time == stamp) {
      batch.push_back(queue_.top());
      queue_.pop();
      if (++telemetry_.last_advance_events_processed > event_guard_)
        throw std::runtime_error("neural event safety guard exceeded");
    }
    telemetry_.total_events_processed += batch.size();
    deliver(stamp, batch);
    now_ = stamp;
    if (next_bridge_sequence_ - first_bridge_sequence >= max_new_bridge_events)
      return false;
  }
  now_ = time;
  return true;
}
std::vector<std::array<double, 10>> NeurodynamicSubstrate::states(const std::vector<std::uint32_t> &ids) const {
  std::vector<std::array<double, 10>> out;
  out.reserve(ids.size());
  for (auto id : ids) {
    if (id >= potential_.size())
      throw std::out_of_range("invalid micro kappa");
    auto dt = now_ - last_update_[id];
    if (dt < 0)
      throw std::logic_error("invalid stored neural time");
    out.push_back({potential_[id] * std::exp(-dt / tau_membrane_), base_threshold_[id], last_update_[id], refractory_until_[id], adaptation_[id] * std::exp(-dt / tau_adaptation_), last_spike_[id], double(spike_count_[id]), pre_trace_at(id, now_), post_trace_at(id, now_), homeostatic_bias_at(id, now_)});
  }
  return out;
}
NeuroSnapshot NeurodynamicSubstrate::snapshot() const {
  NeuroSnapshot s;
  s.tau_membrane = tau_membrane_;
  s.tau_adaptation = tau_adaptation_;
  s.refractory_period = refractory_period_;
  s.reset_potential = reset_potential_;
  s.adaptation_increment = adaptation_increment_;
  s.tau_pre = tau_pre_;
  s.tau_post = tau_post_;
  s.a_plus = a_plus_;
  s.a_minus = a_minus_;
  s.weight_min = weight_min_;
  s.weight_max = weight_max_;
  s.tau_homeostasis = tau_homeostasis_;
  s.homeostasis_spike_increment = homeostasis_spike_increment_;
  s.assembly_tracking_enabled = assembly_tracking_enabled_;
  s.assembly_window = assembly_window_;
  s.assembly_decay_tau = assembly_decay_tau_;
  s.assembly_member_ratio_threshold = assembly_member_ratio_threshold_;
  s.assembly_candidate_similarity_threshold = assembly_candidate_similarity_threshold_;
  s.assembly_temporal_similarity_threshold = assembly_temporal_similarity_threshold_;
  s.assembly_min_support = assembly_min_support_;
  s.assembly_min_members = assembly_min_members_;
  s.assembly_max_members = assembly_max_members_;
  s.assembly_consolidation_support = assembly_consolidation_support_;
  s.max_assembly_candidates = max_assembly_candidates_;
  s.max_consolidated_assemblies = max_consolidated_assemblies_;
  s.max_temporal_edges = max_temporal_edges_;
  s.max_recent_spikes = max_recent_spikes_;
  s.next_assembly_id = next_assembly_id_;
  s.recent_spikes = recent_spikes_;
  s.assemblies = assemblies_;
  s.recent_matches = recent_matches_;
  s.node_activity_support = node_activity_support_;
  s.next_bridge_sequence = next_bridge_sequence_;
  s.bridge_events = bridge_events_;
  s.next_recognition_episode_id=next_recognition_episode_id_;
  s.recognition_episodes=recognition_episodes_;
  s.event_guard = event_guard_;
  s.now = now_;
  s.next_sequence = next_sequence_;
  s.potential = potential_;
  s.base_threshold = base_threshold_;
  s.last_update = last_update_;
  s.refractory_until = refractory_until_;
  s.adaptation = adaptation_;
  s.last_spike = last_spike_;
  s.pre_trace = pre_trace_;
  s.post_trace = post_trace_;
  s.trace_last_update = trace_last_update_;
  s.homeostatic_threshold_bias = homeostatic_threshold_bias_;
  s.homeostasis_last_update = homeostasis_last_update_;
  s.spike_count = spike_count_;
  s.source = source_;
  s.target = target_;
  s.weight = weight_;
  s.delay = delay_;
  s.polarity = polarity_;
  s.plasticity_enabled = plasticity_enabled_;
  s.telemetry = telemetry_;
  auto queue = queue_;
  while (!queue.empty()) {
    s.pending.push_back(queue.top());
    queue.pop();
  }
  return s;
}
void NeurodynamicSubstrate::restore(const NeuroSnapshot &s) {
  if (!(s.tau_membrane > 0 && s.tau_adaptation > 0 && s.refractory_period >= 0 && s.event_guard > 0 && s.tau_pre > 0 && s.tau_post > 0 && s.tau_homeostasis > 0 && s.weight_min >= 0 && s.weight_max >= s.weight_min && std::isfinite(s.tau_membrane) && std::isfinite(s.tau_adaptation) && std::isfinite(s.refractory_period) && std::isfinite(s.reset_potential) && std::isfinite(s.adaptation_increment) && std::isfinite(s.tau_pre) && std::isfinite(s.tau_post) && finite_nonnegative(s.a_plus) && finite_nonnegative(s.a_minus) && std::isfinite(s.weight_min) && std::isfinite(s.weight_max) && finite_nonnegative(s.homeostasis_spike_increment) && std::isfinite(s.now)) || s.potential.size() != s.base_threshold.size() || s.potential.size() != s.last_update.size() || s.potential.size() != s.refractory_until.size() || s.potential.size() != s.adaptation.size() || s.potential.size() != s.last_spike.size() || s.potential.size() != s.pre_trace.size() || s.potential.size() != s.post_trace.size() || s.potential.size() != s.trace_last_update.size() || s.potential.size() != s.homeostatic_threshold_bias.size() || s.potential.size() != s.homeostasis_last_update.size() || s.potential.size() != s.spike_count.size() || s.source.size() != s.target.size() || s.source.size() != s.weight.size() || s.source.size() != s.delay.size() || s.source.size() != s.polarity.size() || s.source.size() != s.plasticity_enabled.size())
    throw std::invalid_argument("invalid neuro snapshot");
  for (std::size_t i = 0; i < s.potential.size(); ++i)
    if (!std::isfinite(s.potential[i]) || !std::isfinite(s.base_threshold[i]) || !std::isfinite(s.last_update[i]) || s.last_update[i] > s.now || !valid_history(s.refractory_until[i]) || !std::isfinite(s.adaptation[i]) || !valid_history(s.last_spike[i]) || !finite_nonnegative(s.pre_trace[i]) || !finite_nonnegative(s.post_trace[i]) || !std::isfinite(s.trace_last_update[i]) || s.trace_last_update[i] > s.now || !finite_nonnegative(s.homeostatic_threshold_bias[i]) || !std::isfinite(s.homeostasis_last_update[i]) || s.homeostasis_last_update[i] > s.now)
      throw std::invalid_argument("invalid snapshot micro kappa");
  for (std::size_t i = 0; i < s.source.size(); ++i)
    if (s.source[i] >= s.potential.size() || s.target[i] >= s.potential.size() || !std::isfinite(s.weight[i]) || s.weight[i] < 0 || s.plasticity_enabled[i] > 1 || (s.plasticity_enabled[i] && (s.weight[i] < s.weight_min || s.weight[i] > s.weight_max)) || !std::isfinite(s.delay[i]) || s.delay[i] <= 0 || (s.polarity[i] != (std::uint8_t)MicroPolarity::Excitatory && s.polarity[i] != (std::uint8_t)MicroPolarity::Inhibitory))
      throw std::invalid_argument("invalid snapshot rho");
  std::set<std::uint64_t> sequences;
  for (auto const &e : s.pending)
    if (e.target >= s.potential.size() || !std::isfinite(e.time) || e.time < s.now || !std::isfinite(e.amplitude) || e.sequence >= s.next_sequence || !sequences.insert(e.sequence).second)
      throw std::invalid_argument("invalid snapshot event");
  if (!(s.assembly_window > 0) || !(s.assembly_decay_tau > 0) || s.assembly_member_ratio_threshold <= 0 || s.assembly_member_ratio_threshold > 1 || s.assembly_candidate_similarity_threshold <= 0 || s.assembly_candidate_similarity_threshold > 1 || s.assembly_temporal_similarity_threshold < 0 || s.assembly_temporal_similarity_threshold > 1 || s.assembly_min_support == 0 || s.assembly_min_members < 2 || s.assembly_max_members < s.assembly_min_members || s.assembly_consolidation_support < s.assembly_min_support || s.max_assembly_candidates == 0 || s.max_consolidated_assemblies == 0 || s.max_temporal_edges == 0 || s.max_recent_spikes < s.assembly_min_members || s.node_activity_support.size() != s.potential.size())
    throw std::invalid_argument("invalid assembly snapshot physiology");
  for (auto const &e : s.recent_spikes)
    if (e.target >= s.potential.size() || !std::isfinite(e.time) || e.time > s.now)
      throw std::invalid_argument("invalid recent assembly spike");
  for (auto const &a : s.assemblies) {
    if (a.members.size() > s.assembly_max_members || a.temporal_edges.size() > s.max_temporal_edges || !std::isfinite(a.first_seen) || !std::isfinite(a.last_seen) || a.last_seen < a.first_seen)
      throw std::invalid_argument("invalid assembly record");
    for (auto id : a.members)
      if (id >= s.potential.size())
        throw std::invalid_argument("invalid assembly member");
  }
  if(!s.next_bridge_sequence||!s.next_recognition_episode_id||s.bridge_events.size()>bridge_event_capacity||s.recognition_episodes.size()>s.max_consolidated_assemblies)throw std::invalid_argument("invalid assembly bridge bounds");
  std::uint64_t previous_bridge{};double previous_bridge_time=-INFINITY;
  for (auto const &event : s.bridge_events) {
    auto assembly = std::find_if(s.assemblies.begin(), s.assemblies.end(), [&](auto const &a) { return a.id == event.assembly_id; });
    if (!event.sequence || event.sequence <= previous_bridge || event.sequence >= s.next_bridge_sequence || assembly == s.assemblies.end() || !assembly->consolidated || !std::isfinite(event.time) || event.time<previous_bridge_time || event.time > s.now || !std::isfinite(event.confidence) || event.confidence < 0. || event.confidence > 1. || !std::isfinite(event.contribution)||event.contribution<0.||event.contribution>event.confidence || (event.kind != AssemblyBridgeEventKind::Consolidated && event.kind != AssemblyBridgeEventKind::Recognized)|| (event.kind==AssemblyBridgeEventKind::Consolidated&&(event.recognition_episode_id||event.contribution))||(event.kind==AssemblyBridgeEventKind::Recognized&&(!event.recognition_episode_id||event.recognition_episode_id>=s.next_recognition_episode_id)))
      throw std::invalid_argument("invalid assembly bridge event");
    previous_bridge = event.sequence;previous_bridge_time=event.time;
  }
  std::set<std::uint64_t> episode_assemblies,episode_ids;
  for(auto const&episode:s.recognition_episodes){auto assembly=std::find_if(s.assemblies.begin(),s.assemblies.end(),[&](auto const&a){return a.id==episode.assembly_id;});if(assembly==s.assemblies.end()||!assembly->consolidated||!episode.episode_id||episode.episode_id>=s.next_recognition_episode_id||!episode_assemblies.insert(episode.assembly_id).second||!episode_ids.insert(episode.episode_id).second||!std::isfinite(episode.last_time)||episode.last_time>s.now||!std::isfinite(episode.peak_confidence)||episode.peak_confidence<0.||episode.peak_confidence>1.)throw std::invalid_argument("invalid recognition episode state");}
  assembly_tracking_enabled_ = s.assembly_tracking_enabled;
  assembly_window_ = s.assembly_window;
  assembly_decay_tau_ = s.assembly_decay_tau;
  assembly_member_ratio_threshold_ = s.assembly_member_ratio_threshold;
  assembly_candidate_similarity_threshold_ = s.assembly_candidate_similarity_threshold;
  assembly_temporal_similarity_threshold_ = s.assembly_temporal_similarity_threshold;
  assembly_min_support_ = s.assembly_min_support;
  assembly_min_members_ = s.assembly_min_members;
  assembly_max_members_ = s.assembly_max_members;
  assembly_consolidation_support_ = s.assembly_consolidation_support;
  max_assembly_candidates_ = s.max_assembly_candidates;
  max_consolidated_assemblies_ = s.max_consolidated_assemblies;
  max_temporal_edges_ = s.max_temporal_edges;
  max_recent_spikes_ = s.max_recent_spikes;
  next_assembly_id_ = s.next_assembly_id;
  recent_spikes_ = s.recent_spikes;
  assemblies_ = s.assemblies;
  recent_matches_ = s.recent_matches;
  node_activity_support_ = s.node_activity_support;
  next_bridge_sequence_ = s.next_bridge_sequence;
  bridge_events_ = s.bridge_events;
  next_recognition_episode_id_=s.next_recognition_episode_id;
  recognition_episodes_=s.recognition_episodes;
  for (auto &assembly : assemblies_) {
    assembly.temporal_edges.clear();
    for (auto const &r : assembly.temporal_support) {
      auto source = (std::uint32_t)r[0], target = (std::uint32_t)r[1];
      if (assembly.support && r[2] / assembly.support >= assembly_temporal_similarity_threshold_ && std::binary_search(assembly.members.begin(), assembly.members.end(), source) && std::binary_search(assembly.members.begin(), assembly.members.end(), target))
        assembly.temporal_edges.push_back({source, target});
    }
    std::sort(assembly.temporal_edges.begin(), assembly.temporal_edges.end());
  }
  tau_membrane_ = s.tau_membrane;
  tau_adaptation_ = s.tau_adaptation;
  refractory_period_ = s.refractory_period;
  reset_potential_ = s.reset_potential;
  adaptation_increment_ = s.adaptation_increment;
  tau_pre_ = s.tau_pre;
  tau_post_ = s.tau_post;
  a_plus_ = s.a_plus;
  a_minus_ = s.a_minus;
  weight_min_ = s.weight_min;
  weight_max_ = s.weight_max;
  tau_homeostasis_ = s.tau_homeostasis;
  homeostasis_spike_increment_ = s.homeostasis_spike_increment;
  event_guard_ = s.event_guard;
  now_ = s.now;
  next_sequence_ = s.next_sequence;
  potential_ = s.potential;
  base_threshold_ = s.base_threshold;
  last_update_ = s.last_update;
  refractory_until_ = s.refractory_until;
  adaptation_ = s.adaptation;
  last_spike_ = s.last_spike;
  pre_trace_ = s.pre_trace;
  post_trace_ = s.post_trace;
  trace_last_update_ = s.trace_last_update;
  homeostatic_threshold_bias_ = s.homeostatic_threshold_bias;
  homeostasis_last_update_ = s.homeostasis_last_update;
  spike_count_ = s.spike_count;
  source_ = s.source;
  target_ = s.target;
  weight_ = s.weight;
  delay_ = s.delay;
  polarity_ = s.polarity;
  plasticity_enabled_ = s.plasticity_enabled;
  telemetry_ = s.telemetry;
  outgoing_.assign(potential_.size(), {});
  incoming_.assign(potential_.size(), {});
  while (!queue_.empty()) queue_.pop();
  for (std::uint32_t i = 0; i < source_.size(); ++i) {
    outgoing_[source_[i]].push_back(i);
    incoming_[target_[i]].push_back(i);
  }
  for (auto const &e : s.pending) queue_.push(e);
}
} // namespace se
