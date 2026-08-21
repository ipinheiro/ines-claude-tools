---
name: fixing-type-errors
description: 'This skill should be used when the user says "fix pyright errors", "fix ty errors", "fix type errors", "fix typing", "type check fails", "fix pylance errors", or when pyright/ty/pylance/mypy reports type errors. Also use when tempted to add "type: ignore", use cast(), or reach for Any.'
---

# Fixing Type Errors

Fix type errors at their source by tracing the issue through the type system, not by adding inline suppressions or casts.

## Invocation

- `/fixing-type-errors <path>` — systematically eliminate all pyright errors in a package (e.g., `/fixing-type-errors src/my_package/`)
- Auto-triggered when type errors appear during development

If invoked with `<args>`, run the **Systematic Workflow**. Otherwise, apply the **Core Principles** during your current task.

## The Rule

**Never suppress, always fix.** Trace to source. No exceptions.

Announce: "I'm using the fixing-type-errors skill to fix this properly."

## Red Flags

These thoughts mean STOP - you're about to suppress instead of fix:

| Thought | Reality |
|---------|---------|
| "I'll just add type: ignore" | You're hiding a bug, not fixing it. Trace to source. |
| "cast() will fix this" | cast() lies to the type checker. Fix the actual type. |
| "This is a pyright bug" | 99% of the time it's your code. Trace to source first. |
| "Any will work here" | Any is a hole in your type safety. Fix the actual type. |
| "I'll fix this later" | No you won't. Fix it now or it compounds. |
| "The types are too complex" | Complex types catch complex bugs. Figure it out. |
| "I'll just fix them all at once" | Batch fixes mask regressions. Fix in small clusters, validate each. |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "It works at runtime" | Runtime errors are worse than type errors. Fix the types. |
| "Pyright is wrong" | Pyright is almost never wrong. You're missing something. |
| "This is just for speed" | Type suppression is technical debt with interest. |
| "The library has bad types" | Document WHY with a comment if truly necessary. |
| "I know the type is right" | If you knew, pyright would know. Something's wrong. |

## Core Principle

Type errors are symptoms. The disease is either:
1. Wrong type annotation somewhere upstream
2. Missing type annotation causing inference to fail
3. Actual logic bug where types don't align
4. Missing `None` handling

Many errors **cascade** from a single source — fixing one annotation can resolve 5-10 downstream errors. Always look for the root, not the leaves.

## Forbidden Moves

**Never use these to "fix" type errors:**

```python
# FORBIDDEN - Suppression
x: str = get_value()  # type: ignore

# FORBIDDEN - Blind casting
x = cast(str, get_value())

# FORBIDDEN - Lying about types
x: str = get_value()  # type: ignore[assignment]

# FORBIDDEN - Any escape hatch
from typing import Any
x: Any = get_value()

# FORBIDDEN - Inline suppression without justification
result = lib_call()  # pyright: ignore
```

**Only acceptable suppression:** genuinely wrong third-party stubs, documented with `# pyright: ignore[errorCode] — reason` comment.

## Root Cause Patterns

When you see pyright errors, match them against these root causes. Fix the root cause, not the symptom.

### Pattern 1: Bare Generic

```python
# Error: reportMissingTypeArgument
items: list = []           # bare list
mapping: dict = {}         # bare dict
callback: Callable = fn    # bare Callable

# Fix: Add type parameters
items: list[str] = []
mapping: dict[str, int] = {}
callback: Callable[[str], bool] = fn
```

### Pattern 2: Bare default_factory

```python
# Error: reportUnknownVariableType on field default
class Config(BaseModel):
    tags: list = Field(default_factory=list)

# Fix: Typed lambda
class Config(BaseModel):
    tags: list[str] = Field(default_factory=lambda: list[str]())
    # Or simply:
    tags: list[str] = Field(default_factory=list)  # with explicit annotation
```

### Pattern 3: Untyped Local Variable

```python
# Error: reportUnknownVariableType
results = []
for item in items:
    results.append(process(item))

# Fix: Annotate the variable
results: list[ProcessedItem] = []
for item in items:
    results.append(process(item))
```

### Pattern 4: Library Invariance

```python
# Error: list[str] not assignable to List[TEncodable]
tags: list[str] = ["a", "b"]
send_to_api(tags=tags)  # API expects Sequence or its own type

# Fix: Annotate variable with library's expected type
from library import TEncodable
tags: list[TEncodable] = ["a", "b"]
send_to_api(tags=tags)

# Or use Sequence for covariance:
tags: Sequence[str] = ["a", "b"]
```

### Pattern 5: model_dump() Dict Propagation

```python
# Error: dict[str, Any] flowing through multiple signatures
def process(data: MyModel) -> dict:
    return data.model_dump()  # Returns dict[str, Any]

def send(payload: dict) -> None:  # Bare dict spreads Any
    api.post(payload)

# Fix Option A: Define a TypedDict alias in a central types module
# types.py
class MyModelDict(TypedDict):
    name: str
    value: int

# Fix Option B: Keep the model, don't dump until the boundary
def process(data: MyModel) -> MyModel:
    return data  # Pass typed models in public signatures

def send(payload: MyModel) -> None:
    api.post(payload.model_dump())  # Dump only at the I/O boundary
```

### Pattern 6: boto3 / SDK Kwargs Unpacking

```python
# Error: dict[str, str] not assignable to specific keyword parameters
params: dict[str, str] = {"Bucket": bucket, "Key": key}
s3.get_object(**params)  # pyright can't verify dict keys match params

# Fix: Use explicit keyword arguments
s3.get_object(Bucket=bucket, Key=key)

# Or use a TypedDict matching the SDK's expected shape
class GetObjectParams(TypedDict):
    Bucket: str
    Key: str

params: GetObjectParams = {"Bucket": bucket, "Key": key}
s3.get_object(**params)
```

### Pattern 7: TypedDict Optional Access

```python
# Error: "Key" is not required in TypedDict
response = s3.head_object(Bucket=b, Key=k)
size = response["ContentLength"]  # ContentLength may not be present in stubs

# Fix: Use .get() with a walrus operator or default
if (size := response.get("ContentLength")) is not None:
    process(size)
```

### Pattern 8: str vs Literal

```python
# Error: str not assignable to Literal["json", "csv"]
config = load_config()
format_type: str = config["format"]
export(format=format_type)  # export expects Literal["json", "csv"]

# Fix: Use model_validate or explicit Literal annotation
from typing import Literal

FormatType = Literal["json", "csv"]
format_type: FormatType = config["format"]  # If source is trusted

# Or with Pydantic validation:
class ExportConfig(BaseModel):
    format: Literal["json", "csv"]

validated = ExportConfig.model_validate(config)
export(format=validated.format)
```

### Pattern 9: Missing None Handling

```python
# Error: "str | None" not assignable to "str"
def process(user_id: str | None):
    save_user(user_id)  # save_user expects str

# Fix: Add None check (guard clause)
def process(user_id: str | None):
    if user_id is None:
        raise ValueError("user_id required")
    save_user(user_id)  # Now pyright knows it's str
```

### Pattern 10: Wrong Return Type

```python
# Error: Return type "str | None" doesn't match "str"
def get_name() -> str:
    return config.get("name")  # .get() returns str | None

# Fix: Either correct the annotation or the implementation
def get_name() -> str | None:
    return config.get("name")

# Or if None is truly impossible:
def get_name() -> str:
    name = config.get("name")
    if name is None:
        raise ValueError("name not configured")
    return name
```

### Pattern 11: Containing Any at Boundaries

When `Any` is unavoidable (e.g., Snowflake row values, third-party SDK returns), **contain it** — don't let it leak through your codebase.

```python
# BAD: Any leaks everywhere
def get_rows() -> list[dict[str, Any]]:  # Any escapes into every caller
    return cursor.fetchall()

# GOOD: Define named type aliases in a central types module
# types.py
from typing import Any

# Boundary types — Any is contained here, documented, and named
SnowflakeRow = dict[str, Any]  # Raw row from Snowflake cursor
RawJsonPayload = dict[str, Any]  # Unparsed JSON from external API

# services.py
from .types import SnowflakeRow

def get_rows() -> list[SnowflakeRow]:  # Named, traceable
    return cursor.fetchall()

def process_rows(rows: list[SnowflakeRow]) -> list[User]:
    return [User.model_validate(row) for row in rows]  # Any stops here
```

Individual files should never `from typing import Any` directly. If you need `Any`, the type alias should already exist in your types module.

## Systematic Workflow (User-Invoked)

When invoked with a path (`/fixing-type-errors <path>`), follow this systematic workflow to eliminate all pyright errors.

### Phase 1: Triage

Detect which type checker the project uses and run it:

```bash
# Check pyproject.toml for [tool.pyright] or [tool.ty] sections, or check dev dependencies
# Then run the appropriate checker:
uv run pyright <path>/
# or
uv run ty check <path>/
```

Throughout this workflow, `pyright` and `ty` are interchangeable — use whichever the project has configured. If both are present, prefer `ty`.

Categorize the output:

1. **By error code** — group errors by `reportMissingTypeArgument`, `reportUnknownVariableType`, etc. This reveals which root cause patterns dominate.
2. **By file** — identify which files have the most errors.
3. **By root cause cluster** — many errors cascade from a single source. Look for:
   - A single untyped function whose return value is used in 10 places
   - A bare `dict` in a types module that propagates `Any` downstream
   - A missing generic parameter on a base class

Present the triage breakdown to the user before fixing:

```
## Pyright Triage: <path>

**Total errors:** N

### By error code
| Error Code | Count | Root Cause Pattern |
|------------|-------|--------------------|
| reportMissingTypeArgument | 23 | Pattern 1: Bare Generic |
| reportUnknownVariableType | 15 | Pattern 3: Untyped Local |
| ... | ... | ... |

### By file (top 10)
| File | Errors | Likely Root Cause |
|------|--------|-------------------|
| models/types.py | 12 | Bare generics in base types |
| ... | ... | ... |

### Source vs Test
| Category | Files | Errors |
|----------|-------|--------|
| Source | N | M |
| Tests | N | M |

### Cascade candidates
- `models/types.py:MetadataDict` — bare dict used in 8 files (fixing = ~15 errors)
- ...
```

### Phase 2: Plan Fix Order

Fix errors in **dependency order** — upstream fixes eliminate downstream errors automatically:

1. **Shared types modules** (e.g., `models/types.py`, `schemas.py`) — bare generics, type aliases, boundary types
2. **Core/utility modules** — functions used by many other modules
3. **Service layer** — business logic
4. **Routes / CLI / entrypoints** — leaf modules
5. **Tests** — fix last; many test errors are mechanical fixture annotations that resolve when source types improve

**Source errors before test errors.** Always.

To determine dependency order, check imports:

```bash
# Which files import from the high-error files?
rg "from.*models.types import" <path>/ --files-with-matches
```

### Phase 3: Fix by Cluster

For each cluster (group of related errors from the same root cause):

1. **Identify the root cause** — match against the Root Cause Patterns above
2. **Fix at the source** — the upstream annotation, not each downstream error
3. **Validate the cluster** — run pyright on affected files only:
   ```bash
   uv run pyright <file1> <file2> <file3>
   ```
4. **Run tests** to catch behavioral regressions:
   ```bash
   uv run pytest <relevant_test_files> -x
   ```
5. **Move to the next cluster**

Fix in small batches. Never fix everything at once — regressions become impossible to trace.

### Phase 4: Parallelize Independent Clusters

Errors in **unrelated files** (no import relationship) can be fixed by parallel subagents. After triage:

1. Group files by dependency cluster (files that import from each other are in the same cluster)
2. Dispatch one agent per independent cluster
3. Each agent fixes its cluster and validates with pyright + pytest

Use the Agent tool with clear scoping:

```
Fix pyright errors in <cluster_files>.

Root cause: <identified pattern>
Expected fix: <specific approach>

After fixing, validate:
1. uv run pyright <cluster_files>
2. uv run pytest <relevant_tests> -x

Do NOT use cast(), type: ignore, or Any as escape hatches.
```

### Phase 5: Final Validation

After all clusters are fixed:

```bash
# Full pyright check
uv run pyright <path>/

# Full test suite
uv run pytest
```

Report results to the user:
- Errors before vs after
- Any remaining errors and why (genuinely wrong stubs, etc.)
- Any behavioral changes detected by tests

## Individual Error Fixing (Auto-Triggered)

When type errors appear during development (not a systematic cleanup), follow this process:

### Step 1: Run the Type Checker

```bash
uv run pyright
# or
uv run ty check

# For a specific file:
uv run pyright src/my_package/models.py
uv run ty check src/my_package/models.py
```

### Step 2: Understand the Error

Read the error carefully. Type checker errors have this structure (pyright shown, ty is similar):

```
src/file.py:42:15 - error: Argument of type "str | None" cannot be
  assigned to parameter "name" of type "str"
    "str | None" is not assignable to "str" (reportArgumentType)
```

Key parts:
- **Location**: `src/file.py:42:15` (file, line, column)
- **Issue**: What pyright expected vs what it got
- **Error code**: `reportArgumentType` (helps identify category)

### Step 3: Trace to Source

**Don't fix at the error location.** Trace upstream:

1. What function/variable is involved?
2. Where does its type come from?
3. Why does pyright think it has the wrong type?

**Example trace:**

```
Error: Argument "user_id" has type "str | None", expected "str"
  at: process_user(user_id)

Trace:
  -> user_id comes from get_user_id() return value
  -> get_user_id() returns str | None (line 15)
  -> But process_user() expects str (line 42)

Root cause: Missing None check before calling process_user()
```

### Step 4: Fix at Source

Match against the **Root Cause Patterns** above and apply the appropriate fix.

### Step 5: Check Propagation

After fixing, run the type checker again. Fixing one error might:
- Resolve multiple downstream errors (good!)
- Reveal new errors that were masked (fix these too)

```bash
uv run pyright  # or: uv run ty check
```

Repeat until clean.

### Step 6: Verify Logic

Type fixes can change behavior. Quick sanity check:
- Did the fix change what the code does?
- Are the tests still passing?

```bash
uv run pytest
```

## Error Categories

### reportArgumentType
**Cause:** Function called with wrong argument type
**Fix:** Either fix the caller's value or the function's parameter type

### reportReturnType
**Cause:** Function returns wrong type for its annotation
**Fix:** Either fix the return statement or the return type annotation

### reportAssignmentType
**Cause:** Variable assigned incompatible type
**Fix:** Either fix the assignment or the variable's type annotation

### reportOptionalMemberAccess
**Cause:** Accessing attribute on potentially None value
**Fix:** Add None check before access

### reportGeneralTypeIssues
**Cause:** Various type mismatches
**Fix:** Trace to source, understand the mismatch

### reportMissingTypeArgument
**Cause:** Generic type used without type parameters
**Fix:** Add type parameters (e.g., `list` -> `list[str]`)

### reportUnknownParameterType
**Cause:** Parameter has no type annotation, pyright infers `Unknown`
**Fix:** Add explicit type annotation to parameter

### reportUnknownVariableType
**Cause:** Variable type cannot be inferred
**Fix:** Add explicit type annotation to variable

## When Suppression IS Acceptable

Only in these rare cases:

```python
# Acceptable: Third-party library has wrong stubs
# pyright: ignore[reportArgumentType] — boto3 stubs incorrect for this overload
client.put_object(Body=data)

# Acceptable: Known pyright limitation
# pyright: ignore[reportReturnType] — pyright#1234
return complex_generic_thing
```

**Always document why** with a comment. Every suppression must have `— reason` after the error code.

## Quick Checklist

Before "fixing" a type error, ask:

1. [ ] Did I trace to the source, not just the symptom?
2. [ ] Am I fixing the type, not suppressing it?
3. [ ] Does the fix make logical sense, not just silence pyright?
4. [ ] Did I check for propagation effects?
5. [ ] Are tests still passing?
6. [ ] Am I fixing in dependency order (upstream first)?

## Integration with Other Skills

### After `type-safety-audit`

If a type-safety-audit report exists in `~/docs/reviews/<repo-name>/`, read the latest one before starting fixes. The report contains:
- Prioritized findings (P0-P5) with file:line references
- Suggested concrete replacement types for each `Any`
- Suggested TypedDict/Pydantic model definitions for unstructured returns
- Suggested enum names for magic strings
- Cross-referenced findings where one fix resolves multiple issues

Use the report's priority matrix to decide fix order and its suggested types as starting points. The report is audit-only — this skill does the actual fixing.

### During `executing-plans`

If type errors appear while implementing:
1. Stop the current task
2. Use this skill to fix properly
3. Continue with the plan

### Before `finishing-a-development-branch`

Always run `uv run pyright` (or `uv run ty check`) before finishing. Type errors should be fixed, not suppressed, before merge/MR.
