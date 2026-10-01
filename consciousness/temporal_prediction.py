"""Bounded graph projections from observed WorldTime evidence.

Timing moments annotate the existing transition evidence; rho remains the only
source of predictive probability. Helpers have no physical-world inputs.
"""
from math import exp

from .patterns import is_internal_primitive
from .relation import RelationType
from .valuation import InternalEstimate, internal_estimate


def successors(core, frontier, action=None):
    settings = core.settings
    sources = sorted(frontier)
    action_id = action.value if action else 0
    if core.backend:
        rows = [(int(s)+1, int(t)+1, q, delay) for s,t,q,delay in
                core.backend.engine.timed_successors([i-1 for i in sources], action_id,
                    settings.relation_provisional_support, settings.planning_temporal_probability_floor)]
    else:
        rows = []
        kind = RelationType.SELF_ACTION if action else RelationType.SEQUENTIAL
        for source in sources:
            for edge in core.graph.outgoing(source):
                if edge.relation_type is not kind or (action and edge.context_id != action_id):continue
                moments = core.transitions.timings.get((source, edge.target_id, action_id))
                if not moments or moments[0] < settings.relation_provisional_support:continue
                n, mean, m2 = moments
                variance = m2 / max(1, n-1)
                q = edge.prediction_probability * edge.confidence * (1-edge.contradiction_evidence)
                q /= 1 + variance / max(1e-9, mean*mean)
                if q >= settings.planning_temporal_probability_floor:
                    rows.append((source, edge.target_id, q, mean))
    result = {}
    for source,target,q,delay in sorted(rows):
        probability, start = frontier[source]
        witness = (probability*q, start+delay)
        if witness[0] < settings.planning_temporal_probability_floor or witness[1] > settings.planning_prediction_time_horizon:continue
        previous = result.get(target)
        # Correlated witnesses to the same node are not independent trials.
        if previous is None or (witness[0],-witness[1]) > (previous[0],-previous[1]):result[target]=witness
    return result


def internal_channel(graph, node_id):
    node=graph.nodes.get(node_id);pattern=node.pattern if node else None
    if not pattern or len(pattern.participants)!=1:return None
    primitive=pattern.participants[0]
    if not is_internal_primitive(primitive):return None
    suffix=primitive[2].removeprefix("internal_")
    return (int(suffix),primitive[3]) if suffix.isdecimal() else None


def calibrated_estimate(core, witnesses, levels):
    groups={}
    for node_id,(q,delay) in sorted(witnesses.items()):
        channel=internal_channel(core.graph,node_id)
        if channel is None:continue
        previous=groups.setdefault(channel[0],{}).get(channel[1])
        if previous is None or (q,-delay)>(previous[1],-previous[2]):groups[channel[0]][channel[1]]=(node_id,q,delay)
    calibrated={};discounted={};ambiguity=0.
    for bins in groups.values():
        mass=sum(q for _,q,_ in bins.values())
        concentration=sum((q/mass)**2 for _,q,_ in bins.values()) if mass else 0.
        ambiguity=max(ambiguity,1-concentration)
        for node_id,q,delay in bins.values():
            weight=q/max(1.,mass)*concentration
            calibrated[node_id]=weight
            discounted[node_id]=weight*exp(-core.settings.planning_time_discount*delay)
    targets=core.homeostatic_target_levels;bins=core.settings.interoception_bins
    base=internal_estimate(core.graph,calibrated,levels,targets,bins)
    timed=internal_estimate(core.graph,discounted,levels,targets,bins)
    return InternalEstimate(base.levels,timed.progress,base.confidence,base.predictions),ambiguity


def merge_projected_state(graph, baseline, temporal, replaced_internal_channels):
    """Conservative state evolution; absence is never inferred from missing edges."""
    replaced=set(replaced_internal_channels)
    def untouched(node_id):
        node=graph.nodes.get(node_id);pattern=node.pattern if node else None
        if not pattern:return True
        # Mixed sensor patterns also become stale when their internal channel
        # changes; their external participant is preserved as ordinary context.
        channels={int(p[2].removeprefix('internal_')) for p in pattern.participants
                  if is_internal_primitive(p) and p[2].removeprefix('internal_').isdecimal()}
        return not channels & replaced
    retained={i for i in baseline if untouched(i)}
    return frozenset(retained | set(temporal))


def _merge_witnesses(graph, previous, following):
    replaced={internal_channel(graph,i)[0] for i in following if internal_channel(graph,i) is not None}
    same_bins={internal_channel(graph,i) for i in following if internal_channel(graph,i) is not None}
    retained={i:value for i,value in previous.items() if internal_channel(graph,i) is None or
              internal_channel(graph,i)[0] not in replaced or internal_channel(graph,i) in same_bins}
    for node_id,value in sorted(following.items()):
        older=retained.get(node_id)
        if older is None or (value[0],-value[1])>(older[0],-older[1]):retained[node_id]=value
    return retained,replaced


def delayed_estimate(core, state, action, levels, start_time=0., baseline_effects=None, baseline_state=()):
    baseline_effects=baseline_effects or {}
    frontier=successors(core,{i:(1.,start_time) for i in sorted(state)},action)
    if not frontier:
        estimate=internal_estimate(core.graph,baseline_effects,levels,core.homeostatic_target_levels,
                                   core.settings.interoception_bins)
        return estimate,{"usable":False,"passive_depth":0,"elapsed":start_time,"ambiguity":0.,
                         "witnesses":0,"projected_state":tuple(sorted(baseline_state))}
    timed_channels={internal_channel(core.graph,i)[0] for i in frontier if internal_channel(core.graph,i) is not None}
    endpoint={i:(q,start_time) for i,q in sorted(baseline_effects.items()) if i not in frontier and
              (internal_channel(core.graph,i) is None or internal_channel(core.graph,i)[0] not in timed_channels)}
    endpoint,replaced=_merge_witnesses(core.graph,endpoint,frontier)
    projected=merge_projected_state(core.graph,baseline_state,frontier,replaced)
    seen=set(state);depth=0
    for depth_index in range(core.settings.planning_passive_prediction_depth):
        following=successors(core,frontier)
        following={i:value for i,value in following.items() if i not in seen}
        if not following:break
        seen.update(frontier);depth=depth_index+1
        endpoint,replaced=_merge_witnesses(core.graph,endpoint,following)
        projected=merge_projected_state(core.graph,projected,following,replaced)
        frontier=following
    estimate,ambiguity=calibrated_estimate(core,endpoint,levels)
    return estimate,{"usable":True,"passive_depth":depth,
                     "elapsed":max(start_time,max((t for _,t in endpoint.values()),default=start_time)),
                     "ambiguity":ambiguity,"witnesses":len(endpoint),"projected_state":tuple(sorted(projected))}
