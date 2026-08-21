---
name: writing-skills
description: This skill should be used when creating new skills, editing existing skills, improving skill effectiveness, researching a library to create a skill, or when a skill isn't being followed consistently. Triggers on "create a skill", "write a skill", "improve this skill", "skill isn't working", "research this library and make a skill", "read docs and create a skill".
---

# Writing Skills

Create effective skills that Claude actually follows, even under pressure.

## Core Principle

**Skills are documentation that changes behavior.** If Claude doesn't follow a skill under pressure, the skill failed - not Claude.

## When to Create a Skill

Create skills for:
- Repeated workflows (same process used across projects)
- Discipline-enforcing practices (TDD, type safety, code review)
- Library/tool integration patterns (setup, usage, pitfalls)
- Processes with compliance costs (time, effort, rework)
- Workflows that could be rationalized away ("just this once")

Don't create skills for:
- One-off tasks
- Pure reference material (API docs, syntax) without actionable guidance
- Things Claude naturally does well

## Workflow: Building a Skill from Documentation

When creating a skill for a library, tool, or framework:

### 1) Gather Information First

Before writing anything, collect inputs:
- Target library/tool name
- Official docs URL (prefer `llms.txt` endpoint if available)
- Source repository URL (if useful)
- Desired skill name

### 2) Research Documentation Comprehensively

1. Fetch entry docs page (prefer `llms.txt` for LLM-optimized content)
2. Follow linked pages to understand the full picture
3. Prioritize:
   - Getting started / installation
   - Architecture and core concepts
   - Feature documentation
   - Guides, recipes, troubleshooting
   - Changelog and migration notes
4. Capture: API names, required config, dependencies, common pitfalls

If `llms.txt` is absent, use: README, `/docs`, examples, API references.

### 3) Inspect Source and Examples (When Useful)

- Clone or read source to confirm behavior and naming
- Check examples for canonical integration patterns
- Validate uncertain details against real code

### 4) Synthesize Before Writing

Produce an internal model covering:
- Required setup and install commands
- Minimum working integration
- Feature dependency map
- Extension points and customization
- Debugging checklist
- Version-specific gotchas

### 5) Author the Skill

Now write the SKILL.md following the structure below.

## Skill Structure

### Required: Frontmatter

```yaml
---
name: skill-name
description: This skill should be used when [specific triggers]. Triggers on "phrase 1", "phrase 2", "phrase 3".
version: 1.0.0
---
```

**Description rules:**
- Use third person: "This skill should be used when..."
- Include specific trigger phrases users would say
- Include symptoms of ABOUT to violate (for discipline skills)

### Required: Clear Purpose

First paragraph explains what and why in 2-3 sentences.

### Required: Actionable Content

Skills must include content users can act on immediately:

```markdown
## Setup
```bash
# Runnable install commands
uv add library-name
```

## Quick Start
```python
# Minimal working example - complete and copy-pasteable
from library import Thing

thing = Thing(config="value")
result = thing.do_something()
```
```

### Required for Library Skills: Common Pitfalls

```markdown
## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| ImportError: no module named X | Missing dependency | `uv add X` |
| Connection timeout | Missing config | Set `LIBRARY_URL` env var |
| Type errors with responses | Wrong version | Use `library>=2.0` |
```

### Required for Discipline Skills: Authority Language

Use imperative, non-negotiable framing:

```markdown
## The Rule

**Check for skills BEFORE any response.** No exceptions.

Write code before test? Delete it. Start over.
```

### Required for Discipline Skills: Red Flags

```markdown
## Red Flags

These thoughts mean STOP - you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is simple, no skill needed" | Simple things become complex. Use the skill. |
| "I'll add type: ignore here" | You're avoiding the real fix. Trace to source. |
| "Just this once" | There's no "just this once". Follow the process. |
```

### Required for Discipline Skills: Rationalization Table

Explicitly counter every excuse:

```markdown
## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I already know how to do this" | Skills encode lessons from failures you haven't hit yet. |
| "This is faster" | Skipping process creates bugs that take 10x longer. |
| "Being pragmatic" | Pragmatic means following proven processes, not skipping them. |
```

### Optional: References Directory

For detailed content that doesn't need to load every time:
- `references/patterns.md` - Detailed examples
- `references/advanced.md` - Edge cases

## Skill Types

### Discipline Skills (Follow Exactly)

For TDD, type safety, code review requirements:
- Strong authority language (MUST, NEVER, ALWAYS)
- Explicit rationalization counters
- Red flags section
- No flexibility

### Workflow Skills (Follow Process)

For brainstorming, planning, execution:
- Clear step-by-step process
- Checkpoints and handoffs
- Integration with other skills

### Library/Tool Skills (Setup + Patterns)

For integrating external libraries:
- Runnable setup commands
- Minimal working example (complete, not partial)
- Feature and dependency matrix
- Common pitfalls with fixes
- Links to official docs

### Reference Skills (Adapt to Context)

For patterns, examples, documentation:
- Flexible application
- Multiple approaches shown
- Context-dependent guidance

## Persuasion Principles (For Discipline Skills)

### Authority (Most Important)

```markdown
"YOU MUST check for skills before responding."
"Delete it. No exceptions."

NOT: "Consider checking for skills."
NOT: "You might want to delete it."
```

### Commitment

Force explicit choices:

```markdown
"Announce: 'I'm using the [skill] skill to [purpose]'"
"Choose A, B, or C. No other options."

NOT: "Pick whichever approach works."
```

### Scarcity (Time Pressure)

Create urgency:

```markdown
"BEFORE any response, check for skills."
"Run tests BEFORE committing. Not after."

NOT: "When convenient, check for skills."
```

## Testing Skills

### RED: Baseline Test

Run scenario WITHOUT skill. Document failures.

### GREEN: Write Skill

Address specific failures you documented.

### REFACTOR: Close Loopholes

Agent violated rule despite skill? Add explicit counter:

```markdown
Before: "Write code before test? Delete it."
After: "Write code before test? Delete it. Start over.
        Don't keep as 'reference'. Don't 'adapt' it.
        Delete means delete."
```

## Quality Checklist

Before deploying a skill:

- [ ] Frontmatter `name` matches parent directory
- [ ] Description uses third person with specific triggers
- [ ] First paragraph explains purpose clearly
- [ ] Commands are runnable and realistic
- [ ] Examples are complete (not partial snippets)
- [ ] Includes at least one minimal "happy path"
- [ ] Common failure modes documented with fixes
- [ ] No speculative claims unsupported by docs/source
- [ ] Authority language for discipline skills
- [ ] Red Flags + Rationalization table for discipline skills
- [ ] Under 2000 words (details in references/)
- [ ] Tested under pressure scenarios

## Install Locations

Project-level (shared with team):
```
.claude/commands/<skill-name>.md
```

User-level (personal):
```
~/.claude/commands/<skill-name>.md
```

Plugin skills (for distribution):
```
plugins/<plugin-name>/skills/<skill-name>/SKILL.md
```

## Minimal SKILL.md Template

```markdown
---
name: <skill-name>
description: This skill should be used when [triggers]. Triggers on "phrase 1", "phrase 2".
version: 1.0.0
---

# <Title>

<2-3 sentence purpose statement>

## When to Use

- Trigger condition 1
- Trigger condition 2

## Setup

```bash
# install commands
uv add example-library
```

## Quick Start

```python
# minimal complete working example
from example import Client

client = Client(api_key="...")
result = client.do_thing()
print(result)
```

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| Error X | Solution Y |

## References

- [Official Docs](https://...)
```

## Example: Strengthening a Weak Skill

**Before (weak):**
```markdown
## Type Errors

When you see type errors, try to fix them properly.
Consider tracing to the source instead of using suppressions.
```

**After (strong):**
```markdown
## The Rule

**Never suppress, always fix.** Type errors are symptoms. Fix the disease.

## Forbidden

```python
# FORBIDDEN - Suppression
x: str = get_value()  # type: ignore

# FORBIDDEN - Blind casting
x = cast(str, get_value())
```

## Red Flags

| Thought | Reality |
|---------|---------|
| "Just add type: ignore" | You're hiding the bug, not fixing it. |
| "Cast is fine here" | Cast lies to the type checker. Fix the actual type. |
| "This is a pyright bug" | 99% of the time it's your code. Trace to source. |
```

## Output When Done

After creating a skill, report:
- Documentation/sources reviewed
- File path created/updated
- Summary of what the skill covers
- Suggested next steps (test scenarios, copy to other locations)
