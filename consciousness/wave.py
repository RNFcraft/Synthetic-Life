from collections import defaultdict
from dataclasses import dataclass
from config import Settings
from .graph import CognitiveGraph
from .relation import RelationType


@dataclass(frozen=True, slots=True)
class WaveResult:
    active_ids: frozenset[int]
    energy: float
    steps: int
    transmitted_energy: float = 0.0


class ActivityWaveEngine:
    """Sparse propagation with a conserved outgoing energy budget."""
    def __init__(self, settings: Settings) -> None: self.settings = settings

    def propagate(self, graph: CognitiveGraph, seeds: set[int], tick: int) -> WaveResult:
        frontier = {i: graph.nodes[i].activity for i in seeds if i in graph.nodes}
        activated = set(frontier); total_energy = sum(frontier.values()); transmitted_total = 0.0; steps = 0
        cap = min(self.settings.wave_max_steps, self.settings.max_wave_propagation_steps)
        while frontier and steps < cap:
            incoming: dict[int, float] = defaultdict(float)
            for source_id,available in sorted(frontier.items()):
                excitatory=[]; inhibitory=[]
                for relation in graph.outgoing(source_id):
                    confidence=relation.confidence
                    raw=max(0.0,relation.strength*confidence)
                    (inhibitory if relation.relation_type is RelationType.INHIBITORY else excitatory).append((relation,raw))
                raw_sum=sum(raw for _,raw in excitatory)
                budget=max(0.0,available)*self.settings.wave_retention
                if raw_sum:
                    for relation,raw in excitatory:
                        energy=budget*raw/raw_sum; incoming[relation.target_id]+=energy; transmitted_total+=energy; relation.last_used_cognitive_tick=tick
                inhibition_sum=sum(raw for _,raw in inhibitory)
                if inhibition_sum:
                    for relation,raw in inhibitory:
                        incoming[relation.target_id]-=budget*raw/inhibition_sum; relation.last_used_cognitive_tick=tick
            next_frontier={}
            for target_id,energy in sorted(incoming.items()):
                target=graph.nodes.get(target_id)
                if target and target_id not in activated and target.receive(energy,tick,self.settings,wave_step=True):
                    next_frontier[target_id]=min(max(0.0,energy),self.settings.max_wave_energy)
                    activated.add(target_id); total_energy+=max(0.0,energy)
            frontier=next_frontier; steps+=1
        return WaveResult(frozenset(activated),min(total_energy,self.settings.max_wave_energy),steps,transmitted_total)
