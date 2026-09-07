import random

from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.memory import PersistentStructureMemory,SpatialMemory
from consciousness.relational import RelationalStructure


def populated(count=300):
    rng=random.Random(5203);memory=SpatialMemory(Settings());core=SyntheticEntityCore(Settings())
    features=(("occupied",1),("state",1),("appearance",1),("state",2))
    for memory_id in range(1,count+1):
        selected=tuple(sorted(rng.sample(features,rng.randrange(0,3))))
        state=tuple(rng.randrange(3) for _ in range(rng.randrange(0,4)))
        memory.structures[memory_id]=PersistentStructureMemory(memory_id,1000+memory_id,selected,2000+memory_id%19,(float(memory_id%7),float(memory_id%5)),state,rng.random(),rng.randrange(200))
    return memory,core


def test_indexed_structure_match_equals_legacy_full_scan():
    memory,_=populated();rng=random.Random(7);features=(("occupied",1),("state",1),("appearance",1),("state",2))
    for tick in range(40):
        query=tuple(sorted(rng.sample(features,rng.randrange(0,3))));state=tuple(rng.randrange(3) for _ in range(rng.randrange(0,4)));place=2000+rng.randrange(25)
        excluded=set(rng.sample(range(1,301),5));expected=memory._match_structure_legacy(query,state,place,tick,excluded);actual=memory._match_structure(query,state,place,tick,excluded)
        assert (actual.id if actual else None)==(expected.id if expected else None)


def test_indexed_recall_equals_legacy_for_normal_and_target_queries():
    for target in (None,RelationalStructure.from_points(((0,0),(1,0)))):
        memory,core=populated();goals=(1001,1007,2004);expected,expected_strengths=memory.recall_legacy_result(goals,core.graph,250,target)
        actual=memory.recall(goals,core.graph,250,target)
        assert actual==expected
        assert {i:m.last_recall_strength for i,m in memory.structures.items()}==expected_strengths


def test_normal_recall_candidate_count_is_independent_of_unrelated_history():
    memory,core=populated(1000);memory.recall((1001,),core.graph,250)
    assert memory.last_retrieval_total==1000
    assert memory.last_retrieval_candidates==1


def test_indexes_follow_state_update_deletion_and_restore():
    memory,_=populated(20);memory._ensure_indexes();item=memory.structures[1];old=item.remembered_state;item.remembered_state=(99,);memory._reindex_state(item,old)
    assert 1 in memory._by_state[(0,99)]
    memory.remove_structure(1);assert 1 not in memory.structures and 1 not in memory._indexed_ids
    restored=SpatialMemory(Settings());restored.restore(memory.to_dict())
    assert restored._indexed_ids==set(restored.structures)
