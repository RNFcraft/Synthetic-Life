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


def delayed_estimate(core, state, action, levels, start_time=0.):
    frontier=successors(core,{i:(1.,start_time) for i in sorted(state)},action)
    endpoint=dict(frontier);seen=set(state);depth=0
    for depth_index in range(core.settings.planning_passive_prediction_depth):
        following=successors(core,frontier)
        following={i:value for i,value in following.items() if i not in seen}
        if not following:break
        seen.update(frontier);depth=depth_index+1
        replaced={internal_channel(core.graph,i)[0] for i in following if internal_channel(core.graph,i) is not None}
        same_bins={internal_channel(core.graph,i) for i in following if internal_channel(core.graph,i) is not None}
        retained={i:value for i,value in endpoint.items() if internal_channel(core.graph,i) is None or
                  internal_channel(core.graph,i)[0] not in replaced or internal_channel(core.graph,i) in same_bins}
        for node_id,value in following.items():
            previous=retained.get(node_id)
            if previous is not None and (previous[0],-previous[1])>(value[0],-value[1]):following[node_id]=previous
        endpoint=retained
        endpoint.update(following);frontier=following
    estimate,ambiguity=calibrated_estimate(core,endpoint,levels)
    return estimate,{"passive_depth":depth,"elapsed":max((t for _,t in endpoint.values()),default=0.),
                     "ambiguity":ambiguity,"witnesses":len(endpoint),"projected_state":tuple(sorted(frontier))}
