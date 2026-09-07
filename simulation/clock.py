from dataclasses import dataclass


@dataclass(slots=True)
class SimulationClock:
    tick:int=0
    def advance(self)->None:self.tick+=1


class SpeedScheduler:
    """Wall-clock scheduler only; logical cognition receives no elapsed time."""
    SPEEDS=(0.0,0.1,0.25,0.5,1.0,2.0,5.0,10.0,100.0,1000.0,-1.0)
    def __init__(self,speed:float=1.0)->None:self.speed=speed;self.credit=0.0;self._last:float|None=None;self._step_pending=0
    @property
    def paused(self)->bool:return self.speed==0.0
    @property
    def max_mode(self)->bool:return self.speed<0.0
    def set_speed(self,speed:float)->None:
        if speed not in self.SPEEDS:raise ValueError(f"unsupported speed {speed}")
        self.speed=speed;self.credit=0.0;self._last=None
    def step_once(self)->None:self._step_pending+=1
    def due_ticks(self,now:float,max_batch:int=1000)->int:
        if self._step_pending:self._step_pending-=1;self._last=now;return 1
        if self.max_mode:self._last=now;return max_batch
        if self._last is None:self._last=now;return 0
        elapsed=max(0.0,now-self._last);self._last=now
        if self.paused:return 0
        self.credit+=elapsed*self.speed;ticks=min(max_batch,int(self.credit));self.credit-=ticks;return ticks
