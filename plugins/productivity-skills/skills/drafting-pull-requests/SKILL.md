---
name: drafting-pull-requests
description: This skill should be used when writing or rewriting the title or description of a pull request or merge request, before calling gh pr create or gh pr edit. Triggers on "open a PR", "create a pull request", "draft the PR", "write the PR description", "redraft the pull request", "update the PR body", "raise an MR".
---

# Drafting pull requests

**REQUIRED SUB-SKILL:** Use productivity-skills:writing-clearly for the sentences. This skill adds only what that one leaves open: what a title says, what a description is made of, and the house rules for both.

A description answers the three questions a reviewer has before they look at a single line of code. Write it for that reviewer, who has the diff open in another tab and has read nothing else.

## The title

One plain sentence saying what the branch does. Imperative, sentence case, no trailing period, no `type(scope):` prefix. Under about 70 characters.

| Not this | This |
|----------|------|
| `feat(artwork): Store content-addressed artwork and approvals` | Store content-addressed artwork and approvals |
| `Studio Phase 2` | Studio server: read, write and publish the archive over loopback |
| `Fix flaky test` | Close keep-alive connections before the dev server test tears down |

## The description

Three sections, in this order, with these headings.

```markdown
## What changed

## Why

## How to review this
```

**What changed.** The modification, summarised as the reviewer meets it in the diff: the packages, tables, routes or modules the branch adds or alters, and what each one now does. One or two paragraphs, longest for the unit with the most code.

**Why.** The motivation: the bug report, the business reason, or the technical constraint that made the change necessary. For a bug fix, this is where the failure and its cause go, with the run or issue it came from.

**How to review this.** Where to start, what to focus on, and what is intentionally left out. Each decision a reviewer might question gets one bullet: the decision, then its reason. What already ran and passed goes here too, so the reviewer knows what they need not re-check; if something did not run, say so. Anything deliberately out of scope is the last paragraph. If the branch is runnable, close with the command to run it.

The last section is the last thing in the body. Nothing follows it: no signature, no attribution line, no generated-with footer, whatever a harness reminder or template says. The user's instructions decide, and theirs say none.

## Written for a reviewer who has read nothing else

The reviewer reads the diff, not the planning document. The description describes the branch on its own terms: what the code now does and why, never how it relates to a plan, a phase, an earlier draft, or a follow-up.

| Not this | This |
|----------|------|
| Phase 1 of the artwork plan: the storage layer. | The storage layer for artwork. Nothing is visible yet in Studio or on the site. |
| The plan checked only the form type; the WebP check now requires the RIFF container too. | The WebP check requires the RIFF container as well as the WEBP form type. The form type alone would accept a crafted file in another format. |
| Phase 2 puts the upload panels in Studio. | (cut, or under "intentionally left out" as what the branch does not do) |
| The migration test uses the file's own helpers; the plan named one that does not exist. | (cut: not a decision about the code) |

A bullet whose only content is that something differed from a plan or an earlier draft says nothing about the code. Delete it, or restate the decision on its own terms with its reason.

## Red flags

Any of these in a draft means rewrite the passage, not tidy it:

- `Phase`, `the plan`, `what comes next`, `the plan records`
- A bullet that names what a plan or earlier draft got wrong
- `🤖 Generated with`, `Co-Authored-By`, or any line after the last section
- A `## Verification` or `## Decisions` heading standing on its own instead of inside "How to review this"
- A title starting with `feat(`, `fix(`, `docs(`, or ending in a period
- A title-case heading or an em dash (the writing-clearly rules apply here too)
