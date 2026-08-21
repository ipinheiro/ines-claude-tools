---
name: mr-review
description: Review code for GitLab MR inline comments. Strictly scoped to diff changes only. Triggers on "mr review", "review for MR", "gitlab review", "/mr-review".
---

# MR Review

Orchestrate a code review strictly scoped to merge request changes. Produces educational comments you can paste directly into the GitLab MR diff.

**Scope rule: ONLY review code that appears in the diff. Never report issues in unchanged code.**

## Output Location

Reviews are saved to: `docs/reviews/mr-review-{branch}-{YYYY-MM-DD}.md`

Create the directory if it doesn't exist:
```bash
mkdir -p docs/reviews
```

## Workflow

### Step 1: Extract the Diff

Detect the branch we forked from and extract the full unified diff:

```bash
# Supported file extensions
FILE_FILTERS='*.py' '*.ts' '*.tsx'

# Find the branch we forked from — use the upstream tracking branch if set,
# otherwise fall back to main/develop.
UPSTREAM=$(git rev-parse --abbrev-ref '@{upstream}' 2>/dev/null | sed 's|^origin/||')
if [ -z "$UPSTREAM" ]; then
  for candidate in main develop; do
    if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
      UPSTREAM="$candidate"
      break
    fi
  done
fi
FORK_POINT=$(git merge-base "${UPSTREAM}" HEAD)
DIFF=$(git diff "${FORK_POINT}"...HEAD -- $FILE_FILTERS)
```

If the user specified `--base <branch>`, use that directly:
```bash
FORK_POINT=$(git merge-base <branch> HEAD)
DIFF=$(git diff "${FORK_POINT}"...HEAD -- $FILE_FILTERS)
```
If the user specified specific files, add them to the diff filter.

**If the diff is empty, report "No changes to review" and exit.**

### Step 2: Write Diff to Repo-Local File

**CRITICAL: Always write the diff to a file inside the repo directory.** Agents run in a sandbox that restricts access to paths outside the repo. Never write diffs to `/tmp/` or any path outside the working directory.

```bash
mkdir -p docs/reviews
echo "$DIFF" > docs/reviews/mr-diff.txt
```

Check if the diff is manageable for a single pass:

```bash
wc -l < docs/reviews/mr-diff.txt
```

- **Under 1500 lines:** Pass the full diff to each agent.
- **Over 1500 lines:** Split the diff per-file and run agents per-file-diff to avoid context overflow. Write each split to `docs/reviews/mr-diff-<filename>.txt`. Use `git diff ${FORK_POINT}...HEAD -- <file>` for each changed file.

### Step 2.5: Detect Languages and Async Patterns in Diff

```bash
HAS_PYTHON=$(grep -c '^diff --git.*\.py' docs/reviews/mr-diff.txt || true)
HAS_TS=$(grep -c '^diff --git.*\.tsx\?' docs/reviews/mr-diff.txt || true)

# Detect async patterns in added lines to gate concurrency-reviewer dispatch
HAS_ASYNC=$(grep -cE '^\+.*(async def |await |asyncio\.|create_task|\.gather\(|TaskGroup|async with |async function |Promise\.(all|allSettled|race)|AbortController|AbortSignal|\.then\(|new Worker)' docs/reviews/mr-diff.txt || true)
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
- **code-quality-reviewer** - Enforces coding standards (structlog, error handling)
- **type-discipline-reviewer** - Catches Any abuse, redundant isinstance
- **logic-verifier** - Traces execution paths, finds correctness bugs
- **test-quality-reviewer** - Identifies tautological, redundant, and weak tests

**TypeScript agents** (dispatch when diff contains `.ts`/`.tsx` files):
- **ts-react-reviewer** - Hooks discipline, TanStack Query, Zustand, component patterns
- **ts-type-reviewer** - Type safety at API boundaries, `any`/`as` abuse, Zod alignment

**Async agent** (dispatch when diff contains async patterns — `async def`, `await`, `asyncio.*`, `Promise.all`, `create_task`, `AbortController`, etc.):
- **concurrency-reviewer** - Unbounded concurrency, fire-and-forget, blocking-in-async, missing timeouts, resource leaks

**Shared agents** (dispatch when ANY supported files are in the diff):
- **structure-reviewer** - SOLID principles, function decomposition (language-agnostic)
- **security-reviewer** - Injection flaws, secrets, auth, data exposure (language-agnostic)

For mixed-language diffs, dispatch ALL relevant agents in parallel.

**Each agent receives the diff file path AND the diff content in their prompt:**

The diff is saved at `docs/reviews/mr-diff.txt` inside the repo. Include both the path and the inline content so agents have the diff even if one access method fails.

```
You are reviewing a merge request. Your review is STRICTLY SCOPED to the
changes shown in the unified diff below.

The diff is also available at: docs/reviews/mr-diff.txt

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

### Step 4: Validate and Transform to MR Format

After agents return findings, validate and transform:

1. **Validate scope** - Cross-check each finding's file:line against the diff. If a finding references a line NOT in the diff, discard it and log: `[DISCARDED] {finding summary} - not in diff`
2. **Deduplicate** - If multiple agents flag the same line, merge into one finding
3. **Group by file** - Sort files alphabetically by full path
4. **Sort by line** - Within each file, sort findings by line number ascending
5. **Format educationally** - Each finding gets Why/Current/Fix/Learn sections
6. **Collect strengths** - Gather positive observations from all agents
7. **Determine merge readiness** - Based on findings, assign a verdict

### Step 5: Write Output File

Save to `docs/reviews/mr-review-{branch}-{date}.md`

```bash
# Get branch name for filename
branch=$(git branch --show-current | tr '/' '-')
date=$(date +%Y-%m-%d)
output="docs/reviews/mr-review-${branch}-${date}.md"
```

### Step 6: Clean Up Diff Files

Remove the temporary diff files from the repo to avoid committing them:

```bash
rm -f docs/reviews/mr-diff.txt docs/reviews/mr-diff-*.txt
```

## Output Format

```markdown
# MR Review: {branch-name}

**Branch:** {source-branch} -> {target-branch}
**Files reviewed:** {count} files ({N} Python, {M} TypeScript)
**Date:** {YYYY-MM-DD}
**Scope:** Diff changes only
**Agents:** {list agents that were dispatched}

---

## Change Summary

Categorize the changes by reading the diff and commit messages:

- **New features:** {list new functionality added}
- **Bug fixes:** {list bugs addressed}
- **Tests:** {list test changes}
- **Chores:** {list refactoring, config, dependencies}

---

## Summary

| Severity | Count |
|----------|-------|
| Critical | N |
| Important | N |
| Suggestion | N |

---

## src/models/user.py

### Line 15: Unnarrowed Any from JSON parsing
**Severity:** Important | **Found by:** type-discipline-reviewer

**Why this matters:**
`Any` disables type checking. The `data["user_id"]` access returns `Any`,
so type errors in downstream code won't be caught.

**Current code (from diff):**
```python
+data: Any = json.loads(raw)
+user_id = data["user_id"]
```

**Suggested fix:**
```python
class UserPayload(BaseModel):
    user_id: str

payload = UserPayload.model_validate_json(raw)
user_id = payload.user_id
```

**Learn more:** Pydantic models provide type safety AND runtime validation.

---

## src/pipeline.py

### Line 42: Silent exception in processing loop
**Severity:** Critical | **Found by:** logic-verifier

...

---

## Strengths

Highlight what the changes do well. Good patterns reinforce good habits.

- Good use of Pydantic models for data validation
- Parameterized queries used consistently
- ...

---

## Discarded Findings (outside diff scope)

> The following findings were reported by agents but fall outside the diff.
> Consider addressing these in a separate branch.

- **[src/models/user.py:120]** Missing type annotation on `get_name` (type-discipline-reviewer)
- **[src/pipeline.py:200]** Magic number in retry logic (code-quality-reviewer)

---

## Merge Readiness

Based on findings, assign one verdict:

| Verdict | Meaning |
|---------|---------|
| **Ready** | No critical or important issues. Ship it. |
| **Ready with fixes** | Important issues found but no blockers. Fix and merge. |
| **Needs work** | Critical issues that must be resolved before merge. |

---

Review saved to: docs/reviews/mr-review-feature-auth-2026-03-04.md
```

### Ordering Rules

1. **Files:** Alphabetically by full path (`src/a.py` before `src/b/c.py`)
2. **Findings within file:** By line number, ascending
3. **Same line:** Critical -> Important -> Suggestion

This ordering matches GitLab's diff view for linear review.

## Usage Examples

```bash
# Default: auto-detect fork point (upstream tracking branch, or main/develop)
/mr-review

# Explicit base branch
/mr-review --base main
/mr-review --base develop

# Review specific files only
/mr-review src/pipeline.py src/models/

# Run agents sequentially (see progress one at a time)
/mr-review --sequential
```

## What This Does NOT Do

- Auto-post comments to GitLab (you copy/paste from the output file)
- Review pre-existing code (use `/repo-review` for that)
- Auto-fix issues (you decide what to fix)
- Run linters (use ruff/mypy/biome separately)

## Educational Content

When writing findings, consult `references/educational-patterns.md` for consistent explanations of common issues:

- Structure & Decomposition (SRP, parameter objects, guard clauses)
- Error Handling (silent failures, swallowed exceptions)
- Type Safety (Any abuse, redundant isinstance)
- Logging (structlog patterns)
- Security (injection, secrets, path traversal, XSS)

Use these patterns to ensure feedback is educational and helps colleagues learn, not just point out problems.
