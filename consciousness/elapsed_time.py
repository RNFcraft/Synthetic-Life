"""Composable lazy elapsed-time state; uses simulated WorldTime only."""
from dataclasses import dataclass
from math import isfinite

def _dt(now,last):
    if not isfinite(now) or now<last:raise ValueError("elapsed time must be finite and monotonic")
    return now-last

@dataclass(slots=True)
class CognitElapsedState:
    activity:float;utility:float;activity_trace:float;homeostatic_threshold:float;target_activity:float;last_touch_time:float=0.;latent_threshold:float|None=None
    def materialize(self,now,trace_decay,learning_rate,threshold_min,threshold_max,activity_decay,utility_decay):
        dt=_dt(now,self.last_touch_time)
        if not dt:return
        trace0=self.activity_trace;trace_factor=trace_decay**dt;self.activity_trace=trace0*trace_factor
        if trace_decay==1.:trace_sum=trace0*dt
        else:trace_sum=trace0*trace_decay*(1-trace_factor)/(1-trace_decay)
        if self.latent_threshold is None:self.latent_threshold=self.homeostatic_threshold
        self.latent_threshold+=learning_rate*(trace_sum-self.target_activity*dt);self.homeostatic_threshold=max(threshold_min,min(threshold_max,self.latent_threshold))
        self.activity*=activity_decay**dt;self.utility*=utility_decay**dt;self.last_touch_time=now

@dataclass(slots=True)
class RelationElapsedState:
    confidence:float;last_touch_time:float=0.
    def materialize(self,now,decay):self.confidence*=decay**_dt(now,self.last_touch_time);self.last_touch_time=now

@dataclass(slots=True)
class MemoryElapsedState:
    confidence:float;last_confirmed_time:float;last_touch_time:float=0.
    def materialize(self,now,decay):self.confidence*=decay**_dt(now,self.last_touch_time);self.last_touch_time=now
    def recency(self,now,scale):return __import__('math').exp(-_dt(now,self.last_confirmed_time)/scale)

@dataclass(slots=True)
class GoalElapsedState:
    created_time:float;unavailable_since:float|None=None;cooldown_until:float=0.
    def age(self,now):return _dt(now,self.created_time)
    def unavailable_duration(self,now):return 0. if self.unavailable_since is None else _dt(now,self.unavailable_since)
    def cooling_down(self,now):_dt(now,self.created_time);return now<self.cooldown_until

class LazyCognitStore:
    def __init__(self):self.states={};self.materialization_work=0;self.now=0.
    def advance(self,now):_dt(now,self.now);self.now=now
    def touch(self,ids,*policy):
        for i in ids:self.states[i].materialize(self.now,*policy);self.materialization_work+=1
