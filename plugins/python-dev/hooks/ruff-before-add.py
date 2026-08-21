#!/usr/bin/env python3
"""Pre-git-add hook that runs ruff and ast-grep on Python files being staged.

Workflow:
1. Intercept `git add` commands
2. Run `ruff check --fix` to auto-fix what it can
3. Run `ast-grep` to catch inline imports inside functions
4. If unfixable issues remain, block and tell Claude to fix them
5. Claude fixes, then re-runs git add (which triggers this hook again)
6. Once clean, the add proceeds

Exit codes:
- 0: All good, proceed with git add
- 2: Block the command, Claude needs to fix issues
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Get the directory where this script lives (for finding rule files)
SCRIPT_DIR = Path(__file__).parent


# Directories never worth linting. Ruff excludes these by default, but passing a
# file explicitly on the command line overrides that exclusion, so a vendored
# file swept up by rglob would be rewritten in place.
EXCLUDED_DIRS = frozenset(
    {
        ".venv",
        "venv",
        ".git",
        ".tox",
        ".nox",
        "node_modules",
        "__pycache__",
        "site-packages",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "build",
        "dist",
    }
)


def is_excluded(path: Path) -> bool:
    """True if any component of the path is a directory we never lint."""
    return any(part in EXCLUDED_DIRS for part in path.parts)


def get_staged_python_files() -> list[Path]:
    """Python files git reports as changed, for broad adds like 'git add .'."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if len(line) <= 3:
            continue
        filepath = line[3:].strip()
        # Renames are reported as "old -> new"
        if " -> " in filepath:
            filepath = filepath.split(" -> ")[1]
        # Paths containing spaces are quoted by git
        filepath = filepath.strip('"')
        path = Path(filepath)
        if path.suffix == ".py" and path.exists() and not is_excluded(path):
            files.append(path)
    return files


def get_python_files(args: list[str]) -> list[Path]:
    """Extract Python files from git add arguments."""
    files: list[Path] = []

    for arg in args:
        # Skip flags
        if arg.startswith("-"):
            continue

        path = Path(arg)

        if path.suffix == ".py" and path.exists() and not is_excluded(path):
            files.append(path)
        elif path.is_dir():
            # Expand directory to Python files
            files.extend(p for p in path.rglob("*.py") if not is_excluded(p))

    return files


# Rules to enforce:
# E402 - Module level import not at top of file (the main one we want!)
# F401 - Unused imports
# F841 - Unused variables
# I001 - Import sorting
RUFF_RULES = ["E402", "F401", "F841", "I001"]


def run_ruff_fix(files: list[Path]) -> tuple[bool, str]:
    """Run ruff check --fix on files. Returns (success, output)."""
    if not files:
        return True, ""

    result = subprocess.run(
        [
            "ruff",
            "check",
            "--fix",
            "--select",
            ",".join(RUFF_RULES),
            *[str(f) for f in files],
        ],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0, result.stdout + result.stderr


def run_ruff_check(files: list[Path]) -> tuple[bool, str]:
    """Run ruff check (no fix) to see remaining issues. Returns (clean, output)."""
    if not files:
        return True, ""

    result = subprocess.run(
        ["ruff", "check", "--select", ",".join(RUFF_RULES), *[str(f) for f in files]],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0, result.stdout + result.stderr


def find_ast_grep() -> str | None:
    """Find ast-grep binary. Returns path or None if not found."""
    # Check ~/.local/bin first (uv tool install location)
    local_bin = os.path.expanduser("~/.local/bin/ast-grep")
    if os.path.exists(local_bin):
        return local_bin

    # Try system path
    try:
        subprocess.run(["ast-grep", "--version"], capture_output=True, check=True)
        return "ast-grep"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def run_ast_grep_check(files: list[Path]) -> tuple[bool, str, bool]:
    """Run ast-grep to catch inline imports inside functions.

    Returns (clean, output, ast_grep_available).
    """
    if not files:
        return True, "", True

    rule_file = SCRIPT_DIR / "no-inline-imports.yml"
    if not rule_file.exists():
        return True, "", True  # Skip if rule file missing

    ast_grep = find_ast_grep()
    if ast_grep is None:
        return True, "", False  # Not installed

    result = subprocess.run(
        [ast_grep, "scan", "--rule", str(rule_file), *[str(f) for f in files]],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout + result.stderr, True


def print_banner(text: str) -> None:
    """Print a warning banner."""
    red_bg = "\x1b[41m"
    white_fg = "\x1b[37m"
    reset = "\x1b[0m"

    padding = " " * len(text)
    print(f"{red_bg}{padding}{reset}", file=sys.stderr)
    print(f"{red_bg}{white_fg}{text}{reset}", file=sys.stderr)
    print(f"{red_bg}{padding}{reset}", file=sys.stderr)


def main() -> int:
    # Read tool input from stdin (passed by Claude Code hook system)
    try:
        hook_input = json.load(sys.stdin)
        command = hook_input.get("tool_input", {}).get("command", "")
    except (json.JSONDecodeError, KeyError):
        return 0  # Not a valid hook input, let it pass

    # Only intercept git add commands
    if not command.strip().startswith("git add"):
        return 0

    # Parse out the arguments after "git add"
    parts = command.strip().split()
    args = parts[2:]

    # Bare "git add", or a broad add such as "git add .", "-A", "--all".
    # Resolve those against the working tree rather than the filesystem, so we
    # only ever touch files git already knows about.
    if not args or any(arg in (".", "-A", "--all", "-u", "--update") for arg in args):
        files = get_staged_python_files()
    else:
        files = get_python_files(args)

    if not files:
        return 0  # No Python files, nothing to check

    # Check if ruff is available
    try:
        subprocess.run(["ruff", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(file=sys.stderr)
        print_banner("  Ruff is not installed  ")
        print(file=sys.stderr)
        print("Ruff is required for Python development in this team.", file=sys.stderr)
        print(file=sys.stderr)
        print("Install it with:", file=sys.stderr)
        print("  uv tool install ruff", file=sys.stderr)
        print(file=sys.stderr)
        return 2

    # Step 1: Run ruff --fix to auto-fix what we can
    run_ruff_fix(files)

    # Step 2: Check if any ruff issues remain
    ruff_clean, ruff_output = run_ruff_check(files)

    # Step 3: Check for inline imports with ast-grep
    ast_clean, ast_output, ast_grep_available = run_ast_grep_check(files)

    if not ast_grep_available:
        print(file=sys.stderr)
        print_banner("  ast-grep is not installed  ")
        print(file=sys.stderr)
        print("ast-grep is required to check for inline imports.", file=sys.stderr)
        print(file=sys.stderr)
        print("Install it with:", file=sys.stderr)
        print("  uv tool install ast-grep-cli", file=sys.stderr)
        print(file=sys.stderr)
        return 2

    if ruff_clean and ast_clean:
        return 0

    # Issues remain that need manual fixes
    print(file=sys.stderr)

    if not ruff_clean:
        print_banner("  Ruff found issues that need manual fixes  ")
        print(file=sys.stderr)
        print(ruff_output, file=sys.stderr)

    if not ast_clean:
        print_banner("  Inline imports found inside functions  ")
        print(file=sys.stderr)
        print(ast_output, file=sys.stderr)
        print("Move all imports to the top of the file.", file=sys.stderr)

    print(file=sys.stderr)
    print("Fix these issues, then run git add again.", file=sys.stderr)
    print(file=sys.stderr)

    return 2  # Block the git add


if __name__ == "__main__":
    sys.exit(main())
