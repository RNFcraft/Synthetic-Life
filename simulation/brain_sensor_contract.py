"""Preflight compatibility of durable brain sensor-domain representations."""
from consciousness.patterns import is_internal_primitive
from physiology.interoception import InteroceptiveTransducer


def internal_knowledge(sections):
    """Inspect structured patterns, including transferable proto-pattern evidence."""
    for node in sections["COGN"]["nodes"]:
        pattern = node.get("pattern")
        if not pattern:
            continue
        for primitive in pattern["participants"]:
            if is_internal_primitive(primitive):
                return True
        for participant in pattern.get("nodes", ()):
            if participant["participant_type"] == "PRIMITIVE" and is_internal_primitive(participant["reference"]):
                return True
    return any(is_internal_primitive(primitive)
               for prototype in sections["PATT"]["prototypes"]
               for primitive in prototype["participants"])


def brain_sensor_metadata(graph, patterns, settings):
    if not internal_knowledge({"COGN": graph, "PATT": patterns}):
        return {}
    return {"internal_sensor_contract": InteroceptiveTransducer.sensor_contract(settings)}


def validate_brain_sensor_contract(sections, settings):
    """Fail before loading any graph; bin IDs are never reinterpreted or rescaled."""
    if not internal_knowledge(sections):
        return
    saved = sections["META"].get("internal_sensor_contract")
    if saved is None:
        raise ValueError("legacy brain contains internal knowledge but has no internal sensor contract; encoding topology cannot be established")
    expected = InteroceptiveTransducer.sensor_contract(settings)
    if (not isinstance(saved, dict) or set(saved) != set(expected)
            or type(saved["schema"]) is not int or type(saved["bins"]) is not int
            or not isinstance(saved["channels"], list)
            or saved != expected):
        raise ValueError(f"incompatible brain internal sensor contract: saved {saved!r}; expected {expected!r}")
