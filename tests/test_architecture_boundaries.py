"""Repository-wide guards for frozen dependency and causality boundaries."""

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]


def _imports(path: Path) -> set[str]:
    modules = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_data_layers_do_not_import_core_facade():
    paths = sorted((ROOT / "consciousness").glob("*_types.py"))
    paths += sorted((ROOT / "simulation").glob("*_types.py"))
    # Pure helpers do not share the naming convention but have the same
    # downward-only dependency contract.
    paths.append(ROOT / "consciousness" / "memory_matching.py")
    assert paths, "no data/type layers discovered"
    for path in paths:
        assert not any(name in {"core", "consciousness.core"} for name in _imports(path)), f"data layer imports core facade: {path}"


def test_language_modules_have_no_direct_action_policy():
    for path in sorted((ROOT / "consciousness").glob("language*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        assert "ActionType" not in names, f"language gained direct ActionType knowledge: {path}"
        assert not any(name in {"world", "world.actions"} for name in _imports(path)), f"language imports action boundary: {path}"


def test_neural_sources_have_no_action_or_goal_semantics():
    paths = sorted((ROOT / "cpp" / "src").glob("neurodynamic*.cpp"))
    paths += [ROOT / "cpp" / "include" / "se" / "neurodynamic_substrate.hpp"]
    assert {path.name for path in paths} >= {"neurodynamic_substrate.cpp", "neurodynamic_bridge.cpp", "neurodynamic_substrate.hpp"}
    forbidden = ("ActionType", "Goal", "MOVE_", "GRAB_", "INTERACT_", "reward label")
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert not any(token in text for token in forbidden), f"neural layer gained semantic policy token: {path}"


def test_observer_is_snapshot_only():
    source = (ROOT / "cpp" / "src" / "observer.cpp").read_text(encoding="utf-8")
    header = (ROOT / "cpp" / "include" / "se" / "observer.hpp").read_text(encoding="utf-8")
    for forbidden in ('#include "se/world.hpp"', "NativeBrainEngine", "EventScheduler", "advance_world_time", ".schedule("):
        assert forbidden not in source + header, f"observer crossed causal boundary: {forbidden}"


def test_workbench_keeps_ui_dependencies_and_commands_out_of_cognition():
    for path in (ROOT / "consciousness").glob("*.py"):
        assert not any(module.startswith(("simulation.workbench", "ui.workbench")) for module in _imports(path))
    for name in ("planning.py", "choice.py", "valuation.py"):
        tree=ast.parse((ROOT/"consciousness"/name).read_text(encoding="utf-8"))
        identifiers={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
        identifiers|={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}
        assert not identifiers & {"Food","Water","presentation_kind","WorkbenchCommand","WorkbenchStatusSnapshot"}
    cmake=(ROOT/"cpp/CMakeLists.txt").read_text(encoding="utf-8")
    engine="\n".join(line for line in cmake[:cmake.index("if(SE_BUILD_OBSERVER)")].splitlines()
                     if line.startswith(("add_library(se_engine", "target_link_libraries(se_engine", "find_package(", "FetchContent_")))
    assert "imgui" not in engine.lower() and "OpenGL" not in engine and "SDL3" not in engine
    assert "GIT_TAG v1.91.9b" in cmake
    for path in (ROOT/"cpp/src").glob("workbench*.cpp"):
        text=path.read_text(encoding="utf-8")
        assert not any(token in text for token in ('#include "se/world.hpp"',"apply_intent", "spawn_resource", "NativeBrainEngine", "NeurodynamicSubstrate", "PyObject", "gil_scoped"))


def test_workbench_command_handler_cannot_mutate_cognitive_graph_or_physiology():
    tree=ast.parse((ROOT/"simulation/workbench.py").read_text(encoding="utf-8"))
    handler=next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name=="_process_editor_command")
    attrs={node.attr for node in ast.walk(handler) if isinstance(node,ast.Attribute)}
    assert not attrs & {"physiology","add_cognit","connect","delete_cognit","receive","inject_batch","apply_consequence","commit_continuous_action"}
    for path in (ROOT/"consciousness").glob("*.py"):
        tree=ast.parse(path.read_text(encoding="utf-8"))
        attrs={node.attr for node in ast.walk(tree) if isinstance(node,ast.Attribute)}
        assert not attrs & {"workbench_status","workbench_channel","editor_inbox","presentation_kind"}


def test_cognit_bridge_has_no_reverse_micro_injection():
    paths = sorted((ROOT / "cpp" / "src").glob("native_brain*.cpp"))
    assert any(path.name == "native_brain_bridge.cpp" for path in paths)
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    for forbidden in (".inject(", ".inject_batch(", ".add_micro_kappa(", ".add_micro_rho("):
        assert forbidden not in text, f"Cognit layer gained reverse neural mutation: {forbidden}"


def test_full_graph_sync_counter_has_no_increment_path():
    path = ROOT / "consciousness" / "backends.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    writes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Attribute) and target.attr == "full_graph_sync_calls":
                    writes.append(node)
    assert len(writes) == 1 and isinstance(writes[0], ast.Assign), "full graph synchronization path was added"


def test_physiological_policy_dependency_boundaries():
    for name in ("planning.py", "choice.py", "valuation.py"):
        path = ROOT / "consciousness" / name
        assert path.is_file()
        assert not any(module.startswith(("physiology", "world.objects", "world.native_world"))
                       for module in _imports(path)), path
        tree = ast.parse(path.read_text(encoding="utf-8"))
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        assert not attributes & {"physiology", "pending_consequence", "nutrient_payload",
            "hydration_payload", "resource_channel", "homeostatic_projection"}, path
    path = ROOT / "physiology" / "interoception.py"
    assert not any(module.startswith(("world", "consciousness")) for module in _imports(path))
    names = {node.id for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(node, ast.Name)}
    assert not names & {"Action", "ActionType", "Goal", "DeliberativePlanner"}


def test_language_has_no_physiological_sensor_domain():
    for path in (ROOT / "consciousness").glob("language*.py"):
        assert not any(module.startswith("physiology") for module in _imports(path))
        tree = ast.parse(path.read_text(encoding="utf-8"))
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        assert not attributes & {"previous_internal", "homeostatic_projection", "physiology"}
        strings = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        assert not any(value.startswith("internal_") for value in strings)


def test_observer_cannot_write_internal_state():
    for path in (ROOT / "ui").rglob("*.py"):
        assert not any(module.startswith("physiology") for module in _imports(path))
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Call)):
                # Explicit production access chains, including mutation calls.
                chain = ast.unparse(node)
                assert ".physiology." not in chain and ".interoception." not in chain, path
    sources = "\n".join((ROOT / "cpp" / part).read_text(encoding="utf-8")
                        for part in ("src/observer.cpp", "include/se/observer.hpp"))
    for forbidden in ("apply_consequence", "InteroceptiveTransducer", "Physiology&", "Physiology *"):
        assert forbidden not in sources


def test_spatial_candidate_path_uses_sensor_domain_predicate():
    from consciousness.patterns import is_spatial_primitive
    assert not is_spatial_primitive((0, 0, "internal_1", 3, 1))
    assert is_spatial_primitive((0, 0, "appearance", 3, 1))
    source = (ROOT / "consciousness" / "sensory.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    movable = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "movable" for t in node.targets))
    assert any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
               and node.func.id == "is_spatial_primitive" for node in ast.walk(movable))


def test_brain_compatibility_preflight_precedes_graph_loading():
    tree = ast.parse((ROOT / "simulation" / "simulation.py").read_text(encoding="utf-8"))
    load = next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)
                and node.name == "load_brain")
    checks = [node for node in ast.walk(load) if isinstance(node,ast.Call)
              and isinstance(node.func,ast.Name) and node.func.id == "validate_brain_sensor_contract"]
    assert len(checks) == 1
    activation = [node for node in ast.walk(load) if isinstance(node,ast.Call)
                  and isinstance(node.func,ast.Attribute)
                  and node.func.attr in {"snapshot_data","load","load_graph"}]
    assert activation and all(checks[0].lineno < node.lineno for node in activation)
    path = ROOT / "simulation" / "brain_sensor_contract.py"
    helper = ast.parse(path.read_text(encoding="utf-8"))
    assert any(isinstance(node,ast.Call) and isinstance(node.func,ast.Name)
               and node.func.id == "is_internal_primitive" for node in ast.walk(helper))
    # Compatibility only compares contracts. It cannot rewrite or rescale bins.
    assert not any(isinstance(node,ast.BinOp) for node in ast.walk(helper))
    assert not any(isinstance(node,ast.Assign) and any(isinstance(t,ast.Subscript)
               for t in node.targets) for node in ast.walk(helper))


def test_brain_sensor_metadata_has_no_episode_state_access():
    tree = ast.parse((ROOT / "physiology" / "interoception.py").read_text(encoding="utf-8"))
    contract = next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)
                    and node.name == "sensor_contract")
    attributes = {node.attr for node in ast.walk(contract) if isinstance(node,ast.Attribute)}
    assert attributes == {"ENCODING","CHANNELS","interoception_bins"}
    returns = [node for node in ast.walk(contract) if isinstance(node,ast.Return)]
    assert len(returns) == 1 and isinstance(returns[0].value,ast.Dict)
    assert {key.value for key in returns[0].value.keys} == {"schema","encoding","channels","bins"}


def test_delayed_prediction_has_only_graph_and_sensor_domain_inputs():
    path=ROOT / "consciousness" / "temporal_prediction.py"
    tree=ast.parse(path.read_text(encoding="utf-8"))
    assert not any(module.startswith(("physiology","world","simulation")) for module in _imports(path))
    attributes={node.attr for node in ast.walk(tree) if isinstance(node,ast.Attribute)}
    assert not attributes & {"physiology","world","resource_nutrient_payload","resource_hydration_payload",
                             "energy","nutrients","hydration","homeostatic_projection"}
    assert not attributes & {"INTERACT_UP","INTERACT_DOWN","INTERACT_LEFT","INTERACT_RIGHT"}
    source=path.read_text(encoding="utf-8")
    assert "RelationType.SEQUENTIAL" in source and "RelationType.SELF_ACTION" in source
    assert "is_internal_primitive" in source
    cpp=(ROOT / "cpp/src/native_brain_engine.cpp").read_text(encoding="utf-8")
    start=cpp.index("void NativeBrainEngine::observe_transition_delay")
    stop=cpp.index("void NativeBrainEngine::clear_transition_evidence",start)
    block=cpp[start:stop]
    assert not any(word in block for word in ("homeostatic","Goal","reward","digestion","nutrient","hydration"))


def test_internal_observation_uses_owned_sensor_boundary_without_action_or_neural_injection():
    tree=ast.parse((ROOT/'simulation/continuous.py').read_text(encoding='utf-8'))
    functions={node.name:node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}
    for name in ('_schedule_internal_change','_observe_internal_change'):
        attributes={node.attr for node in ast.walk(functions[name]) if isinstance(node,ast.Attribute)}
        assert 'sample_internal_frame' in attributes
        assert not attributes & {'physiology','world','rng','advance_to','apply_intent','transduce',
                                 'neural_sensory','commit_continuous_action','begin_continuous_observation'}
    scheduling=functions['_schedule_internal_change']
    assert any(isinstance(node,ast.Compare) and isinstance(node.left,ast.Attribute)
               and node.left.attr=='levels' for node in ast.walk(scheduling))
    core=ast.parse((ROOT/'consciousness/core.py').read_text(encoding='utf-8'))
    observation=next(node for node in ast.walk(core) if isinstance(node,ast.FunctionDef)
                     and node.name=='observe_passive_internal')
    calls={node.func.attr for node in ast.walk(observation) if isinstance(node,ast.Call)
           and isinstance(node.func,ast.Attribute)}
    assert '_observe' in calls
    assert not calls & {'commit_continuous_action','_choose_action','transduce'}


def test_temporal_merge_and_passive_action_contract_are_generic():
    from world import ActionType
    assert all(0 < action.value <= 255 for action in ActionType)
    tree=ast.parse((ROOT/'consciousness/temporal_prediction.py').read_text(encoding='utf-8'))
    merge=next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)
               and node.name=='merge_projected_state')
    attributes={node.attr for node in ast.walk(merge) if isinstance(node,ast.Attribute)}
    assert not attributes & {'physiology','world','energy','nutrients','hydration','IDLE','INTERACT_UP'}
    tree=ast.parse((ROOT/'consciousness/core_learning.py').read_text(encoding='utf-8'))
    acquisition=next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)
                     and node.name=='_acquire_timed_transition')
    assert not any(isinstance(node,ast.Constant) and node.value=='IDLE' for node in ast.walk(acquisition))
    assert not any(module.startswith(('physiology','simulation')) for module in _imports(ROOT/'consciousness/core_learning.py'))


def test_brain_backend_check_precedes_snapshot_activation():
    tree=ast.parse((ROOT/'simulation/simulation.py').read_text(encoding='utf-8'))
    load=next(node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef) and node.name=='load_brain')
    guard=next(node for node in ast.walk(load) if isinstance(node,ast.If)
               and 'saved_backend' in ast.unparse(node.test))
    assert any(isinstance(node,ast.Raise) for node in ast.walk(guard))
    assert all(guard.lineno < node.lineno for node in ast.walk(load) if isinstance(node,ast.Call)
               and isinstance(node.func,ast.Attribute) and node.func.attr in {'snapshot_data','load','load_graph'})


def test_scenario_dependencies_are_directional_and_metadata_not_policy():
    for path in (ROOT/'consciousness').rglob('*.py'):
        assert not any(name.startswith(('simulation.scenario','experiments.scenario_runner')) for name in _imports(path))
    for path in (ROOT/'simulation/scenario.py', ROOT/'experiments/scenario_runner.py'):
        assert not any(name.startswith(('ui','pygame','imgui','OpenGL','se.observer')) for name in _imports(path))
    source=(ROOT/'simulation/scenario.py').read_text(encoding='utf-8')
    assert 'SCENARIO_SETTING_NAMES' not in source
    assert 'scenario_configuration' in source and 'restore_scenario_settings' in source
    tree=ast.parse(source)
    export=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='export_scenario')
    attrs={n.attr for n in ast.walk(export) if isinstance(n,ast.Attribute)}
    assert not attrs & {'schedule','next','advance_to','apply_action','record_action_outcome','load_brain','run_until','inject_utterance'}


def test_native_error_ownership_and_host_export_boundary():
    dialogue=(ROOT/'cpp/src/workbench_dialogue_view.cpp').read_text(encoding='utf-8')
    world=(ROOT/'cpp/src/workbench_world_view.cpp').read_text(encoding='utf-8')
    assert 'workbench_notice' not in dialogue and 'dialogue_error' not in world
    assert 'input_error' not in (ROOT/'cpp/include/se/workbench_ui.hpp').read_text(encoding='utf-8')
    from simulation.workbench import CAUSAL_COMMANDS
    assert 'EXPORT_SCENARIO' not in CAUSAL_COMMANDS


def test_research_protocol_and_metrics_never_enter_runtime_policy():
    for folder in ("consciousness", "simulation", "world", "physiology"):
        if not (ROOT/folder).exists():continue
        for path in (ROOT/folder).rglob("*.py"):
            assert not any(name.startswith("experiments") for name in _imports(path)), str(path)
    for name in ("planning.py", "choice.py", "valuation.py", "core_learning.py"):
        source=(ROOT/"consciousness"/name).read_text(encoding="utf-8")
        assert not any(token in source for token in ("securriculum", "censored_time", "energy_spent", "EXPERIENCED_FULL", "paired_win"))


def test_v093a_diagnostics_have_no_cognitive_write_or_policy_path():
    forbidden={"_schedule_action","apply_action","apply_intent","set_body_state",
        "record_action_outcome","add_cognit","connect","accept_sensation",
        "schedule","receive","set_cognit_fields","restore_transition_history"}
    for path in (ROOT/"experiments/v093a").glob("*.py"):
        tree=ast.parse(path.read_text(encoding="utf-8"))
        assert not [n for n in ast.walk(tree) if isinstance(n,ast.Call)
            and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden],str(path)
    for folder in ("consciousness","simulation","world","physiology"):
        for path in (ROOT/folder).glob("*.py"):
            assert not any(name.startswith("experiments.v093a") for name in _imports(path))
    source=(ROOT/"consciousness/planning.py").read_text(encoding="utf-8")
    assert "=observer." not in source and "= observer." not in source
    assert "diagnostic_observer" not in (ROOT/"consciousness/graph.py").read_text(encoding="utf-8")
