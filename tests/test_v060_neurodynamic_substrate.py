import copy
import math
import pytest

from consciousness._native_brain import MicroPolarity,NeurodynamicSubstrate
from consciousness.native_engine import NativeBrainEngine


def state(s,i=0):return s.states([i])[0]


def test_lazy_leak_is_analytical_and_silent_advance_does_no_work():
    s=NeurodynamicSubstrate(tau_membrane=1_000_000.);n=s.add_micro_kappa(10.);s.inject(n,1.,0.);s.advance_to(0.);s.advance_to(1_000_000.)
    assert s.telemetry()[3:5]==(1,0) and s.telemetry()[-1]==0
    assert state(s)[0]==pytest.approx(math.exp(-1.)) and s.snapshot()["potential"][n]==1.


def test_single_spike_reset_refractory_and_adaptation():
    s=NeurodynamicSubstrate(refractory_period=2.,adaptation_increment=.25);n=s.add_micro_kappa(1.);s.inject(n,1.,0.);s.advance_to(0.);x=state(s)
    assert x[0]==0. and x[3]==2. and x[4]==.25 and x[6]==1 and s.telemetry()[4]==1


def test_delayed_chain_and_inhibition_same_time_aggregation():
    s=NeurodynamicSubstrate();a=s.add_micro_kappa(1.);b=s.add_micro_kappa(1.);s.add_micro_rho(a,b,1.,2.,MicroPolarity.EXCITATORY);s.inject(a,1.,1.);s.advance_to(2.9);assert state(s,b)[6]==0;s.advance_to(3.);assert state(s,b)[6]==1
    def run(order):
        x=NeurodynamicSubstrate();n=x.add_micro_kappa(1.)
        for amp in order:x.inject(n,amp,1.)
        x.advance_to(1.);return state(x),x.telemetry()
    assert run((1e16,-1e16,1.5,-.75))==run((-.75,1.5,-1e16,1e16)) and run((1.5,-.75))[0][6]==0


def test_real_inhibitory_micro_rho_is_signed_and_order_independent():
    def run(reverse):
        s=NeurodynamicSubstrate();e=s.add_micro_kappa(1.);i=s.add_micro_kappa(1.);target=s.add_micro_kappa(1.)
        edges=((e,target,1.5,2.,MicroPolarity.EXCITATORY),(i,target,.75,2.,MicroPolarity.INHIBITORY))
        for edge in reversed(edges) if reverse else edges:s.add_micro_rho(*edge)
        for source in (i,e) if reverse else (e,i):s.inject(source,1.,0.)
        s.advance_to(2.);return state(s,target),s.snapshot()
    left,left_snapshot=run(False);right,right_snapshot=run(True)
    assert left==right and left[0]==pytest.approx(.75) and left[6]==0
    assert left_snapshot["potential"]==right_snapshot["potential"]


def test_refractory_and_adaptation_decay():
    s=NeurodynamicSubstrate(refractory_period=2.,adaptation_increment=.5,tau_adaptation=10.);n=s.add_micro_kappa(1.);s.inject(n,1.,0.);s.advance_to(0.);s.inject(n,2.,1.);s.advance_to(1.);assert state(s)[6]==1 and s.telemetry()[5]==1
    s.inject(n,1.,2.);s.advance_to(2.);assert state(s)[6]==1
    s.inject(n,1.,100.);s.advance_to(100.);assert state(s)[6]==2 and state(s)[4]>.5


def test_snapshot_restore_pending_events_and_replay_are_exact():
    a=NeurodynamicSubstrate();x=a.add_micro_kappa(1.);y=a.add_micro_kappa(1.);a.add_micro_rho(x,y,1.,4.,MicroPolarity.EXCITATORY);a.inject(x,1.,1.);a.advance_to(1.);snap=a.snapshot();b=NeurodynamicSubstrate();b.restore(snap)
    for time in (3.,5.,9.):a.advance_to(time);b.advance_to(time)
    assert a.snapshot()==b.snapshot()


def test_snapshot_restore_preserves_custom_physiology_on_different_instance():
    a=NeurodynamicSubstrate(3.,5.,2.,-.25,.4,17);x=a.add_micro_kappa(1.);y=a.add_micro_kappa(1.)
    a.add_micro_rho(x,y,1.2,4.,MicroPolarity.EXCITATORY);a.inject(x,1.2,1.);a.advance_to(1.)
    b=NeurodynamicSubstrate();b.restore(a.snapshot())
    for time in (3.,5.,9.):a.advance_to(time);b.advance_to(time)
    assert a.snapshot()==b.snapshot()


def test_restore_rejects_invalid_physiology_topology_and_pending_events():
    a=NeurodynamicSubstrate();x=a.add_micro_kappa();y=a.add_micro_kappa();a.add_micro_rho(x,y,1.,1.,MicroPolarity.EXCITATORY)
    a.inject(x,.2,1.);a.inject(y,.2,2.);snapshot=a.snapshot()
    corruptions=(
        lambda d:d.__setitem__("tau_membrane",0.),
        lambda d:d.__setitem__("weight",[float("inf")]),
        lambda d:d.__setitem__("polarity",[2]),
        lambda d:d.__setitem__("pending",[d["pending"][0],d["pending"][0]]),
    )
    for corrupt in corruptions:
        bad=copy.deepcopy(snapshot);corrupt(bad)
        with pytest.raises(ValueError):NeurodynamicSubstrate().restore(bad)


def test_identical_experiment_has_exact_deterministic_replay():
    def run():
        s=NeurodynamicSubstrate(tau_membrane=7.,tau_adaptation=13.,adaptation_increment=.2)
        a=s.add_micro_kappa(1.);b=s.add_micro_kappa(1.)
        s.add_micro_rho(a,b,1.1,.5,MicroPolarity.EXCITATORY)
        s.inject(a,1.,1.);s.inject(a,.3,4.);s.inject(b,-.2,1.5)
        s.advance_to(10.);return s.snapshot()
    assert run()==run()


def test_silent_10k_50k_has_zero_event_work_and_validation():
    s=NeurodynamicSubstrate();[s.add_micro_kappa() for _ in range(10_000)]
    for i in range(50_000):s.add_micro_rho(i%10_000,(i+1)%10_000,.1,1.,MicroPolarity.EXCITATORY)
    s.advance_to(1_000_000.);t=s.telemetry();assert (s.micro_kappa_count,s.micro_rho_count,t[3],t[4],t[-1])==(10_000,50_000,0,0,0)
    with pytest.raises(ValueError):s.inject(0,1.,float("nan"))
    with pytest.raises(ValueError):s.add_micro_rho(0,1,1.,0.,MicroPolarity.EXCITATORY)


def test_native_backend_owns_empty_substrate_by_default():
    s=NativeBrainEngine().neurodynamic_substrate();assert s.telemetry()==(0,0,0,0,0,0,0,0)
