# Educational Patterns Reference

Reusable explanations for common issues. Agents should use these patterns for consistent, educational feedback.

## Structure & Decomposition

### Single Responsibility Principle

**Why it matters:**
Functions with multiple responsibilities are hard to test in isolation, harder to debug (which part failed?), and require changes for multiple reasons. When you can't name a function clearly, it's probably doing too much.

**The fix pattern:**
1. Identify distinct responsibilities (validation, transformation, persistence, notification)
2. Extract each into a focused function
3. Create a coordinator that calls them in sequence

**Example transformation:**
```python
# Before: One function, three responsibilities
def sync_user(user_id: str) -> None:
    data = api.fetch(user_id)      # Fetch
    clean = transform(data)         # Transform
    db.save(clean)                  # Persist

# After: Focused functions + coordinator
def fetch_user(user_id: str) -> RawUser: ...
def transform_user(raw: RawUser) -> User: ...
def save_user(user: User) -> None: ...

def sync_user(user_id: str) -> None:
    raw = fetch_user(user_id)
    user = transform_user(raw)
    save_user(user)
```

### Parameter Objects (Pydantic)

**Why it matters:**
Functions with many parameters are hard to call correctly, hard to extend (adding a parameter touches all call sites), and don't communicate intent. Grouping related parameters into a model makes the API clearer and enables validation.

**The fix pattern:**
```python
# Before: 8 parameters
def create_report(
    title: str, author: str, date: date,
    format: str, template: str, output_path: Path,
    include_charts: bool, page_size: str
) -> None: ...

# After: Pydantic model
class ReportConfig(BaseModel):
    title: str
    author: str
    date: date
    format: str = "pdf"
    template: str = "default"
    output_path: Path
    include_charts: bool = True
    page_size: str = "A4"

def create_report(config: ReportConfig) -> None:
    # Access config.title, config.author, etc.
    ...
```

### Tuple Unpacking Anti-Pattern

**Why it matters:**
When you unpack a tuple into N variables, then pass those N variables to another function, you've created fragile code. Adding a field requires changes in multiple places, and the compiler can't catch mismatches between unpacking and usage.

**The fix pattern:**
```python
# Before: Unpack then pass-through
def process(args: tuple) -> Result:
    (a, b, c, d, e) = args
    return do_work(a=a, b=b, c=c, d=d, e=e)

# After: Pydantic model with model_dump()
class TaskArgs(BaseModel):
    a: str
    b: int
    c: Path
    d: str
    e: bool

def process(args: TaskArgs) -> Result:
    return do_work(**args.model_dump())
```

### Guard Clauses

**Why it matters:**
Deep nesting makes code hard to follow. Each level of indentation adds cognitive load. Guard clauses (early returns for invalid cases) flatten the structure and make the "happy path" clear.

**The fix pattern:**
```python
# Before: Nested conditionals
def process(user: User | None) -> Result:
    if user:
        if user.is_active:
            if user.has_permission:
                return do_work(user)
    return None

# After: Guard clauses
def process(user: User | None) -> Result:
    if not user:
        return None
    if not user.is_active:
        return None
    if not user.has_permission:
        return None
    return do_work(user)
```

## Error Handling

### Silent Failure Anti-Pattern

**Why it matters:**
When exceptions are caught and ignored (or just logged), failures become invisible. In data pipelines, this means records silently disappear. You end up with partial results and no way to know what's missing.

**The fix pattern:**
```python
# Before: Silent failure
for record in records:
    try:
        result = process(record)
        results.append(result)
    except Exception:
        continue  # Record vanishes!

# After: Track failures explicitly
failed_count = 0
for record in records:
    try:
        result = process(record)
        results.append(result)
    except ProcessingError as e:
        logger.warning("processing failed", record_id=record.id, error=str(e))
        failed_count += 1

if failed_count > 0:
    logger.error("batch completed with failures", total=len(records), failed=failed_count)
```

### Swallowing Exceptions

**Why it matters:**
`except Exception: pass` or `except: continue` hides bugs. The code appears to work, but it's silently failing. This is especially dangerous in data pipelines where partial results look like complete results.

**The fix pattern:**
1. Catch specific exceptions you can handle
2. Log failures with context
3. Track failure counts
4. Consider failing fast for critical operations

### Default Values Masking Missing Data

**Why it matters:**
Using `.get("field", 0)` or `.get("field", "")` silently replaces missing data with defaults. This corrupts calculations (0 in a sum, empty string in concatenation) without any indication that data was missing.

**The fix pattern:**
```python
# Before: Default masks missing data
value = data.get("price", 0)
total += value  # Missing prices become 0, corrupting sum

# After: Explicit handling
price = data.get("price")
if price is None:
    logger.warning("missing price", record_id=data.get("id"))
    continue  # Or raise, or use a sentinel
total += price
```

## Type Safety

### Any Abuse

**Why it matters:**
`Any` disables type checking. It's a virus - any value that touches `Any` becomes `Any`. The type checker can't catch bugs in code that uses `Any`, defeating the purpose of type hints.

Per Python's typing module documentation, `Any` represents an unconstrained type that is compatible with every type. This flexibility comes at the cost of type safety - operations on `Any` values are not checked.

**The fix pattern:**
```python
# Before: Any leaks everywhere
data: Any = json.loads(raw)
user_id = data["user_id"]  # user_id is Any!

# After: TypedDict for dictionary types
from typing import TypedDict

class UserPayload(TypedDict):
    user_id: str
    name: str

data: UserPayload = json.loads(raw)
user_id = data["user_id"]  # user_id is str!

# Or with Pydantic (preferred - adds validation)
class UserPayload(BaseModel):
    user_id: str
    name: str

payload = UserPayload.model_validate_json(raw)
user_id = payload.user_id  # str, validated
```

**Learn more:** Python's `TypedDict` (from `typing` module) defines dictionary types with specific keys and value types. Type checking is enforced by static type checkers, not at runtime. Use `NotRequired` from `typing` to mark optional keys.

### Redundant isinstance Checks

**Why it matters:**
If the type annotation says `user: User`, then `isinstance(user, User)` is always true. The check adds noise and suggests you don't trust your types. Trust the type system, or fix the types.

**The fix pattern:**
```python
# Before: Redundant check
def process(user: User) -> None:
    if isinstance(user, User):  # Always true!
        user.do_thing()

# After: Trust the types
def process(user: User) -> None:
    user.do_thing()

# Legitimate use: Union discrimination
def handle(event: ClickEvent | KeyEvent) -> None:
    if isinstance(event, ClickEvent):
        handle_click(event)  # Narrowed to ClickEvent
```

### TypedDict for External Data

**Why it matters:**
When receiving JSON from APIs or files, `TypedDict` provides type safety without runtime validation overhead. For untrusted data, combine with Pydantic.

**The pattern:**
```python
from typing import TypedDict, NotRequired

class UserPayload(TypedDict):
    user_id: str
    name: str
    email: NotRequired[str]  # Optional key (Python 3.11+)

# Type checker enforces key access
def process(data: UserPayload) -> str:
    return data["user_id"]  # OK - key is required
    # data["missing"]  # Type error - key not defined
```

## Logging (structlog)

### F-strings in Log Messages

**Why it matters:**
Structured logging requires key-value pairs so logs can be searched, filtered, and aggregated. F-strings create unstructured messages that are hard to query in log aggregation tools.

Per Python's logging cookbook, structured logging uses key-value pairs that can be serialized to JSON for machine-readable log entries.

**The fix pattern:**
```python
# Before: Unstructured f-string
logger.info(f"Processing user {user_id} with {len(items)} items")

# After: Structured key-value pairs
logger.info("processing user", user_id=user_id, item_count=len(items))
```

### Print Statements

**Why it matters:**
`print()` bypasses the logging system entirely. Output goes to stdout, isn't captured in log files, has no level/timestamp/context, and can't be filtered or searched.

**The fix pattern:**
```python
# Before: print() for debugging
print(f"DEBUG: {variable}")

# After: Proper logging
logger.debug("variable value", variable=variable)

# Exception: CLI output intended for users
typer.echo(f"Processing {count} files...")  # OK - user-facing output
```

### Context Binding

**Why it matters:**
When multiple log calls share the same context (request_id, user_id, etc.), binding the context once prevents repetition and ensures consistency.

**The pattern:**
```python
import structlog

logger = structlog.get_logger()

def handle_request(request_id: str, user_id: str) -> None:
    # Bind context once
    log = logger.bind(request_id=request_id, user_id=user_id)

    log.info("starting request")  # Includes request_id, user_id
    result = process()
    log.info("completed", result=result)  # Still has context
```

## Security

### Injection Flaws

**Why it matters:**
When user-controlled input reaches a dangerous sink (SQL query, shell command, template engine) without sanitization, attackers can execute arbitrary commands. SQL injection alone accounts for a significant share of web application breaches (OWASP A03:2021).

**The fix pattern:**
```python
# Before: String interpolation in SQL
query = f"SELECT * FROM users WHERE id = '{user_id}'"
cursor.execute(query)

# After: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Before: Shell=True with user input
subprocess.run(f"convert {user_path}", shell=True)

# After: List args, no shell
subprocess.run(["convert", user_path])
```

### Secrets in Code

**Why it matters:**
Hardcoded secrets end up in git history, CI logs, and error messages. Once committed, they're effectively public — rotating them is expensive and often forgotten.

**The fix pattern:**
```python
# Before: Hardcoded
API_KEY = "sk-abc123..."

# After: Environment variable
API_KEY = os.environ["API_KEY"]

# After: Secret manager
secret = secretmanager.access_secret_version(name="projects/x/secrets/api-key")
```

### Path Traversal

**Why it matters:**
When user input controls file paths, `../../etc/passwd` style attacks can read or overwrite arbitrary files. This is especially dangerous in file upload/download endpoints.

**The fix pattern:**
```python
# Before: Direct concatenation
path = Path(upload_dir) / user_filename

# After: Resolve and verify containment
base = Path(upload_dir).resolve()
target = (base / user_filename).resolve()
if not target.is_relative_to(base):
    raise ValueError("Path traversal detected")
```

### Unsafe Deserialization

**Why it matters:**
`pickle.loads()`, `yaml.load()`, and `eval()` on untrusted data can execute arbitrary code. An attacker who controls the serialized payload controls your server.

**The fix pattern:**
```python
# Before: Unsafe
config = yaml.load(user_input)
data = pickle.loads(request.data)

# After: Safe
config = yaml.safe_load(user_input)
# For pickle: only deserialize from trusted internal sources
```

### Data Exposure in API Responses

**Why it matters:**
Returning full model dumps or raw exception details can leak password hashes, internal IDs, infrastructure details, and PII to API consumers.

**The fix pattern:**
```python
# Before: Full dump
return user.model_dump()  # Includes password_hash, email, internal fields

# After: Explicit response model
class UserResponse(BaseModel):
    id: str
    name: str
    role: str

return UserResponse.model_validate(user).model_dump()
```

## Pydantic Patterns

### Required vs Optional Fields

**Why it matters:**
In Pydantic v2, `Optional[T]` (or `T | None`) does NOT imply a default value. It only means the field accepts `None`. This is a common source of confusion.

**The rules:**
```python
from pydantic import BaseModel

class Example(BaseModel):
    f1: str              # Required, cannot be None
    f2: str | None       # Required, CAN be None (must be provided)
    f3: str | None = None  # Optional (has default), can be None
    f4: str = "default"  # Optional (has default), cannot be None
```

**Do NOT flag:** `field: T | None` without a default as "missing default". This creates a required-but-nullable field, which is often intentional.

### model_dump() for Passing to Functions

**Why it matters:**
When you need to pass a Pydantic model's data to a function that expects kwargs, `model_dump()` provides a clean conversion.

**The pattern:**
```python
class Config(BaseModel):
    host: str
    port: int
    timeout: int = 30

def connect(host: str, port: int, timeout: int) -> Connection:
    ...

config = Config(host="localhost", port=5432)
conn = connect(**config.model_dump())  # Unpacks to kwargs
```
