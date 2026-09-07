from curriculum import TARGET_PATTERNS,evaluate_pattern
from world.objects import WorldObject

def objects(points):return [WorldObject(i,x,y) for i,(x,y) in enumerate(points)]

def test_curriculum_patterns_are_external_and_translation_invariant()->None:
    assert evaluate_pattern(objects(((7,8),(8,8))),TARGET_PATTERNS["pair"])
    assert evaluate_pattern(objects(((4,4),(4,5),(4,6))),TARGET_PATTERNS["line3"])
    assert not evaluate_pattern(objects(((1,1),(3,3),(7,7))),TARGET_PATTERNS["l"])

def test_advanced_patterns()->None:
    assert evaluate_pattern(objects(((4,4),(5,4),(4,5),(5,5))),TARGET_PATTERNS["square2"])
    assert evaluate_pattern(objects(((5,4),(4,5),(5,5),(6,5),(5,6))),TARGET_PATTERNS["plus"])
