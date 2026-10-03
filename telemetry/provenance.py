"""Execution provenance for host diagnostics; never imported by cognition."""
from hashlib import sha256
import os
import platform
from pathlib import Path
import subprocess
import sys


def execution_provenance():
    root = Path(__file__).resolve().parents[1]
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.PIPE)
    diff = git('diff', '--binary', 'HEAD')
    status = git('status', '--porcelain=v1').decode('utf-8')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z').decode('utf-8').split('\0')
    deployed = next((root/'consciousness').glob('_native_brain*.pyd'), None)
    loaded = sys.modules.get('consciousness._native_brain')
    module = Path(loaded.__file__) if loaded is not None else deployed
    return dict(head=git('rev-parse', 'HEAD').decode().strip(),
                branch=git('branch', '--show-current').decode().strip(),
                working_tree_status=status, dirty=bool(status),
                tracked_diff_sha256=sha256(diff).hexdigest(),
                untracked_sha256={name:sha256((root/name).read_bytes()).hexdigest()
                                  for name in untracked if name and (root/name).is_file()},
                native_module_sha256=sha256(module.read_bytes()).hexdigest() if module else None,
                native_module_path=str(module) if module else None,
                deployed_native_module_sha256=sha256(deployed.read_bytes()).hexdigest() if deployed else None,
                python=platform.python_version(), platform=platform.platform(),
                hashseed=os.environ.get('PYTHONHASHSEED', 'random'))
