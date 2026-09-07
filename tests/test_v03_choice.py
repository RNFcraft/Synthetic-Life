from collections import Counter
from config import Settings
from consciousness.choice import SymmetryPreservingTieResolver,TieResolutionMethod
from consciousness.core import SyntheticEntityCore
from consciousness.state import FutureEstimate
from world.actions import ActionType


MOVES=(ActionType.MOVE_UP,ActionType.MOVE_RIGHT,ActionType.MOVE_DOWN,ActionType.MOVE_LEFT)


def test_tie_balance() -> None:
    resolver=SymmetryPreservingTieResolver(1e-6);history=[];scores={a:1.0 for a in MOVES}
    for _ in range(10_000):history.append(resolver.resolve(scores,history[-64:]).action)
    counts=Counter(history);assert max(counts.values())-min(counts.values())<=1


def test_tie_does_not_override_best() -> None:
    resolver=SymmetryPreservingTieResolver(.01);scores={a:1.0 for a in MOVES};scores[ActionType.MOVE_RIGHT]=1.02
    for _ in range(100):
        decision=resolver.resolve(scores,[]);assert decision.action is ActionType.MOVE_RIGHT and decision.method is TieResolutionMethod.NONE


def test_near_tie_balances() -> None:
    resolver=SymmetryPreservingTieResolver(.01);history=[];scores={a:1.0+i*.001 for i,a in enumerate(MOVES)}
    for _ in range(400):history.append(resolver.resolve(scores,history[-64:]).action)
    counts=Counter(history);assert max(counts.values())-min(counts.values())<=1


def test_rotational_action_score_symmetry() -> None:
    core=SyntheticEntityCore(Settings());core.state.futures=core._imagine(set())
    scores={a:core.state.futures[a].score for a in MOVES};rotated={MOVES[(i+1)%4]:scores[a] for i,a in enumerate(MOVES)}
    assert all(abs(rotated[MOVES[(i+1)%4]]-scores[a])<1e-12 for i,a in enumerate(MOVES))

