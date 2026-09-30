import json
from math import isfinite
from random import Random
from pathlib import Path
from typing import Any


RNG_STATE_ENCODING = "python-random-json-v1"


def _rng_json(value: object, depth: int = 0) -> object:
    """Encode only the structural types produced by ``Random.getstate``."""
    if depth > 8:
        raise ValueError("RNG state nesting is invalid")
    if value is None:
        return value
    if isinstance(value,int) and not isinstance(value,bool):
        return value
    if isinstance(value,float) and isfinite(value):
        return value
    if isinstance(value, tuple):
        return [_rng_json(item, depth + 1) for item in value]
    raise ValueError(f"unsupported RNG state value: {type(value).__name__}")


def encode_random_state(state: object) -> dict[str, object]:
    """Serialize Python's RNG state without executable deserialization."""
    return {"encoding": RNG_STATE_ENCODING, "state": _rng_json(state)}


def _rng_tuple(value: object, depth: int = 0) -> object:
    if depth > 8:
        raise ValueError("RNG state nesting is invalid")
    if value is None:
        return None
    # bool is an int subclass but is not a valid MT state word.
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float) and isfinite(value):
        return value
    if isinstance(value, list):
        return tuple(_rng_tuple(item, depth + 1) for item in value)
    raise ValueError("RNG state must contain only finite numeric tuples and null")


def decode_random_state(value: object) -> object:
    """Restore a validated JSON RNG state.

    Legacy base64 pickle payloads deliberately fail closed: normal snapshot and
    .seworld loaders must never execute bytes supplied by an artifact.
    """
    if not isinstance(value, dict) or value.get("encoding") != RNG_STATE_ENCODING:
        raise ValueError("unsafe or unsupported RNG state encoding")
    if set(value) != {"encoding", "state"}:
        raise ValueError("malformed RNG state")
    state = _rng_tuple(value["state"])
    if not isinstance(state, tuple) or len(state) != 3:
        raise ValueError("malformed RNG state")
    try:
        Random().setstate(state)
    except (TypeError, ValueError) as exc:
        raise ValueError("malformed RNG state") from exc
    return state


def save_snapshot(data: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_snapshot(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
