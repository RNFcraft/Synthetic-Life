"""Host validation of a detached configuration draft; never episode mutation."""
from dataclasses import replace
from config import Settings
from .persisted_settings import scenario_configuration, restore_scenario_settings

EDITABLE_FIELDS = (
    'world_width',
    'world_height',
    'object_count',
    'max_objects',
    'entity_count',
    'perception_radius',
    'resource_spawning_enabled',
    'resource_spawn_interval_seconds',
    'resource_max_live',
    'resource_nutrient_payload',
    'resource_hydration_payload',
    'physiology_initial_energy',
    'physiology_initial_nutrients',
    'physiology_initial_hydration',
    'physiology_max_energy',
    'physiology_max_nutrients',
    'physiology_max_hydration',
    'physiology_energy_target',
    'physiology_nutrient_target',
    'physiology_hydration_target',
    'physiology_basal_body_rate',
    'physiology_basal_brain_rate',
    'physiology_hydration_rate',
    'physiology_digestion_rate',
    'physiology_digestion_efficiency',
    'physiology_movement_cost',
    'physiology_interaction_cost',
    'interoception_enabled',
    'interoception_bins',
    'homeostatic_valuation_enabled',
    'delayed_homeostatic_prediction_enabled',
    'planning_horizon',
    'planning_beam_width',
    'planning_passive_prediction_depth',
    'planning_prediction_time_horizon',
    'planning_time_discount',
    'planning_temporal_probability_floor',
)
PRESETS = ("Current", "Classic Baseline", "Workbench Sparse", "Empty Experiment")


def configuration_draft(settings=None, seed=12345, preset=0):
    settings = settings or Settings()
    return {**{name: getattr(settings, name) for name in EDITABLE_FIELDS}, "seed": seed, "preset": preset}


def preset_draft(name, seed=12345):
    if name not in PRESETS[1:]:
        raise ValueError("unknown workbench preset")
    index = PRESETS.index(name)
    settings = replace(Settings(), object_count=(25, 3, 0)[index-1], max_objects=(25, 150, 150)[index-1])
    return configuration_draft(settings, seed, index)


def validate_draft(draft, current=None):
    if not isinstance(draft, dict) or set(draft) != set(EDITABLE_FIELDS) | {"seed", "preset"}:
        raise ValueError("invalid new-world configuration fields")
    if type(draft["seed"]) is not int or not 0 <= draft["seed"] <= 2**63-1:
        raise ValueError("invalid new-world seed")
    if type(draft["preset"]) is not int or not 0 <= draft["preset"] < len(PRESETS):
        raise ValueError("invalid workbench preset")
    defaults = Settings()
    for name in EDITABLE_FIELDS:
        value, reference = draft[name], getattr(defaults, name)
        if (type(reference) is bool and type(value) is not bool
            or type(reference) is int and type(value) is not int
            or type(reference) is float and type(value) not in (int, float)):
            raise ValueError(f"invalid new-world setting {name}")
    base = current if draft["preset"] == 0 and current is not None else defaults
    settings = replace(base, **{name: draft[name] for name in EDITABLE_FIELDS})
    settings = restore_scenario_settings(scenario_configuration(settings))
    if settings.object_count + settings.entity_count > settings.world_width * settings.world_height:
        raise ValueError("initial objects and bodies exceed world area")
    if not 1 <= settings.planning_horizon <= 64 or not 1 <= settings.planning_beam_width <= 256:
        raise ValueError("planning limits invalid")
    return settings, draft["seed"]


def create_new_world(draft, current=None):
    from .continuous import ContinuousRuntime
    settings, seed = validate_draft(draft, current)
    return ContinuousRuntime(seed=seed, settings=settings)
