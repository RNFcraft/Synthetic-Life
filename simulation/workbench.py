"""Presentation and explicit human interventions; never a cognitive input API."""
from dataclasses import asdict, dataclass, field
from math import isfinite


CAUSAL_COMMANDS = {"PLACE_FOOD", "PLACE_WATER", "PLACE_OBJECT", "REMOVE_OBJECT", "SEND_DIALOGUE"}


@dataclass(frozen=True, slots=True)
class EditorCommand:
    id: int
    kind: str
    issued_at: float
    x: int = 0
    y: int = 0
    object_id: int = 0
    text: str = ""


@dataclass(frozen=True, slots=True)
class WorkbenchStatusSnapshot:
    world_time: float
    event_sequence: int
    paused: bool
    actions_completed: int
    pending_events: int
    energy: float
    energy_max: float
    nutrients: float
    nutrients_max: float
    hydration: float
    hydration_max: float
    hunger: float
    tension: float
    energy_depleted: bool
    interoception_enabled: bool
    bin_count: int
    bins: tuple[int, ...]
    target_bins: tuple[int, ...]
    internal_observed_at: float
    cognits: int
    relations: int
    active_cognits: int
    micro_cognits: int
    micro_relations: int
    assemblies: int
    current_action: str
    planned_actions: tuple[str, ...]
    has_plan: bool
    plan_score: float
    plan_confidence: float
    homeostatic_component: float
    prediction_confidence: float
    delayed_prediction_enabled: bool
    has_temporal_prediction: bool
    passive_depth: int
    predicted_delay: float
    ambiguity: float
    food_payload: float
    water_payload: float
    last_command_result: str
    seed: int = 12345
    dialogue_notice: str = ""
    configuration: dict = field(default_factory=dict)


class WorkbenchRuntimeMixin:
    """Runtime-side owner of accepted causal commands and detached status."""

    def _init_workbench(self):
        self.editor_inbox = {}
        self.next_editor_command_id = 1
        self.last_editor_result = ""
        self.last_workbench_notice = ""
        self.last_dialogue_notice = ""
        self.workbench_channel = None

    def accept_editor_command(self, kind, *, x=0, y=0, object_id=0, text=""):
        from consciousness.native_engine import RuntimeEventType
        if kind not in CAUSAL_COMMANDS:
            raise ValueError("invalid causal editor command")
        if any(type(value) is not int for value in (x, y, object_id)) or object_id < 0 or object_id > 0xffffffff:
            raise ValueError("invalid editor coordinates or ID")
        if not isinstance(text, str) or len(text.encode("utf-8")) > 4096:
            raise ValueError("editor text exceeds limit")
        if kind == "SEND_DIALOGUE" and not text.strip():
            raise ValueError("empty dialogue")
        if len(self.editor_inbox) >= 256:
            raise ValueError("editor inbox is full")
        command = EditorCommand(self.next_editor_command_id, kind, self.world_time, x, y, object_id, text)
        self.scheduler.schedule(self.world_time, RuntimeEventType.EXTERNAL_INPUT, command.id)
        self.editor_inbox[command.id] = command
        self.next_editor_command_id += 1
        return command.id

    def _process_editor_command(self, event):
        from consciousness.native_engine import RuntimeEventType
        command = self.editor_inbox[event.payload]
        core = self.simulation.core
        frontier = core.continuous_frontier
        # Finish the ordinary cognition/language transaction first. Committed
        # physical actions are allowed to complete against the edited world.
        if self.language_frontier is not None or (frontier is not None and not frontier.committed):
            self.scheduler.schedule(event.time, RuntimeEventType.EXTERNAL_INPUT, command.id)
            return
        world = self.simulation.world
        try:
            if command.kind == "SEND_DIALOGUE":
                # UI whitespace-delimited tokens are explicit utterance boundaries.
                self.inject_utterance(tuple(command.text.split()), event.time)
            else:
                sequence = self.simulation.event_sequence.value + 1
                position = (command.x, command.y)
                if command.kind == "PLACE_FOOD":
                    world.spawn_resource(position, 1, self.simulation.settings.resource_nutrient_payload, 0., event.time, sequence)
                elif command.kind == "PLACE_WATER":
                    world.spawn_resource(position, 2, 0., self.simulation.settings.resource_hydration_payload, event.time, sequence)
                elif command.kind == "PLACE_OBJECT":
                    world.editor_place_object(position, event.time, sequence)
                else:
                    world.editor_remove_object(command.object_id, event.time, sequence)
                self.simulation.event_sequence.next()
                # Preserve an in-flight action, using its completion observation.
                if not self._action_in_flight() and not any(e.type == RuntimeEventType.SENSORY_CHANGE and not e.payload for e in self.scheduler.snapshot()):
                    self.scheduler.schedule(event.time, RuntimeEventType.SENSORY_CHANGE)
            if command.kind == "SEND_DIALOGUE":
                self.last_dialogue_notice = ""
            else:
                self.last_editor_result = f"#{command.id} {command.kind}: accepted"
        except (ValueError, TypeError) as error:
            if command.kind == "SEND_DIALOGUE":
                self.last_dialogue_notice = f"Dialogue rejected: {error}"
            else:
                self.last_editor_result = f"#{command.id} {command.kind}: rejected ({error})"
        del self.editor_inbox[command.id]

    def _editor_state(self):
        return {"version": 1, "next_id": self.next_editor_command_id,
                "inbox": [asdict(value) for _, value in sorted(self.editor_inbox.items())]}

    def _restore_editor_state(self, value):
        self._init_workbench()
        if value is None:
            from consciousness.native_engine import RuntimeEventType
            if any(e.type == RuntimeEventType.EXTERNAL_INPUT for e in self.scheduler.snapshot()):
                raise ValueError("editor inbox missing for scheduled commands")
            return
        if value.get("version") != 1 or type(value.get("next_id")) is not int or value["next_id"] < 1:
            raise ValueError("invalid editor state")
        rows = value.get("inbox", [])
        if len(rows) > 256:
            raise ValueError("editor inbox exceeds limit")
        for row in rows:
            command = EditorCommand(**row)
            if type(command.id) is not int or command.kind not in CAUSAL_COMMANDS or command.id in self.editor_inbox or not 0 < command.id < value["next_id"]:
                raise ValueError("invalid saved editor command")
            if not isfinite(command.issued_at) or command.issued_at > self.world_time or command.issued_at < 0:
                raise ValueError("invalid command timestamp")
            if any(type(v) is not int for v in (command.x, command.y, command.object_id)) or not 0 <= command.object_id <= 0xffffffff:
                raise ValueError("invalid saved editor payload")
            if not isinstance(command.text, str) or len(command.text.encode("utf-8")) > 4096:
                raise ValueError("invalid saved editor text")
            if command.kind == "SEND_DIALOGUE" and not command.text.strip():
                raise ValueError("empty saved dialogue command")
            self.editor_inbox[command.id] = command
        from consciousness.native_engine import RuntimeEventType
        pending = [e.payload for e in self.scheduler.snapshot() if e.type == RuntimeEventType.EXTERNAL_INPUT]
        if sorted(pending) != sorted(self.editor_inbox):
            raise ValueError("editor inbox and scheduler disagree")
        self.next_editor_command_id = value["next_id"]

    def workbench_status(self, paused=False):
        sim = self.simulation
        core, configured = sim.core, sim.settings
        from .workbench_settings import configuration_draft
        physical = sim.physiology.snapshot()
        plan = core.planner.plan
        diagnostics = core.planner.homeostatic_diagnostics()
        temporal = diagnostics.get("temporal", {})
        substrate = core.backend.engine.neurodynamic_substrate()
        observed = self.last_internal
        return WorkbenchStatusSnapshot(
            self.world_time, sim.event_sequence.value, paused, self.actions_completed, self.scheduler.size,
            physical.energy, configured.physiology_max_energy, physical.nutrients, configured.physiology_max_nutrients,
            physical.hydration, configured.physiology_max_hydration, physical.hunger, physical.tension, physical.energy <= 0.,
            configured.interoception_enabled, configured.interoception_bins,
            observed.levels if observed else (-1, -1, -1), sim.interoception.target_levels if sim.interoception else (-1, -1, -1),
            observed.world_time if observed else -1., core.backend.engine.live_cognit_count, core.backend.engine.relation_count,
            len(core.last_wave.active_ids), substrate.micro_kappa_count, substrate.micro_rho_count,
            substrate.consolidated_assembly_count,
            sim.last_action.kind.name if sim.last_action else "—", tuple(a.name for a in plan.actions) if plan else (),
            plan is not None, plan.score if plan else 0., plan.confidence if plan else 0.,
            diagnostics.get("homeostatic_plan_component", 0.), diagnostics.get("homeostatic_prediction_confidence", 0.),
            configured.delayed_homeostatic_prediction_enabled, bool(temporal.get("usable")),
            temporal.get("passive_depth", 0), temporal.get("elapsed", 0.), temporal.get("ambiguity", 0.),
            configured.resource_nutrient_payload, configured.resource_hydration_payload,
            self.last_workbench_notice or self.last_editor_result,
            sim.seed if 0 <= sim.seed <= 2**63-1 else 0, self.last_dialogue_notice,
            configuration_draft(configured, sim.seed if 0 <= sim.seed <= 2**63-1 else 0))

    def publish_workbench_status(self, paused=False):
        value = self.workbench_status(paused)
        if self.workbench_channel is not None:
            self.workbench_channel.publish(asdict(value))
        return value

    def step_causal_boundary(self):
        """Execute the next timestamp and all zero-time continuations it creates."""
        if not self.scheduler.size:
            return 0
        return self.run_until(self.scheduler.snapshot()[0].time)


class WorkbenchController:
    """Host-only pause and queue polling. Host timing never enters commands."""
    def __init__(self, runtime, observer=None):
        from consciousness._native_brain import WorkbenchCommandChannel, WorkbenchStatusChannel
        self.runtime = runtime
        self.paused = False
        self.replacement = None
        self.commands = WorkbenchCommandChannel()
        runtime.workbench_channel = WorkbenchStatusChannel()
        if observer is not None:
            observer.attach_workbench(runtime.workbench_channel, self.commands)
        runtime.publish_workbench_status(self.paused)

    def poll(self):
        stepped = False
        for row in self.commands.drain():
            _, kind, x, y, object_id, text = row[:6]
            name = kind.name
            if name == "CREATE_NEW_WORLD":
                from .workbench_settings import create_new_world, PRESETS
                try:
                    if len(row) != 7:
                        raise ValueError("missing new-world configuration")
                    replacement = create_new_world(row[6], self.runtime.simulation.settings)
                    replacement.last_workbench_notice = f"New world created - {PRESETS[row[6]['preset']]}, seed {row[6]['seed']}"
                    self.replacement = replacement
                    break  # Commands after reset belong to the discarded episode.
                except (ValueError, TypeError, KeyError, RuntimeError) as error:
                    self.runtime.last_workbench_notice = f"New world rejected: {error}"
            elif name == "PAUSE":
                self.paused = True
            elif name == "RESUME":
                self.paused = False
            elif name == "STEP":
                if self.paused:
                    self.runtime.step_causal_boundary()
                    stepped = True
            elif name == "REACH_SCENARIO_BOUNDARY":
                if self.paused:
                    self.runtime.reach_scenario_boundary()
                    self.runtime.last_workbench_notice = "Safe physical boundary reached; Save does not advance time"
                    stepped = True
                else:
                    self.runtime.last_workbench_notice = "Pause before finishing the current action"
            elif name == "EXPORT_SCENARIO":
                from .scenario import export_scenario
                try:
                    if len(row) != 9:
                        raise ValueError("missing scenario export payload")
                    path, scenario_name, seed = row[6:]
                    export_scenario(self.runtime, path, seed=seed, name=scenario_name, paused=self.paused)
                    self.runtime.last_workbench_notice = f"Scenario saved: {path}"
                except (ValueError, OSError, TypeError) as error:
                    self.runtime.last_workbench_notice = f"Scenario export rejected: {error}"
            else:
                try:
                    if name != "SEND_DIALOGUE":self.runtime.last_workbench_notice = ""
                    self.runtime.accept_editor_command(name, x=x, y=y, object_id=object_id, text=text)
                except (ValueError, TypeError) as error:
                    if name == "SEND_DIALOGUE":self.runtime.last_dialogue_notice = str(error)
                    else:self.runtime.last_editor_result = f"{name}: rejected ({error})"
        if self.replacement is not None:
            return False
        if self.paused and self.runtime.editor_inbox:
            # Editing a paused world applies only its current causal timestamp.
            self.runtime.run_to_quiescence()
        self.runtime.publish_workbench_status(self.paused)
        return stepped
