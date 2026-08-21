---
name: type-safety-audit
description: Orchestrate a parallel multi-agent audit of a Python package for type safety issues. Dispatches 7 specialized agents and produces a dated report. Triggers on "type safety audit", "type audit", "audit types", "audit type safety", "/type-safety-audit".
---

# Type Safety Audit

Orchestrate a comprehensive type safety audit of a Python package using 7 specialized parallel agents. Produces a dated report — never modifies code.

## Invocation

- `/type-safety-audit <scope>` — e.g. `/type-safety-audit umbra_generator/` or `/type-safety-audit src/pipeline/ src/models/`
- `<args>` contains the directories or files to audit

If no scope is provided, ask the user which directories to audit.

## The Rule

**Audit only, never fix.** This skill produces a report. Code changes are a separate step using `fixing-type-errors` or `executing-plans`.

## Workflow

### Step 1: Inventory the Scope

Read the target directories and build context:

1. **Find all Python files** in the scope:
   ```bash
   fd -e py <scope>
   ```

2. **Inventory existing type infrastructure** — find enums, TypedDicts, Pydantic models, and Literal types already in the codebase so agents don't suggest types that already exist:
   ```bash
   rg "class \w+\(.*StrEnum|IntEnum|Enum\)" <scope> --line-number
   rg "class \w+\(.*TypedDict\)" <scope> --line-number
   rg "class \w+\(.*BaseModel|BaseSettings\)" <scope> --line-number
   rg "Literal\[" <scope> --line-number
   rg "class \w+\(.*NamedTuple\)" <scope> --line-number
   ```

3. **Build the file list and type inventory** to pass to each agent.

Record these counts for the report header:
- Number of Python files
- Number of existing enums, TypedDicts, Pydantic models

### Step 2: Dispatch 7 Audit Agents in Parallel

**IMPORTANT: Dispatch ALL 7 agents in a single response using 7 parallel Agent tool calls.** Do NOT wait for one agent to finish before starting the next.

Each agent receives the same context:
- The scope (directories to audit)
- The file list
- The existing type infrastructure inventory

**Agents to dispatch (all at once):**

1. **any-usage-auditor** — Find all `Any` type annotations. Every instance gets a concrete replacement suggestion (`Any` is never legitimate in modern Python). Report file:line, context, suggested type, and complexity.

2. **unstructured-returns-auditor** — Find functions returning bare dicts, untyped dicts, or `dict[str, Any]`. Identify actual dict shapes and whether they cross module boundaries. Suggest TypedDict or Pydantic model names and fields.

3. **magic-strings-auditor** — Find string literals used as type discriminators, template names, status values, alignment values, pipeline types, etc. Cross-reference against existing enums. Suggest new enums or Literal types.

4. **config-access-auditor** — Find the config loader and all config access points. Note key, expected type, and whether typed or untyped. Check config validation at load time. Find config inconsistencies and orphaned keys.

5. **hardcoded-values-auditor** — Find numeric constants, file paths, model IDs, bucket names hardcoded as literals. Flag values appearing in multiple files as high priority.

6. **brittle-paths-auditor** — Find fragile path constructions: chained `.parent` traversals, `__file__`-relative data access, hardcoded path separators. Suggest `importlib.resources` for package data and config/constants for external paths.

7. **environment-coupling-auditor** — Find code coupled to specific environments: scattered `os.getenv` calls that bypass centralized config, hardcoded environment names in business logic, constructors that default to dev/prod, duplicate credential loading, and environment-dependent value construction.

**Agent prompt template:**

For each agent, use:

```
You are running as part of a type safety audit. Audit ONLY, never modify code.

**Scope:** {directories}
**Python files in scope ({count}):**
{file_list}

**Existing type infrastructure (do NOT suggest types that already exist):**
{type_inventory}

Follow your agent instructions to audit the scope. Return your findings in the output format specified in your agent definition.
```

Use `subagent_type` matching the agent name (e.g., `"python-dev:any-usage-auditor"`), with `model="opus"`.

### Step 3: Consolidate Findings

After all 7 agents return:

1. **Deduplicate** — A `dict[str, Any]` return might also appear in the "Any usage" findings. Link these rather than listing twice.

2. **Cross-reference** — Look for findings that are the same underlying issue:
   - A magic string AND an `Any` annotation → same fix (create an enum, use it in the type)
   - A hardcoded value AND a config access issue → same fix (add to config)
   - An unstructured return AND an `Any` parameter in the caller → same fix (create TypedDict)
   - A brittle path AND a hardcoded value → same fix (move to config or use importlib.resources)
   - An environment coupling bypass AND a config access issue → same fix (add field to config model)
   - A hardcoded env-specific default AND a magic string → same fix (remove default, inject via config)

3. **Prioritize by blast radius:**

   | Priority | Category | Criteria |
   |----------|----------|----------|
   | P0 | Cross-boundary contracts | Functions returning `dict[str, Any]` or `Any` consumed by other modules |
   | P1 | Public signature `Any` | `Any` in public function parameters or returns |
   | P2 | Magic strings with existing enum | Easy win — the enum already exists, just use it |
   | P3 | Config access typing | Untyped config access that could cause runtime errors |
   | P4 | Internal helper `Any` | Low blast radius, internal scope |

4. **Count findings** for the executive summary.

### Step 4: Write the Report

Derive the repo name and create the output directory:

```bash
REPO_NAME=$(basename "$(pwd)")
mkdir -p ~/docs/reviews/${REPO_NAME}
```

Create the report file at `~/docs/reviews/<repo-name>/type-safety-audit-{YYYY-MM-DD}.md` using today's date.

**YAML frontmatter:** The report must start with frontmatter before the first heading:

```yaml
---
project: <repo-name>
date: YYYY-MM-DD
tags: [<tag1>, <tag2>, <tag3>]
---
```

Choose 3 short, lowercase tags that capture the audit's scope (e.g. `[types, audit, pipeline]`). Tags help with search - pick terms someone would use to find this document later.

**Report template:**

```markdown
# Type Safety Audit: {package}

**Date:** {YYYY-MM-DD}
**Scope:** {directories audited}
**Files audited:** N Python files

## Executive Summary

- **Any usage:** N replaceable / M total
- **Unstructured returns:** N functions
- **Magic strings:** N literal sets -> N suggested enums
- **Untyped config access:** N access points
- **Hardcoded values:** N values should be constants/config
- **Brittle paths:** N fragile path constructions
- **Environment coupling:** N config bypasses, M env-defaulting constructors

## Priority Matrix

| Priority | Category | Count | Impact |
|----------|----------|-------|--------|
| P0 | Cross-boundary dict returns | N | Callers can't type-check |
| P1 | Any in public function signatures | N | Type safety hole propagates |
| P2 | Magic strings with existing enum candidates | N | Easy win, enum exists |
| P3 | Config access typing | N | Runtime errors on bad config |
| P4 | Internal helper Any usage | N | Low blast radius |
| P5 | Environment coupling | N | Config bypasses make CI/CD harder |
| P6 | Brittle path constructions | N | Breaks on restructure or wheel install |

## Findings

### 1. Any Usage

Every `Any` is replaceable. Modern Python always has a better type (`object`, `TypedDict`, `Protocol`, `ParamSpec`, `Unpack`, etc.).

| File | Line | Current | Suggested Type | Complexity | Impact |
|------|------|---------|----------------|------------|--------|
| ... | ... | ... | ... | ... | ... |

### 2. Unstructured Returns

| Function | File | Line | Current Return | Actual Shape | Cross-Boundary | Suggested Type |
|----------|------|------|----------------|--------------|----------------|----------------|
| ... | ... | ... | ... | ... | ... | ... |

### 3. Magic String Literals

For each group:

#### {Group Name} (e.g., "Pipeline Type")
**Values:** `"value1"`, `"value2"`, ...
**Occurrences:** N across M files
**Existing enum:** {name} in {file} / None

| File | Line | Usage | Value |
|------|------|-------|-------|
| ... | ... | ... | ... |

**Recommendation:** {Create new enum / Extend existing enum / Use Literal type}

### 4. Config Access

#### Untyped access points

| File | Line | Access Pattern | Key | Expected Type | Risk |
|------|------|---------------|-----|---------------|------|
| ... | ... | ... | ... | ... | ... |

#### Hardcoded values that should be in config

| File | Line | Value | Category | Appears In |
|------|------|-------|----------|------------|
| ... | ... | ... | ... | ... |

#### Orphaned config keys

| Config Source | Key | Defined At | Status |
|--------------|-----|-----------|--------|
| ... | ... | ... | ... |

### 5. Hardcoded Values

#### Multi-file duplicates (high priority)

| Value | Type | Files | Suggested Name |
|-------|------|-------|----------------|
| ... | ... | ... | ... |

#### Single-file magic numbers

| File | Line | Value | Context | Suggested Name |
|------|------|-------|---------|----------------|
| ... | ... | ... | ... | ... |

### 7. Environment Coupling

#### Config Bypasses (os.getenv outside config system)

| File | Line | Variable | Used For | Should Be |
|------|------|----------|----------|-----------|
| ... | ... | ... | ... | Config model field |

#### Environment-Defaulting Constructors

| File | Line | Class | Default | Risk |
|------|------|-------|---------|------|
| ... | ... | ... | `Environment.DEV` | Silent dev behavior in prod |

#### Hardcoded Environment-Specific Values

| File | Line | Value | Fix |
|------|------|-------|-----|
| ... | ... | `"DSA_DEV"` | Remove default, inject via config |

#### Duplicate Credential Loading

| Variable | Files | Count |
|----------|-------|-------|
| ... | ... | ... |

### 8. Brittle Paths

#### High risk (3+ parent traversals)

| File | Line | Pattern | Depth | Accesses | Suggested Fix |
|------|------|---------|-------|----------|---------------|
| ... | ... | ... | ... | ... | ... |

#### Medium risk (2 parent traversals)

| File | Line | Pattern | Accesses | Suggested Fix |
|------|------|---------|----------|---------------|
| ... | ... | ... | ... | ... |

#### importlib.resources candidates

| File | Line | Data Accessed | Package Location |
|------|------|--------------|-----------------|
| ... | ... | ... | ... |

## Cross-Referenced Findings

Findings from different categories that represent the same underlying fix:

| Finding A | Finding B | Unified Fix |
|-----------|-----------|-------------|
| Any usage: `data: Any` (file.py:42) | Unstructured return: `get_data() -> dict` (api.py:10) | Create `DataPayload(TypedDict)`, use as return type AND parameter type |

## Suggested Fix Branches

### fix/type-safety-returns (P0)
- Replace N cross-boundary `dict[str, Any]` returns with TypedDicts
- Files affected: ...

### fix/type-safety-any (P1)
- Replace N `Any` annotations in public signatures
- Files affected: ...

### fix/type-safety-enums (P2)
- Use existing enums for N magic string groups
- Create N new enums
- Files affected: ...

### fix/type-safety-config (P3)
- Type N config access points
- Move N hardcoded values to config
- Remove N orphaned config keys

### fix/type-safety-constants (P4)
- Extract N hardcoded values to named constants
- Files affected: ...

### fix/type-safety-env-coupling (P5)
- Centralize N scattered os.getenv calls into config model
- Remove N environment-defaulting constructors
- Fix N hardcoded env-specific defaults
- Files affected: ...

### fix/type-safety-paths (P6)
- Migrate N brittle path constructions to importlib.resources or config
- Files affected: ...
```

### Step 5: Present Summary

After writing the report, present a concise summary to the user:
- Total findings per category
- Top 5 highest-impact findings
- Link to the full report file
- Suggested next steps (use `fixing-type-errors` skill, use `executing-plans` skill to batch the fix branches)
