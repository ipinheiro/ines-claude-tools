---
name: using-git-worktrees
description: This skill should be used when starting feature work that needs isolation, before executing implementation plans, or when the user says "create a worktree", "isolated workspace", "work on feature branch separately". Creates isolated git worktrees with smart directory selection and safety verification.
---

# Using Git Worktrees

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

## Core Principle

**Systematic directory selection + safety verification = reliable isolation.**

## When to Use

- Starting a new feature that shouldn't interfere with current work
- Before executing an implementation plan
- Working on multiple features in parallel
- Testing changes in isolation
- When user requests isolated workspace

## Branch Naming Convention

Use conventional prefixes to indicate the type of work:

| Prefix | Use When | Example |
|--------|----------|---------|
| `feat/` | Adding new functionality | `feat/awards-extractor` |
| `fix/` | Fixing a bug | `fix/csv-export-encoding` |
| `refactor/` | Restructuring without behavior change | `refactor/modernize-codebase` |
| `chore/` | Maintenance tasks (deps, CI, etc.) | `chore/upgrade-dependencies` |
| `docs/` | Documentation only | `docs/api-reference` |
| `test/` | Adding/improving tests only | `test/analyzer-coverage` |

### Determining Branch Type

Ask yourself:
- **Is it a new capability?** → `feat/`
- **Is something broken?** → `fix/`
- **Same behavior, better code?** → `refactor/`
- **Everything else?** → `chore/`

### Collecting Branch Name

When creating a worktree, if the user doesn't specify a branch name, ask:

```
What should this branch be called?

1. What's the feature/task? (e.g., "awards extractor", "fix CSV encoding")
2. What type of work? (feat/fix/refactor/chore)
```

Then construct: `<type>/<kebab-case-name>`

**Examples:**
- "awards extractor" + feat → `feat/awards-extractor`
- "fix the CSV encoding bug" + fix → `fix/csv-encoding`
- "modernize to use uv and type hints" + refactor → `refactor/modernize-codebase`

## Directory Selection Process

Follow this priority order:

### 1. Check Existing Directories

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative
```

**If found:** Use that directory. If both exist, `.worktrees/` wins.

### 2. Check CLAUDE.md

```bash
grep -i "worktree.*director" CLAUDE.md 2>/dev/null
```

**If preference specified:** Use it without asking.

### 3. Ask User

If no directory exists and no CLAUDE.md preference:

```
No worktree directory found. Where should I create worktrees?

1. .worktrees/ (project-local, hidden)
2. ../worktrees/<project-name>/ (sibling directory)

Which would you prefer?
```

## Safety Verification

### For Project-Local Directories

**MUST verify .gitignore before creating worktree:**

```bash
# Check if directory pattern in .gitignore
grep -q "^\.worktrees/$" .gitignore || grep -q "^worktrees/$" .gitignore
```

**If NOT in .gitignore:**

1. Add appropriate line to .gitignore
2. Commit the change
3. Proceed with worktree creation

**Why critical:** Prevents accidentally committing worktree contents to repository.

### For Sibling Directory

No .gitignore verification needed - outside project entirely.

## Creation Steps

### Step 1: Detect Project Info

```bash
project=$(basename "$(git rev-parse --show-toplevel)")
main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
```

### Step 2: Create Worktree

```bash
# Determine full path based on selected location
# Example for .worktrees:
path=".worktrees/$BRANCH_NAME"

# Create worktree with new branch from main
git worktree add "$path" -b "$BRANCH_NAME" "$main_branch"
cd "$path"
```

### Step 3: Run Project Setup

For Python projects with uv:

```bash
# Python with uv (preferred)
if [ -f pyproject.toml ]; then
    uv sync
fi

# Alternative Python setups
if [ -f requirements.txt ] && [ ! -f pyproject.toml ]; then
    uv pip install -r requirements.txt
fi
```

### Step 4: Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# Python with uv
uv run pytest

# Or specific test subset for speed
uv run pytest tests/unit -q
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### Step 5: Report Location

```
Worktree ready at <full-path>
Branch: <branch-name>
Tests passing (N tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify .gitignore) |
| `worktrees/` exists | Use it (verify .gitignore) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md -> Ask user |
| Directory not in .gitignore | Add it immediately + commit |
| Tests fail during baseline | Report failures + ask |
| No pyproject.toml | Skip dependency install |

## Python/uv Specific Notes

### Virtual Environment

uv creates a `.venv` in the worktree automatically when you run `uv sync`. Each worktree gets its own isolated virtual environment.

```bash
# In worktree directory
uv sync                    # Creates .venv and installs deps
uv run pytest              # Runs in worktree's venv
uv run <your-cli> --help   # CLI works in isolation
```

### Shared Dependencies

The worktree shares the uv cache (`~/.cache/uv/`), so dependency installation is fast after the first time.

### IDE Setup

If using VS Code, open the worktree directory separately:
```bash
code .worktrees/feature-name
```

This gives you a separate VS Code window with its own Python interpreter.

## Example Workflow

```
User: "Let's start implementing the awards extractor in an isolated workspace"

# Check for existing worktree directory
ls -d .worktrees 2>/dev/null
# Not found

# Check CLAUDE.md
grep -i "worktree" CLAUDE.md
# No preference

# Ask user
"No worktree directory found. Where should I create worktrees?
1. .worktrees/ (project-local, hidden)
2. ../worktrees/<repo-name>/ (sibling directory)"

User: "1"

# Verify .gitignore
grep "worktrees" .gitignore
# Not found - need to add

# Add to .gitignore
echo ".worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: Add .worktrees to gitignore"

# Create worktree
mkdir -p .worktrees
git worktree add .worktrees/awards-extractor -b feat/awards-extractor main

# Setup
cd .worktrees/awards-extractor
uv sync

# Verify baseline
uv run pytest -q
# 42 passed in 3.21s

"Worktree ready at <repo>/.worktrees/awards-extractor
Branch: feat/awards-extractor
Tests passing (42 tests, 0 failures)
Ready to implement awards extractor"
```

## Managing Worktrees

### List Worktrees

```bash
git worktree list
```

### Remove Worktree

After merging or when done:

```bash
# From main repo
git worktree remove .worktrees/feature-name

# Or force remove if uncommitted changes
git worktree remove --force .worktrees/feature-name
```

### Prune Stale Worktrees

If worktree directory was manually deleted:

```bash
git worktree prune
```

## Common Mistakes

**Skipping .gitignore verification**
- Problem: Worktree contents get tracked, pollute git status
- Fix: Always grep .gitignore before creating project-local worktree

**Assuming directory location**
- Problem: Creates inconsistency, violates project conventions
- Fix: Follow priority: existing > CLAUDE.md > ask

**Proceeding with failing tests**
- Problem: Can't distinguish new bugs from pre-existing issues
- Fix: Report failures, get explicit permission to proceed

**Forgetting uv sync**
- Problem: Missing dependencies, import errors
- Fix: Always run `uv sync` after creating worktree

**Running commands in wrong directory**
- Problem: Affects main repo instead of worktree
- Fix: Verify `pwd` is in worktree before running commands

## Red Flags

**Never:**
- Create worktree without .gitignore verification (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Use `pip install` instead of `uv sync`

**Always:**
- Follow directory priority: existing > CLAUDE.md > ask
- Verify .gitignore for project-local directories
- Run `uv sync` after creating worktree
- Verify clean test baseline
- Report worktree location clearly

## Integration with Other Skills

### After `brainstorming`

When design is approved and implementation follows:
```
brainstorming (design approved)
    |
using-git-worktrees (create isolated workspace)
    |
executing-plans (implement in worktree)
```

### Before `executing-plans`

Create worktree before starting plan execution:
```
Plan ready in docs/plans/
    |
using-git-worktrees
    |
executing-plans (in worktree)
```

### With `finishing-a-development-branch`

When work is complete:
```
Implementation done
    |
finishing-a-development-branch
    |
If merged: Remove worktree
If PR/MR: Keep worktree until merged
```

### With `dispatching-parallel-agents`

Each agent can work in the same worktree (they share the branch) or dispatch can happen from main repo targeting worktree files.
