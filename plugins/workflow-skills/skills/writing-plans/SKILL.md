---
description: This skill should be used when the user has a spec, requirements, or design for a multi-step task and needs a phased implementation plan before touching code. Triggers on "write a plan", "create implementation plan", "plan this out", "how should we implement this".
---

# Writing phased plans

`superpowers:writing-plans` defines what a task looks like: bite-sized steps, real code in every code step, no placeholders, the self-review pass. Follow all of it.

This skill changes one thing: **the plan is a directory of phase files, not a single document**. That is what makes a plan survive across sessions.

Announce: "I'm using the writing-plans skill to create a phased implementation plan."

## Before you write

**Load the skills for the stack**, so the plan proposes patterns the codebase actually uses:

| Signal | Load |
|--------|------|
| Any Python | `python-dev:python-best-practices` |
| Tests in the plan | `python-dev:python-test-quality` |
| dbt | `python-dev:dbt-python-integration` |
| New dependencies or workspace changes | `python-dev:uv-pyproject` |
| FastAPI | `python-dev:fastapi-patterns` |

**Check the docs for anything external.** Resolve the library with `context7:resolve-library-id`, then `context7:query-docs` for the patterns the plan will use. A plan built on a half-remembered API produces code that has to be rewritten during execution. This matters most for libraries new to the codebase and for anything with a fast-moving API.

## Layout

```
docs/plans/<feature-name>/
├── 00-overview.md      summary, architecture, phase table, progress
├── 01-data-models.md   phase 1
├── 02-core-logic.md    phase 2
└── 03-integration.md   phase 3
```

A phase is 3 to 5 tasks ending at a checkpoint you can run. Phases exist so that work can stop and resume cleanly: one file completed, one commit, one place to pick up.

## Overview document

```markdown
# [Feature] implementation plan

> **For agentic workers:** use `superpowers:subagent-driven-development` (a fresh
> subagent per task) or `workflow-skills:executing-plans` (batched, in-session).
> Work phase files in order. Steps use `- [ ]` for tracking.

**Goal:** [one sentence]
**Architecture:** [2-3 sentences]
**Tech stack:** [key libraries]

## Global constraints

[Project-wide requirements from the spec: version floors, naming rules,
platform limits. One line each, values copied verbatim. Every task
inherits this section.]

## Files

- `src/pkg/models.py` - new Pydantic models
- `tests/test_models.py` - unit tests

## Phases

| Phase | File | Goal | Checkpoint |
|-------|------|------|------------|
| 1 | `01-data-models.md` | Define models | `uv run pyright` passes |
| 2 | `02-core-logic.md` | Extraction logic | `uv run pytest tests/` passes |

## Progress

- [ ] Phase 1: Data models
- [ ] Phase 2: Core logic
```

## Phase document

```markdown
# Phase 1: Data models

> Part of [Feature](./00-overview.md).

**Goal:** Define the models
**Checkpoint:** `uv run pyright src/pkg/models.py` reports 0 errors

---

## Task 1.1: Create the Award model

**Files:**
- Create: `src/pkg/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: nothing
- Produces: `Award(name: str, year: int | None)`, imported by Task 2.1

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run it, expect FAIL**
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run it, expect PASS**
- [ ] **Step 5: Commit**

---

## Phase complete

**Commit:** `feat(models): add Award model with validation`
**Next:** [Phase 2](./02-core-logic.md)
```

Every code step carries the actual code. The **Interfaces** block is not optional: a subagent executing Task 2.1 sees only Task 2.1, so exact names and types are the only way it learns what Task 1.1 produced.

## Handoff

After saving all files, state what was written and offer the choice:

```
Plan saved to docs/plans/<feature>/ - 3 phases, 9 tasks.

1. Subagent-driven (recommended) - fresh subagent per task, review between each
2. Inline - batched execution in this session with checkpoints

Which?
```

Subagent-driven uses `superpowers:subagent-driven-development`. Inline uses `workflow-skills:executing-plans`.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| One giant plan file | Split into phase files with an overview |
| No overview | Always write `00-overview.md` with the phase table and progress list |
| Phases with no checkpoint | Every phase ends at a command that passes or fails |
| Missing Interfaces block | A subagent cannot guess a neighbouring task's signatures |
| Describing code instead of writing it | Code steps carry code. See the no-placeholders rule |
| Relative paths | Always full paths from the repo root |

When the plan says to fix type errors, point at `python-dev:fixing-type-errors` and state that `# type: ignore` is not the fix.
