"""Optional bounded host profiler. Installed by host tools, never read by policy."""
from collections import deque
from dataclasses import dataclass, field
from functools import wraps
from time import perf_counter_ns


@dataclass
class Sample:
    count: int = 0
    total_us: float = 0.
    ema_us: float = 0.
    maximum_us: float = 0.
    work_units: int = 0
    recent: deque = field(default_factory=lambda: deque(maxlen=256))

    def add(self, us, units):
        self.ema_us = .8*self.ema_us+.2*us if self.count else us
        self.count += 1
        self.total_us += us
        self.maximum_us = max(self.maximum_us, us)
        self.work_units += units
        self.recent.append(us)

    def report(self):
        values = sorted(self.recent)
        return dict(count=self.count,total_us=self.total_us,ema_us=self.ema_us,
                    max_us=self.maximum_us,work_units=self.work_units,
                    p50_us=values[(len(values)-1)//2] if values else 0.,
                    p95_us=values[int((len(values)-1)*.95)] if values else 0.)


class HostProfiler:
    """Explicit attachment; no timers, wrappers or samples exist until enabled."""
    def __init__(self):
        self.samples = {}
        self._restores = []
        self._planner_depth = 0

    def wrap(self, owner, method, label, units=lambda args: 1):
        original = getattr(owner, method)
        sample = self.samples.setdefault(label, Sample())
        @wraps(original)
        def measured(*args, **kwargs):
            start = perf_counter_ns()
            planner = label == 'planner_beam_refinement'
            if planner:self._planner_depth += 1
            try:
                return original(*args, **kwargs)
            finally:
                elapsed = (perf_counter_ns()-start)/1000.
                if planner:self._planner_depth -= 1
                sample.add(elapsed, units(args))
                if self._planner_depth and label.startswith('native_call.'):
                    self.samples.setdefault('planner_'+label,Sample()).add(elapsed,units(args))
        own = method in vars(owner)
        self._restores.append((owner,method,original,own))
        setattr(owner,method,measured)

    def attach(self, runtime):
        core = runtime.simulation.core
        for owner,method,label in (
            (runtime,'_dispatch','scheduler_dispatch'),
            (runtime.simulation.world,'apply_intent','world_action_completion'),
            (core.patterns,'observe','sensory_decomposition'),
            (core,'_match_and_birth','pattern_matching_birth'),
            (core,'_propagate','wave_propagation'),
            (core.backend,'update_transition_evidence','relation_evidence'),
            (core.backend,'materialize','relation_materialization'),
            (core.backend.engine,'lifecycle_step','relation_lifecycle_boundary'),
            (core.backend.engine,'homeostatic_step','homeostasis_numeric_boundary'),
            (core.backend,'predict_graph_batch','prediction_batch'),
            (core.backend,'planner_transition_batch','planner_transition_batch_boundary'),
            (core.planner,'_search','planner_beam_refinement'),
            (core.memory,'recall','memory_recall'),
            (runtime.simulation.physiology,'advance_to','physiology_numeric_update'),
            (runtime,'publish_brain_snapshot','presentation_snapshot_preparation'),
            (runtime,'advance_neural_to','micro_neural_boundary'),
        ):
            self.wrap(owner,method,label)
        return self

    def attach_native_calls(self, engine):
        """Count callable pybind crossings, including direct timed-successor calls.

        Properties are excluded; these diagnostic wrappers are never used for
        uninstrumented throughput measurements.
        """
        descriptors=getattr(engine,'_inner',engine)
        for name in sorted(vars(type(descriptors))):
            if not name.startswith('_') and callable(getattr(engine,name,None)):
                self.wrap(engine,name,'native_call.'+name)
        return self

    def close(self):
        for owner,method,original,own in reversed(self._restores):
            if own:
                setattr(owner,method,original)
            else:
                delattr(owner,method)
        self._restores.clear()

    def report(self):
        return {name: sample.report() for name,sample in sorted(self.samples.items())}
