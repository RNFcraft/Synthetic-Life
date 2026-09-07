from config import Settings
from consciousness.core import SyntheticEntityCore
from consciousness.memory import SpatialMemory
from consciousness.percepts import PersistentPercept
from consciousness.state import Goal
from world.actions import ActionType
from world.perception import BodySense,SensoryCell,SensoryFrame
from simulation import Simulation


def track(x=0,y=-1)->PersistentPercept:
    return PersistentPercept(1,((x,y,"occupied",1,1),),(x,y),frozenset({("occupied",1)}),(1,),1.,last_seen_tick=0)


def test_place_memory_birth_transition_and_no_coordinates()->None:
    core=SyntheticEntityCore(Settings(place_birth_visits=2));m=core.memory;obs=frozenset({(0,-1,"occupied",1,1)})
    assert not m.observe(obs,(),core.graph,0,None);active=m.observe(obs,(track(),),core.graph,1,ActionType.MOVE_UP)
    assert len(m.places)==1 and active and all(not hasattr(x,"x") and not hasattr(x,"world_position") for x in m.places.values())


def test_object_memory_persists_reactivates_confirms_and_contradicts()->None:
    core=SyntheticEntityCore(Settings(place_birth_visits=1));m=core.memory;obs=frozenset({(0,-1,"occupied",1,1)})
    m.observe(obs,(track(),),core.graph,0,None);memory=next(iter(m.structures.values()));initial=memory.confidence
    m.current_place_id=None;m.observe(frozenset(),(),core.graph,10,ActionType.MOVE_DOWN);assert memory.cognit_id in core.graph.nodes
    recalled=m.recall((memory.cognit_id,),core.graph,11);assert memory.cognit_id in recalled and memory.reactivations>0
    m.observe(obs,(track(),),core.graph,12,ActionType.MOVE_UP);assert memory.confidence>=initial
    m.observe(obs,(),core.graph,14,ActionType.IDLE);assert memory.contradictions>0


def test_deliberation_does_not_step_world_is_bounded_and_builds_plan()->None:
    sim=Simulation(3,Settings(object_count=0,min_deliberation_cycles=2,max_deliberation_cycles=4,planning_horizon=3));frame=sim.world.perceive(0);sim.core.step(frame);before=sim.world.to_dict();sim.core.deliberate(frame)
    assert sim.world.to_dict()==before and 2<=sim.core.planner.cycles_last<=4
    assert sim.core.planner.plan is not None and len(sim.core.planner.plan.actions)<=3


def test_plan_revalidation_and_subgoal_shape()->None:
    sim=Simulation(4,Settings(object_count=0));sim.step();old=sim.core.planner.plan;sim.step()
    assert sim.core.planner.plan is not None and sim.core.planner.plan is not old
    child=Goal(2,(1,),1.,.5,.5,parent_id=1,depth=1);assert child.parent_id==1 and child.depth==1
