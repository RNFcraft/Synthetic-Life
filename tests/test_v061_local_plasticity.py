import pytest

from consciousness._native_brain import MicroPolarity, NeurodynamicSubstrate


def _weight(substrate, rho=0):
    return substrate.snapshot()["weight"][rho]


def _pair(causal: bool, delay: float = 100.0):
    substrate = NeurodynamicSubstrate(tau_pre=10., tau_post=10., a_plus=.4, a_minus=.4)
    source = substrate.add_micro_kappa(1.)
    target = substrate.add_micro_kappa(1.)
    substrate.add_micro_rho(source, target, .5, delay, MicroPolarity.EXCITATORY, True)
    first, second = (source, target) if causal else (target, source)
    substrate.inject(first, 1., 0.)
    substrate.advance_to(0.)
    substrate.inject(second, 1., 1.)
    substrate.advance_to(1.)
    return substrate


def test_local_causal_potentiation_and_anti_causal_depression():
    assert _weight(_pair(True)) > .5
    assert _weight(_pair(False)) < .5


def test_shorter_causal_interval_has_stronger_local_update():
    short = _pair(True, 100.)
    long = NeurodynamicSubstrate(tau_pre=10., tau_post=10., a_plus=.4, a_minus=.4)
    a = long.add_micro_kappa(1.); b = long.add_micro_kappa(1.)
    long.add_micro_rho(a, b, .5, 100., MicroPolarity.EXCITATORY, True)
    long.inject(a, 1., 0.); long.advance_to(0.); long.inject(b, 1., 10.); long.advance_to(10.)
    assert _weight(short) > _weight(long) > .5


def test_unrelated_synapse_is_unchanged_and_weights_are_bounded():
    substrate = NeurodynamicSubstrate(a_plus=2., a_minus=2., weight_min=.2, weight_max=.8)
    a = substrate.add_micro_kappa(1.); b = substrate.add_micro_kappa(1.); c = substrate.add_micro_kappa(1.); d = substrate.add_micro_kappa(1.)
    substrate.add_micro_rho(a, b, .5, 100., MicroPolarity.EXCITATORY, True)
    substrate.add_micro_rho(c, d, .5, 100., MicroPolarity.EXCITATORY, True)
    for tick in range(40):
        time = tick * 3.
        substrate.inject(a, 1., time); substrate.advance_to(time)
        substrate.inject(b, 1., time + 1.); substrate.advance_to(time + 1.)
    assert .2 <= _weight(substrate, 0) <= .8
    assert _weight(substrate, 1) == .5


def test_same_time_spikes_cause_no_fake_stdp_regardless_of_order():
    def run(reverse):
        substrate = NeurodynamicSubstrate(a_plus=.9, a_minus=.9)
        a = substrate.add_micro_kappa(1.); b = substrate.add_micro_kappa(1.)
        substrate.add_micro_rho(a, b, .5, 10., MicroPolarity.EXCITATORY, True)
        for node in (b, a) if reverse else (a, b): substrate.inject(node, 1., 0.)
        substrate.advance_to(0.)
        return substrate.snapshot()
    left, right = run(False), run(True)
    assert left["weight"] == right["weight"] == [.5]
    assert left["telemetry"][8:11] == right["telemetry"][8:11] == (0, 0, 0)


def test_inhibitory_polarity_is_fixed_while_magnitude_learns_and_transmits_negative():
    substrate = NeurodynamicSubstrate(a_plus=.5)
    a = substrate.add_micro_kappa(1.); b = substrate.add_micro_kappa(10.)
    substrate.add_micro_rho(a, b, .5, 2., MicroPolarity.INHIBITORY, True)
    substrate.inject(a, 1., 0.); substrate.advance_to(0.)
    substrate.inject(b, 10., 1.); substrate.advance_to(1.)
    learned = _weight(substrate)
    substrate.advance_to(2.)
    assert learned > .5 and substrate.snapshot()["polarity"] == [int(MicroPolarity.INHIBITORY.value)]
    assert substrate.states([b])[0][0] < 0.


def test_homeostasis_is_lazy_and_separate_from_fast_adaptation():
    substrate = NeurodynamicSubstrate(tau_adaptation=1., adaptation_increment=.5, tau_homeostasis=100., homeostasis_spike_increment=.5, refractory_period=0.)
    node = substrate.add_micro_kappa(1.)
    substrate.inject(node, 2., 0.); substrate.advance_to(0.)
    after = substrate.states([node])[0]
    assert after[4] == pytest.approx(.5) and after[9] == pytest.approx(.5)
    substrate.inject(node, 3., 1.); substrate.advance_to(1.)
    repeated = substrate.states([node])[0]
    assert repeated[9] > after[9] and repeated[1] + repeated[4] + repeated[9] > after[1] + after[4] + after[9]
    substrate.advance_to(10.)
    quiet = substrate.states([node])[0]
    assert quiet[4] < .001 and quiet[9] > .4 and substrate.telemetry()[7] == 0


def test_disabled_plasticity_and_zero_homeostasis_match_v060_state():
    def run(tpre, tpost, plus, minus):
        substrate = NeurodynamicSubstrate(tau_pre=tpre, tau_post=tpost, a_plus=plus, a_minus=minus, homeostasis_spike_increment=0.)
        a = substrate.add_micro_kappa(1.); b = substrate.add_micro_kappa(1.)
        substrate.add_micro_rho(a, b, 1., 2., MicroPolarity.EXCITATORY, False)
        substrate.inject(a, 1., 1.); substrate.advance_to(3.)
        return [row[:7] for row in substrate.states([a, b])], substrate.snapshot()["weight"], substrate.telemetry()[:8]
    assert run(1., 2., 9., 8.) == run(100., 200., .001, .002)


def test_snapshot_restore_preserves_learning_homeostasis_and_pending_events():
    a = NeurodynamicSubstrate(tau_pre=7., tau_post=11., a_plus=.5, tau_homeostasis=50., homeostasis_spike_increment=.2)
    source = a.add_micro_kappa(1.); target = a.add_micro_kappa(1.)
    a.add_micro_rho(source, target, .5, 4., MicroPolarity.EXCITATORY, True)
    a.inject(source, 1., 0.); a.advance_to(0.); a.inject(target, 1., 1.); a.advance_to(1.)
    b = NeurodynamicSubstrate(); b.restore(a.snapshot())
    for time in (3., 4., 9.): a.advance_to(time); b.advance_to(time)
    assert a.snapshot() == b.snapshot()


def test_deterministic_replay_and_silent_10k_50k_learning_work():
    def run():
        substrate = _pair(True)
        substrate.advance_to(5.)
        return substrate.snapshot()
    assert run() == run()
    silent = NeurodynamicSubstrate(homeostasis_spike_increment=.5)
    for _ in range(10_000): silent.add_micro_kappa()
    for i in range(50_000): silent.add_micro_rho(i % 10_000, (i + 1) % 10_000, .1, 1., MicroPolarity.EXCITATORY, True)
    silent.advance_to(1_000_000.)
    telemetry = silent.telemetry()
    assert telemetry[3] == telemetry[8] == telemetry[12] == 0
