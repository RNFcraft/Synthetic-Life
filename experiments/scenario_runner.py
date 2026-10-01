"""Один воспроизводимый запуск, без curriculum/training loop."""
import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import tempfile

from persistence import save_container
from simulation import ContinuousRuntime
from simulation.scenario import (artifact_checksum, artifact_path, canonical_json,
                                 causal_digest, exact, load_artifact, load_scenario,
                                 number, text)


@dataclass(frozen=True, slots=True)
class ExperimentManifest:
    scenario: str
    seconds: float
    brain_in: str | None = None
    brain_out: str | None = None
    world_out: str | None = None
    result_out: str | None = None

    def __post_init__(self):
        text(self.scenario, 4096, "manifest scenario path", True)
        number(self.seconds, 0, 1_000_000, "manifest horizon")
        for path in (self.brain_in, self.brain_out, self.world_out, self.result_out):
            if path is not None:
                text(path, 4096, "manifest path", True)

    def sections(self):
        return {"META": dict(schema="synthetic-life-experiment-manifest", version=1),
                "RUN": {name: getattr(self, name) for name in self.__dataclass_fields__}}


def save_manifest(manifest, path):
    save_container(artifact_path(path), "manifest", manifest.sections())


def load_manifest(path):
    sections = load_artifact(path, "manifest", ("META", "RUN"))
    exact(sections["META"], ("schema", "version"), "manifest metadata")
    if sections["META"] != dict(schema="synthetic-life-experiment-manifest", version=1) or type(sections["META"]["version"]) is not int:
        raise ValueError("unsupported manifest schema/version")
    exact(sections["RUN"], ExperimentManifest.__dataclass_fields__, "manifest invocation")
    return ExperimentManifest(**sections["RUN"])


def _write_result(path, result):
    path = artifact_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(canonical_json(result)+"\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def run_scenario(scenario, seconds, *, brain_in=None, brain_out=None, world_out=None,
                 result_out=None, manifest_checksum=None, declared_paths=None):
    seconds = number(seconds, 0, 1_000_000, "run horizon")
    scenario_path = artifact_path(scenario)
    inputs = [scenario_path.resolve()] + ([artifact_path(brain_in).resolve()] if brain_in is not None else [])
    outputs = [artifact_path(p).resolve() for p in (brain_out, world_out, result_out) if p is not None]
    if len(set(outputs)) != len(outputs) or set(outputs) & set(inputs):
        raise ValueError("outputs must be distinct from input artifacts and each other")
    definition = load_scenario(scenario_path)
    scenario_checksum = artifact_checksum(scenario_path)
    brain_checksum = artifact_checksum(brain_in) if brain_in is not None else None
    runtime = ContinuousRuntime.from_scenario(definition, brain_in)
    runtime.run_until(seconds)
    result = dict(schema="synthetic-life-run-result", version=1, software_milestone="v0.9.1",
                  scenario_name=definition.sections["META"]["name"], scenario_checksum=scenario_checksum,
                  scenario_causal_checksum=definition.causal_checksum, manifest_checksum=manifest_checksum,
                  brain_input_checksum=brain_checksum, seed=definition.seed, horizon=seconds,
                  world_time=runtime.world_time, actions_completed=runtime.actions_completed,
                  cognits=runtime.simulation.core.backend.engine.live_cognit_count,
                  relations=runtime.simulation.core.backend.engine.relation_count,
                  final_digest=causal_digest(runtime),
                  paths={"declared": declared_paths or {"scenario": str(scenario), "brain_in": str(brain_in) if brain_in is not None else None},
                         "resolved": {"scenario": str(scenario_path.resolve()), "brain_in": str(Path(brain_in).resolve()) if brain_in is not None else None}})
    if brain_out is not None:
        runtime.simulation.save_brain(artifact_path(brain_out))
    if world_out is not None:
        runtime.save_world(artifact_path(world_out))
    if result_out is not None:
        _write_result(result_out, result)
    return runtime, result


def run_manifest(path):
    manifest_path = artifact_path(path).resolve()
    manifest = load_manifest(manifest_path)
    paths = {name: getattr(manifest, name) for name in ("scenario", "brain_in", "brain_out", "world_out", "result_out")}
    resolved = {name: str((manifest_path.parent / value).resolve()) if value is not None else None for name, value in paths.items()}
    if any(Path(resolved[name]) == manifest_path for name in ("brain_out", "world_out", "result_out") if resolved[name] is not None):
        raise ValueError("cannot overwrite manifest with run output")
    return run_scenario(resolved.pop("scenario"), manifest.seconds, **resolved,
                        manifest_checksum=artifact_checksum(manifest_path), declared_paths=paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--scenario")
    source.add_argument("--manifest")
    parser.add_argument("--seconds", type=float)
    for option in ("brain-in", "brain-out", "world-out", "result"):
        parser.add_argument("--"+option)
    args = parser.parse_args(argv)
    try:
        if args.manifest:
            if any(getattr(args, name) is not None for name in ("seconds", "brain_in", "brain_out", "world_out", "result")):
                parser.error("manifest invocation does not accept CLI overrides")
            _, result = run_manifest(args.manifest)
        else:
            if args.seconds is None:
                parser.error("--seconds is required with --scenario")
            _, result = run_scenario(args.scenario, args.seconds, brain_in=args.brain_in,
                                    brain_out=args.brain_out, world_out=args.world_out, result_out=args.result)
    except (ValueError, OSError, TypeError) as error:
        parser.error(str(error))
    print(canonical_json(result))


if __name__ == "__main__":
    main()
