from copy import deepcopy
import random

import pytest

from config import Settings
from consciousness.memory import PersistentStructureMemory, SpatialMemory
from consciousness.relational import RelationalStructure


class EmptyGraph:
    @staticmethod
    def outgoing_targets(_):
        return ()


def make_large_target_memory():
    memory = SpatialMemory(Settings())
    rows = {}
    memory_id = 1
    for place_id in range(1, 5001):
        distance = 1.0 if place_id <= 2 else 3.0
        confidence = 0.9 if place_id <= 4 else 0.01
        for x in (0.0, distance):
            rows[memory_id] = PersistentStructureMemory(
                memory_id,
                20_000 + memory_id,
                ((place_id, 0, "occupied", 1),),
                place_id,
                (x, 0.0),
                (1,),
                confidence,
                0,
                last_confirmed_time_seconds=0.0,
                last_touch_time_seconds=0.0,
            )
            memory_id += 1
    memory.structures = rows
    memory._rebuild_indexes()
    memory.set_world_time(0.0)
    return memory


def test_indexed_target_recall_matches_full_scan_without_touching_all_memory():
    indexed = make_large_target_memory()
    oracle = deepcopy(indexed)
    target = RelationalStructure.from_points(((0.0, 0.0), (1.0, 0.0)))

    oracle.set_world_time(1000.0)
    for item in oracle.structures.values():
        oracle._materialize(item)
    expected_ids, expected_strengths, expected_structural = (
        oracle.recall_legacy_target_result((), EmptyGraph(), 0, target)
    )

    indexed.set_world_time(1000.0)
    actual_ids = indexed.recall((), EmptyGraph(), 0, target)

    assert actual_ids == expected_ids
    assert len(indexed.structures) == 10_000
    assert len(indexed._by_place) == 5_000
    assert indexed.last_target_candidate_places == 4
    assert indexed.last_retrieval_candidates == 8
    assert indexed.materialization_work == 8
    for place_id in (1, 2,3,4):
        group = indexed._by_place[place_id]
        assert indexed.last_target_structural_scores[place_id] == pytest.approx(
            expected_structural[place_id], rel=1e-13, abs=1e-13
        )
        for memory_id in group:
            assert indexed.structures[memory_id].last_recall_strength == pytest.approx(
                expected_strengths[memory_id], rel=1e-13, abs=1e-13
            )


def make_groups(groups):
    memory=SpatialMemory(Settings());rows={};memory_id=1
    for place_id,(points,confidence,last_confirmed) in enumerate(groups,1):
        for point in points:
            rows[memory_id]=PersistentStructureMemory(memory_id,1000+memory_id,((place_id,0,"occupied",1),),place_id,point,(1,),confidence,last_confirmed,last_confirmed_time_seconds=float(last_confirmed),last_touch_time_seconds=float(last_confirmed));memory_id+=1
    memory.structures=rows;memory._rebuild_indexes();memory.set_world_time(0.);return memory


def compare_to_oracle(memory,target,associated=(),now=0.):
    indexed=deepcopy(memory);oracle=deepcopy(memory);indexed.set_world_time(now);oracle.set_world_time(now)
    for item in oracle.structures.values():oracle._materialize(item)
    expected,strengths,_=oracle.recall_legacy_target_result(associated,EmptyGraph(),0,target)
    actual=indexed.recall(associated,EmptyGraph(),0,target)
    assert actual==expected
    for memory_id,strength in strengths.items():
        if strength>=.12:assert indexed.structures[memory_id].last_recall_strength==pytest.approx(strength,rel=1e-12,abs=1e-12)
    return indexed,expected,strengths


def test_no_token_overlap_high_confidence_is_admitted_but_low_is_rejected():
    target=RelationalStructure.from_points(((0.,0.),(1.,0.)))
    memory=make_groups(((((0.,0.),(3.,0.)),.9,0),(((0.,0.),(3.,0.)),.05,0)))
    indexed,recalled,_=compare_to_oracle(memory,target)
    assert {1,1001,1002}<=recalled and not ({2,1003,1004}&recalled)
    assert indexed.last_target_candidate_places==1


def test_participant_count_recency_and_direct_association_are_conservative():
    target=RelationalStructure.from_points(((0.,0.),(1.,0.)))
    groups=[]
    for count in (1,2,3,5,10):groups.append((tuple((float(i*3),0.) for i in range(count)),.9,0))
    memory=make_groups(tuple(groups));indexed,expected,_=compare_to_oracle(memory,target,associated=(1001,),now=100.)
    assert {1,1001}<=expected
    assert indexed.last_target_candidate_places>=1


def test_direct_association_bypasses_a_structurally_impossible_bound():
    target=RelationalStructure.from_points(((0.,0.),(1.,0.)))
    memory=make_groups((((((0.,0.),),.2,0)),))
    indexed,expected,_=compare_to_oracle(memory,target,associated=(1001,))
    assert expected=={1,1001} and indexed.last_target_candidate_places==1


def test_stale_and_fresh_memories_keep_exact_final_decision():
    target=RelationalStructure.from_points(((0.,0.),(1.,0.)))
    memory=make_groups(((((0.,0.),(3.,0.)),.9,0),(((0.,0.),(3.,0.)),.9,10_000)))
    indexed,expected,_=compare_to_oracle(memory,target,now=10_000.)
    assert {2,1003,1004}<=expected and not ({1,1001,1002}&expected)
    assert indexed.last_target_candidate_places==2


def test_randomized_conservative_target_recall_has_no_false_negatives():
    rng=random.Random(731)
    for _ in range(80):
        groups=[]
        for _place in range(rng.randint(2,12)):
            count=rng.randint(1,5);points=tuple((float(i*rng.randint(1,4)),float((i*i+rng.randint(0,2))%4)) for i in range(count));groups.append((points,rng.uniform(.01,1.),rng.randint(0,20)))
        target_count=rng.randint(1,5);target=RelationalStructure.from_points(tuple((float(i*rng.randint(1,3)),float(i%2)) for i in range(target_count)))
        memory=make_groups(tuple(groups));now=float(rng.randint(20,60));compare_to_oracle(memory,target,now=now)
