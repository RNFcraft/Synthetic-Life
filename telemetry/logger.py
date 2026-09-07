from collections import deque


class EventLogger:
    def __init__(self, capacity: int = 10000) -> None:
        self.events: deque[str] = deque(maxlen=capacity)

    def emit(self, tick: int, event: str) -> None:
        self.events.append(f"[{tick}] {event}")

