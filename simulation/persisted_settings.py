"""One ownership boundary for causal settings stored in world artifacts."""
from dataclasses import replace
from config import Settings
from physiology.model import Physiology


# Explicit configuration ownership. State (RNG, bodies, clocks, frontiers) lives
# in episode sections. Display speed/history are observational; event weights
# are the disabled legacy autonomous-event API.
WORLD_CAUSAL_FIELDS = (
    'world_width',
    'world_height',
    'object_count',
    'max_objects',
    'entity_count',
    'perception_radius',
    'spawn_interval_min',
    'spawn_interval_max',
)

V084_CAUSAL_FIELDS = (
    'delayed_homeostatic_prediction_enabled', 'planning_passive_prediction_depth',
    'planning_prediction_time_horizon', 'planning_time_discount',
    'planning_temporal_probability_floor',
)

RUNTIME_CAUSAL_FIELDS = V084_CAUSAL_FIELDS + (
    'world_tick_interval',
    'continuous_maintenance_interval_seconds',
    'homeostatic_valuation_enabled',
)

NEURAL_CAUSAL_FIELDS = (
    'sensory_neural_enabled',
    'neural_behavioral_participation',
    'sensory_neural_channel_bins',
    'sensory_neural_max_receptors',
    'sensory_neural_max_injections_per_frame',
    'sensory_neural_input_amplitude',
)

COGNITIVE_CAUSAL_FIELDS = (
    'cognit_activity_decay',
    'homeostasis_trace_decay',
    'homeostasis_learning_rate',
    'homeostasis_target_activity',
    'homeostasis_input_gain',
    'threshold_min',
    'threshold_max',
    'refractory_wave_steps',
    'refractory_attenuation',
    'sensory_activation',
    'wave_retention',
    'wave_max_steps',
    'max_wave_energy',
    'max_wave_propagation_steps',
    'cognit_birth_threshold',
    'cognit_death_threshold',
    'cognit_death_age',
    'proto_min_occurrences',
    'pattern_match_threshold',
    'pattern_frequency_weight',
    'pattern_stability_weight',
    'pattern_prediction_weight',
    'pattern_compression_weight',
    'pattern_redundancy_weight',
    'min_relation_support',
    'min_relation_lift',
    'relation_evidence_window',
    'relation_confidence_k',
    'relation_confidence_decay',
    'relation_death_threshold',
    'relation_max_idle',
    'relation_provisional_support',
    'relation_consolidated_support',
    'relation_provisional_lift',
    'relation_consolidated_confidence',
    'relation_confirmation_rate',
    'relation_contradiction_rate',
    'relation_utility_rate',
    'prediction_probability_floor',
    'prediction_error_learning_rate',
    'novelty_rarity_weight',
    'novelty_prediction_error_weight',
    'novelty_representation_weight',
    'controllability_baseline',
    'control_min_support',
    'goal_tension_threshold',
    'goal_inertia',
    'goal_initial_persistence',
    'goal_decay',
    'goal_understanding_decay',
    'goal_min_persistence',
    'choice_goal_weight',
    'choice_information_weight',
    'choice_novelty_weight',
    'choice_control_weight',
    'choice_loop_weight',
    'choice_cost_weight',
    'interact_cost',
    'grab_cost',
    'release_cost',
    'movement_cost',
    'idle_cost',
    'action_tie_epsilon',
    'working_memory_size',
    'loop_max_period',
    'loop_min_repeats',
    'loop_similarity_threshold',
    'loop_cognit_weight',
    'loop_percept_weight',
    'loop_action_weight',
    'loop_goal_weight',
    'loop_error_weight',
    'loop_tension_weight',
    'percept_feature_weight',
    'percept_spatial_weight',
    'percept_structure_weight',
    'percept_state_weight',
    'percept_temporal_weight',
    'percept_continuity_threshold',
    'percept_persistence_window',
    'percept_confidence_decay',
    'percept_spatial_scale',
    'sensorimotor_min_support',
    'sensorimotor_prior_variance',
    'composite_window_min',
    'composite_window_max',
    'composite_min_participants',
    'composite_max_participants',
    'composite_min_support',
    'composite_birth_threshold',
    'composite_frequency_weight',
    'composite_stability_weight',
    'composite_prediction_weight',
    'composite_compression_weight',
    'composite_redundancy_weight',
    'composite_complexity_weight',
    'max_abstraction_depth',
    'max_composite_candidates',
    'pattern_background_window',
    'retention_utility_weight',
    'retention_confidence_weight',
    'retention_prediction_weight',
    'retention_recency_weight',
    'retention_threshold',
    'retention_grace_ticks',
    'lifecycle_batch_size',
    'calibration_window',
    'prediction_error_neutral',
    'novelty_instability_weight',
    'goal_unavailable_limit',
    'max_cognits',
    'max_relations',
    'max_new_cognits_per_tick',
    'max_new_relations_per_tick',
    'language_min_support',
    'language_min_lift',
    'language_relation_initial_strength',
    'language_relation_confirmation_rate',
    'language_relation_contradiction_rate',
    'language_confidence_k',
    'language_symbol_activation',
    'language_grounding_horizon_seconds',
    'language_grounding_tau_seconds',
    'language_min_background_seconds',
    'language_lift_saturation',
    'language_recent_contexts',
    'language_max_provisional_candidates_per_symbol',
    'language_max_tokens_per_utterance',
    'language_max_semantic_anchors_per_token',
    'language_sequence_min_support',
    'language_sequence_confidence_k',
    'language_max_sequence_candidates_per_symbol',
    'language_request_min_support',
    'language_request_min_probability',
    'language_request_confidence_k',
    'agency_min_confidence',
    'place_birth_visits',
    'memory_confidence_decay',
    'memory_match_threshold',
    'memory_contradiction_rate',
    'min_deliberation_cycles',
    'max_deliberation_cycles',
    'planning_horizon',
    'planning_beam_width',
    'action_dominance_margin',
)

CAUSAL_GROUPS = {
    "world": WORLD_CAUSAL_FIELDS,
    "runtime": RUNTIME_CAUSAL_FIELDS,
    "cognitive": COGNITIVE_CAUSAL_FIELDS,
    "neural": NEURAL_CAUSAL_FIELDS,
    "resources": Settings.RESOURCE_FIELDS,
    "interoception": Settings.INTEROCEPTION_FIELDS,
}


def causal_configuration(settings):
    return {label: {name: getattr(settings, name) for name in fields}
            for label, fields in CAUSAL_GROUPS.items()}


def scenario_configuration(settings):
    """Полный initial-condition contract; исторический world wire не меняется."""
    return {**causal_configuration(settings),
            "physiology": {name: getattr(settings, name) for name in Physiology.CONFIG_FIELDS}}


def restore_scenario_settings(configuration):
    from math import isfinite
    groups = {**CAUSAL_GROUPS, "physiology": Physiology.CONFIG_FIELDS}
    if not isinstance(configuration, dict) or set(configuration) != set(groups):
        raise ValueError("invalid scenario configuration groups")
    defaults = Settings()
    for group, names in groups.items():
        values = configuration[group]
        if not isinstance(values, dict) or set(values) != set(names):
            raise ValueError(f"invalid scenario {group} configuration")
        for name, value in values.items():
            reference = getattr(defaults, name)
            if isinstance(reference, bool):
                valid = type(value) is bool
            elif isinstance(reference, int):
                valid = type(value) is int and 0 <= value <= 1_000_000
            else:
                valid = type(value) in (int, float) and isfinite(value) and 0 <= value <= 1_000_000
            if not valid:
                raise ValueError(f"invalid scenario setting {name}")
    settings = restore_settings({"causal_config": {k: configuration[k] for k in CAUSAL_GROUPS},
                                 "physiology": {"config": configuration["physiology"]}})
    if not (1 <= settings.world_width <= 4096 and 1 <= settings.world_height <= 4096
            and settings.world_width * settings.world_height <= 1_000_000
            and 1 <= settings.entity_count <= 64 and settings.max_objects <= 10000
            and settings.object_count <= settings.max_objects
            and settings.spawn_interval_min >= 1 and settings.spawn_interval_max >= settings.spawn_interval_min
            and settings.continuous_maintenance_interval_seconds > 0
            and settings.world_tick_interval > 0 and settings.max_wave_propagation_steps > 0
            and settings.wave_max_steps > 0 and settings.max_cognits > 0):
        raise ValueError("scenario Settings limits invalid")
    Physiology(settings)
    return settings


def restore_settings(state, explicit=None, sensory=None):
    sources = (("physiology", state.get("physiology", {}).get("config"), Physiology.CONFIG_FIELDS),
               ("resources", state.get("resource_config"), Settings.RESOURCE_FIELDS),
               ("interoception", state.get("interoception_config"), Settings.INTEROCEPTION_FIELDS),
               ("world", state.get("world_config"), Settings.WORLD_FIELDS),
               ("sensory-neural topology", sensory, ("sensory_neural_enabled", "neural_behavioral_participation", "perception_radius", "sensory_neural_channel_bins", "sensory_neural_max_receptors", "sensory_neural_max_injections_per_frame", "sensory_neural_input_amplitude")))
    configuration = state.get("causal_config")
    if configuration is not None:
        if set(configuration) != set(CAUSAL_GROUPS):
            raise ValueError("invalid saved causal configuration groups")
        sources += tuple((label, configuration[label], fields) for label, fields in CAUSAL_GROUPS.items())
    merged = {}
    for label, values, fields in sources:
        if values is None:
            continue
        if label == "runtime" and set(values) == set(fields) - set(V084_CAUSAL_FIELDS):
            # Exact historical v0.8.3 group, not a permissive missing-field rule.
            values = {**{name:getattr(Settings(),name) for name in V084_CAUSAL_FIELDS}, **values}
        if set(values) != set(fields):
            raise ValueError(f"invalid saved {label} configuration")
        for name, value in values.items():
            if name in merged and merged[name] != value:
                raise ValueError(f"conflicting saved {name}")
            merged[name] = value
            if explicit is not None and getattr(explicit, name) != value:
                raise ValueError(f"explicit Settings are incompatible with saved {label}")
    return explicit if explicit is not None else replace(Settings(), **merged)
