---
name: finishing-a-development-branch
description: This skill should be used when the user says "finish the branch", "ready to merge", "create a PR", "create an MR", "complete the work", "wrap up", or when implementation is complete. Use when tempted to merge without verification or skip the MR/PR.
---

# Finishing a Development Branch

Guide completion of development work by presenting clear options and handling the chosen workflow.

## The Rule

**Verify tests -> Summarize changes -> Present options -> Execute choice.** No shortcuts.

Announce: "I'm using the finishing-a-development-branch skill to complete this work."

## Red Flags

These thoughts mean STOP - you're about to skip important steps:

| Thought | Reality |
|---------|---------|
| "Tests probably pass" | Run them. "Probably" isn't verified. |
| "I'll skip the MR/PR" | MRs/PRs create audit trail. Don't skip. |
| "Just merge it quickly" | Verify tests first. Always. |
| "I'll clean up later" | Clean up now or it won't happen. |
| "No one reviews anyway" | Code review catches bugs. Request it. |

## When to Use

- All tasks from `executing-plans` skill are complete
- User says "done", "ready to merge", "create PR", "create MR", "wrap up"
- Ready to integrate work back to main branch

**Tests MUST pass before proceeding.** This is not negotiable.

## The Process

### Step 1: Verify Tests

Before presenting options, verify tests pass:

```bash
uv run pytest
```

**If tests fail:**
```
Tests failing (N failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR/MR until tests pass.
```

Stop here. Do not proceed to Step 2.

**If tests pass:** Continue to Step 2.

### Step 2: Detect Git Platform

Check which platform the repo uses:

```bash
# Check remote URL
git remote get-url origin
```

- **GitLab** (`gitlab.com` or self-hosted): Use `glab` for MRs
- **GitHub** (`github.com`): Use `gh` for PRs

### Step 3: Summarize Changes

Show what was accomplished:

```bash
# Changes since branching from main
git log main..HEAD --oneline

# Files changed
git diff main --stat
```

```
## Summary of Changes

### Commits
- abc1234 feat: Add awards_extractor_agent
- def5678 feat: Integrate into copy_workflow
- ghi9012 test: Add unit and integration tests

### Files Changed
- src/pkg/extraction/awards_extractor.py (new)
- src/pkg/models.py (modified)
- src/pkg/workflow.py (modified)
- tests/test_awards_extractor.py (new)

### Verification
$ uv run pytest
42 passed in 3.21s
```

### Step 4: Present Options

Present exactly these 4 options (adapt terminology to platform):

**For GitLab:**
```
Implementation complete. What would you like to do?

1. Merge back to main locally
2. Push and create a Merge Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

**For GitHub:**
```
Implementation complete. What would you like to do?

1. Merge back to main locally
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 5: Execute Choice

#### Option 1: Merge Locally

```bash
# Switch to main
git checkout main

# Pull latest
git pull

# Merge feature branch
git merge <feature-branch>

# Verify tests on merged result
uv run pytest

# If tests pass, delete feature branch
git branch -d <feature-branch>
```

Report: "Merged to main. Branch deleted."

#### Option 2: Push and Create MR/PR

**For GitLab (using glab):**

```bash
# Push branch
git push -u origin <feature-branch>

# Create MR with structured description
glab mr create --title "<title>" --description "$(cat <<'EOF'
## Summary
- <what changed>
- <why it changed>

## Test Plan
- [ ] Unit tests pass: `uv run pytest`
- [ ] Type check passes: `uv run pyright`
- [ ] Manual smoke test: `uv run <your-cli> <command>`

EOF
)"
```

Report: "MR created: <url>"

**For GitHub (using gh):**

```bash
# Push branch
git push -u origin <feature-branch>

# Create PR with structured body
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
- <what changed>
- <why it changed>

## Test Plan
- [ ] Unit tests pass: `uv run pytest`
- [ ] Type check passes: `uv run pyright`
- [ ] Manual smoke test: `uv run <your-cli> <command>`

EOF
)"
```

Report: "PR created: <url>"

#### Option 3: Keep As-Is

Report: "Keeping branch `<name>` for later. No changes made."

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch: <name>
- Commits: <list>

Type 'discard' to confirm.
```

Wait for exact confirmation "discard".

If confirmed:
```bash
git checkout main
git branch -D <feature-branch>
```

Report: "Branch deleted. Work discarded."

## GitLab vs GitHub Commands

| Action | GitLab (glab) | GitHub (gh) |
|--------|---------------|-------------|
| Create MR/PR | `glab mr create` | `gh pr create` |
| List MRs/PRs | `glab mr list` | `gh pr list` |
| View MR/PR | `glab mr view` | `gh pr view` |
| Merge MR/PR | `glab mr merge` | `gh pr merge` |
| Check CI status | `glab ci status` | `gh run list` |

## Quick Reference

| Option | Merge | Push | Keep Branch | Delete Branch |
|--------|-------|------|-------------|---------------|
| 1. Merge locally | Yes | - | - | Yes |
| 2. Create MR/PR | - | Yes | Yes | - |
| 3. Keep as-is | - | - | Yes | - |
| 4. Discard | - | - | - | Yes (force) |

## Integration with Other Skills

### After `executing-plans`

When all tasks complete in `executing-plans`, that skill hands off here:

```
executing-plans (all tasks done)
    |
finishing-a-development-branch
    |
Verify -> Summarize -> Present options -> Execute
```

### After `brainstorming`

If brainstorming led directly to implementation without a formal plan:

```
brainstorming (design complete)
    |
Implementation (ad-hoc)
    |
finishing-a-development-branch
```

### With `dispatching-parallel-agents`

If parallel agents were used for implementation, ensure all agent work is integrated before finishing:

```
dispatching-parallel-agents (all agents done)
    |
Review & integrate all changes
    |
finishing-a-development-branch
```

## Common Mistakes

**Skipping test verification**
- Problem: Merge broken code, create failing MR/PR
- Fix: Always run `uv run pytest` before presenting options

**Wrong CLI tool**
- Problem: Using `gh` on GitLab repo or vice versa
- Fix: Check remote URL first, use appropriate tool

**Open-ended questions**
- Problem: "What should I do next?" is ambiguous
- Fix: Present exactly 4 structured options

**No confirmation for discard**
- Problem: Accidentally delete work
- Fix: Require typed "discard" confirmation

**Forgetting to pull main**
- Problem: Merge conflicts after merging
- Fix: Always `git pull` on main before merging

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on merged result
- Delete work without typed confirmation
- Force-push without explicit request
- Use wrong platform CLI (glab vs gh)

**Always:**
- Verify tests before offering options
- Detect platform from remote URL
- Present exactly 4 options
- Summarize what changed
- Get typed confirmation for Option 4
