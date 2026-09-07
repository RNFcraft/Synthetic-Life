from collections import Counter,deque
from dataclasses import dataclass
from .patterns import CognitPattern,PatternNode,PatternParticipantType,PatternRelation,PatternRelationType


@dataclass(slots=True)
class CompositeCandidate:
    sequence:tuple[int,...];support:int=0;stability:float=0.;prediction_gain:float=0.;compression_gain:float=0.;redundancy:float=0.;score:float=0.


class CompositeTracker:
    """Discovers only short observed temporal sequences; never enumerates κ combinations."""
    def __init__(self,settings)->None:
        self.settings=settings;self.recent:deque[tuple[int,...]]=deque(maxlen=settings.composite_window_max)
        self.candidates:dict[tuple[int,...],CompositeCandidate]={};self.composites:dict[tuple[int,...],int]={};self.dependencies:Counter[int]=Counter()
        self.created_total=0;self.deleted_total=0

    def observe(self,active:set[int],graph)->tuple[set[int],list[CognitPattern]]:
        compact=tuple(sorted(active)[:self.settings.composite_max_participants]);self.recent.append(compact);activated=set();births=[]
        for length in range(self.settings.composite_window_min,min(len(self.recent),self.settings.composite_window_max)+1):
            states=list(self.recent)[-length:];sequence=tuple(i for state in states for i in state)
            sequence=tuple(dict.fromkeys(sequence))[:self.settings.composite_max_participants]
            if len(sequence)<self.settings.composite_min_participants:continue
            if sequence in self.composites:activated.add(self.composites[sequence]);continue
            if len(self.candidates)>=self.settings.max_composite_candidates and sequence not in self.candidates:continue
            candidate=self.candidates.setdefault(sequence,CompositeCandidate(sequence));candidate.support+=1
            candidate.stability=min(1.,candidate.support/self.settings.composite_min_support)
            candidate.prediction_gain=min(1.,sum(graph.nodes[i].novelty for i in sequence if i in graph.nodes)/max(1,len(sequence)))
            raw=max(0.,len(sequence)-1);candidate.compression_gain=raw/(raw+2)
            overlap=max((len(set(sequence)&set(s))/max(1,len(set(sequence)|set(s))) for s in self.composites),default=0.);candidate.redundancy=overlap
            frequency=min(1.,candidate.support/self.settings.composite_min_support);complexity=len(sequence)/self.settings.composite_max_participants
            candidate.score=(self.settings.composite_frequency_weight*frequency+self.settings.composite_stability_weight*candidate.stability+
              self.settings.composite_prediction_weight*candidate.prediction_gain+self.settings.composite_compression_weight*candidate.compression_gain-
              self.settings.composite_redundancy_weight*candidate.redundancy-self.settings.composite_complexity_weight*complexity)
            depths=[graph.nodes[i].pattern.abstraction_depth for i in sequence if i in graph.nodes and graph.nodes[i].pattern]
            depth=1+max(depths,default=0)
            if candidate.support>=self.settings.composite_min_support and candidate.score>=self.settings.composite_birth_threshold and depth<=self.settings.max_abstraction_depth:
                nodes=tuple(PatternNode(PatternParticipantType.COGNIT,i) for i in sequence)
                relations=tuple(PatternRelation(i,i+1,PatternRelationType.BEFORE,1,1) for i in range(len(sequence)-1))
                births.append(CognitPattern((),nodes=nodes,relations=relations,occurrence_count=candidate.support,stability=candidate.stability,
                  predictive_value=candidate.prediction_gain,compression_gain=candidate.compression_gain,redundancy=candidate.redundancy,abstraction_depth=depth))
        return activated,births

    def register(self,pattern:CognitPattern,node_id:int)->None:
        sequence=tuple(int(n.reference) for n in pattern.nodes if n.participant_type is PatternParticipantType.COGNIT)
        self.composites[sequence]=node_id
        for child in sequence:self.dependencies[child]+=1
        self.created_total+=1

    def is_protected(self,node_id:int)->bool:return self.dependencies[node_id]>0

