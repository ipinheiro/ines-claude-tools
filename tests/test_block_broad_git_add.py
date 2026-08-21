"""The broad-add guard must block real broad adds and nothing else.

A false positive here is not cosmetic: the hook exits 2, so it blocks the whole
Bash call. Mentioning a broad add inside a commit message used to be enough.
"""

from types import ModuleType

import pytest
from hypothesis import given
from hypothesis import strategies as st

# Assembled at runtime so this file's own source cannot trip the installed hook.
ADD = "git " + "add"

BROAD_COMMANDS = [
    f"{ADD} .",
    f"{ADD} -A",
    f"{ADD} --all",
    f"{ADD} . && git commit -m 'wip'",
    f"{ADD} -A; git status",
    "git -C /some/repo " + "add .",
    f"cd /tmp && {ADD} --all",
]

TARGETED_COMMANDS = [
    f"{ADD} file1.py file2.py",
    f"{ADD} src/",
    f"{ADD} 'name with spaces.py'",
    f"{ADD} --patch src/app.py",
    "git status",
    "git commit -m 'done'",
]

MENTIONS_NOT_INVOCATIONS = [
    f'git commit -m "never use {ADD} -A in this repo"',
    f"echo '{ADD} .' >> notes.md",
    f'git commit -m "$(cat <<EOF\nAvoid {ADD} .\nEOF\n)"',
    f"grep -r '{ADD} --all' docs/",
]


@pytest.mark.parametrize("command", BROAD_COMMANDS)
def test_blocks_broad_adds(git_add_guard: ModuleType, command: str) -> None:
    assert git_add_guard.is_broad_git_add(command) is True


@pytest.mark.parametrize("command", TARGETED_COMMANDS)
def test_allows_targeted_adds(git_add_guard: ModuleType, command: str) -> None:
    assert git_add_guard.is_broad_git_add(command) is False


@pytest.mark.parametrize("command", MENTIONS_NOT_INVOCATIONS)
def test_allows_broad_add_mentioned_as_text(
    git_add_guard: ModuleType, command: str
) -> None:
    """Quoted text and heredoc bodies are data, not commands."""
    assert git_add_guard.is_broad_git_add(command) is False


def test_allows_command_merely_starting_with_the_word_git(
    git_add_guard: ModuleType,
) -> None:
    assert git_add_guard.is_broad_git_add("echo git " + "add .") is False


@given(
    st.lists(
        st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_-", min_size=1).map(
            lambda stem: f"{stem}.py"
        ),
        min_size=1,
        max_size=5,
    )
)
def test_never_blocks_explicitly_named_files(
    git_add_guard: ModuleType, filenames: list[str]
) -> None:
    """Naming files explicitly is the workflow the hook exists to encourage."""
    assert git_add_guard.is_broad_git_add(f"{ADD} {' '.join(filenames)}") is False
