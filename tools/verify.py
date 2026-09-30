"""Portable, offline project verification entrypoint."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def verification_commands(mode: str, *, build_configured: bool, windows: bool, build_dir: str = "cpp/build", observer_source: str | None = None) -> list[list[str]]:
    """Return the ordered commands for the selected verification contract."""
    python = sys.executable
    tests = [python, "-B", "-m", "pytest", "-q"]
    if mode == "fast":
        tests += ["tests/test_main_entrypoint.py", "tests/test_architecture_boundaries.py", "tests/test_verify_tool.py"]
<<<<<<< HEAD
    smokes = [
        [python, "-B", "-c", "import main"],
        [python, "-B", "main.py", "--headless", "--seconds", "0"],
        tests,
    ]
    commands = [] if mode == "full" else smokes
=======
    commands: list[list[str]] = []
>>>>>>> ccb06e20407de836efa0483a9017f417bb41a9d9
    if not build_configured:
        configure = ["cmake", "-S", "cpp", "-B", build_dir]
        if windows:
            configure += ["-A", "x64"]
        if mode == "full":
            configure += ["-DSE_BUILD_OBSERVER=ON"]
            if observer_source:
                configure += [f"-DFETCHCONTENT_SOURCE_DIR_SDL3={observer_source}"]
        commands.append(configure)
<<<<<<< HEAD
    commands.append(["cmake", "--build", build_dir, "--config", "Release"])
    if mode == "full":commands.extend(smokes)
    commands.append(["ctest", "--test-dir", build_dir, "-C", "Release", "--output-on-failure"])
=======
    commands += [
        ["cmake", "--build", "cpp/build", "--config", "Release"],
        ["ctest", "--test-dir", "cpp/build", "-C", "Release", "--output-on-failure"],
        [python, "-B", "-c", "import main"],
        [python, "-B", "main.py", "--headless", "--seconds", "0"],
        tests,
    ]
>>>>>>> ccb06e20407de836efa0483a9017f417bb41a9d9
    return commands


def run(mode: str, root: Path = ROOT) -> int:
    """Run in repository-root context and stop at the first failed command."""
    build_dir = "cpp/build"
    cache = root / build_dir / "CMakeCache.txt"
    if cache.is_file():
        expected = f"CMAKE_HOME_DIRECTORY:INTERNAL={str((root / 'cpp').resolve()).replace(chr(92), '/')}"
        if expected.lower() not in cache.read_text(encoding="utf-8", errors="replace").replace(chr(92), '/').lower():
            build_dir = "cpp/build-verify"
            cache = root / build_dir / "CMakeCache.txt"
    if mode == "full" and cache.is_file() and "SE_BUILD_OBSERVER:BOOL=ON" not in cache.read_text(encoding="utf-8", errors="replace"):
        build_dir = "cpp/build-verify"
        cache = root / build_dir / "CMakeCache.txt"
    configured = cache.is_file()
    observer_source = root / "cpp" / "build" / "_deps" / "sdl3-src"
    commands = verification_commands(mode, build_configured=configured, windows=os.name == "nt", build_dir=build_dir, observer_source=str(observer_source) if observer_source.is_dir() else None)
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
