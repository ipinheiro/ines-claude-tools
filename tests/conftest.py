"""Shared fixtures for hook tests.

Hook scripts live at plugin roots and use hyphenated filenames, so they cannot
be imported normally. Load them by path instead.
"""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_hook(relative_path: str) -> ModuleType:
    """Import a hook script by its path relative to the repo root."""
    path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(path.stem.replace("-", "_"), path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load hook at {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def git_add_guard() -> ModuleType:
    """The git-conventions hook that blocks broad `git add` commands."""
    return load_hook("plugins/git-conventions/hooks/block_broad_git_add.py")


@pytest.fixture(scope="session")
def ruff_guard() -> ModuleType:
    """The python-dev hook that lints Python files before staging."""
    return load_hook("plugins/python-dev/hooks/ruff-before-add.py")
