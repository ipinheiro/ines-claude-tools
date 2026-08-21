"""Command hook helper.

This script intentionally exits with an error and prints guidance when users invoke
the wrong command.

In this repo we prefer Python tooling via `uv` (managed interpreters, dependency
management, and running project tools) over ad-hoc system Python usage.
"""

import sys
from typing import Literal, TypedDict


class FgColours(TypedDict):
    blue: str
    white: str


class BgColours(TypedDict):
    red: str


class Colours(TypedDict):
    reset: str
    bright: str
    fg: FgColours
    bg: BgColours


colours: Colours = {
    "reset": "\x1b[0m",
    "bright": "\x1b[1m",
    "fg": {
        "blue": "\x1b[34m",
        "white": "\x1b[37m",
    },
    "bg": {
        "red": "\x1b[41m",
    },
}


def print_with_bg(bg: Literal["red"], text: str, *, fg: str = "") -> None:
    """Print a line with a background colour, optional foreground colour, then reset."""

    print(colours["bg"][bg] + fg + text + colours["reset"])


def print_bg_banner(bg: Literal["red"], text: str, *, fg: str) -> None:
    """Print a 3-line banner: padding line, text line, padding line."""

    padding = " " * len(text)
    print_with_bg(bg, padding)
    print_with_bg(bg, text, fg=fg)
    print_with_bg(bg, padding)


print()
msg = (
    "                This is not the python command you are looking for                "
)
print_bg_banner("red", msg, fg=colours["fg"]["white"])

print()
print(
    f"To run Python from the command line, {colours['fg']['blue']}python{colours['reset']}, either:\n"
)
print(
    f"- Use {colours['bright']}uv python install{colours['reset']} to install a managed Python runtime"
)
print(
    f"- Use {colours['bright']}uv run{colours['reset']} to execute tools from your project environment"
)
print(
    f"- Use {colours['bright']}uv add{colours['reset']} to add dependencies instead of pip install"
)

sys.exit(1)
