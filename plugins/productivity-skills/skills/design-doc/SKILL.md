---
name: design-doc
description: Use when creating or refining technical design documents. Invoked with /design-doc for new designs or /design-doc refine <path> for existing ones. Guides structured design through iterative collaboration with critical review.
---

# Design Doc Skill

Create and refine technical design documents through structured, iterative collaboration. Produces two artifacts: the main design document and a chronological decision log.

## Invocation

- `/design-doc` or `/design-doc new` — Create a new design document
- `/design-doc refine <path>` — Refine an existing design document

## Output Files

- `docs/plans/YYYY-MM-DD-<topic>-design.md` — Main design document
- `docs/plans/YYYY-MM-DD-<topic>-decisions.md` — Chronological decision log

## Process Overview

### Creating a New Design

**Phase 1: Context Gathering**
- Read existing docs, recent commits, related code
- Ask clarifying questions one at a time (prefer multiple choice)
- Understand: scope, constraints, existing infrastructure, success criteria

**Phase 2: Initial Draft**
- Present architecture in sections (200-300 words each)
- After each section ask: "Does this look right so far?"
- Write to file incrementally — don't wait until the end
- Log each significant decision to the decisions file

**Phase 3: Critical Review**
After drafting, proactively cycle through all critical lenses (see below). Do not wait for user to request critique.

**Phase 4: Refinement**
- Address issues surfaced by critical review
- Log each change to decisions file with rationale
- Commit after each significant change

**Phase 5: Companion Docs**
When warranted, suggest (wait for approval before creating):
- Post-POC/deferred features parking lot
- Audience-specific overview (e.g., for non-technical stakeholders)

### Refining an Existing Design

1. Load context: Read design doc, decisions log, recent commits
2. Ask: "What aspect needs refinement?" (full review / specific concern / scope review / cross-check)
3. Apply relevant lenses, surface issues one at a time
4. For each change: explain issue, propose fix, wait for approval
5. After approval: edit doc, append to decisions log, commit
6. Check companion docs for drift if they exist

## Standard Template

```markdown
# <Title>

## Overview
Problem statement and solution summary (2-3 paragraphs)

## Glossary
Domain terms readers might not know

## Architecture
- System context diagram (Mermaid)
- Component responsibilities
- Data flow

## Data Model
- Schema definitions
- Constraints and invariants
- Migration considerations

## API Contracts
- Endpoints
- Request/response shapes
- Error handling

## Security & Access Control
- Authentication approach
- Authorization model
- Input validation and sanitization

## Error Handling & Degradation
- Failure modes
- Retry behavior
- User-facing error states

## Open Questions
- Organized by owner/team
- Blocking vs non-blocking

## Implementation Phases
- In scope for initial delivery
- Explicitly deferred
```

Mark sections N/A if not applicable, but explicitly consider each.

## Decision Log Format

Append-only chronological entries:

```markdown
### YYYY-MM-DD HH:MM — <Short title>

**Context:** Why this decision came up

**Options considered:**
1. Option A — tradeoffs
2. Option B — tradeoffs

**Decision:** Which option and why

**Consequences:** What this enables or constrains
```

## Critical Lenses

Apply proactively after drafting. If context is missing to apply a lens, ask for it — don't skip or assume.

### Loading Lenses

1. Apply all **core lenses** defined below
2. Check for `.claude/design-doc.local.md` in the project — if present, load and apply **project-specific lenses** defined there
3. During design work, if a new lens emerges, ask: "Should this lens be project-specific or universally useful?"
   - **Project-specific:** Append to `.claude/design-doc.local.md`
   - **Universal:** Append to this skill file (`~/.claude/skills/design-doc/SKILL.md`)

### Core Lenses

#### YAGNI Lens
- Is this needed for the stated goal, or speculative?
- Could this be deferred to a later phase?
- Am I building for hypothetical future requirements?

#### Security Lens
- What are the trust boundaries?
- Where does untrusted input enter? How is it validated?
- What authentication/authorization model applies?

#### Concurrency Lens
- Can multiple actors modify the same data?
- What happens if state changes between read and write?
- Are there race conditions in the proposed flow?

#### Data Flow Lens
- Who writes to each data store? Is ownership clear?
- Am I storing derived values that could be calculated?
- Is mutable state necessary, or could this be append-only?

#### Failure Modes Lens
- What external dependencies can fail? How does the system degrade?
- How does the user know something went wrong?
- What's the recovery path?

#### Existing Infrastructure Lens
- What's already deployed that could be leveraged?
- Am I introducing new dependencies when existing ones would work?
- Do I understand the domain's canonical identifiers and data models?

### Adding New Lenses

When a new lens emerges during design work:

1. **Identify it explicitly:** "This seems like a recurring concern — should we formalize it as a lens?"
2. **Ask scope:** "Is this lens project-specific (e.g., 'GDPR Lens' for EU user data) or universally useful?"
3. **Write and store:**
   - **Project-specific:** Append to `.claude/design-doc.local.md` in the project
   - **Universal:** Append to `~/.claude/skills/design-doc/SKILL.md` under Core Lenses

#### Project-Local Lenses File Format

Create `.claude/design-doc.local.md` in the project root:

```markdown
# Project-Specific Design Lenses

## <Lens Name> Lens
- Question 1 this lens asks
- Question 2 this lens asks
- What to watch for

## <Another Lens> Lens
- ...
```

This file is read automatically when the skill is invoked in the project.

## Behavioral Principles

**Communication**
- One question at a time — don't overwhelm
- Multiple choice when options are clear; open-ended when exploring
- Lead with recommendation and reasoning
- Be direct about uncertainty: "I don't have enough context to assess X"

**Writing**
- Write to file incrementally
- Commit after each significant decision
- Keep review sections to 200-300 words
- Glossary entries for terms a peer engineer might not know

**Decision Making**
- Log every significant choice, including rejected alternatives
- "No decision" is a decision — if deferring, log why
- When user corrects an assumption, acknowledge it and note the lesson

**Critique**
- Apply all lenses proactively after drafting
- Don't skip a lens — ask for context if needed
- Distinguish "wrong" from "needs clarification" from "could be simpler"
- Challenge scope aggressively but accept user's final call

**Scope Management**
- Propose post-POC parking lot when deferring features
- Suggest companion docs when audience diverges
- Always wait for approval before creating new files

**Course Correction**
- When wrong, say so: "I assumed X, but you're right that Y"
- Re-read the spec when uncertain rather than guessing
- Propose simplifications — user can reject
