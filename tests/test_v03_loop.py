from consciousness.state import TraceEntry,WorkingTrace
from world.actions import ActionType


def entry(tick:int,node:int,action:ActionType,goal:int,error:float=.1)->TraceEntry:
    return TraceEntry(tick,((node,1.),),action,(),error,goal,.2,(7,),.1)


def test_richer_loop_distance() -> None:
    identical=WorkingTrace(32);different=WorkingTrace(32)
    for tick,node in enumerate((1,2,1,2,1,2)):
        identical.append(entry(tick,node,ActionType.IDLE,1))
        different.append(entry(tick,node,ActionType.MOVE_LEFT if tick%2 else ActionType.MOVE_RIGHT,tick))
    assert identical.loop_score(max_period=4,min_repeats=3)>different.loop_score(max_period=4,min_repeats=3)

