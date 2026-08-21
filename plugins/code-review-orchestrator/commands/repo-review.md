---
name: repo-review
description: Comprehensive full-repo code review for refactor planning. Inventories the repo, batches files by dependency, and dispatches review agents systematically. Triggers on "repo review", "full review", "review the repo", "/repo-review".
---

# Repo Review

Orchestrate a comprehensive review of an entire repository (or scoped directories) for refactor planning. Uses dependency-aware batching to ensure related files are reviewed together, and consolidates findings into actionable fix branches.

**This is NOT for MR/PR reviews.** Use `/mr-review` or `/deep-review` for diff-scoped reviews.

## Output Location

Reviews are saved to: `docs/reviews/repo-review-{YYYY-MM-DD}.md`

```bash
mkdir -p docs/reviews
```

## Workflow

### Step 1: Plan Review Batches

Launch the **repo-review-planner** agent in **planning mode**:

```
Mode: PLANNING

Inventory this repository and create dependency-aware review batches.
Scope: {user-specified directories or entire repo}

Exclude from review:
- Test files (unless --include-tests is specified)
- Migration files
- Generated code
- __init__.py files that only re-export
- Generated route trees (e.g. routeTree.gen.ts)
- Generated API types (e.g. v1.d.ts from openapi-typescript)

Return a structured review plan with batches of 5-8 files each,
clustered by import dependencies. Group Python and TypeScript files
into separate batches so the right agents are dispatched for each.
```

If the user specified directories (e.g., `/repo-review src/pipeline/ src/models/`), pass those as the scope.

**Review the plan before proceeding.** If the repo has >200 files and no scope was specified, confirm with the user before continuing.

### Step 2: Run Review Agents on Each Batch

For each batch, **dispatch the relevant agents based on batch language in a single response using parallel Agent tool calls.** Do NOT wait for one agent to finish before starting the next.

**Agent selection by language:**

| Agent | Python | TypeScript | Async | Always |
|-------|--------|------------|-------|--------|
| code-quality-reviewer | Y | | | |
| type-discipline-reviewer | Y | | | |
| logic-verifier | Y | | | |
| structure-reviewer | Y | Y | | |
| test-quality-reviewer | Y | | | |
| ts-react-reviewer | | Y | | |
| ts-type-reviewer | | Y | | |
| concurrency-reviewer | | | Y | |
| security-reviewer | | | | Y |

**Python batches** dispatch: code-quality, type-discipline, logic-verifier, structure, test-quality, security (6 agents). Add concurrency-reviewer if batch contains async patterns.

**TypeScript batches** dispatch: ts-react-reviewer, ts-type-reviewer, structure, security (4 agents). Add concurrency-reviewer if batch contains async patterns.

**Async detection for repo-review batches:**

Before dispatching agents for a batch, check if any files in the batch contain async patterns:

```bash
# Check batch files for async patterns
HAS_ASYNC=0
for f in $BATCH_FILES; do
  if grep -qE 'async def |await |asyncio\.|create_task|\.gather\(|TaskGroup|async with |async function |Promise\.(all|allSettled|race)|AbortController|AbortSignal|\.then\(|new Worker' "$f" 2>/dev/null; then
    HAS_ASYNC=1
    break
  fi
done
```

Only dispatch **concurrency-reviewer** when `HAS_ASYNC=1`.

**Each agent receives the full file contents for their batch:**

```
You are reviewing the following files as part of a full repository review
for refactor planning. Review ALL code in these files — there is no diff scope.

Batch context:
- Batch {N} of {M}: {batch description}
- These files are clustered because: {cluster reason}
- Dependencies: {dependency notes from planner}

Files to review:
{list of file paths}

Read each file and apply your full analysis framework. Report all findings
regardless of when the code was written.
```

**Execution order:**
- Default: **parallel agents within each batch** — all 6 agents run simultaneously for each batch, but batches are sequential to manage context.
- With `--sequential`: Run agents one at a time within each batch for progress visibility.
- With `--full-parallel`: Run all batches and agents simultaneously. Fastest but heavy on resources.

### Step 3: Consolidate Findings

After all batches are complete, launch the **repo-review-planner** agent in **consolidation mode**:

```
Mode: CONSOLIDATION

Cross-reference and consolidate findings from all review batches.

Batch results:
<batch-1-results>
{findings from batch 1}
</batch-1-results>

<batch-2-results>
{findings from batch 2}
</batch-2-results>

...

Tasks:
1. Cross-reference findings across batches for contradictions
2. Deduplicate identical/similar findings
3. Consolidate recurring patterns into single findings with file lists
4. Group all findings into suggested fix branches ordered by dependency and risk
```

### Step 4: Write Output File

```bash
date=$(date +%Y-%m-%d)
output="docs/reviews/repo-review-${date}.md"
```

## Output Format

```markdown
# Repo Review: {repo-name}

**Date:** {YYYY-MM-DD}
**Scope:** {entire repo | specific directories}
**Files reviewed:** {N} files ({P} Python, {T} TypeScript) across {M} modules
**Batches:** {B} batches
**Agents:** logic, code-quality, type-discipline, structure, test-quality, security

---

## Executive Summary

- **Critical:** N issues across M files
- **Important:** N issues across M files
- **Suggestions:** N improvements identified
- **Recurring patterns:** N patterns found across multiple files

### Top Modules Needing Attention

| Module | Critical | Important | Suggestions |
|--------|----------|-----------|-------------|
| src/pipeline/ | 3 | 5 | 2 |
| src/models/ | 1 | 4 | 6 |
| src/cli/ | 0 | 2 | 3 |

---

## Cross-Batch Issues

### Conflicts
- [CONFLICT] Agent suggested removing `transform_legacy()` in src/pipeline/transform.py:45, but it's called in src/cli/commands.py:23

### Recurring Patterns
- **Silent exception swallowing** — found in 6 files. Suggest fixing all in `fix/error-handling`
- **Unnarrowed Any from JSON** — found in 4 files. Suggest fixing all in `fix/type-safety`

---

## Findings by Module

### src/pipeline/

#### [src/pipeline/extract.py:42-55] Silent data loss in transform loop
**Severity:** Critical | **Found by:** logic-verifier | **Confidence:** HIGH

**Why this matters:**
...

**Current code:**
```python
...
```

**Suggested fix:**
```python
...
```

---

#### [src/pipeline/transform.py:10-65] Function too long (55 lines)
**Severity:** Important | **Found by:** structure-reviewer | **Confidence:** HIGH

...

---

### src/models/

...

---

## Suggested Fix Branches

Findings grouped into logical branches, ordered by dependency graph and risk.

### 1. fix/error-handling (8 issues, 4 files)
**Risk:** High | **Priority:** 1 (blocks safe refactoring)
**Files:** src/pipeline/extract.py, src/pipeline/load.py, src/models/user.py, src/cli/commands.py

| File | Line | Issue | Severity |
|------|------|-------|----------|
| src/pipeline/extract.py | 42 | Silent data loss in transform loop | Critical |
| src/pipeline/load.py | 88 | Bare except swallows connection errors | Critical |
| ... | ... | ... | ... |

### 2. fix/type-safety (5 issues, 3 files)
**Risk:** Low | **Priority:** 2 (additive, no behavior change)
**Files:** src/models/user.py, src/models/config.py, src/pipeline/validators.py

| File | Line | Issue | Severity |
|------|------|-------|----------|
| ... | ... | ... | ... |

### 3. refactor/pipeline-decomposition (3 issues, 2 files)
**Risk:** Medium | **Priority:** 3 (requires test verification)
**Note:** Run tests after each function extraction
**Files:** src/pipeline/transform.py, src/pipeline/extract.py

| File | Line | Issue | Severity |
|------|------|-------|----------|
| ... | ... | ... | ... |

---

Review saved to: docs/reviews/repo-review-2026-03-20.md
```

## Usage Examples

```bash
# Review entire repo
/repo-review

# Review specific directories
/repo-review src/pipeline/ src/models/

# Include test files in the review
/repo-review --include-tests

# Run agents sequentially within each batch
/repo-review --sequential

# Full parallel (all batches + all agents simultaneously)
/repo-review --full-parallel
```

## What This Does NOT Do

- Review diff/changes only (use `/mr-review` or `/deep-review` for that)
- Auto-fix issues (you decide what to fix)
- Run linters (use ruff/mypy/biome separately)
- Create the fix branches (you do, guided by the suggested groupings)

## Educational Content

When writing findings, consult `references/educational-patterns.md` for consistent explanations of common issues.
