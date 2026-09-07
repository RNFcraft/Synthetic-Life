from config import Settings
from consciousness.cognit import Cognit
from consciousness.graph import CognitiveGraph
from consciousness.memory import PersistentStructureMemory
from consciousness.relational import BeliefScene,RelationalStructure
from consciousness.relation import RelationType
from curriculum import TARGET_PATTERNS
from simulation import Simulation
from world import Action,ActionType

def mem(i,p,t,confidence=.8):return PersistentStructureMemory(i,i,(),10,p,(),confidence,t)
def scene_for(points,confidence=.8):
    graph=CognitiveGraph();items=[]
    for i,p in enumerate(points,1):graph.add_cognit(Cognit(i));items.append(mem(i,p,0,confidence))
    scene=BeliefScene();scene.update(items,10,0,graph,{});return scene

def test_incompatible_historical_frames_do_not_create_relation()->None:
    graph=CognitiveGraph();graph.add_cognit(Cognit(1));graph.add_cognit(Cognit(2));scene=BeliefScene();scene.update((mem(1,(2.,1.),0),),10,0,graph,{});scene.update((mem(2,(1.,0.),1),),10,1,graph,{})
    target=RelationalStructure.from_points(((0,0),(1,0)));binding=scene.best_binding(target)
    assert not scene.relations and binding.unknown==1 and binding.satisfied==binding.violated==0

def test_coobservation_survives_loss_and_contradiction_is_recorded()->None:
    graph=CognitiveGraph();graph.add_cognit(Cognit(1));graph.add_cognit(Cognit(2));scene=BeliefScene();scene.update((mem(1,(0.,0.),0),mem(2,(1.,0.),0)),10,0,graph,{});old=next(iter(scene.relations.values()));scene.update((),10,1,graph,{});assert old in scene.relations.values()
    scene.update((mem(1,(0.,0.),2),mem(2,(3.,0.),2)),10,2,graph,{});assert old.contradictions==1 and old.confidence<.9

def test_confidence_changes_uncertainty_not_structural_geometry()->None:
    target=RelationalStructure.from_points(((0,0),(1,0)));high=scene_for(((0.,0.),(1.,0.)),.9);low=scene_for(((0.,0.),(1.,0.)),.3)
    assert high.mismatch(target)==low.mismatch(target)==0 and high.knowledge_uncertainty<low.knowledge_uncertainty

def test_all_targets_match_with_permuted_participants_and_extras()->None:
    for target in TARGET_PATTERNS.values():
        points=list(reversed(sorted(target.offsets)))+[(10,10),(15,3)];scene=scene_for(points);binding=scene.best_binding(RelationalStructure.from_points(target.offsets));assert binding.score==1.,target.name

def test_predicted_relations_preserve_endpoints_for_all_target_shapes()->None:
    for target in TARGET_PATTERNS.values():
        structure=RelationalStructure.from_points(target.offsets);scene=scene_for(tuple(reversed(sorted(target.offsets)))+((20,20),));extra=max(scene.participants);wanted={r.cognit_id for r in scene.relations.values() if extra not in (r.source_id,r.target_id)}
        assert scene.predicted_mismatch(structure,wanted)==0.,target.name
        if structure.participant_count>2:
            # A bag of correct-looking tokens on the wrong endpoint subgraph is
            # not a valid predicted future for the target roles.
            incomplete=set(sorted(wanted)[:-1]);assert scene.predicted_mismatch(structure,incomplete)>0.,target.name

def learned_physical_pair_effect():
    settings=Settings(object_count=0,perception_radius=4,relation_provisional_support=3,relation_provisional_lift=1.)
    sim=Simulation(11,settings);world=sim.world;core=sim.core
    for trial in range(8):
        # Controlled calibration forces an action, but both causal states come
        # only through normal perception of an actual World displacement.
        world.body.x,world.body.y,world.body.orientation=5,5,"NORTH"
        world.initialize_controlled_objects([(5,2),(5,4)])
        core.previous_action=None;core.step(world.perceive(2*trial))
        assert world.apply_action(Action(ActionType.MOVE_UP)).name=="SUCCESS"
        core.previous_action=ActionType.MOVE_UP;core.step(world.perceive(2*trial+1))
    bound={relation.cognit_id:relation for relation in core.belief_scene.relations.values()}
    effects=[]
    for edges in core.graph.adjacency.values():
        for rho in edges.values():
            before=bound.get(rho.source_id);after=bound.get(rho.target_id)
            if rho.relation_type is RelationType.SELF_ACTION and rho.context_id==ActionType.MOVE_UP.value and before and after and (before.source_id,before.target_id)==(after.source_id,after.target_id) and before.token!=after.token:
                effects.append((rho,before,after))
    return sim,max(effects,key=lambda item:item[0].support)

def test_physical_action_materializes_bound_effect_and_survives_evidence_clear()->None:
    sim,(rho,before,after)=learned_physical_pair_effect();core=sim.core
    assert before.token==(0,1,2) and after.token==(0,1,1) and rho.support>=3
    assert core.transitions.action_pair_counts[before.cognit_id,ActionType.MOVE_UP,after.cognit_id]>=3
    core.transitions.clear_evidence()
    assert core.predict_from_relations({before.cognit_id},ActionType.MOVE_UP).get(after.cognit_id,0)>=.25

def test_unsatisfied_bound_relation_creates_graph_native_stable_subgoal()->None:
    sim,(rho,before,after)=learned_physical_pair_effect();core=sim.core;parent=core.receive_target(TARGET_PATTERNS["pair"])
    core.belief_scene.new_episode()
    for participant_id in (before.source_id,before.target_id):core.belief_scene.participants[participant_id].episode=core.belief_scene.episode
    core.belief_scene.participants[before.source_id].relative_position=(0.,0.);core.belief_scene.participants[before.target_id].relative_position=(0.,2.)
    core.target_mismatch=core.belief_scene.mismatch(core.target_structure)
    assert core.belief_scene.last_binding.violated
    core.planner._manage_goals(core,{before.cognit_id},100);child=core.state.goal
    assert child.parent_id==parent.id and child.target_cognit_ids==(after.cognit_id,)
    created=core.state.subgoals_created;core.state.goal=parent;core.goal_stack.clear();core.planner._manage_goals(core,{before.cognit_id},101)
    assert core.state.subgoals_created==created
