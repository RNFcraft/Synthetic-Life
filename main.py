import argparse
import time
from collections.abc import Callable

from simulation import ContinuousRuntime


OBSERVER_BUILD_HELP = """Native observer is unavailable.
Rebuild with:
    cmake -S cpp -B cpp/build -DSE_BUILD_OBSERVER=ON
    cmake --build cpp/build --config Release"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic Entity continuous native runtime")
    parser.add_argument("--headless", action="store_true", help="run the continuous runtime without a window")
    parser.add_argument("--seconds", type=float, help="simulated seconds to execute (headless default: 100)")
    parser.add_argument("--speed", type=float, default=1.0, help="live simulated-time multiplier")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--save", metavar="PATH", help="write a continuous .seworld snapshot after execution")
    parser.add_argument("--load", metavar="PATH", help="load a continuous .seworld snapshot before execution")
    parser.add_argument("--telemetry", metavar="PATH", help="deprecated legacy tick telemetry; unavailable in production continuous mode")
    args=parser.parse_args(argv)
    if args.seconds is not None and args.seconds<0:parser.error("--seconds must be non-negative")
    if args.speed<=0:parser.error("--speed must be positive")
    if args.telemetry:parser.error("--telemetry is legacy tick-only and is not available in the continuous production entrypoint")
    return args


def create_runtime(seed:int=12345,load_path:str|None=None)->ContinuousRuntime:
    return ContinuousRuntime.load_world(load_path) if load_path else ContinuousRuntime(seed=seed)


def run_headless(runtime:ContinuousRuntime,seconds:float)->ContinuousRuntime:
    if seconds<runtime.world_time:raise ValueError("--seconds precedes the loaded WorldTime")
    runtime.run_until(seconds);return runtime


def drive_live(runtime:ContinuousRuntime,observer,speed:float=1.0,seconds:float|None=None,
               monotonic:Callable[[],float]=time.monotonic,sleep:Callable[[float],None]=time.sleep)->ContinuousRuntime:
    if speed<=0:raise ValueError("speed must be positive")
    if seconds is not None and seconds<0:raise ValueError("seconds must be non-negative")
    if not observer.start():raise RuntimeError("native observer did not start")
    if seconds is not None and seconds<runtime.world_time:raise ValueError("--seconds precedes the loaded WorldTime")
    real_start=monotonic();sim_start=runtime.world_time;deadline=seconds
    try:
        while observer.is_running:
            target=sim_start+max(0.0,monotonic()-real_start)*speed
            if deadline is not None:target=min(target,deadline)
            if target>runtime.world_time:runtime.run_until(target)
            if deadline is not None and runtime.world_time>=deadline:break
            sleep(.005)
    finally:observer.stop()
    return runtime


def create_native_observer(runtime:ContinuousRuntime):
    native=runtime.simulation.world.native
    if not hasattr(native,"create_observer"):raise RuntimeError(OBSERVER_BUILD_HELP)
    try:
        runtime.publish_brain_snapshot()
        return native.create_brain_observer(runtime.simulation.core.backend.engine)
    except (AttributeError,RuntimeError) as error:raise RuntimeError(OBSERVER_BUILD_HELP) from error


def main(argv:list[str]|None=None)->None:
    args=parse_args(argv);runtime=create_runtime(args.seed,args.load);started=time.perf_counter()
    if args.headless:
        seconds=100.0 if args.seconds is None else args.seconds;run_headless(runtime,seconds)
    else:
        observer=create_native_observer(runtime)
        try:drive_live(runtime,observer,args.speed,args.seconds)
        except KeyboardInterrupt:pass
    elapsed=time.perf_counter()-started
    if args.save:runtime.save_world(args.save)
    print(f"world time:           {runtime.world_time:.6f} s")
    print(f"host elapsed:         {elapsed:.3f} s")
    print(f"actions completed:    {runtime.actions_completed}")
    print(f"final cognit count:   {len(runtime.simulation.core.graph.nodes)}")
    print(f"final relation count: {runtime.simulation.core.graph.relation_count}")


if __name__=="__main__":main()
