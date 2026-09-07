"""Final small boundary check for the frozen v0.5.1 Python oracle."""
from pathlib import Path
import json
from experiments.v051_causal_validation import SETTINGS,train
from simulation import Simulation
from curriculum import TARGET_PATTERNS

CASES=(
 ("translated_vertical",((8,2),(8,4)),(8,5,"NORTH"),True),
 ("horizontal_mirror",((4,8),(6,8)),(3,8,"EAST"),False),
 ("approach_from_south_orientation",((10,7),(10,9)),(10,6,"SOUTH"),False),
 ("irrelevant_distractor",((12,2),(12,4),(15,3)),(12,5,"NORTH"),True),
 ("distance_three_two_interventions",((16,1),(16,4)),(16,5,"NORTH"),False),
)

def pair_distance(sim):
    points={o.id:o.position for o in sim.world.objects}
    for body_id,obj in sim.world.held_objects.items():points[obj.id]=sim.world.bodies[body_id].position
    a,b=points[1],points[2];return abs(a[0]-b[0])+abs(a[1]-b[1])

def main():
    out=Path("runs/v051-generalization");out.mkdir(parents=True,exist_ok=True);brain=out/"oracle.sebrain";trained=train(512);trained.save_brain(brain);rows=[]
    for index,(name,positions,body,represented_transfer) in enumerate(CASES):
        sim=Simulation(800+index,SETTINGS);sim.load_brain(brain);sim.core.belief_scene.new_episode();sim.world.body.x,sim.world.body.y,sim.world.body.orientation=body;sim.world.initialize_controlled_objects(list(positions));sim.core.receive_target(TARGET_PATTERNS["pair"])
        initial=minimum=pair_distance(sim);first=None;trajectory=[]
        for tick in range(30):
            metric=sim.step();d=pair_distance(sim);trajectory.append({"tick":tick,"action":metric.action,"distance":d});minimum=min(minimum,d)
            if d<initial and first is None:first=tick
            if d==1:break
        rows.append({"case":name,"represented_transfer_expected":represented_transfer,"success":pair_distance(sim)==1,"initial_distance":initial,"minimum_distance":minimum,"first_useful_action":first,"actions":len(trajectory),"trajectory":trajectory})
    result={"version":"v0.5.1","seed":512,"budget_per_case":30,"cases":rows};(out/"result.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps([{k:r[k] for k in ("case","represented_transfer_expected","success","minimum_distance","first_useful_action","actions")} for r in rows],indent=2))

if __name__=="__main__":main()
