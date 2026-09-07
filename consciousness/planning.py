from dataclasses import dataclass
from heapq import nsmallest
from world.actions import ActionType


@dataclass(frozen=True,slots=True)
class Plan:
    actions:tuple[ActionType,...];predicted_states:tuple[frozenset[int],...];score:float;confidence:float;goal_alignment:float;uncertainty:float;loop_risk:float;created_tick:int;revision:int=0


class DeliberativePlanner:
    def __init__(self,settings)->None:
        self.settings=settings;self.plan:Plan|None=None;self.cycles_last=0;self.total_cycles=0;self.plans_created=0;self.plans_revised=0;self.plans_abandoned=0;self.plan_steps_executed=0;self.last_reason="NONE";self.internal_tick=0;self.converged=False;self.last_active=frozenset();self.subgoal_signature=None;self.subgoal_cooldown_until=0

    def deliberate(self,core,current:set[int],tick:int)->ActionType:
        self._manage_goals(core,current,tick)
        scores=core.state.action_scores;ordered=sorted(scores.values(),reverse=True);margin=ordered[0]-ordered[1] if len(ordered)>1 else 1.
        need=max(0.,core.state.uncertainty)+(1-min(1.,margin/max(self.settings.action_dominance_margin,1e-9)))+(1 if core.state.goal and core.memory.recall(core.state.goal.target_cognit_ids,core.graph,tick) else 0)
        budget=max(self.settings.min_deliberation_cycles,min(self.settings.max_deliberation_cycles,1+int(need*self.settings.max_deliberation_cycles/3)))
        self.cycles_last=0;self.converged=False;stable=0;previous_ranking=();previous_plan=();working=set(current);semantic_cache=({}, {}, {})
        for cycle in range(budget):
            recalled=core.memory.recall(core.state.goal.target_cognit_ids if core.state.goal else (),core.graph,tick)
            core.cognitive_tick+=1;cognitive_tick=core.cognitive_tick
            recall_operations=[]
            for node_id in recalled:
                node=core.graph.nodes.get(node_id)
                if node:recall_operations.append((node_id,.12*next((m.last_recall_strength for m in core.memory.structures.values() if m.cognit_id==node_id),.5)));working.add(node_id)
            if core.backend:core.backend.receive_batch(recall_operations,cognitive_tick,core.settings)
            else:
                for node_id,energy in recall_operations:core.graph.nodes[node_id].receive(energy,cognitive_tick,core.settings)
            wave=core._propagate(working,cognitive_tick);working=set(wave.active_ids)|set(recalled);core.last_wave=wave
            core.state.futures=core._imagine(working);core.state.action_scores={a:f.score for a,f in core.state.futures.items()}
            core.state.uncertainty=.8*core.state.uncertainty+.2*(1-max((f.confidence for f in core.state.futures.values()),default=0.))
            initial_predictions={action:future.probabilities for action,future in core.state.futures.items()}
            candidate=self._search(core,working,tick,semantic_cache,initial_predictions);ranking=tuple(a for a,_ in sorted(core.state.action_scores.items(),key=lambda x:(-x[1],x[0].value)))
            signature=tuple(a.value for a in candidate.actions);stable=stable+1 if ranking==previous_ranking and signature==previous_plan else 0;previous_ranking,previous_plan=ranking,signature
            self.cycles_last+=1;self.total_cycles+=1;self.internal_tick+=1
            if self.cycles_last>=self.settings.min_deliberation_cycles and stable>=2:self.converged=True;break
        current_plan=candidate;self.last_active=frozenset(working)
        if self.plan and self.plan.actions:
            expected=self.plan.predicted_states[0] if self.plan.predicted_states else frozenset()
            overlap=len(expected&current)/max(1,len(expected|current))
            if overlap<.15:self.plans_abandoned+=1;self.last_reason="PREDICTION_MISMATCH"
            else:self.plans_revised+=1;self.last_reason="REVALIDATED"
        else:self.plans_created+=1;self.last_reason="CREATED"
        self.plan=current_plan
        return current_plan.actions[0] if current_plan.actions else core._choose_action().kind

    def _manage_goals(self,core,current:set[int],tick:int)->None:
        goal=core.state.goal
        if goal and goal.parent_id is not None and set(goal.target_cognit_ids)&current:
            core.state.subgoals_completed+=1
            self.subgoal_cooldown_until=tick+16
            if core.goal_stack:core.state.goal=core.goal_stack.pop();core.state.parent_resumptions+=1
            return
        if not goal or goal.parent_id is not None or goal.origin!="TARGET" or not core.memory.structures:return
        # Prefer repairing a known violated binding with a learned causal edge.
        # Missing-participant recall below is the fallback when no such edge is known.
        if core.belief_scene.last_binding.violated or core.belief_scene.last_binding.unknown:
            ranked=[]
            for action in core.available_actions:
                progress=core.predicted_target_progress(current,action)
                for node_id,probability in core.predict_from_relations(current,action).items():
                    node=core.graph.nodes.get(node_id)
                    if node and node.kind=="BOUND_RELATION":ranked.append((progress*probability,probability,-action.value,node_id,action))
            if ranked:
                value,probability,_,node_id,action=max(ranked)
                if value>0:
                    signature=(goal.id,node_id,action.value)
                    if signature==self.subgoal_signature and tick<self.subgoal_cooldown_until:return
                    self.subgoal_signature=signature;self.subgoal_cooldown_until=tick+16;core.goal_stack.append(goal)
                    child=type(goal)(core.next_goal_id,(node_id,),1.,goal.intensity,probability,persistence=.95,parent_id=goal.id,depth=goal.depth+1,origin="PLANNER",target_signature=((node_id,),))
                    core.next_goal_id+=1;core.state.goal=child;core.state.subgoals_created+=1;core.state.max_goal_depth=max(core.state.max_goal_depth,child.depth);return
        bound=set(core.belief_scene.last_binding.role_to_participant);candidates=sorted(core.memory.structures.values(),key=lambda m:(m.cognit_id in bound,-m.last_recall_strength,-m.confidence,m.id))
        chosen=next((m for m in candidates if m.cognit_id not in bound and m.confidence>=.2 and m.place_cognit_id not in current),None)
        if chosen:
            signature=(goal.id,chosen.cognit_id,chosen.place_cognit_id)
            if signature==self.subgoal_signature and tick<self.subgoal_cooldown_until:return
            self.subgoal_signature=signature;self.subgoal_cooldown_until=tick+16;core.goal_stack.append(goal);child=type(goal)(core.next_goal_id,(chosen.place_cognit_id,),1.,goal.intensity,chosen.confidence,persistence=.95,parent_id=goal.id,depth=goal.depth+1,origin="PLANNER",target_signature=((chosen.cognit_id,),))
            core.next_goal_id+=1;core.state.goal=child;core.state.subgoals_created+=1;core.state.max_goal_depth=max(core.state.max_goal_depth,child.depth)
            return

    def _search(self,core,current:set[int],tick:int,semantic_cache=None,initial_predictions=None)->Plan:
        epistemic_cache,progress_cache,shared_memory=semantic_cache or ({},{},{})
        initial_state=frozenset(current);goal=set(core.state.goal.target_cognit_ids) if core.state.goal else set();beam=[((),initial_state,(),0.,1.,())];prediction_cache=({initial_state:initial_predictions} if initial_predictions is not None else {});transition_cache={};loop_cache={};memory_cache={}
        memory_index={}
        if shared_memory:memory_index=shared_memory
        else:
            for memory in core.memory.structures.values():
                for node_id in (memory.cognit_id,memory.place_cognit_id):memory_index[node_id]=max(memory_index.get(node_id,float('-inf')),memory.confidence)
            shared_memory.update(memory_index)
        best=beam[0]
        for _ in range(self.settings.planning_horizon):
            expanded=[]
            if core.backend:
                layer_states=[];seen=set()
                for _,state,_,_,_,_ in beam:
                    needs_predictions=state not in prediction_cache
                    needs_effects=core.target_structure is not None and any((state,action) not in progress_cache for action in core.available_actions)
                    if (needs_predictions or needs_effects) and state not in seen:seen.add(state);layer_states.append(state)
                if layer_states:
                    core.backend.prediction_tick=core.trace.entries[-1].tick+1 if core.trace.entries else 0
                    for state,(predictions,effects) in core.backend.planner_transition_batch(layer_states,core.available_actions).items():
                        if state not in prediction_cache:prediction_cache[state]=predictions
                        if core.target_structure is not None:
                            for candidate_action,values in effects.items():
                                key=(state,candidate_action)
                                if key not in progress_cache:
                                    predicted_ids={i for i,p in values.items() if p>=.25}
                                    progress_cache[key]=core.target_mismatch-core.belief_scene.predicted_mismatch(core.target_structure,predicted_ids)
            for actions,state,states,score,confidence,action_values in beam:
                predictions=prediction_cache.get(state)
                if predictions is None:
                    predictions=core._graph_predictions_for_actions(set(state),core.available_actions);prediction_cache[state]=predictions
                if core.backend and core.target_structure is not None and any((state,candidate_action) not in progress_cache for candidate_action in core.available_actions):
                    effects=core.backend.action_effects_batch(state,core.available_actions)
                    for candidate_action,values in effects.items():
                        predicted_ids={i for i,p in values.items() if p>=.25};progress_cache[(state,candidate_action)]=core.target_mismatch-core.belief_scene.predicted_mismatch(core.target_structure,predicted_ids)
                for action,p in predictions.items():
                    key=(state,action)
                    if key not in transition_cache:
                        transition_cache[key]=(frozenset(i for i,v in p.items() if v>=.25),sum(p.get(i,0.) for i in goal)/max(1,len(goal)),sum(p.values())/max(1,len(p)))
                    next_state,alignment,conf=transition_cache[key]
                    if next_state not in memory_cache:
                        values=[memory_index[i] for i in next_state if i in memory_index];memory_cache[next_state]=max(values) if values else .5
                    memory_conf=memory_cache[next_state]
                    if next_state not in loop_cache:loop_cache[next_state]=core.trace.loop_score(next_state,core.settings.loop_max_period,core.settings.loop_min_repeats) if next_state else 0.
                    loop=loop_cache[next_state]
                    if key not in epistemic_cache:epistemic_cache[key]=core.affordances.epistemic(state,action)
                    if key not in progress_cache:progress_cache[key]=core.predicted_target_progress(set(state),action)
                    epistemic=epistemic_cache[key];progress=progress_cache[key];value=score+alignment+.1*conf+.12*memory_conf+.45*epistemic+.8*progress-.12*loop-.03*len(actions)
                    expanded.append((actions+(action,),next_state,states+(next_state,),value,confidence*max(.05,conf),action_values+(action.value,)))
            if not expanded:break
            beam=nsmallest(self.settings.planning_beam_width,expanded,key=lambda x:(-x[3],x[5]))
            if beam[0][3]>best[3]:best=beam[0]
        actions,state,states,score,confidence,_=best;alignment=len(state&goal)/max(1,len(goal));loop=core.trace.loop_score(state,core.settings.loop_max_period,core.settings.loop_min_repeats) if state else 0.;return Plan(actions,states,score,confidence,alignment,1-confidence,loop,tick,(self.plan.revision+1 if self.plan else 0))

    def committed(self)->None:
        if self.plan and self.plan.actions:self.plan_steps_executed+=1

    def to_dict(self)->dict:
        from dataclasses import asdict
        data=asdict(self.plan) if self.plan else None
        if data:
            data["actions"]=[a.name for a in self.plan.actions];data["predicted_states"]=[sorted(x) for x in self.plan.predicted_states]
        return {"plan":data,"cycles_last":self.cycles_last,"total_cycles":self.total_cycles,"plans_created":self.plans_created,"plans_revised":self.plans_revised,"plans_abandoned":self.plans_abandoned,"plan_steps_executed":self.plan_steps_executed,"last_reason":self.last_reason,"internal_tick":self.internal_tick,"converged":self.converged,"subgoal_signature":self.subgoal_signature,"subgoal_cooldown_until":self.subgoal_cooldown_until}

    def restore(self,data:dict)->None:
        raw=data.get("plan")
        if raw:self.plan=Plan(tuple(ActionType[x] for x in raw["actions"]),tuple(frozenset(x) for x in raw["predicted_states"]),raw["score"],raw["confidence"],raw["goal_alignment"],raw["uncertainty"],raw["loop_risk"],raw["created_tick"],raw.get("revision",0))
        for key in ("cycles_last","total_cycles","plans_created","plans_revised","plans_abandoned","plan_steps_executed","last_reason","internal_tick","converged","subgoal_cooldown_until"):setattr(self,key,data.get(key,getattr(self,key)))
        self.subgoal_signature=tuple(data["subgoal_signature"]) if data.get("subgoal_signature") else None
