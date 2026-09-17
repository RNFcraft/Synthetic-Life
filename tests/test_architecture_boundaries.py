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
