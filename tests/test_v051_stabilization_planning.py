from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.memory import PersistentStructureMemory,PlaceMemory
from curriculum import TARGET_PATTERNS
from world.perception import BodySense,SensoryFrame

FRAME=SensoryFrame(0,4,(),BodySense(False,False,False,False,False,0.))

def test_target_enters_cognition_and_creates_persistent_goal_without_world_ids()->None:
    core=SyntheticEntityCore(Settings());goal=core.receive_target(TARGET_PATTERNS["pair"])
    assert goal.origin=="TARGET" and core.graph.nodes[goal.target_cognit_ids[0]].kind=="TARGET"
    # Target-only channels were intentionally replaced by the shared grounded relation language.
    assert all(x[2]=="spatial_relation" for x in goal.target_signature) and not hasattr(core,"world")
    for _ in range(40):core.step(FRAME);core.deliberate(FRAME)
    assert core.state.goal is not None

def test_planner_creates_real_subgoal_and_child_completion_resumes_parent()->None:
    core=SyntheticEntityCore(Settings(min_deliberation_cycles=1,max_deliberation_cycles=2));parent=core.receive_target(TARGET_PATTERNS["pair"])
    place=core.graph.add_cognit();memory_node=core.graph.add_cognit();core.memory.places[1]=PlaceMemory(1,place.id,(),.8)
    core.memory.structures[1]=PersistentStructureMemory(1,memory_node.id,(),place.id,(0.,0.),(),.8,last_recall_strength=.5)
    core.state.action_scores={a:0. for a in core.available_actions};core.planner.deliberate(core,set(),0)
    assert core.state.goal.parent_id==parent.id and core.state.subgoals_created==1
    core.planner.deliberate(core,{place.id},1)
    assert core.state.goal.id==parent.id and core.state.parent_resumptions==1 and core.state.subgoals_completed==1
