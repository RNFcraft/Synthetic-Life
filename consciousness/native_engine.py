"""Coarse Python API for the authoritative v0.5.2 native graph substrate."""
try:
    from ._native_brain import NativeBrainEngine, EvidenceConfig, WorldRuntime, EventScheduler, RuntimeEvent, RuntimeEventType
except ImportError as error:
    raise ImportError("Build the native backend with: cmake -S cpp -B cpp/build -A x64; cmake --build cpp/build --config Release") from error

__all__=["NativeBrainEngine","EvidenceConfig","WorldRuntime","EventScheduler","RuntimeEvent","RuntimeEventType"]
