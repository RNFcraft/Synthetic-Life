"""Portable, offline project verification entrypoint."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def verification_commands(mode: str, *, build_configured: bool, windows: bool) -> list[list[str]]:
    """Return the ordered commands for the selected verification contract."""
    python = sys.executable
    tests = [python, "-B", "-m", "pytest", "-q"]
    if mode == "fast":
        tests += ["tests/test_main_entrypoint.py", "tests/test_architecture_boundaries.py", "tests/test_verify_tool.py"]
    commands = [
        [python, "-B", "-c", "import main"],
        [python, "-B", "main.py", "--headless", "--seconds", "0"],
        tests,
    ]
    if not build_configured:
        configure = ["cmake", "-S", "cpp", "-B", "cpp/build"]
        if windows:
            configure += ["-A", "x64"]
        commands.append(configure)
    commands += [
        ["cmake", "--build", "cpp/build", "--config", "Release"],
        ["ctest", "--test-dir", "cpp/build", "-C", "Release", "--output-on-failure"],
    ]
    return commands


def run(mode: str, root: Path = ROOT) -> int:
    """Run in repository-root context and stop at the first failed command."""
    configured = (root / "cpp" / "build" / "CMakeCache.txt").is_file()
    commands = verification_commands(mode, build_configured=configured, windows=os.name == "nt")
    for index, command in enumerate(commands, 1):
        print(f"[{index}/{len(commands)}] {subprocess.list2cmdline(command)}", flush=True)
        try:
            result = subprocess.run(command, cwd=root, check=False)
        except FileNotFoundError as error:
            print(f"verification prerequisite missing: {error.filename}", file=sys.stderr)
            return 127
        if result.returncode:
            print(f"verification failed ({result.returncode}): {subprocess.list2cmdline(command)}", file=sys.stderr)
            return result.returncode
    print(f"verification PASS ({mode})")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--fast", action="store_true", help="smokes, boundary/tooling tests, Release build and CTest (default)")
    modes.add_argument("--full", action="store_true", help="smokes, complete pytest suite, Release build and CTest")
    args = parser.parse_args(argv)
    args.mode = "full" if args.full else "fast"
    return args


if __name__ == "__main__":
    raise SystemExit(run(parse_args().mode))
