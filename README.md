# ines-claude-tools

![Claude Code](https://img.shields.io/badge/Claude_Code-plugins-blueviolet?logo=anthropic&logoColor=white)
![Plugins](https://img.shields.io/badge/plugins-7-blue)
![Skills](https://img.shields.io/badge/skills-24-green)
![Commands](https://img.shields.io/badge/commands-6-orange)
![Agents](https://img.shields.io/badge/agents-17-red)
![Pine tree approved](https://img.shields.io/badge/%F0%9F%8C%B2-approved-2ea44f)

A [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) for Claude Code. It ships seven plugins containing [skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents), and [hooks](https://code.claude.com/docs/en/hooks).

Verified against Claude Code v2.1.222.

## Contents

**Using it**
- [Installation](#installation) - add the marketplace, install plugins, activate
- [Keeping up to date](#keeping-up-to-date) - auto-update is off by default
- [Invoking what you installed](#invoking-what-you-installed) - namespacing, and what Claude loads on its own
- [Command reference](#command-reference) - every command, with [`/branch-report`](#branch-report), [`/analyse`](#analyse) and [`/type-safety-audit`](#type-safety-audit) in detail
- [Skill workflow](#skill-workflow) - how the workflow skills chain together

**What is in here**
- [Repository layout](#repository-layout)
- [Tool hierarchy](#tool-hierarchy) - every skill, command, agent and hook
- [Hooks](#hooks) - what runs automatically and what it blocks
- [How this relates to Superpowers](#how-this-relates-to-superpowers) - why some skills are thin layers

**Changing it**
- [Changing a plugin](#changing-a-plugin) - test, validate, version, ship
- [Authoring notes](#authoring-notes) - frontmatter, namespacing, substitutions
- [Resources](#resources)

## Repository layout

| Path | Contents |
|------|----------|
| `.claude-plugin/marketplace.json` | The marketplace catalog. One entry per plugin |
| `plugins/` | The seven plugin packages |
| `tests/` | Tests for the hook scripts. `uv run pytest` |

Documentation is not vendored here. Component schemas change often, so `CLAUDE.md` points at [code.claude.com/docs](https://code.claude.com/docs/en/) and a local snapshot would only go stale and override it.

## How this relates to Superpowers

Several skills here have a same-named counterpart in Anthropic's [Superpowers](https://code.claude.com/docs/en/discover-plugins) plugin: planning, executing plans, worktrees, TDD, receiving review feedback. Those built-ins are good, and this marketplace does not try to replace them.

**The rule is: defer to the built-in for the general discipline, add only what is specific to how I work.** When both are installed, both load, so anything restated here is duplicated context at best. Worse, when the two disagree, Claude gets contradictory instructions and picks one arbitrarily.

What earns its place:

- **A different artefact shape.** `writing-plans` defers to `superpowers:writing-plans` for what a task looks like, then changes one thing: plans are a directory of phase files rather than a single document, because our work spans sessions and a phase boundary is a natural place to stop, commit, and resume.
- **Stack knowledge the built-in cannot have.** `verifying-python-review-feedback` leaves the review discipline to Superpowers and covers only what a reviewer gets wrong about *our* stack: whether a suggested library survives the Snowflake connector, whether a validation is load-bearing given where the data originates.
- **Steps the built-in skips.** `executing-plans` keeps a mandatory pre-flight (worktree, green baseline, load the stack skills, scan for parallel work) that Superpowers has no equivalent of, because its own version defers to `subagent-driven-development` instead.
- **Tooling that is ours.** `uv`, `shucks`, dbt, and Snowflake are not general knowledge.

What does not earn its place, and gets deleted when found: a restatement of a built-in's process, a second copy of a rationalization table, or guidance that contradicts a built-in without saying so.

When adding a skill, check whether Superpowers or a [bundled skill](https://code.claude.com/docs/en/commands) already covers it. If it mostly does, write the thin layer on top and say in the first paragraph which skill you are deferring to and what you are adding.

## Tool hierarchy

Everything this marketplace installs, grouped by plugin. Versions come from each plugin's `.claude-plugin/plugin.json`.

```
ines-claude-tools/                          marketplace: ines-claude-tools
│
├── python-dev                     v1.0.0   10 skills · 7 agents · 3 hooks
│   ├── skills/
│   │   ├── python-best-practices           typing, Pydantic, error handling, match dispatch
│   │   ├── fixing-type-errors              resolve pyright/ty/mypy errors without suppressions
│   │   ├── python-test-quality             pytest structure, fixtures, Hypothesis
│   │   ├── test-review                     audit existing tests for tautology and weak coverage
│   │   ├── type-safety-audit               orchestrates the 7 auditor agents below
│   │   ├── uv-pyproject                    pyproject.toml and uv workspace configuration
│   │   ├── fastapi-patterns                routers, Depends, lifespan, HTTPException
│   │   ├── dbt-python-integration          dbtRunner, manifest.json, run_results.json
│   │   ├── using-shucks                    Snowflake connection and credential handling
│   │   └── writing-dagster-pipelines       assets, checks, dbt, scheduling, and deployment on the centralised Dagster platform
│   ├── agents/
│   │   ├── any-usage-auditor               every Any annotation, with a concrete replacement
│   │   ├── unstructured-returns-auditor    bare dicts and dict[str, Any] returns
│   │   ├── magic-strings-auditor           string literals used as discriminators
│   │   ├── config-access-auditor           untyped config access and orphaned keys
│   │   ├── hardcoded-values-auditor        scattered numeric, path, and ID literals
│   │   ├── brittle-paths-auditor           __file__ and .parent.parent chains
│   │   └── environment-coupling-auditor    scattered os.getenv and hardcoded env names
│   └── hooks/
│       ├── python-uv-guard.py              PreToolUse: blocks bare `python`, points to uv
│       ├── ruff-before-add.py              PreToolUse: lints Python files before `git add`
│       │   └── no-inline-imports.yml       ast-grep rule used by the above
│       └── skill-detector.py               UserPromptSubmit: injects skill reminders
│
├── code-review-orchestrator       v1.0.0   3 commands · 1 skill · 10 agents
│   ├── commands/
│   │   ├── deep-review                     review uncommitted, staged, or branch changes
│   │   ├── mr-review                       GitLab MR review producing pasteable comments
│   │   └── repo-review                     whole-repo review for refactor planning
│   ├── skills/
│   │   └── verifying-python-review-feedback  check a reviewer's claim against the stack
│   └── agents/
│       ├── code-quality-reviewer           logging, error handling, organisation      [py]
│       ├── type-discipline-reviewer        Any abuse, missing annotations, narrowing   [py]
│       ├── logic-verifier                  execution paths, boundaries, contracts      [py]
│       ├── test-quality-reviewer           tautological and framework-testing tests    [py]
│       ├── concurrency-reviewer            asyncio and Promise correctness         [py + ts]
│       ├── structure-reviewer              decomposition and SOLID                 [py + ts]
│       ├── ts-react-reviewer               hooks, TanStack Query, Zustand, forms       [ts]
│       ├── ts-type-reviewer                API boundaries, casts, Zod alignment        [ts]
│       ├── security-reviewer               injection, secrets, authz, path traversal   [all]
│       └── repo-review-planner             inventory and batching for /repo-review     [all]
│
├── dev-commands                   v1.0.0   3 commands
│   └── commands/
│       ├── analyse                         multi-mode analysis for data science codebases
│       ├── branch-report                   stale branch detection and cleanup commands
│       └── handoff                         write HANDOFF.md for a fresh session
│
├── workflow-skills                v1.0.0   5 skills
│   └── skills/
│       ├── writing-plans                   turn a spec into a step-by-step plan
│       ├── executing-plans                 batch execution with verification checkpoints
│       ├── test-driven-development         TDD plus feature planning and living notes
│       ├── using-git-worktrees             isolated workspaces for feature work
│       └── finishing-a-development-branch  verify, then merge or open an MR
│
├── productivity-skills            v1.0.0   6 skills
│   └── skills/
│       ├── brainstorming                   design before code
│       ├── design-doc                      structured technical design documents
│       ├── dispatching-parallel-agents     2+ independent tasks in parallel
│       ├── github-issue-search             find known issues and workarounds
│       ├── writing-clearly                 sentence craft for any prose: docs, commits, posts
│       └── writing-confluence-docs         house style for the team wiki: grammar, spelling, voice, formatting
│
├── git-conventions                v1.0.0   1 skill · 3 hooks
│   ├── skills/
│   │   └── git-conventions                 atomic commits, explicit staging, branch naming
│   └── hooks/
│       ├── block_broad_git_add.py          PreToolUse: blocks `git add .`, `-A`, `--all`
│       ├── validate_commit_message.py      PreToolUse: enforces `type(scope): Subject`
│       └── block_bare_rm.py                PreToolUse: blocks `rm` on git-tracked files
│
└── meta-skills                    v1.0.0   1 skill
    └── skills/
        └── writing-skills                  how to author a skill that actually triggers
```

## Installation

### 1. Add the marketplace

This repository is the marketplace, so you add it once and then install plugins from it. Run this inside Claude Code:

```
/plugin marketplace add ipinheiro/ines-claude-tools
```

The repository is private, so this needs GitHub access. The `owner/repo` shorthand clones over SSH by default, which works as long as `github.com` is already in `known_hosts` and your key is loaded in `ssh-agent`. To clone over HTTPS instead, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` and configure a credential helper, for example with `gh auth setup-git`.

The same subcommands exist outside a session as `claude plugin marketplace add ...` for scripting.

### 2. Install plugins

Browse with `/plugin` and pick from the **Discover** tab, or install by name:

```
/plugin install python-dev@ines-claude-tools
/plugin install code-review-orchestrator@ines-claude-tools
/plugin install dev-commands@ines-claude-tools
/plugin install workflow-skills@ines-claude-tools
/plugin install productivity-skills@ines-claude-tools
/plugin install git-conventions@ines-claude-tools
/plugin install meta-skills@ines-claude-tools
```

Each install asks for a scope: **user** (all your projects), **project** (committed to `.claude/settings.json` for everyone on the repo), or **local** (just you, just this repo).

### 3. Activate

Read the install summary. If it says `Run /reload-plugins to activate.`, run that. If the reload warns that it will invalidate the prompt cache, rerun as `/reload-plugins --force`. A summary reporting `Plugin is now active.` needs nothing further.

`/reload-plugins` counts skills from `commands/` directories only, so it can report `0 skills` even when a plugin's `skills/` directory loaded correctly.

### Keeping up to date

Third-party marketplaces have auto-update off by default. Either turn it on from `/plugin` → **Marketplaces** → **Enable auto-update**, or refresh manually:

```
/plugin marketplace update ines-claude-tools
```

Background auto-update disables git credential helpers for its `git pull`, so over HTTPS it can fail against a private repository and fall back to a re-clone. SSH remotes are unaffected. Set `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` to keep the existing clone when a background pull fails.

## Invoking what you installed

Plugin skills and commands are namespaced by plugin name. This is the form that always works and the one autocomplete offers:

```
/python-dev:type-safety-audit src/
/code-review-orchestrator:mr-review
/dev-commands:branch-report 30
```

The bare name also works when nothing else claims it. No skill in this marketplace currently collides with a bundled or Superpowers skill.

Skills that Claude loads on its own, rather than ones you type, trigger from the phrases in their `description` frontmatter. `python-best-practices` fires on Python work, `git-conventions` on commits, and so on. You do not need to invoke those by name.

## Command reference

| Command | What it does | Output |
|---------|--------------|--------|
| `/code-review-orchestrator:deep-review` | Multi-agent review of uncommitted, staged, or branch changes | `docs/reviews/` |
| `/code-review-orchestrator:mr-review` | Diff-scoped review producing GitLab inline comments | `docs/reviews/mr-review-{branch}-{date}.md` |
| `/code-review-orchestrator:repo-review` | Dependency-batched review of a whole repo for refactor planning | `docs/reviews/repo-review-{date}.md` |
| `/dev-commands:analyse [mode]` | Security, performance, and quality analysis for data science code | Markdown or JSON report |
| `/dev-commands:branch-report [days]` | Stale branches, merge status, cleanup commands | Markdown or JSON report |
| `/dev-commands:handoff` | Session state for a fresh agent | `HANDOFF.md` |

### `/branch-report`

```
/dev-commands:branch-report [days] [--format=json|md] [--include-remote] [--author=name] [--output=path]
```

Detects staleness against a configurable threshold (default 30 days) and reports merge status against `develop`, `main`, and `master`. For any branch that has diverged from a base branch without being merged, it dispatches a subagent to read the commits and summarise the changes into the report, so you are deciding on described work rather than a branch name.

### `/analyse`

```
/dev-commands:analyse [mode] [--plan] [--output=path] [--parallel]
```

Runs ruff, bandit, safety, semgrep, scalene, and memray through `uv run --with`, and dispatches subagents for the analysis passes that can run in parallel. Produces a report with per-finding line references and a metrics baseline.

### `/type-safety-audit`

```
/python-dev:type-safety-audit umbra_generator/
/python-dev:type-safety-audit src/pipeline/ src/models/
```

Dispatches the seven auditor agents in parallel and writes `docs/reviews/type-safety-audit-{date}.md`. It never modifies code. Findings are ranked by blast radius:

| Priority | Category |
|----------|----------|
| P0 | Cross-boundary contracts, where callers cannot type-check |
| P1 | `Any` in public signatures, where the hole propagates |
| P2 | Magic strings that already have an enum |
| P3 | Config access typing, where bad config fails at runtime |
| P4 | Internal helper `Any`, low blast radius |
| P5 | Environment coupling that complicates CI/CD |
| P6 | Brittle path construction that breaks on restructure |

Take the report into `fixing-type-errors` to implement fixes by priority, then `executing-plans` to batch them into branches.

## Skill workflow

The workflow skills are built to chain:

```
brainstorming            design before code
     ↓
writing-plans            spec becomes a step-by-step plan
     ↓
using-git-worktrees      isolated workspace
     ↓
executing-plans          implement with verification checkpoints
     ↓
deep-review / mr-review  multi-agent review of the diff
     ↓
finishing-a-development-branch
```

## Hooks

Hooks are configured in each plugin's `plugin.json` and activate on install. They run as `PreToolUse` or `UserPromptSubmit` handlers, and a `PreToolUse` hook exiting with code 2 blocks the tool call.

### python-dev

**`python-uv-guard.py`** blocks bare `python` commands and points at `uv run`, `uv python install`, and `uv add`.

**`ruff-before-add.py`** runs on `git add` and lints the Python files being staged. It auto-fixes unused imports and import ordering, and blocks on what it cannot fix. Rules: E402 imports at top, F401 unused imports, F841 unused variables, I001 import sorting, plus function-level and class-level inline imports caught by the `no-inline-imports.yml` ast-grep rule. Requires `uv tool install ruff` and `uv tool install ast-grep-cli`.

**`skill-detector.py`** scans your prompt and injects a reminder to load the matching skill: `pyproject.toml` loads `uv-pyproject`, Snowflake or shucks loads `using-shucks`, dbt commands load `dbt-python-integration`, pytest and fixtures load `python-test-quality`, test audit requests load `test-review`, type safety requests load `type-safety-audit`, Dagster work loads `writing-dagster-pipelines`, and general Python work loads `python-best-practices`.

### git-conventions

**`block_broad_git_add.py`** blocks `git add .`, `git add -A`, and `git add --all`. Stage files explicitly instead: `git add file1.py file2.py`. This stops secrets, large files, and unrelated changes riding along in a commit.

**`validate_commit_message.py`** enforces `type(scope): Subject`, where type is one of `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf` and scope is required.

**`block_bare_rm.py`** blocks `rm` on git-tracked files and suggests the intended alternative: `git restore <file>` to discard changes, or `git rm <file>` to remove from the repository if you passed `-f`. Untracked files, globs, directories, and paths outside a git repo are all allowed through.

## Changing a plugin

### 1. Edit and test locally

```bash
claude --plugin-dir ./plugins/python-dev
```

A `--plugin-dir` plugin takes precedence over an installed plugin of the same name for that session, so you can iterate on something you already have installed without uninstalling it. Run `/reload-plugins` to pick up edits without restarting.

### 2. Run the checks

```bash
uv run pytest                                 # hook script tests
claude plugin validate .                      # the marketplace catalog
claude plugin validate ./plugins/python-dev   # one plugin, plus its frontmatter
claude plugin validate . --strict             # warnings become errors
```

`pytest` covers the hook scripts in `plugins/*/hooks/`. They run on every matching tool call and one of them rewrites files, so changes there need a test.

The marketplace validator checks schema errors, duplicate plugin names, path traversal in sources, and version drift between a marketplace entry and the plugin's own `plugin.json`.

### 3. Bump the version

Two places, and they must match:

```
plugins/<name>/.claude-plugin/plugin.json     "version"
.claude-plugin/marketplace.json               the matching entry's "version"
```

At install time `plugin.json` wins and the entry version is ignored, so a stale entry is silently wrong and `claude plugin validate .` will warn about it. Use a major bump when you remove or rename a component, since anyone invoking the old name breaks.

Update the counts and the tool hierarchy in this README in the same change, so the two never drift.

### 4. Ship it

Push to the default branch. Because this marketplace is a git source, that is the whole release step. Users pick the change up as described in [Keeping up to date](#keeping-up-to-date) - auto-update is off by default for third-party marketplaces, so most people need `/plugin marketplace update ines-claude-tools`.

## Authoring notes

Custom commands and skills are the same mechanism now. A file at `commands/deploy.md` and a directory at `skills/deploy/SKILL.md` both produce `/plugin-name:deploy`. Skills are preferred for anything new, because a skill is a directory and can carry references, scripts, and templates alongside `SKILL.md`.

Component directories live at the plugin root, never inside `.claude-plugin/`. Only `plugin.json` goes in there.

Frontmatter fields that matter, all optional:

```yaml
---
description: What this does and when to use it. Claude reads this to decide when to load the skill.
argument-hint: "[scope] [--format=md]"
allowed-tools: Read, Grep, Bash(git:*)
disable-model-invocation: true   # only you can invoke it, never Claude
user-invocable: false            # background knowledge, hidden from the / menu
model: opus
---
```

Quote a `description` that contains a colon followed by a space. An unquoted `"type: ignore"` inside a description is parsed as a nested YAML mapping and the whole frontmatter block fails.

Skill files carry no version. Bump the version in `plugin.json` and the matching marketplace entry so update detection works.

Use `$ARGUMENTS` for everything passed after the command, or `$0`, `$1`, and so on for positional arguments. `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin's installed location and `${CLAUDE_SKILL_DIR}` to the individual skill's directory. Plugins are copied to a cache on install, so paths pointing outside the plugin directory will not resolve.

Discipline skills follow a consistent shape: the rule, red flags that signal you are about to deviate, the process, a rationalisation table countering common excuses, and integration notes pointing at related skills. `meta-skills:writing-skills` covers this in full.

## Resources

- [Claude Code documentation](https://code.claude.com/docs/en/overview)
- [Create plugins](https://code.claude.com/docs/en/plugins)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference)
- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Skills](https://code.claude.com/docs/en/skills)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Settings](https://code.claude.com/docs/en/settings)
