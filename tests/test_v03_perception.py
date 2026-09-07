from config import Settings
from consciousness.core import SyntheticEntityCore
from consciousness.patterns import CognitPattern,OnlineSpatialConstraint,SensoryEventKind,SensoryPrimitive
from consciousness.percepts import PerceptualContinuityEngine,PersistentPercept
from world.perception import SensoryCell,SensoryFrame


def event(x:int,y:int,channel:str="occupied",value:int=1)->SensoryPrimitive:
    return SensoryPrimitive(x,y,channel,value,value,SensoryEventKind.OCCUPIED_PRESENT)


def test_empty_active_prediction_and_representation_error() -> None:
    cells=tuple(SensoryCell(x,y,False,0,False,x==y==0) for y in range(-3,4) for x in range(-3,4));core=SyntheticEntityCore(Settings())
    core.step(SensoryFrame(0,3,cells))
    assert not core.state.prediction_error_valid and core.state.prediction_error==0
    assert core.state.representation_error>0 and 0<=core.state.internal_tension<=1
    initial=core.state.representation_error
    for tick in range(1,8):core.step(SensoryFrame(tick,3,cells))
    assert core.state.representation_error<initial


def test_local_percept_creation_and_no_world_identity() -> None:
    engine=PerceptualContinuityEngine(Settings());local=engine.local_percepts((event(0,1),event(1,1)))
    # v0.5.1 participant binding requires adjacent occupied structures to retain identities.
    assert len(local)==2 and all(item.spatial_extent==(1,1) for item in local)
    assert not hasattr(local[0],"object_id") and not hasattr(local[0],"world")


def test_percept_continuity_and_incompatible_pattern() -> None:
    engine=PerceptualContinuityEngine(Settings());first=engine.update((event(0,0),),0,None);identifier=first[0].id
    second=engine.update((event(1,0),),1,None);assert second[0].id==identifier
    engine2=PerceptualContinuityEngine(Settings());old=engine2.update((event(0,0),),0,None)[0]
    new=engine2.update((event(1,0,"state",3),),1,None);assert any(t.id!=old.id for t in new)


def test_percept_missing_and_expiration() -> None:
    settings=Settings(percept_persistence_window=2);engine=PerceptualContinuityEngine(settings);identifier=engine.update((event(0,0),),0,None)[0].id
    engine.update((),1,None);engine.update((),2,None);assert engine.update((event(0,0),),3,None)[0].id==identifier
    engine=PerceptualContinuityEngine(settings);track=engine.update((event(0,0),),0,None)[0]
    for tick in range(1,4):engine.update((),tick,None)
    assert track.closed


def test_sensorimotor_transform_is_learned_not_hardcoded() -> None:
    engine=PerceptualContinuityEngine(Settings());assert all(s.support==0 and s.mean_dx==s.mean_dy==0 for s in engine.transforms.stats.values())
    from world.actions import ActionType
    for tick,x in enumerate(range(7)):
        engine.update((event(x,0),),tick,ActionType.MOVE_RIGHT if tick else None)
    dx,dy,_,confidence=engine.transforms.estimate(ActionType.MOVE_RIGHT)
    assert dx>.5 and abs(dy)<.1 and confidence>.4


def test_spatial_tolerance_and_anchored_vs_tolerant() -> None:
    constraint=OnlineSpatialConstraint();[constraint.update(x) for x in (1.,1.1,.9,1.)];assert constraint.match(1.05)>.7 and constraint.match(5)<.01
    key=(0,0,"occupied",1,SensoryEventKind.OCCUPIED_PRESENT.value);observation=frozenset({(2,1,*key[2:])})
    assert CognitPattern((key,)).match(observation)==0
    assert CognitPattern((key,),is_translation_tolerant=True).match(observation)==1
