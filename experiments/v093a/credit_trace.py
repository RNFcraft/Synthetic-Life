"""Streaming observation of existing evidence and planner operations."""
from dataclasses import asdict, is_dataclass
from enum import Enum
from hashlib import sha256
import json

from experiments.v092.recorder import sample
from simulation.scenario import canonical_json


def plain(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.name
    if is_dataclass(value):
        return plain(asdict(value))
    if isinstance(value, dict):
        return {str(plain(k)): plain(v) for k, v in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted(plain(v) for v in value)
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    return value


def digest(value):
    return sha256(canonical_json(plain(value)).encode()).hexdigest()


def relation_rows(core):
    # outgoing() copies stored records and does not materialize lazy decay.
    return [list(row) for row in core.backend.engine.outgoing([i-1 for i in sorted(core.graph.nodes)])]


def boundary_state(runtime):
    """Stored state, not a projected/materialized persistence snapshot."""
    sim = runtime.simulation
    core = sim.core
    engine = core.backend.engine
    memory = core.memory.to_dict()
    for field in ("feature_seen", "feature_change"):
        memory[field] = sorted(memory[field], key=lambda row: canonical_json(row[0]))
    return plain(dict(
        measurement=sample(runtime), world=sim.world.to_dict(),
        physiology=sim.physiology.to_dict(), rng=sim.rng.getstate(),
        nodes=engine.diagnostic_stored_nodes(), relations=relation_rows(core),
        elapsed=engine.continuous_time_state(), relation_elapsed=engine.continuous_relation_time_state(),
        temporal=engine.temporal_state(), history=engine.transition_history(),
        scheduler=runtime.scheduler_state(), frontier=runtime._frontier_state(),
        calibration=core.calibration.to_dict(), memory=memory,
        state=core.state, previous_ids=core.previous_active,
        patterns=[(i, n.kind, n.pattern) for i, n in sorted(core.graph.nodes.items())],
        temporal_context=dict(ids=sorted(getattr(core, "timed_previous_ids", ())),
            time=getattr(core, "timed_observation_time", None),
            attempt=getattr(core, "learning_action_attempt", None),
            completion=getattr(core, "pending_learning_action", None))))


def candidate_rows(core, before, completion, observed):
    """Actual native pair counts and admission predicates for internal targets."""
    action = completion[0].value if completion else 0
    history = core.backend.engine.transition_history()
    edges = {(r[0]+1, r[1]+1, r[2], r[3]): r for r in relation_rows(core)}
    timings = {(int(s)+1, int(t)+1, int(a)): (n, mean, m2)
               for s, t, a, n, mean, m2 in core.backend.engine.temporal_state()}
    settings = core.settings
    rows = []
    for target in sorted(observed):
        node = core.graph.nodes.get(target)
        if not node or not node.pattern or not any(p[2].startswith("internal_") for p in node.pattern.participants):
            continue
        for source in sorted(before):
            if source == target:
                continue
            metrics = core.backend.engine.transition_metrics(source-1, target-1, action)
            pairs, conditional, baseline, lift, probability, trials = metrics
            for conditioned in (False, True) if action else (False,):
                kind = "SELF_ACTION" if conditioned else "SEQUENTIAL"
                from consciousness.relation import RelationType
                key = (source, target, RelationType[kind].value, action if conditioned else 0)
                edge = edges.get(key)
                support = sum(source-1 in b and target-1 in t and a == action for b, a, t in history) if conditioned else pairs
                actual_lift = probability/max(conditional, 1e-9) if conditioned else lift
                reasons = []
                if conditioned and completion and not completion[1]: reasons.append("FAILED_ACTION_NO_POSITIVE_EVIDENCE")
                if support < settings.relation_provisional_support: reasons.append("INSUFFICIENT_SUPPORT")
                if actual_lift < settings.relation_provisional_lift: reasons.append("LIFT_BELOW_THRESHOLD")
                if edge is None and not reasons:
                    # Quota and capacity are evaluated inside native materialize_current;
                    # don't invent which one fired when the endpoint snapshot cannot tell.
                    reasons.append("NOT_MATERIALIZED_REQUIRES_QUOTA_OR_LIFECYCLE_TRACE")
                rows.append(dict(source=source, target=target, type=kind, action=key[3],
                    source_pattern=plain(core.graph.nodes[source].pattern), target_pattern=plain(node.pattern),
                    support=support, required_support=settings.relation_provisional_support,
                    lift=actual_lift, required_lift=settings.relation_provisional_lift,
                    confidence=edge[5] if edge else None, contradiction=edge[11] if edge else None,
                    admitted=edge is not None, reasons=reasons,
                    admission_result="EXISTING_MATERIALIZED_RELATION" if edge else "NO_MATERIALIZED_RELATION",
                    materialized_support=edge[7] if edge else None,
                    timing=timings.get((source,target,key[3])), relation=plain(edge)))
    return rows


class CreditTrace:
    """Constant retained history; caller owns the JSONL stream and its lifetime."""
    def __init__(self, stream):
        self.stream = stream
        self.rows = 0

    def write(self, row):
        self.stream.write(canonical_json(plain(row))+"\n")
        self.rows += 1

    def event(self, runtime, event, phase):
        core=runtime.simulation.core
        self.write(dict(kind="event", phase=phase, time=event.time, event_id=event.id,
            event_type=event.type.name, payload=event.payload, measurement=sample(runtime),
            sensory=plain(core.patterns.last_events),
            percepts=plain(list(core.perception.tracks.values())),
            futures=plain(core.state.futures)))

    def learning(self, core, before, completion, observed, now, elapsed, phase):
        endpoints = []
        for primitive in core.patterns.last_events:
            if not primitive.channel.startswith("internal_"): continue
            key = primitive.structural_key()
            proto = core.patterns.prototypes.get(((key,), False))
            node_id = core.pattern_nodes.get((key,))
            score = None
            if proto:
                s = core.settings
                score = max(0., min(1.,
                    s.pattern_frequency_weight*min(1.,proto.occurrences/s.proto_min_occurrences)
                    + s.pattern_stability_weight*proto.stability
                    + s.pattern_prediction_weight*(1.-proto.predictive_value)
                    + s.pattern_compression_weight*min(1.,proto.occurrences/12.)
                    - s.pattern_redundancy_weight*proto.redundancy))
            reasons = []
            if node_id is None:
                if proto is None: reasons.append("NO_PROTOTYPE")
                elif proto.occurrences < core.settings.proto_min_occurrences: reasons.append("PROTO_OCCURRENCES_BELOW_THRESHOLD")
                elif score < core.settings.cognit_birth_threshold: reasons.append("COGNIT_BIRTH_SCORE_BELOW_THRESHOLD")
                else: reasons.append("BIRTH_QUOTA_OR_CAPACITY_REQUIRES_BIRTH_TRACE")
            elif node_id not in observed: reasons.append("NOT_DIRECTLY_MATCHED_ENDPOINT")
            endpoints.append(dict(primitive=plain(primitive), key=key, cognit_id=node_id,
                observed=node_id in observed, prototype=plain(proto), birth_score=score,
                birth_threshold=core.settings.cognit_birth_threshold,
                required_occurrences=core.settings.proto_min_occurrences, reasons=reasons))
        self.write(dict(kind="learning", phase=phase, time=now, elapsed=elapsed,
            sources=sorted(before), targets=sorted(observed), completion=plain(completion),
            source_identities=[dict(id=i,kind=core.graph.nodes[i].kind,
                pattern=plain(core.graph.nodes[i].pattern)) for i in sorted(before) if i in core.graph.nodes],
            spatial_context=dict(place=core.memory.current_place_id,
                structures=plain([m for m in core.memory.structures.values() if m.cognit_id in before])),
            internal_endpoints=endpoints,
            candidates=candidate_rows(core, before, completion, observed)))

    def plan_candidate(self, core, actions, state, projected, terms, confidence, estimate, usable):
        self.write(dict(kind="planner_candidate", tick=core.cognitive_tick,
            actions=plain(actions), sources=sorted(state), projected=sorted(projected),
            terms=terms, confidence=confidence, estimate=plain(estimate), temporal_usable=usable,
            temporal=plain(getattr(core.planner, "temporal_diagnostics", {}))))

    def selectivity(self, core, node_id, before, after, old, new):
        self.write(dict(kind="selectivity_update",tick=core.cognitive_tick,
            cognit_id=node_id,sum_before=before,sum_after=after,old=old,new=new))


def attach(runtime, observer):
    """Register host-only callbacks; registration never enters saved causal state."""
    runtime.diagnostic_observer = observer
    runtime.simulation.core.diagnostic_observer = observer


def read_rows(path):
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)
