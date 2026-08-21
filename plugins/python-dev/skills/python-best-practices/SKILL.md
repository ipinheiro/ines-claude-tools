---
name: python-best-practices
description: This skill should be used when writing Python code, reviewing Python code, or making decisions about typing, error handling, or code structure. Triggers on "write python", "python code", "type hints", "typing", "Any type", "error handling", "pydantic", "data model".
---

# Python Best Practices

**Follow these rules when writing Python code.** This skill encodes lessons from real failures—type confusion, debugging nightmares, and maintenance hell. Every rule exists because ignoring it caused pain.

## The Rules

### 1. Type Everything. Escape Hatches Are Lies.

**Every function parameter and return type MUST have a type annotation.** No exceptions.

```python
# ✅ CORRECT
def process_user(user_id: int, options: dict[str, str] | None = None) -> User:
    ...

# ❌ FORBIDDEN - Missing types
def process_user(user_id, options=None):
    ...
```

### 2. Modern Syntax Only (Python 3.10+)

**NEVER import from `typing` for basic types.** Use built-in generics.

```python
# ✅ CORRECT - Modern syntax
list[str]
dict[str, int]
set[User]
tuple[int, str, float]
str | None
int | str | float

# ❌ FORBIDDEN - Legacy syntax
from typing import List, Dict, Set, Tuple, Optional, Union
List[str]
Dict[str, int]
Optional[str]
Union[int, str]
```

**Only import from `typing` what doesn't exist as a builtin:**
- `Any` - when genuinely needed (see below)
- `TypeVar` - for generics
- `Protocol` - for structural subtyping
- `Callable` - for function types
- `Literal` - for literal types
- `TypedDict` - for typed dictionaries
- `ClassVar` - for class variables

### 3. `Any` Is a Code Smell

**`Any` means "I gave up on type safety."** Every `Any` is tech debt.

#### When `Any` Is FORBIDDEN

```python
# ❌ FORBIDDEN - Lazy typing
def process(data: Any) -> Any:
    ...

# ❌ FORBIDDEN - "I don't know what this is"
config: Any = load_config()

# ❌ FORBIDDEN - Dict of unknown stuff
cache: dict[str, Any] = {}
```

#### When `Any` Is Acceptable

1. **Third-party library boundaries** with no stubs:
```python
# ✅ OK - External library with no types
result: Any = weird_untyped_library.do_thing()
# Immediately narrow the type
parsed: UserData = UserData.model_validate(result)
```

2. **JSON/dynamic data at system boundaries** (but narrow immediately):
```python
# ✅ OK - JSON input, immediately validated
def handle_webhook(payload: Any) -> WebhookEvent:
    return WebhookEvent.model_validate(payload)  # Narrow immediately
```

3. **Generic containers that truly accept anything** (rare):
```python
# ✅ OK - Genuinely polymorphic
def serialize_to_json(obj: Any) -> str:
    return json.dumps(obj, default=str)
```

#### The Rule

**If you write `Any`, you MUST either:**
1. Narrow it to a concrete type within 3 lines, OR
2. Add a comment explaining why `Any` is unavoidable

### 4. Prefer Specific Types Over Broad Ones

```python
# ❌ TOO BROAD
def process(items: list) -> dict:
    ...

# ❌ STILL TOO BROAD
def process(items: list[Any]) -> dict[str, Any]:
    ...

# ✅ CORRECT - Specific types
def process(items: list[OrderItem]) -> dict[str, OrderSummary]:
    ...
```

### 5. Use `object` Not `Any` for "Accepts Anything Safely"

```python
# ❌ WRONG - Any disables type checking
def log_value(value: Any) -> None:
    print(value)  # Any allows calling .foo() with no error

# ✅ CORRECT - object is the true base type
def log_value(value: object) -> None:
    print(value)  # Safe - only allows operations valid on all objects
```

### 6. TypedDict for Structured Dicts

**If a dict has known keys, use TypedDict.**

```python
# ❌ WRONG - Loses structure information
def get_user() -> dict[str, Any]:
    return {"name": "Alice", "age": 30, "active": True}

# ✅ CORRECT - Preserves structure
class UserDict(TypedDict):
    name: str
    age: int
    active: bool

def get_user() -> UserDict:
    return {"name": "Alice", "age": 30, "active": True}

# ✅ EVEN BETTER - Use Pydantic
class User(BaseModel):
    name: str
    age: int
    active: bool = True
```

### 7. Never Suppress Type Errors

```python
# ❌ FORBIDDEN
x = get_value()  # type: ignore

# ❌ FORBIDDEN
x = cast(str, mystery_value)  # Lying to the type checker

# ✅ CORRECT - Fix the actual type
x: str = get_value()  # If this errors, fix get_value's return type
```

**If pyright complains, the code is wrong.** Trace to the source and fix it.

### 8. Use `match` for Structural Dispatch (Python 3.10+)

**Use `match` when dispatching on the structure or type of data. Don't use it as a fancy if/elif.**

#### When `match` IS the right tool

**Type/variant dispatch** — when handling union types, tagged data, or polymorphic structures:

```python
# ✅ CORRECT — structural pattern matching
match event:
    case ClickEvent(x=x, y=y):
        handle_click(x, y)
    case KeyEvent(key=key, modifiers=mods):
        handle_key(key, mods)
    case _:
        logger.warning("unhandled event", event_type=type(event).__name__)
```

**Destructuring nested data** — when extracting values from complex structures:

```python
# ✅ CORRECT — cleaner than nested if/elif with isinstance
match command:
    case {"action": "create", "payload": {"name": str(name), "type": str(kind)}}:
        create_resource(name, kind)
    case {"action": "delete", "id": int(resource_id)}:
        delete_resource(resource_id)
    case {"action": action}:
        raise ValueError(f"unknown action: {action}")
```

**Enum/literal dispatch** — when branching on a known set of values with associated data:

```python
# ✅ CORRECT — exhaustive matching with guards
match status, role:
    case ("active", "admin"):
        grant_full_access()
    case ("active", _):
        grant_read_access()
    case ("suspended", _):
        deny_access()
```

#### When `match` is NOT the right tool

**Simple value equality** — use `if/elif` or a dict lookup:

```python
# ❌ WRONG — match adds nothing here
match color:
    case "red":
        return "#ff0000"
    case "blue":
        return "#0000ff"

# ✅ CORRECT — dict lookup
COLORS = {"red": "#ff0000", "blue": "#0000ff"}
return COLORS[color]
```

**Boolean conditions** — match can't express arbitrary predicates well:

```python
# ❌ WRONG — guard clauses do this better
match user:
    case user if user.age > 18 and user.is_active:
        ...

# ✅ CORRECT — guard clauses
if user.age <= 18:
    raise ValueError("underage")
if not user.is_active:
    raise ValueError("inactive")
```

#### The Rule

**Use `match` when you're dispatching on shape or type. Use `if/elif` when you're testing conditions. Use a dict when you're mapping values.**

| Pattern | Use |
|---------|-----|
| Branch on type of value | `match` with class patterns |
| Branch on structure of dict/tuple | `match` with mapping/sequence patterns |
| Branch on enum/literal value with associated data | `match` |
| Branch on simple equality | dict lookup |
| Branch on boolean conditions | `if/elif` with guard clauses |
| Branch on 2 options | `if/else` |

### 9. Snowflake Row Type Safety

**Snowflake query results arrive as `list[dict[str, Any]]` because the database layer cannot know column types from SQL strings. The `Any` MUST NOT leak past the first consumer.**

Use `model_validate` with `validation_alias` to cross the boundary:

```python
class WorkRecord(FrozenModel):
    work_id: Annotated[str | int, Field(validation_alias="WORK_ID")]
    isbn13: Annotated[str, Field(validation_alias="ISBN13")]
    title: Annotated[str, Field(validation_alias="TITLE")] = ""
    division: Annotated[str | None, Field(validation_alias="DIVISION")] = None

# At the call site — one line, no Any escapes
record = WorkRecord.model_validate(results[0])
```

**Rules:**
1. Never pass `SnowflakeRow` (`dict[str, Any]`) into business logic — always validate into a Pydantic model first
2. Never use `cast()` to narrow `SnowflakeRow` — it lies to the type checker with zero runtime safety
3. Use `validation_alias` to map uppercase SQL column names to snake_case fields
4. Use `Field(default=...)` for columns that may be absent, `field_validator(mode="before")` for columns that may be NULL but need coercion
5. Use `ConfigDict(populate_by_name=True)` if the model is also constructed directly (e.g., in tests) with Python field names
6. `SnowflakeRow` stays as `dict[str, Any]` in `database.py` — that's the correct type for the generic query executor. The typed boundary is the `model_validate` call in each consumer

### 10. Avoid Positional Coupling in SQL

**SQL queries break silently when columns are reordered or added.** Positional parameters and tuple unpacking create invisible coupling between Python code and column order.

#### Named parameters over positional

**Above 4 parameters, use named parameter dicts (`:key`) instead of positional `?` lists.** The column-to-value mapping must be explicit so reordering or adding columns doesn't require counting question marks.

```python
# ❌ FRAGILE - 12 positional params, one reorder breaks everything silently
db.execute(
    "INSERT INTO books (title, isbn, author, publisher, year, pages, "
    "language, format, price, stock, category, active) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (title, isbn, author, publisher, year, pages,
     language, fmt, price, stock, category, active),
)

# ✅ CORRECT - named params, column-to-value mapping is explicit
db.execute(
    "INSERT INTO books (title, isbn, author, publisher, year, pages, "
    "language, format, price, stock, category, active) "
    "VALUES (:title, :isbn, :author, :publisher, :year, :pages, "
    ":language, :format, :price, :stock, :category, :active)",
    {
        "title": title, "isbn": isbn, "author": author,
        "publisher": publisher, "year": year, "pages": pages,
        "language": language, "format": fmt, "price": price,
        "stock": stock, "category": category, "active": active,
    },
)
```

For 1-4 parameters, positional `?` is fine - the mapping is obvious at a glance.

#### Row access by name over tuple unpacking

**Use `sqlite3.Row` (or a row factory) instead of tuple unpacking for SELECT results.** `row["column_name"]` survives column reordering; `col_a, col_b, col_c = row` does not.

```python
# ❌ FRAGILE - adding a column or reordering breaks all unpack sites
cursor.execute("SELECT id, title, isbn, author, year FROM books WHERE id = ?", (book_id,))
book_id, title, isbn, author, year = cursor.fetchone()

# ✅ CORRECT - access by name, immune to column reordering
conn.row_factory = sqlite3.Row  # set once on the connection
cursor = conn.execute(
    "SELECT id, title, isbn, author, year FROM books WHERE id = ?", (book_id,)
)
row = cursor.fetchone()
title = row["title"]
year = row["year"]
```

For Snowflake results (already `dict[str, Any]`), this is already handled - validate into a Pydantic model per rule 9.

### 11. Constrain SQL Identifiers with Enums, Not f-strings

**When SQL identifiers (schema names, table names) come from application config rather than user input, constrain them with enums and pre-computed static SQL instead of f-string interpolation.** Even trusted config values should not be interpolated into SQL as raw strings - it creates a pattern that's easy to misuse and impossible for static analysis to distinguish from real injection.

#### Enum + static dict for complete SQL fragments

When the set of values is closed (e.g. schema names), map each enum member to a pre-built SQL string. The function returns the string from the dict, never interpolates.

```python
from enum import StrEnum

class Schema(StrEnum):
    APLUS_DEV = "dsa_dev.aplus_dev"
    APLUS_PROD = "dsa_dev.aplus_prod"

    @property
    def use_schema_sql(self) -> str:
        return _USE_SCHEMA_SQL[self]

_USE_SCHEMA_SQL: dict[Schema, str] = {
    Schema.APLUS_DEV: "USE SCHEMA dsa_dev.aplus_dev",
    Schema.APLUS_PROD: "USE SCHEMA dsa_dev.aplus_prod",
}
```

The function signature changes from `schema: str` to `schema: Schema`, so the type system rejects arbitrary strings at the call site.

#### Double-quote identifiers when column names are dynamic

When column names come from a DataFrame, always quote with `"` and escape embedded double quotes by doubling them:

```python
safe_name = col_name.replace('"', '""')
f'$1:"{safe_name}"::{sf_type} AS "{safe_name}"'
```

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "I'll just use `Any` for now" | `Any` spreads. Fix it now or fix it everywhere later. |
| "The types are too complex" | Complex types reveal complex code. Simplify the code. |
| "Type hints slow me down" | Type errors found later slow you down 10x more. |
| "It's just a script" | Scripts become modules. Type it correctly from the start. |
| "I'll add types later" | You won't. Do it now. |
| "pyright is being too strict" | pyright is catching bugs. Thank it and fix the code. |
| "The column order won't change" | It will. And the bug will be silent. Use named params and row access by name. |
| "I'll just use `# nosec`, it's from config" | Constrain with an enum so the type system enforces safety, not a comment. |

## Rationalization Table

| Excuse | Reality |
|--------|---------|
| "This dict really could have any values" | Then use `TypedDict` with optional keys, or `Mapping[str, ConcreteType]`. |
| "`Any` is fine at the boundary" | Only if you narrow immediately. Otherwise you're just propagating uncertainty. |
| "The library doesn't have types" | Write a stub, use `Any` with immediate narrowing, or find a typed alternative. |
| "Generics are confusing" | Learn them. They're essential for reusable, type-safe code. |
| "It works, so the types don't matter" | Types aren't for the computer. They're for the next person reading this code. |
| "The value comes from config, not user input" | Config values change. Enum-constrained SQL is safe by construction. f-string SQL is safe by convention - and conventions break. |

## Quick Reference

### Type Syntax Cheat Sheet

```python
# Basics
x: int = 1
name: str = "hello"
flag: bool = True
value: float = 3.14

# Collections (use lowercase builtins)
items: list[str] = []
mapping: dict[str, int] = {}
unique: set[User] = set()
pair: tuple[int, str] = (1, "a")
fixed: tuple[int, ...] = (1, 2, 3)  # Variable-length homogeneous

# Unions (use |)
maybe: str | None = None
multi: int | str | float = 42

# Callables
handler: Callable[[int, str], bool]  # Takes int, str; returns bool
simple: Callable[..., None]  # Any args, returns None

# Generics
T = TypeVar("T")
def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### When to Use What

| Situation | Use This |
|-----------|----------|
| Known structure | Pydantic model or TypedDict |
| Optional value | `T \| None` |
| Multiple possible types | `T1 \| T2 \| T3` |
| Any JSON value | `JsonValue` type alias (see references) |
| Callback function | `Callable[[Args], Return]` |
| Reusable container | Generic with `TypeVar` |
| External untyped data | `Any` + immediate Pydantic validation |
| Unknown but safe | `object` |

## See Also

- `references/patterns.md` - Common typing patterns and examples
- `references/pydantic.md` - Pydantic best practices
- `references/generics.md` - Generic types guide
- `references/structlog.md` - Structured logging with structlog
- `references/snowflake-row-type-safety.md` - Crossing the Snowflake→Python type boundary with model_validate
