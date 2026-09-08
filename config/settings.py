from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    # WORLD
    world_width: int = 30
    world_height: int = 30
    object_count: int = 25
    max_objects: int = 25
    entity_count: int = 1
    perception_radius: int = 4
    world_tick_interval: int = 1
    # Absolute simulated-time maintenance cadence for ContinuousRuntime only.
    continuous_maintenance_interval_seconds: float = 1.0
    world_event_weights: tuple[float,float,float] = (1.0,0.0,0.0)  # legacy API; autonomous events are disabled
    spawn_interval_min: int = 250
    spawn_interval_max: int = 750
    # HOMEOSTASIS
    cognit_activity_decay: float = 0.72
    homeostasis_trace_decay: float = 0.95
    homeostasis_learning_rate: float = 0.025
    homeostasis_target_activity: float = 0.08
    homeostasis_input_gain: float = 8.0
    threshold_min: float = 0.12
    threshold_max: float = 0.90
    refractory_wave_steps: int = 2
    refractory_attenuation: float = 0.20
    # WAVE
    sensory_activation: float = 0.55
    wave_retention: float = 0.72
    wave_max_steps: int = 8
    max_wave_energy: float = 256.0
    max_wave_propagation_steps: int = 8
    # PATTERN
    cognit_birth_threshold: float = 0.66
    cognit_death_threshold: float = 0.08
    cognit_death_age: int = 2000
    proto_min_occurrences: int = 4
    pattern_match_threshold: float = 0.45
    pattern_frequency_weight: float = 0.28
    pattern_stability_weight: float = 0.22
    pattern_prediction_weight: float = 0.22
    pattern_compression_weight: float = 0.18
    pattern_redundancy_weight: float = 0.10
    # RELATION
    min_relation_support: int = 20
    min_relation_lift: float = 3.0
    relation_evidence_window: int = 512
    relation_confidence_k: float = 8.0
    relation_confidence_decay: float = 0.9995
    relation_death_threshold: float = 0.035
    relation_max_idle: int = 3000
    relation_provisional_support: int = 6
    relation_consolidated_support: int = 20
    relation_provisional_lift: float = 1.35
    relation_consolidated_confidence: float = 0.68
    relation_confirmation_rate: float = 0.08
    relation_contradiction_rate: float = 0.04
    relation_utility_rate: float = 0.03
    # PREDICTION
    prediction_probability_floor: float = 0.01
    prediction_error_learning_rate: float = 0.10
    # NOVELTY / CONTROL
    novelty_rarity_weight: float = 0.35
    novelty_prediction_error_weight: float = 0.35
    novelty_representation_weight: float = 0.30
    controllability_baseline: float = 0.15
    control_min_support: int = 2
    # GOAL
    goal_tension_threshold: float = 0.08
    goal_inertia: float = 0.88
    goal_initial_persistence: float = 0.85
    goal_decay: float = 0.995
    goal_understanding_decay: float = 0.08
    goal_min_persistence: float = 0.08
    # CHOICE
    choice_goal_weight: float = 1.00
    choice_information_weight: float = 0.70
    choice_novelty_weight: float = 0.65
    choice_control_weight: float = 0.35
    choice_loop_weight: float = 0.90
    choice_cost_weight: float = 0.10
    interact_cost: float = 0.15
    grab_cost: float = 0.12
    release_cost: float = 0.10
    movement_cost: float = 0.04
    idle_cost: float = 0.08
    action_tie_epsilon: float = 1e-4
    # LOOP / WORKING MEMORY
    working_memory_size: int = 64
    loop_max_period: int = 8
    loop_min_repeats: int = 3
    loop_similarity_threshold: float = 0.75
    loop_cognit_weight: float = 0.35
    loop_percept_weight: float = 0.15
    loop_action_weight: float = 0.15
    loop_goal_weight: float = 0.10
    loop_error_weight: float = 0.15
    loop_tension_weight: float = 0.10
    # PERCEPTUAL CONTINUITY
    percept_feature_weight: float = 0.25
    percept_spatial_weight: float = 0.30
    percept_structure_weight: float = 0.15
    percept_state_weight: float = 0.15
    percept_temporal_weight: float = 0.15
    percept_continuity_threshold: float = 0.52
    percept_persistence_window: int = 3
    percept_confidence_decay: float = 0.82
    percept_spatial_scale: float = 1.5
    sensorimotor_min_support: int = 4
    sensorimotor_prior_variance: float = 4.0
    # COMPOSITES
    composite_window_min: int = 2
    composite_window_max: int = 4
    composite_min_participants: int = 2
    composite_max_participants: int = 4
    composite_min_support: int = 6
    composite_birth_threshold: float = 0.58
    composite_frequency_weight: float = 0.25
    composite_stability_weight: float = 0.20
    composite_prediction_weight: float = 0.20
    composite_compression_weight: float = 0.20
    composite_redundancy_weight: float = 0.10
    composite_complexity_weight: float = 0.05
    max_abstraction_depth: int = 4
    max_composite_candidates: int = 1024
    pattern_background_window: int = 64
    # LIFECYCLE
    retention_utility_weight: float = 0.25
    retention_confidence_weight: float = 0.25
    retention_prediction_weight: float = 0.30
    retention_recency_weight: float = 0.20
    retention_threshold: float = 0.10
    retention_grace_ticks: int = 256
    lifecycle_batch_size: int = 16
    # PREDICTION CALIBRATION
    calibration_window: int = 512
    prediction_error_neutral: float = 0.0
    novelty_instability_weight: float = 0.15
    # GOAL AVAILABILITY
    goal_unavailable_limit: int = 32
    # SAFETY / TELEMETRY
    max_cognits: int = 2048
    max_relations: int = 16384
    max_new_cognits_per_tick: int = 4
    max_new_relations_per_tick: int = 16
    telemetry_history: int = 100_000
    # AGENCY
    agency_min_confidence: float = 0.15
    # SIMULATION SPEED (scheduler only; never enters cognition)
    simulation_speeds: tuple[float, ...] = (0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0, 1000.0, -1.0)
    # MEMORY / PLANNING
    place_birth_visits: int = 2
    memory_confidence_decay: float = 0.9995
    memory_match_threshold: float = 0.55
    memory_contradiction_rate: float = 0.15
    min_deliberation_cycles: int = 1
    max_deliberation_cycles: int = 16
    planning_horizon: int = 4
    planning_beam_width: int = 8
    action_dominance_margin: float = 0.12
