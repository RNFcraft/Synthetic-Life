from simulation import Simulation


def test_seed_is_reproducible() -> None:
    first, second = Simulation(seed=123), Simulation(seed=123)
    for _ in range(50): first.step(); second.step()
    assert first.world.to_dict() == second.world.to_dict()
    assert first.core.graph.to_dict() == second.core.graph.to_dict()


def test_world_uses_logical_consciousness_ticks() -> None:
    simulation=Simulation(seed=4); simulation.run(25)
    assert simulation.clock.tick == 25
    assert simulation.world.world_tick_count == 25


def test_snapshot_v4_continuation(tmp_path) -> None:
    simulation=Simulation(seed=8); simulation.run(30)
    path=tmp_path/"snapshot.json"; simulation.save(str(path)); restored=Simulation.load(str(path))
    assert restored.clock.tick == simulation.clock.tick
    assert restored.world.to_dict() == simulation.world.to_dict()
    assert restored.core.graph.to_dict() == simulation.core.graph.to_dict()
    simulation.step(); restored.step()
    assert restored.world.to_dict() == simulation.world.to_dict()


def test_v02_snapshot_is_rejected(tmp_path) -> None:
    path=tmp_path/"old.json";path.write_text('{"version": 2}',encoding="utf-8")
    try:Simulation.load(str(path))
    except ValueError as error:assert "expected v4" in str(error)
    else:raise AssertionError("v0.1 snapshot must not load silently")


def test_deterministic_spawn_continuation(tmp_path) -> None:
    from config import Settings
    settings=Settings(spawn_interval_min=3,spawn_interval_max=5)
    simulation=Simulation(seed=18,settings=settings);simulation.run(20);path=tmp_path/"spawn-v4.json";simulation.save(str(path))
    a=Simulation.load(str(path),settings);b=Simulation.load(str(path),settings);a.run(20);b.run(20)
    assert a.world.to_dict()==b.world.to_dict() and a.snapshot_data()["random_state"]==b.snapshot_data()["random_state"]
