"""Set reductions and durable counter order must be independent of hashseed."""
import json
import os
from pathlib import Path
import subprocess
import sys


def test_memory_similarity_and_feature_counters_match_across_hashseeds():
    code='''
import json
from config import Settings
from consciousness.memory import SpatialMemory
from consciousness.memory_matching import weighted_similarity
left=tuple((i,0,'boundary' if i%2 else 'occupied',1) for i in range(40))
right=left[:27]+((40,0,'state',1),)
weights={feature:.2+.8*(i%7/7) for i,feature in enumerate(left)}
memory=SpatialMemory(Settings())
memory._learn_stability(frozenset((*feature,1) for feature in left))
print(json.dumps([weighted_similarity(left,right,weights),memory.to_dict()]))
'''
    rows=[subprocess.check_output([sys.executable,'-c',code],cwd=Path(__file__).parents[1],
          env={**os.environ,'PYTHONHASHSEED':seed},text=True) for seed in ('1','2','777')]
    assert rows[0]==rows[1]==rows[2]
    assert 0<json.loads(rows[0])[0]<1
