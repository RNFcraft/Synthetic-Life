from collections import Counter
from dataclasses import dataclass
from enum import Enum,auto
from world.actions import ActionType


class TieResolutionMethod(Enum):
    NONE=auto();LEAST_USED=auto();OLDEST_USED=auto();ROTATING_CURSOR=auto()


@dataclass(frozen=True,slots=True)
class TieDecision:
    action:ActionType;tied:tuple[ActionType,...];method:TieResolutionMethod


class SymmetryPreservingTieResolver:
    """Balances only actions that the current model cannot distinguish."""
    def __init__(self,epsilon:float)->None:self.epsilon=epsilon;self.cursor=0

    def resolve(self,scores:dict[ActionType,float],history:list[ActionType]|tuple[ActionType,...]=())->TieDecision:
        best=max(scores.values());tied=tuple(a for a in ActionType if a in scores and best-scores[a]<=self.epsilon)
        if len(tied)==1:return TieDecision(tied[0],tied,TieResolutionMethod.NONE)
        counts=Counter(a for a in history if a in tied);least=min(counts.get(a,0) for a in tied)
        candidates=[a for a in tied if counts.get(a,0)==least]
        if len(candidates)==1:return TieDecision(candidates[0],tied,TieResolutionMethod.LEAST_USED)
        last={a:-1 for a in candidates}
        for index,action in enumerate(history):
            if action in last:last[action]=index
        oldest=min(last.values());old=[a for a in candidates if last[a]==oldest]
        if len(old)==1:return TieDecision(old[0],tied,TieResolutionMethod.OLDEST_USED)
        action=old[self.cursor%len(old)];self.cursor=(self.cursor+1)%max(1,len(ActionType))
        return TieDecision(action,tied,TieResolutionMethod.ROTATING_CURSOR)

    def to_dict(self)->dict[str,int|float]:return {"epsilon":self.epsilon,"cursor":self.cursor}
