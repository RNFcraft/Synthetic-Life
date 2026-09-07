from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.memory import PersistentStructureMemory
from consciousness.percepts import PersistentPercept
from world.actions import ActionType
from world.perception import BodySense,SensoryFrame

def obs(*items):return frozenset(items)
def track(feature=("occupied",1),centroid=(0.,-1.)):
    return PersistentPercept(1,(),centroid,frozenset({feature}),(feature[1],),1.)

def test_place_survives_orientation_change()->None:
    core=SyntheticEntityCore(Settings(place_birth_visits=1));m=core.memory
    first=obs((1,-1,"boundary",1,0));m.observe(first,(),core.graph,0,None);place=m.current_place_id
    rotated=obs((1,1,"boundary",1,0));m.observe(rotated,(),core.graph,1,ActionType.TURN_RIGHT)
    assert m.current_place_id==place and len(m.places)==1 and len(m.places[place].views)>=1

def test_place_uses_transition_evidence_and_similar_views_can_split()->None:
    core=SyntheticEntityCore(Settings(place_birth_visits=1));m=core.memory;s=obs((0,-1,"boundary",1,0))
    m.observe(s,(),core.graph,0,None);a=m.current_place_id;m.current_place_id=None
    m.observe(s,(),core.graph,1,None);assert m.current_place_id==a
    different=obs((2,-2,"boundary",1,0));m.current_place_id=a;m.observe(different,(),core.graph,2,ActionType.MOVE_RIGHT)
    assert len(m.places)==2

def test_confidence_affects_recall_strength_and_weak_memory_survives()->None:
    core=SyntheticEntityCore(Settings());m=core.memory
    high=PersistentStructureMemory(1,1,(),2,(0.,0.),(),.9);low=PersistentStructureMemory(2,3,(),2,(0.,0.),(),.2)
    m.structures={1:high,2:low};m.recall((1,3),core.graph,2)
    assert high.last_recall_strength>low.last_recall_strength and 2 in m.structures

def test_internal_cycle_changes_cognition_without_world()->None:
    core=SyntheticEntityCore(Settings(min_deliberation_cycles=3,max_deliberation_cycles=4,object_count=0));frame=SensoryFrame(0,4,(),BodySense(False,False,False,False,False,0.))
    core.step(frame);before=(core.planner.internal_tick,dict(core.state.action_scores));core.deliberate(frame)
    assert core.planner.internal_tick>before[0] and 3<=core.planner.cycles_last<=4 and core.state.action_scores
