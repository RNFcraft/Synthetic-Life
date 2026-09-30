"""One ownership boundary for causal settings stored in world artifacts."""
from dataclasses import replace
from config import Settings
from physiology.model import Physiology


def restore_settings(state, explicit=None, sensory=None):
    sources = (("physiology", state.get("physiology", {}).get("config"), Physiology.CONFIG_FIELDS),
               ("resources", state.get("resource_config"), Settings.RESOURCE_FIELDS),
               ("interoception", state.get("interoception_config"), Settings.INTEROCEPTION_FIELDS),
               ("world", state.get("world_config"), Settings.WORLD_FIELDS),
               ("sensory-neural topology", sensory, ("sensory_neural_enabled", "neural_behavioral_participation", "perception_radius", "sensory_neural_channel_bins", "sensory_neural_max_receptors", "sensory_neural_max_injections_per_frame", "sensory_neural_input_amplitude")))
    merged = {}
    for label, values, fields in sources:
        if values is None:
            continue
        if set(values) != set(fields):
            raise ValueError(f"invalid saved {label} configuration")
        for name, value in values.items():
            if name in merged and merged[name] != value:
                raise ValueError(f"conflicting saved {name}")
            merged[name] = value
            if explicit is not None and getattr(explicit, name) != value:
                raise ValueError(f"explicit Settings are incompatible with saved {label}")
    return explicit if explicit is not None else replace(Settings(), **merged)
