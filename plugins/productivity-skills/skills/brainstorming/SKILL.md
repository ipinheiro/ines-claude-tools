---
name: brainstorming
description: This skill should be used when the user asks to "brainstorm", "design a feature", "plan a pipeline", "architect a solution", "think through", or BEFORE any creative work involving new features, data pipelines, ML workflows, API endpoints, or system modifications. Use when tempted to "just start coding".
---

# Brainstorming Ideas Into Designs

Turn ideas into fully formed designs through collaborative dialogue. **Design BEFORE code. Always.**

## The Rule

**BEFORE writing any code for a new feature, use this skill.** No exceptions.

Announce: "I'm using the brainstorming skill to design this before implementation."

## Red Flags

These thoughts mean STOP - you need to brainstorm first:

| Thought | Reality |
|---------|---------|
| "This is simple, I'll just code it" | Simple things become complex. Design first. |
| "I know how to do this" | You know A way. Brainstorming finds the BEST way. |
| "Let me quickly prototype" | Prototypes become production. Design first. |
| "The user wants it fast" | Fast wrong is slower than slow right. Design first. |
| "I'll refactor later" | You won't. Design now. |

## When to Use

**MUST use before:**
- Building data pipelines or ETL workflows
- Creating ML/AI features or Pydantic AI agents
- Designing API endpoints or CLI commands
- Adding Pydantic models or database schemas
- Refactoring existing systems
- Any feature that touches multiple files

## The Process

### 1. Gather Context

**BEFORE asking questions:**
- Review project structure, existing patterns, and recent commits
- Identify relevant existing code (models, agents, utilities)
- Note the tech stack constraints (Pydantic, structlog, async patterns)

### 2. Understand the Idea

Ask questions **one at a time**:
- Prefer multiple choice when possible (easier to answer)
- Focus on: purpose, data flow, success criteria, edge cases
- For data work: input sources, transformations, output format, validation needs
- For ML/agents: model selection, prompt strategy, retry/fallback handling

**Example questions:**
- "Should this be a Pydantic AI agent or a simpler function? (a) Agent - needs LLM reasoning (b) Function - deterministic logic"
- "Where does the input data come from? (a) Snowflake (b) S3 (c) API (d) Local files"
- "What happens when validation fails?"

**One question per message. Wait for answer before next question.**

### 3. Explore Approaches

Present 2-3 approaches with trade-offs:
- **Lead with recommended option** and explain why
- Consider: complexity, performance, maintainability, testing ease
- For data pipelines: batch vs streaming, sync vs async
- For agents: single agent vs multi-agent, structured vs unstructured output

**Force a choice:** "Which approach: A, B, or C?"

### 4. Present the Design

Once approach is chosen, present in sections (200-300 words each):

1. **Overview** - What it does, why this approach
2. **Data/Control Flow** - Input -> processing -> output
3. **Models & Schemas** - Pydantic models, database tables
4. **Error Handling** - Validation, retries, fallbacks
5. **Testing Strategy** - Unit tests, mocks, integration tests

**Check after each section:** "Does this look right so far?"

## After the Design

### Save the Design Document

**MUST save** to `docs/plans/YYYY-MM-DD-<topic>-design.md`:

```markdown
# <Feature> Design

## Goal
[One sentence]

## Approach
[Why this approach over alternatives]

## Components
[Key modules, classes, functions]

## Data Flow
[Input -> transformations -> output]

## Models
[Pydantic models with key fields]

## Error Handling
[Validation, retries, edge cases]

## Testing
[Test strategy and key scenarios]

## Open Questions
[Unresolved decisions]
```

**Commit the design document before any implementation.**

### Handoff to Implementation

After design is saved:

"Design complete and saved to `docs/plans/<filename>.md`.

Next steps:
1. Use `writing-plans` skill to create detailed implementation plan
2. Use `using-git-worktrees` skill to create isolated workspace
3. Use `executing-plans` skill to implement

Ready to continue to planning?"

## Key Principles

| Principle | Meaning |
|-----------|---------|
| **One question at a time** | Never overwhelm with multiple questions |
| **Multiple choice preferred** | Reduce cognitive load on user |
| **YAGNI ruthlessly** | Cut unnecessary features. If in doubt, leave it out. |
| **Follow existing patterns** | Match project conventions (Pydantic AI, structlog, async) |
| **Incremental validation** | Present design in chunks, confirm each |
| **Data-first thinking** | For pipelines, start with data shape and work outward |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "User wants quick answer" | Quick wrong answer wastes more time than proper design |
| "I'll design as I code" | You'll build the first thing that works, not the best thing |
| "It's just a small change" | Small changes to complex systems need design too |
| "The design is obvious" | If it's obvious, documenting it takes 2 minutes. Do it. |
| "I can refactor later" | Technical debt compounds. Design now. |

## Integration with Other Skills

```
brainstorming (this skill)
    | saves design document
writing-plans (detailed implementation plan)
    |
using-git-worktrees (isolated workspace)
    |
executing-plans (implementation)
```

**NEVER skip straight to implementation.** The design document is the contract.
