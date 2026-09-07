from math import isclose
from consciousness.graph import CognitiveGraph


def test_relation_creation_strengthening_and_removal() -> None:
    graph = CognitiveGraph(); a=graph.add_cognit(); b=graph.add_cognit()
    relation, created = graph.connect(a.id, b.id)
    assert created and graph.relation_count == 1
    same, created = graph.connect(a.id, b.id)
    same.strength += 0.1
    assert not created and isclose(relation.strength, 0.3)
    graph.remove_cognit(b.id)
    assert graph.relation_count == 0
