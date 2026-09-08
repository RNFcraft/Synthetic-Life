"""Graph substrate boundary for Python research orchestration.

The native implementation owns numeric graph/evidence state.  This module
contains no shadow Cognit or Relation collection.
"""
from __future__ import annotations
from typing import Protocol,Sequence
from world.actions import ActionType
from .native_engine import NativeBrainEngine,EvidenceConfig

class _ObservedEngine:
    """Expose the native API while invalidating Python's observational cache on mutation."""
    _mutators=frozenset({'add_cognit','add_cognits','set_activity','set_refractory','set_cognit_states','set_cognit_fields','receive','receive_batch','remove_cognit','propagate','homeostatic_step','begin_continuous_time','materialize_cognits_at','load_graph'})
    def __init__(self,inner,on_mutation):self._inner=inner;self._on_mutation=on_mutation;self._wrapped={}
    def __getattr__(self,name):
        value=getattr(self._inner,name)
        if name not in self._mutators or not callable(value):return value
        wrapped=self._wrapped.get(name)
        if wrapped is None:
            def wrapped(*args,**kwargs):
                result=value(*args,**kwargs);self._on_mutation(name,args);return result
            self._wrapped[name]=wrapped
        return self._wrapped[name]

class BrainGraphBackend(Protocol):
    def add_cognit(self,activity:float=0.,threshold:float=.25,confidence:float=.5)->int:...
    def propagate(self,seeds:Sequence[int],cognitive_tick:int):...
    def predict(self,active:Sequence[int],action:ActionType):...
    def predict_actions_batch(self,active:Sequence[int],actions:Sequence[ActionType]):...
    def update_transition_evidence(self,before:Sequence[int],action:ActionType,after:Sequence[int])->None:...
    def materialize(self,world_tick:int):...

class NativeGraphBackend:
    """ID-only coarse facade; NativeBrainEngine is the sole graph authority."""
    def __init__(self,settings):
        self.settings=settings;self.full_graph_sync_calls=0;self.ffi_calls=0;self.receive_calls=0;self.field_write_calls=0;self.state_read_calls=0;self.relation_proxy_objects_created=0;self._state_cache={}
        self.engine=_ObservedEngine(NativeBrainEngine(settings.relation_evidence_window),self._native_mutated)
        self.evidence_config=EvidenceConfig();self.evidence_config.minimum_support=settings.relation_provisional_support
        self.evidence_config.minimum_lift=settings.relation_provisional_lift
        self.evidence_config.confidence_k=settings.relation_confidence_k;self.evidence_config.consolidated_support=settings.relation_consolidated_support;self.evidence_config.consolidated_confidence=settings.relation_consolidated_confidence
    def _native_mutated(self,name,args):
        if name in {'add_cognit','add_cognits'}:return
        if name in {'set_activity','set_refractory','receive','remove_cognit'} and args:self.invalidate_state([int(args[0])+1]);return
        if name=='set_cognit_states' and args:self.invalidate_state([int(i)+1 for i in args[0]]);return
        self.invalidate_state()
    def add_cognit(self,activity=0.,threshold=.25,confidence=.5):return self.engine.add_cognit(activity,threshold,confidence)
    def begin_continuous_time(self,now):
        s=self.settings;self.engine.begin_continuous_time(float(now),s.homeostasis_trace_decay,s.homeostasis_learning_rate,s.threshold_min,s.threshold_max,s.cognit_activity_decay,.999,s.relation_confidence_decay);self.invalidate_state()
    def propagate(self,seeds,cognitive_tick):self.ffi_calls+=1;return self.engine.propagate(list(seeds),cognitive_tick)
    def predict(self,active,action):self.ffi_calls+=1;return self.engine.predict_compact(list(active),action.value)
    def predict_actions_batch(self,active,actions):self.ffi_calls+=1;return self.engine.predict_actions_batch(list(active),[a.value for a in actions])
    def update_transition_evidence(self,before,action,after):self.ffi_calls+=1;self.engine.update_transition_evidence(list(before),action.value,list(after))
    def materialize(self,world_tick,before,action,after):self.ffi_calls+=1;return self.engine.materialize_current(self.evidence_config,world_tick,list(before),action.value,list(after),self.settings.max_new_relations_per_tick,self.settings.max_relations,self.settings.relation_confidence_decay)
    def cognit_state_one(self,node_id):
        row=self._state_cache.get(node_id)
        if row is None or any(value is None for value in row):self.ffi_calls+=1;self.state_read_calls+=1;self._state_cache[node_id]=list(self.engine.cognit_state_full([node_id-1]))
        return self._state_cache[node_id]
    def cognit_state_fields(self,node_ids,fields):
        ids=list(dict.fromkeys(node_ids));missing=[]
        for node_id in ids:
            row=self._state_cache.setdefault(node_id,[None]*12)
            if any(row[field] is None for field in fields):missing.append(node_id)
        if missing:
            mask=sum(1<<field for field in fields);self.ffi_calls+=1;self.state_read_calls+=1
            values=iter(self.engine.cognit_state_masked([i-1 for i in missing],mask))
            for node_id in missing:
                row=self._state_cache[node_id]
                for field in fields:row[field]=next(values)
        return {node_id:tuple(self._state_cache[node_id][field] for field in fields) for node_id in ids}
    def cognit_field(self,node_id,field):
        row=self._state_cache.get(node_id)
        if row is None:
            self.ffi_calls+=1;self.state_read_calls+=1;self._state_cache[node_id]=list(self.engine.cognit_state_full([node_id-1]))
        elif row[field] is None:self.cognit_state_fields((node_id,),(field,))
        return self._state_cache[node_id][field]
    def set_cognit_field(self,node_id,index,value):
        self.ffi_calls+=1;self.field_write_calls+=1;self.engine.set_cognit_fields([node_id-1],[index],[float(value)])
        self._state_cache.pop(node_id,None)
    def set_cognit_fields(self,updates):
        if not updates:return
        self.ffi_calls+=1;self.field_write_calls+=1
        self.engine.set_cognit_fields([node_id-1 for node_id,_,_ in updates],[field for _,field,_ in updates],[value for _,_,value in updates])
        self.invalidate_state([node_id for node_id,_,_ in updates])
    def invalidate_state(self,ids=None):
        if ids is None:self._state_cache.clear()
        else:
            for node_id in ids:self._state_cache.pop(node_id,None)
    def receive(self,node_id,energy,tick,settings,wave_step=False):
        self.ffi_calls+=1;self.receive_calls+=1;active=self.engine.receive(node_id-1,energy,tick,wave_step,settings.refractory_attenuation,settings.refractory_wave_steps);self._state_cache.pop(node_id,None);return active
    def receive_batch(self,operations,tick,settings,wave_step=False):
        if not operations:return []
        self.ffi_calls+=1;self.receive_calls+=1
        result=self.engine.receive_batch([node_id-1 for node_id,_ in operations],[energy for _,energy in operations],tick,wave_step,settings.refractory_attenuation,settings.refractory_wave_steps)
        self.invalidate_state([node_id for node_id,_ in operations]);return result
    def propagate_graph(self,graph,seeds,cognitive_tick):
        from .wave import WaveResult
        self.ffi_calls+=1;active,energy,steps,transmitted=self.engine.propagate([i-1 for i in seeds],cognitive_tick)
        ids=frozenset(i+1 for i in active);self.invalidate_state()
        return WaveResult(ids,energy,steps,transmitted)
    def predict_graph_batch(self,graph,active,actions):
        self.ffi_calls+=1;rows=self.engine.predict_actions_batch_at([i-1 for i in active],[a.value if a is not None else 0 for a in actions],getattr(self,"prediction_tick",0),self.settings.relation_confidence_decay)
        return {action:{target+1:value for target,value in values} for action,values in zip(actions,rows)}
    def action_trials(self,active,actions):self.ffi_calls+=1;return dict(zip(actions,self.engine.action_trials([i-1 for i in active],[a.value for a in actions])))
    def action_effects(self,active,action):self.ffi_calls+=1;return {target+1:value for target,value in self.engine.action_effects([i-1 for i in active],action.value,self.settings.prediction_probability_floor)}
    def action_effects_batch(self,active,actions):
        self.ffi_calls+=1;rows=self.engine.action_effects_batch([i-1 for i in active],[a.value for a in actions],self.settings.prediction_probability_floor);return {action:{target+1:value for target,value in row} for action,row in zip(actions,rows)}
    def planner_transition_batch(self,states,actions):
        self.ffi_calls+=1
        rows=self.engine.planner_transition_batch([[i-1 for i in state] for state in states],[a.value for a in actions],getattr(self,"prediction_tick",0),self.settings.relation_confidence_decay,self.settings.prediction_probability_floor)
        result={}
        for state,(prediction_rows,effect_rows) in zip(states,rows):
            predictions={action:{target+1:value for target,value in row} for action,row in zip(actions,prediction_rows)}
            effects={action:{target+1:value for target,value in row} for action,row in zip(actions,effect_rows)}
            result[state]=(predictions,effects)
        return result
    def update_outcomes(self,before,current,action,tick):
        s=self.settings
        self.engine.update_outcomes([i-1 for i in before],[i-1 for i in current],action.value if action else -1,tick,s.relation_confirmation_rate,s.relation_contradiction_rate,s.relation_utility_rate,s.relation_consolidated_confidence)
    @property
    def cognit_count(self):return self.engine.cognit_count
    @property
    def relation_count(self):return self.engine.relation_count

class PythonGraphBackend:
    """Oracle/debug marker; SyntheticEntityCore itself supplies its frozen implementation."""
    def __init__(self,core):self.core=core
    def propagate(self,seeds,cognitive_tick):return self.core.wave.propagate(self.core.graph,set(seeds),cognitive_tick)
    def predict(self,active,action):return self.core.predict_from_relations(set(active),action)
    def predict_actions_batch(self,active,actions):return self.core._graph_predictions_for_actions(set(active),tuple(actions))
    def update_transition_evidence(self,before,action,after):self.core.transitions.observe(set(before),action,set(after))
    def materialize(self,world_tick):return self.core._materialize_relations(world_tick,set())
