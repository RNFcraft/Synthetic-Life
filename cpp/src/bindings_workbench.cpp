#include "bindings_workbench.hpp"
#include "se/workbench_commands.hpp"
#include "se/workbench_snapshot.hpp"
#include <pybind11/stl.h>
namespace py = pybind11;
using namespace se;
void bind_workbench(py::module_ &m) {
  py::enum_<WorkbenchCommandKind>(m, "WorkbenchCommandKind")
      .value("PLACE_FOOD", WorkbenchCommandKind::PlaceFood)
      .value("PLACE_WATER", WorkbenchCommandKind::PlaceWater)
      .value("PLACE_OBJECT", WorkbenchCommandKind::PlaceObject)
      .value("REMOVE_OBJECT", WorkbenchCommandKind::RemoveObject)
      .value("SEND_DIALOGUE", WorkbenchCommandKind::SendDialogue)
      .value("PAUSE", WorkbenchCommandKind::Pause)
      .value("RESUME", WorkbenchCommandKind::Resume)
      .value("STEP", WorkbenchCommandKind::Step);
  py::class_<WorkbenchCommandChannel, std::shared_ptr<WorkbenchCommandChannel>>(
      m, "WorkbenchCommandChannel")
      .def(py::init<>())
      .def("submit", &WorkbenchCommandChannel::submit, py::arg("kind"),
           py::arg("x") = 0, py::arg("y") = 0, py::arg("object_id") = 0,
           py::arg("text") = "")
      .def("drain",
           [](WorkbenchCommandChannel &c) {
             py::list out;
             for (auto &v : c.drain())
               out.append(
                   py::make_tuple(v.id, v.kind, v.x, v.y, v.object_id, v.text));
             return out;
           })
      .def("close", &WorkbenchCommandChannel::close);
  py::class_<WorkbenchStatusChannel, std::shared_ptr<WorkbenchStatusChannel>>(
      m, "WorkbenchStatusChannel")
      .def(py::init<>())
      .def("publish", [](WorkbenchStatusChannel &c, const py::dict &d) {
        WorkbenchStatusSnapshot s;
#define FIELD(name)                                                            \
  if (d.contains(#name))                                                       \
    s.name = d[#name].cast<decltype(s.name)>();
        FIELD(world_time)
        FIELD(event_sequence) FIELD(paused) FIELD(actions_completed) FIELD(
            pending_events) FIELD(energy) FIELD(energy_max) FIELD(nutrients)
            FIELD(nutrients_max) FIELD(hydration) FIELD(hydration_max) FIELD(
                hunger) FIELD(tension) FIELD(energy_depleted)
                FIELD(interoception_enabled) FIELD(bin_count) FIELD(bins) FIELD(
                    target_bins) FIELD(internal_observed_at) FIELD(cognits)
                    FIELD(relations) FIELD(active_cognits) FIELD(
                        micro_cognits) FIELD(micro_relations) FIELD(assemblies)
                        FIELD(current_action) FIELD(planned_actions) FIELD(
                            has_plan) FIELD(plan_score) FIELD(plan_confidence)
                            FIELD(homeostatic_component)
                                FIELD(prediction_confidence) FIELD(
                                    delayed_prediction_enabled)
                                    FIELD(has_temporal_prediction) FIELD(
                                        passive_depth) FIELD(predicted_delay)
                                        FIELD(ambiguity) FIELD(food_payload)
                                            FIELD(water_payload)
                                                FIELD(last_command_result)
#undef FIELD
                                                    c.publish(std::move(s));
      });
}
