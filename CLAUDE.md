# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Repository purpose

This repository is a Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces). It packages Inês's personal skills, subagents, and hooks. It is not a conventional software project: there is no application to build or test, and the deliverable is the plugin content itself.

## Architecture

```
.claude-plugin/marketplace.json   catalog, one entry per plugin
plugins/<name>/
  .claude-plugin/plugin.json      manifest: name, version, description, author, hooks
  skills/<skill-name>/SKILL.md    model-invoked and user-invoked skills
  commands/<name>.md              legacy flat-file form of a skill
  agents/<name>.md                subagent definitions
  hooks/                          hook scripts, referenced from plugin.json
  .mcp.json                       MCP server definitions
```

Component directories live at the **plugin root**, never inside `.claude-plugin/`. Only `plugin.json` goes in there.

## Consulting the docs

Always check the live documentation at **https://code.claude.com/docs/en/** before writing or changing a component. Do not answer from memory: the plugin and skill schemas change often, and this repository has already carried stale guidance once.

The pages that matter here:

| Topic | URL |
|-------|-----|
| Skills, frontmatter, substitutions | https://code.claude.com/docs/en/skills |
| Creating plugins | https://code.claude.com/docs/en/plugins |
| Plugin schemas and file locations | https://code.claude.com/docs/en/plugins-reference |
| Marketplace schema | https://code.claude.com/docs/en/plugin-marketplaces |
| Subagents | https://code.claude.com/docs/en/sub-agents |
| Hooks and events | https://code.claude.com/docs/en/hooks |
| Settings and permissions | https://code.claude.com/docs/en/settings |

Documentation is deliberately not vendored into this repo. A local snapshot goes stale and then silently overrides the live docs.

## Skills and commands are the same mechanism

Custom commands have been merged into skills. A file at `commands/deploy.md` and a directory at `skills/deploy/SKILL.md` both produce `/plugin-name:deploy`.

**Write new work as a skill**, not a command. A skill is a directory, so it can carry `references/`, `scripts/`, and templates alongside `SKILL.md`. The `commands/` directories that remain here are legacy and fine to leave in place.

Plugin skills are namespaced `/plugin-name:skill-name`. The bare name also resolves unless something else already claims it, so check for collisions with [bundled skills](https://code.claude.com/docs/en/commands) before picking a name.

### Frontmatter

Verify fields against the [skills docs](https://code.claude.com/docs/en/skills) rather than copying from an existing file. All fields are optional; `description` is what makes a skill trigger.

```yaml
---
description: What this does and when to use it, including trigger phrases.
argument-hint: "[scope] [--format=md]"
allowed-tools: Read, Grep, Bash(git:*)
disable-model-invocation: true   # only a human can invoke it
user-invocable: false            # background knowledge, hidden from the / menu
---
```

Two traps that have already bitten this repo:

- **Skills carry no `version` field.** Version the plugin in `plugin.json`, not the skill.
- **Quote any `description` containing a colon followed by a space.** An unquoted `"type: ignore"` parses as a nested mapping and the whole frontmatter block is dropped.

Field names use hyphens (`user-invocable`, `allowed-tools`), not underscores. Unrecognized fields are ignored silently at runtime, so a typo fails quietly.

### Check for an existing skill first

Before writing a skill, check whether [Superpowers](https://code.claude.com/docs/en/discover-plugins) or a [bundled skill](https://code.claude.com/docs/en/commands) already covers it. Several skills here layer on Superpowers rather than competing with it.

**Defer to the built-in for the general discipline. Add only what is team-specific.** Both plugins load together, so a restated process is wasted context, and a contradicting one makes Claude choose arbitrarily between two sets of instructions.

A layer is justified by a different artefact shape (phased plan directories), stack knowledge the built-in cannot have (Snowflake, dbt, uv, shucks), or a step the built-in skips. It is not justified by wanting the guidance in our own words.

When you write a layer, name the skill you defer to in the first paragraph and state what you add. See `workflow-skills:writing-plans` and `code-review-orchestrator:verifying-python-review-feedback`.

### Skill structure

Discipline skills follow a consistent shape: the rule, red flags signalling you are about to deviate, the process, a rationalization table countering common excuses, and integration notes. Use authority language (MUST, NEVER, ALWAYS) and test under pressure before deploying. `meta-skills:writing-skills` covers this in full.

## Subagents

Defined in `agents/<name>.md`. Required frontmatter is `name` and `description`; everything else is optional. Fields used here: `model`, `tools`, `skills` (preloads full skill content), `memory`, `maxTurns`.

Agent `name` cannot contain `:` - that is reserved for plugin scoping. Claude Code refuses to load such a file and only logs it to the debug log.

Dispatch agents with the `Agent` tool, issuing every call in a **single message** so they run concurrently. Add `isolation: "worktree"` when parallel agents would edit overlapping files.

## Hooks

Configure hooks either inline in `plugin.json` under a `hooks` key, or in `hooks/hooks.json`. Both sources load and merge, and identical commands are deduplicated - but pick one location per plugin rather than splitting across both.

Reference scripts with `${CLAUDE_PLUGIN_ROOT}`. Plugins are copied to a cache on install, so any path outside the plugin directory will not resolve.

A `PreToolUse` hook exiting with code 2 blocks the tool call. The full event list is in the [hooks docs](https://code.claude.com/docs/en/hooks) and is much longer than `PreToolUse`/`PostToolUse`/`SessionStart`.

Hooks receive the event JSON on stdin. Consume it (`cat`, `jq`, or reading `sys.stdin`) even on the paths where you do not need it.

## Validating changes

Run both before every commit:

```bash
uv run pytest                                 # hook script tests
claude plugin validate .                      # marketplace catalog
claude plugin validate ./plugins/<name>       # one plugin, plus its skill/command/agent frontmatter
claude plugin validate . --strict             # warnings become errors
```

Hook scripts get tests. They run on every matching tool call, they can block any Bash command, and `ruff-before-add.py` rewrites files in place - a bug there is not contained to one session. `tests/conftest.py` loads them by path, since hyphenated filenames at a plugin root cannot be imported normally.

Two rules for hooks:

- Never pass a path to a formatter or linter without excluding vendored directories. An explicitly named path overrides the tool's own exclusions, so `.venv` contents get rewritten.
- Match shell commands by tokenising, never with a substring or regex search over the raw string. A mention inside a commit message or heredoc will otherwise trigger the guard.

The marketplace validator catches version drift between an entry and the plugin's own `plugin.json`. At install time `plugin.json` wins and the entry version is ignored, so **bump both together** or updates silently never reach users.

Test without installing:

```bash
claude --plugin-dir ./plugins/<name>
```

A `--plugin-dir` plugin overrides an installed plugin of the same name for that session. Run `/reload-plugins` to pick up edits without restarting.

## Conventions

Marketplace entries carry no `skills` or `commands` arrays. Auto-discovery from `skills/` and `commands/` finds everything, and explicit lists only drift.

When you add, remove, or rename a component, update in the same change:
1. The plugin's `version` in `plugin.json`
2. The matching `version` in `.claude-plugin/marketplace.json`
3. The tool hierarchy and counts in `README.md`
