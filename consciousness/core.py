from collections import defaultdict,deque
from dataclasses import dataclass
from math import prod,sqrt
from config import Settings
from world.actions import Action,ActionType
from world.perception import SensoryFrame
from .cognit import Cognit
from .calibration import CalibrationTracker
from .choice import SymmetryPreservingTieResolver
from .composites import CompositeTracker
from .graph import CognitiveGraph
from .learning import TransitionModel
from .patterns import CognitPattern,PrimitiveKey
from .relation import RelationStatus,RelationType
from .sensory import SensoryPatternTracker
from .percepts import PerceptualContinuityEngine
from .memory import SpatialMemory
from .planning import DeliberativePlanner,DeliberationSession
from .relational import BeliefScene,RelationalStructure,observed_structure
from .affordance import AffordanceEvidence
from .state import ConsciousnessState,FutureEstimate,Goal,TraceEntry,WorkingTrace
from .wave import ActivityWaveEngine,WaveResult


@dataclass(slots=True)
class ContinuousCognitionFrontier:
    generation:int;world_time:float;frame:SensoryFrame;current:set[int];track_ids:tuple[int,...];session:DeliberationSession|None=None;phase:str="OBSERVED";action:ActionType|None=None;committed:bool=False

class SyntheticEntityCore:
    """v0.2 cognitive loop. It consumes sensory values and returns an action only."""
    def __init__(self,settings:Settings,backend:str="python")->None:
        self.settings=settings
        if backend not in {"python","native"}:raise ValueError("backend must be 'python' or 'native'")
        self.backend_name=backend
        if backend=="native":
            from .backends import NativeGraphBackend
            from .native_graph import NativeGraphFacade
            self.backend=NativeGraphBackend(settings);self.graph=NativeGraphFacade(self.backend)
        else:self.backend=None;self.graph=CognitiveGraph()
        self.patterns=SensoryPatternTracker(settings);self.wave=ActivityWaveEngine(settings)
        self.transitions=TransitionModel(settings.relation_evidence_window);self.trace=WorkingTrace(settings.working_memory_size);self.state=ConsciousnessState()
        self.perception=PerceptualContinuityEngine(settings);self.composites=CompositeTracker(settings);self.memory=SpatialMemory(settings);self.planner=DeliberativePlanner(settings)
        self.tie_resolver=SymmetryPreservingTieResolver(settings.action_tie_epsilon);self.calibration=CalibrationTracker(settings.calibration_window)
        self.pattern_nodes:dict[tuple[PrimitiveKey,...],int]={};self.primitive_index:dict[PrimitiveKey,set[int]]=defaultdict(set)
        self.previous_active:set[int]=set();self.previous_action:ActionType|None=None
        self.last_wave=WaveResult(frozenset(),0.0,0);self.events:list[str]=[];self.next_goal_id=1
        self.dirty_cognits:set[int]=set();self.deletion_candidates:deque[int]=deque();self.lifecycle_cursor=0
        self.relation_prediction_enabled=True;self.predictions_without_composites:dict[int,float]={}
        self.available_actions:tuple[ActionType,...]=tuple(ActionType)
        self.relation_candidates=0;self.relations_materialized=0;self.candidate_supports:deque[int]=deque(maxlen=4096);self.candidate_lifts:deque[float]=deque(maxlen=4096)
        self.goal_stack:list[Goal]=[];self.target_cognit_ids:set[int]=set()
        self.current_structure=RelationalStructure(0,());self.target_structure:RelationalStructure|None=None;self.target_mismatch=1.;self.previous_target_mismatch=1.;self.relational_nodes={};self.affordances=AffordanceEvidence();self.previous_context=frozenset();self.previous_body_signature=()
        self.belief_scene=BeliefScene();self.target_knowledge_uncertainty=1.
        self.cognitive_tick=0
        self.world_time_seconds:float|None=None
        self._selectivity_sum=0.;self._selectivity_count=0
        self.continuous_frontier:ContinuousCognitionFrontier|None=None
    def _propagate(self,seeds:set[int],tick:int)->WaveResult:
        return self.backend.propagate_graph(self.graph,seeds,tick) if self.backend else self.wave.propagate(self.graph,seeds,tick)

    def receive_target(self,target)->Goal:
        """Convert a relational target description into ordinary graph substrate."""
        self.target_structure=RelationalStructure.from_points(target.offsets);signature=tuple((x,y,"spatial_relation",d,0) for x,y,d in self.target_structure.relations)
        pattern=CognitPattern(signature,occurrence_count=1,stability=1.,predictive_value=0.,is_translation_tolerant=True)
        node=self.graph.add_cognit(Cognit(self.graph.next_id,pattern=pattern,kind="TARGET",confidence=1.))
        for token in self.target_structure.relations:
            if token not in self.relational_nodes:self.relational_nodes[token]=self.graph.add_cognit(Cognit(self.graph.next_id,kind="RELATIONAL",confidence=1.)).id
            relation,_=self.graph.connect(node.id,self.relational_nodes[token],RelationType.ASSOCIATIVE);relation.strength=relation.prediction_probability=1.;relation.confidence=1.;relation.support+=1
        self.pattern_nodes[signature]=node.id;self.target_cognit_ids.add(node.id)
        goal=Goal(self.next_goal_id,(node.id,),1.,1.,1.,persistence=1.,origin_tension=1.,origin="TARGET",target_signature=signature)
        self.next_goal_id+=1;self.state.goals_generated+=1;self.state.goal=goal;self.events.append(f"TARGET_RECEIVED G{goal.id}");return goal

    def step(self,frame:SensoryFrame,world_time:float|None=None)->Action:
        return self._observe(frame,world_time,True)

    def _observe(self,frame:SensoryFrame,world_time:float|None,commit:bool,generation:int=0):
        self.world_time_seconds=world_time;self.memory.set_world_time(world_time)
        if world_time is not None and self.backend:self.backend.begin_continuous_time(world_time)
        self.events=[];self.cognitive_tick+=1;cognitive_tick=self.cognitive_tick
        observation,protos=self.patterns.observe(frame,self.state.representation_coverage,self.state.predictions)
        tracks=self.perception.update(self.patterns.last_events,frame.tick,self.previous_action)
        self.current_structure=observed_structure(observation);self.previous_target_mismatch=self.target_mismatch
        memory_active=self.memory.observe(observation,tracks,self.graph,frame.tick,self.previous_action)
        relational_active=set()
        for token in self.current_structure.relations:
            if token not in self.relational_nodes:self.relational_nodes[token]=self.graph.add_cognit(Cognit(self.graph.next_id,kind="RELATIONAL",confidence=self.current_structure.confidence)).id
            relational_active.add(self.relational_nodes[token])
        current_place=self.memory.places.get(self.memory.current_place_id).cognit_id if self.memory.current_place_id in self.memory.places else None
        bound_active=self.belief_scene.update(self.memory.structures.values(),current_place,frame.tick,self.graph,self.relational_nodes);relational_active.update(bound_active);self.target_mismatch=self.belief_scene.mismatch(self.target_structure) if self.target_structure else 1.;self.target_knowledge_uncertainty=self.belief_scene.knowledge_uncertainty
        matched=self._match_and_birth(observation,protos,cognitive_tick)
        recalled=self.memory.recall(self.state.goal.target_cognit_ids if self.state.goal else (),self.graph,frame.tick,self.target_structure);seeds=set(memory_active)|set(recalled)|relational_active
        if self.state.goal and self.state.goal.origin=="TARGET":seeds.update(self.state.goal.target_cognit_ids)
        if self.backend:self.backend.receive_batch([(node_id,self.settings.sensory_activation*.5) for node_id in seeds if node_id in self.graph.nodes],cognitive_tick,self.settings)
        else:
            for node_id in seeds:
                node=self.graph.nodes.get(node_id)
                if node:node.receive(self.settings.sensory_activation*.5,cognitive_tick,self.settings)
        if self.backend:
            states=self.backend.cognit_state_fields(matched,(7,8));operations=[]
            for node_id,match in matched.items():
                activity_trace,target_activity=states[node_id];homeostatic_gain=1.0/(1.0+self.settings.homeostasis_input_gain*activity_trace/max(target_activity,1e-6));operations.append((node_id,self.settings.sensory_activation*match*homeostatic_gain))
            for (node_id,_),active in zip(operations,self.backend.receive_batch(operations,cognitive_tick,self.settings)):
                if active:seeds.add(node_id)
        else:
            for node_id,match in matched.items():
                node=self.graph.nodes[node_id]
                homeostatic_gain=1.0/(1.0+self.settings.homeostasis_input_gain*node.activity_trace/max(node.target_activity,1e-6))
                stimulus=self.settings.sensory_activation*match*homeostatic_gain
                if node.receive(stimulus,cognitive_tick,self.settings):seeds.add(node_id)
        self.last_wave=self._propagate(seeds,cognitive_tick);current=set(self.last_wave.active_ids)
        composite_active,composite_births=self.composites.observe(current,self.graph)
        for pattern in composite_births[:self.settings.max_new_cognits_per_tick]:
            node=self.graph.add_cognit(Cognit(self.graph.next_id,pattern=pattern,target_activity=self.settings.homeostasis_target_activity));self.composites.register(pattern,node.id)
            self.events.append(f"COMPOSITE_CREATED κ{node.id}")
        composite_seeds=set()
        if self.backend:
            operations=[(node_id,self.settings.sensory_activation) for node_id in composite_active if node_id in self.graph.nodes]
            composite_seeds={node_id for (node_id,_),active in zip(operations,self.backend.receive_batch(operations,cognitive_tick,self.settings)) if active}
        else:
            for node_id in composite_active:
                if node_id in self.graph.nodes and self.graph.nodes[node_id].receive(self.settings.sensory_activation,cognitive_tick,self.settings):composite_seeds.add(node_id)
        if composite_seeds:
            extra=self._propagate(composite_seeds,cognitive_tick);current|=set(extra.active_ids)
            self.last_wave=WaveResult(frozenset(current),min(self.settings.max_wave_energy,self.last_wave.energy+extra.energy),self.last_wave.steps+extra.steps,self.last_wave.transmitted_energy+extra.transmitted_energy)
        self.dirty_cognits.update(matched);self.dirty_cognits.update(current)
        self._prediction_error(current);self._update_relation_outcomes(frame.tick,current)
        if self.backend and self.previous_action is not None:
            priority=lambda i:(0 if self.graph.nodes.get(i) and self.graph.nodes[i].kind=='BOUND_RELATION' else 1,i)
            before=[i-1 for i in sorted(self.previous_active,key=priority)];after=[i-1 for i in sorted(current,key=priority)]
            self.backend.update_transition_evidence(before,self.previous_action,after);self.backend.materialize(frame.tick,before,self.previous_action,after)
        elif not self.backend:
            self.transitions.observe(self.previous_active,self.previous_action,current);self._materialize_relations(frame.tick,current)
        self._update_intrinsic_state(current,matched,observation)
        self._update_goal(current)
        if not commit:
            self.continuous_frontier=ContinuousCognitionFrontier(generation,float(world_time),frame,current,tuple(t.id for t in tracks));return None
        self.state.futures=self._imagine(current);action=self._choose_action()
        if self.previous_action is not None and self.previous_context:
            body_sig=(frame.body.holding,frame.body.action_resistance>0,frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right);effect=body_sig!=self.previous_body_signature
            self.affordances.observe(self.previous_context,self.previous_action,effect,0.)
        self.state.predictions=dict(self.state.futures[action.kind].probabilities)
        self.predictions_without_composites=self._graph_predict(current,action.kind,exclude_composites=True)
        if self.backend:self.backend.cognit_state_fields(sorted(current),(0,))
        self.trace.append(TraceEntry(frame.tick,tuple((i,self.graph.nodes[i].activity) for i in sorted(current)),action.kind,
            tuple(sorted(self.state.predictions.items())),self.state.prediction_error,self.state.goal.id if self.state.goal else None,self.state.internal_tension,
            tuple(t.id for t in tracks),self.state.representation_error))
        self.state.loop_score=self.trace.loop_score(max_period=self.settings.loop_max_period,min_repeats=self.settings.loop_min_repeats)
        if self.backend:
            self.backend.engine.homeostatic_step([i-1 for i in current],self.settings.homeostasis_trace_decay,self.settings.homeostasis_learning_rate,self.settings.threshold_min,self.settings.threshold_max,self.settings.cognit_activity_decay,.999);self.backend.invalidate_state()
        else:
            for node in list(self.graph.nodes.values()):node.homeostatic_step(node.id in current,self.settings)
        self._prune(frame.tick);self.previous_active=current;self.previous_context=frozenset(current);self.previous_body_signature=(frame.body.holding,frame.body.action_resistance>0,frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right);self.previous_action=action.kind
        return action

    def begin_continuous_observation(self,frame:SensoryFrame,world_time:float,generation:int)->None:
        self._observe(frame,world_time,False,generation)

    def begin_continuous_cognition(self,generation:int)->bool:
        f=self.continuous_frontier
        if f is None or f.generation!=generation:return False
        if f.phase=="OBSERVED":f.session=self.planner.begin_continuous(self,set(f.current),f.frame.tick);f.phase="DELIBERATING"
        return True

    def continue_continuous_cognition(self,generation:int)->bool|None:
        f=self.continuous_frontier
        if f is None or f.generation!=generation:return None
        if f.phase!="DELIBERATING" or f.session is None:raise RuntimeError("invalid continuous cognition phase")
        quiet=self.planner.continue_continuous(self,f.session)
        if quiet:f.phase="QUIESCENT"
        return quiet

    def commit_continuous_action(self,generation:int)->Action|None:
        f=self.continuous_frontier
        if f is None or f.generation!=generation:return None
        if f.committed:return Action(f.action)
        if f.phase!="QUIESCENT" or f.session is None:raise RuntimeError("continuous cognition is not quiescent")
        kind=self.planner.finalize_continuous(self,f.session);current=set(self.planner.last_active);frame=f.frame
        if self.previous_action is not None and self.previous_context:
            body_sig=(frame.body.holding,frame.body.action_resistance>0,frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right);effect=body_sig!=self.previous_body_signature;self.affordances.observe(self.previous_context,self.previous_action,effect,0.)
        self.state.predictions=self._graph_predict(current,kind);self.predictions_without_composites=self._graph_predict(current,kind,exclude_composites=True)
        if self.backend:self.backend.cognit_state_fields(sorted(current),(0,))
        self.trace.append(TraceEntry(frame.tick,tuple((i,self.graph.nodes[i].activity) for i in sorted(current)),kind,tuple(sorted(self.state.predictions.items())),self.state.prediction_error,self.state.goal.id if self.state.goal else None,self.state.internal_tension,f.track_ids,self.state.representation_error))
        self.state.loop_score=self.trace.loop_score(max_period=self.settings.loop_max_period,min_repeats=self.settings.loop_min_repeats)
        if self.backend:self.backend.engine.homeostatic_step([i-1 for i in current],self.settings.homeostasis_trace_decay,self.settings.homeostasis_learning_rate,self.settings.threshold_min,self.settings.threshold_max,self.settings.cognit_activity_decay,.999);self.backend.invalidate_state()
        else:
            for node in list(self.graph.nodes.values()):node.homeostatic_step(node.id in current,self.settings)
        self._prune(frame.tick);self.previous_active=current;self.previous_context=frozenset(current);self.previous_body_signature=(frame.body.holding,frame.body.action_resistance>0,frame.body.touch_up,frame.body.touch_down,frame.body.touch_left,frame.body.touch_right);self.previous_action=kind;self.planner.committed();f.action=kind;f.committed=True;f.phase="COMMITTED";return Action(kind)

    def deliberate(self,frame:SensoryFrame)->Action:
        """Advance bounded internal recall/planning without another World observation."""
        current=set(self.last_wave.active_ids);kind=self.planner.deliberate(self,current,frame.tick);current=set(self.planner.last_active);self.previous_action=kind
        if self.trace.entries:
            old=self.trace.entries.pop();self.trace.append(TraceEntry(old.tick,old.active,kind,old.prediction,old.prediction_error,old.goal_id,old.internal_tension,old.percept_ids,old.representation_error))
        self.state.predictions=self._graph_predict(current,kind);self.planner.committed();return Action(kind)

    def _match_and_birth(self,observation:frozenset[PrimitiveKey],protos:list, tick:int)->dict[int,float]:
        candidate_ids=set()
        for primitive in observation:candidate_ids.update(self.primitive_index.get(primitive,set()))
        matched={i:self.graph.nodes[i].pattern.match(observation) for i in candidate_ids if self.graph.nodes[i].pattern}
        matched={i:m for i,m in matched.items() if m>=self.settings.pattern_match_threshold}
        births=0
        for proto,score in sorted(protos,key=lambda item:(-item[1],item[0].translation_tolerant,item[0].participants)):
            signature=proto.participants
            if signature in self.pattern_nodes or score<self.settings.cognit_birth_threshold or proto.occurrences<self.settings.proto_min_occurrences:continue
            if births>=self.settings.max_new_cognits_per_tick or len(self.graph.nodes)>=self.settings.max_cognits:break
            pattern=CognitPattern(signature,occurrence_count=proto.occurrences,stability=proto.stability,predictive_value=proto.predictive_value,is_translation_tolerant=proto.translation_tolerant)
            node=self.graph.add_cognit(Cognit(self.graph.next_id,pattern=pattern,target_activity=self.settings.homeostasis_target_activity))
            self.pattern_nodes[signature]=node.id
            for primitive in signature:self.primitive_index[primitive].add(node.id)
            matched[node.id]=1.0;births+=1;self.events.append(f"COGNIT_CREATED κ{node.id}")
        for node_id,match in matched.items():
            pattern=self.graph.nodes[node_id].pattern
            if pattern:
                counted=pattern.selectivity_trials>0;old=pattern.match_selectivity
                pattern.occurrence_count+=1;pattern.stability=0.98*pattern.stability+0.02*match
                background=pattern.match(getattr(self,"previous_observation",frozenset())) if getattr(self,"previous_observation",None) else 0.0
                pattern.observe_selectivity(match,background)
                if counted:self._selectivity_sum-=old
                else:self._selectivity_count+=1
                self._selectivity_sum+=pattern.match_selectivity
        self.previous_observation=observation
        return matched

    def _prediction_error(self,current:set[int])->None:
        predicted=self.state.predictions;universe=set(predicted)|current
        if not universe:self.state.prediction_error=self.settings.prediction_error_neutral;self.state.prediction_error_valid=False;return
        errors=[abs((1.0 if i in current else 0.0)-predicted.get(i,0.0)) for i in universe]
        self.state.prediction_error=sum(errors)/len(errors);self.state.prediction_error_valid=True
        valid=[node_id for node_id in universe if node_id in self.graph.nodes]
        if self.backend:
            contributions=self.backend.cognit_state_fields(valid,(10,));updates=[]
            for node_id in valid:
                correct=1-abs((1. if node_id in current else 0.)-predicted.get(node_id,0.));updates.append((node_id,10,.95*contributions[node_id][0]+.05*correct))
            self.backend.set_cognit_fields(updates)
        else:
            for node_id in valid:
                correct=1-abs((1. if node_id in current else 0.)-predicted.get(node_id,0.));node=self.graph.nodes[node_id]
                node.predictive_contribution=.95*node.predictive_contribution+.05*correct
        self.calibration.observe(predicted,current);self.state.brier_score=self.calibration.brier_score;self.state.ece=self.calibration.ece
        if self.predictions_without_composites:
            universe2=set(self.predictions_without_composites)|current
            error_without=sum(abs((1. if i in current else 0.)-self.predictions_without_composites.get(i,0.)) for i in universe2)/max(1,len(universe2))
            contribution=error_without-self.state.prediction_error
            for node_id in self.previous_active:
                node=self.graph.nodes.get(node_id)
                if node and node.pattern and node.pattern.nodes:node.predictive_contribution=.95*node.predictive_contribution+.05*contribution

    def _materialize_relations(self,tick:int,current:set[int])->None:
        created=0;relation_count=self.graph.relation_count
        candidates={(s,t) for s in self.previous_active for t in current if s!=t}
        for source,target in sorted(candidates):
            support,conditional,_,lift=self.transitions.metrics(source,target)
            self.relation_candidates+=1;self.candidate_supports.append(support);self.candidate_lifts.append(lift)
            if support<self.settings.relation_provisional_support or lift<self.settings.relation_provisional_lift:continue
            if (target,RelationType.SEQUENTIAL,None) not in self.graph.adjacency.get(source,{}) and created>=max(1,self.settings.max_new_relations_per_tick//2):continue
            if relation_count>=self.settings.max_relations and (target,RelationType.SEQUENTIAL,None) not in self.graph.adjacency.get(source,{}):continue
            relation,is_new=self.graph.connect(source,target,RelationType.SEQUENTIAL)
            if is_new:
                if created>=self.settings.max_new_relations_per_tick or relation_count>=self.settings.max_relations:self.graph.remove_relation(source,target);continue
                created+=1;relation_count+=1;self.relations_materialized+=1;self.events.append(f"RELATION_CREATED κ{source} -> κ{target} SEQUENTIAL")
            relation.materialize_decay(tick,self.settings.relation_confidence_decay);relation.support=support;relation.lift=lift
            relation.strength=max(0.0,min(1.0,conditional));relation.prediction_probability=relation.strength
            relation.confidence=support/(support+self.settings.relation_confidence_k);relation.uncertainty=1-relation.confidence;relation.last_evidence_world_tick=tick
            if support>=self.settings.relation_consolidated_support and relation.confidence>=self.settings.relation_consolidated_confidence:relation.status=RelationStatus.CONSOLIDATED
        # Materialize action-conditioned evidence only where it has repeated support.
        if self.previous_action is not None:
            priority=lambda i:(0 if self.graph.nodes.get(i) and self.graph.nodes[i].kind=="BOUND_RELATION" else 1,i)
            for source in sorted(self.previous_active,key=priority):
                for target in sorted(current,key=priority):
                    probability,support=self.transitions.action_probability(source,self.previous_action,target)
                    _,conditional,_,_=self.transitions.metrics(source,target)
                    lift=probability/max(conditional,1e-9)
                    self.relation_candidates+=1;self.candidate_supports.append(support);self.candidate_lifts.append(lift)
                    if support>=self.settings.relation_provisional_support and lift>=self.settings.relation_provisional_lift and source!=target:
                        key=(target,RelationType.SELF_ACTION,self.previous_action.value)
                        if relation_count>=self.settings.max_relations and key not in self.graph.adjacency.get(source,{}):continue
                        relation,is_new=self.graph.connect(source,target,RelationType.SELF_ACTION,self.previous_action.value)
                        if is_new and (created>=self.settings.max_new_relations_per_tick or relation_count>=self.settings.max_relations):
                            self.graph.remove_relation(source,target,RelationType.SELF_ACTION,self.previous_action.value);continue
                        if is_new:created+=1;relation_count+=1
                        if is_new:self.relations_materialized+=1;self.events.append(f"RELATION_CREATED κ{source} -> κ{target} SELF_ACTION")
                        relation.strength=probability;relation.prediction_probability=probability;relation.support=support;relation.lift=lift
                        relation.confidence=support/(support+self.settings.relation_confidence_k);relation.uncertainty=1-relation.confidence;relation.last_evidence_world_tick=tick
                        if support>=self.settings.relation_consolidated_support and relation.confidence>=self.settings.relation_consolidated_confidence:relation.status=RelationStatus.CONSOLIDATED

    def _update_relation_outcomes(self,tick:int,current:set[int])->None:
        if self.backend:
            self.backend.update_outcomes(self.previous_active,current,self.previous_action,tick)
            return
        for source in self.previous_active:
            for relation in self.graph.outgoing(source):
                if relation.relation_type is RelationType.SELF_ACTION and (self.previous_action is None or relation.context_id!=self.previous_action.value):continue
                confirmed=relation.target_id in current
                relation.update_outcome(confirmed,self.settings.relation_confirmation_rate,self.settings.relation_contradiction_rate)
                relation.usefulness=max(0.,min(1.,relation.usefulness+self.settings.relation_utility_rate*((1. if confirmed else 0.)-relation.strength)))
                relation.last_evidence_world_tick=tick
                if relation.status is RelationStatus.CONSOLIDATED and relation.confidence<self.settings.relation_consolidated_confidence*.6:relation.status=RelationStatus.PROVISIONAL

    def _update_intrinsic_state(self,current:set[int],matched:dict[int,float],observation:frozenset[PrimitiveKey])->None:
        covered:set[PrimitiveKey]=set()
        for node_id,score in matched.items():
            pattern=self.graph.nodes[node_id].pattern
            if pattern and score>=self.settings.pattern_match_threshold:
                for primitive in observation:
                    if primitive in pattern.participants or pattern.is_translation_tolerant:covered.add(primitive)
        coverage=len(covered)/max(1,len(observation));self.state.representation_coverage=coverage;self.state.representation_error=1-coverage
        self.state.continuity_error=self.perception.last_continuity_error
        novelty_values=[];control_predictions=self._graph_predictions_for_actions(self.previous_active,self.available_actions);controls=[]
        for node_id in current:
            node=self.graph.nodes[node_id];occ=node.pattern.occurrence_count if node.pattern else 1
            rarity=1.0/sqrt(max(1,occ));surprise=self.state.prediction_error if self.state.prediction_error_valid else 0.;instability=1-(node.pattern.stability if node.pattern else .5)
            components=((rarity,self.settings.novelty_rarity_weight),(surprise,self.settings.novelty_prediction_error_weight),(self.state.representation_error,self.settings.novelty_representation_weight),(instability,self.settings.novelty_instability_weight))
            node.novelty=1.0
            for value,weight in components:node.novelty*=max(0.,1-value)**weight
            node.novelty=1-node.novelty
            novelty_values.append(node.novelty);controls.append(self._control_from_predictions(control_predictions,node_id))
        base_novelty=sum(novelty_values)/len(novelty_values) if novelty_values else 0.0
        self.state.novelty=1-(1-base_novelty)*(1-self.state.representation_error)**self.settings.novelty_representation_weight
        predicted_confidence=sum(self.state.predictions.values())/max(1,len(self.state.predictions))
        self.state.uncertainty=1.0-min(1.0,predicted_confidence)
        self.state.controllability=sum(controls)/max(1,len(controls)) if controls else 0.0
        self.state.pattern_selectivity=self._selectivity_sum/max(1,self._selectivity_count);self.state.representation_quality=coverage*self.state.pattern_selectivity
        self.state.internal_tension=min(1.0,self.state.novelty*(self.state.prediction_error+self.state.uncertainty)*
            (self.settings.controllability_baseline+self.state.controllability))
        self.state.overall_surprise=1-(1-(self.state.prediction_error if self.state.prediction_error_valid else 0.))*(1-self.state.representation_error)*(1-self.state.continuity_error)

    def _update_goal(self,current:set[int])->None:
        goal=self.state.goal
        candidate_ids=tuple(sorted(current,key=lambda i:self.graph.nodes[i].novelty,reverse=True)[:3])
        candidate_intensity=self.state.internal_tension
        if goal:
            goal.age+=1;understanding=(1-self.state.novelty)*(1-self.state.prediction_error)
            available=any(i in current for i in goal.target_cognit_ids)
            if available:goal.unavailable_ticks=0;goal.target_last_seen=goal.age;goal.unavailable_since_seconds=None
            else:
                goal.unavailable_ticks+=1
                if self.world_time_seconds is not None and goal.unavailable_since_seconds is None:goal.unavailable_since_seconds=self.world_time_seconds
            if goal.origin!="TARGET":
                understanding_factor=1-self.settings.goal_understanding_decay*understanding
                if self.world_time_seconds is None:goal.persistence*=self.settings.goal_decay*understanding_factor
                else:
                    if goal.created_time_seconds is None:goal.created_time_seconds=self.world_time_seconds
                    last=goal.last_touch_time_seconds if goal.last_touch_time_seconds is not None else goal.created_time_seconds
                    goal.persistence*=self.settings.goal_decay**(self.world_time_seconds-last)
                    goal.persistence*=understanding_factor;goal.last_touch_time_seconds=self.world_time_seconds
            goal.intensity=self.settings.goal_inertia*goal.intensity+(1-self.settings.goal_inertia)*candidate_intensity
            if goal.persistence<self.settings.goal_min_persistence:
                self.state.completed_goal_lifetimes.append(goal.age);self.events.append(f"GOAL_COMPLETED G{goal.id}");self.state.goal=None
            elif goal.origin!="TARGET" and ((self.world_time_seconds is None and goal.unavailable_ticks>self.settings.goal_unavailable_limit) or (self.world_time_seconds is not None and goal.unavailable_since_seconds is not None and self.world_time_seconds-goal.unavailable_since_seconds>self.settings.goal_unavailable_limit)):
                goal.status="RETIRED";self.state.goals_retired+=1;self.state.completed_goal_lifetimes.append(goal.age);self.events.append(f"GOAL_RETIRED G{goal.id}");self.state.goal=None
        if self.state.goal is None and candidate_ids and candidate_intensity>=self.settings.goal_tension_threshold:
            self.state.goal=Goal(self.next_goal_id,candidate_ids,1.0,candidate_intensity,1-self.state.uncertainty,
                persistence=self.settings.goal_initial_persistence,origin_tension=candidate_intensity,created_time_seconds=self.world_time_seconds,last_touch_time_seconds=self.world_time_seconds)
            self.next_goal_id+=1;self.state.goals_generated+=1;self.events.append(f"GOAL_CREATED G{self.state.goal.id}")

    def _imagine(self,current:set[int])->dict[ActionType,FutureEstimate]:
        futures={};goal_targets=set(self.state.goal.target_cognit_ids) if self.state.goal else set()
        predictions_by_action=self._graph_predictions_for_actions(current,self.available_actions)
        native_trials=self.backend.action_trials(current,self.available_actions) if self.backend else None
        all_targets={target for prediction in predictions_by_action.values() for target in prediction}
        target_control={i:self._control_from_predictions(predictions_by_action,i) for i in all_targets}
        for action in self.available_actions:
            probabilities=predictions_by_action[action];experience=native_trials[action] if native_trials is not None else sum(self.transitions.action_source_counts[i,action] for i in current)
            confidence=experience/(experience+6);uncertainty=1-confidence
            expected_novelty=sum(self.graph.nodes[i].novelty*p for i,p in probabilities.items() if i in self.graph.nodes)/max(sum(probabilities.values()),1e-9) if probabilities else 1.0
            alignment=sum(probabilities.get(i,0.0) for i in goal_targets)/max(1,len(goal_targets))
            control=sum(target_control.get(i,0.0)*p for i,p in probabilities.items())/max(sum(probabilities.values()),1e-9) if probabilities else 0.0
            predicted_signature=frozenset(i for i,p in probabilities.items() if p>=0.35)
            loop_risk=self.trace.loop_score(predicted_signature,self.settings.loop_max_period,self.settings.loop_min_repeats) if predicted_signature else 0.0
            cost=self.settings.idle_cost if action is ActionType.IDLE else self.settings.grab_cost if action.name.startswith("GRAB_") else self.settings.release_cost if action is ActionType.RELEASE else self.settings.interact_cost if action.name.startswith("INTERACT") else self.settings.movement_cost
            score=(self.settings.choice_goal_weight*alignment+self.settings.choice_information_weight*uncertainty+
                self.settings.choice_novelty_weight*expected_novelty+self.settings.choice_control_weight*control-
                self.settings.choice_loop_weight*loop_risk-self.settings.choice_cost_weight*cost)
            epistemic=self.affordances.epistemic(current,action);progress=self.predicted_target_progress(current,action);score+=.45*epistemic+.8*progress
            futures[action]=FutureEstimate(probabilities,confidence,expected_novelty,alignment,uncertainty,control,loop_risk,score)
        values=list(target_control.values());self.state.agency_estimate=sum(values)/max(1,len(values))
        return futures

    def _graph_predict(self,active:set[int],action:ActionType|None,exclude_composites:bool=False)->dict[int,float]:
        return self._graph_predictions_for_actions(active,(action,),exclude_composites)[action]

    def _graph_predictions_for_actions(self,active:set[int],actions:tuple[ActionType|None,...],exclude_composites:bool=False)->dict[ActionType|None,dict[int,float]]:
        if not self.relation_prediction_enabled:return {a:{} for a in actions}
        if self.backend:
            if exclude_composites:active={i for i in active if not (self.graph.nodes.get(i) and self.graph.nodes[i].pattern and self.graph.nodes[i].pattern.nodes)}
            self.backend.prediction_tick=self.trace.entries[-1].tick+1 if self.trace.entries else 0
            return self.backend.predict_graph_batch(self.graph,active,actions)
        common:dict[int,list[float]]=defaultdict(list);conditioned:dict[int,dict[int,list[float]]]=defaultdict(lambda:defaultdict(list));tick=self.trace.entries[-1].tick+1 if self.trace.entries else 0
        for source in active:
            node=self.graph.nodes.get(source)
            if exclude_composites and node and node.pattern and node.pattern.nodes:continue
            activity=node.activity if node else 1.0
            for relation in self.graph.outgoing(source):
                probability=relation.prediction_probability if relation.prediction_probability>0 else relation.strength
                q=max(0.,min(1.,activity*probability*relation.effective_confidence(tick,self.settings.relation_confidence_decay)))
                if relation.relation_type is RelationType.SELF_ACTION and relation.context_id is not None:conditioned[relation.context_id][relation.target_id].append(q)
                else:common[relation.target_id].append(q)
        result={}
        for action in actions:
            action_causes=conditioned.get(action.value,{}) if action is not None else {};targets=set(common)|set(action_causes);prediction={}
            for target in targets:prediction[target]=1-prod(1-q for q in (*common.get(target,()),*action_causes.get(target,())))
            result[action]=prediction
        return result

    def _graph_controllability(self,active:set[int],target:int)->float:
        return self._control_from_predictions({a:self._graph_predict(active,a) for a in self.available_actions},target)

    @staticmethod
    def _control_from_predictions(predictions:dict[ActionType,dict[int,float]],target:int)->float:
        values=[p.get(target,0.) for p in predictions.values()];return max(values)-min(values) if values else 0.0

    def predict_from_relations(self,active:set[int],action:ActionType|None=None)->dict[int,float]:
        """Diagnostic surface proving runtime knowledge resides in materialized rho."""
        return self._graph_predict(active,action)

    def predicted_target_progress(self,active:set[int],action:ActionType)->float:
        """Compare Target to participant states predicted by acquired graph rho only."""
        if self.target_structure is None:return 0.
        # Structural progress is an intervention query: unconditioned temporal
        # succession must not make every action look causally equivalent.
        if self.backend:prediction=self.backend.action_effects(active,action)
        else:
            causes=defaultdict(list)
            for source in active:
                for relation in self.graph.outgoing(source):
                    if relation.relation_type is not RelationType.SELF_ACTION or relation.context_id!=action.value:continue
                    q=relation.prediction_probability*relation.confidence
                    if q>=self.settings.prediction_probability_floor:causes[relation.target_id].append(q)
            prediction={target:1-prod(1-q for q in values) for target,values in causes.items()}
        predicted_ids={i for i,p in prediction.items() if p>=.25}
        predicted=self.belief_scene.predicted_mismatch(self.target_structure,predicted_ids)
        return self.target_mismatch-predicted

    def _choose_action(self)->Action:
        self.state.action_scores={a:f.score for a,f in self.state.futures.items()}
        epistemic=self.affordances.last_epistemic
        # When a context is genuinely unknown, choose by information deficit first;
        # the symmetry resolver supplies deterministic diversity without randomness/frequency rules.
        decision_scores=epistemic if epistemic and max(epistemic.values())>.35 else self.state.action_scores
        decision=self.tie_resolver.resolve(decision_scores,[entry.action for entry in self.trace.entries])
        self.state.tie_set=decision.tied;self.state.tie_resolution_method=decision.method.name
        if len(decision.tied)>1:self.state.tie_count+=1
        return Action(decision.action)

    def _prune(self,tick:int)->None:
        stale=[]
        if self.backend and tick%64==0:
            removed,_=self.backend.engine.lifecycle_step(tick,self.settings.relation_max_idle,self.settings.relation_death_threshold,self.settings.relation_confidence_decay)
            if removed:self.events.append(f"RELATION_DELETED {removed} native")
        elif tick%64==0:
            for source,edges in self.graph.adjacency.items():
                for key,relation in edges.items():
                    if tick-relation.last_evidence_world_tick>self.settings.relation_max_idle and relation.effective_confidence(tick,self.settings.relation_confidence_decay)<self.settings.relation_death_threshold:stale.append((source,key,relation))
        for source,key,relation in stale:
            self.graph.adjacency[source].pop(key,None);self.events.append(f"RELATION_DELETED κ{source} -> κ{relation.target_id}")
        # Cognit IDs are monotonic and never reused; dict insertion order is ID order.
        ids=tuple(self.graph.nodes)
        if ids:
            batch=[ids[(self.lifecycle_cursor+i)%len(ids)] for i in range(min(self.settings.lifecycle_batch_size,len(ids)))]
            self.lifecycle_cursor=(self.lifecycle_cursor+len(batch))%len(ids)
            for node_id in batch:
                node=self.graph.nodes[node_id];retention=node.retention_score(self.cognitive_tick,self.settings)
                node.low_retention_ticks=node.low_retention_ticks+1 if retention<self.settings.retention_threshold else 0
                if node.low_retention_ticks>=self.settings.retention_grace_ticks:self.deletion_candidates.append(node_id)
        for _ in range(min(self.settings.lifecycle_batch_size,len(self.deletion_candidates))):
            node_id=self.deletion_candidates.popleft()
            if node_id not in self.graph.nodes or self.composites.is_protected(node_id):continue
            node=self.graph.nodes[node_id]
            if node.retention_score(self.cognitive_tick,self.settings)>=self.settings.retention_threshold:continue
            if node.pattern:
                if node.pattern.selectivity_trials:self._selectivity_sum-=node.pattern.match_selectivity;self._selectivity_count-=1
                self.pattern_nodes.pop(node.pattern.signature,None)
                for p in node.pattern.participants:self.primitive_index[p].discard(node_id)
            self.graph.remove_cognit(node_id);self.events.append(f"COGNIT_DELETED κ{node_id}")
