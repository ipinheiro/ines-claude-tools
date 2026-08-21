---
allowed-tools:
  - Read
  - Write
  - Bash(git status:*)
  - Bash(git log:*)
  - Bash(git diff:*)
description: Create or update HANDOFF.md to enable seamless context transfer to a fresh agent session
---

# Handoff Document Generator

Create or update HANDOFF.md to enable seamless context transfer to a fresh agent session.

## Process

1. **Check for existing handoff**: Look for HANDOFF.md in the project root
2. **If it exists**: Read it first to preserve historical context and patterns
3. **Gather current state**: Review recent work, git status/log, and any relevant files

## Document Structure

```markdown
# Handoff Document

## Goal
[One clear sentence describing the objective]

## Context
[Brief project background - tech stack, key files, architecture decisions]

## Progress
- [x] Completed items
- [ ] In-progress items

## What Worked
- [Successful approaches worth continuing]

## What Didn't Work
- [Failed approaches with brief explanation - prevents repeated mistakes]

## Next Steps
1. [Immediate next action - be specific]
2. [Subsequent actions]

## Key Files
- `path/to/file` - [why it matters]

## Open Questions
- [Unresolved decisions or blockers]
```

4. **Save** to `./HANDOFF.md`
5. **Report**: Confirm the file path and suggest: "Start a new conversation with: `Read HANDOFF.md and continue the work`"
