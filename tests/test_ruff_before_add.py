"""File selection for the pre-staging lint hook.

The selected files are passed to `ruff check --fix`, which rewrites them in
place. Passing a path explicitly overrides ruff's own exclusions, so anything
this function returns will be modified. Vendored code must never appear.
"""

from pathlib import Path
from types import ModuleType

import pytest

VENDORED_DIRS = [
    ".venv/lib/site-packages",
    "venv/lib/site-packages",
    "node_modules/pkg",
    "build/lib",
    "dist",
    "__pycache__",
]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A project tree holding one real source file and several vendored ones."""
    source = tmp_path / "src" / "app.py"
    source.parent.mkdir(parents=True)
    source.write_text("import os, sys\n")

    for directory in VENDORED_DIRS:
        vendored = tmp_path / directory / "vendored.py"
        vendored.parent.mkdir(parents=True, exist_ok=True)
        vendored.write_text("import os, sys\n")

    return tmp_path


def test_expanding_a_directory_finds_real_sources(
    ruff_guard: ModuleType, project: Path
) -> None:
    selected = ruff_guard.get_python_files([str(project)])

    assert [p.name for p in selected] == ["app.py"]


@pytest.mark.parametrize("directory", VENDORED_DIRS)
def test_expanding_a_directory_skips_vendored_code(
    ruff_guard: ModuleType, project: Path, directory: str
) -> None:
    selected = ruff_guard.get_python_files([str(project)])

    assert project / directory / "vendored.py" not in selected


def test_explicitly_named_vendored_file_is_refused(
    ruff_guard: ModuleType, project: Path
) -> None:
    """Naming it directly must not be an escape hatch."""
    vendored = project / ".venv/lib/site-packages/vendored.py"

    assert ruff_guard.get_python_files([str(vendored)]) == []


def test_flags_are_not_treated_as_paths(ruff_guard: ModuleType) -> None:
    assert ruff_guard.get_python_files(["-A", "--all", "-u"]) == []


def test_nonexistent_path_is_ignored(ruff_guard: ModuleType, tmp_path: Path) -> None:
    assert ruff_guard.get_python_files([str(tmp_path / "missing.py")]) == []


def test_non_python_files_are_ignored(ruff_guard: ModuleType, tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("# hello\n")

    assert ruff_guard.get_python_files([str(readme)]) == []


@pytest.mark.parametrize(
    "path",
    [
        "src/.venv/lib/app.py",
        "nested/node_modules/thing/mod.py",
        ".venv/bin/script.py",
    ],
)
def test_excluded_directory_detected_at_any_depth(
    ruff_guard: ModuleType, path: str
) -> None:
    assert ruff_guard.is_excluded(Path(path)) is True


@pytest.mark.parametrize("path", ["src/app.py", "tests/test_app.py", "app.py"])
def test_ordinary_source_paths_are_not_excluded(
    ruff_guard: ModuleType, path: str
) -> None:
    assert ruff_guard.is_excluded(Path(path)) is False
