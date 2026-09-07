from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.cognit import Cognit
from consciousness.graph import CognitiveGraph
from consciousness.memory import PersistentStructureMemory
from consciousness.relational import BeliefScene,BoundSpatialRelation,RelationalStructure
from consciousness.relation import RelationType
from curriculum import TARGET_PATTERNS
from simulation import Simulation
from world import ActionType

def memories(points,tick=0):return [PersistentStructureMemory(i+1,i+1,(),10,p,(),.9,tick) for i,p in enumerate(points)]

def test_relational_edges_preserve_participants_and_out_of_view_belief()->None:
    graph=CognitiveGraph();[graph.add_cognit(Cognit(i+1)) for i in range(2)];scene=BeliefScene();nodes={};scene.update(memories(((0.,0.),(1.,0.))),10,0,graph,nodes);relation=next(iter(scene.relations.values()))
    assert (relation.source_id,relation.target_id)==(1,2) and graph.relation_count>0
    before=scene.mismatch(RelationalStructure.from_points(((0,0),(1,0))));scene.update((),10,1,graph,nodes)
    assert len(scene.participants)==2 and scene.mismatch(RelationalStructure.from_points(((0,0),(1,0))))==before

def test_role_binding_is_permutation_stable_and_ignores_extra_participants()->None:
    target=RelationalStructure.from_points(((0,0),(1,0)));graph=CognitiveGraph();[graph.add_cognit(Cognit(i+1)) for i in range(3)];scene=BeliefScene();scene.update(memories(((9.,9.),(1.,0.),(0.,0.))),10,0,graph,{})
    first=scene.best_binding(target);scene.participants=dict(reversed(list(scene.participants.items())));second=scene.best_binding(target)
    assert first.score==second.score==1. and set(first.role_to_participant)==set(second.role_to_participant)=={2,3}

def test_graph_predicted_bound_relation_reduces_mismatch()->None:
    core=SyntheticEntityCore(Settings());target=RelationalStructure.from_points(((0,0),(1,0)));core.target_structure=target
    for i in range(1,4):core.graph.add_cognit(Cognit(i,activity=1.))
    core.belief_scene.update(memories(((0.,0.),(3.,0.))),10,0,core.graph,core.relational_nodes);core.target_mismatch=core.belief_scene.mismatch(target)
    desired=BoundSpatialRelation(core.graph.add_cognit(Cognit(core.graph.next_id,kind="BOUND_RELATION")).id,1,2,target.relations[0],.9,0);core.belief_scene.relations[(1,2,target.relations[0])]=desired
    rho,_=core.graph.connect(3,desired.cognit_id,RelationType.SELF_ACTION,ActionType.MOVE_RIGHT.value);rho.strength=rho.prediction_probability=rho.confidence=1.
    assert core.predicted_target_progress({3},ActionType.MOVE_RIGHT)>0

def test_equivalent_subgoal_has_hysteresis()->None:
    core=SyntheticEntityCore(Settings());parent=core.receive_target(TARGET_PATTERNS["pair"]);place=core.graph.add_cognit();memory=core.graph.add_cognit();core.memory.structures[1]=PersistentStructureMemory(1,memory.id,(),place.id,(0.,0.),(),.8,last_recall_strength=.5)
    core.state.action_scores={a:0. for a in core.available_actions};core.planner._manage_goals(core,set(),0);created=core.state.subgoals_created;core.state.goal=parent;core.goal_stack.clear();core.planner._manage_goals(core,set(),1)
    assert core.state.subgoals_created==created

def test_controlled_initializer_has_valid_ids_and_baseline()->None:
    sim=Simulation(77,Settings(object_count=0));positions=[(1,1),(4,4),(8,8)];sim.world.initialize_controlled_objects(positions)
    assert [o.id for o in sim.world.objects]==[1,2,3] and sim.world.next_object_id==4 and sim.world.next_spawn_tick is None and sim.world.world_modification()==0

def test_brain_reload_reuses_relational_cognit_mapping(tmp_path)->None:
    sim=Simulation(78,Settings(object_count=0));sim.core.receive_target(TARGET_PATTERNS["pair"]);path=tmp_path/"r.sebrain";sim.save_brain(path);fresh=Simulation(79);fresh.load_brain(path);before=sum(n.kind=="RELATIONAL" for n in fresh.core.graph.nodes.values());fresh.core.receive_target(TARGET_PATTERNS["pair"]);after=sum(n.kind=="RELATIONAL" for n in fresh.core.graph.nodes.values())
    assert after==before
