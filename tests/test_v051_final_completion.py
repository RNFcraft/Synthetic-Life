from pathlib import Path
from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.memory import PersistentStructureMemory
from consciousness.relational import RelationalStructure,observed_structure
from curriculum import TARGET_PATTERNS
from simulation import Simulation
from simulation import MultiEntitySimulation
from telemetry import SocialTelemetry
from world import Action
from world.objects import WorldObject
from world import ActionType
from world.perception import BodySense,SensoryFrame

def observation(points):return frozenset((x,y,"occupied",1,0) for x,y in points)

def test_current_and_target_share_translation_invariant_relations()->None:
    target=RelationalStructure.from_points(TARGET_PATTERNS["pair"].offsets);a=observed_structure(observation(((0,0),(1,0))));b=observed_structure(observation(((5,7),(6,7))))
    assert a.relations==target.relations==b.relations and a.match(target)==1

def test_target_mismatch_orders_partial_far_complete_without_world_truth()->None:
    target=RelationalStructure.from_points(TARGET_PATTERNS["pair"].offsets)
    complete=1-observed_structure(observation(((0,0),(1,0)))).match(target);far=1-observed_structure(observation(((0,0),(3,0)))).match(target);partial=1-observed_structure(observation(((0,0),))).match(target)
    assert complete<far<partial and not hasattr(target,"world")

def test_untried_context_has_value_and_no_effect_reduces_it()->None:
    core=SyntheticEntityCore(Settings());context={1,2};before=core.affordances.epistemic(context,ActionType.GRAB_UP)
    for _ in range(5):core.affordances.observe(context,ActionType.GRAB_UP,False,0.)
    assert core.affordances.epistemic(context,ActionType.GRAB_UP)<before and ActionType.GRAB_UP in core.available_actions

def test_effectful_context_is_distinct_but_not_target_value_policy()->None:
    core=SyntheticEntityCore(Settings());near={1,2};empty={9}
    for _ in range(4):core.affordances.observe(near,ActionType.GRAB_UP,True,.8);core.affordances.observe(empty,ActionType.GRAB_UP,False,0.)
    core.affordances.epistemic(near,ActionType.GRAB_UP);near_effect=core.affordances.last_effect_probability[ActionType.GRAB_UP];core.affordances.epistemic(empty,ActionType.GRAB_UP);empty_effect=core.affordances.last_effect_probability[ActionType.GRAB_UP]
    assert near_effect>empty_effect and core.affordances.predicted_progress(near,ActionType.GRAB_UP)==0

def test_target_retrieval_prefers_structurally_relevant_memory()->None:
    core=SyntheticEntityCore(Settings());target=RelationalStructure.from_points(((0,0),(1,0)));ms=core.memory
    ms.structures={1:PersistentStructureMemory(1,1,(),10,(0.,0.),(),.8),2:PersistentStructureMemory(2,2,(),10,(1.,0.),(),.8),3:PersistentStructureMemory(3,3,(),11,(0.,0.),(),.8)}
    ms.recall((),core.graph,1,target);assert ms.structures[1].last_recall_strength>ms.structures[3].last_recall_strength

def test_cognitive_clock_advances_without_world_or_memory_aging(tmp_path)->None:
    sim=Simulation(401,Settings(object_count=0,min_deliberation_cycles=3,max_deliberation_cycles=3));frame=sim.world.perceive(0);sim.core.step(frame);world_before=sim.world.to_dict();memory_before=[m.confidence for m in sim.core.memory.structures.values()];ct=sim.core.cognitive_tick
    sim.core.deliberate(frame);assert sim.clock.tick==0 and sim.world.to_dict()==world_before and sim.core.cognitive_tick>=ct+3 and [m.confidence for m in sim.core.memory.structures.values()]==memory_before
    path=tmp_path/"clock.seworld";sim.save_world(path);loaded=Simulation.load_world(path);assert loaded.core.cognitive_tick==sim.core.cognitive_tick

def test_brain_transfer_resets_current_place_but_preserves_history(tmp_path)->None:
    sim=Simulation(402,Settings(place_birth_visits=1));sim.step();assert sim.core.memory.places;path=tmp_path/"transfer.sebrain";sim.save_brain(path);fresh=Simulation(999);fresh.load_brain(path)
    assert fresh.core.memory.places and fresh.core.memory.current_place_id is None

def test_same_other_structure_reidentified_not_global_reactivation()->None:
    sim=MultiEntitySimulation(2,403,Settings(object_count=0,place_birth_visits=1));a,b=sim.world.bodies.values();a.x,a.y,a.orientation=5,5,"EAST";b.x,b.y=7,5;core=sim.cores[0]
    for tick in (0,1):frame=sim.world.perceive(tick,0);core.step(frame);sim.social.observe(0,frame,core)
    b.x=20
    for tick in (2,3):frame=sim.world.perceive(tick,0);core.step(frame);sim.social.observe(0,frame,core)
    b.x=7;frame=sim.world.perceive(4,0);core.step(frame);before=core.memory.reactivation_count;sim.social.observe(0,frame,core)
    assert sim.social.other_reidentifications==1 and sim.social.other_reidentifications!=before

def test_joint_metric_requires_shared_object_context()->None:
    sim=MultiEntitySimulation(2,404,Settings(object_count=0));a,b=sim.world.bodies.values();a.x,a.y=5,5;b.x,b.y=7,5;sim.world.objects=[WorldObject(1,6,5)];metric=SocialTelemetry()
    metric.observe_intents(0,{0:Action(ActionType.GRAB_RIGHT)},sim.world);metric.observe_intents(1,{1:Action(ActionType.GRAB_LEFT)},sim.world)
    assert metric.joint_object_interactions==1
    sim.world.objects=[WorldObject(2,5,4),WorldObject(3,7,4)];metric.observe_intents(2,{0:Action(ActionType.GRAB_UP),1:Action(ActionType.GRAB_UP)},sim.world);assert metric.joint_object_interactions==1
