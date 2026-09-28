from config import Settings
from consciousness import SyntheticEntityCore
from consciousness.cognit import Cognit


def test_activation_decay_and_aging() -> None:
    cognit = Cognit(1, threshold=0.2)
    assert cognit.activate(0.5, 4)
    assert cognit.last_activated_cognitive_tick == 4
    cognit.decay(0.5)
    assert cognit.activity == 0.25 and cognit.age == 1


def test_synthetic_entity_core_standalone_initialization() -> None:
    core = SyntheticEntityCore(Settings(), backend="python")
    assert core.homeostatic_projection is None
    assert core.backend is None
    assert len(core.graph.nodes) == 0

