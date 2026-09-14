"""File selection for the pre-staging lint hook.

The selected files are passed to `ruff check --fix`, which rewrites them in
place. Passing a path explicitly overrides ruff's own exclusions, so anything
this function returns will be modified. Vendored code must never appear.
"""

import io
import json
import subprocess
from pathlib import Path
from types import ModuleType

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

VENDORED_DIRS = [
    ".venv/lib/site-packages",
    "venv/lib/site-packages",
    "node_modules/pkg",
    "build/lib",
    "dist",
    "__pycache__",
]

PATH_SEGMENT = st.from_regex(r"[a-z][a-z0-9_]{0,7}", fullmatch=True)


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


def test_explicitly_named_source_file_is_selected(
    ruff_guard: ModuleType, project: Path
) -> None:
    source = project / "src" / "app.py"

    assert ruff_guard.get_python_files([str(source)]) == [source]


def test_explicitly_named_vendored_file_is_refused(
    ruff_guard: ModuleType, project: Path
) -> None:
    """Naming it directly must not be an escape hatch."""
    vendored = project / ".venv/lib/site-packages/vendored.py"

    assert ruff_guard.get_python_files([str(vendored)]) == []


def test_flags_are_not_treated_as_paths(
    ruff_guard: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A directory literally named like a flag must not be expanded."""
    monkeypatch.chdir(tmp_path)
    trap = tmp_path / "-v" / "trap.py"
    trap.parent.mkdir()
    trap.write_text("")

    assert ruff_guard.get_python_files(["-v", "--verbose"]) == []


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


@pytest.mark.parametrize(
    "path",
    [
        "src/app.py",
        "tests/test_app.py",
        "app.py",
        # Excluded names as substrings of a component must not match.
        "distribution/app.py",
        "builder/lib.py",
        "myvenv/tool.py",
    ],
)
def test_ordinary_source_paths_are_not_excluded(
    ruff_guard: ModuleType, path: str
) -> None:
    assert ruff_guard.is_excluded(Path(path)) is False


@given(
    parts=st.lists(PATH_SEGMENT, min_size=1, max_size=5),
    position=st.integers(min_value=0, max_value=5),
    which=st.integers(min_value=0, max_value=20),
)
def test_any_path_through_an_excluded_directory_is_excluded(
    ruff_guard: ModuleType, parts: list[str], position: int, which: int
) -> None:
    excluded_dirs = sorted(ruff_guard.EXCLUDED_DIRS)
    assume(not any(part in excluded_dirs for part in parts))
    cut = position % (len(parts) + 1)
    excluded = excluded_dirs[which % len(excluded_dirs)]

    clean = Path(*parts, "mod.py")
    dirty = Path(*parts[:cut], excluded, *parts[cut:], "mod.py")

    assert ruff_guard.is_excluded(clean) is False
    assert ruff_guard.is_excluded(dirty) is True


def test_broad_add_selects_changed_python_files_git_knows_about(
    ruff_guard: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Renames resolve to the new name, quoted paths are unquoted, vendored and non-Python files drop."""
    monkeypatch.chdir(tmp_path)
    for name in [
        "src/app.py",
        "src/new.py",
        "with space.py",
        ".venv/lib/vendored.py",
        "README.md",
    ]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")
    porcelain = (
        " M src/app.py\n"
        "R  old.py -> src/new.py\n"
        '?? "with space.py"\n'
        " M .venv/lib/vendored.py\n"
        " M README.md\n"
    )

    def fake_git(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 0, stdout=porcelain, stderr="")

    monkeypatch.setattr(ruff_guard.subprocess, "run", fake_git)

    assert ruff_guard.get_staged_python_files() == [
        Path("src/app.py"),
        Path("src/new.py"),
        Path("with space.py"),
    ]


@pytest.mark.parametrize(
    ("command", "selector"),
    [
        ("git add -A", "get_staged_python_files"),
        ("git add .", "get_staged_python_files"),
        ("git add", "get_staged_python_files"),
        ("git add src/app.py", "get_python_files"),
    ],
)
def test_git_add_routes_to_the_matching_selector(
    ruff_guard: ModuleType, monkeypatch: pytest.MonkeyPatch, command: str, selector: str
) -> None:
    """Broad adds resolve against git's view of the tree, explicit adds against the filesystem."""
    calls: list[str] = []

    def staged() -> list[Path]:
        calls.append("get_staged_python_files")
        return []

    def explicit(args: list[str]) -> list[Path]:
        calls.append("get_python_files")
        return []

    monkeypatch.setattr(ruff_guard, "get_staged_python_files", staged)
    monkeypatch.setattr(ruff_guard, "get_python_files", explicit)
    hook_input = json.dumps({"tool_input": {"command": command}})
    monkeypatch.setattr(ruff_guard.sys, "stdin", io.StringIO(hook_input))

    assert ruff_guard.main() == 0
    assert calls == [selector]
