from config import Settings
from consciousness.composites import CompositeTracker
from consciousness.graph import CognitiveGraph


def build()->tuple[CognitiveGraph,CompositeTracker,list[int]]:
    graph=CognitiveGraph();ids=[graph.add_cognit().id for _ in range(3)];return graph,CompositeTracker(Settings(composite_min_support=3)),ids


def test_temporal_composite_birth_and_activation() -> None:
    graph,tracker,(a,b,c)=build();born=[]
    for _ in range(5):
        for node in (a,b,c):
            active,births=tracker.observe({node},graph)
            for pattern in births:
                composite=graph.add_cognit();composite.pattern=pattern;tracker.register(pattern,composite.id);born.append(composite.id)
    assert born and tracker.candidates[(a,b,c)].support>=3
    active=set()
    for node in (a,b,c):active,_=tracker.observe({node},graph)
    assert set(born)&active


def test_single_or_random_order_does_not_create_same_composite() -> None:
    graph,tracker,(a,b,c)=build();tracker.observe({a},graph);tracker.observe({b},graph);_,births=tracker.observe({c},graph)
    assert not births
    for sequence in ((a,c,b),(b,a,c),(c,b,a)):
        for node in sequence:tracker.observe({node},graph)
    assert tracker.candidates.get((a,b,c)).support<3


def test_recursive_composite_and_dependency_integrity() -> None:
    graph,tracker,(a,b,c)=build()
    from consciousness.patterns import CognitPattern,PatternNode,PatternParticipantType
    pattern=CognitPattern((),nodes=(PatternNode(PatternParticipantType.COGNIT,a),PatternNode(PatternParticipantType.COGNIT,b)),abstraction_depth=1)
    composite=graph.add_cognit();composite.pattern=pattern;tracker.register(pattern,composite.id)
    assert tracker.is_protected(a) and tracker.is_protected(b)
    for _ in range(4):tracker.observe({composite.id},graph);_,births=tracker.observe({c},graph)
    assert any(p.abstraction_depth==2 for p in births)

