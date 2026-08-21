#!/usr/bin/env python3
"""
Validate git commit messages follow conventional commit format.

Format: <type>(<scope>): <subject>

Types: feat, fix, refactor, chore, docs, test, perf
"""

import json
import re
import sys

# Valid commit types from the git-conventions skill
VALID_TYPES = ["feat", "fix", "refactor", "chore", "docs", "test", "perf"]

# Pattern: type(scope): subject
# - type: one of VALID_TYPES
# - scope: required, alphanumeric with hyphens/underscores
# - subject: starts with capital or lowercase letter
COMMIT_PATTERN = re.compile(
    r"^(" + "|".join(VALID_TYPES) + r")"  # type
    r"\([a-zA-Z0-9_-]+\)"  # (scope) - required
    r": "  # colon and space
    r"[A-Za-z]"  # subject starts with letter
)


def extract_commit_message(command: str) -> str | None:
    """Extract the commit message from a git commit command."""
    # Match: git commit -m "message" or git commit -m 'message'
    # Also handles: git commit -m "$(cat <<'EOF' ... EOF )"

    # Heredoc style: -m "$(cat <<'EOF'\nmessage\nEOF\n)"
    # The newlines may be literal \n or actual newlines
    heredoc_match = re.search(
        r'-m\s+"\$\(cat\s+<<[\'"]?EOF[\'"]?\s*[\n\\n]+([^\\]+?)(?:\\n|$)',
        command,
    )
    if heredoc_match:
        # Get first line of heredoc (the subject line)
        first_line = heredoc_match.group(1).split("\\n")[0].split("\n")[0]
        return first_line.strip()

    # Simple -m "message" or -m 'message'
    simple_match = re.search(r'-m\s+["\']([^"\']+)["\']', command)
    if simple_match:
        return simple_match.group(1).strip()

    return None


def validate_commit_message(message: str) -> tuple[bool, str]:
    """Validate a commit message. Returns (is_valid, error_message)."""
    # Get first line (subject)
    subject = message.split("\n")[0].strip()

    if not subject:
        return False, "Commit message is empty"

    if not COMMIT_PATTERN.match(subject):
        # Provide helpful feedback
        if not any(subject.startswith(t) for t in VALID_TYPES):
            return False, (
                f"Commit must start with a type: {', '.join(VALID_TYPES)}\n"
                f"Got: {subject[:50]}..."
            )

        if "(" not in subject or ")" not in subject:
            return False, (
                "Commit must include a scope in parentheses: type(scope): subject\n"
                f"Got: {subject[:50]}..."
            )

        if ": " not in subject:
            return False, (
                "Commit must have ': ' after the scope: type(scope): subject\n"
                f"Got: {subject[:50]}..."
            )

        return False, (
            "Commit message format: type(scope): subject\n"
            f"Types: {', '.join(VALID_TYPES)}\n"
            f"Got: {subject[:50]}..."
        )

    # Check subject length (50 chars recommended)
    # Extract just the subject part after "type(scope): "
    subject_text = re.sub(r"^[a-z]+\([^)]+\):\s*", "", subject)
    if len(subject_text) > 50:
        return False, (
            f"Subject line too long ({len(subject_text)} chars). "
            "Keep it under 50 characters.\n"
            f"Subject: {subject_text[:50]}..."
        )

    return True, ""


def print_error(message: str) -> None:
    """Print error with formatting."""
    red_bg = "\x1b[41m"
    white_fg = "\x1b[37m"
    reset = "\x1b[0m"

    print(file=sys.stderr)
    header = "  Invalid commit message format  "
    padding = " " * len(header)
    print(f"{red_bg}{padding}{reset}", file=sys.stderr)
    print(f"{red_bg}{white_fg}{header}{reset}", file=sys.stderr)
    print(f"{red_bg}{padding}{reset}", file=sys.stderr)
    print(file=sys.stderr)
    print(message, file=sys.stderr)
    print(file=sys.stderr)
    print("Expected format: type(scope): subject", file=sys.stderr)
    print(f"Valid types: {', '.join(VALID_TYPES)}", file=sys.stderr)
    print(file=sys.stderr)
    print("Examples:", file=sys.stderr)
    print("  feat(auth): Add OAuth2 login flow", file=sys.stderr)
    print("  fix(api): Handle null response from endpoint", file=sys.stderr)
    print("  docs(readme): Update installation instructions", file=sys.stderr)
    print(file=sys.stderr)


def main() -> int:
    """Main hook function."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Allow on parse error

    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        return 0

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only check git commit commands
    if "git commit" not in command or "-m" not in command:
        return 0

    # Skip if --amend without -m (uses previous message)
    if "--amend" in command and "-m" not in command:
        return 0

    commit_message = extract_commit_message(command)
    if not commit_message:
        # Couldn't parse message, let it through
        return 0

    is_valid, error = validate_commit_message(commit_message)
    if not is_valid:
        print_error(error)
        return 2  # Block

    return 0  # Allow


if __name__ == "__main__":
    sys.exit(main())
