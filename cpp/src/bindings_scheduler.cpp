#include "bindings_scheduler.hpp"
#include "se/event_scheduler.hpp"
#include <pybind11/stl.h>
namespace py = pybind11;
using namespace se;
void bind_scheduler(py::module_ &m) {
  py::class_<RuntimeEvent>(m, "RuntimeEvent").def(py::init([](double t, std::uint64_t id, RuntimeEventType type, std::uint64_t payload) { return RuntimeEvent{t, id, type, payload}; })).def_readonly("time", &RuntimeEvent::time).def_readonly("id", &RuntimeEvent::id).def_readonly("type", &RuntimeEvent::type).def_readonly("payload", &RuntimeEvent::payload);
  py::enum_<RuntimeEventType>(m, "RuntimeEventType").value("WORLD_ACTION_COMPLETE", RuntimeEventType::WorldActionComplete).value("WORLD_SPAWN", RuntimeEventType::WorldSpawn).value("SENSORY_CHANGE", RuntimeEventType::SensoryChange).value("COGNITION_WAKE", RuntimeEventType::CognitionWake).value("COGNITION_CONTINUE", RuntimeEventType::CognitionContinue).value("MEMORY_TIMER", RuntimeEventType::MemoryTimer).value("RELATION_TIMER", RuntimeEventType::RelationTimer).value("MAINTENANCE", RuntimeEventType::Maintenance).value("EXTERNAL_INPUT", RuntimeEventType::ExternalInput).value("LANGUAGE_INPUT", RuntimeEventType::LanguageInput).value("LANGUAGE_CONTINUE", RuntimeEventType::LanguageContinue).value("NEURAL_BRIDGE",RuntimeEventType::NeuralBridge);
  py::class_<EventScheduler>(m, "EventScheduler").def(py::init<>()).def("schedule", &EventScheduler::schedule, py::arg("time"), py::arg("event_type"), py::arg("payload") = 0).def("pop_ready", &EventScheduler::pop_ready).def("snapshot", &EventScheduler::snapshot).def("restore", &EventScheduler::restore,py::arg("now"),py::arg("next_id"),py::arg("events"),py::arg("peak_size")=0).def_property_readonly("now", &EventScheduler::now).def_property_readonly("next_id", &EventScheduler::next_id).def_property_readonly("size", &EventScheduler::size).def_property_readonly("peak_size",&EventScheduler::peak_size);
}
