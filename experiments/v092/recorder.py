"""Causally inert event-boundary observation on the production runtime."""
from consciousness.native_engine import RuntimeEventType
from simulation.scenario import causal_digest
from .metrics import trajectory_metrics


def sample(runtime):
    sim=runtime.simulation;core=sim.core
    physical=sim.physiology.snapshot();plan=core.planner.plan
    pending=[event for event in runtime.scheduler.snapshot() if event.type==RuntimeEventType.WORLD_ACTION_COMPLETE]
    return dict(time=runtime.world_time,energy=physical.energy,nutrients=physical.nutrients,hydration=physical.hydration,
        tension=physical.tension,brownout=physical.energy<=0,actions=runtime.actions_completed,
        event_sequence=sim.event_sequence.value,
        resources=[list(row) for row in sim.world.native.resource_state()],
        bodies=[[b.id,b.x,b.y,b.orientation] for b in sim.world.bodies.values()],
        completed_action=sim.last_action.kind.name if sim.last_action else None,
        completed_success=sim.last_action_result.name if sim.last_action_result else None,
        pending_action=pending[0].payload if pending else None,
        pending_completion=pending[0].time if pending else None,
        internal=list(runtime.last_internal.levels) if runtime.last_internal else None,
        plan=None if plan is None else dict(actions=[a.name for a in plan.actions],score=plan.score,confidence=plan.confidence),
        diagnostics=core.planner.homeostatic_diagnostics())


def learned_evidence(runtime,initial_levels):
    core=runtime.simulation.core;engine=core.backend.engine
    timing=engine.temporal_state();relations=[];beneficial=[]
    for node_id in sorted(core.graph.nodes):
        for relation in core.graph.outgoing(node_id):
            if relation.relation_type.name not in ("SELF_ACTION","SEQUENTIAL"): continue
            target=core.graph.nodes.get(relation.target_id);pattern=target.pattern if target else None
            row=dict(source=relation.source_id,target=relation.target_id,type=relation.relation_type.name,
                     action=relation.context_id,support=relation.support,confidence=relation.confidence,
                     probability=relation.prediction_probability,contradiction=relation.contradiction_evidence)
            relations.append(row)
            if pattern and any(p[2].startswith("internal_") and p[2][9:].isdigit()
                               and int(p[2][9:])<3 and p[3]>initial_levels[int(p[2][9:])]
                               for p in pattern.participants):
                beneficial.append(row)
    timed_keys={(int(row[0])+1,int(row[1])+1,int(row[2])):row for row in timing}
    for row in beneficial:
        moments=timed_keys.get((row["source"],row["target"],row["action"] or 0))
        row["timing"] = list(moments) if moments else None
    return dict(timing_rows=[list(row) for row in timing],timing_observations=sum(int(row[3]) for row in timing),
                passive_observations=sum(int(row[3]) for row in timing if int(row[2])==0),
                relations=relations,beneficial_relations=beneficial,
                full_graph_sync_calls=core.backend.full_graph_sync_calls)


def record(runtime,horizon,discount, *, include_evidence=True):
    if runtime.world_time!=0: raise ValueError("recording must start from a fresh physical episode")
    samples=[sample(runtime)];consumptions=[];decisions=[];last_decision=None
    initial_levels=runtime.simulation.interoception.sample(runtime.simulation.physiology.snapshot()).levels
    while runtime.scheduler.size and runtime.scheduler.snapshot()[0].time<=horizon:
        timestamp=runtime.scheduler.snapshot()[0].time
        runtime.run_until(timestamp)
        current=sample(runtime);previous=samples[-1]
        before={int(row[0]):row for row in previous["resources"] if row[2]>0}
        after={int(row[0]) for row in current["resources"]}
        disappeared=sorted(set(before)-after)
        if disappeared and current["actions"]>previous["actions"] and current["completed_success"]=="SUCCESS" and current["completed_action"].startswith("INTERACT"):
            if current["nutrients"]>previous["nutrients"]:
                consumptions.append(dict(time=current["time"],actions=current["actions"],ids=disappeared,
                    nutrient_gain=current["nutrients"]-previous["nutrients"],
                    previous_internal=previous["internal"],observed_internal=current["internal"],
                    energy_before=previous["energy"],energy_after=current["energy"]))
        decision=(current["pending_completion"],current["pending_action"])
        if current["pending_action"] is not None and decision!=last_decision:
            decisions.append(dict(time=current["time"],action=current["pending_action"],plan=current["plan"],
                                  diagnostics=current["diagnostics"],body=current["bodies"],
                                  energy=current["energy"],nutrients=current["nutrients"],internal=current["internal"]))
            last_decision=decision
        samples.append(current)
    if runtime.world_time<horizon:
        runtime.run_until(horizon);samples.append(sample(runtime))
    metrics=trajectory_metrics(samples,consumptions,horizon,discount)
    metrics.update(initial_reserves={key:samples[0][key] for key in ("energy","nutrients","hydration")},
                   final_reserves={key:samples[-1][key] for key in ("energy","nutrients","hydration")},
                   consumptions=consumptions,decisions=decisions,trajectory=samples,
                   final_digest=causal_digest(runtime),
                   evidence=learned_evidence(runtime,initial_levels) if include_evidence else None,
                   full_graph_sync_calls=runtime.simulation.core.backend.full_graph_sync_calls)
    assert metrics["full_graph_sync_calls"]==0
    return metrics
