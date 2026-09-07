"""Export deterministic primitive equivalence data from frozen Python v0.5.1."""
from pathlib import Path
from config import Settings
from simulation import Simulation
from world import Action,ActionType
from consciousness.cognit import Cognit
from consciousness.relation import RelationType

def main():
    sim=Simulation(1,Settings(object_count=0,perception_radius=4));w=sim.world;w.body.x,w.body.y,w.body.orientation=5,5,"NORTH";w.initialize_controlled_objects([(5,2),(5,4)])
    frame=w.perceive(0);occupied=sorted((c.relative_x,c.relative_y) for c in frame.cells if c.occupied);result=w.apply_action(Action(ActionType.MOVE_UP))
    core=sim.core;source=core.graph.add_cognit(Cognit(core.graph.next_id,activity=1.)).id;target=core.graph.add_cognit().id;rho,_=core.graph.connect(source,target,RelationType.SELF_ACTION,ActionType.MOVE_UP.value);rho.strength=rho.prediction_probability=1.;rho.confidence=.75
    prediction=core.predict_from_relations({source},ActionType.MOVE_UP)[target]
    lines=["# Frozen Python v0.5.1 primitive fixture","WORLD 30 30 4 5 5 N 2 5 2 5 4",f"FRAME 0 {len(occupied)} "+" ".join(f"{x} {y}" for x,y in occupied),f"ACTION {ActionType.MOVE_UP.value} {result.name} {w.body.x} {w.body.y} "+" ".join(f"{o.x} {o.y}" for o in w.objects),f"PREDICT {source-1} {ActionType.MOVE_UP.value} {target-1} {prediction:.9f}"]
    Path("cpp/fixtures/oracle_v051.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__":main()
