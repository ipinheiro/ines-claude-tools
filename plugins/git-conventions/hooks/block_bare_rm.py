#!/usr/bin/env python3
"""
Block bare rm commands on git-tracked files.

Blocks: rm <tracked-file> (single file, no glob, no recursive)
Allows: rm on untracked files, globs, directories, outside git repos

Suggests git restore (default) or git rm (if -f flag present).
"""

import json
import re
import subprocess
import sys


def parse_rm_command(command: str) -> tuple[bool, bool, str | None]:
    """Parse rm command and extract file path.

    Returns:
        (is_simple_rm, has_force_flag, file_path or None)
    """
    # Skip if not an rm command
    if not re.match(r"^\s*rm\s", command):
        return False, False, None

    # Skip recursive flags (-r, -rf, -fr, -R, etc.)
    if re.search(r"\s-[a-zA-Z]*[rR][a-zA-Z]*\s", f" {command} "):
        return False, False, None

    # Skip globs (*, ?, [...])
    if re.search(r"[*?\[\]]", command):
        return False, False, None

    # Check for force flag
    has_force = bool(re.search(r"\s-[a-zA-Z]*f[a-zA-Z]*\s", f" {command} "))

    # Extract file path - match rm with optional flags then the file
    # Pattern: rm [-flags]... <filepath>
    match = re.match(r"^\s*rm(?:\s+-[a-zA-Z]+)*\s+([^\s;|&]+)", command)
    if not match:
        return False, False, None

    file_path = match.group(1)

    # Skip if it looks like a flag we missed
    if file_path.startswith("-"):
        return False, False, None

    return True, has_force, file_path


def is_in_git_repo() -> bool:
    """Check if current directory is in a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def is_file_tracked(file_path: str) -> bool:
    """Check if file is tracked by git."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", file_path],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def main() -> None:
    """Main hook function."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # Allow on parse error

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Parse the rm command
    is_simple_rm, has_force, file_path = parse_rm_command(command)

    if not is_simple_rm or file_path is None:
        sys.exit(0)  # Allow non-simple rm commands

    # Check if in git repo
    if not is_in_git_repo():
        sys.exit(0)  # Allow outside git repos

    # Check if file is tracked
    if not is_file_tracked(file_path):
        sys.exit(0)  # Allow untracked files

    # Block with context-aware suggestion
    if has_force:
        # -f flag suggests intent to delete
        message = (
            f"Blocked: '{file_path}' is tracked by git.\n\n"
            f"To remove from repository: git rm {file_path}\n"
            f"To discard local changes:  git restore {file_path}"
        )
    else:
        # Default: suggest restore (most common case is undoing changes)
        message = (
            f"Blocked: '{file_path}' is tracked by git.\n\n"
            f"To discard local changes:  git restore {file_path}\n"
            f"To remove from repository: git rm {file_path}"
        )

    print(message, file=sys.stderr)
    sys.exit(2)  # Block


if __name__ == "__main__":
    main()
