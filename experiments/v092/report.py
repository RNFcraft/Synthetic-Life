"""Predeclared deterministic paired gates and complete research tables."""
from collections import defaultdict
import json
from pathlib import Path
from .metrics import aggregate, paired_win, reduced_advantage
from .protocol import GROUPS
from world.actions import ActionType


def case_key(row):return (row["scenario"],row["seed"])


def compare(rows,thresholds,economy=False):
    groups={name:[r for r in rows if r["group"]==name] for name in GROUPS}
    summaries={name:aggregate(values) for name,values in groups.items()}
    maps={name:{case_key(row):row for row in values} for name,values in groups.items()}
    keys=set(maps["FRESH_FULL"])
    if any(set(mapping)!=keys for mapping in maps.values()):raise ValueError("unpaired group cases")
    fresh,full=summaries["FRESH_FULL"],summaries["EXPERIENCED_FULL"]
    wins=sum(paired_win(maps["EXPERIENCED_FULL"][key],maps["FRESH_FULL"][key]) for key in keys)
    gates=dict(minimum_cases=len(keys)>=thresholds["minimum_cases"],
        success_noninferiority=full["successes"]>=fresh["successes"],
        lower_median_time=full["median_censored_time"]<fresh["median_censored_time"]-1e-9,
        lower_median_actions=full["median_censored_actions"]<fresh["median_censored_actions"],
        paired_wins=wins/len(keys)>=thresholds["paired_win_rate"],
        practical_effect=(full["median_censored_time"]<=thresholds["practical_ratio"]*fresh["median_censored_time"]
                          or full["median_censored_actions"]<=thresholds["practical_ratio"]*fresh["median_censored_actions"]))
    if economy:
        gates.update(lower_J=full["median_J"]<fresh["median_J"]-1e-9,
            economy_effect=(full["median_energy_spent"]<=thresholds["economy_ratio"]*fresh["median_energy_spent"]
                            or full["median_censored_actions"]<=thresholds["economy_ratio"]*fresh["median_censored_actions"]
                            or full["brownouts"]<fresh["brownouts"]))
    # Primary delayed effect: censored time. Primary motivation effect: discounted tension J.
    gates["delayed_ablation"]=reduced_advantage(fresh["median_censored_time"],full["median_censored_time"],
        summaries["EXPERIENCED_NO_DELAYED"]["median_censored_time"],thresholds["ablation_reduction"])
    gates["motivation_ablation"]=reduced_advantage(fresh["median_J"],full["median_J"],
        summaries["EXPERIENCED_NO_MOTIVATION"]["median_J"],thresholds["ablation_reduction"])
    paired=[dict(scenario=key[0],seed=key[1],experienced_win=paired_win(maps["EXPERIENCED_FULL"][key],maps["FRESH_FULL"][key]),
        delta_time=maps["EXPERIENCED_FULL"][key]["censored_time"]-maps["FRESH_FULL"][key]["censored_time"],
        delta_actions=maps["EXPERIENCED_FULL"][key]["censored_actions"]-maps["FRESH_FULL"][key]["censored_actions"],
        delta_J=maps["EXPERIENCED_FULL"][key]["J"]-maps["FRESH_FULL"][key]["J"]) for key in sorted(keys)]
    return dict(summaries=summaries,gates=gates,paired_wins=wins,paired_cases=len(keys),paired=paired)


def stage2_mechanism(row,output):
    detail=json.loads((output/row["trajectory_reference"]).read_text(encoding="utf-8"))
    initial=detail["trajectory"][0]
    resource=next((r for r in detail["trajectory"] if r["resources"]),None)
    # The declared Stage 2 task is north: no coordinate rule reaches the organism.
    first_move=next((d for d in detail["decisions"] if ActionType(d["action"]).name.startswith("MOVE_")),None)
    if first_move is None: return dict(passed=False,reason="no autonomous MOVE decision")
    plan=first_move["plan"];actions=plan["actions"] if plan else []
    chain=bool(actions and actions[0]=="MOVE_UP" and "INTERACT_UP" in actions[1:])
    matching=[(a,b) for a,b in zip(detail["trajectory"],detail["trajectory"][1:])
              if b["actions"]>a["actions"] and b["completed_action"]=="MOVE_UP"]
    physical=bool(matching and matching[0][1]["energy"]<matching[0][0]["energy"]
                  and matching[0][1]["nutrients"]<=matching[0][0]["nutrients"])
    diagnostics=first_move["diagnostics"]
    predicted=bool(diagnostics.get("temporal",{}).get("usable") and diagnostics.get("homeostatic_plan_component",0)>0)
    return dict(passed=chain and physical and predicted,move_interact_chain=chain,physical_cost_without_nutrient_benefit=physical,
                delayed_prediction=predicted,first_move=first_move)


def analyze(protocol,result,output):
    thresholds=protocol.data["ACCEPTANCE"];stages={}
    for index in range(1,5):
        name=f"stage_{index}";rows=[r for r in result["trials"] if r["stage"]==name]
        stages[name]=compare(rows,thresholds,economy=index==4)
    training=[r for r in result["training"] if r["stage"]=="stage_1"]
    consumptions=sum(r["consumptions"] for r in training)
    end=training[-1]["evidence"]
    supported=[r for r in end["beneficial_relations"] if r["timing"] and r["support"]>=thresholds["timing_support"]]
    acquisition=dict(physical_consumptions=consumptions,nutrient_gain=sum(r["nutrient_gain"] for r in training),
        internal_bin_changes=sum(r["internal_bin_changes"] for r in training),
        timing_observations=end["timing_observations"],passive_timing_observations=end["passive_observations"],
        supported_beneficial_relations=supported,
        gates=dict(autonomous_discovery=consumptions>=thresholds["discovery_consumptions"],
                   physical_nutrient_consequence=sum(r["nutrient_gain"] for r in training)>0,
                   observed_bin_change=any(r["internal_bin_changes"]>0 for r in training),
                   learned_supported_consequence=bool(supported)))
    mechanisms=[dict(seed=r["seed"],scenario=r["scenario"],**stage2_mechanism(r,output))
                for r in result["trials"] if r["stage"]=="stage_2" and r["group"]=="EXPERIENCED_FULL"]
    stages["stage_1"]["gates"].update(acquisition["gates"])
    stages["stage_2"]["gates"]["model_chain"]=sum(r["passed"] for r in mechanisms)/len(mechanisms)>=thresholds["mechanistic_rate"]
    variants={}
    for scenario in sorted({r["scenario"] for r in result["trials"] if r["stage"]=="stage_3"}):
        comparison=compare([r for r in result["trials"] if r["stage"]=="stage_3" and r["scenario"]==scenario],thresholds)
        relevant=("minimum_cases","success_noninferiority","lower_median_time","lower_median_actions","paired_wins","practical_effect")
        comparison["passed"]=all(comparison["gates"][name] for name in relevant);variants[scenario]=comparison
    translated=[v["passed"] for k,v in variants.items() if "north_translated" in k]
    directions=[v["passed"] for k,v in variants.items() if "north_translated" not in k]
    stages["stage_3"]["gates"]=dict(translation_transfer=bool(translated) and all(translated),
        directional_transfer=sum(directions)>=thresholds["direction_classes"])
    for stage in stages.values():stage["passed"]=all(stage["gates"].values())
    counterfactual=dict(no_consumption=all(r["consumption_count"]==0 for r in result["counterfactual"]),
        no_external_nutrient_gain=True)
    for row in result["counterfactual"]:
        detail=json.loads((output/row["trajectory_reference"]).read_text(encoding="utf-8"))
        counterfactual["no_external_nutrient_gain"] &= all(b["nutrients"]<=a["nutrients"]+1e-9
            for a,b in zip(detail["trajectory"],detail["trajectory"][1:]))
    passed=all(s["passed"] for s in stages.values()) and all(counterfactual.values())
    return dict(verdict="PASS" if passed else "FAIL",stages=stages,acquisition=acquisition,
                stage2_mechanisms=mechanisms,generalization=variants,counterfactual=counterfactual,
                failure_modes=[name+": "+", ".join(k for k,v in stage["gates"].items() if not v)
                               for name,stage in stages.items() if not stage["passed"]])


def write_report(protocol,result,path):
    verdict=result["acceptance"]["verdict"]
    lines=["# v0.9.2 survival-learning research results", "", "Overall proof: **"+verdict+"**.", "",
        "Canonical protocol SHA-256: `"+protocol.checksum+"`.",
        "Software: `"+str(result["software"])+"`.", "Thresholds changed after first full run: **NO**.", "",
        "## Acquisition", "", "```json",json.dumps(result["acceptance"]["acquisition"],indent=2,sort_keys=True),"```", "",
        "## Behavior and economy", "",
        "| Stage | Group | N | Success | Median time | Median actions | Energy spent | Brownout | Median J |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name,stage in result["acceptance"]["stages"].items():
        for group,row in stage["summaries"].items():
            lines.append(f"| {name} | {group} | {row['n']} | {row['successes']} | {row['median_censored_time']:.6g} | {row['median_censored_actions']:.6g} | {row['median_energy_spent']:.6g} | {row['brownouts']} | {row['median_J']:.6g} |")
    lines += ["", "## Gates and causal ablations", ""]
    for name,stage in result["acceptance"]["stages"].items():
        lines += ["### "+name,"",f"Paired wins: {stage['paired_wins']}/{stage['paired_cases']}.","", "```json",json.dumps(stage["gates"],indent=2,sort_keys=True),"```", ""]
    lines += ["## Withheld generalization","", "| Variant | Fresh median time | Experienced median time | Result |","|---|---:|---:|---|"]
    for name,row in result["acceptance"]["generalization"].items():
        lines.append(f"| {Path(name).stem} | {row['summaries']['FRESH_FULL']['median_censored_time']:.6g} | {row['summaries']['EXPERIENCED_FULL']['median_censored_time']:.6g} | {'PASS' if row['passed'] else 'FAIL'} |")
    lines += ["", "## Stage 2 model evidence", "", "```json",json.dumps(result["acceptance"]["stage2_mechanisms"],indent=2,sort_keys=True),"```", "",
        "## Counterfactual", "", "```json",json.dumps(result["acceptance"]["counterfactual"],indent=2,sort_keys=True),"```", "",
        "## Paired effects (experienced minus fresh)","", "| Stage | Scenario | Seed | Win | Time delta | Action delta | J delta |","|---|---|---:|---|---:|---:|---:|"]
    for name,stage in result["acceptance"]["stages"].items():
        for row in stage["paired"]:
            lines.append(f"| {name} | {Path(row['scenario']).stem} | {row['seed']} | {row['experienced_win']} | {row['delta_time']:.6g} | {row['delta_actions']:.6g} | {row['delta_J']:.6g} |")
    lines += ["", "## Complete per-seed results", "", "| Stage | Scenario | Seed | Group | Success | Censored time | Censored actions | Energy spent | Brownout | J |", "|---|---|---:|---|---|---:|---:|---:|---|---:|"]
    for row in result["trials"]:
        lines.append(f"| {row['stage']} | {Path(row['scenario']).stem} | {row['seed']} | {row['group']} | {row['success']} | {row['censored_time']:.6g} | {row['censored_actions']} | {row['energy_spent']:.6g} | {row['brownout']} | {row['J']:.6g} |")
    lines += ["", "## Checkpoint provenance", "", "```json",json.dumps(result["checkpoints"],indent=2,sort_keys=True),"```", "",
        "Training seeds: "+str(protocol.data["PROTOCOL"]["training_seeds"])+".",
        "Evaluation seeds: "+str(protocol.data["PROTOCOL"]["evaluation_seeds"])+".", "",
        "## Interpretation and limits", "",
        "Static scenarios may produce identical trajectories across seeds because no stochastic physical spawning occurs; these are deterministic paired cases, not independent population statistics.",
        "First consumption requires disappearing nutritive resource, successful completed INTERACT and actual nutrient increase. Raw physiology and tracked IDs are measurement-only.",
        "J is midpoint-discounted trapezoidal integration of physical tension, with lambda=0.02; energy expenditure is the sum of positive sample-to-sample E declines, not net energy loss.",
        "Input checkpoint brains are reloaded independently for every experienced/ablated trial; evaluation learning is discarded. All declared seeds and failures are retained.", ""]
    if verdict=="PASS":
        lines += ["v0.9.2 establishes a narrow controlled survival-learning result: under the declared embodied curriculum and deterministic evaluation set, prior physical experience produced a reproducible advantage in homeostatic behavior over fresh controls, and that advantage was materially reduced by the relevant delayed-consequence and motivation ablations.","", "This is not a reward-learning result and not a claim of general intelligence. Food remained a human/editor label for a physical resource; cognition received ordinary sensory and interoceptive consequences only."]
    else:
        lines += ["v0.9.2 experiment infrastructure is implemented, but the predeclared survival-learning proof was not established.","", "No acceptance threshold or cognitive policy was changed to force a passing result. The failing stage/mechanism is documented as the next research blocker.","",*result["acceptance"]["failure_modes"]]
    lines += ["", "v0.9.3 remains long-run stability, boundedness and soak-test scope.", ""]
    Path(path).write_text("\n".join(lines),encoding="utf-8")
