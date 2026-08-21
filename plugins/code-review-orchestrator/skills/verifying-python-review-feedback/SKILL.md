---
description: This skill should be used when evaluating code review feedback on a Python codebase, before implementing any suggestion. Covers verifying a reviewer's claim against the codebase, and the library, validation, and Pydantic suggestions that reviewers get wrong. Triggers on "review feedback", "MR comments", "PR comments", "reviewer says", "reviewer suggested".
---

# Verifying Python review feedback

`superpowers:receiving-code-review` covers the general discipline: no performative agreement, clarify before implementing, push back with technical reasoning. Follow it. This skill adds the verification step for Python codebases, where a suggestion can be reasonable in the abstract and wrong for this stack.

## The rule

**A reviewer sees the diff. You see the codebase. Verify before you implement.**

## Verify first

Run these before touching anything. Each answers a question the diff cannot.

```bash
uv run pytest                    # does the current code actually work?
uv run pyright                   # what are the type implications?
rg "symbol_name" --type py       # is the "unused" thing really unused?
git log --oneline -10 -- path/to/file.py   # why is it this way?
git blame path/to/file.py                  # who decided, and when?
```

`git blame` is the one people skip. Most "why is this here" questions are answered by the commit that added it, and a reviewer without that context is guessing.

If you cannot verify a claim, say so rather than proceeding: "I can't verify this without access to X. Should I investigate, or do you want it as-is?"

## Suggestions reviewers commonly get wrong

### "Use X instead of Y"

A library swap has to survive the whole stack, not just the line under review.

- Does it handle the edge cases the current code handles?
- Does it work with the Snowflake connector and the existing Pydantic models?
- What are the performance implications at production data volume, not on the test fixture?
- Does it conflict with anything already resolved in the lockfile?

A swap that is faster in a benchmark and incompatible with your I/O layer is not an improvement.

### "Remove this validation"

Trace where the data comes from before deleting a guard:

| Source | Verdict |
|--------|---------|
| External API | Keep it. You do not control the payload |
| User input | Keep it |
| Database query | Check the constraint actually exists in the schema first |
| Internal pipeline, already validated upstream | Probably safe to remove |

Then check what it catches. `rg "ValidationError" --type py` shows whether anything downstream depends on the failure mode.

### "Simplify this Pydantic model"

Complexity in a model is often load-bearing. Before flattening it:

- Are the validators catching real bad data, or defending against nothing?
- Does `Field(default_factory=...)` exist because the API returns `null` where the type says list?
- What breaks if you simplify? Run against real data, not a fixture.

If the complexity is load-bearing, the right outcome is usually a comment explaining why, not a simplification.

### "This prompt is too long"

Prompt length is frequently the fix for an edge case someone already hit. Check the tests that cover it before shortening, and compare output quality on the cases that motivated the original wording.

## Pushing back with evidence

Cite the specific thing that breaks. Vague disagreement loses; a file and line wins.

```
"This validation exists because Snowflake returns None for missing fields and
 the downstream code assumes non-None. Removing it raises AttributeError at
 loader.py:87. Happy to add a comment explaining why instead."

"Field(default_factory=list) is there because the API returns null for empty
 arrays. Switching to a plain list[str] raises ValidationError. Want a test
 case that pins this?"
```

When you were wrong, say so in one line and move on: "Verified, you're right. The connector does handle this. Removing the redundant check."

## Related skills

| Situation | Skill |
|-----------|-------|
| General review discipline | `superpowers:receiving-code-review` |
| Feedback about type errors | `python-dev:fixing-type-errors`. Never add `# type: ignore` because a reviewer suggested it |
| Feedback needing several coordinated changes | `workflow-skills:executing-plans` |
| All feedback addressed | `workflow-skills:finishing-a-development-branch` |
