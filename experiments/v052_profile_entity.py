"""Profile the normal native Entity path; diagnostic artifact only."""
from __future__ import annotations

import argparse
import cProfile
import json
import pstats
from pathlib import Path
from time import perf_counter

from simulation import Simulation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--output", default="runs/v052-entity-profile")
    args = parser.parse_args()
    simulation = Simulation(args.seed, backend="native")
    profiler = cProfile.Profile()
    started = perf_counter()
    profiler.enable()
    simulation.run(args.steps)
    profiler.disable()
    elapsed = perf_counter() - started
    prefix = Path(args.output)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    profiler.dump_stats(str(prefix.with_suffix(".prof")))
    stats = pstats.Stats(profiler)
    rows = []
    for (filename, line, function), values in sorted(
        stats.stats.items(), key=lambda item: item[1][3], reverse=True
    )[:80]:
        primitive, calls, own, cumulative, _ = values
        rows.append({"file": filename, "line": line, "function": function,
                     "calls": calls, "primitive_calls": primitive,
                     "own_seconds": own, "cumulative_seconds": cumulative,
                     "seconds_per_call": cumulative / max(1, calls)})
    result = {"seed": args.seed, "steps": args.steps, "wall_seconds": elapsed,
              "cognits": len(simulation.core.graph.nodes),
              "relations": simulation.core.graph.relation_count,
              "full_graph_sync_calls": simulation.core.backend.full_graph_sync_calls,
              "top": rows}
    prefix.with_suffix(".json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
