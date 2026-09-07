from config import Settings
from consciousness.graph import CognitiveGraph
from consciousness.wave import ActivityWaveEngine


def test_wave_propagates_decays_and_stops_on_cycle() -> None:
    graph=CognitiveGraph(); a=graph.add_cognit(); b=graph.add_cognit(); c=graph.add_cognit()
    a.activity=1.0; b.threshold=c.threshold=0.01
    for source,target in ((a.id,b.id),(b.id,c.id),(c.id,a.id)):
        edge,_=graph.connect(source,target); edge.strength=edge.confidence=1.0
    result=ActivityWaveEngine(Settings(wave_retention=0.5, wave_max_steps=5)).propagate(graph,{a.id},0)
    assert result.active_ids == frozenset({a.id,b.id,c.id})
    assert result.steps <= 5 and b.activity > c.activity > 0
