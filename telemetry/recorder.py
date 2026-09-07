import json
from pathlib import Path
from .metrics import Telemetry


def write_jsonl(telemetry: Telemetry, path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as stream:
        for item in telemetry.history:
            stream.write(json.dumps(item.to_dict(), ensure_ascii=False) + "\n")

