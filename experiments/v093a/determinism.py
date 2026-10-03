"""Event-index differential localization without rounding scientific state."""
from .credit_trace import boundary_state, digest, plain, relation_rows


def first_difference(left, right, path="$", limit=20):
    """Return exact leaf differences, retaining a bounded explanatory result."""
    rows = []
    def visit(a, b, name):
        if len(rows) >= limit: return
        from dataclasses import is_dataclass
        from enum import Enum
        if is_dataclass(a) or isinstance(a,(Enum,tuple,set,frozenset)):a=plain(a)
        if is_dataclass(b) or isinstance(b,(Enum,tuple,set,frozenset)):b=plain(b)
        if type(a) is not type(b):
            rows.append(dict(path=name, left=a, right=b)); return
        if isinstance(a, dict):
            for key in sorted(set(a)|set(b),key=str):
                if key not in a or key not in b: rows.append(dict(path=name+"."+str(key), left=a.get(key), right=b.get(key)))
                else: visit(a[key], b[key], name+"."+str(key))
                if len(rows) >= limit: break
        elif isinstance(a, list):
            if len(a) != len(b): rows.append(dict(path=name+".length", left=len(a), right=len(b)))
            for index, (x,y) in enumerate(zip(a,b)): visit(x,y,f"{name}[{index}]")
        elif a != b: rows.append(dict(path=name, left=a, right=b))
    visit(left, right, path)
    return rows[:limit]


class BoundaryTrace:
    def __init__(self, stream, *, detail_index=None):
        self.stream = stream
        self.index = 0
        self.detail_index = detail_index
        self.detail = None
        self.operations = []

    def event(self, runtime, event, phase):
        if phase != "after": return
        core=runtime.simulation.core
        engine=core.backend.engine
        # Compact boundary projection; full stored state is replayed only at the
        # first differing index. No copying of the cumulative timing map per step.
        state = dict(world=runtime.simulation.world.to_dict(),
            physiology=runtime.simulation.physiology.to_dict(),
            nodes=engine.diagnostic_stored_nodes(), relations=relation_rows(core),
            counts=[engine.live_cognit_count,engine.relation_count],
            selectivity=[core._selectivity_sum,core._selectivity_count,
                [(i,n.pattern.selectivity_trials,n.pattern.positive_match_mean,n.pattern.background_match_mean)
                 for i,n in sorted(core.graph.nodes.items()) if n.pattern]],
            state=core.state, planner=core.planner.to_dict(),
            action=plain(runtime.simulation.last_action),
            rng=runtime.simulation.rng.getstate(), scheduler=runtime.scheduler_state())
        row = dict(index=self.index, time=event.time, event_id=event.id,
            event_type=event.type.name, payload=event.payload,
            digests={k:digest(v) for k,v in state.items()})
        from simulation.scenario import canonical_json
        self.stream.write(canonical_json(row)+"\n")
        self.stream.flush()
        if self.index == self.detail_index: self.detail = boundary_state(runtime)
        self.index += 1

    def learning(self, *args): pass
    def plan_candidate(self, *args): pass
    def selectivity(self, core, node_id, before, after, old, new):
        if self.index == self.detail_index:
            self.operations.append(dict(cognit_id=node_id,sum_before=before,sum_after=after,old=old,new=new))


def first_boundary(left_path, right_path):
    """Linear streaming search: O(1) retained rows, earliest unequal event.

    Binary search of unchained checkpoint digests could miss reconvergence; a
    linear stream guarantees the first divergence without duplicating full state.
    """
    from itertools import zip_longest
    from .credit_trace import read_rows
    for index, (left,right) in enumerate(zip_longest(read_rows(left_path), read_rows(right_path))):
        if left != right:
            return dict(index=index, left=left, right=right)
    return None
