from pathlib import Path
from types import SimpleNamespace

import tools.verify as verify


def test_default_and_explicit_modes():
    assert verify.parse_args([]).mode == "fast"
    assert verify.parse_args(["--fast"]).mode == "fast"
    assert verify.parse_args(["--full"]).mode == "full"


def test_fast_and_full_select_expected_python_scope():
    fast = verify.verification_commands("fast", build_configured=True, windows=True)
    full = verify.verification_commands("full", build_configured=True, windows=True)
    fast_pytest = next(cmd for cmd in fast if "-m" in cmd and "pytest" in cmd)
    full_pytest = next(cmd for cmd in full if "-m" in cmd and "pytest" in cmd)
    assert "tests/test_architecture_boundaries.py" in fast_pytest
    assert full_pytest[-3:] == ["-m", "pytest", "-q"]
    assert "tests/test_architecture_boundaries.py" not in full_pytest


def test_unconfigured_windows_build_gets_portable_configure_step():
    commands = verify.verification_commands("fast", build_configured=False, windows=True)
    assert ["cmake", "-S", "cpp", "-B", "cpp/build", "-A", "x64"] in commands


def test_runner_propagates_first_failure(monkeypatch, tmp_path: Path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=9)

    monkeypatch.setattr(verify.subprocess, "run", fake_run)
    assert verify.run("fast", tmp_path) == 9
    assert len(calls) == 1


def test_stale_cmake_cache_uses_isolated_build_directory(monkeypatch, tmp_path: Path):
    cache=tmp_path / "cpp" / "build" / "CMakeCache.txt"
    cache.parent.mkdir(parents=True)
    cache.write_text("CMAKE_HOME_DIRECTORY:INTERNAL=D:/old/workspace/cpp",encoding="utf-8")
    calls=[]
    def fake_run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(verify.subprocess,"run",fake_run)
    assert verify.run("fast",tmp_path)==0
    assert ["cmake","-S","cpp","-B","cpp/build-verify","-A","x64"] in calls if verify.os.name=="nt" else ["cmake","-S","cpp","-B","cpp/build-verify"] in calls
