from config import Settings
from consciousness.cognit import Cognit
from consciousness.graph import CognitiveGraph
from consciousness.learning import TransitionModel
from consciousness.state import TraceEntry,WorkingTrace
from consciousness.wave import ActivityWaveEngine
from world.actions import ActionType


def test_homeostasis_prevents_permanent_saturation_and_recovers_threshold() -> None:
    settings=Settings(cognit_activity_decay=0.55,homeostasis_learning_rate=0.08)
    node=Cognit(1,target_activity=settings.homeostasis_target_activity);initial=node.homeostatic_threshold
    observed=[]
    for tick in range(80):
        active=node.receive(0.35,tick,settings);node.homeostatic_step(active,settings);observed.append(node.activity)
    raised=node.homeostatic_threshold
    assert raised>initial and min(observed[-20:])<0.95
    for _ in range(160):node.homeostatic_step(False,settings)
    assert node.activity<1e-6 and node.homeostatic_threshold<raised


def _transmission(outgoing:int)->float:
    settings=Settings(wave_retention=0.6,wave_max_steps=1);graph=CognitiveGraph();source=graph.add_cognit();source.activity=1.0
    for _ in range(outgoing):
        target=graph.add_cognit();target.threshold=0.01;edge,_=graph.connect(source.id,target.id);edge.strength=edge.confidence=1.0
    return ActivityWaveEngine(settings).propagate(graph,{source.id},0).transmitted_energy


def test_energy_is_conserved_across_fanout() -> None:
    assert abs(_transmission(1)-_transmission(100))<1e-9
    assert _transmission(100)<=0.6+1e-9


def test_lift_rejects_frequent_baseline_and_accepts_dependency() -> None:
    model=TransitionModel();A,B,C=1,2,3
    for tick in range(200):
        previous={A} if tick%10==0 else {9}
        current={B};current.update({C} if tick%10==0 else set())
        model.observe(previous,ActionType.IDLE,current)
    assert model.metrics(A,B)[3]<1.1
    assert model.metrics(A,C)[3]>5.0


def test_prediction_learns_then_reports_broken_expectation() -> None:
    model=TransitionModel();A,B=1,2
    for _ in range(30):model.observe({A},ActionType.IDLE,{B})
    predicted=model.predict({A},ActionType.IDLE)[B]
    assert predicted>0.75
    broken_error=abs(0.0-predicted)
    for _ in range(50):model.observe({A},ActionType.IDLE,set())
    assert broken_error>0.75 and model.predict({A},ActionType.IDLE)[B]<predicted


def test_self_action_conditioned_prediction() -> None:
    model=TransitionModel();A,B,C=1,2,3
    for _ in range(30):
        model.observe({A},ActionType.MOVE_RIGHT,{B});model.observe({A},ActionType.MOVE_LEFT,{C})
    assert model.predict({A},ActionType.MOVE_RIGHT)[B]>model.predict({A},ActionType.MOVE_LEFT)[B]
    assert model.predict({A},ActionType.MOVE_LEFT)[C]>model.predict({A},ActionType.MOVE_RIGHT)[C]


def test_internal_loop_score_discriminates_periodic_trace() -> None:
    periodic=WorkingTrace(32);varied=WorkingTrace(32)
    for tick,node in enumerate([1,2,1,2,1,2]):
        periodic.append(TraceEntry(tick,((node,1.0),),ActionType.IDLE,(),0.1,None,0.1))
    for tick,node in enumerate([1,2,3,4,5,6]):
        varied.append(TraceEntry(tick,((node,1.0),),ActionType.IDLE,(),0.1,None,0.1))
    assert periodic.loop_score(max_period=4,min_repeats=3)>0.9
    assert varied.loop_score(max_period=4,min_repeats=3)<0.5

