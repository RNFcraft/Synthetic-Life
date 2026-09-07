from collections import Counter,defaultdict,deque
from math import prod
from world.actions import ActionType


class TransitionModel:
    """Local sufficient statistics for baseline-corrected temporal/action transitions."""
    def __init__(self,window_size:int=512)->None:
        self.total_steps=0;self.source_counts:Counter[int]=Counter();self.target_counts:Counter[int]=Counter()
        self.pair_counts:Counter[tuple[int,int]]=Counter();self.action_source_counts:Counter[tuple[int,ActionType]]=Counter()
        self.action_pair_counts:Counter[tuple[int,ActionType,int]]=Counter();self.action_counts:Counter[ActionType]=Counter()
        self.outgoing_targets:dict[int,set[int]]=defaultdict(set)
        self.window_size=window_size;self.history:deque[tuple[set[int],ActionType,set[int]]]=deque()

    def observe(self,previous:set[int],action:ActionType|None,current:set[int])->None:
        if action is None:return
        self.history.append((set(previous),action,set(current)))
        self.total_steps+=1;self.action_counts[action]+=1
        self.target_counts.update(current);self.source_counts.update(previous)
        for source in previous:
            self.action_source_counts[source,action]+=1
            for target in current:
                self.pair_counts[source,target]+=1;self.action_pair_counts[source,action,target]+=1
                self.outgoing_targets[source].add(target)
        if len(self.history)>self.window_size:self._forget(self.history.popleft())

    def clear_evidence(self) -> None:
        """Clear transient observations without touching materialized graph knowledge."""
        self.total_steps=0;self.source_counts.clear();self.target_counts.clear();self.pair_counts.clear()
        self.action_source_counts.clear();self.action_pair_counts.clear();self.action_counts.clear();self.outgoing_targets.clear();self.history.clear()

    def _forget(self,item:tuple[set[int],ActionType,set[int]])->None:
        previous,action,current=item;self.total_steps-=1;self.action_counts[action]-=1
        for target in current:self.target_counts[target]-=1
        for source in previous:
            self.source_counts[source]-=1;self.action_source_counts[source,action]-=1
            for target in current:
                self.pair_counts[source,target]-=1;self.action_pair_counts[source,action,target]-=1
                if self.pair_counts[source,target]<=0:
                    self.pair_counts.pop((source,target),None);self.outgoing_targets[source].discard(target)

    def metrics(self,source:int,target:int)->tuple[int,float,float,float]:
        support=self.pair_counts[source,target];conditional=support/max(1,self.source_counts[source])
        baseline=self.target_counts[target]/max(1,self.total_steps);lift=conditional/max(baseline,1e-9)
        return support,conditional,baseline,lift

    def action_probability(self,source:int,action:ActionType,target:int)->tuple[float,int]:
        support=self.action_pair_counts[source,action,target];trials=self.action_source_counts[source,action]
        return support/max(1,trials),trials

    def candidate_targets(self,active:set[int])->set[int]:
        result:set[int]=set()
        for source in active:result.update(self.outgoing_targets.get(source,()))
        return result

    def predict(self,active:set[int],action:ActionType|None=None)->dict[int,float]:
        result={}
        for target in self.candidate_targets(active):
            causes=[]
            for source in active:
                base_support,conditional,_,_=self.metrics(source,target)
                probability=conditional
                if action is not None:
                    conditioned,trials=self.action_probability(source,action,target)
                    if trials: probability=(conditioned*trials+conditional*2)/(trials+2)
                confidence=base_support/(base_support+4)
                causes.append(max(0.0,min(1.0,probability*confidence)))
            result[target]=1.0-prod(1.0-p for p in causes)
        return result

    def controllability(self,active:set[int],target:int)->float:
        values=[]
        for action in ActionType:
            estimates=[self.action_probability(source,action,target) for source in active]
            supported=[p for p,n in estimates if n>0]
            if supported:values.append(sum(supported)/len(supported))
        return max(values)-min(values) if len(values)>1 else 0.0

    def to_dict(self)->dict:
        return {"total_steps":self.total_steps,"source_counts":dict(self.source_counts),"target_counts":dict(self.target_counts),
          "pair_counts":[[s,t,n] for (s,t),n in self.pair_counts.items()],"action_source_counts":[[s,a.name,n] for (s,a),n in self.action_source_counts.items()],
          "action_pair_counts":[[s,a.name,t,n] for (s,a,t),n in self.action_pair_counts.items()],"action_counts":{a.name:n for a,n in self.action_counts.items()},
          "window_size":self.window_size,"history":[[sorted(p),a.name,sorted(c)] for p,a,c in self.history]}

    def restore(self,data:dict)->None:
        self.total_steps=data.get("total_steps",0);self.source_counts=Counter({int(k):v for k,v in data.get("source_counts",{}).items()});self.target_counts=Counter({int(k):v for k,v in data.get("target_counts",{}).items()})
        self.pair_counts=Counter({(s,t):n for s,t,n in data.get("pair_counts",[])})
        self.action_source_counts=Counter({(s,ActionType[a]):n for s,a,n in data.get("action_source_counts",[])})
        self.action_pair_counts=Counter({(s,ActionType[a],t):n for s,a,t,n in data.get("action_pair_counts",[])})
        self.action_counts=Counter({ActionType[a]:n for a,n in data.get("action_counts",{}).items()})
        self.outgoing_targets=defaultdict(set)
        for source,target in self.pair_counts:self.outgoing_targets[source].add(target)
        self.window_size=data.get("window_size",self.window_size);self.history=deque((set(p),ActionType[a],set(c)) for p,a,c in data.get("history",[]))
