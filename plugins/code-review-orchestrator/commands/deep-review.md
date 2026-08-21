---
name: deep-review
description: Comprehensive multi-agent code review scoped to your working changes. Triggers on "deep review", "thorough review", "review this code", "/deep-review".
---

# Deep Code Review

Orchestrate a comprehensive code review using specialized agents. Strictly scoped to your working changes — uncommitted, staged, or branch changes.

**Scope rule: ONLY review code that appears in the diff. Never report issues in unchanged code.**

## Workflow

### Step 1: Extract the Diff

Determine which changes to review and extract the unified diff:

```bash
# Priority order for auto-detection:
# 1. If --base is specified, use that
# 2. If there are staged changes, review those
# 3. If there are uncommitted changes, review those
# 4. If on a branch, compare to the branch we forked from

# Supported file extensions
FILE_FILTERS='*.py' '*.ts' '*.tsx'

# Check for staged changes
STAGED=$(git diff --cached -- $FILE_FILTERS)

# Check for uncommitted changes
UNCOMMITTED=$(git diff HEAD -- $FILE_FILTERS)

# Compare to the branch we forked from (not a hardcoded branch name).
# Try the upstream tracking branch first, then fall back to main/develop.
UPSTREAM=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null | sed 's|^origin/||')
if [ -z "$UPSTREAM" ]; then
  # No tracking branch — find the nearest common ancestor from main or develop
  for candidate in main develop; do
    if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
      UPSTREAM="$candidate"
      break
    fi
  done
fi
FORK_POINT=$(git merge-base "${UPSTREAM}" HEAD)
BRANCH_DIFF=$(git diff "${FORK_POINT}"...HEAD -- $FILE_FILTERS)
```

If the user specified `--base <branch>`, use that directly:
```bash
FORK_POINT=$(git merge-base <branch> HEAD)
DIFF=$(git diff "${FORK_POINT}"...HEAD -- $FILE_FILTERS)
```

If the user specified specific files, use those as the diff filter.

**If the diff is empty, report "No changes to review" and exit.**

### Step 2: Write Diff to Repo-Local File

**CRITICAL: Always write the diff to a file inside the repo directory.** Agents run in a sandbox that restricts access to paths outside the repo. Never write diffs to `/tmp/` or any path outside the working directory.

```bash
mkdir -p docs/reviews
echo "$DIFF" > docs/reviews/deep-review-diff.txt
```

Check diff size:

```bash
wc -l < docs/reviews/deep-review-diff.txt
```

- **Under 1500 lines:** Pass the full diff to each agent.
- **Over 1500 lines:** Split per-file and run agents per-file-diff. Write each split to `docs/reviews/deep-review-diff-<filename>.txt`.

### Step 2.5: Detect Languages and Async Patterns in Diff

Determine which languages are present in the diff to select the right agents:

```bash
HAS_PYTHON=$(grep -c '^diff --git.*\.py' docs/reviews/deep-review-diff.txt || true)
HAS_TS=$(grep -c '^diff --git.*\.tsx\?' docs/reviews/deep-review-diff.txt || true)

# Detect async patterns in added lines to gate concurrency-reviewer dispatch
HAS_ASYNC=$(grep -cE '^\+.*(async def |await |asyncio\.|create_task|\.gather\(|TaskGroup|async with |async function |Promise\.(all|allSettled|race)|AbortController|AbortSignal|\.then\(|new Worker)' docs/reviews/deep-review-diff.txt || true)
```

### Step 3: Run Review Agents

**Dispatch agents based on detected languages in a single response using parallel Agent tool calls.** Do NOT wait for one agent to finish before starting the next. Only use sequential execution if the user passes `--sequential`.

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

**Python agents** (dispatch when diff contains `.py` files):
- **code-quality-reviewer** - enforces coding standards (structlog, error handling)
- **type-discipline-reviewer** - ensures type safety (Any abuse, redundant isinstance)
- **logic-verifier** - checks correctness (contracts, control flow, silent failures)
- **test-quality-reviewer** - identifies tautological, redundant, and weak tests

**TypeScript agents** (dispatch when diff contains `.ts`/`.tsx` files):
- **ts-react-reviewer** - hooks discipline, TanStack Query, Zustand, component patterns
- **ts-type-reviewer** - type safety at API boundaries, `any`/`as` abuse, Zod alignment

**Async agent** (dispatch when diff contains async patterns — `async def`, `await`, `asyncio.*`, `Promise.all`, `create_task`, `AbortController`, etc.):
- **concurrency-reviewer** - unbounded concurrency, fire-and-forget, blocking-in-async, missing timeouts, resource leaks

**Shared agents** (dispatch when ANY supported files are in the diff):
- **structure-reviewer** - SOLID principles, function decomposition (language-agnostic)
- **security-reviewer** - injection flaws, secrets, auth, data exposure (language-agnostic)

For mixed-language diffs, dispatch ALL relevant agents in a single response. For example, a diff with both `.py` and `.tsx` files that contain async patterns dispatches all 9 agents in parallel.

**Each agent receives the diff file path AND the diff content in their prompt:**

The diff is saved at `docs/reviews/deep-review-diff.txt` inside the repo. Include both the path and the inline content so agents have the diff even if one access method fails.

```
You are reviewing working changes (uncommitted/staged/branch). Your review
is STRICTLY SCOPED to the changes shown in the unified diff below.

The diff is also available at: docs/reviews/deep-review-diff.txt

Rules:
1. ONLY report findings on lines that appear in the diff (lines prefixed with +)
2. You MAY read full files for surrounding context to understand the changes
3. You MUST NOT report issues on unchanged code (lines without + prefix)
4. Reference findings by file path and line number from the diff header
5. If a change introduces a problem that interacts with existing code,
   report it as a finding on the CHANGED line, explaining the interaction
6. In addition to issues, note any STRENGTHS — good patterns, solid design
   choices, or well-handled edge cases in the changed code

<diff>
{unified diff content}
</diff>
```

### Step 4: Validate and Synthesize Findings

After agents return findings:

1. **Validate scope** - Cross-check each finding's file:line against the diff. If a finding references a line NOT in the diff, discard it and log in the "Discarded Findings" section
2. **Deduplicate** - If multiple agents flag the same line, merge into one finding
3. **Prioritize** - Critical issues first, then Important, then Suggestions
4. **Group by file** - easier for the user to address
5. **Collect strengths** - Gather positive observations from all agents
6. **Determine merge readiness** - Based on findings, assign a verdict

### Step 5: Present Summary

```markdown
# Deep Review Summary

**Scope:** {X files, Y lines changed}
**Change type:** {uncommitted | staged | branch vs main}
**Reviewed by:** {list agents that were dispatched}

## Change Summary

Categorize the changes by reading the diff:

- **New features:** {list new functionality added}
- **Bug fixes:** {list bugs addressed}
- **Tests:** {list test changes}
- **Chores:** {list refactoring, config, dependencies}

## Critical Issues (must fix before merge)

### file.py

#### [Line 42] Silent data loss in exception handler
**Found by:** logic-verifier
**Issue:** Exception swallowed with bare `except: continue`
**Fix:** Log failures and track count, fail if too many errors

#### [Line 78] SQL injection via f-string query
**Found by:** security-reviewer | **CWE:** CWE-89
**Issue:** User input interpolated directly into SQL query
**Fix:** Use parameterized query

## Important Issues (should fix)

...

## Suggestions (consider for next iteration)

...

## Strengths

Highlight what the changes do well. Good patterns reinforce good habits.

- Good use of Pydantic models for data validation
- Comprehensive error messages with context
- Parameterized queries used consistently in new endpoints
- ...

## Discarded Findings (outside diff scope)

> These findings were reported by agents but fall outside your changes.
> Consider addressing them in a separate branch or via `/repo-review`.

- **[src/models/user.py:120]** Missing type annotation on `get_name` (type-discipline-reviewer)

## Merge Readiness

Based on findings, assign one verdict:

| Verdict | Meaning |
|---------|---------|
| **Ready** | No critical or important issues. Ship it. |
| **Ready with fixes** | Important issues found but no blockers. Fix and merge. |
| **Needs work** | Critical issues that must be resolved before merge. |
```

### Step 6: Clean Up Diff Files

Remove the temporary diff files from the repo to avoid committing them:

```bash
rm -f docs/reviews/deep-review-diff.txt docs/reviews/deep-review-diff-*.txt
```

## Usage Examples

```bash
# Review uncommitted changes
/deep-review

# Review staged changes
/deep-review --staged

# Review specific files
/deep-review src/pipeline.py src/transform.py

# Review changes since branching from main
/deep-review --base main

# Run agents sequentially (see progress one at a time)
/deep-review --sequential
```

## Integration with Other Tools

After deep review, you might want to:
- `/commit-smart` - commit the fixes
- Run tests to verify changes
- Request a human review for critical changes
- `/repo-review` - review the full repo for refactor planning

## What This Does NOT Do

- Auto-fix issues (you decide what to fix)
- Review pre-existing code (use `/repo-review` for that)
- Run linters (use ruff/mypy separately)
- Review documentation quality
