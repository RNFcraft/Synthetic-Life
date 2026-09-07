from __future__ import annotations
from dataclasses import dataclass
from world.actions import ActionType

@dataclass(slots=True)
class ContextEvidence:
    context:frozenset[int];action:ActionType;trials:int=0;effects:int=0;mismatch_delta:float=0.

class AffordanceEvidence:
    """Generalized experience counts for epistemic value; durable prediction remains in rho."""
    def __init__(self):self.entries=[];self.unique_trials=0;self.last_epistemic={};self.last_effect_probability={};self._lookup_cache={}
    def _entry(self,context,action,create=False):
        key=(frozenset(context),action)
        if not create and key in self._lookup_cache:return self._lookup_cache[key]
        best=None;score=0.
        for item in self.entries:
            if item.action is not action:continue
            union=context|item.context;value=len(context&item.context)/max(1,len(union))
            if value>score:best,score=item,value
        if best is None or score<.35:
            if not create:return None
            best=ContextEvidence(frozenset(context),action);self.entries.append(best);self.unique_trials+=1;self._lookup_cache.clear()
        if not create:self._lookup_cache[key]=best
        return best
    def epistemic(self,context,action):
        item=self._entry(frozenset(context),action);trials=item.trials if item else 0;uncertainty=1/(1+trials);effect=(item.effects+.5)/(trials+1) if item else .5;value=uncertainty*(.5+abs(.5-effect));self.last_epistemic[action]=value;self.last_effect_probability[action]=effect;return value
    def observe(self,context,action,effect,mismatch_delta):
        item=self._entry(frozenset(context),action,True);item.trials+=1;item.effects+=int(effect);item.mismatch_delta+=(mismatch_delta-item.mismatch_delta)/item.trials;self._lookup_cache.clear()
    def predicted_progress(self,context,action):
        # Target value is deliberately not stored here; graph rho owns prediction.
        return 0.
    def to_dict(self):return [{"context":sorted(x.context),"action":x.action.name,"trials":x.trials,"effects":x.effects,"mismatch_delta":x.mismatch_delta} for x in self.entries]
    def restore(self,data):self.entries=[ContextEvidence(frozenset(x["context"]),ActionType[x["action"]],x["trials"],x["effects"],x["mismatch_delta"]) for x in data];self.unique_trials=len(self.entries);self._lookup_cache.clear()
