---
description: This skill should be used when executing a written implementation plan in the current session, in batches with review checkpoints. Triggers on "execute the plan", "implement the design", "follow the plan", "start implementation". Use when tempted to "just implement without a plan".
---

# Executing plans in batches

Use this when executing a plan **inline in this session**. If the plan is task-decomposed and you have subagents, `superpowers:subagent-driven-development` is the better path: a fresh subagent per task keeps context clean and gives a two-stage review. This skill is for when you want the work in front of you.

**The rule: follow the plan exactly, verify every task, stop between batches.**

Announce: "I'm using the executing-plans skill to implement this plan."

**No plan?** Use `workflow-skills:writing-plans` first.

## Pre-flight

Complete this before Task 1. It is the part people skip and the part that prevents rework.

**1. Isolated workspace.** Use `workflow-skills:using-git-worktrees`. Never start implementation on `main` without explicit consent.

**2. Green baseline.** Run the test suite before changing anything. A failure you inherit will otherwise look like a failure you caused.

**3. Load the stack skills.** `python-dev:python-best-practices` for Python, `python-dev:python-test-quality` when writing tests, `python-dev:dbt-python-integration` for dbt.

**4. Scan the whole plan for parallel work.** Tasks are independent when they touch different files, no data flows between them, and order does not matter.

| Pattern | Action |
|---------|--------|
| Tasks 3, 5, 7 each create a separate module | Dispatch together |
| Test files for three unrelated packages | Dispatch together |
| Task 4 imports a model defined in Task 3 | Sequential |

If the plan has 5 or more tasks, some are usually parallelizable. Use `productivity-skills:dispatching-parallel-agents` for the batch, issuing all `Agent` calls in one message.

**5. Announce readiness** and only then start:

```
Pre-flight complete:
- Worktree: ../feature-x
- Baseline: 84 passing
- Skills loaded: python-best-practices, python-test-quality
- Parallel: tasks 3, 5, 7 (independent modules)
```

## The loop

**Read the plan fully and review it critically before executing anything.** Are the dependencies available? Are the interfaces specified? Is any step ambiguous? Raise concerns now, one at a time. Once clear, create a task list with `TaskCreate` covering every plan task.

Then, in batches:

| Task type | Batch size |
|-----------|------------|
| Default | 3 |
| Complex, such as new services or pipelines | 2 |
| Mechanical, such as config, imports, renames | 5 |

For each task: mark it `in_progress` with `TaskUpdate`, follow the steps exactly as written, run the verification the plan specifies, and only then mark it `completed`. Never mark a task complete on unverified work.

At the end of a batch, report what changed and paste the actual verification output, not a summary of it:

```
## Batch 1 complete

Implemented
- Award model in src/pkg/models.py
- Year validator with 1900..current+1 bounds
- 3 tests in tests/test_models.py

Verification
$ uv run pytest tests/test_models.py
3 passed in 0.42s

$ uv run pyright src/pkg/models.py
0 errors

Next batch: extraction logic, pipeline wiring, integration test.
```

**Then wait.** Do not roll into the next batch automatically.

## Finishing

After every task is done: run the full suite, run the type checker, smoke test the entry point if there is one, and summarise files changed, dependencies added, and any deviation from the plan with its justification.

Then hand off to `/code-review-orchestrator:deep-review` or `/code-review-orchestrator:mr-review`, and `workflow-skills:finishing-a-development-branch`.

## Stop immediately when

A dependency is missing from `pyproject.toml`. A test fails unexpectedly after your change. A step is ambiguous. Credentials are not configured. Validation fails in a way you cannot explain.

Ask rather than guess, and make the question answerable:

```
Blocked on task 2: "Add the query for endorsements".

The plan doesn't name the source table. Candidates I can see:
(a) PRODUCT_DESCRIPTION
(b) MARKETING_COPY

Which one?
```

## Red flags

| Thought | Reality |
|---------|---------|
| "I'll skip pre-flight, this is quick" | Quick work done wrong is rework |
| "No worktree needed for a small change" | Small changes on main become merge conflicts |
| "This is basically what the plan says" | Basically is not exactly |
| "I'll verify at the end" | You will have built on a broken foundation |
| "I know a better way" | Propose it. Do not silently deviate from an approved plan |
| "These tasks aren't parallelizable" | Did you scan the whole plan? Justify it in the announcement |
| "This blocker is minor" | Stop and ask. Minor blockers compound |

Type errors during execution go to `python-dev:fixing-type-errors`. Never reach for `# type: ignore`.
