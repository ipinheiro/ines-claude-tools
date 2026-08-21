---
name: git-conventions
description: This skill should be used when committing changes, creating git commits, or when Claude mentions "let me commit", "I'll commit", "commit the changes". Triggers on "commit", "git commit", "save changes to git".
---

# Git Conventions

Create atomic, well-formed git commits for changes made in this session.

## The Rule

**Only commit files you touched. Review before committing. Never use broad adds.**

Announce: "I'm using the git-conventions skill to commit these changes."

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just `git add .`" | BLOCKED by hook. Add files explicitly. |
| "I'll commit everything" | Only commit files from THIS session. |
| "Pre-commit failed, I'll --no-verify" | Fix the issues. Never skip hooks without user approval. |
| "This is a quick fix, no need to check" | Always run the workflow. Always. |
| "I'll include multiple changes in one commit" | Each commit does ONE thing. Split it. |

## Workflow

### 1. Review Changes

Run these in parallel:

```bash
git status
git diff --staged
git diff
git log --oneline -5  # For commit message style reference
```

### 2. Identify Session Files

Check conversation history for files you edited/created:
- Look for Edit/Write tool calls
- Cross-reference with `git status` output

**If files appear in git status that you did NOT touch:**
- Warn the user: "These files were modified but not by me in this session: [list]"
- Ask if they should be included
- Default to excluding them

### 3. Check for Clean Tree

If nothing to commit:
- Report: "No changes to commit"
- Stop

### 4. Stage Files

**Stage specific files:**
```bash
git add path/to/file1 path/to/file2
```

**Quote paths with special characters:**
```bash
git add "src/app/[slug]/page.tsx"
```

**Review what you staged:**
```bash
git diff --staged
```

### 5. Compose Commit Message

```
<type>(<scope>): <subject>

[optional body]
```

**Subject line rules:**
- 50 characters or fewer
- Imperative mood: what the commit *does*, not what you *did*
- No trailing period
- Capitalise after the colon

**Types:**

| Type | When to use |
|------|-------------|
| `feat` | New feature or behaviour |
| `fix` | Bug fix |
| `refactor` | Code change that is neither fix nor feature |
| `chore` | Tooling, deps, build, CI |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |

**Before/After examples:**

| Bad | Good |
|-----|------|
| `fixed the thing with user login` | `fix(auth): redirect to login when session expires` |
| `WIP changes` | `refactor(models): extract validation logic into BaseModel` |
| `updated deps and fixed bug and added feature` | Three separate commits |

**Body (when to include):**
Add a body when the *why* isn't obvious. Wrap at 72 characters.

### 6. Execute Commit

```bash
git commit -m "$(cat <<'EOF'
type(scope): description

Optional body explaining why.
EOF
)"
```

### 7. Verify

```bash
git status
```

## The Atomic Commit Rule

Each commit should do **one thing** and be independently understandable.

Test: if you had to revert this commit alone, would it make sense?

Signs a commit is too large:
- Subject line has "and" in it
- Body has multiple unrelated bullet points
- Changes span multiple unrelated concerns

## Handling Pre-commit Failures

1. **Read the error output carefully**
2. **Fix the issues** (formatting, linting, type errors)
3. **Re-stage the fixed files**
4. **Try the commit again**

**NEVER use `--no-verify` unless:**
- The user explicitly approves
- The failure is a known false positive

## Safety Rules - CRITICAL

**NEVER run these without explicit user request:**
- `git reset --hard`
- `git checkout <older-commit>`
- `git restore` (on files you didn't author)
- `git push --force`
- `rm` on tracked files

**If unsure, STOP and ask.**

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll include that other file too" | Not your session, not your commit. Ask first. |
| "The message doesn't need to be precise" | Commit messages are permanent documentation. |
| "Pre-commit is being annoying" | Pre-commit exists for a reason. Fix the issue. |
| "I already know the changes" | Run git diff anyway. Verify assumptions. |
| "One big commit is easier" | Atomic commits are easier to review, revert, bisect. |

## Quick Reference

| Action | Command |
|--------|---------|
| Stage specific files | `git add file1 file2` |
| Stage with special chars | `git add "path/[slug]/file"` |
| Review staged changes | `git diff --staged` |
| Commit with message | `git commit -m "type(scope): msg"` |
| View unstaged changes | `git diff` |
| Check status | `git status` |
