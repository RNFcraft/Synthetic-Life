import argparse
import time

from simulation import Simulation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic Entity research environment")
    parser.add_argument("--headless", action="store_true", help="run without Pygame")
    parser.add_argument("--ticks", type=int, default=100_000, help="headless tick count")
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--save", metavar="PATH", help="write a JSON snapshot after the run")
    parser.add_argument("--telemetry", metavar="PATH", help="write compact JSONL telemetry")
    return parser.parse_args()


def main() -> None:
    args = parse_args(); simulation = Simulation(seed=args.seed)
    if args.headless:
        started = time.perf_counter(); simulation.run(args.ticks); elapsed = time.perf_counter()-started
        if args.save: simulation.save(args.save)
        if args.telemetry:
            from telemetry.recorder import write_jsonl
            write_jsonl(simulation.telemetry,args.telemetry)
        print(f"ticks executed:       {args.ticks}")
        print(f"elapsed time:         {elapsed:.3f} s")
        print(f"ticks/sec:            {args.ticks/max(elapsed,1e-9):,.0f}")
        print(f"final cognit count:   {len(simulation.core.graph.nodes)}")
        print(f"final relation count: {simulation.core.graph.relation_count}")
        print(f"peak active cognits:  {simulation.telemetry.peak_active_cognits}")
        latest=simulation.telemetry.latest
        if latest:
            print(f"active ratio:         {latest.active_ratio:.3f}")
            print(f"relation density:     {latest.relation_density:.6f}")
            print(f"prediction error:     {latest.prediction_error:.3f}")
            print(f"novelty/tension:      {latest.novelty:.3f} / {latest.internal_tension:.3f}")
            print(f"agency estimate:      {latest.agency_estimate:.4f}")
            print(f"objects/configs:      {latest.objects_spawned} / {latest.unique_object_configurations}")
            print(f"world modification:  {latest.world_modification:.1f}")
            print(f"unique positions:     {latest.unique_positions_visited}")
    else:
        from ui import Renderer
        Renderer(simulation).run()


if __name__ == "__main__":
    main()
