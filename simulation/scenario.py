"""Проверенные начальные условия; не checkpoint и не learned knowledge."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from persistence import inspect_container, load_container, save_container
from persistence.container import HEADER
from .persisted_settings import scenario_configuration, restore_scenario_settings

MAX_ARTIFACT_BYTES = 8 * 1024 * 1024
MAX_PATH_BYTES = 4096


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def exact(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(f"invalid {label} fields")


def integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"invalid {label}")
    return value


def number(value, low, high, label):
    if type(value) not in (int, float) or not isfinite(value) or not low <= value <= high:
        raise ValueError(f"invalid {label}")
    return float(value)


def text(value, limit, label, nonempty=False):
    if not isinstance(value, str) or "\x00" in value or len(value.encode("utf-8")) > limit or (nonempty and not value.strip()):
        raise ValueError(f"invalid {label}")
    return value


def artifact_path(value):
    path = Path(text(str(value) if isinstance(value, Path) else value, MAX_PATH_BYTES, "artifact path", True))
    if path.is_dir():
        raise ValueError("artifact path is a directory")
    return path


def load_artifact(path, kind, groups):
    path = artifact_path(path)
    if path.stat().st_size > MAX_ARTIFACT_BYTES:
        raise ValueError("artifact size limit exceeded")
    raw = path.read_bytes()
    if len(raw) < HEADER.size:
        raise ValueError("truncated artifact header")
    # Ограничиваем число JSON containers ДО materialization: миллион пустых
    # records не проходит даже в маленьком файле. Строки metadata не считаются.
    table_size = HEADER.unpack(raw[:HEADER.size])[-1]
    quoted = escaped = False
    containers = depth = 0
    for byte in raw[HEADER.size+table_size:]:
        if quoted:
            if escaped:escaped = False
            elif byte == 92:escaped = True
            elif byte == 34:quoted = False
        elif byte == 34:quoted = True
        elif byte in (91,123):
            containers += 1;depth += 1
            if containers > 12000 or depth > 32:
                raise ValueError("artifact JSON complexity limit exceeded")
        elif byte in (93,125):depth -= 1
    info = inspect_container(path)
    if {row["name"] for row in info["sections"]} != set(groups):
        raise ValueError("invalid artifact sections")
    end = 0
    for row in sorted(info["sections"], key=lambda r: r["offset"]):
        if row["offset"] != end:
            raise ValueError("invalid artifact section layout")
        end += row["size"]
    return load_container(path, kind, set(groups))


def artifact_checksum(path):
    return sha256(Path(path).read_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    """JSON хранится канонически и неизменяемо; sections возвращает копию."""
    _canonical: str

    def __post_init__(self):
        normalized = validate_sections(json.loads(self._canonical))
        object.__setattr__(self, "_canonical", canonical_json(normalized))

    @classmethod
    def from_sections(cls, sections):
        return cls(canonical_json(sections))

    @property
    def sections(self):
        return json.loads(self._canonical)

    @property
    def seed(self):
        return self.sections["CONFIG"]["seed"]

    @property
    def settings(self):
        return restore_scenario_settings(self.sections["CONFIG"]["settings"])

    @property
    def causal_checksum(self):
        sections = self.sections
        return sha256(canonical_json({k: sections[k] for k in ("CONFIG", "INITIAL")}).encode()).hexdigest()

    def instantiate(self, brain=None):
        from .continuous import ContinuousRuntime
        return ContinuousRuntime.from_scenario(self, brain)


def validate_sections(sections):
    exact(sections, ("META", "CONFIG", "INITIAL"), "scenario sections")
    meta, config, initial = sections["META"], sections["CONFIG"], sections["INITIAL"]
    exact(meta, ("schema", "version", "name", "description", "tags"), "scenario metadata")
    if meta["schema"] != "synthetic-life-scenario" or type(meta["version"]) is not int or meta["version"] != 1:
        raise ValueError("unsupported scenario schema/version")
    text(meta["name"], 256, "scenario name", True)
    text(meta["description"], 4096, "scenario description")
    if not isinstance(meta["tags"], list) or len(meta["tags"]) > 32:
        raise ValueError("invalid scenario tags")
    for tag in meta["tags"]:
        text(tag, 64, "scenario tag", True)
    exact(config, ("seed", "settings"), "scenario config")
    integer(config["seed"], 0, 2**63-1, "scenario seed")
    settings = restore_scenario_settings(config["settings"])
    exact(initial, ("bodies", "objects", "held_objects", "physiology"), "scenario initial")
    exact(initial["physiology"], ("energy", "nutrients", "hydration"), "initial physiology")
    for name, value in initial["physiology"].items():
        initial["physiology"][name] = number(value, 0, getattr(settings, f"physiology_max_{name}"), name)
    bodies, objects, held = initial["bodies"], initial["objects"], initial["held_objects"]
    if not isinstance(bodies, list) or len(bodies) != settings.entity_count or not 1 <= len(bodies) <= 64:
        raise ValueError("invalid scenario body count")
    if any(not isinstance(rows, list) or len(rows) > settings.max_objects + settings.resource_max_live for rows in (objects, held)):
        raise ValueError("scenario object capacity exceeded")
    positions, body_ids, object_ids, owners = set(), set(), set(), set()
    for body in bodies:
        exact(body, ("id", "x", "y", "orientation", "appearance"), "body")
        identifier = integer(body["id"], 0, 2**32-2, "body ID")
        if identifier in body_ids:
            raise ValueError("duplicate body ID")
        body_ids.add(identifier)
        integer(body["appearance"], 0, 65535, "body appearance")
        if body["orientation"] not in ("NORTH", "EAST", "SOUTH", "WEST"):
            raise ValueError("invalid orientation")
        position = (integer(body["x"], 0, settings.world_width-1, "body x"), integer(body["y"], 0, settings.world_height-1, "body y"))
        if position in positions:
            raise ValueError("overlapping bodies")
        positions.add(position)
    if body_ids != set(range(settings.entity_count)):
        raise ValueError("current runtime requires contiguous body IDs starting at 0")
    ordinary, resources = 0, 0
    for rows, held_row in ((objects, False), (held, True)):
        for obj in rows:
            fields = ("id", "x", "y", "state", "resource_channel", "nutrients", "hydration")
            exact(obj, fields + (("owner_id",) if held_row else ()), "object")
            identifier = integer(obj["id"], 1, 2**32-2, "object ID")
            if identifier in object_ids:
                raise ValueError("duplicate free/held object ID")
            object_ids.add(identifier)
            position = (integer(obj["x"], 0, settings.world_width-1, "object x"), integer(obj["y"], 0, settings.world_height-1, "object y"))
            integer(obj["state"], -2**31, 2**31-1, "object appearance")
            channel = integer(obj["resource_channel"], 0, 2, "resource channel")
            for key in ("nutrients", "hydration"):
                obj[key] = number(obj[key], 0, 100, "resource payload")
            if channel:
                if obj["state"] != channel or not (obj["nutrients"] or obj["hydration"]):
                    raise ValueError("invalid native resource representation")
                resources += 1
            else:
                if obj["nutrients"] or obj["hydration"]:
                    raise ValueError("neutral object cannot carry resource payload")
                ordinary += 1
            if held_row:
                owner = integer(obj["owner_id"], 0, 2**32-2, "held owner")
                if owner not in body_ids or owner in owners:
                    raise ValueError("invalid held-object owner")
                owners.add(owner)
            else:
                if position in positions:
                    raise ValueError("overlapping object/body geometry")
                positions.add(position)
    if ordinary > settings.max_objects or resources > settings.resource_max_live:
        raise ValueError("scenario capacity exceeded")
    initial["bodies"] = sorted(bodies, key=lambda r: r["id"])
    initial["objects"] = sorted(objects, key=lambda r: r["id"])
    initial["held_objects"] = sorted(held, key=lambda r: (r["owner_id"], r["id"]))
    return sections


def save_scenario(definition, path):
    if not isinstance(definition, ScenarioDefinition):
        raise TypeError("expected validated ScenarioDefinition")
    save_container(artifact_path(path), "scenario", definition.sections)


def load_scenario(path):
    return ScenarioDefinition.from_sections(load_artifact(path, "scenario", ("META", "CONFIG", "INITIAL")))


def export_rejection(runtime, paused):
    if not paused:
        return "pause the host first"
    if runtime._action_in_flight():
        return "physical action is in flight; use Finish action & pause"
    if runtime.editor_inbox or runtime.language_inbox or runtime.language_frontier is not None:
        return "pending editor/language input"
    frontier = runtime.simulation.core.continuous_frontier
    if frontier is not None and not frontier.committed:
        return "uncommitted cognition transaction"
    if runtime.simulation.world.native.pending_consequence() != (0., 0.):
        return "pending physical consequence"
    return None


def export_scenario(runtime, path, *, seed, name, description="", tags=(), paused=False):
    rejection = export_rejection(runtime, paused)
    if rejection:
        raise ValueError(f"Scenario export rejected: {rejection}")
    native = runtime.simulation.world.native
    bodies, objects, held, *_ = native.full_state()
    resources = {row[0]: row[1:] for row in native.resource_state()}
    def obj(row):
        identifier, x, y, state = row
        channel, nutrients, hydration = resources.get(identifier, (0, 0., 0.))
        return dict(id=identifier, x=x, y=y, state=state, resource_channel=channel, nutrients=nutrients, hydration=hydration)
    from world.native_world import LONG
    physical = runtime.simulation.physiology.snapshot()
    definition = ScenarioDefinition.from_sections({
        "META": dict(schema="synthetic-life-scenario", version=1, name=name, description=description, tags=list(tags)),
        "CONFIG": dict(seed=seed, settings=scenario_configuration(runtime.simulation.settings)),
        "INITIAL": dict(bodies=[dict(id=i, x=x, y=y, orientation=LONG[orientation], appearance=appearance) for i,x,y,orientation,held_id,appearance in bodies],
                        objects=[obj(row) for row in objects],
                        held_objects=[dict(owner_id=row[0], **obj(row[1:])) for row in held],
                        physiology={k:getattr(physical,k) for k in ("energy", "nutrients", "hydration")})})
    save_scenario(definition, path)
    return definition


def causal_digest(runtime):
    """Диагностический digest milestone, не вечный публичный ABI."""
    value = {"simulation": runtime.simulation.snapshot_data(), "scheduler": runtime.scheduler_state(),
             "frontier": runtime._frontier_state(), "language_frontier": runtime._language_frontier_state(),
             "language_inbox": [[identifier,asdict(frame)] for identifier,frame in sorted(runtime.language_inbox.items())],
             "language": runtime.simulation.core.language.to_dict(),
             "grounding": runtime.simulation.core.grounding_context.durable_dict(),
             "grounding_episode": runtime.simulation.core.grounding_context.episode_dict(),
             "actions": runtime.actions_completed, "observations": runtime.observation_ordinal,
             "generation": runtime.cognition_generation, "maintenance": runtime.maintenance_ordinal}
    # Эти две таблицы сериализуют mapping как пары; порядок insertion зависит
    # от hash seed, но не является causal ordering. Остальные sequences не сортируем.
    memory = value["simulation"]["core"]["memory"]
    for field in ("feature_seen", "feature_change"):
        if field in memory:
            memory[field] = sorted(memory[field], key=lambda row: canonical_json(row[0]))
    return sha256(canonical_json(value).encode()).hexdigest()
