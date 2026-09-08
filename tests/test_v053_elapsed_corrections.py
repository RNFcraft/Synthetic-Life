from copy import deepcopy

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
        confidence = 0.9 if place_id <= 2 else 0.01
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
    assert indexed.last_target_candidate_places == 2
    assert indexed.last_retrieval_candidates == 4
    assert indexed.materialization_work == 4
    for place_id in (1, 2):
        group = indexed._by_place[place_id]
        assert indexed.last_target_structural_scores[place_id] == pytest.approx(
            expected_structural[place_id], rel=1e-13, abs=1e-13
        )
        for memory_id in group:
            assert indexed.structures[memory_id].last_recall_strength == pytest.approx(
                expected_strengths[memory_id], rel=1e-13, abs=1e-13
            )
