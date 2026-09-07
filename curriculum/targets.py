"""External structural curriculum. Nothing here is exposed as world truth to Core."""
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

def _normalise(points:Iterable[tuple[int,int]])->frozenset[tuple[int,int]]:
    values=tuple(points);ox=min(x for x,_ in values);oy=min(y for _,y in values)
    return frozenset((x-ox,y-oy) for x,y in values)

@dataclass(frozen=True)
class TargetPattern:
    name:str
    offsets:frozenset[tuple[int,int]]
    level:int

    def __init__(self,name:str,offsets:Iterable[tuple[int,int]],level:int):
        object.__setattr__(self,"name",name);object.__setattr__(self,"offsets",_normalise(offsets));object.__setattr__(self,"level",level)

TARGET_PATTERNS={
 "pair":TargetPattern("pair",((0,0),(1,0)),1),
 "line3":TargetPattern("line3",((0,0),(1,0),(2,0)),2),
 "l":TargetPattern("l",((0,0),(0,1),(1,1)),3),
 "square2":TargetPattern("square2",((0,0),(1,0),(0,1),(1,1)),4),
 "plus":TargetPattern("plus",((1,0),(0,1),(1,1),(2,1),(1,2)),5),
}

def _variants(points:frozenset[tuple[int,int]]):
    current=set(points)
    for _ in range(4):
        yield _normalise(current);yield _normalise((-x,y) for x,y in current)
        current={(-y,x) for x,y in current}

def evaluate_pattern(objects:Iterable[object],target:TargetPattern)->bool:
    """Translation/rotation/reflection invariant external success check; never reward."""
    positions={(int(o.x),int(o.y)) for o in objects}
    n=len(target.offsets)
    return any(_normalise(group) in set(_variants(target.offsets)) for group in combinations(positions,n))
