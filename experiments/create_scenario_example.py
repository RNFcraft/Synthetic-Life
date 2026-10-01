"""Создание маленькой canonical presentation fixture, не survival experiment."""
from dataclasses import replace
from pathlib import Path
from config import Settings
from simulation.persisted_settings import scenario_configuration
from simulation.scenario import ScenarioDefinition, save_scenario
from experiments.scenario_runner import ExperimentManifest, save_manifest


def example():
    settings = replace(Settings(), world_width=8, world_height=8, object_count=0,
                       max_objects=8, resource_max_live=8, resource_nutrient_payload=31.,
                       resource_hydration_payload=27., interoception_enabled=True,
                       homeostatic_valuation_enabled=True, delayed_homeostatic_prediction_enabled=True)
    return ScenarioDefinition.from_sections({
        "META": dict(schema="synthetic-life-scenario", version=1, name="Workbench smoke",
                     description="Physical initial-condition fixture, not a survival claim", tags=["infrastructure"]),
        "CONFIG": dict(seed=9100, settings=scenario_configuration(settings)),
        "INITIAL": dict(bodies=[dict(id=0, x=3, y=4, orientation="NORTH", appearance=1)],
                        objects=[dict(id=1, x=3, y=3, state=1, resource_channel=1, nutrients=31., hydration=0.),
                                 dict(id=2, x=4, y=3, state=2, resource_channel=2, nutrients=0., hydration=27.),
                                 dict(id=3, x=1, y=1, state=0, resource_channel=0, nutrients=0., hydration=0.)],
                        held_objects=[], physiology=dict(energy=60., nutrients=20., hydration=35.))})


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    save_scenario(example(), root / "scenarios/examples/workbench_smoke.sescenario")
    save_manifest(ExperimentManifest("../../scenarios/examples/workbench_smoke.sescenario", .6),
                  root / "experiments/manifests/workbench_smoke.semanifest")
