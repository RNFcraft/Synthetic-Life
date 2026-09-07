from consciousness.cognit import Cognit


def test_activation_decay_and_aging() -> None:
    cognit = Cognit(1, threshold=0.2)
    assert cognit.activate(0.5, 4)
    assert cognit.last_activated_cognitive_tick == 4
    cognit.decay(0.5)
    assert cognit.activity == 0.25 and cognit.age == 1
