"""Generate the predeclared physical task family, without cognitive tuning."""
from dataclasses import replace
from pathlib import Path
import json

from config import Settings
from simulation.persisted_settings import scenario_configuration
from simulation.scenario import ScenarioDefinition, save_scenario, artifact_checksum
from .protocol import GROUPS, ROOT, save_protocol


def scenario(name,body=(3,3),direction=(0,-1),distance=1,identifier=101,size=7,spawning=False,counterfactual=False):
    settings=replace(Settings(),world_width=size,world_height=size,object_count=1 if counterfactual else 0,
        max_objects=1 if counterfactual else 0,resource_max_live=2,resource_nutrient_payload=40.,resource_hydration_payload=0.,
        resource_spawning_enabled=spawning,resource_spawn_interval_seconds=6.,
        interoception_enabled=True,homeostatic_valuation_enabled=True,delayed_homeostatic_prediction_enabled=True,
        physiology_initial_energy=45.,physiology_initial_nutrients=12.,physiology_initial_hydration=80.,
        physiology_basal_body_rate=.3,physiology_basal_brain_rate=.1,physiology_hydration_rate=.08,
        physiology_digestion_rate=2.5,physiology_digestion_efficiency=.75,
        physiology_movement_cost=.2,physiology_interaction_cost=.1)
    x,y=body;dx,dy=direction
    return ScenarioDefinition.from_sections({
        "META":dict(schema="synthetic-life-scenario",version=1,name=name,description="Predeclared physical research initial condition",tags=[]),
        "CONFIG":dict(seed=92001,settings=scenario_configuration(settings)),
        "INITIAL":dict(bodies=[dict(id=0,x=x,y=y,orientation="NORTH",appearance=1)],
            objects=[dict(id=identifier,x=x+dx*distance,y=y+dy*distance,state=1,
                          resource_channel=0 if counterfactual else 1,nutrients=0. if counterfactual else 40.,hydration=0.)],
            held_objects=[],physiology=dict(energy=45.,nutrients=12.,hydration=80.))})


def generate():
    definitions={
        "train_adjacent_north":scenario("Canonical adjacent training"),
        "stage1_adjacent_north":scenario("Adjacent evaluation",identifier=1001),
        "train_one_move_north":scenario("Canonical one-move training",distance=2),
        "stage2_one_move_north":scenario("One-move evaluation",distance=2,identifier=2001),
        "stage3_east_a":scenario("Withheld east",body=(2,2),direction=(1,0),distance=2,identifier=3001),
        "stage3_south_a":scenario("Withheld south",body=(4,2),direction=(0,1),distance=2,identifier=3011),
        "stage3_west_a":scenario("Withheld west",body=(5,4),direction=(-1,0),distance=2,identifier=3021),
        "stage3_north_translated":scenario("Withheld translated north",body=(1,5),distance=2,identifier=3031),
        "stage4_scarcity_a":scenario("Scarcity A",distance=2,identifier=4001,spawning=True),
        "stage4_scarcity_b":scenario("Scarcity B",body=(4,5),distance=3,size=9,identifier=4011,spawning=True),
        "counterfactual_same_appearance":scenario("Same appearance zero payload",identifier=5001,counterfactual=True),
    }
    for name,delta in (("north",(0,-1)),("east",(1,0)),("south",(0,1)),("west",(-1,0))):
        definitions[f"train_consolidate_{name}"]=scenario(f"Consolidation {name}",direction=delta,distance=2,identifier=201)
    inventory=[]
    for name,definition in definitions.items():
        path=ROOT/"scenarios/v092"/(name+".sescenario");save_scenario(definition,path)
        inventory.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=artifact_checksum(path),
                              initial=definition.sections["INITIAL"],settings=definition.sections["CONFIG"]["settings"]))
    Path(ROOT/"scenarios/v092/inventory.json").write_text(json.dumps(inventory,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    path=lambda name:"scenarios/v092/"+name+".sescenario"
    train=lambda name,episodes,horizon:dict(scenario=path(name),episodes=episodes,horizon=horizon)
    evaluate=lambda name,horizon:dict(scenario=path(name),horizon=horizon)
    data={"META":dict(schema="synthetic-life-curriculum",version=1,name="v092 survival learning",description="Fixed autonomous protocol; no policy or threshold adaptation"),
          "PROTOCOL":dict(backend="native",evaluation_discount=.02,training_seeds=list(range(92001,92009)),
              evaluation_seeds=list(range(92101,92117)),groups=GROUPS,counterfactual=path("counterfactual_same_appearance"),
              counterfactual_horizon=9.,determinism_seeds=[92101,92102]),
          "STAGES":[
              dict(id="stage_1",training=[train("train_adjacent_north",32,6.)],evaluation=[evaluate("stage1_adjacent_north",6.)],checkpoint="stage1_experienced"),
              dict(id="stage_2",training=[train("train_one_move_north",48,9.)],evaluation=[evaluate("stage2_one_move_north",9.)],checkpoint="stage2_experienced"),
              dict(id="stage_3",training=[],evaluation=[evaluate("stage3_"+name,9.) for name in ("east_a","south_a","west_a","north_translated")],checkpoint="stage2_experienced"),
              dict(id="stage_4",training=[train("train_consolidate_"+name,8,9.) for name in ("north","east","south","west")],evaluation=[evaluate("stage4_scarcity_"+name,30.) for name in ("a","b")],checkpoint="stage3_consolidated")],
          "ACCEPTANCE":dict(minimum_cases=16,paired_win_rate=.75,practical_ratio=.8,economy_ratio=.85,ablation_reduction=.5,
                            direction_classes=3,discovery_consumptions=1,timing_support=6,mechanistic_rate=.75)}
    protocol=save_protocol(data,ROOT/"experiments/protocols/v092_survival.securriculum")
    print("Predeclared protocol SHA-256:",protocol.checksum)


if __name__=="__main__":generate()
