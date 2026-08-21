#!/usr/bin/env python3
"""
Block broad git add commands.

Blocks: git add -A, git add --all, git add .
Allows: git add <specific-files>
"""

import json
import re
import shlex
import sys

BROAD_ARGS = frozenset({".", "-A", "--all"})

# Tokens that end one command and begin another, so the next word is a command name.
SEPARATORS = frozenset({";", "&&", "||", "|", "&", "(", ")", "{", "}"})

# A heredoc and its body: <<EOF ... EOF, <<-'EOF' ... EOF, etc.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1.*?^\s*\2\s*$", re.DOTALL | re.MULTILINE)


def is_broad_git_add(command: str) -> bool:
    """True if the command actually runs a broad `git add`.

    Matches only at command position, so a mention inside a commit message,
    a heredoc, or any other quoted string is not a match.
    """
    # Heredoc bodies are data, not commands.
    cleaned = HEREDOC.sub(" ", command)

    try:
        # shlex keeps quoted strings as single tokens, so "git add -A" inside a
        # -m message never looks like two adjacent words. punctuation_chars
        # splits shell operators off, so `-A;` tokenises as `-A` then `;`.
        lexer = shlex.shlex(cleaned, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        # Unbalanced quotes. Fall back to a naive split rather than crash; a
        # false positive here is safer than letting a broad add through.
        tokens = cleaned.split()

    for i, token in enumerate(tokens):
        if token != "git":
            continue
        if i > 0 and tokens[i - 1] not in SEPARATORS:
            continue  # not at command position, e.g. `echo git add .`

        # Skip git's own options and their values, e.g. `git -C path add .`
        j = i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            j += 2 if tokens[j] in ("-C", "-c", "--git-dir", "--work-tree") else 1

        if j < len(tokens) and tokens[j] == "add":
            if any(arg in BROAD_ARGS for arg in tokens[j + 1 :]):
                return True

    return False


def main():
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

    if is_broad_git_add(command):
        message = (
            "Blocked: Use targeted git adds instead of 'git add -A', 'git add --all', or 'git add .'.\n"
            "Specify files explicitly: git add <file1> <file2> ...\n"
            "See the git-conventions skill for commit workflow guidance."
        )
        print(message, file=sys.stderr)
        sys.exit(2)  # Block

    sys.exit(0)  # Allow


if __name__ == "__main__":
    main()
