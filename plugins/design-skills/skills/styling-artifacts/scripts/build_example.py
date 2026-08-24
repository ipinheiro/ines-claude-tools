# /// script
# requires-python = ">=3.10"
# dependencies = ["typer"]
# ///
"""Build example.html from the skill's CSS and snippet files.

The showcase page and the files a session pastes into a new artifact must
never drift, so the page is assembled from them rather than maintained by
hand. Run from anywhere:

    uv run plugins/design-skills/skills/styling-artifacts/scripts/build_example.py
    uv run .../build_example.py --artifact out.html   # body-only copy for the Artifact tool
"""

from pathlib import Path

import typer

SKILL_DIR = Path(__file__).resolve().parent.parent
SRC = SKILL_DIR / "scripts" / "example.src.html"
OUT = SKILL_DIR / "example.html"

app = typer.Typer(add_completion=False)


def split_toggle(snippet: str) -> tuple[str, str]:
    """Split theme-toggle.html into its button markup and its script."""
    button, script = snippet.split("<script>", 1)
    return button.strip(), "<script>" + script.strip()


def assemble() -> str:
    """Fill the template's markers from the sibling files."""
    template = SRC.read_text()
    button, script = split_toggle((SKILL_DIR / "theme-toggle.html").read_text())
    replacements = {
        "<!-- @head.html -->": (SKILL_DIR / "head.html").read_text().strip(),
        "/* @tokens.css */": (SKILL_DIR / "tokens.css").read_text().strip(),
        "/* @components.css */": (SKILL_DIR / "components.css").read_text().strip(),
        "<!-- @theme-toggle.button -->": button,
        "<!-- @theme-toggle.script -->": script,
    }
    for marker, content in replacements.items():
        if marker not in template:
            raise ValueError(f"marker missing from template: {marker}")
        template = template.replace(marker, content)
    return template


def body_only(document: str) -> str:
    """Strip the document wrapper so the Artifact tool can add its own.

    Keeps the title, the head snippet, the stylesheet and the body contents.
    """
    head = document.split("<head>", 1)[1].split("</head>", 1)[0]
    body = document.split("<body>", 1)[1].rsplit("</body>", 1)[0]
    title_start = head.index("<title>")
    title_end = head.index("</title>") + len("</title>")
    title = head[title_start:title_end]
    after_title = head[title_end:]
    return f"{title}\n{after_title.strip()}\n{body.strip()}\n"


@app.command()
def main(
    artifact: Path | None = typer.Option(
        None, help="Also write a body-only copy to this path for the Artifact tool."
    ),
) -> None:
    """Write example.html next to the skill, and optionally an artifact copy."""
    document = assemble()
    OUT.write_text(document)
    typer.echo(f"wrote {OUT} ({len(document):,} bytes)")
    if artifact is None:
        return
    artifact.write_text(body_only(document))
    typer.echo(f"wrote {artifact}")


if __name__ == "__main__":
    app()
