from .simulation import Simulation
from .clock import SpeedScheduler
from .multi import MultiEntitySimulation

def __getattr__(name: str):
    if name in {"ContinuousRuntime", "RenderSnapshot"}:
        from .continuous import ContinuousRuntime, RenderSnapshot
        return ContinuousRuntime if name == "ContinuousRuntime" else RenderSnapshot
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["Simulation", "MultiEntitySimulation", "SpeedScheduler", "ContinuousRuntime", "RenderSnapshot"]

