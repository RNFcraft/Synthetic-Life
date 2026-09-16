#include "se/native_brain_engine.hpp"
#include "se/world.hpp"
#ifdef SE_WITH_OBSERVER
#include "se/observer.hpp"
#endif
#include "se/event_scheduler.hpp"
#include "se/neurodynamic_substrate.hpp"
#include <algorithm>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
using namespace se;
PYBIND11_MODULE(_native_brain, m) {
  // RuntimeEvent — causal wire record: [time: WorldTime float64,
  // id: scheduler uint64 sequence, type: RuntimeEventType, payload: opaque
  // uint64]. Python может читать поля, но порядок (time, id) задаёт native queue.
  py::class_<RuntimeEvent>(m, "RuntimeEvent").def(py::init([](double t, std::uint64_t id, RuntimeEventType type, std::uint64_t payload) { return RuntimeEvent{t, id, type, payload}; })).def_readonly("time", &RuntimeEvent::time).def_readonly("id", &RuntimeEvent::id).def_readonly("type", &RuntimeEvent::type).def_readonly("payload", &RuntimeEvent::payload);
  py::enum_<RuntimeEventType>(m, "RuntimeEventType").value("WORLD_ACTION_COMPLETE", RuntimeEventType::WorldActionComplete).value("WORLD_SPAWN", RuntimeEventType::WorldSpawn).value("SENSORY_CHANGE", RuntimeEventType::SensoryChange).value("COGNITION_WAKE", RuntimeEventType::CognitionWake).value("COGNITION_CONTINUE", RuntimeEventType::CognitionContinue).value("MEMORY_TIMER", RuntimeEventType::MemoryTimer).value("RELATION_TIMER", RuntimeEventType::RelationTimer).value("MAINTENANCE", RuntimeEventType::Maintenance).value("EXTERNAL_INPUT", RuntimeEventType::ExternalInput).value("LANGUAGE_INPUT", RuntimeEventType::LanguageInput).value("LANGUAGE_CONTINUE", RuntimeEventType::LanguageContinue).value("NEURAL_BRIDGE",RuntimeEventType::NeuralBridge);
  py::class_<EventScheduler>(m, "EventScheduler").def(py::init<>()).def("schedule", &EventScheduler::schedule, py::arg("time"), py::arg("event_type"), py::arg("payload") = 0).def("pop_ready", &EventScheduler::pop_ready).def("snapshot", &EventScheduler::snapshot).def("restore", &EventScheduler::restore,py::arg("now"),py::arg("next_id"),py::arg("events"),py::arg("peak_size")=0).def_property_readonly("now", &EventScheduler::now).def_property_readonly("next_id", &EventScheduler::next_id).def_property_readonly("size", &EventScheduler::size).def_property_readonly("peak_size",&EventScheduler::peak_size);
  py::enum_<MicroPolarity>(m, "MicroPolarity").value("EXCITATORY", MicroPolarity::Excitatory).value("INHIBITORY", MicroPolarity::Inhibitory);
  py::class_<NeurodynamicSubstrate>(m, "NeurodynamicSubstrate")
      .def(py::init([](double tm, double ta, double rp, double reset,
                       double inc, std::uint64_t guard, double tpre,
                       double tpost, double plus, double minus, double wmin,
                       double wmax, double thomeo, double hinc, bool tracking,
                       double window, std::uint32_t min_support,
                       std::uint32_t min_members, std::uint32_t max_members,
                       std::uint32_t consolidation, double decay) {
             return NeurodynamicSubstrate(
                 tm, ta, rp, reset, inc, guard, tpre, tpost, plus, minus, wmin,
                 wmax, thomeo, hinc, tracking, window, min_support, min_members,
                 max_members, consolidation, decay);
           }),
           py::arg("tau_membrane") = 10., py::arg("tau_adaptation") = 100.,
           py::arg("refractory_period") = 1., py::arg("reset_potential") = 0.,
           py::arg("adaptation_increment") = .1,
           py::arg("event_guard") = 1'000'000, py::arg("tau_pre") = 20.,
           py::arg("tau_post") = 20., py::arg("a_plus") = .1,
           py::arg("a_minus") = .1, py::arg("weight_min") = 0.,
           py::arg("weight_max") = 10., py::arg("tau_homeostasis") = 1'000.,
           py::arg("homeostasis_spike_increment") = 0.,
           py::arg("assembly_tracking_enabled") = false,
           py::arg("assembly_window") = 5., py::arg("assembly_min_support") = 2,
           py::arg("assembly_min_members") = 3,
           py::arg("assembly_max_members") = 8,
           py::arg("assembly_consolidation_support") = 3,
           py::arg("assembly_decay_tau") = 1'000.)
      .def("add_micro_kappa", &NeurodynamicSubstrate::add_micro_kappa,
           py::arg("base_threshold") = 1.)
      .def("add_micro_rho", &NeurodynamicSubstrate::add_micro_rho,
           py::arg("source"), py::arg("target"), py::arg("weight"),
           py::arg("delay"), py::arg("polarity"),
           py::arg("plasticity_enabled") = false)
      .def("inject", &NeurodynamicSubstrate::inject)
      .def("inject_batch",
           [](NeurodynamicSubstrate &s, const std::vector<std::uint32_t> &targets,
              const std::vector<double> &amplitudes, const std::vector<double> &times) {
             py::gil_scoped_release release;
             s.inject_batch(targets, amplitudes, times);
           })
      .def("advance_to",
           [](NeurodynamicSubstrate &s, double t) {
             py::gil_scoped_release release;
             s.advance_to(t);
           })
      .def("advance_to_bridge_boundary",
           [](NeurodynamicSubstrate &s, double t, std::size_t limit) {
             py::gil_scoped_release release;
             return s.advance_to_bridge_boundary(t, limit);
           }, py::arg("time"), py::arg("max_new_bridge_events") = 64)
      .def("states", &NeurodynamicSubstrate::states)
      .def_property_readonly("micro_kappa_count",
                             &NeurodynamicSubstrate::micro_kappa_count)
      .def_property_readonly("micro_rho_count",
                             &NeurodynamicSubstrate::micro_rho_count)
      .def_property_readonly("pending_events",
                             &NeurodynamicSubstrate::pending_events)
      .def_property_readonly("current_time", &NeurodynamicSubstrate::now)
      .def_property_readonly("next_event_sequence",
                             &NeurodynamicSubstrate::next_sequence)
      .def("assemblies",
           [](const NeurodynamicSubstrate &s) {
             // Positional read-only row:
             // 0 AssemblyID (native uint64), 1 micro-kappa member IDs,
             // 2 directed temporal micro-kappa pairs, 3 support,
             // 4/5 first/last neural time, 6 consolidated flag.
             py::list out;
             for (auto const &a : s.assemblies()) {
               py::list edges;
               for (auto const &e : a.temporal_edges)
                 edges.append(py::make_tuple(e[0], e[1]));
               out.append(py::make_tuple(a.id, a.members, edges, a.support,
                                         a.first_seen, a.last_seen,
                                         a.consolidated));
             }
             return out;
           })
      .def("recent_assembly_matches",
           [](const NeurodynamicSubstrate &s) {
             py::list out;
             for (auto const &v : s.recent_assembly_matches())
               out.append(py::make_tuple(v.assembly_id, v.confidence,
                                         v.completeness, v.temporal_match,
                                         v.matched_members, v.time));
             return out;
           })
      .def(
          "assembly_bridge_events_after",
          [](const NeurodynamicSubstrate &s, std::uint64_t cursor,
             std::size_t limit) {
            // Positional bridge event (native ownership): sequence, AssemblyID,
            // neural time, confidence, kind, recognition episode, contribution.
            py::list out;
            for (auto const &event :
                 s.assembly_bridge_events_after(cursor, limit))
              out.append(py::make_tuple(event.sequence, event.assembly_id,
                                        event.time, event.confidence,
                                        (std::uint8_t)event.kind,
                                        event.recognition_episode_id,
                                        event.contribution));
            return out;
          },
          py::arg("cursor"), py::arg("limit") = 64)
      .def("telemetry",
           [](const NeurodynamicSubstrate &s) {
             auto t = s.telemetry();
             auto rows = s.assemblies();
             std::uint64_t candidates{}, consolidated{};
             for (auto const &a : rows) {
               if (a.consolidated)
                 ++consolidated;
               else
                 ++candidates;
             }
             return py::make_tuple(
                 s.micro_kappa_count(), s.micro_rho_count(), s.pending_events(),
                 t.total_events_processed, t.total_spikes,
                 t.refractory_discards, t.max_queue_depth,
                 t.last_advance_events_processed, t.plasticity_updates,
                 t.potentiation_updates, t.depression_updates,
                 t.total_abs_weight_change, t.homeostatic_updates,
                 t.max_observed_homeostatic_bias, t.assembly_candidates_created,
                 t.assemblies_consolidated, t.assembly_matches,
                 t.assembly_evidence_updates, candidates, consolidated,
                 t.max_recent_activity_size, t.assembly_prunes);
           })
      .def("snapshot",
           [](const NeurodynamicSubstrate &s) {
             auto x = s.snapshot();
             py::dict d;
             d["tau_membrane"] = x.tau_membrane;
             d["tau_adaptation"] = x.tau_adaptation;
             d["refractory_period"] = x.refractory_period;
             d["reset_potential"] = x.reset_potential;
             d["adaptation_increment"] = x.adaptation_increment;
             d["tau_pre"] = x.tau_pre;
             d["tau_post"] = x.tau_post;
             d["a_plus"] = x.a_plus;
             d["a_minus"] = x.a_minus;
             d["weight_min"] = x.weight_min;
             d["weight_max"] = x.weight_max;
             d["tau_homeostasis"] = x.tau_homeostasis;
             d["homeostasis_spike_increment"] = x.homeostasis_spike_increment;
             d["event_guard"] = x.event_guard;
             d["now"] = x.now;
             d["next_sequence"] = x.next_sequence;
             d["potential"] = x.potential;
             d["base_threshold"] = x.base_threshold;
             d["last_update"] = x.last_update;
             d["refractory_until"] = x.refractory_until;
             d["adaptation"] = x.adaptation;
             d["last_spike"] = x.last_spike;
             d["pre_trace"] = x.pre_trace;
             d["post_trace"] = x.post_trace;
             d["trace_last_update"] = x.trace_last_update;
             d["homeostatic_threshold_bias"] = x.homeostatic_threshold_bias;
             d["homeostasis_last_update"] = x.homeostasis_last_update;
             d["spike_count"] = x.spike_count;
             d["source"] = x.source;
             d["target"] = x.target;
             d["weight"] = x.weight;
             d["delay"] = x.delay;
             d["polarity"] = x.polarity;
             d["plasticity_enabled"] = x.plasticity_enabled;
             py::list pending;
             for (auto &e : x.pending)
               pending.append(
                   py::make_tuple(e.time, e.sequence, e.target, e.amplitude));
             d["pending"] = pending;
             d["telemetry"] = py::make_tuple(
                 x.telemetry.total_events_processed, x.telemetry.total_spikes,
                 x.telemetry.refractory_discards, x.telemetry.max_queue_depth,
                 x.telemetry.last_advance_events_processed,
                 x.telemetry.plasticity_updates,
                 x.telemetry.potentiation_updates,
                 x.telemetry.depression_updates,
                 x.telemetry.total_abs_weight_change,
                 x.telemetry.homeostatic_updates,
                 x.telemetry.max_observed_homeostatic_bias,
                 x.telemetry.assembly_candidates_created,
                 x.telemetry.assemblies_consolidated,
                 x.telemetry.assembly_matches,
                 x.telemetry.assembly_evidence_updates,
                 x.telemetry.max_recent_activity_size,
                 x.telemetry.assembly_prunes);
             d["assembly_config"] = py::make_tuple(
                 x.assembly_tracking_enabled, x.assembly_window,
                 x.assembly_decay_tau, x.assembly_member_ratio_threshold,
                 x.assembly_candidate_similarity_threshold,
                 x.assembly_temporal_similarity_threshold,
                 x.assembly_min_support, x.assembly_min_members,
                 x.assembly_max_members, x.assembly_consolidation_support,
                 x.max_assembly_candidates, x.max_consolidated_assemblies,
                 x.max_temporal_edges, x.max_recent_spikes, x.next_assembly_id);
             py::list recent;
             for (auto &e : x.recent_spikes)
               recent.append(py::make_tuple(e.time, e.target));
             d["recent_spikes"] = recent;
             py::list records;
             for (auto &a : x.assemblies)
               records.append(py::make_tuple(
                   a.id, a.members, a.temporal_edges, a.member_support,
                   a.temporal_support, a.support, a.decayed_support,
                   a.first_seen, a.last_seen, a.candidate, a.consolidated));
             d["assembly_records"] = records;
             py::list matches;
             for (auto &v : x.recent_matches)
               matches.append(py::make_tuple(v.assembly_id, v.confidence,
                                             v.completeness, v.temporal_match,
                                             v.time, v.matched_members));
             d["assembly_matches"] = matches;
             d["node_activity_support"] = x.node_activity_support;
             d["next_bridge_sequence"] = x.next_bridge_sequence;
             py::list bridge_events;
             for (auto const &event : x.bridge_events)
               bridge_events.append(
                   py::make_tuple(event.sequence, event.assembly_id, event.time,
                                  event.confidence, (std::uint8_t)event.kind,
                                  event.recognition_episode_id,event.contribution));
             d["assembly_bridge_events"] = bridge_events;
             d["next_recognition_episode_id"]=x.next_recognition_episode_id;
             py::list episodes;for(auto const&episode:x.recognition_episodes)episodes.append(py::make_tuple(episode.assembly_id,episode.episode_id,episode.last_time,episode.peak_confidence));d["recognition_episodes"]=episodes;
             return d;
           })
      .def("restore", [](NeurodynamicSubstrate &s, py::dict d) {
        NeuroSnapshot x;
        x.tau_membrane = d["tau_membrane"].cast<double>();
        x.tau_adaptation = d["tau_adaptation"].cast<double>();
        x.refractory_period = d["refractory_period"].cast<double>();
        x.reset_potential = d["reset_potential"].cast<double>();
        x.adaptation_increment = d["adaptation_increment"].cast<double>();
        x.tau_pre = d["tau_pre"].cast<double>();
        x.tau_post = d["tau_post"].cast<double>();
        x.a_plus = d["a_plus"].cast<double>();
        x.a_minus = d["a_minus"].cast<double>();
        x.weight_min = d["weight_min"].cast<double>();
        x.weight_max = d["weight_max"].cast<double>();
        x.tau_homeostasis = d["tau_homeostasis"].cast<double>();
        x.homeostasis_spike_increment =
            d["homeostasis_spike_increment"].cast<double>();
        x.event_guard = d["event_guard"].cast<std::uint64_t>();
        x.now = d["now"].cast<double>();
        x.next_sequence = d["next_sequence"].cast<std::uint64_t>();
        x.potential = d["potential"].cast<std::vector<double>>();
        x.base_threshold = d["base_threshold"].cast<std::vector<double>>();
        x.last_update = d["last_update"].cast<std::vector<double>>();
        x.refractory_until = d["refractory_until"].cast<std::vector<double>>();
        x.adaptation = d["adaptation"].cast<std::vector<double>>();
        x.last_spike = d["last_spike"].cast<std::vector<double>>();
        x.pre_trace = d["pre_trace"].cast<std::vector<double>>();
        x.post_trace = d["post_trace"].cast<std::vector<double>>();
        x.trace_last_update =
            d["trace_last_update"].cast<std::vector<double>>();
        x.homeostatic_threshold_bias =
            d["homeostatic_threshold_bias"].cast<std::vector<double>>();
        x.homeostasis_last_update =
            d["homeostasis_last_update"].cast<std::vector<double>>();
        x.spike_count = d["spike_count"].cast<std::vector<std::uint64_t>>();
        x.source = d["source"].cast<std::vector<std::uint32_t>>();
        x.target = d["target"].cast<std::vector<std::uint32_t>>();
        x.weight = d["weight"].cast<std::vector<double>>();
        x.delay = d["delay"].cast<std::vector<double>>();
        x.polarity = d["polarity"].cast<std::vector<std::uint8_t>>();
        x.plasticity_enabled =
            d["plasticity_enabled"].cast<std::vector<std::uint8_t>>();
        for (auto raw : d["pending"].cast<py::list>()) {
          auto t = raw.cast<py::tuple>();
          x.pending.push_back({t[0].cast<double>(), t[1].cast<std::uint64_t>(),
                               t[2].cast<std::uint32_t>(),
                               t[3].cast<double>()});
        }
        auto z = d["telemetry"].cast<py::tuple>();
        x.telemetry.total_events_processed = z[0].cast<std::uint64_t>();
        x.telemetry.total_spikes = z[1].cast<std::uint64_t>();
        x.telemetry.refractory_discards = z[2].cast<std::uint64_t>();
        x.telemetry.max_queue_depth = z[3].cast<std::uint64_t>();
        x.telemetry.last_advance_events_processed = z[4].cast<std::uint64_t>();
        x.telemetry.plasticity_updates = z[5].cast<std::uint64_t>();
        x.telemetry.potentiation_updates = z[6].cast<std::uint64_t>();
        x.telemetry.depression_updates = z[7].cast<std::uint64_t>();
        x.telemetry.total_abs_weight_change = z[8].cast<double>();
        x.telemetry.homeostatic_updates = z[9].cast<std::uint64_t>();
        x.telemetry.max_observed_homeostatic_bias = z[10].cast<double>();
        if (z.size() > 11) {
          x.telemetry.assembly_candidates_created = z[11].cast<std::uint64_t>();
          x.telemetry.assemblies_consolidated = z[12].cast<std::uint64_t>();
          x.telemetry.assembly_matches = z[13].cast<std::uint64_t>();
          x.telemetry.assembly_evidence_updates = z[14].cast<std::uint64_t>();
          x.telemetry.max_recent_activity_size = z[15].cast<std::uint64_t>();
          x.telemetry.assembly_prunes = z[16].cast<std::uint64_t>();
        }
        if (d.contains("assembly_config")) {
          auto c = d["assembly_config"].cast<py::tuple>();
          x.assembly_tracking_enabled = c[0].cast<bool>();
          x.assembly_window = c[1].cast<double>();
          x.assembly_decay_tau = c[2].cast<double>();
          x.assembly_member_ratio_threshold = c[3].cast<double>();
          x.assembly_candidate_similarity_threshold = c[4].cast<double>();
          x.assembly_temporal_similarity_threshold = c[5].cast<double>();
          x.assembly_min_support = c[6].cast<std::uint32_t>();
          x.assembly_min_members = c[7].cast<std::uint32_t>();
          x.assembly_max_members = c[8].cast<std::uint32_t>();
          x.assembly_consolidation_support = c[9].cast<std::uint32_t>();
          x.max_assembly_candidates = c[10].cast<std::uint32_t>();
          x.max_consolidated_assemblies = c[11].cast<std::uint32_t>();
          x.max_temporal_edges = c[12].cast<std::uint32_t>();
          x.max_recent_spikes = c[13].cast<std::uint32_t>();
          x.next_assembly_id = c[14].cast<std::uint64_t>();
          for (auto raw : d["recent_spikes"].cast<py::list>()) {
            auto t = raw.cast<py::tuple>();
            x.recent_spikes.push_back(
                {t[0].cast<double>(), 0, t[1].cast<std::uint32_t>(), 0.});
          }
          for (auto raw : d["assembly_records"].cast<py::list>()) {
            auto t = raw.cast<py::tuple>();
            AssemblyRecord a;
            a.id = t[0].cast<std::uint64_t>();
            a.members = t[1].cast<std::vector<std::uint32_t>>();
            a.temporal_edges =
                t[2].cast<std::vector<std::array<std::uint32_t, 2>>>();
            a.member_support = t[3].cast<std::vector<std::array<double, 2>>>();
            a.temporal_support =
                t[4].cast<std::vector<std::array<double, 3>>>();
            a.support = t[5].cast<std::uint32_t>();
            a.decayed_support = t[6].cast<double>();
            a.first_seen = t[7].cast<double>();
            a.last_seen = t[8].cast<double>();
            a.candidate = t[9].cast<bool>();
            a.consolidated = t[10].cast<bool>();
            x.assemblies.push_back(std::move(a));
          }
          for (auto raw : d["assembly_matches"].cast<py::list>()) {
            auto t = raw.cast<py::tuple>();
            x.recent_matches.push_back(
                {t[0].cast<std::uint64_t>(), t[1].cast<double>(),
                 t[2].cast<double>(), t[3].cast<double>(), t[4].cast<double>(),
                 t[5].cast<std::vector<std::uint32_t>>()});
          }
          x.node_activity_support =
              d["node_activity_support"].cast<std::vector<std::uint64_t>>();
          if (d.contains("next_bridge_sequence")) {
            x.next_bridge_sequence =
                d["next_bridge_sequence"].cast<std::uint64_t>();
            for (auto raw : d["assembly_bridge_events"].cast<py::list>()) {
              auto t = raw.cast<py::tuple>();
              AssemblyBridgeEvent event;event.sequence=t[0].cast<std::uint64_t>();event.assembly_id=t[1].cast<std::uint64_t>();event.time=t[2].cast<double>();event.confidence=t[3].cast<double>();event.kind=(AssemblyBridgeEventKind)t[4].cast<std::uint8_t>();if(t.size()>5){event.recognition_episode_id=t[5].cast<std::uint64_t>();event.contribution=t[6].cast<double>();}x.bridge_events.push_back(event);
            }
            if(d.contains("next_recognition_episode_id")){x.next_recognition_episode_id=d["next_recognition_episode_id"].cast<std::uint64_t>();for(auto raw:d["recognition_episodes"].cast<py::list>()){auto t=raw.cast<py::tuple>();x.recognition_episodes.push_back({t[0].cast<std::uint64_t>(),t[1].cast<std::uint64_t>(),t[2].cast<double>(),t[3].cast<double>()});}}
          }
        } else {
          x.assembly_window = 5.;
          x.assembly_decay_tau = 1000.;
          x.assembly_member_ratio_threshold = .6;
          x.assembly_candidate_similarity_threshold = .6;
          x.assembly_temporal_similarity_threshold = .5;
          x.assembly_min_support = 2;
          x.assembly_min_members = 3;
          x.assembly_max_members = 8;
          x.assembly_consolidation_support = 3;
          x.max_assembly_candidates = 64;
          x.max_consolidated_assemblies = 64;
          x.max_temporal_edges = 64;
          x.max_recent_spikes = 64;
          x.node_activity_support.assign(x.potential.size(), 0);
        }
        s.restore(x);
      });
#ifdef SE_WITH_OBSERVER
  py::class_<NativeObserver>(m, "NativeObserver")
      .def("start", &NativeObserver::start)
      .def("stop",
           [](NativeObserver &o) {
             py::gil_scoped_release release;
             o.stop();
           })
      .def_property_readonly("is_running", &NativeObserver::is_running)
      .def_property_readonly("frames_rendered", &NativeObserver::frames_rendered)
      .def_property_readonly("brain_snapshot_rebuilds", &NativeObserver::brain_snapshot_rebuilds)
      .def_property_readonly("last_snapshot_event_sequence", &NativeObserver::last_snapshot_event_sequence)
      .def("latest_snapshot",
           [](const NativeObserver &o) {
             auto s = o.latest_snapshot();
             py::list bodies, objects, held;
             for (auto const &b : s.bodies) bodies.append(py::make_tuple(b.id, b.x, b.y, std::string(1, b.orientation), b.appearance, b.held_object_id));
             for (auto const &v : s.objects) objects.append(py::make_tuple(v.id, v.x, v.y, v.state));
             for (auto const &h : s.held_objects) held.append(py::make_tuple(h.owner_body_id, h.object_id, h.state));
             return py::make_tuple(s.world_time, s.event_sequence, s.world_width, s.world_height, bodies, objects, held);
           })
      .def("latest_dialogue_snapshot", [](const NativeObserver &o) {
        auto s = o.latest_dialogue_snapshot();
        py::list lines;
        for (auto const &line : s.lines) lines.append(py::make_tuple(line.sequence, line.world_time, (int)line.role, line.text));
        return py::make_tuple(s.revision, lines);
      });
#endif
  py::class_<World>(m,"WorldRuntime").def(py::init<int,int,int>(),py::arg("width")=30,py::arg("height")=30,py::arg("radius")=4)
    .def("initialize",[](World&w,int x,int y,const std::string&o,const std::vector<std::pair<int,int>>&objects){w.initialize({x,y,o.empty()?'N':o[0]},objects);})
    .def("initialize_multi",[](World&w,const std::vector<std::tuple<std::uint32_t,int,int,std::string,std::uint16_t>>&bodies,const std::vector<std::tuple<std::uint32_t,int,int,int>>&objects){std::vector<Body>bs;std::vector<Object>os;for(auto&[id,x,y,o,appearance]:bodies)bs.push_back({x,y,o.empty()?'N':o[0],0,appearance,id});for(auto&[id,x,y,state]:objects)os.push_back({id,x,y,state});w.initialize_multi(std::move(bs),std::move(os));})
    .def("restore",[](World&w,const std::vector<std::tuple<std::uint32_t,int,int,std::string,std::uint16_t>>&bodies,const std::vector<std::tuple<std::uint32_t,int,int,int>>&objects,const std::vector<std::tuple<std::uint32_t,std::uint32_t,int,int,int>>&held,const std::vector<double>&resistance,std::uint64_t tick,std::optional<std::uint64_t>next,std::uint32_t next_id,std::uint32_t cursor,std::uint64_t conflicts,const std::vector<std::uint64_t>&wins,double time,std::uint64_t sequence,std::uint32_t max_objects){std::vector<Body>bs;std::vector<Object>os;std::vector<std::pair<std::uint32_t,Object>>hs;for(auto&[id,x,y,o,appearance]:bodies)bs.push_back({x,y,o.empty()?'N':o[0],0,appearance,id});for(auto&[id,x,y,state]:objects)os.push_back({id,x,y,state});for(auto&[body,id,x,y,state]:held)hs.push_back({body,{id,x,y,state}});w.restore(std::move(bs),std::move(os),std::move(hs),resistance,tick,next,next_id,cursor,conflicts,wins,time,sequence,max_objects);})
    .def("set_body_state",[](World&w,std::uint32_t id,int x,int y,const std::string&o){w.set_body_state(id,x,y,o.empty()?'N':o[0]);})
    .def("configure_spawning",&World::configure_spawning).def("world_tick",[](World&w,py::object position,py::object next){std::optional<std::pair<int,int>>p;if(!position.is_none())p=position.cast<std::pair<int,int>>();std::optional<std::uint64_t>n;if(!next.is_none())n=next.cast<std::uint64_t>();return w.world_tick(p,n);})
    .def("apply_spawn_event",[](World&w,py::object position,double time,std::uint64_t event){std::optional<std::pair<int,int>>p;if(!position.is_none())p=position.cast<std::pair<int,int>>();auto result=w.apply_spawn_event(p,time,event);return result?py::cast(*result):py::none();})
    .def("apply",[](World&w,int action,std::uint32_t body_id){return (int)w.apply((ActionType)action,body_id);},py::arg("action"),py::arg("body_id")=0)
    .def("resolve_intents",[](World&w,const std::vector<std::uint32_t>&ids,const std::vector<std::uint8_t>&actions){auto rows=w.resolve_intents(ids,actions);std::vector<int>out;for(auto value:rows)out.push_back((int)value);return out;})
    .def("apply_intent",[](World&w,int action,double issued,std::uint64_t event){return (int)w.apply_intent((ActionType)action,issued,event);})
    .def("advance_world_time",&World::advance_world_time).def("time_state",[](const World&w){return py::make_tuple(w.world_time(),w.event_sequence());})
#ifdef SE_WITH_OBSERVER
    .def("create_observer",[](World&w){return std::make_unique<NativeObserver>(w.snapshot_channel());})
    .def("create_brain_observer",[](World&w,NativeBrainEngine&e){return std::make_unique<NativeObserver>(w.snapshot_channel(),e.brain_snapshot_channel(),e.dialogue_snapshot_channel());},py::keep_alive<0,1>(),py::keep_alive<0,2>())
#endif
    .def("latest_render_snapshot",[](const World&w){auto s=w.latest_render_snapshot();py::list bodies,objects,held;for(auto const&b:s.bodies)bodies.append(py::make_tuple(b.id,b.x,b.y,std::string(1,b.orientation),b.appearance,b.held_object_id));for(auto const&o:s.objects)objects.append(py::make_tuple(o.id,o.x,o.y,o.state));for(auto const&h:s.held_objects)held.append(py::make_tuple(h.owner_body_id,h.object_id,h.state));return py::make_tuple(s.world_time,s.event_sequence,s.world_width,s.world_height,bodies,objects,held);})
    .def("state",[](const World&w){py::list objects;for(auto&o:w.objects())objects.append(py::make_tuple(o.id,o.x,o.y,o.state));auto&b=w.body();return py::make_tuple(b.x,b.y,std::string(1,b.orientation),b.held_object_id,objects,w.resistance());})
    .def("full_state",[](const World&w){py::list bodies,objects,held;for(auto&b:w.bodies())bodies.append(py::make_tuple(b.id,b.x,b.y,std::string(1,b.orientation),b.held_object_id,b.appearance));auto sorted=w.objects();std::sort(sorted.begin(),sorted.end(),[](auto&a,auto&b){return a.id<b.id;});for(auto&o:sorted)objects.append(py::make_tuple(o.id,o.x,o.y,o.state));for(std::size_t i=0;i<w.held_objects().size();++i)if(w.held_objects()[i]){auto&o=*w.held_objects()[i];held.append(py::make_tuple((std::uint32_t)i,o.id,o.x,o.y,o.state));}return py::make_tuple(bodies,objects,held,w.world_tick_count(),w.next_spawn_tick(),w.next_object_id(),w.conflict_cursor(),w.conflict_count(),w.fairness_wins());})
    .def("resistances",&World::resistances)
    .def("perceive",[](const World&w,std::uint64_t tick,std::uint32_t body_id){auto f=w.perceive(tick,body_id);py::list cells;for(auto&c:f.cells)cells.append(py::make_tuple(c.dx,c.dy,c.occupied,c.state,c.boundary,c.self,c.appearance));return py::make_tuple(cells,py::make_tuple(f.body.up,f.body.down,f.body.left,f.body.right,f.body.holding,f.body.resistance));},py::arg("tick"),py::arg("body_id")=0);
  py::class_<EvidenceConfig>(m, "EvidenceConfig").def(py::init<>()).def_readwrite("minimum_support", &EvidenceConfig::minimum_support).def_readwrite("minimum_lift", &EvidenceConfig::minimum_lift).def_readwrite("confidence_k", &EvidenceConfig::confidence_k).def_readwrite("consolidated_support", &EvidenceConfig::consolidated_support).def_readwrite("consolidated_confidence", &EvidenceConfig::consolidated_confidence);
  py::class_<NativeBrainEngine>(m, "NativeBrainEngine")
      .def(py::init<std::size_t>(), py::arg("evidence_window") = 512)
      .def("add_cognit", &NativeBrainEngine::add_cognit,
           py::arg("activity") = 0, py::arg("threshold") = .25,
           py::arg("confidence") = .5)
      .def("add_cognits", &NativeBrainEngine::add_cognits, py::arg("count"),
           py::arg("activity") = 0, py::arg("threshold") = .25,
           py::arg("confidence") = .5)
      .def("set_activity", &NativeBrainEngine::set_activity)
      .def("transition_history", &NativeBrainEngine::transition_history)
      .def("restore_transition_history",
           &NativeBrainEngine::restore_transition_history)
      .def("homeostasis_runtime_state",
           &NativeBrainEngine::homeostasis_runtime_state)
      .def("restore_homeostasis_runtime_state",
           &NativeBrainEngine::restore_homeostasis_runtime_state)
      .def("dirty_relation_state", &NativeBrainEngine::dirty_relation_state)
      .def("restore_dirty_relation_state",
           &NativeBrainEngine::restore_dirty_relation_state)
      .def("remove_cognit", &NativeBrainEngine::remove_cognit)
      .def("cognit_alive", &NativeBrainEngine::cognit_alive)
      .def_property_readonly("state_revision",
                             &NativeBrainEngine::state_revision)
      .def_property_readonly("live_cognit_count",
                             &NativeBrainEngine::live_cognit_count)
      .def("set_refractory", &NativeBrainEngine::set_refractory)
      .def("receive", &NativeBrainEngine::receive)
      .def("receive_batch",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids,
              const std::vector<double> &energies, std::uint64_t tick,
              bool wave_step, double attenuation,
              std::uint16_t refractory_steps) {
             py::gil_scoped_release release;
             return e.receive_batch(ids, energies, tick, wave_step, attenuation,
                                    refractory_steps);
           })
      .def(
          "add_relation",
          [](NativeBrainEngine &e, std::uint32_t s, std::uint32_t t, int type,
             std::uint32_t action, double strength, double confidence,
             double probability) {
            auto h = e.add_relation(s, t, (RelationType)type, action, strength,
                                    confidence, probability);
            return py::make_tuple(h.page, h.slot, h.generation);
          },
          py::arg("source"), py::arg("target"), py::arg("relation_type"),
          py::arg("action") = 0, py::arg("strength") = .2,
          py::arg("confidence") = .3, py::arg("probability") = 0.)
      .def("set_relation_capacity",&NativeBrainEngine::set_relation_capacity)
      .def_property_readonly("relation_capacity",&NativeBrainEngine::relation_capacity)
      .def("upsert_relation_states_batch",
           [](NativeBrainEngine &e, std::uint32_t source,
              const std::vector<
                  std::tuple<std::uint32_t, std::uint8_t, std::uint32_t, double,
                             double, double, std::uint32_t, double>> &values,
              std::uint32_t max_new, std::uint32_t max_total) {
             std::vector<PersistedRelation> rows;
             rows.reserve(values.size());
             for (auto const &v : values) {
               PersistedRelation r;
               r.target = std::get<0>(v) - 1;
               r.type = std::get<1>(v);
               r.action = std::get<2>(v);
               r.strength = std::get<3>(v);
               r.confidence = std::get<4>(v);
               r.prediction = std::get<5>(v);
               r.support = std::get<6>(v);
               r.lift = std::get<7>(v);
               rows.push_back(r);
             }
             py::gil_scoped_release release;
             return e.upsert_relation_states_batch(source, rows, max_new,
                                                   max_total);
           })
      .def(
          "remove_relation",
          [](NativeBrainEngine &e,
             const std::tuple<std::uint32_t, std::uint32_t, std::uint32_t> &h) {
            return e.remove_relation(
                {std::get<0>(h), std::get<1>(h), std::get<2>(h)});
          })
      .def(
          "relation_handle_valid",
          [](NativeBrainEngine &e,
             const std::tuple<std::uint32_t, std::uint32_t, std::uint32_t> &h) {
            return e.relation_handle_valid(
                {std::get<0>(h), std::get<1>(h), std::get<2>(h)});
          })
      .def("outgoing",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &sources) {
             auto rows = e.outgoing(sources);
             py::list out;
             for (auto &[h, r] : rows)
               out.append(py::make_tuple(
                   r.source, r.target, r.type, r.action, r.strength,
                   r.confidence, r.prediction, r.support, r.lift,
                   r.last_evidence_world_tick, r.status, r.contradiction,
                   r.usefulness, r.confirmations, r.last_used_cognitive_tick,
                   py::make_tuple(h.page, h.slot, h.generation)));
             return out;
           })
      .def("outgoing_targets",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &sources) {
             py::gil_scoped_release release;
             return e.outgoing_targets(sources);
           })
      .def("relation_state",
           [](NativeBrainEngine &e, std::uint32_t source,
              const std::tuple<std::uint32_t, std::uint32_t, std::uint32_t>
                  &raw) {
             RelationHandle h{std::get<0>(raw), std::get<1>(raw),
                              std::get<2>(raw)};
             auto r = e.relation_state(source, h);
             return py::make_tuple(
                 r.source, r.target, r.type, r.action, r.strength, r.confidence,
                 r.prediction, r.support, r.lift, r.last_evidence_world_tick,
                 r.status, r.contradiction, r.usefulness, r.confirmations,
                 r.last_used_cognitive_tick, raw);
           })
      .def("update_relation",
           [](NativeBrainEngine &e,
              const std::tuple<std::uint32_t, std::uint32_t, std::uint32_t> &h,
              const std::tuple<double, double, double, std::uint32_t, double,
                               std::uint64_t, std::uint8_t, double, double,
                               std::uint32_t, std::uint64_t> &v) {
             PersistedRelation r;
             r.strength = std::get<0>(v);
             r.confidence = std::get<1>(v);
             r.prediction = std::get<2>(v);
             r.support = std::get<3>(v);
             r.lift = std::get<4>(v);
             r.last_evidence_world_tick = std::get<5>(v);
             r.status = std::get<6>(v);
             r.contradiction = std::get<7>(v);
             r.usefulness = std::get<8>(v);
             r.confirmations = std::get<9>(v);
             r.last_used_cognitive_tick = std::get<10>(v);
             e.update_relation({std::get<0>(h), std::get<1>(h), std::get<2>(h)},
                               r);
           })
      .def("predict",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              int action) {
             py::gil_scoped_release release;
             return e.predict(active, (std::uint8_t)action);
           })
      .def("predict_compact",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              int action) {
             std::vector<std::pair<std::uint32_t, double>> rows;
             {
               py::gil_scoped_release release;
               rows = e.predict(active, (std::uint8_t)action);
             }
             py::array_t<std::uint32_t> ids(rows.size());
             py::array_t<double> values(rows.size());
             auto *i = ids.mutable_data();
             auto *v = values.mutable_data();
             for (std::size_t n = 0; n < rows.size(); ++n) {
               i[n] = rows[n].first;
               v[n] = rows[n].second;
             }
             return py::make_tuple(std::move(ids), std::move(values));
           })
      .def("predict_actions_batch",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              const std::vector<std::uint8_t> &actions) {
             py::gil_scoped_release release;
             return e.predict_actions_batch(active, actions);
           })
      .def("predict_actions_batch_at",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              const std::vector<std::uint8_t> &actions, std::uint64_t tick,
              double decay) {
             py::gil_scoped_release release;
             return e.predict_actions_batch_at(active, actions, tick, decay);
           })
      .def("action_effects",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              int action, double floor) {
             py::gil_scoped_release release;
             return e.action_effects(active, (std::uint8_t)action, floor);
           })
      .def("action_effects_batch",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              const std::vector<std::uint8_t> &actions, double floor) {
             py::gil_scoped_release release;
             return e.action_effects_batch(active, actions, floor);
           })
      .def("planner_transition_batch",
           [](NativeBrainEngine &e,
              const std::vector<std::vector<std::uint32_t>> &states,
              const std::vector<std::uint8_t> &actions, std::uint64_t tick,
              double decay, double floor) {
             std::vector<PlannerTransition> rows;
             {
               py::gil_scoped_release release;
               rows = e.planner_transition_batch(states, actions, tick, decay,
                                                 floor);
             }
             py::list out;
             for (auto &row : rows)
               out.append(py::make_tuple(row.predictions, row.effects));
             return out;
           })
      .def("propagate",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &seeds,
              std::uint64_t tick) {
             py::gil_scoped_release release;
             auto r = e.propagate(seeds, tick);
             return std::make_tuple(r.active, r.energy, r.steps,
                                    r.transmitted_energy);
           })
      .def("publish_brain_snapshot",
           [](NativeBrainEngine &e, double time, std::uint64_t tick,
              std::uint64_t generation,
              const std::vector<std::uint32_t> &active) {
             py::gil_scoped_release release;
             e.publish_brain_snapshot(time, tick, generation, active);
           })
      .def("publish_dialogue_line",
           [](NativeBrainEngine &e, double time, int role,
              const std::string &value) {
             e.publish_dialogue(time, (DialogueRole)role, value);
           })
      .def("dialogue_snapshot",
           [](NativeBrainEngine &e) {
             auto s = e.dialogue_snapshot_channel()->latest();
             py::list lines;
             if (!s)
               return py::make_tuple(std::uint64_t(0), lines);
             for (auto const &line : s->lines)
               lines.append(py::make_tuple(line.sequence, line.world_time,
                                           (int)line.role, line.text));
             return py::make_tuple(std::uint64_t(s->revision), lines);
           })
      .def("latest_brain_snapshot",
           [](NativeBrainEngine &e) -> py::object {
             auto p = e.brain_snapshot_channel()->latest();
             if (!p)
               return py::none();
             py::list nodes, edges;
             for (auto const &n : p->nodes)
               nodes.append(py::make_tuple(n.id, n.activity, n.threshold,
                                           n.confidence, n.composite, n.alive,
                                           n.last_active_cognitive_tick));
             for (auto const &r : p->edges)
               edges.append(py::make_tuple(r.source, r.target, r.relation_type,
                                           r.strength, r.confidence,
                                           r.activation));
             return py::make_tuple(p->world_time, p->cognitive_tick,
                                   p->cognition_generation, nodes, edges,
                                   p->total_cognits, p->total_relations,
                                   p->active_cognits, p->truncated);
           })
      .def("cognit_state",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids) {
             return e.cognit_state(ids);
           })
      .def("cognit_state_full",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids) {
             return e.cognit_state_full(ids);
           })
      .def("cognit_state_masked",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids,
              std::uint16_t mask) { return e.cognit_state_masked(ids, mask); })
      .def("set_cognit_states",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids,
              const std::vector<double> &values) {
             e.set_cognit_states(ids, values);
           })
      .def("set_cognit_fields",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids,
              const std::vector<std::uint8_t> &fields,
              const std::vector<double> &values) {
             e.set_cognit_fields(ids, fields, values);
           })
      .def("homeostatic_step",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &active,
              double trace_decay, double learning_rate, double threshold_min,
              double threshold_max, double activity_decay,
              double utility_decay) {
             py::gil_scoped_release release;
             e.homeostatic_step(active, trace_decay, learning_rate,
                                threshold_min, threshold_max, activity_decay,
                                utility_decay);
           })
      .def("begin_continuous_time", &NativeBrainEngine::begin_continuous_time)
      .def("materialize_cognits_at",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids,
              double now) {
             py::gil_scoped_release release;
             e.materialize_cognits_at(ids, now);
           })
      .def("cognit_elapsed_times",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &ids) {
             return e.cognit_elapsed_times(ids);
           })
      .def("continuous_time_state", &NativeBrainEngine::continuous_time_state)
      .def("restore_continuous_time_state",
           &NativeBrainEngine::restore_continuous_time_state,
           py::arg("enabled"), py::arg("epoch"), py::arg("now"),
           py::arg("last_touch"), py::arg("last_active"),
           py::arg("latent_threshold"), py::arg("work") = 0)
      .def("continuous_relation_time_state",
           &NativeBrainEngine::continuous_relation_time_state)
      .def("restore_continuous_relation_time_state",
           &NativeBrainEngine::restore_continuous_relation_time_state,
           py::arg("rows"), py::arg("work") = 0)
      .def("update_transition_evidence",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &before,
              int action, const std::vector<std::uint32_t> &after) {
             py::gil_scoped_release release;
             e.update_transition_evidence(before, (std::uint8_t)action, after);
           })
      .def("materialize_relations",
           [](NativeBrainEngine &e, const EvidenceConfig &c,
              std::uint64_t tick) {
             py::gil_scoped_release release;
             auto rows = e.materialize_relations(c, tick);
             std::vector<std::tuple<std::uint32_t, std::uint32_t, std::uint8_t,
                                    std::uint32_t, double, double, double>>
                 out;
             for (auto &r : rows)
               out.emplace_back(r.source, r.target, r.action, r.support,
                                r.probability, r.confidence, r.lift);
             return out;
           })
      .def("materialize_current",
           [](NativeBrainEngine &e, const EvidenceConfig &c, std::uint64_t tick,
              const std::vector<std::uint32_t> &before, int action,
              const std::vector<std::uint32_t> &after, std::uint32_t max_new,
              std::uint32_t max_relations, double decay) {
             std::vector<MaterializedRelation> rows;
             {
               py::gil_scoped_release release;
               rows =
                   e.materialize_current(c, tick, before, (std::uint8_t)action,
                                         after, max_new, max_relations, decay);
             }
             std::vector<std::tuple<std::uint32_t, std::uint32_t, std::uint8_t,
                                    std::uint32_t, double, double, double>>
                 out;
             for (auto &r : rows)
               out.emplace_back(r.source, r.target, r.action, r.support,
                                r.probability, r.confidence, r.lift);
             return out;
           })
      .def("clear_transition_evidence",
           &NativeBrainEngine::clear_transition_evidence)
      .def("set_evidence_window", &NativeBrainEngine::set_evidence_window)
      .def_property_readonly("evidence_stats",
                             &NativeBrainEngine::evidence_stats)
      .def("transition_metrics", &NativeBrainEngine::transition_metrics)
      .def("action_trials",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &sources,
              const std::vector<std::uint8_t> &actions) {
             return e.action_trials(sources, actions);
           })
      .def("update_outcomes",
           [](NativeBrainEngine &e, const std::vector<std::uint32_t> &before,
              const std::vector<std::uint32_t> &current, int action,
              std::uint64_t tick, double confirmation, double contradiction,
              double utility, double consolidated) {
             py::gil_scoped_release release;
             e.update_outcomes(before, current, action, tick, confirmation,
                               contradiction, utility, consolidated);
           })
      .def("lifecycle_step", &NativeBrainEngine::lifecycle_step)
      .def("neurodynamic_substrate", &NativeBrainEngine::neurodynamic_substrate,
           py::return_value_policy::reference_internal)
      .def(
          "process_assembly_bridge",
          [](NativeBrainEngine &e, std::uint64_t tick, std::size_t limit,std::size_t max_cognits,std::size_t max_births) {
            // Positional result consumed by NativeGraphBackend:
            // 0 event sequence; 1 AssemblyID; 2 native 0-based Cognit index;
            // 3 confidence; 4 kind; 5 born; 6 activated; 7 neural time;
            // 8 recognition episode; 9 contribution; 10 birth suppressed.
            // Это INTERNAL wire ABI: tuple shape не менять как formatting cleanup.
            py::list out;
            for (auto const &row : e.process_assembly_bridge(tick, limit,max_cognits,max_births))
              out.append(py::make_tuple(row.event_sequence, row.assembly_id,
                                        row.cognit_id, row.confidence, row.kind,
                                        row.born, row.activated,row.event_time,
                                        row.recognition_episode_id,row.contribution,row.birth_suppressed));
            return out;
          },
          py::arg("cognitive_tick"), py::arg("max_events") = 64,py::arg("max_cognits")=2048,py::arg("max_births")=4)
      .def("assembly_cognit_mapping",
           &NativeBrainEngine::assembly_cognit_mapping)
      .def("assembly_bridge_state", &NativeBrainEngine::assembly_bridge_state)
      .def("restore_assembly_bridge_state",
           &NativeBrainEngine::restore_assembly_bridge_state)
      .def("save_graph", &NativeBrainEngine::save_graph)
      .def("load_graph", &NativeBrainEngine::load_graph)
      .def_property_readonly("cognit_count", &NativeBrainEngine::cognit_count)
      .def_property_readonly("relation_count",
                             &NativeBrainEngine::relation_count)
      .def_property_readonly("provisional_count",
                             &NativeBrainEngine::provisional_count)
      .def_property_readonly("consolidated_count",
                             &NativeBrainEngine::consolidated_count)
      .def_property_readonly("logical_bytes", &NativeBrainEngine::logical_bytes)
      .def_property_readonly("reserved_bytes",
                             &NativeBrainEngine::reserved_bytes)
      .def_property_readonly_static("provisional_relation_bytes",
                                    [](py::object) {
                                      return NativeBrainEngine::
                                          provisional_relation_bytes();
                                    })
      .def_property_readonly_static(
          "consolidated_relation_bytes", [](py::object) {
            return NativeBrainEngine::consolidated_relation_bytes();
          });
  m.attr("RELATION_ASSOCIATIVE") = (int)RelationType::Associative;
  m.attr("RELATION_SEQUENTIAL") = (int)RelationType::Sequential;
  m.attr("RELATION_SELF_ACTION") = (int)RelationType::SelfAction;
}
