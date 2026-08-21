# Snowflake Row Type Safety

Snowflake query results arrive as `list[dict[str, Any]]` because the database layer cannot know column types from SQL strings. **The `Any` must not leak past the first consumer.**

This reference covers the patterns and anti-patterns for crossing the Snowflake→Python type boundary, based on the overloaded `execute_query` in `api/services/database.py`.

## The Overloaded `execute_query`

The canonical pattern: `DatabaseService.execute_query` accepts an optional `model=` keyword arg. When provided, it calls `model.model_validate(row)` on each result row and returns `list[T]` instead of `list[dict[str, Any]]`.

```python
# Overload signatures (from database.py)
@overload
async def execute_query(
    self, query: str, params: QueryParams = None,
) -> list[SnowflakeRow]: ...

@overload
async def execute_query[T: BaseModel](
    self, query: str, params: QueryParams = None, *, model: type[T],
) -> list[T]: ...
```

**Always use `model=` when the query result has a known shape.** The untyped overload (`list[SnowflakeRow]`) exists only for ad-hoc/dynamic queries where the shape genuinely isn't known in advance.

## Pattern 1: Direct Column Name Match

When field names match SQL column names exactly, no aliasing is needed:

```python
class WorkRecord(FrozenModel):
    WORK_ID: str | int
    ISBN13: str
    TITLE: str
    DIVISION: str
    GLANCE_VIEWS: int
    SALES: int

# Call site — typed result, no Any escapes
results = await db.execute_query(query, (work_id,), model=WorkRecord)
work = results[0]  # WorkRecord, not dict[str, Any]
work.WORK_ID       # type-checked attribute access
```

Use this pattern for internal/DB-layer models where Pythonic naming doesn't matter.

## Pattern 2: validation_alias for Snake-Case Fields

When the model is API-facing or consumed by business logic that expects Pythonic names:

```python
class AssetRecord(FrozenModel):
    """Single asset record for listing.

    Constructed via model_validate() from Snowflake rows using
    validation_alias to map uppercase SQL column names.
    """
    model_config = ConfigDict(populate_by_name=True)

    isbn_identifier: str = Field(validation_alias="ISBN13")
    work_id: str = Field(validation_alias="WORK_ID")
    title: str = Field(default="", validation_alias="TITLE")
    asin: str | None = Field(None, validation_alias="ASIN")
    division: str | None = Field(None, validation_alias="DIVISION")
    imprint: str | None = Field(None, validation_alias="IMPRINT")
    author_short: str | None = Field(None, validation_alias="AUTHOR")
    status: str = Field(validation_alias="STATUS")
    glance_views: int | None = Field(None, validation_alias="GLANCE_VIEWS")

# Call site
records = await db.execute_query(data_query, tuple(params), model=AssetRecord)
records[0].work_id        # snake_case access, type-checked
records[0].isbn_identifier # str, not Any
```

**Key details:**
- `ConfigDict(populate_by_name=True)` allows construction by **either** the Python field name or the SQL alias — essential for tests
- `validation_alias` maps the uppercase SQL column to the snake_case field
- `Field(default=...)` for columns that may be absent in the result
- `Field(None, ...)` for nullable columns

## Pattern 3: Nullability — Match Reality, Not the Schema

Snowflake schemas are often permissive (most columns nullable). **Type the model based on what the application actually writes**, not the DDL:

```python
# ❌ WRONG — blindly copying Snowflake's nullable schema
class WorkRecord(FrozenModel):
    work_id: str | None = None    # WORK_ID is PK, never null
    isbn13: str | None = None     # Always populated
    title: str | None = None      # Always populated

# ✅ CORRECT — typed to match actual application behavior
class WorkRecord(FrozenModel):
    """Work record from ASSET_GENERATION_RESULTS.

    work_id/isbn13/title are non-optional because the ingestion pipeline
    guarantees these are always populated (enforced by the INSERT query).
    division/imprint may be null for backlist titles missing metadata.
    """
    work_id: str | int            # PK, always present
    isbn13: str                   # Always populated
    title: str                    # Always populated
    division: str | None = None   # May be null for backlist
    imprint: str | None = None    # May be null for backlist
```

Document the reasoning in a docstring so future maintainers know **why** a field is non-optional even though the DDL allows null.

## Pattern 4: Test Fixtures — Use Model Instances

When mocking `execute_query` with `model=`, the mock should return validated model instances, not raw dicts:

```python
# ❌ WRONG — raw dicts bypass validation, won't catch schema drift
mock_db.execute_query.return_value = [
    {"WORK_ID": "W123", "ISBN13": "9780000000001", "TITLE": "Test"}
]

# ✅ CORRECT — model instances, same as production
mock_db.execute_query.return_value = [
    WorkRecord(WORK_ID="W123", ISBN13="9780000000001", TITLE="Test")
]

# ✅ CORRECT — with validation_alias models, use Python field names
# (requires populate_by_name=True on the model)
mock_db.execute_query.return_value = [
    AssetRecord(
        isbn_identifier="9780000000001",
        work_id="W123",
        title="Test",
        status="PENDING",
    )
]
```

## Anti-Patterns

### Anti-Pattern 1: `cast()` to Narrow SnowflakeRow

```python
# ❌ FORBIDDEN — cast() is a no-op at runtime. If the row is missing a
# field or has wrong types, cast silently propagates bad data.
from typing import cast
results = await db.execute_query(query, (work_id,))
record = cast(WorkRecord, results[0])  # LIES to the type checker

# ✅ CORRECT — model_validate actually validates at runtime
results = await db.execute_query(query, (work_id,), model=WorkRecord)
record = results[0]  # Validated WorkRecord
```

### Anti-Pattern 2: Passing SnowflakeRow Into Business Logic

```python
# ❌ WRONG — Any leaks into business logic via dict access
results = await db.execute_query(query, (work_id,))
await process_work(results[0])  # process_work receives dict[str, Any]

async def process_work(row: SnowflakeRow) -> None:
    work_id = row["WORK_ID"]  # Any — typos in key names are silent
    title = row["TITEL"]      # Typo! No error at typecheck or runtime (returns None/KeyError)

# ✅ CORRECT — validate at the boundary, pass typed model downstream
results = await db.execute_query(query, (work_id,), model=WorkRecord)
await process_work(results[0])

async def process_work(record: WorkRecord) -> None:
    record.WORK_ID  # Type-checked, autocomplete works
    record.TITEL    # pyright error: "TITEL" is not a known member
```

### Anti-Pattern 3: Manual Row Destructuring

```python
# ❌ WRONG — manual destructuring with string keys, no type safety
results = await db.execute_query(query, (page_size, offset))
works = [
    ExcludedWork(
        work_id=row["WORK_ID"],
        title=row.get("TITLE"),
        reason=row["REASON"],
    )
    for row in results
]

# ✅ CORRECT — let model_validate do the mapping
results = await db.execute_query(query, (page_size, offset), model=ExcludedWork)
# results is already list[ExcludedWork], no manual mapping needed
```

If the model needs `validation_alias` for column name mapping, add it to the model definition once — don't repeat the mapping at every call site.

### Anti-Pattern 4: Inline Dicts in Test Data

```python
# ❌ WRONG — raw dicts don't validate, won't catch field renames
test_data = [
    {"WORK_ID": "W1", "ISBN13": "978...", "TITEL": "Oops"}  # typo goes unnoticed
]
mock_db.execute_query.return_value = test_data

# ✅ CORRECT — model constructor catches the typo immediately
test_data = [
    WorkRecord(WORK_ID="W1", ISBN13="978...", TITEL="Oops")  # pyright error + runtime ValidationError
]
```

## Where SnowflakeRow Is Correct

`SnowflakeRow` (`dict[str, Any]`) is the **correct type** in exactly one place: the generic query executor in `database.py`. That function cannot know the shape of arbitrary SQL results — `dict[str, Any]` is honest there.

The typed boundary is the `model=` parameter or the `model_validate()` call in each consumer. Everything downstream of that boundary should use the typed model.

```
┌─────────────┐     dict[str, Any]     ┌──────────────┐     WorkRecord     ┌────────────────┐
│  Snowflake   │ ──────────────────────▶│ execute_query │ ─────────────────▶│ Business Logic  │
│  (database)  │                        │  model=...    │                   │  (typed models) │
└─────────────┘                         └──────────────┘                    └────────────────┘
                  ▲ Any is correct here                    ▲ Any must not cross this boundary
```

## Quick Decision Guide

| Scenario | Approach |
|----------|----------|
| Query with known result shape | `execute_query(..., model=MyModel)` |
| Model fields match SQL column names | No aliases needed, use uppercase field names |
| Model needs Pythonic field names | `Field(validation_alias="SQL_NAME")` + `ConfigDict(populate_by_name=True)` |
| Column always populated by app logic | Non-optional field, document why in docstring |
| Column may be NULL in practice | `field: type \| None = Field(None, ...)` |
| Column may be absent from result | `field: type = Field(default=..., ...)` |
| Column needs type coercion | `field_validator(mode="before")` |
| Ad-hoc/dynamic query | Raw `execute_query(...)` → `list[SnowflakeRow]` is acceptable |
| Test fixtures | Use model instances, not raw dicts |
