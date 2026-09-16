"""Small, read-only diagnostics for v0.6.6 endurance validation."""
from dataclasses import asdict,dataclass
import math


@dataclass(frozen=True,slots=True)
class LongLifeSample:
    simulated_time:float;actions_completed:int;scheduler_events_processed:int;scheduler_queue:int;peak_scheduler_queue:int
    cognits_current:int;cognits_peak:int;relations_current:int;relations_peak:int;assemblies_current:int;assemblies_peak:int
    assembly_candidates:int;bridge_log_size:int;bridge_log_peak:int;planner_cycles:int;planner_pending_work:int
    memory_structures:int;percept_tracks:int;composite_candidates:int;deletion_candidates:int;dirty_cognits:int
    neural_event_count:int;full_graph_sync_calls:int
    def to_dict(self):return asdict(self)


class LongLifeDiagnostics:
    def __init__(self):self.cognits_peak=0;self.relations_peak=0;self.assemblies_peak=0;self.bridge_log_peak=0
    def sample(self,runtime):
        core=runtime.simulation.core;engine=core.backend.engine;neural=engine.neurodynamic_substrate();snapshot=neural.snapshot();frontier=core.continuous_frontier;session=frontier.session if frontier else None
        self.cognits_peak=max(self.cognits_peak,len(core.graph.nodes));self.relations_peak=max(self.relations_peak,core.graph.relation_count);self.assemblies_peak=max(self.assemblies_peak,len(snapshot["assembly_records"]));self.bridge_log_peak=max(self.bridge_log_peak,len(snapshot["assembly_bridge_events"]))
        telemetry=snapshot["telemetry"]
        return LongLifeSample(runtime.world_time,runtime.actions_completed,runtime.scheduler_events_processed,runtime.scheduler.size,runtime.peak_scheduler_queue,len(core.graph.nodes),self.cognits_peak,core.graph.relation_count,self.relations_peak,len(snapshot["assembly_records"]),self.assemblies_peak,len(snapshot["assembly_matches"]),len(snapshot["assembly_bridge_events"]),self.bridge_log_peak,core.planner.total_cycles,0 if session is None else len(session.pending_work),len(core.memory.structures),len(core.perception.tracks),len(core.composites.candidates),len(core.deletion_candidates),len(core.dirty_cognits),int(telemetry[0]),core.backend.full_graph_sync_calls)


def validate_long_life_state(runtime):
    """Fail loudly on corrupt native/runtime state; never repairs or clamps it."""
    core=runtime.simulation.core;neural=core.backend.engine.neurodynamic_substrate().snapshot()
    numeric=("potential","base_threshold","adaptation","pre_trace","post_trace","homeostatic_threshold_bias","weight","delay")
    for name in numeric:
        if not all(math.isfinite(float(value)) for value in neural[name]):raise AssertionError(f"non-finite neural {name}")
    if not math.isfinite(float(neural["now"])):raise AssertionError("non-finite neural time")
    for name in ("last_update","refractory_until","last_spike","trace_last_update","homeostasis_last_update"):
        if any(not math.isfinite(float(value)) and float(value)!=float("-inf") for value in neural[name]):raise AssertionError(f"invalid neural time sentinel in {name}")
    if any(weight<neural["weight_min"] or weight>neural["weight_max"] for weight in neural["weight"]):raise AssertionError("neural weight outside configured bounds")
    if any(float(row[0])<neural["now"] for row in neural["pending"]):raise AssertionError("pending neural event is in the past")
    events=runtime.scheduler.snapshot()
    if any(not math.isfinite(event.time) or event.time<runtime.world_time for event in events):raise AssertionError("scheduler event is non-finite or in the past")
    frontier=core.continuous_frontier;session=frontier.session if frontier else None
    if session is not None:
        if session.pending_keys!={(work.kind.value,work.key) for work in session.pending_work}:raise AssertionError("planner pending key divergence")
        if any(node_id not in core.graph.nodes for node_id in session.working|set(session.last_recalled)):raise AssertionError("planner contains stale Cognit ID")
    if any(node_id not in core.graph.nodes for node_id in core.previous_active|set(core.previous_context)|core.dirty_cognits):raise AssertionError("runtime context contains stale Cognit ID")
    return True
