from dataclasses import replace
import pytest

from config import Settings
from consciousness.native_engine import EventScheduler,RuntimeEventType
from simulation.continuous import ContinuousRuntime
from world.perception import BodySense,SensoryCell,SensoryFrame


DIRECTION={"NORTH":(0,-1),"SOUTH":(0,1),"EAST":(1,0),"WEST":(-1,0)}
RIGHT={"NORTH":(1,0),"SOUTH":(-1,0),"EAST":(0,1),"WEST":(0,-1)}


def _runtime(seed=6401):return ContinuousRuntime(seed,Settings(sensory_neural_enabled=True))


def _place_relative(runtime,forward=1,lateral=0):
    body=runtime.simulation.world.body;fx,fy=DIRECTION[body.orientation];rx,ry=RIGHT[body.orientation]
    runtime.simulation.world.initialize_controlled_objects([(body.x+forward*fx+lateral*rx,body.y+forward*fy+lateral*ry)])
    return runtime.simulation.world.perceive(runtime.observation_ordinal)


def _experience(runtime,frame,start=0.,repeats=12):
    runtime.scheduler=EventScheduler()
    for index in range(repeats):
        time=start+index*.2;_,frontier=runtime.neural_sensory.transduce(frame,time);runtime.advance_neural_to(frontier);runtime.run_until(frontier)


def test_real_world_frame_uses_one_batched_native_boundary_without_direct_cognit_birth():
    runtime=_runtime();_place_relative(runtime,1,1);runtime.scheduler=EventScheduler();runtime.scheduler.schedule(0.,RuntimeEventType.SENSORY_CHANGE);runtime.run_until(.05)
    engine=runtime.simulation.core.backend.engine;telemetry=runtime.neural_sensory.telemetry;neural=engine.neurodynamic_substrate().telemetry()
    assert telemetry.sensory_frames_transduced==1 and telemetry.active_receptors>=4
    assert telemetry.sensory_receptor_events==telemetry.active_receptors and neural[3]>=telemetry.active_receptors and neural[4]>=telemetry.active_receptors
    assert engine.cognit_count==0 and engine.assembly_cognit_mapping()==[]


def test_one_shot_has_neural_activity_without_consolidated_assembly_or_cognit():
    runtime=_runtime();frame=_place_relative(runtime,1,-1);_experience(runtime,frame,repeats=1);engine=runtime.simulation.core.backend.engine
    assert engine.neurodynamic_substrate().telemetry()[4]>0
    assert not any(row[-1] for row in engine.neurodynamic_substrate().assemblies())
    assert engine.assembly_cognit_mapping()==[]


def test_recurrent_real_sensory_experience_forms_one_stable_assembly_cognit():
    runtime=_runtime();frame=_place_relative(runtime,1,-1);_experience(runtime,frame);engine=runtime.simulation.core.backend.engine
    mapping=engine.assembly_cognit_mapping();assert len(mapping)==1
    before=(mapping,engine.cognit_count);_experience(runtime,frame,3.,6)
    assert engine.assembly_cognit_mapping()==before[0] and engine.cognit_count==before[1]


def test_distinct_retinotopic_world_experiences_form_distinct_representations():
    runtime=_runtime();left=_place_relative(runtime,1,-1);_experience(runtime,left)
    right=_place_relative(runtime,1,1);assert set(runtime.neural_sensory.receptor_ids(left))!=set(runtime.neural_sensory.receptor_ids(right));_experience(runtime,right,3.)
    mapping=runtime.simulation.core.backend.engine.assembly_cognit_mapping()
    assert len(mapping)==2 and len({row[0] for row in mapping})==len({row[1] for row in mapping})==2


def test_raw_channel_permutation_and_retinotopy_only_permute_receptors():
    runtime=_runtime();transducer=runtime.neural_sensory
    def frame(x,state,appearance):return SensoryFrame(0,4,(SensoryCell(x,0,True,state,False,False,appearance),))
    a=dict(transducer.receptor_ids(frame(-1,1,2)));b=dict(transducer.receptor_ids(frame(-1,2,1)));moved=dict(transducer.receptor_ids(frame(1,1,2)))
    base=transducer._cell_base(-1,0);assert base+3+1 in a and base+3+2 in b
    assert base+3+transducer.bins+2 in a and base+3+transducer.bins+1 in b
    assert set(a)!=set(b) and set(a).isdisjoint(set(moved))


def test_same_frame_cell_permutation_is_exact_and_creates_no_fake_temporal_edges():
    cells=(SensoryCell(-1,0,True,1,False,False,2),SensoryCell(1,0,True,2,False,False,1))
    left,right=_runtime(),_runtime();a=SensoryFrame(0,4,cells);b=SensoryFrame(0,4,tuple(reversed(cells)))
    for runtime,frame in ((left,a),(right,b)):
        runtime.scheduler=EventScheduler();_,frontier=runtime.neural_sensory.transduce(frame,2.5);runtime.advance_neural_to(frontier);runtime.run_until(frontier)
    assert left.simulation.core.backend.engine.neurodynamic_substrate().snapshot()==right.simulation.core.backend.engine.neurodynamic_substrate().snapshot()
    assert all(not row[2] for row in left.simulation.core.backend.engine.neurodynamic_substrate().assemblies())


def test_body_channels_are_bounded_nonsemantic_receptors():
    runtime=_runtime();t=runtime.neural_sensory;frame=SensoryFrame(0,4,(),BodySense(True,False,True,False,True,.5));active=dict(t.receptor_ids(frame));base=t.cell_count*t.cell_stride
    assert active=={base:1.,base+2:1.,base+4:1.,base+5:.5}


def test_receptor_bank_is_bounded_stable_and_rejects_malformed_inputs():
    runtime=_runtime();t=runtime.neural_sensory;count=t.substrate.micro_kappa_count;frame=_place_relative(runtime,1,1)
    assert t.receptor_ids(frame)==t.receptor_ids(frame) and t.substrate.micro_kappa_count==count==t.receptor_count<=t.settings.sensory_neural_max_receptors
    with pytest.raises(ValueError):t.receptor_ids(SensoryFrame(0,4,(SensoryCell(0,0,True,t.bins,False,False,0),)))
    with pytest.raises(ValueError):t.receptor_ids(SensoryFrame(0,4,(SensoryCell(9,0,True,0,False,False,0),)))
    with pytest.raises(ValueError):ContinuousRuntime(1,replace(Settings(),sensory_neural_enabled=True,sensory_neural_max_receptors=10))
    with pytest.raises(ValueError):ContinuousRuntime(1,replace(Settings(),sensory_neural_enabled=True,sensory_neural_max_injections_per_frame=410))


def test_saturated_bounded_frame_encodes_every_expected_receptor_without_truncation():
    runtime=_runtime();t=runtime.neural_sensory;r=t.radius
    cells=tuple(SensoryCell(x,y,True,t.bins-1,True,True,t.bins-1) for y in range(-r,r+1) for x in range(-r,r+1))
    frame=SensoryFrame(0,r,cells,BodySense(True,True,True,True,True,1.));active=t.receptor_ids(frame)
    assert len(active)==t.maximum_frame_injections==411
    assert len({row[0] for row in active})==len(active)<=t.settings.sensory_neural_max_injections_per_frame


def test_sensory_snapshot_restore_preserves_topology_pending_events_and_continuation(tmp_path):
    runtime=_runtime();frame=_place_relative(runtime,1,-1);_experience(runtime,frame,repeats=2)
    _,frontier=runtime.neural_sensory.transduce(frame,.4);runtime.advance_neural_to(frontier);path=tmp_path/"sensory.seworld";runtime.save_world(path)
    restored=ContinuousRuntime.load_world(path);runtime.run_until(frontier);restored.run_until(frontier)
    with pytest.raises(ValueError,match="incompatible"):ContinuousRuntime.load_world(path,Settings())
    le,re=runtime.simulation.core.backend.engine,restored.simulation.core.backend.engine
    assert runtime.neural_sensory.receptor_ids(frame)==restored.neural_sensory.receptor_ids(frame)
    assert le.neurodynamic_substrate().snapshot()==re.neurodynamic_substrate().snapshot()
    assert le.assembly_bridge_state()==re.assembly_bridge_state() and runtime.scheduler_state()==restored.scheduler_state()


def test_production_world_recurrence_forms_and_reuses_one_assembly_cognit():
    runtime=_runtime();_place_relative(runtime,1,-1);runtime.scheduler=EventScheduler();runtime.simulation.core.begin_continuous_cognition=lambda generation:False
    for index in range(5):runtime.scheduler.schedule(index*1.1,RuntimeEventType.SENSORY_CHANGE)
    runtime.run_until(4.5);engine=runtime.simulation.core.backend.engine;mapping=engine.assembly_cognit_mapping()
    assert len(mapping)==1;identity=mapping[0]
    for index in range(5,8):runtime.scheduler.schedule(index*1.1,RuntimeEventType.SENSORY_CHANGE)
    runtime.run_until(8.)
    assert engine.assembly_cognit_mapping()==[identity]
    assert sum(node.kind=="NEURAL_ASSEMBLY" for node in runtime.simulation.core.graph.nodes.values())==1


def test_disabled_and_silent_paths_do_zero_sensory_work():
    disabled=ContinuousRuntime(6402);disabled.run_until(.2);assert disabled.neural_sensory is None and disabled.simulation.core.backend.engine.neurodynamic_substrate().micro_kappa_count==0
    enabled=_runtime();before=enabled.neural_sensory.telemetry.sensory_frames_transduced;enabled.scheduler=EventScheduler();enabled.run_until(10.)
    assert enabled.neural_sensory.telemetry.sensory_frames_transduced==before


def test_disabled_seworld_without_sensory_config_loads_backward_compatibly(tmp_path):
    runtime=ContinuousRuntime(6403);path=tmp_path/"legacy-compatible.seworld";runtime.save_world(path);restored=ContinuousRuntime.load_world(path)
    assert restored.neural_sensory is None
