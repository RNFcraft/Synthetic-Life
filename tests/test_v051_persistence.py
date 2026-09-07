import pytest
from persistence import ContainerError,inspect_container
from simulation import Simulation

def test_world_container_exact_roundtrip(tmp_path)->None:
    sim=Simulation(91);sim.run(3);path=tmp_path/"state.seworld";sim.save_world(path);loaded=Simulation.load_world(path)
    assert loaded.snapshot_data()==sim.snapshot_data();assert inspect_container(path)["magic"]=="SEWORLD1"

def test_brain_has_no_world_and_loads_into_fresh_runtime(tmp_path)->None:
    sim=Simulation(92);sim.run(3);path=tmp_path/"mind.sebrain";sim.save_brain(path);fresh=Simulation(1);fresh.load_brain(path)
    assert len(fresh.core.graph.nodes)==len(sim.core.graph.nodes)
    assert b'"world"' not in path.read_bytes()

def test_checksum_corruption_is_explicit(tmp_path)->None:
    sim=Simulation(93);path=tmp_path/"bad.seworld";sim.save_world(path);raw=bytearray(path.read_bytes());raw[-1]^=1;path.write_bytes(raw)
    with pytest.raises(ContainerError,match="corrupt section"):Simulation.load_world(path)
