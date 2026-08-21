#!/usr/bin/env python3
"""UserPromptSubmit hook to detect context and remind Claude to load relevant skills.

Scans user prompts for:
- File patterns (pyproject.toml, conftest.py, etc.)
- Keywords (dbt, dagster, pytest, etc.)
- Code review requests

Injects system reminders to load appropriate skills.
"""

import json
import re
import sys
from dataclasses import dataclass


@dataclass
class SkillTrigger:
    """A skill that should be loaded based on patterns."""

    skill_name: str
    plugin: str
    patterns: list[str]
    description: str


# Skills and their trigger patterns
SKILL_TRIGGERS = [
    SkillTrigger(
        skill_name="uv-pyproject",
        plugin="python-dev",
        patterns=[
            r"pyproject\.toml",
            r"\buv\s+(sync|add|lock|build)",
            r"\bworkspace\b.*\b(member|root)\b",
            r"\bdependency.?(group|version)",
            r"\bbuild.?backend\b",
            r"\bhatchling\b",
            r"\bversion\s+floor",
            r"\[tool\.uv",
            r"\[build-system\]",
        ],
        description="pyproject.toml configuration, uv workspaces, dependency management",
    ),
    SkillTrigger(
        skill_name="dbt-python-integration",
        plugin="python-dev",
        patterns=[
            r"\bdbt\b",
            r"dbtRunner",
            r"manifest\.json",
            r"run_results\.json",
            r"dbt\s+(run|build|test|compile)",
            r"dbt_project\.yml",
        ],
        description="dbt integration with Python",
    ),
    SkillTrigger(
        skill_name="python-test-quality",
        plugin="python-dev",
        patterns=[
            r"\bpytest\b",
            r"\bconftest\.py\b",
            r"\bfixture\b",
            r"\bhypothesis\b",
            r"test_\w+\.py",
            r"\w+_test\.py",
            r"\btdd\b",
            r"test.?driven",
        ],
        description="Python testing best practices",
    ),
    SkillTrigger(
        skill_name="test-review",
        plugin="python-dev",
        patterns=[
            r"\btest.?review\b",
            r"\breview.?test",
            r"\baudit.?test",
            r"\btest.?quality\b",
            r"\btautological\b",
            r"\btests?\s+meaningful\b",
        ],
        description="Test quality review - identify tautological, redundant, and weak tests",
    ),
    SkillTrigger(
        skill_name="fixing-type-errors",
        plugin="python-dev",
        patterns=[
            r"\bfix\s+(pyright|ty|type)\s+error",
            r"\b(pyright|ty)\s+error",
            r"\btype\s+check\s+fail",
            r"\bfix\s+typ(e|ing)\b",
            r"\beliminate\s+(pyright|ty|type)\s+error",
            r"\bpylance\s+error",
            r"\b(pyright|ty)\b.*\bfix\b",
        ],
        description="Fix pyright/ty/type errors systematically — trace to source, never suppress",
    ),
    SkillTrigger(
        skill_name="type-safety-audit",
        plugin="python-dev",
        patterns=[
            r"\btype.?safety.?audit\b",
            r"\baudit.?type.?safety\b",
            r"\baudit.?types?\b",
            r"\btype.?audit\b",
        ],
        description="Multi-agent type safety audit with report generation",
    ),
    SkillTrigger(
        skill_name="fastapi-patterns",
        plugin="python-dev",
        patterns=[
            r"\bfastapi\b",
            r"\bFastAPI\b",
            r"\bAPIRouter\b",
            r"\bDepends\b",
            r"\bHTTPException\b",
            r"\bQuery\s*\(",
            r"\bPath\s*\(",
            r"\bHeader\s*\(",
            r"\blifespan\b",
            r"\bendpoint\b.*\brouter\b",
            r"\brouter\b.*\bendpoint\b",
        ],
        description="FastAPI endpoints, dependencies, query parameters, lifespan",
    ),
    SkillTrigger(
        skill_name="python-best-practices",
        plugin="python-dev",
        patterns=[
            r"\.py\b",  # Any Python file
            r"\bpydantic\b",
            r"\btyping\b",
            r"\btype\s+hint",
            r"\bBaseModel\b",
            r"\bpyright\b",
            r"\bruff\b",
        ],
        description="Python typing, Pydantic, code style",
    ),
    SkillTrigger(
        skill_name="writing-dagster-pipelines",
        plugin="python-dev",
        patterns=[
            r"\bdagster\b",
            r"\bcode\s+location\b",
            r"definitions\.py",
            r"MaterializeResult",
            r"AutomationCondition",
            r"dbt_assets",
            r"resources\.yaml",
            r"ShucksSnowflakeResource",
            r"\bmateriali[sz]e\b",
            r"\bstep\s+pod\b",
        ],
        description="Dagster pipelines on the PRH UK centralised platform",
    ),
]

# Code review triggers - when reviewing, check for skills based on content
CODE_REVIEW_PATTERNS = [
    r"\breview\b.*\b(code|changes|diff|pr|mr)\b",
    r"\bcode\s+review\b",
    r"\bcheck\b.*\b(implementation|changes)\b",
    r"git\s+diff",
    r"\bmerge\b.*\brequest\b",
    r"\bpull\s+request\b",
]

CODE_REVIEW_PATTERN = re.compile("|".join(CODE_REVIEW_PATTERNS), re.IGNORECASE)


def detect_skills(user_prompt: str) -> list[SkillTrigger]:
    """Detect which skills should be loaded based on user prompt."""
    matched_skills: list[SkillTrigger] = []
    seen_names: set[str] = set()

    for trigger in SKILL_TRIGGERS:
        if trigger.skill_name in seen_names:
            continue

        combined_pattern = re.compile("|".join(trigger.patterns), re.IGNORECASE)
        if combined_pattern.search(user_prompt):
            matched_skills.append(trigger)
            seen_names.add(trigger.skill_name)

    return matched_skills


def is_code_review(user_prompt: str) -> bool:
    """Check if the user is requesting a code review."""
    return bool(CODE_REVIEW_PATTERN.search(user_prompt))


def format_skill_reminder(skills: list[SkillTrigger], is_review: bool) -> str:
    """Format the skill reminder message."""
    if not skills:
        return ""

    skill_lines = []
    for skill in skills:
        skill_lines.append(
            f"- {skill.plugin}:{skill.skill_name} - {skill.description}"
        )

    context = "code review" if is_review else "task"
    action = (
        "When reviewing code, apply the loaded skills to check for violations and best practices."
        if is_review
        else "Apply the skill guidance throughout this task."
    )

    return f"""Based on the user's {context}, consider loading these skills:

{chr(10).join(skill_lines)}

{action}"""


def main() -> None:
    """Check user prompt and inject skill reminders."""
    try:
        input_data = json.load(sys.stdin)
        user_prompt = input_data.get("prompt", "")

        if not user_prompt:
            print(json.dumps({}))
            sys.exit(0)

        # Detect matching skills
        matched_skills = detect_skills(user_prompt)
        reviewing = is_code_review(user_prompt)

        if matched_skills:
            reminder = format_skill_reminder(matched_skills, reviewing)
            # Use additionalContext in hookSpecificOutput per Claude Code docs
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": reminder
                }
            }))
        else:
            print(json.dumps({}))

    except Exception as e:
        # On error, allow operation but log
        print(json.dumps({"systemMessage": f"skill-detector error: {e}"}))

    sys.exit(0)


if __name__ == "__main__":
    main()
