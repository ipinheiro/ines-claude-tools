# Code Review Orchestrator

Multi-agent code review with specialized agents for Python and TypeScript. Each command dispatches the right agents for the languages in your diff, runs them in parallel, and consolidates findings into a single educational report.

## Why This Exists

A single reviewer can't hold code quality, type safety, logic correctness, security, and test quality in their head simultaneously. This plugin splits code review into orthogonal dimensions — each handled by an agent that only cares about one thing — then merges the results.

The output is educational: every finding explains *why* it matters, shows the current code, suggests a fix, and links to a learning resource. The goal is to help colleagues learn, not just point out problems.

## Architecture

```
/mr-review, /deep-review, or /repo-review
│
├── Detect languages in diff (.py → Python agents, .ts/.tsx → TypeScript agents)
│
├── Dispatch agents in parallel ─────────────────────────────
│   │                                                        │
│   │  Python                    TypeScript       Always     │
│   ├── code-quality-reviewer    ts-react-reviewer           │
│   ├── type-discipline-reviewer ts-type-reviewer            │
│   ├── logic-verifier                                       │
│   ├── test-quality-reviewer    structure-reviewer           │
│   └──────────────────────────  security-reviewer ──────────│
│
├── Validate findings against diff scope
├── Deduplicate, group by file, sort by line
└── Write report to docs/reviews/
```

## Commands

| Command | Scope | When to Use |
|---------|-------|-------------|
| `/mr-review` | Diff between current branch and upstream | Before submitting a GitLab merge request |
| `/deep-review` | Working changes (uncommitted, staged, or branch) | Quick review of current work |
| `/repo-review` | Entire repository or scoped directories | Planning a major refactor |

### `/mr-review`

Reviews only code that appears in the merge request diff. Produces findings formatted for pasting into GitLab MR comments.

```bash
# Auto-detect fork point
/mr-review

# Explicit base branch
/mr-review --base main

# Review specific files only
/mr-review src/pipeline.py src/models/

# Sequential agent execution (see progress one at a time)
/mr-review --sequential
```

### `/deep-review`

Reviews your working changes — uncommitted modifications, staged files, or the full branch diff.

```bash
/deep-review
/deep-review --staged
```

### `/repo-review`

Full repository review that inventories files, batches them by dependency, and dispatches agents per batch. Designed for refactor planning.

```bash
/repo-review
/repo-review src/pipeline/ src/models/
```

## Agents

### Python Agents

| Agent | What It Reviews |
|-------|----------------|
| **code-quality-reviewer** | Coding standards: structlog patterns, error handling, code organization |
| **type-discipline-reviewer** | Type hints: Any abuse, missing annotations, redundant isinstance, type narrowing |
| **logic-verifier** | Correctness: execution paths, boundary conditions, contracts, silent failures |
| **test-quality-reviewer** | Tests: tautological tests, framework testing, redundant coverage, missing behavioral tests |

### TypeScript Agents

| Agent | What It Reviews |
|-------|----------------|
| **ts-react-reviewer** | React/TypeScript: hooks discipline, component patterns, TanStack Query, Zustand, forms |
| **ts-type-reviewer** | Type safety: API boundaries, unsafe casts, `any` abuse, discriminated unions, Zod alignment |

### Shared Agents (always dispatched)

| Agent | What It Reviews |
|-------|----------------|
| **structure-reviewer** | SOLID principles, function decomposition, parameter counts, single responsibility |
| **security-reviewer** | Injection flaws, secrets in code, auth issues, data exposure, path traversal, XSS |

All agents have access to Context7 for verifying framework behavior before making claims.

## Skills

| Skill | Description |
|-------|-------------|
| **receiving-code-review** | How to handle reviewer feedback — verify claims before implementing, evaluate technically rather than emotionally |

## Output Format

Reports are saved to `docs/reviews/` with findings grouped by file, sorted by line number:

```
docs/reviews/mr-review-feature-auth-2026-03-04.md
docs/reviews/deep-review-2026-03-04.md
docs/reviews/repo-review-2026-03-04.md
```

Each finding includes:
- **Severity** (Critical / Important / Suggestion)
- **Why this matters** — the impact of not fixing it
- **Current code** — the exact lines from the diff
- **Suggested fix** — concrete replacement code
- **Learn more** — educational context

Findings outside the diff scope are collected in a "Discarded Findings" section for future reference.

## Integration

```
/repo-review                        (find problems across the repo)
    │
/refactor --from-review ...         (fix them with refactor-engine)
    │
/mr-review                          (review the fix branch)
    │
finishing-a-development-branch      (ship it)
```

## Install

```bash
claude plugin install code-review-orchestrator@claude-code-tools
```
