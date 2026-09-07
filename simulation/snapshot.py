import base64
import json
import pickle
from pathlib import Path
from typing import Any


def encode_random_state(state: object) -> str:
    # RNG state contains tuples not faithfully represented by JSON; the pickle is
    # isolated, base64-wrapped and never used for arbitrary application objects.
    return base64.b64encode(pickle.dumps(state, protocol=4)).decode("ascii")


def decode_random_state(value: str) -> object:
    return pickle.loads(base64.b64decode(value.encode("ascii")))


def save_snapshot(data: dict[str, Any], path: str | Path) -> None:
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def load_snapshot(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

