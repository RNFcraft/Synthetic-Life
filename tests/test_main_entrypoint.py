import itertools
import subprocess
import sys
from pathlib import Path

import pytest

import main
from simulation import ContinuousRuntime


class FakeObserver:
    def __init__(self,running=True):self.running=running;self.starts=0;self.stops=0
    @property
    def is_running(self):return self.running
    def start(self):self.starts+=1;return True
    def stop(self):self.stops+=1;self.running=False


def _causal(runtime):
    native_time,native_sequence=runtime.simulation.world.native.time_state();frontier=runtime.simulation.core.continuous_frontier
    return (runtime.scheduler_state(),runtime.simulation.event_sequence.value,native_time,native_sequence,runtime.simulation.rng.getstate(),runtime.simulation.world.to_dict(),runtime.maintenance_ordinal,runtime.cognition_generation,runtime.actions_completed,None if frontier is None else (frontier.generation,frontier.phase,frontier.committed))


def _clock(values):
    iterator=iter(values);last=values[-1]
    return lambda:next(iterator,last)


def test_headless_runner_uses_continuous_runtime_to_exact_world_time():
    runtime=main.create_runtime(seed=1001);assert isinstance(runtime,ContinuousRuntime)
    main.run_headless(runtime,1.25);assert runtime.world_time==1.25


def test_live_style_partitioning_matches_headless_trajectory():
    headless=main.run_headless(main.create_runtime(1002),1.2);live=main.create_runtime(1002);observer=FakeObserver()
    main.drive_live(live,observer,1.0,1.2,_clock([10.,10.2,10.55,10.9,11.3]),lambda _:None)
    assert observer.starts==observer.stops==1 and _causal(live)==_causal(headless)


@pytest.mark.parametrize("clock",([0.,.1,.2,.4,.8,1.], [0.,.01,.02,.03,.5,.51,.99,1.]))
def test_observer_polling_frequency_does_not_control_world_time(clock):
    runtime=main.create_runtime(1003);observer=FakeObserver();main.drive_live(runtime,observer,1.,1.,_clock(clock),lambda _:None)
    assert runtime.world_time==1.


def test_window_close_exits_without_causal_mutation():
    runtime=main.create_runtime(1004);before=_causal(runtime);observer=FakeObserver(False)
    main.drive_live(runtime,observer,monotonic=lambda:0.,sleep=lambda _:None)
    assert observer.starts==observer.stops==1 and _causal(runtime)==before


def test_keyboard_interrupt_stops_observer_and_propagates():
    runtime=main.create_runtime(1005);observer=FakeObserver();calls=itertools.count()
    def interrupted():
        if next(calls):raise KeyboardInterrupt
        return 0.
    with pytest.raises(KeyboardInterrupt):main.drive_live(runtime,observer,monotonic=interrupted,sleep=lambda _:None)
    assert observer.stops==1


def test_production_source_has_no_legacy_renderer_or_step_loop():
    source=open(main.__file__,encoding="utf-8").read()
    assert "from ui" not in source and "Renderer(" not in source and "simulation.step(" not in source and "--ticks" not in source


def test_missing_native_observer_has_actionable_build_message():
    class Value:pass
    runtime=Value();runtime.simulation=Value();runtime.simulation.world=Value();runtime.simulation.world.native=Value()
    with pytest.raises(RuntimeError,match="SE_BUILD_OBSERVER=ON"):main.create_native_observer(runtime)


def test_production_headless_save_and_load_use_seworld(tmp_path,capsys):
    path=tmp_path/"production.seworld";main.main(["--headless","--seconds","0.3","--seed","1007","--save",str(path)])
    restored=main.create_runtime(load_path=str(path));assert restored.world_time==.3
    main.main(["--headless","--seconds","0.45","--load",str(path)])
    assert "world time:           0.450000 s" in capsys.readouterr().out


def test_clean_source_production_entrypoint_executes_without_bytecode():
    result=subprocess.run(
        [sys.executable,"-B","main.py","--headless","--seconds","0"],
        cwd=Path(__file__).resolve().parents[1],capture_output=True,text=True,
        check=False,
    )
    assert result.returncode==0,result.stderr
    assert "world time:           0.000000 s" in result.stdout
