# v0.9.2 survival-learning research results

Overall proof: **FAIL**.

Canonical protocol SHA-256: `87fd4007f3dc4e81a5a12d8e2fedf5747750f2ed37e466a9c9d6b1729bb8c0e9`.
Software: `{'git_head': 'aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65', 'numeric_backend': 'native', 'platform': 'Windows-10-10.0.19045-SP0', 'project_version': '0.9.2', 'python': '3.12.10'}`.
Thresholds changed after first full run: **NO**.

## Acquisition

```json
{
  "gates": {
    "autonomous_discovery": true,
    "learned_supported_consequence": false,
    "observed_bin_change": true,
    "physical_nutrient_consequence": true
  },
  "internal_bin_changes": 11,
  "nutrient_gain": 237.75,
  "passive_timing_observations": 4348,
  "physical_consumptions": 6,
  "supported_beneficial_relations": [],
  "timing_observations": 426424
}
```

## Behavior and economy

| Stage | Group | N | Success | Median time | Median actions | Energy spent | Brownout | Median J |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| stage_1 | FRESH_FULL | 16 | 0 | 6 | 39 | 0.9325 | 0 | 1.8167 |
| stage_1 | EXPERIENCED_FULL | 16 | 16 | 0.15 | 1 | 0.17875 | 0 | 0.337434 |
| stage_1 | EXPERIENCED_NO_DELAYED | 16 | 16 | 0.15 | 1 | 0.0525 | 0 | 0.333483 |
| stage_1 | EXPERIENCED_NO_MOTIVATION | 16 | 16 | 0.15 | 1 | 0 | 0 | 0.347331 |
| stage_2 | FRESH_FULL | 16 | 16 | 4.2 | 28 | 0.0525 | 0 | 1.51379 |
| stage_2 | EXPERIENCED_FULL | 16 | 0 | 9 | 59 | 3.25875 | 0 | 2.80693 |
| stage_2 | EXPERIENCED_NO_DELAYED | 16 | 0 | 9 | 59 | 2.20625 | 0 | 2.79391 |
| stage_2 | EXPERIENCED_NO_MOTIVATION | 16 | 16 | 0.6 | 4 | 0.17875 | 0 | 0.65166 |
| stage_3 | FRESH_FULL | 64 | 0 | 9 | 59 | 1.90625 | 0 | 2.77 |
| stage_3 | EXPERIENCED_FULL | 64 | 16 | 9 | 59 | 2.79313 | 0 | 2.77607 |
| stage_3 | EXPERIENCED_NO_DELAYED | 64 | 0 | 9 | 59 | 2.38 | 0 | 2.78413 |
| stage_3 | EXPERIENCED_NO_MOTIVATION | 64 | 16 | 9 | 59 | 2.43 | 0 | 2.7792 |
| stage_4 | FRESH_FULL | 32 | 17 | 8.7 | 58 | 9.62438 | 0 | 5.57508 |
| stage_4 | EXPERIENCED_FULL | 32 | 18 | 9 | 60 | 11.3981 | 0 | 5.30142 |
| stage_4 | EXPERIENCED_NO_DELAYED | 32 | 1 | 30 | 200 | 19.38 | 0 | 8.54687 |
| stage_4 | EXPERIENCED_NO_MOTIVATION | 32 | 6 | 30 | 200 | 20.2725 | 0 | 8.58413 |

## Gates and causal ablations

### stage_1

Paired wins: 16/16.

```json
{
  "autonomous_discovery": true,
  "delayed_ablation": false,
  "learned_supported_consequence": false,
  "lower_median_actions": true,
  "lower_median_time": true,
  "minimum_cases": true,
  "motivation_ablation": false,
  "observed_bin_change": true,
  "paired_wins": true,
  "physical_nutrient_consequence": true,
  "practical_effect": true,
  "success_noninferiority": true
}
```

### stage_2

Paired wins: 0/16.

```json
{
  "delayed_ablation": false,
  "lower_median_actions": false,
  "lower_median_time": false,
  "minimum_cases": true,
  "model_chain": false,
  "motivation_ablation": false,
  "paired_wins": false,
  "practical_effect": false,
  "success_noninferiority": false
}
```

### stage_3

Paired wins: 48/64.

```json
{
  "directional_transfer": false,
  "translation_transfer": false
}
```

### stage_4

Paired wins: 21/32.

```json
{
  "delayed_ablation": false,
  "economy_effect": false,
  "lower_J": true,
  "lower_median_actions": false,
  "lower_median_time": false,
  "minimum_cases": true,
  "motivation_ablation": true,
  "paired_wins": false,
  "practical_effect": false,
  "success_noninferiority": true
}
```

## Withheld generalization

| Variant | Fresh median time | Experienced median time | Result |
|---|---:|---:|---|
| stage3_east_a | 9 | 9 | FAIL |
| stage3_north_translated | 9 | 9 | FAIL |
| stage3_south_a | 9 | 1.35 | PASS |
| stage3_west_a | 9 | 9 | FAIL |

## Stage 2 model evidence

```json
[
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92101
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92102
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92103
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92104
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92105
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92106
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92107
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92108
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92109
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92110
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92111
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92112
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92113
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92114
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92115
  },
  {
    "delayed_prediction": false,
    "first_move": {
      "action": 2,
      "body": [
        [
          0,
          3,
          3,
          "NORTH"
        ]
      ],
      "diagnostics": {
        "homeostatic_plan_component": 0.0,
        "homeostatic_prediction_confidence": 0.9410292665955833,
        "homeostatic_predictions_considered": 391,
        "temporal": {
          "ambiguity": 0.0,
          "elapsed": 0.41111111111110626,
          "passive_depth": 0,
          "projected_state": [
            1,
            3,
            4,
            5,
            6,
            8,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            24,
            25,
            26,
            28,
            29,
            30,
            31,
            32,
            33,
            34,
            39,
            40,
            41,
            52,
            53,
            84,
            110,
            127
          ],
          "usable": false,
          "witnesses": 0
        }
      },
      "energy": 45.22125,
      "internal": [
        3,
        0,
        6
      ],
      "nutrients": 11.625,
      "plan": {
        "actions": [
          "MOVE_UP",
          "INTERACT_LEFT",
          "TURN_RIGHT",
          "INTERACT_DOWN"
        ],
        "confidence": 0.0014005864221449077,
        "score": 0.7063210969604341
      },
      "time": 0.15
    },
    "move_interact_chain": false,
    "passed": false,
    "physical_cost_without_nutrient_benefit": false,
    "scenario": "scenarios/v092/stage2_one_move_north.sescenario",
    "seed": 92116
  }
]
```

## Counterfactual

```json
{
  "no_consumption": true,
  "no_external_nutrient_gain": true
}
```

## Paired effects (experienced minus fresh)

| Stage | Scenario | Seed | Win | Time delta | Action delta | J delta |
|---|---|---:|---|---:|---:|---:|
| stage_1 | stage1_adjacent_north | 92101 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92102 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92103 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92104 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92105 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92106 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92107 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92108 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92109 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92110 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92111 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92112 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92113 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92114 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92115 | True | -5.85 | -38 | -1.47926 |
| stage_1 | stage1_adjacent_north | 92116 | True | -5.85 | -38 | -1.47926 |
| stage_2 | stage2_one_move_north | 92101 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92102 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92103 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92104 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92105 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92106 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92107 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92108 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92109 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92110 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92111 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92112 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92113 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92114 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92115 | False | 4.8 | 31 | 1.29314 |
| stage_2 | stage2_one_move_north | 92116 | False | 4.8 | 31 | 1.29314 |
| stage_3 | stage3_east_a | 92101 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92102 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92103 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92104 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92105 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92106 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92107 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92108 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92109 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92110 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92111 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92112 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92113 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92114 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92115 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_east_a | 92116 | False | 0 | 0 | 0.0279712 |
| stage_3 | stage3_north_translated | 92101 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92102 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92103 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92104 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92105 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92106 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92107 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92108 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92109 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92110 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92111 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92112 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92113 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92114 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92115 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_north_translated | 92116 | True | 0 | 0 | -0.00697209 |
| stage_3 | stage3_south_a | 92101 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92102 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92103 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92104 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92105 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92106 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92107 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92108 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92109 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92110 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92111 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92112 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92113 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92114 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92115 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_south_a | 92116 | True | -7.65 | -50 | -1.97104 |
| stage_3 | stage3_west_a | 92101 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92102 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92103 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92104 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92105 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92106 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92107 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92108 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92109 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92110 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92111 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92112 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92113 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92114 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92115 | True | 0 | 0 | -0.00405886 |
| stage_3 | stage3_west_a | 92116 | True | 0 | 0 | -0.00405886 |
| stage_4 | stage4_scarcity_a | 92101 | True | -3.75 | -25 | -1.57539 |
| stage_4 | stage4_scarcity_a | 92102 | True | -3.75 | -25 | -0.379442 |
| stage_4 | stage4_scarcity_a | 92103 | True | -3.75 | -25 | -0.99046 |
| stage_4 | stage4_scarcity_a | 92104 | True | -3.75 | -25 | -0.339004 |
| stage_4 | stage4_scarcity_a | 92105 | True | -3.75 | -25 | -1.02065 |
| stage_4 | stage4_scarcity_a | 92106 | True | -3.75 | -25 | 1.0809 |
| stage_4 | stage4_scarcity_a | 92107 | True | -3.75 | -25 | -3.19579 |
| stage_4 | stage4_scarcity_a | 92108 | True | -3.75 | -25 | -0.966593 |
| stage_4 | stage4_scarcity_a | 92109 | True | -3.75 | -25 | -0.983452 |
| stage_4 | stage4_scarcity_a | 92110 | True | -3.75 | -25 | -1.03796 |
| stage_4 | stage4_scarcity_a | 92111 | True | -3.75 | -25 | -0.975801 |
| stage_4 | stage4_scarcity_a | 92112 | True | -3.75 | -25 | 1.80031 |
| stage_4 | stage4_scarcity_a | 92113 | True | -3.75 | -25 | -0.98767 |
| stage_4 | stage4_scarcity_a | 92114 | True | -3.75 | -25 | -0.989209 |
| stage_4 | stage4_scarcity_a | 92115 | True | -3.75 | -25 | -1.00034 |
| stage_4 | stage4_scarcity_a | 92116 | True | -3.75 | -25 | -0.971923 |
| stage_4 | stage4_scarcity_b | 92101 | True | -12.45 | -83 | -2.02632 |
| stage_4 | stage4_scarcity_b | 92102 | True | 0 | 0 | -0.0510148 |
| stage_4 | stage4_scarcity_b | 92103 | True | 0 | 0 | -0.021189 |
| stage_4 | stage4_scarcity_b | 92104 | True | 0 | 0 | -0.0510148 |
| stage_4 | stage4_scarcity_b | 92105 | False | 0 | 0 | 0.0873955 |
| stage_4 | stage4_scarcity_b | 92106 | True | -2.4 | -16 | -0.34046 |
| stage_4 | stage4_scarcity_b | 92107 | False | 0 | 0 | 0.131427 |
| stage_4 | stage4_scarcity_b | 92108 | False | 0 | 0 | 0.179476 |
| stage_4 | stage4_scarcity_b | 92109 | False | 0 | 0 | 0.00205983 |
| stage_4 | stage4_scarcity_b | 92110 | False | 0 | 0 | 0.19955 |
| stage_4 | stage4_scarcity_b | 92111 | False | 0 | 0 | 0.131657 |
| stage_4 | stage4_scarcity_b | 92112 | False | 16.8 | 112 | 2.69281 |
| stage_4 | stage4_scarcity_b | 92113 | False | 0 | 0 | 0.0763763 |
| stage_4 | stage4_scarcity_b | 92114 | False | 0 | 0 | 0.138327 |
| stage_4 | stage4_scarcity_b | 92115 | False | 0 | 0 | 0.192809 |
| stage_4 | stage4_scarcity_b | 92116 | False | 0 | 0 | 0.131427 |

## Complete per-seed results

| Stage | Scenario | Seed | Group | Success | Censored time | Censored actions | Energy spent | Brownout | J |
|---|---|---:|---|---|---:|---:|---:|---|---:|
| stage_1 | stage1_adjacent_north | 92101 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92101 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92101 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92101 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92102 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92102 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92102 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92102 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92103 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92103 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92103 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92103 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92104 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92104 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92104 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92104 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92105 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92105 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92105 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92105 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92106 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92106 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92106 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92106 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92107 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92107 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92107 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92107 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92108 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92108 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92108 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92108 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92109 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92109 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92109 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92109 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92110 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92110 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92110 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92110 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92111 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92111 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92111 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92111 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92112 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92112 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92112 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92112 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92113 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92113 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92113 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92113 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92114 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92114 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92114 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92114 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92115 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92115 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92115 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92115 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_1 | stage1_adjacent_north | 92116 | FRESH_FULL | False | 6 | 39 | 0.9325 | False | 1.8167 |
| stage_1 | stage1_adjacent_north | 92116 | EXPERIENCED_FULL | True | 0.15 | 1 | 0.17875 | False | 0.337434 |
| stage_1 | stage1_adjacent_north | 92116 | EXPERIENCED_NO_DELAYED | True | 0.15 | 1 | 0.0525 | False | 0.333483 |
| stage_1 | stage1_adjacent_north | 92116 | EXPERIENCED_NO_MOTIVATION | True | 0.15 | 1 | 0 | False | 0.347331 |
| stage_2 | stage2_one_move_north | 92101 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92101 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92101 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92101 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92102 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92102 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92102 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92102 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92103 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92103 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92103 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92103 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92104 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92104 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92104 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92104 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92105 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92105 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92105 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92105 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92106 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92106 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92106 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92106 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92107 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92107 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92107 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92107 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92108 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92108 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92108 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92108 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92109 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92109 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92109 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92109 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92110 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92110 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92110 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92110 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92111 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92111 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92111 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92111 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92112 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92112 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92112 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92112 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92113 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92113 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92113 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92113 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92114 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92114 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92114 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92114 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92115 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92115 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92115 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92115 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_2 | stage2_one_move_north | 92116 | FRESH_FULL | True | 4.2 | 28 | 0.0525 | False | 1.51379 |
| stage_2 | stage2_one_move_north | 92116 | EXPERIENCED_FULL | False | 9 | 59 | 3.25875 | False | 2.80693 |
| stage_2 | stage2_one_move_north | 92116 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.20625 | False | 2.79391 |
| stage_2 | stage2_one_move_north | 92116 | EXPERIENCED_NO_MOTIVATION | True | 0.6 | 4 | 0.17875 | False | 0.65166 |
| stage_3 | stage3_east_a | 92101 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92101 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92101 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92101 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92102 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92102 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92102 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92102 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92103 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92103 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92103 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92103 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92104 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92104 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92104 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92104 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92105 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92105 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92105 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92105 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92106 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92106 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92106 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92106 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92107 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92107 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92107 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92107 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92108 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92108 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92108 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92108 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92109 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92109 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92109 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92109 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92110 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92110 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92110 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92110 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92111 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92111 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92111 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92111 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92112 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92112 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92112 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92112 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92113 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92113 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92113 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92113 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92114 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92114 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92114 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92114 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92115 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92115 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92115 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92115 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_east_a | 92116 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_east_a | 92116 | EXPERIENCED_FULL | False | 9 | 59 | 2.90625 | False | 2.79044 |
| stage_3 | stage3_east_a | 92116 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.70625 | False | 2.78733 |
| stage_3 | stage3_east_a | 92116 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.60625 | False | 2.78827 |
| stage_3 | stage3_south_a | 92101 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92101 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92101 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92101 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92102 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92102 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92102 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92102 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92103 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92103 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92103 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92103 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92104 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92104 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92104 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92104 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92105 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92105 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92105 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92105 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92106 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92106 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92106 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92106 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92107 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92107 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92107 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92107 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92108 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92108 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92108 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92108 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92109 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92109 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92109 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92109 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92110 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92110 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92110 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92110 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92111 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92111 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92111 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92111 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92112 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92112 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92112 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92112 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92113 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92113 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92113 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92113 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92114 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92114 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92114 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92114 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92115 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92115 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92115 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92115 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_south_a | 92116 | FRESH_FULL | False | 9 | 59 | 1.68 | False | 2.76247 |
| stage_3 | stage3_south_a | 92116 | EXPERIENCED_FULL | True | 1.35 | 9 | 0 | False | 0.791429 |
| stage_3 | stage3_south_a | 92116 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 1.68 | False | 2.77087 |
| stage_3 | stage3_south_a | 92116 | EXPERIENCED_NO_MOTIVATION | True | 1.35 | 9 | 0.23125 | False | 0.820644 |
| stage_3 | stage3_west_a | 92101 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92101 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92101 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92101 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92102 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92102 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92102 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92102 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92103 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92103 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92103 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92103 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92104 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92104 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92104 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92104 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92105 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92105 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92105 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92105 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92106 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92106 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92106 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92106 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92107 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92107 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92107 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92107 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92108 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92108 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92108 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92108 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92109 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92109 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92109 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92109 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92110 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92110 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92110 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92110 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92111 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92111 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92111 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92111 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92112 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92112 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92112 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92112 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92113 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92113 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92113 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92113 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92114 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92114 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92114 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92114 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92115 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92115 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92115 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92115 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_west_a | 92116 | FRESH_FULL | False | 9 | 59 | 2.1325 | False | 2.77752 |
| stage_3 | stage3_west_a | 92116 | EXPERIENCED_FULL | False | 9 | 59 | 2.68 | False | 2.77346 |
| stage_3 | stage3_west_a | 92116 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.28 | False | 2.78898 |
| stage_3 | stage3_west_a | 92116 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 3.18 | False | 2.77914 |
| stage_3 | stage3_north_translated | 92101 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92101 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92101 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92101 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92102 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92102 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92102 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92102 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92103 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92103 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92103 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92103 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92104 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92104 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92104 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92104 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92105 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92105 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92105 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92105 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92106 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92106 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92106 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92106 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92107 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92107 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92107 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92107 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92108 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92108 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92108 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92108 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92109 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92109 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92109 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92109 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92110 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92110 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92110 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92110 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92111 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92111 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92111 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92111 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92112 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92112 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92112 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92112 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92113 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92113 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92113 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92113 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92114 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92114 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92114 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92114 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92115 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92115 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92115 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92115 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_3 | stage3_north_translated | 92116 | FRESH_FULL | False | 9 | 59 | 3.3325 | False | 2.78566 |
| stage_3 | stage3_north_translated | 92116 | EXPERIENCED_FULL | False | 9 | 59 | 3.18 | False | 2.77868 |
| stage_3 | stage3_north_translated | 92116 | EXPERIENCED_NO_DELAYED | False | 9 | 59 | 2.48 | False | 2.78092 |
| stage_3 | stage3_north_translated | 92116 | EXPERIENCED_NO_MOTIVATION | False | 9 | 59 | 1.68 | False | 2.77927 |
| stage_4 | stage4_scarcity_a | 92101 | FRESH_FULL | True | 4.2 | 28 | 1.50125 | False | 3.87569 |
| stage_4 | stage4_scarcity_a | 92101 | EXPERIENCED_FULL | True | 0.45 | 3 | 0.2525 | False | 2.3003 |
| stage_4 | stage4_scarcity_a | 92101 | EXPERIENCED_NO_DELAYED | True | 17.55 | 117 | 9.3 | False | 6.38944 |
| stage_4 | stage4_scarcity_a | 92101 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 17.58 | False | 8.56861 |
| stage_4 | stage4_scarcity_a | 92102 | FRESH_FULL | True | 4.2 | 28 | 3.2975 | False | 4.46558 |
| stage_4 | stage4_scarcity_a | 92102 | EXPERIENCED_FULL | True | 0.45 | 3 | 3.66 | False | 4.08614 |
| stage_4 | stage4_scarcity_a | 92102 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 18.98 | False | 8.4498 |
| stage_4 | stage4_scarcity_a | 92102 | EXPERIENCED_NO_MOTIVATION | True | 26.1 | 174 | 20.2725 | False | 8.03876 |
| stage_4 | stage4_scarcity_a | 92103 | FRESH_FULL | True | 4.2 | 28 | 4.57 | False | 5.08949 |
| stage_4 | stage4_scarcity_a | 92103 | EXPERIENCED_FULL | True | 0.45 | 3 | 3.89125 | False | 4.09903 |
| stage_4 | stage4_scarcity_a | 92103 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 23.58 | False | 8.59506 |
| stage_4 | stage4_scarcity_a | 92103 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.28 | False | 8.64259 |
| stage_4 | stage4_scarcity_a | 92104 | FRESH_FULL | True | 4.2 | 28 | 0.53625 | False | 2.63949 |
| stage_4 | stage4_scarcity_a | 92104 | EXPERIENCED_FULL | True | 0.45 | 3 | 0.305 | False | 2.30049 |
| stage_4 | stage4_scarcity_a | 92104 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 18.98 | False | 8.4498 |
| stage_4 | stage4_scarcity_a | 92104 | EXPERIENCED_NO_MOTIVATION | True | 26.1 | 174 | 20.2725 | False | 8.03876 |
| stage_4 | stage4_scarcity_a | 92105 | FRESH_FULL | True | 4.2 | 28 | 5.86375 | False | 5.11865 |
| stage_4 | stage4_scarcity_a | 92105 | EXPERIENCED_FULL | True | 0.45 | 3 | 6.73875 | False | 4.098 |
| stage_4 | stage4_scarcity_a | 92105 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.38 | False | 8.52286 |
| stage_4 | stage4_scarcity_a | 92105 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 14.88 | False | 8.54783 |
| stage_4 | stage4_scarcity_a | 92106 | FRESH_FULL | True | 4.2 | 28 | 0.48375 | False | 3.0103 |
| stage_4 | stage4_scarcity_a | 92106 | EXPERIENCED_FULL | True | 0.45 | 3 | 3.765 | False | 4.0912 |
| stage_4 | stage4_scarcity_a | 92106 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 17.18 | False | 8.46835 |
| stage_4 | stage4_scarcity_a | 92106 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 16.38 | False | 8.58237 |
| stage_4 | stage4_scarcity_a | 92107 | FRESH_FULL | True | 4.2 | 28 | 4.99125 | False | 5.0989 |
| stage_4 | stage4_scarcity_a | 92107 | EXPERIENCED_FULL | True | 0.45 | 3 | 0.07875 | False | 1.90311 |
| stage_4 | stage4_scarcity_a | 92107 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 18.78 | False | 8.52779 |
| stage_4 | stage4_scarcity_a | 92107 | EXPERIENCED_NO_MOTIVATION | True | 27 | 180 | 20.58 | False | 8.17366 |
| stage_4 | stage4_scarcity_a | 92108 | FRESH_FULL | True | 4.2 | 28 | 4.43875 | False | 5.0811 |
| stage_4 | stage4_scarcity_a | 92108 | EXPERIENCED_FULL | True | 0.45 | 3 | 11.6913 | False | 4.11451 |
| stage_4 | stage4_scarcity_a | 92108 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 19.58 | False | 8.5029 |
| stage_4 | stage4_scarcity_a | 92108 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 18.88 | False | 8.6156 |
| stage_4 | stage4_scarcity_a | 92109 | FRESH_FULL | True | 4.2 | 28 | 3.765 | False | 5.0794 |
| stage_4 | stage4_scarcity_a | 92109 | EXPERIENCED_FULL | True | 0.45 | 3 | 6.765 | False | 4.09595 |
| stage_4 | stage4_scarcity_a | 92109 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.38 | False | 8.56756 |
| stage_4 | stage4_scarcity_a | 92109 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 20.18 | False | 8.62838 |
| stage_4 | stage4_scarcity_a | 92110 | FRESH_FULL | True | 4.2 | 28 | 10.2637 | False | 5.14871 |
| stage_4 | stage4_scarcity_a | 92110 | EXPERIENCED_FULL | True | 0.45 | 3 | 6.93875 | False | 4.11075 |
| stage_4 | stage4_scarcity_a | 92110 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 14.28 | False | 8.38967 |
| stage_4 | stage4_scarcity_a | 92110 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.38 | False | 8.68171 |
| stage_4 | stage4_scarcity_a | 92111 | FRESH_FULL | True | 4.2 | 28 | 5.6125 | False | 5.09491 |
| stage_4 | stage4_scarcity_a | 92111 | EXPERIENCED_FULL | True | 0.45 | 3 | 5.1375 | False | 4.1191 |
| stage_4 | stage4_scarcity_a | 92111 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.78 | False | 8.59249 |
| stage_4 | stage4_scarcity_a | 92111 | EXPERIENCED_NO_MOTIVATION | True | 17.1 | 114 | 9.7775 | False | 6.48661 |
| stage_4 | stage4_scarcity_a | 92112 | FRESH_FULL | True | 4.2 | 28 | 0.48375 | False | 2.31288 |
| stage_4 | stage4_scarcity_a | 92112 | EXPERIENCED_FULL | True | 0.45 | 3 | 8.41125 | False | 4.11319 |
| stage_4 | stage4_scarcity_a | 92112 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 18.98 | False | 8.4842 |
| stage_4 | stage4_scarcity_a | 92112 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 20.08 | False | 8.74867 |
| stage_4 | stage4_scarcity_a | 92113 | FRESH_FULL | True | 4.2 | 28 | 6.44375 | False | 5.09967 |
| stage_4 | stage4_scarcity_a | 92113 | EXPERIENCED_FULL | True | 0.45 | 3 | 5.9125 | False | 4.112 |
| stage_4 | stage4_scarcity_a | 92113 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 15.68 | False | 8.36303 |
| stage_4 | stage4_scarcity_a | 92113 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 20.78 | False | 8.66322 |
| stage_4 | stage4_scarcity_a | 92114 | FRESH_FULL | True | 4.2 | 28 | 7.5375 | False | 5.10013 |
| stage_4 | stage4_scarcity_a | 92114 | EXPERIENCED_FULL | True | 0.45 | 3 | 10.2387 | False | 4.11092 |
| stage_4 | stage4_scarcity_a | 92114 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.78 | False | 8.59249 |
| stage_4 | stage4_scarcity_a | 92114 | EXPERIENCED_NO_MOTIVATION | True | 17.1 | 114 | 9.65125 | False | 6.47312 |
| stage_4 | stage4_scarcity_a | 92115 | FRESH_FULL | True | 4.2 | 28 | 8.985 | False | 5.08873 |
| stage_4 | stage4_scarcity_a | 92115 | EXPERIENCED_FULL | True | 0.45 | 3 | 3.7125 | False | 4.08839 |
| stage_4 | stage4_scarcity_a | 92115 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 18.48 | False | 8.4806 |
| stage_4 | stage4_scarcity_a | 92115 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.48 | False | 8.70815 |
| stage_4 | stage4_scarcity_a | 92116 | FRESH_FULL | True | 4.2 | 28 | 6.84375 | False | 5.10835 |
| stage_4 | stage4_scarcity_a | 92116 | EXPERIENCED_FULL | True | 0.45 | 3 | 9.89125 | False | 4.13643 |
| stage_4 | stage4_scarcity_a | 92116 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 12.18 | False | 8.32817 |
| stage_4 | stage4_scarcity_a | 92116 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 15.48 | False | 8.53463 |
| stage_4 | stage4_scarcity_b | 92101 | FRESH_FULL | False | 30 | 200 | 14.4063 | False | 8.49273 |
| stage_4 | stage4_scarcity_b | 92101 | EXPERIENCED_FULL | True | 17.55 | 117 | 11.105 | False | 6.46641 |
| stage_4 | stage4_scarcity_b | 92101 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.88 | False | 8.5683 |
| stage_4 | stage4_scarcity_b | 92101 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.68 | False | 8.55718 |
| stage_4 | stage4_scarcity_b | 92102 | FRESH_FULL | False | 30 | 200 | 12.9063 | False | 8.4693 |
| stage_4 | stage4_scarcity_b | 92102 | EXPERIENCED_FULL | False | 30 | 200 | 14.78 | False | 8.41829 |
| stage_4 | stage4_scarcity_b | 92102 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 17.98 | False | 8.54994 |
| stage_4 | stage4_scarcity_b | 92102 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 22.38 | False | 8.5888 |
| stage_4 | stage4_scarcity_b | 92103 | FRESH_FULL | False | 30 | 200 | 16.7063 | False | 8.53076 |
| stage_4 | stage4_scarcity_b | 92103 | EXPERIENCED_FULL | False | 30 | 200 | 19.88 | False | 8.50957 |
| stage_4 | stage4_scarcity_b | 92103 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 23.38 | False | 8.68584 |
| stage_4 | stage4_scarcity_b | 92103 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 19.28 | False | 8.57085 |
| stage_4 | stage4_scarcity_b | 92104 | FRESH_FULL | False | 30 | 200 | 12.9063 | False | 8.4693 |
| stage_4 | stage4_scarcity_b | 92104 | EXPERIENCED_FULL | False | 30 | 200 | 14.78 | False | 8.41829 |
| stage_4 | stage4_scarcity_b | 92104 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 17.98 | False | 8.54994 |
| stage_4 | stage4_scarcity_b | 92104 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 22.38 | False | 8.5888 |
| stage_4 | stage4_scarcity_b | 92105 | FRESH_FULL | False | 30 | 200 | 14.4063 | False | 8.49273 |
| stage_4 | stage4_scarcity_b | 92105 | EXPERIENCED_FULL | False | 30 | 200 | 20.58 | False | 8.58013 |
| stage_4 | stage4_scarcity_b | 92105 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 17.78 | False | 8.48284 |
| stage_4 | stage4_scarcity_b | 92105 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 18.88 | False | 8.58925 |
| stage_4 | stage4_scarcity_b | 92106 | FRESH_FULL | False | 30 | 200 | 12.9063 | False | 8.42999 |
| stage_4 | stage4_scarcity_b | 92106 | EXPERIENCED_FULL | True | 27.6 | 184 | 18.12 | False | 8.08953 |
| stage_4 | stage4_scarcity_b | 92106 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 23.48 | False | 8.67864 |
| stage_4 | stage4_scarcity_b | 92106 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.58 | False | 8.67968 |
| stage_4 | stage4_scarcity_b | 92107 | FRESH_FULL | False | 30 | 200 | 13.4063 | False | 8.49747 |
| stage_4 | stage4_scarcity_b | 92107 | EXPERIENCED_FULL | False | 30 | 200 | 21.08 | False | 8.6289 |
| stage_4 | stage4_scarcity_b | 92107 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 19.38 | False | 8.54687 |
| stage_4 | stage4_scarcity_b | 92107 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 22.18 | False | 8.58413 |
| stage_4 | stage4_scarcity_b | 92108 | FRESH_FULL | False | 30 | 200 | 11.8063 | False | 8.43035 |
| stage_4 | stage4_scarcity_b | 92108 | EXPERIENCED_FULL | False | 30 | 200 | 25.68 | False | 8.60983 |
| stage_4 | stage4_scarcity_b | 92108 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 22.98 | False | 8.67715 |
| stage_4 | stage4_scarcity_b | 92108 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 18.48 | False | 8.53314 |
| stage_4 | stage4_scarcity_b | 92109 | FRESH_FULL | False | 30 | 200 | 17.5063 | False | 8.52901 |
| stage_4 | stage4_scarcity_b | 92109 | EXPERIENCED_FULL | False | 30 | 200 | 23.28 | False | 8.53107 |
| stage_4 | stage4_scarcity_b | 92109 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 23.78 | False | 8.68595 |
| stage_4 | stage4_scarcity_b | 92109 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 21.08 | False | 8.60479 |
| stage_4 | stage4_scarcity_b | 92110 | FRESH_FULL | False | 30 | 200 | 12.9063 | False | 8.42938 |
| stage_4 | stage4_scarcity_b | 92110 | EXPERIENCED_FULL | False | 30 | 200 | 23.18 | False | 8.62893 |
| stage_4 | stage4_scarcity_b | 92110 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 17.18 | False | 8.50314 |
| stage_4 | stage4_scarcity_b | 92110 | EXPERIENCED_NO_MOTIVATION | True | 25.35 | 169 | 14.2725 | False | 7.66448 |
| stage_4 | stage4_scarcity_b | 92111 | FRESH_FULL | False | 30 | 200 | 12.9063 | False | 8.42999 |
| stage_4 | stage4_scarcity_b | 92111 | EXPERIENCED_FULL | False | 30 | 200 | 21.98 | False | 8.56164 |
| stage_4 | stage4_scarcity_b | 92111 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 20.68 | False | 8.66378 |
| stage_4 | stage4_scarcity_b | 92111 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 24.88 | False | 8.71979 |
| stage_4 | stage4_scarcity_b | 92112 | FRESH_FULL | True | 13.2 | 88 | 5.6125 | False | 6.00145 |
| stage_4 | stage4_scarcity_b | 92112 | EXPERIENCED_FULL | False | 30 | 200 | 24.58 | False | 8.69426 |
| stage_4 | stage4_scarcity_b | 92112 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 15.38 | False | 8.44409 |
| stage_4 | stage4_scarcity_b | 92112 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 23.68 | False | 8.63755 |
| stage_4 | stage4_scarcity_b | 92113 | FRESH_FULL | False | 30 | 200 | 13.4063 | False | 8.49779 |
| stage_4 | stage4_scarcity_b | 92113 | EXPERIENCED_FULL | False | 30 | 200 | 20.98 | False | 8.57417 |
| stage_4 | stage4_scarcity_b | 92113 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 21.88 | False | 8.58655 |
| stage_4 | stage4_scarcity_b | 92113 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 18.28 | False | 8.49798 |
| stage_4 | stage4_scarcity_b | 92114 | FRESH_FULL | False | 30 | 200 | 11.1063 | False | 8.41611 |
| stage_4 | stage4_scarcity_b | 92114 | EXPERIENCED_FULL | False | 30 | 200 | 21.48 | False | 8.55444 |
| stage_4 | stage4_scarcity_b | 92114 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 19.48 | False | 8.60686 |
| stage_4 | stage4_scarcity_b | 92114 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 25.98 | False | 8.69913 |
| stage_4 | stage4_scarcity_b | 92115 | FRESH_FULL | False | 30 | 200 | 11.7063 | False | 8.424 |
| stage_4 | stage4_scarcity_b | 92115 | EXPERIENCED_FULL | False | 30 | 200 | 21.78 | False | 8.61681 |
| stage_4 | stage4_scarcity_b | 92115 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 22.68 | False | 8.63117 |
| stage_4 | stage4_scarcity_b | 92115 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 13.98 | False | 8.41625 |
| stage_4 | stage4_scarcity_b | 92116 | FRESH_FULL | False | 30 | 200 | 13.4063 | False | 8.49747 |
| stage_4 | stage4_scarcity_b | 92116 | EXPERIENCED_FULL | False | 30 | 200 | 21.08 | False | 8.6289 |
| stage_4 | stage4_scarcity_b | 92116 | EXPERIENCED_NO_DELAYED | False | 30 | 200 | 19.38 | False | 8.54687 |
| stage_4 | stage4_scarcity_b | 92116 | EXPERIENCED_NO_MOTIVATION | False | 30 | 200 | 22.18 | False | 8.58413 |

## Checkpoint provenance

```json
{
  "stage_1": {
    "path": "brains\\stage1_experienced.sebrain",
    "sha256": "77a55accbedd540b935be43505ae4a369ed237b5a6500d936b3462f49596cd6d"
  },
  "stage_2": {
    "path": "brains\\stage2_experienced.sebrain",
    "sha256": "4bcc3c1f8e42dc37120f3ff8b8ca02b7fcde7f3c812c900e084c7790dc5bfee9"
  },
  "stage_3": {
    "path": "brains\\stage2_experienced.sebrain",
    "sha256": "4bcc3c1f8e42dc37120f3ff8b8ca02b7fcde7f3c812c900e084c7790dc5bfee9"
  },
  "stage_4": {
    "path": "brains\\stage3_consolidated.sebrain",
    "sha256": "f6fb1d2fc759bff75c50b0e79ebae1229f48c7de1ed08090adccebb1f8eb70c5"
  }
}
```

Training seeds: [92001, 92002, 92003, 92004, 92005, 92006, 92007, 92008].
Evaluation seeds: [92101, 92102, 92103, 92104, 92105, 92106, 92107, 92108, 92109, 92110, 92111, 92112, 92113, 92114, 92115, 92116].

## Interpretation and limits

Static scenarios may produce identical trajectories across seeds because no stochastic physical spawning occurs; these are deterministic paired cases, not independent population statistics.
First consumption requires disappearing nutritive resource, successful completed INTERACT and actual nutrient increase. Raw physiology and tracked IDs are measurement-only.
J is midpoint-discounted trapezoidal integration of physical tension, with lambda=0.02; energy expenditure is the sum of positive sample-to-sample E declines, not net energy loss.
Input checkpoint brains are reloaded independently for every experienced/ablated trial; evaluation learning is discarded. All declared seeds and failures are retained.

v0.9.2 experiment infrastructure is implemented, but the predeclared survival-learning proof was not established.

No acceptance threshold or cognitive policy was changed to force a passing result. The failing stage/mechanism is documented as the next research blocker.

stage_1: delayed_ablation, motivation_ablation, learned_supported_consequence
stage_2: success_noninferiority, lower_median_time, lower_median_actions, paired_wins, practical_effect, delayed_ablation, motivation_ablation, model_chain
stage_3: translation_transfer, directional_transfer
stage_4: lower_median_time, lower_median_actions, paired_wins, practical_effect, economy_effect, delayed_ablation

v0.9.3 remains long-run stability, boundedness and soak-test scope.

## Additional offline audit (does not change acceptance)

| Stage | Ablation | Metric | Full advantage | Remaining advantage | Fraction removed |
|---|---|---|---:|---:|---:|
| stage_1 | EXPERIENCED_NO_DELAYED | median_censored_time | 5.85 | 5.85 | 0% |
| stage_1 | EXPERIENCED_NO_MOTIVATION | median_J | 1.47926 | 1.46936 | 0.669024% |
| stage_2 | EXPERIENCED_NO_DELAYED | median_censored_time | -4.8 | -4.8 | n/a (no positive full advantage) |
| stage_2 | EXPERIENCED_NO_MOTIVATION | median_J | -1.29314 | 0.862128 | n/a (no positive full advantage) |
| stage_3 | EXPERIENCED_NO_DELAYED | median_censored_time | 0 | 0 | n/a (no positive full advantage) |
| stage_3 | EXPERIENCED_NO_MOTIVATION | median_J | -0.00607635 | -0.00920383 | n/a (no positive full advantage) |
| stage_4 | EXPERIENCED_NO_DELAYED | median_censored_time | -0.3 | -21.3 | n/a (no positive full advantage) |
| stage_4 | EXPERIENCED_NO_MOTIVATION | median_J | 0.273662 | -3.00905 | 1199.55% |

Checkpoint graph/bin inventory:

```json
{
  "stage_1": {
    "brain_checksum": "77a55accbedd540b935be43505ae4a369ed237b5a6500d936b3462f49596cd6d",
    "full_graph_sync_calls": 0,
    "node_capacity": 2048,
    "nodes": 284,
    "relation_capacity": 16384,
    "relations": 979,
    "represented_internal_bins": {
      "0": [
        3,
        4
      ],
      "1": [
        0
      ],
      "2": [
        6
      ]
    },
    "supported_timed_beneficial_relations": []
  },
  "stage_2": {
    "brain_checksum": "4bcc3c1f8e42dc37120f3ff8b8ca02b7fcde7f3c812c900e084c7790dc5bfee9",
    "full_graph_sync_calls": 0,
    "node_capacity": 2048,
    "nodes": 439,
    "relation_capacity": 16384,
    "relations": 3632,
    "represented_internal_bins": {
      "0": [
        3,
        4
      ],
      "1": [
        0
      ],
      "2": [
        6
      ]
    },
    "supported_timed_beneficial_relations": []
  },
  "stage_3": {
    "brain_checksum": "4bcc3c1f8e42dc37120f3ff8b8ca02b7fcde7f3c812c900e084c7790dc5bfee9",
    "full_graph_sync_calls": 0,
    "node_capacity": 2048,
    "nodes": 439,
    "relation_capacity": 16384,
    "relations": 3632,
    "represented_internal_bins": {
      "0": [
        3,
        4
      ],
      "1": [
        0
      ],
      "2": [
        6
      ]
    },
    "supported_timed_beneficial_relations": []
  },
  "stage_4": {
    "brain_checksum": "f6fb1d2fc759bff75c50b0e79ebae1229f48c7de1ed08090adccebb1f8eb70c5",
    "full_graph_sync_calls": 0,
    "node_capacity": 2048,
    "nodes": 488,
    "relation_capacity": 16384,
    "relations": 5715,
    "represented_internal_bins": {
      "0": [
        3,
        4
      ],
      "1": [
        0
      ],
      "2": [
        6
      ]
    },
    "supported_timed_beneficial_relations": []
  }
}
```

Counterfactual contradiction observations:

```json
[
  {
    "consumptions": 0,
    "contradiction_increases": [],
    "final_reserves": {
      "energy": 47.19999999999984,
      "hydration": 79.27999999999997,
      "nutrients": 0.0
    },
    "group": "FRESH_FULL",
    "initial_reserves": {
      "energy": 45.0,
      "hydration": 80.0,
      "nutrients": 12.0
    },
    "interpretation": "Perceptual/action contradictions are not proof of a contradicted nutritive hypothesis without a supported resource-to-internal consequence.",
    "relations_with_contradiction": 68
  },
  {
    "consumptions": 0,
    "contradiction_increases": [
      {
        "action": 16,
        "after": 0.8609539326891285,
        "before": 0.8491253609908077,
        "source": 1,
        "target": 35,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.4642150189117003,
        "before": 0.46030275489550815,
        "source": 1,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.46031092480207314,
        "before": 0.45606654166891614,
        "source": 1,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4610768256035975,
        "before": 0.4568975972261257,
        "source": 1,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.47018489737291336,
        "before": 0.4667804876008175,
        "source": 1,
        "target": 34,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4657702124853971,
        "before": 0.4619902479225229,
        "source": 1,
        "target": 52,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5652995622049249,
        "before": 0.5283198374619411,
        "source": 1,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7016699055386234,
        "before": 0.6762911301417355,
        "source": 1,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7116407940650741,
        "before": 0.6871102366157489,
        "source": 1,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8851276549198299,
        "before": 0.8753555283418294,
        "source": 1,
        "target": 57,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8877359513155384,
        "before": 0.8781857110628671,
        "source": 1,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.8701142064779614,
        "before": 0.8590648941818158,
        "source": 1,
        "target": 169,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5887191165446121,
        "before": 0.553731680278442,
        "source": 1,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6728644812013206,
        "before": 0.6450352443590719,
        "source": 1,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5880007049413171,
        "before": 0.5529521537991721,
        "source": 1,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8301232821837508,
        "before": 0.8156719641750767,
        "source": 1,
        "target": 55,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6736384850042201,
        "before": 0.6458750922354818,
        "source": 1,
        "target": 56,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8634202478177109,
        "before": 0.8518014841772037,
        "source": 1,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.703141902574837,
        "before": 0.6778883491480436,
        "source": 1,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6859161274147412,
        "before": 0.6591971868649535,
        "source": 1,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7521965544366059,
        "before": 0.7311160529911088,
        "source": 1,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7803432908093144,
        "before": 0.761657216589968,
        "source": 1,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8095513132138791,
        "before": 0.7933499492338097,
        "source": 1,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9356430597766027,
        "before": 0.9301682506256539,
        "source": 1,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.782431592931931,
        "before": 0.7639231694139876,
        "source": 1,
        "target": 188,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.8046338484446798,
        "before": 0.7880141584686196,
        "source": 1,
        "target": 245,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5919834472222473,
        "before": 0.5572737057533066,
        "source": 1,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6109353204598278,
        "before": 0.5778378043183895,
        "source": 1,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6150925641116226,
        "before": 0.5823487023780627,
        "source": 1,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7808982212130879,
        "before": 0.7622593546148958,
        "source": 1,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.7150235815922927,
        "before": 0.6907807959985816,
        "source": 1,
        "target": 225,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5905626187488296,
        "before": 0.5557320081910044,
        "source": 1,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9501617183317278,
        "before": 0.9459220033981421,
        "source": 1,
        "target": 70,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9497144363739509,
        "before": 0.9454366714127072,
        "source": 1,
        "target": 71,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9174303287049256,
        "before": 0.9104061726398932,
        "source": 1,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.6366174459917108,
        "before": 0.6057046940014224,
        "source": 1,
        "target": 305,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9979521532065434,
        "before": 0.9977779440175166,
        "source": 1,
        "target": 190,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6988609572260412,
        "before": 0.6732432261567288,
        "source": 1,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9202228509077652,
        "before": 0.9134362531551272,
        "source": 1,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.4353266876448864,
        "before": 0.38729024267023265,
        "source": 1,
        "target": 78,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 1,
        "target": 36,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.4120800793733078,
        "before": 0.0004784864940087,
        "source": 2,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025788653898066106,
        "before": 0.002176573664433198,
        "source": 2,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 34,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 4,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 5,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 6,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.024508390293190685,
        "before": 0.0,
        "source": 2,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.024508390293190685,
        "before": 0.0,
        "source": 2,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 63,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 64,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 65,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 66,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 67,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.9915718110069733,
        "before": 0.9856712522864596,
        "source": 2,
        "target": 122,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41179863296342334,
        "before": 0.0,
        "source": 2,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5855909367130437,
        "before": 0.5018851389289778,
        "source": 3,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6110959984676406,
        "before": 0.5224571423451014,
        "source": 3,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5358319984676402,
        "before": 0.5224571423450967,
        "source": 3,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5358319984686803,
        "before": 0.5224571423553293,
        "source": 3,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5133374945589472,
        "before": 0.5018851177416517,
        "source": 3,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.807470102051429,
        "before": 0.7681186231610011,
        "source": 3,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020514534,
        "before": 0.7681186231612429,
        "source": 3,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020514534,
        "before": 0.7681186231612429,
        "source": 3,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020514028,
        "before": 0.7681186231607431,
        "source": 3,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020514028,
        "before": 0.7681186231607431,
        "source": 3,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7476774433498713,
        "before": 9.180849796270683e-13,
        "source": 3,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.513337494559002,
        "before": 0.5018851177421922,
        "source": 3,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5133374945589396,
        "before": 0.501885117741578,
        "source": 3,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996341931832486,
        "before": 0.9964019868687372,
        "source": 3,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996341931837931,
        "before": 0.9964019868740934,
        "source": 3,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802262,
        "source": 3,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802262,
        "source": 3,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802262,
        "source": 3,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802262,
        "source": 3,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802262,
        "source": 3,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074789,
        "before": 0.7337664945802644,
        "source": 3,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.11526400275193481,
        "before": 2.3947643714018287e-08,
        "source": 3,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5028080244428804,
        "before": 0.4795017811606573,
        "source": 3,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5028080244428804,
        "before": 0.4795017811606573,
        "source": 3,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.563057813767346,
        "before": 0.5192045931696581,
        "source": 4,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996500340315,
        "before": 0.9999988090629034,
        "source": 4,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6277423660458421,
        "before": 3.1568170010640325e-08,
        "source": 4,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0132869947241113,
        "before": 4.526524621595098e-06,
        "source": 4,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.01328696250241935,
        "before": 4.416873936311148e-06,
        "source": 4,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.12750976149593313,
        "before": 5.761388298222481e-06,
        "source": 4,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.049109749990082434,
        "before": 5.722233792828254e-06,
        "source": 4,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04911023089075367,
        "before": 7.358742770256542e-06,
        "source": 4,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246578112437001,
        "before": 0.5192045845816702,
        "source": 4,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992777148337,
        "before": 0.9999975420575806,
        "source": 4,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992998160269,
        "before": 0.9999976172681263,
        "source": 4,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246578271648754,
        "before": 0.5192046387615618,
        "source": 4,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753029973761191,
        "before": 0.5192083880031522,
        "source": 4,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030374366436,
        "before": 0.5192085243294489,
        "source": 4,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030385627645,
        "before": 0.5192085281616474,
        "source": 4,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030385627645,
        "before": 0.5192085281616474,
        "source": 4,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030385627645,
        "before": 0.5192085281616474,
        "source": 4,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997835806343,
        "before": 0.9999992635231018,
        "source": 4,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986949859818,
        "before": 0.99999555902646,
        "source": 4,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992548152347,
        "before": 0.9999974641300562,
        "source": 4,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999979942115381,
        "before": 0.999993174285209,
        "source": 4,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999982028236628,
        "before": 0.9999938841940017,
        "source": 4,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999980811882992,
        "before": 0.9999934702678496,
        "source": 4,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991536426666,
        "before": 0.9999971198389667,
        "source": 4,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995712339215,
        "before": 0.9999985409054741,
        "source": 4,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995712339215,
        "before": 0.9999985409054741,
        "source": 4,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.6020062589584614,
        "before": 0.585423186415064,
        "source": 4,
        "target": 61,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.331126717455956,
        "before": 0.30325699734995415,
        "source": 4,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999989615979745,
        "before": 0.9999964663092851,
        "source": 4,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999989614119632,
        "before": 0.9999964656762863,
        "source": 4,
        "target": 136,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999989615979745,
        "before": 0.9999964663092851,
        "source": 4,
        "target": 137,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999998854964069,
        "before": 0.9999961034332191,
        "source": 4,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999275655651,
        "before": 0.9999997535050166,
        "source": 4,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999831126051,
        "before": 0.9999999425320553,
        "source": 4,
        "target": 167,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999831126051,
        "before": 0.9999999425320553,
        "source": 4,
        "target": 171,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991420057863,
        "before": 0.9999970802385663,
        "source": 4,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999985455557537,
        "before": 0.999995050514153,
        "source": 4,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 4,
        "target": 24,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.6027440503139042,
        "before": 0.0,
        "source": 4,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 4,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 4,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 4,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 4,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 4,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 4,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 4,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 4,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5630578072154955,
        "before": 0.5192045708736565,
        "source": 5,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246578212566193,
        "before": 0.5192046186557173,
        "source": 5,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286954049064785,
        "before": 4.388107100564929e-06,
        "source": 5,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286988486767341,
        "before": 4.505298888308438e-06,
        "source": 5,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996553720393,
        "before": 0.9999988272281883,
        "source": 5,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6277423642706136,
        "before": 2.552705194745675e-08,
        "source": 5,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999979865217822,
        "before": 0.9999931481169049,
        "source": 5,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.12750976214978704,
        "before": 5.763613368649279e-06,
        "source": 5,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04910975128532449,
        "before": 5.726641512264384e-06,
        "source": 5,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04911023553484065,
        "before": 7.374546636808252e-06,
        "source": 5,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246578244117146,
        "before": 0.5192046293925321,
        "source": 5,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992803227145,
        "before": 0.9999975509322213,
        "source": 5,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993005536262,
        "before": 0.9999976197781826,
        "source": 5,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753029946861575,
        "before": 0.51920837884919,
        "source": 5,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986969541613,
        "before": 0.9999955657241902,
        "source": 5,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992586271176,
        "before": 0.9999974771019251,
        "source": 5,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999981936503985,
        "before": 0.9999938529773076,
        "source": 5,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030342516251,
        "before": 0.519208513490805,
        "source": 5,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.575303036461771,
        "before": 0.51920852101195,
        "source": 5,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.575303036461771,
        "before": 0.51920852101195,
        "source": 5,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.575303036461771,
        "before": 0.51920852101195,
        "source": 5,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999980820398238,
        "before": 0.9999934731655937,
        "source": 5,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991531450235,
        "before": 0.9999971181454832,
        "source": 5,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995718179568,
        "before": 0.999998542892952,
        "source": 5,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995718179568,
        "before": 0.999998542892952,
        "source": 5,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.6354877502413707,
        "before": 0.6202997398347612,
        "source": 5,
        "target": 61,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.39715593357736373,
        "before": 0.3720374308097539,
        "source": 5,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999988577542946,
        "before": 0.9999961129283794,
        "source": 5,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991420057863,
        "before": 0.9999970802385663,
        "source": 5,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999985455557537,
        "before": 0.999995050514153,
        "source": 5,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 5,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 5,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 5,
        "target": 24,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.6027440503139042,
        "before": 0.0,
        "source": 5,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 5,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 5,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 5,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122035183029303,
        "before": 0.48078632784333963,
        "source": 5,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 5,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 5,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5630577853940375,
        "before": 0.5192044966150531,
        "source": 6,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246577828532978,
        "before": 0.5192044879688946,
        "source": 6,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286950179265686,
        "before": 4.374938142076242e-06,
        "source": 6,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286996156420615,
        "before": 4.531398782075578e-06,
        "source": 6,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.12750977702727828,
        "before": 5.814241594748609e-06,
        "source": 6,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04910976253075723,
        "before": 5.764909813273845e-06,
        "source": 6,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.049110248955951695,
        "before": 7.420218789145441e-06,
        "source": 6,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5246578084003901,
        "before": 0.5192045749058628,
        "source": 6,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6277423674152643,
        "before": 3.622832531711713e-08,
        "source": 6,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986379670759,
        "before": 0.9999953649906493,
        "source": 6,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992093719177,
        "before": 0.9999973094860707,
        "source": 6,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999997954324414,
        "before": 0.9999930385489937,
        "source": 6,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999981450986599,
        "before": 0.9999936877553375,
        "source": 6,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753029896423467,
        "before": 0.5192083616850609,
        "source": 6,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030422966758,
        "before": 0.5192085408681792,
        "source": 6,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030452819123,
        "before": 0.5192085510269634,
        "source": 6,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030452819123,
        "before": 0.5192085510269634,
        "source": 6,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5753030452819123,
        "before": 0.5192085510269634,
        "source": 6,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.5901195019790273,
        "before": 0.5730411478948201,
        "source": 6,
        "target": 61,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999980603570705,
        "before": 0.9999933993790042,
        "source": 6,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991640625955,
        "before": 0.999997155298071,
        "source": 6,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995835114691,
        "before": 0.9999985826860706,
        "source": 6,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995835114691,
        "before": 0.9999985826860706,
        "source": 6,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.45295719622819264,
        "before": 0.43016374607103397,
        "source": 6,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999988244050059,
        "before": 0.9999959994404729,
        "source": 6,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999025526589,
        "before": 0.9999966838588908,
        "source": 6,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999985455557537,
        "before": 0.999995050514153,
        "source": 6,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 6,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.01383923392734789,
        "before": 0.0,
        "source": 6,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 6,
        "target": 24,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.6027440503139042,
        "before": 0.0,
        "source": 6,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.0784,
        "before": 0.0,
        "source": 6,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 6,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 6,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 6,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 6,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5122033413032959,
        "before": 0.4807857255121141,
        "source": 6,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.014417260006289793,
        "before": 4.363512647152198e-06,
        "source": 8,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5258873683620272,
        "before": 0.5192045418356117,
        "source": 8,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5258873856376608,
        "before": 0.5192045960156692,
        "source": 8,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.014417297383425358,
        "before": 4.480735285131389e-06,
        "source": 8,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.05328749651084798,
        "before": 5.745354903377426e-06,
        "source": 8,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.05328748675394282,
        "before": 5.714755175954786e-06,
        "source": 8,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.05328801289616519,
        "before": 7.364848965585305e-06,
        "source": 8,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992150311422,
        "before": 0.9999975381708933,
        "source": 8,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5258873913108463,
        "before": 0.5192046138079837,
        "source": 8,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999978069043984,
        "before": 0.9999931219862651,
        "source": 8,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999980331214684,
        "before": 0.9999938314510564,
        "source": 8,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5391742492828335,
        "before": 0.519208356569361,
        "source": 8,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5391742926329522,
        "before": 0.519208492524542,
        "source": 8,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5391742959212572,
        "before": 0.5192085028373663,
        "source": 8,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5391742959212572,
        "before": 0.5192085028373663,
        "source": 8,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5391742959212572,
        "before": 0.5192085028373663,
        "source": 8,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999979086674268,
        "before": 0.999993441136741,
        "source": 8,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990755690376,
        "before": 0.999997100788104,
        "source": 8,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995307495608,
        "before": 0.9999985283309294,
        "source": 8,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995307495608,
        "before": 0.9999985283309294,
        "source": 8,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992363045068,
        "before": 0.9999976048886845,
        "source": 8,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997684044559,
        "before": 0.9999992736671706,
        "source": 8,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999987526951187,
        "before": 0.9999960881868991,
        "source": 8,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.4072506675748259,
        "before": 0.382552778723777,
        "source": 8,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.6811440626610018,
        "before": 3.872312103070979e-08,
        "source": 8,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999985971111011,
        "before": 0.9999956002423648,
        "source": 8,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990283308828,
        "before": 0.9999969526392146,
        "source": 8,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990690166952,
        "before": 0.9999970802385663,
        "source": 8,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992884174025,
        "before": 0.9999977683257966,
        "source": 8,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999984218269898,
        "before": 0.999995050514153,
        "source": 8,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.015016529869084083,
        "before": 0.0,
        "source": 8,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.015016529869084083,
        "before": 0.0,
        "source": 8,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5141095283238888,
        "before": 0.4807857255121141,
        "source": 8,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5141093199288204,
        "before": 0.48078507194090586,
        "source": 8,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5141093199288204,
        "before": 0.48078507194090586,
        "source": 8,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5141093199288204,
        "before": 0.48078507194090586,
        "source": 8,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5141093199288204,
        "before": 0.48078507194090586,
        "source": 8,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025122186181661964,
        "before": 0.0010869929126122268,
        "source": 9,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.02512209155148426,
        "before": 0.001086825328673625,
        "source": 9,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.02417277486956454,
        "before": 0.0011417578518320972,
        "source": 9,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.02417277486956454,
        "before": 0.0011417578518320972,
        "source": 9,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.024430821186221266,
        "before": 0.0015987412279021883,
        "source": 9,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994101680272235,
        "before": 0.9989554456357848,
        "source": 9,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994220266803598,
        "before": 0.998976446545296,
        "source": 9,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994220266803598,
        "before": 0.998976446545296,
        "source": 9,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991074331888975,
        "before": 0.9984193217714155,
        "source": 9,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991421468883126,
        "before": 0.998480797493139,
        "source": 9,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999533435200431,
        "before": 0.9991737438455819,
        "source": 9,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9997867242041985,
        "before": 0.9996223023274959,
        "source": 9,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9998672570725768,
        "before": 0.9997649208409204,
        "source": 9,
        "target": 167,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995906558378373,
        "before": 0.9992750779022024,
        "source": 9,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9998672570725768,
        "before": 0.9997649208409204,
        "source": 9,
        "target": 171,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992079139532373,
        "before": 0.998597266721427,
        "source": 9,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992928903590795,
        "before": 0.998747754452975,
        "source": 9,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4353266876448864,
        "before": 0.0,
        "source": 9,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 9,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 9,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 9,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025112213366993725,
        "before": 0.0010693317013418563,
        "source": 10,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025112087557729108,
        "before": 0.0010691089012522211,
        "source": 10,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0241353396898614,
        "before": 0.0010754625641249207,
        "source": 10,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999110731827807,
        "before": 0.9984251634480756,
        "source": 10,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999147590233603,
        "before": 0.9984904373064106,
        "source": 10,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999499144829014,
        "before": 0.999113017810427,
        "source": 10,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9997631788346237,
        "before": 0.999580604997271,
        "source": 10,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9998437117030023,
        "before": 0.9997232235106954,
        "source": 10,
        "target": 167,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995638192766932,
        "before": 0.9992275520840757,
        "source": 10,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9998437117030023,
        "before": 0.9997232235106954,
        "source": 10,
        "target": 171,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992130509050092,
        "before": 0.9986063639315472,
        "source": 10,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993013438827137,
        "before": 0.998762725097858,
        "source": 10,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4353266876448864,
        "before": 0.0,
        "source": 10,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 10,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 10,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 10,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 10,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023682805672591945,
        "before": 0.0002740540198074158,
        "source": 10,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 10,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 10,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991150457446001,
        "before": 0.9984328031163557,
        "source": 12,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991519382077072,
        "before": 0.998498137287991,
        "source": 12,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025102052436455868,
        "before": 0.0010513373490047906,
        "source": 12,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994900987533568,
        "before": 0.9990969977941465,
        "source": 12,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992181830775955,
        "before": 0.9986154526780382,
        "source": 12,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023682805672591945,
        "before": 0.0002740540198074158,
        "source": 12,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023682805672591945,
        "before": 0.0002740540198074158,
        "source": 12,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 12,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 12,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196157887,
        "before": 2.5599688638950606e-11,
        "source": 13,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6110121693485513,
        "before": 0.5224571423516672,
        "source": 13,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.29916504060288884,
        "before": 0.2829481777375096,
        "source": 13,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.517985974449035,
        "before": 0.5018851177354816,
        "source": 13,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489042,
        "before": 0.5018851177340845,
        "source": 13,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489296,
        "before": 0.5018851177343564,
        "source": 13,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5902394164341217,
        "before": 0.501885138921432,
        "source": 13,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996628724373064,
        "before": 0.9964019868647291,
        "source": 13,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196199821,
        "before": 2.6047259024994064e-11,
        "source": 13,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631078,
        "before": 0.768118623165143,
        "source": 13,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631206,
        "before": 0.768118623165281,
        "source": 13,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631913,
        "before": 0.7681186231660332,
        "source": 13,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631806,
        "before": 0.7681186231659171,
        "source": 13,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631792,
        "before": 0.7681186231659053,
        "source": 13,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.7788306701561347,
        "before": 1.0942629449090861e-12,
        "source": 13,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7556483020951554,
        "before": 1.6532111402700815e-16,
        "source": 13,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.8090978630893052,
        "before": 0.7928579243590551,
        "source": 13,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7856342267793253,
        "before": 0.7673982495435386,
        "source": 13,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04609764245511286,
        "before": 0.0063517108907425604,
        "source": 13,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.8538284266695855,
        "before": 0.8477379444474848,
        "source": 13,
        "target": 75,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9996628724377843,
        "before": 0.9964019868698286,
        "source": 13,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858344,
        "before": 0.7337664945693517,
        "source": 13,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858344,
        "before": 0.7337664945693517,
        "source": 13,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858344,
        "before": 0.7337664945693517,
        "source": 13,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858311,
        "before": 0.7337664945693172,
        "source": 13,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858301,
        "before": 0.7337664945693044,
        "source": 13,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99966287243861,
        "before": 0.9964019868786427,
        "source": 13,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212859616,
        "before": 0.7337664945707061,
        "source": 13,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.9992102933740606,
        "before": 0.9991431134701179,
        "source": 13,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.997717484565735,
        "before": 0.9975233122458061,
        "source": 13,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6803924749692954,
        "before": 0.6670754947596828,
        "source": 13,
        "target": 25,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6973653684302646,
        "before": 0.684755592114859,
        "source": 13,
        "target": 26,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5326986150744863,
        "before": 0.5132277240359233,
        "source": 13,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6362625547903616,
        "before": 0.6211068279066267,
        "source": 13,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5326986150744863,
        "before": 0.5132277240359233,
        "source": 13,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6921261045394949,
        "before": 0.6792980255619738,
        "source": 13,
        "target": 55,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.545972524431043,
        "before": 0.5270547129490032,
        "source": 13,
        "target": 1,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6427754526052697,
        "before": 0.6278910964638226,
        "source": 13,
        "target": 56,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6427754526052697,
        "before": 0.6278910964638226,
        "source": 13,
        "target": 73,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6819430583273671,
        "before": 0.6686906857576741,
        "source": 13,
        "target": 72,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.7090670312937423,
        "before": 0.6969448242643148,
        "source": 13,
        "target": 112,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 13,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 13,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 13,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424428648,
        "before": 0.5036162959929703,
        "source": 13,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 13,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 13,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 13,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 13,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 13,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 13,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 13,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 13,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 13,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 13,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 13,
        "target": 44,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 13,
        "target": 45,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 13,
        "target": 46,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 13,
        "target": 47,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 13,
        "target": 49,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 13,
        "target": 9,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 13,
        "target": 10,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 13,
        "target": 12,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 13,
        "target": 22,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 13,
        "target": 23,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144221962,
        "before": 0.7409359302560184,
        "source": 13,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7476774433498256,
        "before": 4.679041276716544e-13,
        "source": 14,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5133374945588697,
        "before": 0.5018851177408903,
        "source": 14,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.807470102051498,
        "before": 0.7681186231616827,
        "source": 14,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5133374945589113,
        "before": 0.5018851177412991,
        "source": 14,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5133374945588657,
        "before": 0.501885117740852,
        "source": 14,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5855909367130322,
        "before": 0.5018851389288622,
        "source": 14,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996341931832575,
        "before": 0.9964019868688235,
        "source": 14,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.611095998467775,
        "before": 0.5224571423464234,
        "source": 14,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.535831998467664,
        "before": 0.5224571423453304,
        "source": 14,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5358319984686861,
        "before": 0.5224571423553863,
        "source": 14,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020515465,
        "before": 0.7681186231621573,
        "source": 14,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020515465,
        "before": 0.7681186231621573,
        "source": 14,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020515033,
        "before": 0.7681186231617328,
        "source": 14,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8074701020515033,
        "before": 0.7681186231617328,
        "source": 14,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999634193183771,
        "before": 0.9964019868738738,
        "source": 14,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.22919355605170713,
        "before": 0.20702425786860582,
        "source": 14,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802272,
        "source": 14,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074751,
        "before": 0.7337664945802272,
        "source": 14,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074729,
        "before": 0.7337664945802048,
        "source": 14,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074729,
        "before": 0.7337664945802048,
        "source": 14,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074729,
        "before": 0.7337664945802048,
        "source": 14,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7427313925074742,
        "before": 0.7337664945802185,
        "source": 14,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 14,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.11526400275193481,
        "before": 2.3947643714018287e-08,
        "source": 14,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5028080244428804,
        "before": 0.4795017811606573,
        "source": 14,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5028080244428804,
        "before": 0.4795017811606573,
        "source": 14,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.004236213196182257,
        "before": 2.5859763245184063e-11,
        "source": 15,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196157972,
        "before": 2.5600587054904595e-11,
        "source": 15,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631066,
        "before": 0.768118623165128,
        "source": 15,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.80966435316312,
        "before": 0.7681186231652726,
        "source": 15,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631906,
        "before": 0.7681186231660245,
        "source": 15,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631789,
        "before": 0.768118623165901,
        "source": 15,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631774,
        "before": 0.7681186231658835,
        "source": 15,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6110121693485472,
        "before": 0.5224571423516237,
        "source": 15,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5357481693485466,
        "before": 0.5224571423516164,
        "source": 15,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.06183214556752829,
        "before": 0.025425505173099276,
        "source": 15,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9996878377607047,
        "before": 0.9996612822924313,
        "source": 15,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7556483020951557,
        "before": 3.6702074143798045e-15,
        "source": 15,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.7788306701562606,
        "before": 2.2836230678591708e-12,
        "source": 15,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.4375089373179,
        "before": 0.4330609128883464,
        "source": 15,
        "target": 73,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.45064472843408354,
        "before": 0.4473141584571219,
        "source": 15,
        "target": 61,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9997940423732385,
        "before": 0.9997765216723509,
        "source": 15,
        "target": 188,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9990702186090689,
        "before": 0.9989911226226876,
        "source": 15,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7266339914429232,
        "before": 0.7033788969649775,
        "source": 15,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9996628724377927,
        "before": 0.9964019868699197,
        "source": 15,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.7621792651811857,
        "before": 0.7419479873927797,
        "source": 15,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9996628724373142,
        "before": 0.9964019868648126,
        "source": 15,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744490444,
        "before": 0.5018851177355809,
        "source": 15,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489131,
        "before": 0.501885117734181,
        "source": 15,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489387,
        "before": 0.5018851177344529,
        "source": 15,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5902394164341304,
        "before": 0.5018851389215246,
        "source": 15,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.9266569587440382,
        "before": 0.9204177069705275,
        "source": 15,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 15,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 15,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 15,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 15,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 15,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 15,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 15,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 15,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 15,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 15,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 15,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 15,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 15,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 15,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424377738,
        "before": 0.5036162959449006,
        "source": 15,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 15,
        "target": 44,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 15,
        "target": 45,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720727013175,
        "before": 0.7430529339940617,
        "source": 15,
        "target": 46,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 15,
        "target": 9,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 15,
        "target": 10,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695064157,
        "before": 0.7671674248211388,
        "source": 15,
        "target": 12,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144221962,
        "before": 0.7409359302560184,
        "source": 15,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720726985496,
        "before": 0.7430529339679255,
        "source": 15,
        "target": 47,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720726985496,
        "before": 0.7430529339679255,
        "source": 15,
        "target": 49,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 15,
        "target": 22,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 15,
        "target": 23,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5179859744489979,
        "before": 0.5018851177350849,
        "source": 16,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489931,
        "before": 0.5018851177350355,
        "source": 16,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744490765,
        "before": 0.5018851177359236,
        "source": 16,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5902394164342125,
        "before": 0.5018851389224034,
        "source": 16,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996628724375524,
        "before": 0.9964019868673551,
        "source": 16,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196193788,
        "before": 2.5982845923049176e-11,
        "source": 16,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.3257945689734938,
        "before": 0.3118430652924195,
        "source": 16,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9996628724381882,
        "before": 0.9964019868741413,
        "source": 16,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.7788306701562248,
        "before": 1.9456872653952456e-12,
        "source": 16,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999998857876811,
        "before": 0.9999998760717025,
        "source": 16,
        "target": 188,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999990994860052,
        "before": 0.9999990228797799,
        "source": 16,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999991355065649,
        "before": 0.9999990619645888,
        "source": 16,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7850751120164223,
        "before": 0.7667915711983749,
        "source": 16,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04975325367535477,
        "before": 0.010159639245161224,
        "source": 16,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.7908678648288976,
        "before": 0.782154025863435,
        "source": 16,
        "target": 75,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7556483020951555,
        "before": 1.1517203633495115e-15,
        "source": 16,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858549,
        "before": 0.7337664945695697,
        "source": 16,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858549,
        "before": 0.7337664945695697,
        "source": 16,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858549,
        "before": 0.7337664945695697,
        "source": 16,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858404,
        "before": 0.7337664945694137,
        "source": 16,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.745185621285835,
        "before": 0.7337664945693563,
        "source": 16,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996628724386268,
        "before": 0.9964019868788211,
        "source": 16,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212858412,
        "before": 0.7337664945694229,
        "source": 16,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999662872438642,
        "before": 0.9964019868789841,
        "source": 16,
        "target": 136,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.9943966648951315,
        "before": 0.9939199922907243,
        "source": 16,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5830382807514399,
        "before": 0.5656648757827499,
        "source": 16,
        "target": 25,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5830382807514399,
        "before": 0.5656648757827499,
        "source": 16,
        "target": 26,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.47713649365194744,
        "before": 0.4553505142207786,
        "source": 16,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5251206336228033,
        "before": 0.5053339933570867,
        "source": 16,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.47713649365194744,
        "before": 0.4553505142207786,
        "source": 16,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5125693907957929,
        "before": 0.49225978207895094,
        "source": 16,
        "target": 1,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6017396178901777,
        "before": 0.5851454353022685,
        "source": 16,
        "target": 55,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5537031729155238,
        "before": 0.535107471787004,
        "source": 16,
        "target": 56,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.109478907904,
        "before": 0.0723738624,
        "source": 16,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.109478907904,
        "before": 0.0723738624,
        "source": 16,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.15065344,
        "before": 0.115264,
        "source": 16,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.004236213194593269,
        "before": 8.901192693626669e-12,
        "source": 16,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 16,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585496700566,
        "before": 0.0,
        "source": 16,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585496700566,
        "before": 0.0,
        "source": 16,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 16,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 16,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 16,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 16,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 16,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 16,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 16,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424377738,
        "before": 0.5036162959449006,
        "source": 16,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144221962,
        "before": 0.7409359302560184,
        "source": 16,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720726985496,
        "before": 0.7430529339679255,
        "source": 16,
        "target": 44,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720726985496,
        "before": 0.7430529339679255,
        "source": 16,
        "target": 45,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7742720726985496,
        "before": 0.7430529339679255,
        "source": 16,
        "target": 46,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 16,
        "target": 9,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 16,
        "target": 10,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 16,
        "target": 12,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 16,
        "target": 22,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 16,
        "target": 23,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.6110121693485062,
        "before": 0.5224571423511859,
        "source": 17,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5357481693484983,
        "before": 0.5224571423511013,
        "source": 17,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7556483020951554,
        "before": 5.501467936567807e-16,
        "source": 17,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196154659,
        "before": 2.5565255581246975e-11,
        "source": 17,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196128269,
        "before": 2.5283606349432717e-11,
        "source": 17,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5357481693489441,
        "before": 0.5224571423558576,
        "source": 17,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744490125,
        "before": 0.5018851177352406,
        "source": 17,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744488797,
        "before": 0.501885117733824,
        "source": 17,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.590239416434098,
        "before": 0.5018851389211817,
        "source": 17,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.36674452775537886,
        "before": 0.3562766143179024,
        "source": 17,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.8096643531631882,
        "before": 0.7681186231659999,
        "source": 17,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.9999998781625263,
        "before": 0.9999998677978802,
        "source": 17,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999998830360253,
        "before": 0.9999998730859649,
        "source": 17,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.8576732198473243,
        "before": 0.8455655597301696,
        "source": 17,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7705558066912364,
        "before": 0.751037116635456,
        "source": 17,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.049636418850586776,
        "before": 0.010037936302694563,
        "source": 17,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.7734115665452382,
        "before": 0.7639703818179565,
        "source": 17,
        "target": 75,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701560187,
        "before": 0.0,
        "source": 17,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9982848095331786,
        "before": 0.9981388992330497,
        "source": 17,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9950425277126589,
        "before": 0.9946207982993261,
        "source": 17,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6895780062133602,
        "before": 0.6766437564722502,
        "source": 17,
        "target": 25,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.7121649387075649,
        "before": 0.7001718111537134,
        "source": 17,
        "target": 26,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.41069828153550464,
        "before": 0.38614404326615065,
        "source": 17,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.528877367852294,
        "before": 0.5092472581794729,
        "source": 17,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.41069828153550464,
        "before": 0.38614404326615065,
        "source": 17,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.4840658948650026,
        "before": 0.46256864048437774,
        "source": 17,
        "target": 1,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7629478161857484,
        "before": 0.7543385191897796,
        "source": 17,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7629478161856156,
        "before": 0.7543385191883645,
        "source": 17,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7629478161857484,
        "before": 0.7543385191897796,
        "source": 17,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7629478161857484,
        "before": 0.7543385191897796,
        "source": 17,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7629478161857484,
        "before": 0.7543385191897796,
        "source": 17,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 17,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 17,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 17,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 17,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 17,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 17,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 17,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 17,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 17,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430966377,
        "before": 0.4795017811715497,
        "source": 17,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424377738,
        "before": 0.5036162959449006,
        "source": 17,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7923895695034122,
        "before": 0.7671674247927791,
        "source": 17,
        "target": 9,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144189372,
        "before": 0.7409359302252461,
        "source": 17,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701561544,
        "before": 1.2819256203475251e-12,
        "source": 18,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.2805400236879006,
        "before": 0.2627387409807949,
        "source": 18,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999990619645888,
        "before": 0.9999989821664375,
        "source": 18,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7980630124352169,
        "before": 0.7808843450902961,
        "source": 18,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7838482142800349,
        "before": 0.765460301953163,
        "source": 18,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.004236213196082404,
        "before": 2.479406036735718e-11,
        "source": 18,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7556483020951554,
        "before": 4.148281763587496e-16,
        "source": 18,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.99798057642475,
        "before": 0.9978087851831056,
        "source": 18,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.004236213196126145,
        "before": 2.5260895288285337e-11,
        "source": 18,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489418,
        "before": 0.501885117734485,
        "source": 18,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489682,
        "before": 0.5018851177347678,
        "source": 18,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5902394164341593,
        "before": 0.5018851389218347,
        "source": 18,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6110121693485165,
        "before": 0.5224571423512974,
        "source": 18,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.535748169348513,
        "before": 0.5224571423512594,
        "source": 18,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5357481693489686,
        "before": 0.5224571423561237,
        "source": 18,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.517985974449077,
        "before": 0.5018851177359296,
        "source": 18,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531630758,
        "before": 0.7681186231648013,
        "source": 18,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531630889,
        "before": 0.768118623164941,
        "source": 18,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631622,
        "before": 0.7681186231657244,
        "source": 18,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.809664353163151,
        "before": 0.7681186231656034,
        "source": 18,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.80966435316315,
        "before": 0.768118623165591,
        "source": 18,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996628724373468,
        "before": 0.9964019868651613,
        "source": 18,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 18,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.40912753282217107,
        "before": 0.3845078466897615,
        "source": 18,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5063196234975109,
        "before": 0.48574960780990717,
        "source": 18,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.40912753282217107,
        "before": 0.3845078466897615,
        "source": 18,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 18,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.16613011246798642,
        "before": 0.1313855338208192,
        "source": 18,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 18,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9996628724367536,
        "before": 0.9964019868588282,
        "source": 18,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 18,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 18,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7451856212829985,
        "before": 0.7337664945390835,
        "source": 18,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 18,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 18,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600841895,
        "before": 0.49638372786847756,
        "source": 18,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 18,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 18,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 18,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 18,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600830818,
        "before": 0.49638372785802076,
        "source": 18,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424363591,
        "before": 0.5036162959315419,
        "source": 18,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144189372,
        "before": 0.7409359302252461,
        "source": 18,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.29916503262816135,
        "before": 0.2829481690843765,
        "source": 19,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999461475401,
        "before": 0.9999999415663412,
        "source": 19,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999483016384,
        "before": 0.9999999439036875,
        "source": 19,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7856342267793253,
        "before": 0.7673982495435386,
        "source": 19,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701560187,
        "before": 0.0,
        "source": 19,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9992102933740606,
        "before": 0.9991431134701179,
        "source": 19,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.8076589075016662,
        "before": 0.7912965576189954,
        "source": 19,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.997717484565735,
        "before": 0.9975233122458061,
        "source": 19,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 19,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5193054249925129,
        "before": 0.49927648436720085,
        "source": 19,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6228693647083883,
        "before": 0.6071555882379045,
        "source": 19,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5193054249925129,
        "before": 0.49927648436720085,
        "source": 19,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 19,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 19,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 19,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 19,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 19,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 19,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 19,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 19,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430954838,
        "before": 0.4795017811606573,
        "source": 19,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430941258,
        "before": 0.47950178114783304,
        "source": 19,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600817782,
        "before": 0.4963837278457094,
        "source": 19,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600817782,
        "before": 0.4963837278457094,
        "source": 19,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5175732600817782,
        "before": 0.4963837278457094,
        "source": 19,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424363591,
        "before": 0.5036162959315419,
        "source": 19,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144189372,
        "before": 0.7409359302252461,
        "source": 19,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.29916503246852444,
        "before": 0.2829481689111593,
        "source": 20,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999461475401,
        "before": 0.9999999415663412,
        "source": 20,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999483016384,
        "before": 0.9999999439036875,
        "source": 20,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7856342267793253,
        "before": 0.7673982495435386,
        "source": 20,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9992102933740606,
        "before": 0.9991431134701179,
        "source": 20,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.8076589075016662,
        "before": 0.7912965576189954,
        "source": 20,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.997717484565735,
        "before": 0.9975233122458061,
        "source": 20,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 20,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5193054249925129,
        "before": 0.49927648436720085,
        "source": 20,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.6228693647083883,
        "before": 0.6071555882379045,
        "source": 20,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5193054249925129,
        "before": 0.49927648436720085,
        "source": 20,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 20,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 20,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 20,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701560187,
        "before": 0.0,
        "source": 20,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 20,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 20,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 20,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430941258,
        "before": 0.47950178114783304,
        "source": 20,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430941258,
        "before": 0.47950178114783304,
        "source": 20,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430941258,
        "before": 0.47950178114783304,
        "source": 20,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430941258,
        "before": 0.47950178114783304,
        "source": 20,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5576907424363591,
        "before": 0.5036162959315419,
        "source": 20,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144189372,
        "before": 0.7409359302252461,
        "source": 20,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.29916503246852444,
        "before": 0.2829481689111593,
        "source": 21,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999461475401,
        "before": 0.9999999415663412,
        "source": 21,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9999999483016384,
        "before": 0.9999999439036875,
        "source": 21,
        "target": 227,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7856342267793253,
        "before": 0.7673982495435386,
        "source": 21,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.9992102933740606,
        "before": 0.9991431134701179,
        "source": 21,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.8076589075016662,
        "before": 0.7912965576189954,
        "source": 21,
        "target": 74,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.997717484565735,
        "before": 0.9975233122458061,
        "source": 21,
        "target": 369,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 21,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.4718675561826666,
        "before": 0.4498620376902777,
        "source": 21,
        "target": 39,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.5690596468580063,
        "before": 0.5511037988104232,
        "source": 21,
        "target": 40,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.4718675561826666,
        "before": 0.4498620376902777,
        "source": 21,
        "target": 41,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 21,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 21,
        "target": 80,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.13953680702832638,
        "before": 0.10368417398783998,
        "source": 21,
        "target": 95,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701560187,
        "before": 0.0,
        "source": 21,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 21,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585497516429,
        "before": 7.703683214059443e-12,
        "source": 21,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 21,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144189372,
        "before": 0.7409359302252461,
        "source": 21,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430884273,
        "before": 0.47950178109402597,
        "source": 21,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5027092430884273,
        "before": 0.47950178109402597,
        "source": 21,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9991750111207327,
        "before": 0.9985389979281536,
        "source": 22,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992058055477805,
        "before": 0.9985935328714101,
        "source": 22,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025149133765263846,
        "before": 0.0011347153443479981,
        "source": 22,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995488770053744,
        "before": 0.9992010902857369,
        "source": 22,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4353266876448864,
        "before": 0.0,
        "source": 22,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992418816390982,
        "before": 0.9986574213012832,
        "source": 22,
        "target": 119,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023682805672591945,
        "before": 0.0002740540198074158,
        "source": 22,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023682805672591945,
        "before": 0.0002740540198074158,
        "source": 22,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 22,
        "target": 170,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 22,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.025164360811729448,
        "before": 0.001161681461096279,
        "source": 23,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995627846425933,
        "before": 0.9992257198138458,
        "source": 23,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4353266876448864,
        "before": 0.0,
        "source": 23,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992418816390982,
        "before": 0.9986574213012832,
        "source": 23,
        "target": 119,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 23,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988121722924121,
        "before": 0.9978964337757813,
        "source": 23,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.023528054681463056,
        "before": 0.0,
        "source": 23,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.014416703831393022,
        "before": 2.5144608096625194e-06,
        "source": 24,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013840779338263422,
        "before": 4.652867479399517e-06,
        "source": 24,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.01441673158791134,
        "before": 2.5980291345087707e-06,
        "source": 24,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6678584210324611,
        "before": 1.0624627905628479e-07,
        "source": 24,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999904772740644,
        "before": 0.9999713293200042,
        "source": 24,
        "target": 1,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5169823451323816,
        "before": 0.5102036697865869,
        "source": 24,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5169826393863642,
        "before": 0.5102045557158712,
        "source": 24,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0138406491312774,
        "before": 4.260844979272449e-06,
        "source": 24,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013840627075718448,
        "before": 4.19444089737054e-06,
        "source": 24,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999907886772533,
        "before": 0.9999722668815004,
        "source": 24,
        "target": 56,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993926551705,
        "before": 0.9999981714280792,
        "source": 24,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991357034429,
        "before": 0.99999739780708,
        "source": 24,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992090945581,
        "before": 0.9999976187704035,
        "source": 24,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994476094674,
        "before": 0.9999983368824957,
        "source": 24,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997984227835,
        "before": 0.9999993930985828,
        "source": 24,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999991227194976,
        "before": 0.9999735871548537,
        "source": 24,
        "target": 55,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998387069878,
        "before": 0.9999995143848133,
        "source": 24,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49685763557664425,
        "before": 0.4897985785967717,
        "source": 24,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4968577050851105,
        "before": 0.48979878787035674,
        "source": 24,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49685770958778097,
        "before": 0.4897988014268341,
        "source": 24,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49685770958778097,
        "before": 0.4897988014268341,
        "source": 24,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49685770958749653,
        "before": 0.4897988014259779,
        "source": 24,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997671555332,
        "before": 0.9999992989602724,
        "source": 24,
        "target": 119,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998675636814,
        "before": 0.9999996012655059,
        "source": 24,
        "target": 166,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994500483084,
        "before": 0.9999983442252701,
        "source": 24,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994500483084,
        "before": 0.9999983442252701,
        "source": 24,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994500483084,
        "before": 0.9999983442252701,
        "source": 24,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994155156913,
        "before": 0.9999982402557108,
        "source": 24,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990996519093,
        "before": 0.999997289264422,
        "source": 24,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991346656333,
        "before": 0.9999973946824801,
        "source": 24,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986455027237,
        "before": 0.9999959219284237,
        "source": 24,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516981153971725,
        "before": 0.5102000834830177,
        "source": 24,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516981153971725,
        "before": 0.5102000834830177,
        "source": 24,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516981153971725,
        "before": 0.5102000834830177,
        "source": 24,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516981153971725,
        "before": 0.5102000834830177,
        "source": 24,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516981153971725,
        "before": 0.5102000834830177,
        "source": 24,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999888955840169,
        "before": 0.9999665672246217,
        "source": 24,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012755651915558006,
        "before": 4.61914474881341e-06,
        "source": 25,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286483153824614,
        "before": 2.674220820572158e-06,
        "source": 25,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286435665695677,
        "before": 2.519082423362742e-06,
        "source": 25,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6154983068163604,
        "before": 6.048647101922784e-08,
        "source": 25,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999912426719597,
        "before": 0.9999713907903631,
        "source": 25,
        "target": 1,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5548509463544226,
        "before": 0.5102037255864045,
        "source": 25,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164512075539227,
        "before": 0.5102045788959094,
        "source": 25,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012755532797311642,
        "before": 4.229998782556098e-06,
        "source": 25,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012755513682215612,
        "before": 4.167551905292608e-06,
        "source": 25,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4963039823549338,
        "before": 0.48979853092470405,
        "source": 25,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4963040462793007,
        "before": 0.48979873975844995,
        "source": 25,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4963040487201373,
        "before": 0.48979874773238863,
        "source": 25,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992315939695,
        "before": 0.9999974897035826,
        "source": 25,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995133387092,
        "before": 0.9999984101320832,
        "source": 25,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992954400888,
        "before": 0.9999976982817015,
        "source": 25,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997866965508,
        "before": 0.9999993031615276,
        "source": 25,
        "target": 119,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998315441376,
        "before": 0.9999994496735697,
        "source": 25,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998841096205,
        "before": 0.9999996213991127,
        "source": 25,
        "target": 166,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991829963109,
        "before": 0.9999973309404756,
        "source": 25,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992216969594,
        "before": 0.9999974573711584,
        "source": 25,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999875169531,
        "before": 0.9999959219284237,
        "source": 25,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999875169531,
        "before": 0.9999959219284237,
        "source": 25,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999875169531,
        "before": 0.9999959219284237,
        "source": 25,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999875169531,
        "before": 0.9999959219284237,
        "source": 25,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999875169531,
        "before": 0.9999959219284237,
        "source": 25,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164498315003417,
        "before": 0.5102000834830177,
        "source": 25,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164498315003417,
        "before": 0.5102000834830177,
        "source": 25,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164498315003417,
        "before": 0.5102000834830177,
        "source": 25,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 25,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 25,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 25,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 25,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99998976617023,
        "before": 0.9999665672246217,
        "source": 25,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012755485028859082,
        "before": 4.073944599495514e-06,
        "source": 26,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6154983219793494,
        "before": 1.1002225767411378e-07,
        "source": 26,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286573158586976,
        "before": 2.9682562961328557e-06,
        "source": 26,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.013286491736777848,
        "before": 2.7022603672341024e-06,
        "source": 26,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5548510173361142,
        "before": 0.5102039574756391,
        "source": 26,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990750266828,
        "before": 0.9999969782157965,
        "source": 26,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993734090267,
        "before": 0.9999979529974865,
        "source": 26,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991749686392,
        "before": 0.9999973047149714,
        "source": 26,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996762150524,
        "before": 0.999998942230849,
        "source": 26,
        "target": 119,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.516451000647139,
        "before": 0.5102039029546268,
        "source": 26,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997341358249,
        "before": 0.9999991314515246,
        "source": 26,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995108533016,
        "before": 0.9999984020125339,
        "source": 26,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995657594086,
        "before": 0.9999985813846357,
        "source": 26,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012754237987443816,
        "before": 0.0,
        "source": 26,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.012754237987443816,
        "before": 0.0,
        "source": 26,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 26,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 26,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 26,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 26,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5164497273889148,
        "before": 0.5101997433626494,
        "source": 26,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 26,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 26,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 26,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 26,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49630155400262765,
        "before": 0.4897905977697646,
        "source": 26,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99998976617023,
        "before": 0.9999665672246217,
        "source": 26,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962502895186865,
        "before": 0.9877501159320375,
        "source": 30,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.615498288906257,
        "before": 1.976169306910439e-09,
        "source": 30,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999989748974707,
        "before": 0.9999966511048778,
        "source": 30,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.508703521200132,
        "before": 0.48489375553985414,
        "source": 30,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999985875920653,
        "before": 0.9999953858215072,
        "source": 30,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998646293954,
        "before": 0.9999995577594001,
        "source": 30,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.996250388889303,
        "before": 0.9877504405647088,
        "source": 30,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694161806073557,
        "before": 0.5192084815908024,
        "source": 30,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294161536507554,
        "before": 0.5192083935266095,
        "source": 30,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294163867343608,
        "before": 0.5192091549846359,
        "source": 30,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993459676603,
        "before": 0.9999978633496165,
        "source": 30,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993553684678,
        "before": 0.9999978940610021,
        "source": 30,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999987142676748,
        "before": 0.9999957996565327,
        "source": 30,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999905828111,
        "before": 0.9999999692350986,
        "source": 30,
        "target": 86,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999905837686,
        "before": 0.9999999692382271,
        "source": 30,
        "target": 128,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.038120037327808935,
        "before": 0.0041033332379580845,
        "source": 30,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03811993664532729,
        "before": 0.004103004319569855,
        "source": 30,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03811998870511694,
        "before": 0.004103174393070417,
        "source": 30,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.11653001277325917,
        "before": 0.004135921900709656,
        "source": 30,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962501358281285,
        "before": 0.987749613842202,
        "source": 30,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164153222577,
        "before": 0.5192092483780935,
        "source": 30,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164693399222,
        "before": 0.5192094248477515,
        "source": 30,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164696095182,
        "before": 0.5192094257284912,
        "source": 30,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164696095174,
        "before": 0.5192094257284889,
        "source": 30,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164696095173,
        "before": 0.5192094257284882,
        "source": 30,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999998168050375,
        "before": 0.9999940152258062,
        "source": 30,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994744252961,
        "before": 0.9999982830063221,
        "source": 30,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996113281997,
        "before": 0.9999987302527703,
        "source": 30,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996113281997,
        "before": 0.9999987302527703,
        "source": 30,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990204531015,
        "before": 0.9999967999300202,
        "source": 30,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995416032005,
        "before": 0.9999985024690089,
        "source": 30,
        "target": 193,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990469850574,
        "before": 0.999996886606948,
        "source": 30,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.5739031833700008,
        "before": 0.5561491493437508,
        "source": 30,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999996502432553,
        "before": 0.9999988573838978,
        "source": 30,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999774052681,
        "before": 0.9999999261855426,
        "source": 30,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087035456094944,
        "before": 0.48489383528250724,
        "source": 30,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087035456094944,
        "before": 0.48489383528250724,
        "source": 30,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087035456094944,
        "before": 0.48489383528250724,
        "source": 30,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087035211669002,
        "before": 0.4848937554312901,
        "source": 30,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962508641016038,
        "before": 0.9877519930300585,
        "source": 30,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993246485414,
        "before": 0.9999977937024432,
        "source": 30,
        "target": 120,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962508909674449,
        "before": 0.9877520807977515,
        "source": 30,
        "target": 136,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962508909674449,
        "before": 0.9877520807977515,
        "source": 30,
        "target": 137,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998468952692,
        "before": 0.9999994998239962,
        "source": 30,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998562858755,
        "before": 0.999999530502055,
        "source": 30,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996425633122,
        "before": 0.9999988322943841,
        "source": 30,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998088408922,
        "before": 0.9999993755046097,
        "source": 30,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997474325866,
        "before": 0.9999991748905555,
        "source": 30,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997333677728,
        "before": 0.9999991289423846,
        "source": 30,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087022312795644,
        "before": 0.48488954151386804,
        "source": 30,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.07841185865313624,
        "before": 3.719125563724565e-05,
        "source": 30,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488312925042869,
        "before": 0.5109166631976436,
        "source": 30,
        "target": 9,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488312925042869,
        "before": 0.5109166631976436,
        "source": 30,
        "target": 10,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488312925042869,
        "before": 0.5109166631976436,
        "source": 30,
        "target": 12,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488309915875527,
        "before": 0.510915719458835,
        "source": 30,
        "target": 22,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488309915875527,
        "before": 0.510915719458835,
        "source": 30,
        "target": 23,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5488309915875527,
        "before": 0.510915719458835,
        "source": 30,
        "target": 24,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 31,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 32,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.6027440503139042,
        "before": 0.0,
        "source": 30,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 63,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 64,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 65,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.49116117203916193,
        "before": 0.48905970400968496,
        "source": 30,
        "target": 66,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.07841185865313624,
        "before": 3.719125563724565e-05,
        "source": 30,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5682758925902657,
        "before": 0.5154832883837406,
        "source": 30,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962504070531727,
        "before": 0.9877504999040366,
        "source": 31,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6154982887318597,
        "before": 1.406433291192553e-09,
        "source": 31,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990568715487,
        "before": 0.9999969189050074,
        "source": 31,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03812002303795619,
        "before": 0.004103286554610025,
        "source": 31,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03811992655939272,
        "before": 0.004102971369951534,
        "source": 31,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087034677769358,
        "before": 0.48489358101225727,
        "source": 31,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986539150375,
        "before": 0.9999956024912268,
        "source": 31,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998964757454,
        "before": 0.9999996617978577,
        "source": 31,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962504865762354,
        "before": 0.9877507596969738,
        "source": 31,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694162014167544,
        "before": 0.5192085495727773,
        "source": 31,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294161807937223,
        "before": 0.5192084821996419,
        "source": 31,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294163989813088,
        "before": 0.5192091949940437,
        "source": 31,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993483467514,
        "before": 0.9999978711218405,
        "source": 31,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993733637498,
        "before": 0.999997952849572,
        "source": 31,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999987512354512,
        "before": 0.9999959204261166,
        "source": 31,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999929444415,
        "before": 0.999999976950281,
        "source": 31,
        "target": 86,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999929450527,
        "before": 0.9999999769522777,
        "source": 31,
        "target": 128,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03811997360738286,
        "before": 0.004103125070464592,
        "source": 31,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.11653000166429381,
        "before": 0.004135885608964321,
        "source": 31,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962502452557643,
        "before": 0.9877499713300285,
        "source": 31,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164587108003,
        "before": 0.5192093901236008,
        "source": 31,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694165009933625,
        "before": 0.5192095282559942,
        "source": 31,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694165011877893,
        "before": 0.5192095288911657,
        "source": 31,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694165011877893,
        "before": 0.5192095288911657,
        "source": 31,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694165011877893,
        "before": 0.5192095288911657,
        "source": 31,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999982654009312,
        "before": 0.9999943332591672,
        "source": 31,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994992284427,
        "before": 0.9999983640354229,
        "source": 31,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996305634693,
        "before": 0.9999987930922414,
        "source": 31,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996305634693,
        "before": 0.9999987930922414,
        "source": 31,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990799818275,
        "before": 0.9999969944036979,
        "source": 31,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995281079632,
        "before": 0.9999984583815813,
        "source": 31,
        "target": 193,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991186185229,
        "before": 0.9999971206254537,
        "source": 31,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.5160944900408283,
        "before": 0.4959317604591962,
        "source": 31,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.9999996889216844,
        "before": 0.9999989837419926,
        "source": 31,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999830767093,
        "before": 0.9999999447135047,
        "source": 31,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962509317767441,
        "before": 0.9877522141171596,
        "source": 31,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962509525664881,
        "before": 0.9877522820349243,
        "source": 31,
        "target": 136,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962509525664881,
        "before": 0.9877522820349243,
        "source": 31,
        "target": 137,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998257317055,
        "before": 0.9999994306850052,
        "source": 31,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998507417032,
        "before": 0.9999995123898651,
        "source": 31,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996450978472,
        "before": 0.9999988405744258,
        "source": 31,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995758991759,
        "before": 0.9999986145101191,
        "source": 31,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998042227364,
        "before": 0.9999993604176121,
        "source": 31,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997463074609,
        "before": 0.999999171214895,
        "source": 31,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997396614468,
        "before": 0.999999149503112,
        "source": 31,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087021124653351,
        "before": 0.4848891533610917,
        "source": 31,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087021124653351,
        "before": 0.4848891533610917,
        "source": 31,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087021124653351,
        "before": 0.4848891533610917,
        "source": 31,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087021124653351,
        "before": 0.4848891533610917,
        "source": 31,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.508702208414426,
        "before": 0.484889466816023,
        "source": 31,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.07841185865313624,
        "before": 3.719125563724565e-05,
        "source": 31,
        "target": 8,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5682758925902657,
        "before": 0.5154832883837406,
        "source": 31,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6154982887796483,
        "before": 1.5625529446154294e-09,
        "source": 32,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962502657680383,
        "before": 0.9877500383413299,
        "source": 32,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999989763250371,
        "before": 0.9999966557685769,
        "source": 32,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03812000448963689,
        "before": 0.0041032259593288285,
        "source": 32,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03811989976969211,
        "before": 0.004102883851000829,
        "source": 32,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087034837971394,
        "before": 0.48489363334846763,
        "source": 32,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999887558015,
        "before": 0.9999996326646315,
        "source": 32,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962503522133406,
        "before": 0.9877503207484485,
        "source": 32,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999998561196573,
        "before": 0.9999952995903916,
        "source": 32,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694161366360158,
        "before": 0.5192083379413611,
        "source": 32,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294161142113318,
        "before": 0.5192082646824309,
        "source": 32,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294163509754215,
        "before": 0.519209038164188,
        "source": 32,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99999930318616,
        "before": 0.9999977235872483,
        "source": 32,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993304137591,
        "before": 0.9999978125367638,
        "source": 32,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986669333031,
        "before": 0.9999956450204426,
        "source": 32,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.038119950836122025,
        "before": 0.004103050679306497,
        "source": 32,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.11652997517537114,
        "before": 0.00413579907262154,
        "source": 32,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.996250223344011,
        "before": 0.9877498997467854,
        "source": 32,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164159022818,
        "before": 0.5192092502729663,
        "source": 32,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164617826591,
        "before": 0.5192094001590193,
        "source": 32,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164620028885,
        "before": 0.5192094008784847,
        "source": 32,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164620028885,
        "before": 0.5192094008784847,
        "source": 32,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999998251162182,
        "before": 0.9999942867427684,
        "source": 32,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694164620028751,
        "before": 0.5192094008784405,
        "source": 32,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994669830884,
        "before": 0.9999982586934628,
        "source": 32,
        "target": 90,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996095079748,
        "before": 0.9999987243063002,
        "source": 32,
        "target": 91,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996095079748,
        "before": 0.9999987243063002,
        "source": 32,
        "target": 92,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990015832658,
        "before": 0.9999967382843807,
        "source": 32,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999043374032,
        "before": 0.9999968748101319,
        "source": 32,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996622824677,
        "before": 0.9999988967146564,
        "source": 32,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996157390643,
        "before": 0.9999987446625713,
        "source": 32,
        "target": 193,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998106769458,
        "before": 0.9999993815027913,
        "source": 32,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998378916666,
        "before": 0.9999994704102352,
        "source": 32,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996146472272,
        "before": 0.9999987410956618,
        "source": 32,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995393645162,
        "before": 0.9999984951554785,
        "source": 32,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997875680733,
        "before": 0.9999993060086937,
        "source": 32,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997247259775,
        "before": 0.9999991007106066,
        "source": 32,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997175145907,
        "before": 0.9999990771518141,
        "source": 32,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087020128726335,
        "before": 0.48488882800289207,
        "source": 32,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087020128726335,
        "before": 0.48488882800289207,
        "source": 32,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.508701030646737,
        "before": 0.4848856191809262,
        "source": 32,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.508701030646737,
        "before": 0.4848856191809262,
        "source": 32,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.508701030646737,
        "before": 0.4848856191809262,
        "source": 32,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5682758925902657,
        "before": 0.5154832883837406,
        "source": 32,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4977633577120538,
        "before": 0.4775428576570342,
        "source": 33,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4977633577092368,
        "before": 0.4775428576538502,
        "source": 33,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4977633577132912,
        "before": 0.47754285765843285,
        "source": 33,
        "target": 34,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9965280353466487,
        "before": 0.9960757054608931,
        "source": 33,
        "target": 1,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.49776335771270996,
        "before": 0.4775428576577759,
        "source": 33,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5224358315248191,
        "before": 0.5018851177354816,
        "source": 33,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5224358315235829,
        "before": 0.5018851177340844,
        "source": 33,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5592998502687921,
        "before": 0.501885138921432,
        "source": 33,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.794846198184636,
        "before": 0.768118623165143,
        "source": 33,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.794846198184758,
        "before": 0.768118623165281,
        "source": 33,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7948461981854236,
        "before": 0.7681186231660332,
        "source": 33,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5775006422956447,
        "before": 0.5224571423516672,
        "source": 33,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5224358315238234,
        "before": 0.5018851177343564,
        "source": 33,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7948461981853208,
        "before": 0.7681186231659171,
        "source": 33,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7948461981853104,
        "before": 0.7681186231659053,
        "source": 33,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.996816708250753,
        "before": 0.9964019868647291,
        "source": 33,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9968167082552647,
        "before": 0.9964019868698286,
        "source": 33,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.9999997128657552,
        "before": 0.9999997009018283,
        "source": 33,
        "target": 231,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.7644536333393099,
        "before": 0.7337664945693517,
        "source": 33,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7644536333393099,
        "before": 0.7337664945693517,
        "source": 33,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7644536333393099,
        "before": 0.7337664945693517,
        "source": 33,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7644536333392794,
        "before": 0.7337664945693172,
        "source": 33,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7644536333392682,
        "before": 0.7337664945693044,
        "source": 33,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7644536333405082,
        "before": 0.7337664945707061,
        "source": 33,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.07840002207014846,
        "before": 2.3947643714018287e-08,
        "source": 33,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7612465532955868,
        "before": 0.7409359302252461,
        "source": 33,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5203088414335431,
        "before": 0.47950178106938274,
        "source": 33,
        "target": 30,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5203088414335431,
        "before": 0.47950178106938274,
        "source": 33,
        "target": 34,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.6154982893624414,
        "before": 3.4664725617207856e-09,
        "source": 34,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962503248343537,
        "before": 0.9877502313043653,
        "source": 34,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990371113071,
        "before": 0.9999968543505108,
        "source": 34,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999986495504575,
        "before": 0.9999955882326336,
        "source": 34,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998698634531,
        "before": 0.9999995748584805,
        "source": 34,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962504286723205,
        "before": 0.9877505705313706,
        "source": 34,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996321257286,
        "before": 0.9999987981959678,
        "source": 34,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998235117423,
        "before": 0.9999994234326334,
        "source": 34,
        "target": 70,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998233058679,
        "before": 0.999999422760065,
        "source": 34,
        "target": 71,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998123380609,
        "before": 0.9999993869294683,
        "source": 34,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.038120074373670806,
        "before": 0.004103454262638634,
        "source": 34,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.038119970262243896,
        "before": 0.004103114142270363,
        "source": 34,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03812002455964521,
        "before": 0.004103291525797578,
        "source": 34,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.11653004866570944,
        "before": 0.004136039157323709,
        "source": 34,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962501749580299,
        "before": 0.987749741675206,
        "source": 34,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999987714227493,
        "before": 0.999995986375758,
        "source": 34,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999982128113508,
        "before": 0.9999941614548988,
        "source": 34,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694163955310539,
        "before": 0.5192091837224471,
        "source": 34,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995256849534,
        "before": 0.9999984504658794,
        "source": 34,
        "target": 193,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991141945075,
        "before": 0.9999971061726911,
        "source": 34,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999756361699,
        "before": 0.9999999204060969,
        "source": 34,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962509211386995,
        "before": 0.9877521793638597,
        "source": 34,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694161515276464,
        "before": 0.5192083865906503,
        "source": 34,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.52941612222395,
        "before": 0.5192082908587565,
        "source": 34,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5294163637197885,
        "before": 0.5192090797986066,
        "source": 34,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993271969193,
        "before": 0.9999978020277083,
        "source": 34,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998351221832,
        "before": 0.9999994613626436,
        "source": 34,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997305416888,
        "before": 0.9999991197098843,
        "source": 34,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999998339160624,
        "before": 0.9999945742238199,
        "source": 34,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087019099150635,
        "before": 0.4848884916520454,
        "source": 34,
        "target": 63,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087019099150635,
        "before": 0.4848884916520454,
        "source": 34,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694131030011182,
        "before": 0.5191984273960045,
        "source": 34,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694131030011182,
        "before": 0.5191984273960045,
        "source": 34,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694131030011182,
        "before": 0.5191984273960045,
        "source": 34,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5694131030011182,
        "before": 0.5191984273960045,
        "source": 34,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087006301947735,
        "before": 0.484884310949224,
        "source": 34,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087006301947735,
        "before": 0.484884310949224,
        "source": 34,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087004040716526,
        "before": 0.4848835722303201,
        "source": 34,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5087004040716526,
        "before": 0.4848835722303201,
        "source": 34,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5682758925902657,
        "before": 0.5154832883837406,
        "source": 34,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.5726670846295452,
        "before": 0.5548615464891096,
        "source": 36,
        "target": 245,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5074074188322981,
        "before": 0.5064510928565839,
        "source": 39,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074073034190045,
        "before": 0.5064507308959753,
        "source": 39,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6027440509547783,
        "before": 2.0099172704736284e-09,
        "source": 39,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993937327971,
        "before": 0.9999980986172489,
        "source": 39,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081468814046,
        "before": 0.5064533761732576,
        "source": 39,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081468814046,
        "before": 0.5064533761732576,
        "source": 39,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081468814046,
        "before": 0.5064533761732576,
        "source": 39,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081468814046,
        "before": 0.5064533761732576,
        "source": 39,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081468812857,
        "before": 0.5064533761728839,
        "source": 39,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5310011402692401,
        "before": 0.49357575030424505,
        "source": 39,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962515099583988,
        "before": 0.9882439388529786,
        "source": 39,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992518527586,
        "before": 0.9999976536513051,
        "source": 39,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9962515693343019,
        "before": 0.9882441250684255,
        "source": 39,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993554033666,
        "before": 0.9999979784080111,
        "source": 39,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992579378357,
        "before": 0.9999976727354002,
        "source": 39,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992217509861,
        "before": 0.9999975592457504,
        "source": 39,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997610921323,
        "before": 0.9999992507341701,
        "source": 39,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999689990029,
        "before": 0.9999990277428679,
        "source": 39,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999995457536938,
        "before": 0.9999985753870776,
        "source": 39,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999341564231,
        "before": 0.9999997935005542,
        "source": 39,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998921492506,
        "before": 0.9999996617571365,
        "source": 39,
        "target": 76,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999397469199,
        "before": 0.9999981103353982,
        "source": 39,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999256296095,
        "before": 0.999997667586553,
        "source": 39,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994379637912,
        "before": 0.9999982373350431,
        "source": 39,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994379637912,
        "before": 0.9999982373350431,
        "source": 39,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994379637912,
        "before": 0.9999982373350431,
        "source": 39,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992385022077,
        "before": 0.9999976117811413,
        "source": 39,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991689987376,
        "before": 0.9999973938034924,
        "source": 39,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8480284387943212,
        "before": 0.5233848973014608,
        "source": 39,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.83929613745067,
        "before": 0.516158603283907,
        "source": 39,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5271414172989288,
        "before": 0.5022120054986183,
        "source": 39,
        "target": 44,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5271411911758078,
        "before": 0.5022113246952764,
        "source": 39,
        "target": 45,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5271411911758078,
        "before": 0.5022113246952764,
        "source": 39,
        "target": 46,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5271411911758078,
        "before": 0.5022113246952764,
        "source": 39,
        "target": 47,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.5271411911758078,
        "before": 0.5022113246952764,
        "source": 39,
        "target": 49,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.04000966922199759,
        "before": 2.9111745058629297e-05,
        "source": 39,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5074073609417827,
        "before": 0.506450911299629,
        "source": 40,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6027440514783564,
        "before": 3.6519690733755867e-09,
        "source": 40,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074072911065662,
        "before": 0.5064506922815533,
        "source": 40,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993193681787,
        "before": 0.9999978653940064,
        "source": 40,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996234165939,
        "before": 0.9999988189544322,
        "source": 40,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992107834134,
        "before": 0.9999975248491134,
        "source": 40,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999970853478,
        "before": 0.9999999085903145,
        "source": 40,
        "target": 86,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999708534891,
        "before": 0.9999999085903499,
        "source": 40,
        "target": 128,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993016403107,
        "before": 0.9999978097956462,
        "source": 40,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994718707472,
        "before": 0.9999983436744612,
        "source": 40,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074082049826243,
        "before": 0.5064535583910266,
        "source": 40,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074082049826243,
        "before": 0.5064535583910266,
        "source": 40,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074082049826243,
        "before": 0.5064535583910266,
        "source": 40,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074082049826243,
        "before": 0.5064535583910266,
        "source": 40,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074082049826243,
        "before": 0.5064535583910266,
        "source": 40,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5310012013096268,
        "before": 0.4935759417398653,
        "source": 40,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996796221376,
        "before": 0.9999989952269587,
        "source": 40,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996223617355,
        "before": 0.9999988156461714,
        "source": 40,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999996796736185,
        "before": 0.9999989953884137,
        "source": 40,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999082993285,
        "before": 0.9999997124072123,
        "source": 40,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999998742611145,
        "before": 0.9999996056561413,
        "source": 40,
        "target": 76,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993234010894,
        "before": 0.9999978780420715,
        "source": 40,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991904185096,
        "before": 0.9999974609804488,
        "source": 40,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993783712395,
        "before": 0.9999980504401411,
        "source": 40,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992113337681,
        "before": 0.9999975265751423,
        "source": 40,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993783712395,
        "before": 0.9999980504401411,
        "source": 40,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993783712395,
        "before": 0.9999980504401411,
        "source": 40,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991677039695,
        "before": 0.9999973897428254,
        "source": 40,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999991677039695,
        "before": 0.9999973897428254,
        "source": 40,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999990324870656,
        "before": 0.9999969656738873,
        "source": 40,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8480284387943212,
        "before": 0.5233848973014608,
        "source": 40,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.8392959113275489,
        "before": 0.5161579224805648,
        "source": 40,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.04000966922199759,
        "before": 2.9111745058629297e-05,
        "source": 40,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.6027440509178205,
        "before": 1.8940093707256802e-09,
        "source": 41,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074074410205422,
        "before": 0.5064511624436314,
        "source": 41,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074074063241858,
        "before": 0.5064510536284862,
        "source": 41,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994452368779,
        "before": 0.9999982601449883,
        "source": 41,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997160324685,
        "before": 0.9999991094174913,
        "source": 41,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992746970177,
        "before": 0.9999977252957546,
        "source": 41,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999816690994,
        "before": 0.9999999425104009,
        "source": 41,
        "target": 86,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999981669104,
        "before": 0.9999999425104152,
        "source": 41,
        "target": 128,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999411428761,
        "before": 0.999998154115551,
        "source": 41,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994496114014,
        "before": 0.9999982738644225,
        "source": 41,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081855354811,
        "before": 0.506453497400654,
        "source": 41,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081855354811,
        "before": 0.506453497400654,
        "source": 41,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5310010801674419,
        "before": 0.493575561812236,
        "source": 41,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081855226276,
        "before": 0.5064534973603423,
        "source": 41,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081855226276,
        "before": 0.5064534973603423,
        "source": 41,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5074081855226276,
        "before": 0.5064534973603423,
        "source": 41,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997885284919,
        "before": 0.9999993367804233,
        "source": 41,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999997259373095,
        "before": 0.9999991404811776,
        "source": 41,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999589438218,
        "before": 0.9999987123910262,
        "source": 41,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999999415667815,
        "before": 0.9999998167410125,
        "source": 41,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992920097149,
        "before": 0.9999977795920518,
        "source": 41,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994485083863,
        "before": 0.9999982704051338,
        "source": 41,
        "target": 111,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993186063165,
        "before": 0.9999978630046449,
        "source": 41,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994843354099,
        "before": 0.9999983827662917,
        "source": 41,
        "target": 124,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994843354099,
        "before": 0.9999983827662917,
        "source": 41,
        "target": 125,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999263687486,
        "before": 0.9999976907675245,
        "source": 41,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999993078645665,
        "before": 0.9999978293162344,
        "source": 41,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999999482350193,
        "before": 0.999998376540229,
        "source": 41,
        "target": 126,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999992463723442,
        "before": 0.9999976364635615,
        "source": 41,
        "target": 114,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8480284387943212,
        "before": 0.5233848973014608,
        "source": 41,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.8392956659682597,
        "before": 0.5161571837616606,
        "source": 41,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.04000966922199759,
        "before": 2.9111745058629297e-05,
        "source": 41,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.39532758113560545,
        "before": 1.5823144099629299e-06,
        "source": 44,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.987089269076559,
        "before": 0.9771359286140273,
        "source": 44,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994001669638264,
        "before": 0.9989377343978382,
        "source": 44,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999994013089072,
        "before": 0.9999989397567057,
        "source": 44,
        "target": 231,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999642352780516,
        "before": 0.9993666298518833,
        "source": 44,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994050434369138,
        "before": 0.9989463703170164,
        "source": 44,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994576290300362,
        "before": 0.9990394960092914,
        "source": 44,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9905035855051468,
        "before": 0.9831824626964468,
        "source": 44,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9906122754595817,
        "before": 0.983374945592409,
        "source": 44,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9905035855051468,
        "before": 0.9831824626964468,
        "source": 44,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993838183347874,
        "before": 0.9989087820307241,
        "source": 44,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04916092655709298,
        "before": 0.016223409813516786,
        "source": 44,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48420148323091006,
        "before": 0.08655410928166393,
        "source": 44,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3953276597429348,
        "before": 1.7215229182288377e-06,
        "source": 45,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9870609748397201,
        "before": 0.977085821346303,
        "source": 45,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993746880106871,
        "before": 0.9988926128158865,
        "source": 45,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996274508130376,
        "before": 0.999340239429045,
        "source": 45,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9904657255948843,
        "before": 0.9831154152383249,
        "source": 45,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9905789442974205,
        "before": 0.9833159182549525,
        "source": 45,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9904657255948843,
        "before": 0.9831154152383249,
        "source": 45,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04916092655709298,
        "before": 0.016223409813516786,
        "source": 45,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48420148323091006,
        "before": 0.08655410928166393,
        "source": 45,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.395327881558742,
        "before": 2.1143443996492665e-06,
        "source": 46,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9871282760298554,
        "before": 0.9772050074113475,
        "source": 46,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994479655667932,
        "before": 0.9990223826394339,
        "source": 46,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995957582606745,
        "before": 0.9992841139638076,
        "source": 46,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04916092655709298,
        "before": 0.016223409813516786,
        "source": 46,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48420148323091006,
        "before": 0.08655410928166393,
        "source": 46,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.395327881558742,
        "before": 2.1143443996492665e-06,
        "source": 47,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9871282760298554,
        "before": 0.9772050074113475,
        "source": 47,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9994479655667932,
        "before": 0.9990223826394339,
        "source": 47,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995957582606745,
        "before": 0.9992841139638076,
        "source": 47,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04916092655709298,
        "before": 0.016223409813516786,
        "source": 47,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48420148323091006,
        "before": 0.08655410928166393,
        "source": 47,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.39532789801768375,
        "before": 2.1434921233650003e-06,
        "source": 49,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9871235297859315,
        "before": 0.977196602119615,
        "source": 49,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9995957582606745,
        "before": 0.9992841139638076,
        "source": 49,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.04916092655709298,
        "before": 0.016223409813516786,
        "source": 49,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48420148323091006,
        "before": 0.08655410928166393,
        "source": 49,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3503472688476452,
        "before": 0.33674833859336506,
        "source": 52,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3503472688476452,
        "before": 0.33674833859336506,
        "source": 52,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999977341245391,
        "before": 0.9999975413677724,
        "source": 52,
        "target": 227,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.35034726884024964,
        "before": 0.33674833858534037,
        "source": 52,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.38666990763629777,
        "before": 0.3761609240845245,
        "source": 52,
        "target": 34,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4432914662632511,
        "before": 0.3959325805807846,
        "source": 52,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6636256919089,
        "before": 0.6350105163942057,
        "source": 52,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9487256316575424,
        "before": 0.9443637496284097,
        "source": 52,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.48260454054830754,
        "before": 0.438589996254674,
        "source": 52,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6470475339250873,
        "before": 0.6170220637207978,
        "source": 52,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8816292452503869,
        "before": 0.8715595109053677,
        "source": 52,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.941807191688631,
        "before": 0.9368567618149208,
        "source": 52,
        "target": 70,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9417177719041311,
        "before": 0.9367597351390311,
        "source": 52,
        "target": 71,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.932381971627981,
        "before": 0.9266297435199446,
        "source": 52,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4654472167500571,
        "before": 0.41997310845275293,
        "source": 52,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4826044280261066,
        "before": 0.4385898741602719,
        "source": 52,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6935423641983868,
        "before": 0.6674721833749857,
        "source": 52,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.497486858600005,
        "before": 0.4547383448350749,
        "source": 52,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999946387354788,
        "before": 0.9999941826556845,
        "source": 52,
        "target": 231,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6885970046837653,
        "before": 0.6621061248738773,
        "source": 52,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8564400320388277,
        "before": 0.8442274653199086,
        "source": 52,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.856477223527284,
        "before": 0.8442678206676258,
        "source": 52,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6852502223528963,
        "before": 0.6584746336294448,
        "source": 52,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9014714342069001,
        "before": 0.8930896638529733,
        "source": 52,
        "target": 193,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8748755645523081,
        "before": 0.8642312983423482,
        "source": 52,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8774857205547616,
        "before": 0.8670634988658438,
        "source": 52,
        "target": 57,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8416125368101116,
        "before": 0.8281386033095829,
        "source": 52,
        "target": 55,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8406771022072099,
        "before": 0.8271235918046983,
        "source": 52,
        "target": 56,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8630134724439182,
        "before": 0.8513601046483488,
        "source": 52,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9088481822080392,
        "before": 0.9010939477083758,
        "source": 52,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7568530907052222,
        "before": 0.7361687182131317,
        "source": 52,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7568530907052222,
        "before": 0.7361687182131317,
        "source": 52,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5579975661205923,
        "before": 0.5203966646273788,
        "source": 52,
        "target": 46,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5579975661205923,
        "before": 0.5203966646273788,
        "source": 52,
        "target": 47,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5579975661205923,
        "before": 0.5203966646273788,
        "source": 52,
        "target": 49,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5686469328333196,
        "before": 0.5319519670500429,
        "source": 53,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999974701230111,
        "before": 0.9999972549077811,
        "source": 53,
        "target": 227,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4324969200894462,
        "before": 0.4258864150276109,
        "source": 53,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4324969200894462,
        "before": 0.4258864150276109,
        "source": 53,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4324969200894462,
        "before": 0.4258864150276109,
        "source": 53,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4716544082679341,
        "before": 0.4683750089712827,
        "source": 53,
        "target": 34,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4324969200894462,
        "before": 0.4258864150276109,
        "source": 53,
        "target": 52,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5386470971827032,
        "before": 0.49940006204720394,
        "source": 53,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5490453363954878,
        "before": 0.5106828736930207,
        "source": 53,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8983723323683734,
        "before": 0.8897269231427662,
        "source": 53,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.592174271710489,
        "before": 0.5574807635747493,
        "source": 53,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5980485228176525,
        "before": 0.5638547339601265,
        "source": 53,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8724146109289256,
        "before": 0.8615609927614211,
        "source": 53,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9999815320273988,
        "before": 0.9999799609672296,
        "source": 53,
        "target": 231,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5627653182344621,
        "before": 0.5255700067648242,
        "source": 53,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5920669714445835,
        "before": 0.5573643353348346,
        "source": 53,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6878883693982064,
        "before": 0.6613372063782621,
        "source": 53,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7768170216071291,
        "before": 0.7578309696257911,
        "source": 53,
        "target": 72,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7977643502585837,
        "before": 0.7805602758882202,
        "source": 53,
        "target": 44,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7977643502585837,
        "before": 0.7805602758882202,
        "source": 53,
        "target": 45,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7977643502585837,
        "before": 0.7805602758882202,
        "source": 53,
        "target": 57,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.799354680807481,
        "before": 0.7822858949733951,
        "source": 53,
        "target": 69,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7212258123196926,
        "before": 0.6975106470482776,
        "source": 53,
        "target": 55,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.719194110342616,
        "before": 0.6953061093127344,
        "source": 53,
        "target": 56,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7519256613756253,
        "before": 0.7308221152079267,
        "source": 53,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.836985998355181,
        "before": 0.8231184877985904,
        "source": 53,
        "target": 112,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5506509888032095,
        "before": 0.5124251180590381,
        "source": 53,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5506509888032095,
        "before": 0.5124251180590381,
        "source": 53,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.2530646109889174,
        "before": 0.18952323240984964,
        "source": 53,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.2530646109889174,
        "before": 0.18952323240984964,
        "source": 53,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.20956692228367974,
        "before": 0.14232521949184,
        "source": 53,
        "target": 35,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0687144079983131,
        "before": 0.032893237845391825,
        "source": 54,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4853770985103676,
        "before": 0.4850011919600343,
        "source": 55,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4853770985103676,
        "before": 0.4850011919600343,
        "source": 55,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4853770985103676,
        "before": 0.4850011919600343,
        "source": 55,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4853770985103676,
        "before": 0.4850011919600343,
        "source": 55,
        "target": 56,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7686592988161246,
        "before": 0.7489792738890241,
        "source": 55,
        "target": 129,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7474545418517589,
        "before": 0.7259706400301202,
        "source": 55,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7358143225359897,
        "before": 0.7133401937239472,
        "source": 55,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7819540395349144,
        "before": 0.7634049908147943,
        "source": 55,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9210903681766842,
        "before": 0.9143775696361591,
        "source": 55,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6704804916143886,
        "before": 0.6424484501024182,
        "source": 55,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6378752493836904,
        "before": 0.607069498029178,
        "source": 55,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6378752493836904,
        "before": 0.607069498029178,
        "source": 55,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6888972596926973,
        "before": 0.6624319224096108,
        "source": 55,
        "target": 110,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6888972596926973,
        "before": 0.6624319224096108,
        "source": 55,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5517161648317036,
        "before": 0.5135809080205118,
        "source": 55,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6925436542344374,
        "before": 0.666388513709242,
        "source": 56,
        "target": 127,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4148979382723623,
        "before": 0.4085264087156709,
        "source": 56,
        "target": 73,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4112965473044602,
        "before": 0.40461864941890213,
        "source": 56,
        "target": 39,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4112965473044602,
        "before": 0.40461864941890213,
        "source": 56,
        "target": 40,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4112965473044602,
        "before": 0.40461864941890213,
        "source": 56,
        "target": 41,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8318131866733041,
        "before": 0.8175056279007206,
        "source": 56,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8122168392276139,
        "before": 0.7962422300646852,
        "source": 56,
        "target": 77,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8441886567910033,
        "before": 0.8309338723860713,
        "source": 56,
        "target": 74,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9497258293220492,
        "before": 0.9454490335525708,
        "source": 56,
        "target": 100,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6457278120741211,
        "before": 0.6155900738651487,
        "source": 56,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6241354371837895,
        "before": 0.5921608476386605,
        "source": 56,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6241354371837895,
        "before": 0.5921608476386605,
        "source": 56,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5311008801431893,
        "before": 0.5115634168158223,
        "source": 57,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6679406111047188,
        "before": 0.654104803234082,
        "source": 57,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6114420130092185,
        "before": 0.5952520968846027,
        "source": 58,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.560463528044211,
        "before": 0.5421495083793865,
        "source": 58,
        "target": 75,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6242098003928499,
        "before": 0.6085518754092186,
        "source": 59,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039136863695879306,
        "before": 0.0013593104775448859,
        "source": 63,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039124422926031195,
        "before": 0.001336360685204953,
        "source": 63,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039124422926031195,
        "before": 0.001336360685204953,
        "source": 63,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990216434110837,
        "before": 0.998195201677697,
        "source": 63,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.07914084024294615,
        "before": 0.001366646111153444,
        "source": 63,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.998835595713935,
        "before": 0.9978519949415369,
        "source": 63,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9987349254857171,
        "before": 0.9976662861099599,
        "source": 63,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992849558234104,
        "before": 0.9986809405232189,
        "source": 63,
        "target": 143,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4179528610239613,
        "before": 7.238861983665584e-05,
        "source": 63,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992828285764906,
        "before": 0.9986770163388106,
        "source": 63,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990967466353566,
        "before": 0.998333746431934,
        "source": 63,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981716236066833,
        "before": 0.9966271493598755,
        "source": 63,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.998223178628714,
        "before": 0.9967222541696366,
        "source": 63,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 64,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 65,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 66,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 67,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 101,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 122,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 136,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981388992330497,
        "before": 0.9965667819076586,
        "source": 63,
        "target": 137,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 63,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 63,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 63,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03913687187137596,
        "before": 0.0013593255590834668,
        "source": 64,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03912442631493766,
        "before": 0.0013363669368035888,
        "source": 64,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990215524533296,
        "before": 0.9981950338857037,
        "source": 64,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039124420576998435,
        "before": 0.0013363563518867818,
        "source": 64,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.998835595713935,
        "before": 0.9978519949415369,
        "source": 64,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4179528610239613,
        "before": 7.238861983665584e-05,
        "source": 64,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992828285764906,
        "before": 0.9986770163388106,
        "source": 64,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990967466353566,
        "before": 0.998333746431934,
        "source": 64,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.07867518983090202,
        "before": 0.000507649409993721,
        "source": 64,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9981716236066833,
        "before": 0.9966271493598755,
        "source": 64,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.998223178628714,
        "before": 0.9967222541696366,
        "source": 64,
        "target": 29,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.998255766255652,
        "before": 0.9967823693618805,
        "source": 64,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 64,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 64,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 64,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990183022439441,
        "before": 0.9981890381449761,
        "source": 65,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03913395890723593,
        "before": 0.0013539519429066893,
        "source": 65,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039120968780867155,
        "before": 0.0013299887391602454,
        "source": 65,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039120968780867155,
        "before": 0.0013299887391602454,
        "source": 65,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41794707163549916,
        "before": 6.170879337868114e-05,
        "source": 65,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9988185169820408,
        "before": 0.9978204893872036,
        "source": 65,
        "target": 61,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9992782876888161,
        "before": 0.9986686396522836,
        "source": 65,
        "target": 68,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990916141577878,
        "before": 0.998324278425063,
        "source": 65,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.07848077694300999,
        "before": 0.0001490112019245361,
        "source": 65,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9979772107187915,
        "before": 0.9962685111518065,
        "source": 65,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.99806135336776,
        "before": 0.996423731153811,
        "source": 65,
        "target": 135,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 65,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 65,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 65,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.999027401232378,
        "before": 0.9982058232714284,
        "source": 66,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039153396041704376,
        "before": 0.0013898081001365266,
        "source": 66,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03914236458364674,
        "before": 0.0013694580997169164,
        "source": 66,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.03914236458364674,
        "before": 0.0013694580997169164,
        "source": 66,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41794203205249214,
        "before": 5.24121513779336e-05,
        "source": 66,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991202682549245,
        "before": 0.9983771373387001,
        "source": 66,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.07848077694300999,
        "before": 0.0001490112019245361,
        "source": 66,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 66,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 66,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 66,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990118255759308,
        "before": 0.998177090477125,
        "source": 67,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.039165175363567,
        "before": 0.0014115377032039359,
        "source": 67,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4179398045584815,
        "before": 4.83030387099036e-05,
        "source": 67,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9991192208297967,
        "before": 0.9983752051279555,
        "source": 67,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 67,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 67,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 67,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 67,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 67,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.05023398972942792,
        "before": 0.010660405968154082,
        "source": 79,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3200246318845236,
        "before": 0.2916923248797121,
        "source": 79,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3023445345293473,
        "before": 0.2732755568014034,
        "source": 79,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3023445345293473,
        "before": 0.2732755568014034,
        "source": 79,
        "target": 32,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.33941621262252547,
        "before": 0.311891888148464,
        "source": 79,
        "target": 52,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.4278498224075561,
        "before": 0.4040102316745376,
        "source": 79,
        "target": 53,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.07086486372045085,
        "before": 0.032150899708802964,
        "source": 80,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.6110121693485168,
        "before": 0.5224571423512984,
        "source": 84,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744490771,
        "before": 0.5018851177359303,
        "source": 84,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489418,
        "before": 0.5018851177344855,
        "source": 84,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5179859744489682,
        "before": 0.5018851177347686,
        "source": 84,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.5902394164341594,
        "before": 0.5018851389218353,
        "source": 84,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9996628724373469,
        "before": 0.9964019868651621,
        "source": 84,
        "target": 28,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196126191,
        "before": 2.5261443451322326e-11,
        "source": 84,
        "target": 3,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.004236213196082404,
        "before": 2.4794060557589982e-11,
        "source": 84,
        "target": 14,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.7556483020951554,
        "before": 4.148947579032504e-16,
        "source": 84,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": 3,
        "after": 0.28053997781574425,
        "before": 0.26273869120631976,
        "source": 84,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.7838482142800349,
        "before": 0.765460301953163,
        "source": 84,
        "target": 54,
        "type": "SELF_ACTION"
      },
      {
        "action": 3,
        "after": 0.99798057642475,
        "before": 0.9978087851831056,
        "source": 84,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.535748169348513,
        "before": 0.5224571423512594,
        "source": 84,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531630758,
        "before": 0.7681186231648013,
        "source": 84,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531630889,
        "before": 0.768118623164941,
        "source": 84,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8096643531631622,
        "before": 0.7681186231657244,
        "source": 84,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": 15,
        "after": 0.04,
        "before": 0.0,
        "source": 84,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 15,
        "after": 0.3074660041755197,
        "before": 0.2786104210161664,
        "source": 84,
        "target": 119,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7788306701560187,
        "before": 0.0,
        "source": 84,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.5357481693458331,
        "before": 0.5224571423226564,
        "source": 84,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.1152640025361831,
        "before": 2.3947643714018287e-08,
        "source": 84,
        "target": 480,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585496700566,
        "before": 0.0,
        "source": 84,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.004596585496700566,
        "before": 0.0,
        "source": 84,
        "target": 14,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.7896115144052637,
        "before": 0.7409359300961353,
        "source": 84,
        "target": 2,
        "type": "SELF_ACTION"
      },
      {
        "action": null,
        "after": 0.45323714831713235,
        "before": 0.4171263821496111,
        "source": 89,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.45323714831713235,
        "before": 0.4171263821496111,
        "source": 89,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.915463145148458,
        "before": 0.30775363201753947,
        "source": 89,
        "target": 80,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.8967584158959223,
        "before": 0.4496646769696981,
        "source": 89,
        "target": 190,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.34831078818644373,
        "before": 0.32115707102754554,
        "source": 94,
        "target": 30,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3306306908312674,
        "before": 0.3027403029492369,
        "source": 94,
        "target": 31,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.05219122780687322,
        "before": 0.012699195632159608,
        "source": 95,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9997377129977469,
        "before": 0.999726784372653,
        "source": 95,
        "target": 231,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993589702162722,
        "before": 0.9988647776161861,
        "source": 111,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993145692003479,
        "before": 0.9987861462820098,
        "source": 111,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9993145692003479,
        "before": 0.9987861462820098,
        "source": 111,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3953266876448864,
        "before": 0.0,
        "source": 111,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9958844927762127,
        "before": 0.9927117022644074,
        "source": 111,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.3953266876448864,
        "before": 0.0,
        "source": 112,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9958844927762127,
        "before": 0.9927117022644074,
        "source": 112,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9990095886630296,
        "before": 0.998172963989199,
        "source": 122,
        "target": 95,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.41793655811331576,
        "before": 4.231424193078904e-05,
        "source": 122,
        "target": 33,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 122,
        "target": 4,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 122,
        "target": 5,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 122,
        "target": 6,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 8,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 9,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 10,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 12,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 22,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 23,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0784,
        "before": 0.0,
        "source": 122,
        "target": 24,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 122,
        "target": 25,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.0384,
        "before": 0.0,
        "source": 122,
        "target": 26,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9958844927762127,
        "before": 0.9927117022644074,
        "source": 124,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9958844927762127,
        "before": 0.9927117022644074,
        "source": 125,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": null,
        "after": 0.9957893879664516,
        "before": 0.9925432777830655,
        "source": 126,
        "target": 2,
        "type": "SEQUENTIAL"
      },
      {
        "action": 16,
        "after": 0.8802972526900893,
        "before": 0.0,
        "source": 480,
        "target": 33,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.005195431740881537,
        "before": 0.0,
        "source": 480,
        "target": 3,
        "type": "SELF_ACTION"
      },
      {
        "action": 16,
        "after": 0.005195431740881537,
        "before": 0.0,
        "source": 480,
        "target": 14,
        "type": "SELF_ACTION"
      }
    ],
    "final_reserves": {
      "energy": 44.3999999999998,
      "hydration": 79.27999999999997,
      "nutrients": 0.0
    },
    "group": "EXPERIENCED_FULL",
    "initial_reserves": {
      "energy": 45.0,
      "hydration": 80.0,
      "nutrients": 12.0
    },
    "interpretation": "Perceptual/action contradictions are not proof of a contradicted nutritive hypothesis without a supported resource-to-internal consequence.",
    "relations_with_contradiction": 4952
  }
]
```

Diagnostics above are observational and do not introduce new acceptance gates. Temporal diagnostics can reflect the last planner candidate rather than uniquely identify the selected plan; plan/physical/ablation evidence must be assessed together.
The predeclared Stage 2 gate is conservative: it requires an explicit MOVE_UP/INTERACT_UP chain and a net E decline during MOVE. Generic orientation-relative INTERACT and digestion masking a movement cost can fail this narrow gate without demonstrating absence of an incurred movement cost.

## Interruption recovery and reproducibility

All 112 fixed-budget training episodes were already complete when the process stopped. Recovery preserved 468 completed primary trials and ran only the remaining 44 primary trials plus two counterfactual controls. No completed failures were replaced, no training episode was repeated, and no budget or scientific threshold changed. The recovered output contains 512 primary trials and two controls.

The reverse-order audit compared all 64 declared trials (eight variants, two seeds, four groups). Exact full-record equality failed for 46 trials. The measured success, censored time/actions, energy expenditure, brownout, J and consumption counts matched for all 64 trials. Differences included final causal digests and, in some trials, last-bit planner confidence values. Exact equality was not relaxed or replaced by rounded comparison. Root cause remains unresolved; these results establish metric repeatability on this subset, not complete causal-state determinism.

The independent-process hashseed check with PYTHONHASHSEED=1 and 777 passed exact equality for the declared fresh/experienced Stage 2 pair. This narrower check does not negate the reverse-order mismatch.

```json
{
  "group_order_reversed": true,
  "hashseed": {
    "groups": [
      "FRESH_FULL",
      "EXPERIENCED_FULL"
    ],
    "identical": true,
    "seeds": [
      1,
      777
    ]
  },
  "identical": false,
  "independent_trials_compared": 64,
  "mismatches": [
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_1__stage1_adjacent_north__92102__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_2__stage2_one_move_north__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_2__stage2_one_move_north__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_2__stage2_one_move_north__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_2__stage2_one_move_north__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_2__stage2_one_move_north__92102__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_east_a__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_east_a__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_east_a__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_east_a__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_east_a__92102__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_south_a__92102__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_west_a__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_west_a__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_west_a__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_west_a__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92101__FRESH_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_3__stage3_north_translated__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92101__FRESH_FULL"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_a__92102__FRESH_FULL"
    },
    {
      "differing_fields": [
        "decisions",
        "final_digest",
        "trajectory"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92101__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92101__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92101__EXPERIENCED_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92101__FRESH_FULL"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92102__EXPERIENCED_NO_MOTIVATION"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92102__EXPERIENCED_NO_DELAYED"
    },
    {
      "differing_fields": [
        "final_digest"
      ],
      "metrics_identical": true,
      "trial_id": "stage_4__stage4_scarcity_b__92102__EXPERIENCED_FULL"
    }
  ],
  "protocol_checksum": "87fd4007f3dc4e81a5a12d8e2fedf5747750f2ed37e466a9c9d6b1729bb8c0e9",
  "workers": 3
}
```

## Measurement software provenance

Base and current HEAD: `aea4e1171a2f35e8320e5bc75decf1e5fe7b9a65`; project version 0.9.2. The experiment changes remain in the working tree. The original measurement producer is archived locally in `results/v092/full/measurement-source/`, verified byte-for-byte against the initial manifest below. Later changes added stricter invalid-input checks, recovery and audit reporting. Metric definitions, recorder and acceptance logic remain byte-identical. Runtime, cognitive and physical production policies remain frozen.

`measurement-source-checksums.json`:

```json
{
  "experiments/protocols/v092_survival.securriculum": "ea443bbcf3b356ea27d0f069ae716402da7c867cfeb5d7cb1da4e4bb68a48314",
  "experiments/v092/__init__.py": "66df19cde4d0926c514b418987042aa5580f2e32056421b96c12c942a0ef8e62",
  "experiments/v092/determinism.py": "8011095a1293eae4cfbc5858b78a3b17f4612113ad50057f813c1e0a976082e1",
  "experiments/v092/generate.py": "7fcda92ef8a8774e8b520875913b1f7d9e135afdd8bccaaaee90ee8dd180ef65",
  "experiments/v092/metrics.py": "29987a1ca427165234316634a47dbeccd07a947c605c3e11ce2aca5d2cfa9d4d",
  "experiments/v092/protocol.py": "799d8fcf3595af0a2520a3dccc3d5a9afe34a8421779cd1f768ecc4c4f22c3da",
  "experiments/v092/recorder.py": "7dbac2a5ff3b31cfffef831a6a09f212660d1d9e07174537e406c86028a6c50b",
  "experiments/v092/report.py": "c5193b16463c42b7755137d69e2cec47aa43a9299d1ac8468bfe05a108a57517",
  "experiments/v092/runner.py": "e6efd314409a01b7ba2f6a5782e08aa582b2af78b9648e02d481f036bcdc7d0e",
  "scenarios/v092/counterfactual_same_appearance.sescenario": "1842c74dae7e1ae4018d2e19deb0e93ac925b4847c7e032241fff01daa03be0f",
  "scenarios/v092/stage1_adjacent_north.sescenario": "ff8add2542d1b62bc66d94af3bbb8f566031c81fb23d9c43637496fdbbb849fb",
  "scenarios/v092/stage2_one_move_north.sescenario": "649f121d20e88446c8f029429faf8653f59407c25638c0cfc832db563c70d5e8",
  "scenarios/v092/stage3_east_a.sescenario": "fe4112de9dc24eb28e6856f8b147cd136bfe4d89db304cbb128a22c432fedbca",
  "scenarios/v092/stage3_north_translated.sescenario": "d711d29940c473c0ce464c6cded140b233751dfe85bb8313b72e0a5f77b72aa6",
  "scenarios/v092/stage3_south_a.sescenario": "fab9a88b2cd4aebc9fa6ad8ee48a1ba3eeb82370ff072e747840d1d207e73896",
  "scenarios/v092/stage3_west_a.sescenario": "73bf6a7f466300fd610007993ddde838c6c2541ce9f150874998346747c0b25b",
  "scenarios/v092/stage4_scarcity_a.sescenario": "8a4ee4329abb98067d8076015bb2746f077a661ff2743ef750b0d21a4966525c",
  "scenarios/v092/stage4_scarcity_b.sescenario": "8eccb8cb63ccf2debd752a6abdafe4256b2123cad782a5dadf06d3c11e535e82",
  "scenarios/v092/train_adjacent_north.sescenario": "9368d78d8fb9cc9e1d0f098c34b03c95f6eb5bc8efb16b34e8858d94ac917010",
  "scenarios/v092/train_consolidate_east.sescenario": "625e4a6f32d48d6743d26ef3a4945683217efa453f10243797777fc51a39edc1",
  "scenarios/v092/train_consolidate_north.sescenario": "84bb95f7f975347b93f35e5f35e970480cf70d0ae62d30c9ad95784536f89b82",
  "scenarios/v092/train_consolidate_south.sescenario": "77d38ec3e1263a9dd2e1e89b954793935cd61a532e5209fa74368093b94e326f",
  "scenarios/v092/train_consolidate_west.sescenario": "8284a881a99de1d4ce7a78c529b9d3463f2b3e8d56263ca5cdc7eaf75309a5b8",
  "scenarios/v092/train_one_move_north.sescenario": "4ab5f20867fc19be90ddaa328b0d6f54911b6ee7e37fad6ebee0ca918446740e"
}

```

`measurement-binary-checksums.json`:

```json
{
  "consciousness/SDL3.dll": "700f63f82dbb78bc55f18b46ce37f4e923e2ea4d0a25f9c1047f89633b727060",
  "consciousness/_native_brain.cp312-win_amd64.pyd": "0c60f7c3cac4ec9f7ab7a18623f596cbab6e2e897cb6c93e0009ddd7cbc11427"
}

```

Recovery/audit modules in the final working tree:

```json
{
  "experiments/v092/resume.py": "02785d953a2c4d0b8174db402ebacd4bdbe5d6276d0a242938147e8b571f10bb",
  "experiments/v092/runner.py": "27696a4ef4372dc31aea165dae6323874e20c7c51fdee480ec4ca4b3c92519c6",
  "experiments/v092/determinism.py": "d1d5f3f86b21f156947b2569acd733fa831d9af206699754719fc5444029cb72"
}
```

## Research blockers and next scope

Stage 1 acquired physical consumption (six events, nutrient gain 237.75, eleven upward internal-bin changes), but did not retain a supported beneficial temporal relation. Checkpoints were below graph capacity; a capacity explanation is unsupported. Investigating admission and durable preservation of resource-to-internal consequence evidence is a research hypothesis, not an established root cause. Delayed ablation removed 0% of the Stage 1 time advantage; motivation ablation removed about 0.669% of its J advantage, below the declared 50%.

Stage 2 experienced FULL failed all 16 trials while fresh succeeded in all 16. Its declared explicit chain gate failed. Stage 3 only the South variant passed; East, West and translated North failed. Stage 4 had 18/32 experienced versus 17/32 fresh successes and lower J, with a positive motivation-ablation effect, but failed action/time, paired-win and economy gates. The zero-nutrient appearance control produced no consumption or nutrient gain; perceptual/action contradictions do not establish contradiction of an acquired nutritive hypothesis.

Resolving exact full-state reproducibility is an additional blocker. No cognitive fix or post-hoc threshold adjustment was applied to rescue this experiment. v0.9.3 remains long-run boundedness, stability and soak-test work; a 10-hour soak and manual hardware/DPI verification were not performed here.

## Frozen curriculum and recorder contract

Training: Stage 1 32 fresh physical episodes at 6 s; Stage 2 48 at 9 s; Stage 3 no training; post-heldout consolidation 8 episodes per North/East/South/West direction at 9 s (32 episodes). Training seeds 92001-92008; evaluation seeds 92101-92116. Evaluation horizons are 6/9/9/30 s for stages 1-4. Initial E/N/H=45/12/80; nutrient payload 40, hydration payload 0; basal body/brain rates 0.3/0.1; MOVE/INTERACT cost 0.2/0.1; spawning every 6 s with at most two live resources. Cognitive parameters are unchanged. All experienced/ablated groups independently reload the corresponding immutable checkpoint with fresh physical state; only the declared delayed or valuation flag is disabled. Interoception remains enabled.

The recorder advances only to production scheduler event boundaries using run_until, with WorldTime as the time base. A separate regression checks equivalence to direct run_until(T). No observation forces actions or full graph synchronization. First consumption requires a successful completed INTERACT, disappearance of a nutritive resource and actual N increase; failures keep raw first-consumption fields null and use full-horizon/final-action censoring.

For samples i, J=sum_i[(T_i+T_(i+1))/2 * exp(-0.02*(t_i+t_(i+1))/2) * (t_(i+1)-t_i)], where T is actual physiological tension. Energy spent=sum_i max(E_i-E_(i+1),0); brownout is any E<=0. Held resources are included in disappearance tracking.

Phase A files: cpp/include/se/workbench_ui.hpp, cpp/src/workbench_ui.cpp, cpp/src/observer.cpp, cpp/src/workbench_settings_ui.cpp, cpp/src/workbench_brain_view.cpp, cpp/tests/observer.cpp, cpp/CMakeLists.txt and docs/V0_9_1_FREEZE_CLOSURE.md. They close reconnect selection reset, optional-tooltip coverage, the actual edge cap of 2048, project version and historical freeze provenance. The user settings file was preserved.

## Final validation (2026-10-02)

- python tools/verify.py --full: PASS; 746 pytest cases, Release observer-ON build, import/headless smokes and native CTest 2/2.
- Six required targeted suites: 242 PASS.
- Observer-OFF native module: 157 PASS across survival/scenario/delayed-learning suites; native CTest 1/1 PASS.
- git diff --check: PASS.
- Full curriculum: 112 training episodes, 512 primary evaluations and two counterfactual controls, no thresholds changed. Scientific verdict FAIL is a completed experiment.
- Reverse-order audit: 64 compared, 46 full-record mismatches, all primary measured metrics identical. Hashseed 1/777 declared pair: exact PASS.

Native binary checksums in the measurement manifest identify the binary used during the research run, before the final verification relink. No remote CI or 10-hour soak result is claimed.
