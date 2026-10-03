"""Strict declarative curriculum v1; no executable fields or dynamic policy."""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from simulation.scenario import canonical_json, exact, integer, number, text, load_scenario

ROOT = Path(__file__).resolve().parents[2]
GROUPS = {
    "FRESH_FULL": {}, "EXPERIENCED_FULL": {},
    "EXPERIENCED_NO_DELAYED": {"delayed_homeostatic_prediction_enabled": False},
    "EXPERIENCED_NO_MOTIVATION": {"homeostatic_valuation_enabled": False},
}
ACCEPTANCE_FIELDS = ("minimum_cases", "paired_win_rate", "practical_ratio", "economy_ratio",
                     "ablation_reduction", "direction_classes", "discovery_consumptions",
                     "timing_support", "mechanistic_rate")


def scenario_path(value):
    text(value, 512, "curriculum scenario", True)
    path = ROOT / value
    if not path.resolve().is_relative_to((ROOT / "scenarios/v092").resolve()) or path.suffix != ".sescenario":
        raise ValueError("invalid curriculum scenario path")
    if not path.is_file(): raise ValueError("missing curriculum scenario")
    return path.resolve()


def validate(data):
    exact(data, ("META", "PROTOCOL", "STAGES", "ACCEPTANCE"), "curriculum")
    meta, protocol = data["META"], data["PROTOCOL"]
    exact(meta, ("schema", "version", "name", "description"), "curriculum metadata")
    if meta["schema"] != "synthetic-life-curriculum" or type(meta["version"]) is not int or meta["version"] != 1:
        raise ValueError("unsupported curriculum schema/version")
    text(meta["name"],256,"curriculum name",True); text(meta["description"],4096,"curriculum description")
    exact(protocol, ("backend", "evaluation_discount", "training_seeds", "evaluation_seeds",
                     "groups", "counterfactual", "counterfactual_horizon", "determinism_seeds"), "protocol")
    if protocol["backend"] != "native": raise ValueError("native production backend required")
    number(protocol["evaluation_discount"],0,10,"evaluation discount")
    for label in ("training_seeds","evaluation_seeds","determinism_seeds"):
        seeds=protocol[label]
        if not isinstance(seeds,list) or not 1 <= len(seeds) <= 64: raise ValueError("invalid seed set")
        for seed in seeds: integer(seed,0,2**63-1,"curriculum seed")
        if len(set(seeds)) != len(seeds): raise ValueError("duplicate curriculum seeds")
    if set(protocol["training_seeds"]) & set(protocol["evaluation_seeds"]): raise ValueError("training/evaluation seed overlap")
    if not set(protocol["determinism_seeds"]) <= set(protocol["evaluation_seeds"]): raise ValueError("invalid determinism seed subset")
    if protocol["groups"] != GROUPS or any(type(v) is not bool for flags in protocol["groups"].values() for v in flags.values()):
        raise ValueError("unsupported group/ablation override")
    number(protocol["counterfactual_horizon"],.001,120,"counterfactual horizon")
    load_scenario(scenario_path(protocol["counterfactual"]))
    stages=data["STAGES"]
    if not isinstance(stages,list) or len(stages)!=4: raise ValueError("four stages required")
    evaluation_paths=set(); training_paths=set()
    for index,stage in enumerate(stages,1):
        exact(stage,("id","training","evaluation","checkpoint"),"stage")
        if stage["id"] != f"stage_{index}": raise ValueError("stage order invalid")
        expected=("stage1_experienced","stage2_experienced","stage2_experienced","stage3_consolidated")[index-1]
        if stage["checkpoint"]!=expected:
            raise ValueError("invalid stage checkpoint name")
        for kind in ("training","evaluation"):
            entries=stage[kind]
            if not isinstance(entries,list) or len(entries)>16 or (kind=="evaluation" and not entries): raise ValueError("invalid stage cases")
            seen=set()
            for entry in entries:
                exact(entry,("scenario","horizon","episodes") if kind=="training" else ("scenario","horizon"),"stage case")
                number(entry["horizon"],.001,120,"episode horizon")
                load_scenario(scenario_path(entry["scenario"]))
                if entry["scenario"] in seen:raise ValueError("duplicate stage scenario")
                seen.add(entry["scenario"])
                if kind=="training":
                    integer(entry["episodes"],1,128,"episode count");training_paths.add(entry["scenario"])
                else: evaluation_paths.add(entry["scenario"])
    if not stages[0]["training"]:raise ValueError("initial autonomous training is required")
    if stages[2]["training"]: raise ValueError("Stage 3 must be withheld evaluation")
    withheld={entry["scenario"] for entry in stages[2]["evaluation"]}
    if withheld & training_paths: raise ValueError("withheld variants trained")
    if sum(row["episodes"] for stage in stages for row in stage["training"]) > 256:
        raise ValueError("training budget exceeded")
    acceptance=data["ACCEPTANCE"];exact(acceptance,ACCEPTANCE_FIELDS,"acceptance")
    for name in ("paired_win_rate","practical_ratio","economy_ratio","ablation_reduction","mechanistic_rate"):
        number(acceptance[name],.001,1,name)
    for name,low,high in (("minimum_cases",12,64),("direction_classes",3,3),("discovery_consumptions",1,256),("timing_support",1,10000)):
        integer(acceptance[name],low,high,name)
    if len(protocol["evaluation_seeds"]) < acceptance["minimum_cases"]: raise ValueError("insufficient evaluation cases")
    return data


@dataclass(frozen=True,slots=True)
class Curriculum:
    canonical: str
    def __post_init__(self):
        normalized=validate(json.loads(self.canonical,object_pairs_hook=_unique_pairs))
        object.__setattr__(self,"canonical",canonical_json(normalized))
    @property
    def data(self): return json.loads(self.canonical)
    @property
    def checksum(self): return sha256(self.canonical.encode()).hexdigest()


def _unique_pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError("duplicate curriculum field")
        result[key]=value
    return result


def load_protocol(path):
    raw=Path(path).read_bytes()
    if len(raw)>65536: raise ValueError("curriculum size limit exceeded")
    data=json.loads(raw,object_pairs_hook=_unique_pairs)
    return Curriculum(canonical_json(data))


def save_protocol(data,path):
    protocol=Curriculum(canonical_json(data))
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(protocol.canonical+"\n",encoding="utf-8")
    return protocol
