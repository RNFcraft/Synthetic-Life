"""Explicit forensic line profiler. Its instrumented timings are not throughput."""
import inspect
import sys
from time import perf_counter_ns
from .performance import Sample


class PlannerForensicProfiler:
    stages = ('candidate_generation', 'state_action_expansion', 'prediction_request_preparation',
              'native_batch_call', 'future_state_construction', 'score_decomposition',
              'loop_epistemic', 'homeostatic_estimate', 'candidate_object_creation',
              'beam_sorting_and_ties', 'deduplication', 'other')

    def __init__(self, planner):
        method = inspect.unwrap(planner._search)
        self.code = method.__code__
        source, first = inspect.getsourcelines(method)
        self.labels = {}
        for index, line in enumerate(source, first):
            text = line.strip()
            label = 'other'
            for fragment, stage in (
                ('expanded=[]', 'candidate_generation'),
                ('for actions,state,states', 'state_action_expansion'),
                ('for action,p in predictions', 'state_action_expansion'),
                ('layer_states=[]', 'prediction_request_preparation'),
                ('needs_predictions=', 'prediction_request_preparation'),
                ('needs_effects=', 'prediction_request_preparation'),
                ('prediction_tick=', 'prediction_request_preparation'),
                ('state not in seen', 'deduplication'),
                ('planner_transition_batch(', 'native_batch_call'),
                ('action_effects_batch(', 'native_batch_call'),
                ('_graph_predictions_for_actions(', 'native_batch_call'),
                ('transition_cache[key]=', 'future_state_construction'),
                ('next_state,alignment,conf=', 'future_state_construction'),
                ('predicted_ids=', 'future_state_construction'),
                ('memory_cache', 'score_decomposition'),
                ('epistemic=epistemic_cache', 'score_decomposition'),
                ('value+=', 'score_decomposition'),
                ('loop_cache', 'loop_epistemic'),
                ('epistemic_cache[key]=', 'loop_epistemic'),
                ('progress_cache[key]=core.predicted', 'loop_epistemic'),
                ('estimate=self.homeostatic_estimate', 'homeostatic_estimate'),
                ('estimate_key=', 'homeostatic_estimate'),
                ('cached=homeostatic_numeric_cache', 'homeostatic_estimate'),
                ('homeostatic_numeric_cache[estimate_key]', 'homeostatic_estimate'),
                ('estimate,diagnostics=cached', 'homeostatic_estimate'),
                ('expanded.append(', 'candidate_object_creation'),
                ('return Plan(', 'candidate_object_creation'),
                ('beam=nsmallest(', 'beam_sorting_and_ties'),
            ):
                if fragment in text:label = stage
            self.labels[index] = label
        self.samples = {name:Sample() for name in self.stages}
        self.active = {}
        self.searches = self.native_calls = self.states = self.pairs = 0
        self.previous = None

    def trace(self, frame, event, arg):
        if frame.f_code is not self.code:return None
        now = perf_counter_ns()
        identity = id(frame)
        if event == 'call':
            self.searches += 1
        elif event in ('line', 'return'):
            previous = self.active.pop(identity, None)
            if previous:
                label, start = previous
                self.samples[label].add((now-start)/1000., 1)
            if event == 'line':
                label = self.labels.get(frame.f_lineno, 'other')
                # Each execution of the body starts with key=(state,action).
                if self._pair_line == frame.f_lineno:self.pairs += 1
                if self._state_line == frame.f_lineno:self.states += 1
                self.active[identity] = label, perf_counter_ns()
        return self.trace

    def __enter__(self):
        if sys.gettrace() is not None:
            raise RuntimeError('forensic profiler requires no existing debugger/trace hook')
        source, first = inspect.getsourcelines(self.code)
        self._pair_line = next(first+i for i, line in enumerate(source) if line.strip() == 'key=(state,action)')
        self._state_line = next(first+i for i, line in enumerate(source) if line.strip() == 'predictions=prediction_cache.get(state)')
        sys.settrace(self.trace)
        return self

    def __exit__(self, *exc):
        sys.settrace(None)
        self.active.clear()

    def report(self):
        return dict(instrumented=True, timing_unit='line intervals; nested calls included',
                    searches=self.searches, states_expanded=self.states, state_action_pairs=self.pairs,
                    stages={name:sample.report() for name,sample in self.samples.items()},
                    tie_handling='included in unchanged beam_sorting_and_ties',
                    deduplication='request state deduplication; no candidate deduplication exists')
