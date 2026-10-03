"""Offline audit tables; these never change scientific acceptance or trial policy."""
import argparse
import json
from pathlib import Path
from .protocol import load_protocol,ROOT
from .recorder import learned_evidence
from .runner import instantiate
from simulation.scenario import artifact_checksum


def effect_retained(fresh,full,ablated):
    effect=fresh-full;residual=fresh-ablated
    return dict(full_advantage=effect,remaining_advantage=residual,
        retained_fraction=residual/effect if effect>1e-9 else None,
        removed_fraction=(effect-residual)/effect if effect>1e-9 else None)


def inspect_checkpoint(path,scenario,seed):
    runtime,_=instantiate(scenario,seed,"EXPERIENCED_FULL",path)
    core=runtime.simulation.core
    bins={0:set(),1:set(),2:set()}
    for node in core.graph.nodes.values():
        if not node.pattern:continue
        for p in node.pattern.participants:
            if p[2].startswith("internal_") and p[2][9:].isdigit() and int(p[2][9:]) in bins:
                bins[int(p[2][9:])].add(p[3])
    levels=runtime.simulation.interoception.sample(runtime.simulation.physiology.snapshot()).levels
    evidence=learned_evidence(runtime,levels)
    return dict(brain_checksum=artifact_checksum(path),nodes=len(core.graph.nodes),node_capacity=core.settings.max_cognits,
        relations=core.backend.engine.relation_count,relation_capacity=core.settings.max_relations,
        represented_internal_bins={str(k):sorted(v) for k,v in bins.items()},
        supported_timed_beneficial_relations=[r for r in evidence["beneficial_relations"] if r["timing"] and r["support"]>=6],
        full_graph_sync_calls=core.backend.full_graph_sync_calls),evidence


def audit(protocol,output):
    output=Path(output);result=json.loads((output/"results.json").read_text(encoding="utf-8"))
    if result["protocol_checksum"]!=protocol.checksum:raise ValueError("protocol checksum mismatch")
    effects=[]
    for stage,row in result["acceptance"]["stages"].items():
        groups=row["summaries"]
        for group,metric in (("EXPERIENCED_NO_DELAYED","median_censored_time"),("EXPERIENCED_NO_MOTIVATION","median_J")):
            effects.append(dict(stage=stage,group=group,metric=metric,
                **effect_retained(groups["FRESH_FULL"][metric],groups["EXPERIENCED_FULL"][metric],groups[group][metric])))
    checkpoints={};baseline=None
    from .protocol import scenario_path
    for stage in protocol.data["STAGES"]:
        info=result["checkpoints"][stage["id"]];path=output/info["path"]
        if artifact_checksum(path)!=info["sha256"]:raise ValueError("checkpoint checksum mismatch")
        details,evidence=inspect_checkpoint(path,scenario_path(stage["evaluation"][0]["scenario"]),
                                           protocol.data["PROTOCOL"]["evaluation_seeds"][0])
        checkpoints[stage["id"]]=details
        if stage["id"]=="stage_4":baseline=evidence
    key=lambda r:(r["source"],r["target"],r["type"],r["action"])
    original={key(r):r for r in baseline["relations"]}
    counter=[]
    for row in result["counterfactual"]:
        detail=json.loads((output/row["trajectory_reference"]).read_text(encoding="utf-8"))
        changed=[]
        for relation in detail["evidence"]["relations"]:
            prior=original.get(key(relation)) if row["group"]!="FRESH_FULL" else None
            if prior and relation["contradiction"]>prior["contradiction"]+1e-9:
                changed.append(dict(source=relation["source"],target=relation["target"],action=relation["action"],
                    type=relation["type"],before=prior["contradiction"],after=relation["contradiction"]))
        counter.append(dict(group=row["group"],consumptions=row["consumption_count"],
            initial_reserves=row["initial_reserves"],final_reserves=row["final_reserves"],
            contradiction_increases=changed,
            relations_with_contradiction=sum(r["contradiction"]>0 for r in detail["evidence"]["relations"]),
            interpretation="Perceptual/action contradictions are not proof of a contradicted nutritive hypothesis without a supported resource-to-internal consequence."))
    data=dict(protocol_checksum=protocol.checksum,acceptance_unchanged=True,ablation_effects=effects,
              checkpoints=checkpoints,counterfactual=counter)
    (output/"research-diagnostics.json").write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return data


def appendix(data):
    lines=["", "## Additional offline audit (does not change acceptance)","",
        "| Stage | Ablation | Metric | Full advantage | Remaining advantage | Fraction removed |",
        "|---|---|---|---:|---:|---:|"]
    for row in data["ablation_effects"]:
        removed="n/a (no positive full advantage)" if row["removed_fraction"] is None else f"{100*row['removed_fraction']:.6g}%"
        lines.append(f"| {row['stage']} | {row['group']} | {row['metric']} | {row['full_advantage']:.6g} | {row['remaining_advantage']:.6g} | {removed} |")
    lines += ["", "Checkpoint graph/bin inventory:","", "```json",json.dumps(data["checkpoints"],indent=2,sort_keys=True),"```","",
        "Counterfactual contradiction observations:","", "```json",json.dumps(data["counterfactual"],indent=2,sort_keys=True),"```","",
        "Diagnostics above are observational and do not introduce new acceptance gates. Temporal diagnostics can reflect the last planner candidate rather than uniquely identify the selected plan; plan/physical/ablation evidence must be assessed together.",
        "The predeclared Stage 2 gate is conservative: it requires an explicit MOVE_UP/INTERACT_UP chain and a net E decline during MOVE. Generic orientation-relative INTERACT and digestion masking a movement cost can fail this narrow gate without demonstrating absence of an incurred movement cost.",""]
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--protocol",required=True);parser.add_argument("--output",required=True)
    parser.add_argument("--append-report",action="store_true");args=parser.parse_args()
    data=audit(load_protocol(args.protocol),args.output)
    if args.append_report:
        path=Path(args.output)/"RESULTS.md";text=path.read_text(encoding="utf-8")
        marker="\n## Additional offline audit (does not change acceptance)"
        text=text.split(marker)[0]+appendix(data)
        path.write_text(text,encoding="utf-8")
    print("Offline audit complete; acceptance unchanged.")


if __name__=="__main__":main()
