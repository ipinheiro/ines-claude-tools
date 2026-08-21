# structlog Best Practices

Use **structlog** for all Python logging. Never use the stdlib `logging` module directly for application code.

## Installation

```bash
uv add structlog orjson
```

Optional: `uv add rich` for enhanced dev console output with pretty tracebacks.

## Configuration

### Where to configure

Call `structlog.configure()` once at application startup — before any logger is used. Placement depends on framework:

- **CLI / scripts**: Top of `main()` or `if __name__ == "__main__"` block
- **FastAPI / Starlette**: In a lifespan handler or top of `main.py`
- **Flask**: After `app = Flask(__name__)`, before routes
- **Django**: Bottom of `settings.py`
- **Dagster**: In a `@resource` or at the top of `definitions.py`

### Development configuration (human-readable console output)

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger("debug"),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Production configuration (JSON output, optimized)

```python
import structlog
import orjson

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(serializer=orjson.dumps),
    ],
    wrapper_class=structlog.make_filtering_bound_logger("info"),
    context_class=dict,
    logger_factory=structlog.BytesLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

### Environment-aware configuration (recommended pattern)

```python
import sys
import structlog


def configure_logging(*, debug: bool = False) -> None:
    """Configure structlog. Call once at application startup."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if sys.stderr.isatty() or debug:
        # Development: pretty console output
        import structlog.dev

        processors = [
            *shared_processors,
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(),
        ]
        min_level = "debug"
        factory = structlog.PrintLoggerFactory()
    else:
        # Production: JSON for log aggregation
        import orjson

        processors = [
            *shared_processors,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ]
        min_level = "info"
        factory = structlog.BytesLoggerFactory()

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(min_level),
        context_class=dict,
        logger_factory=factory,
        cache_logger_on_first_use=True,
    )
```

### stdlib integration (when third-party libs use `logging`)

Only use this when you need to capture logs from third-party libraries that use stdlib `logging`. This is the **only** case where importing `logging` is acceptable:

```python
import logging
import structlog

shared_processors = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
]

structlog.configure(
    processors=[
        *shared_processors,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

formatter = structlog.stdlib.ProcessorFormatter(
    processors=[
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        structlog.dev.ConsoleRenderer(),  # or JSONRenderer for prod
    ],
    foreign_pre_chain=shared_processors,
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)
```

## Logger Creation

### Module-level logger (preferred)

```python
import structlog

log = structlog.get_logger()
```

- Always use `structlog.get_logger()` at **module level**.
- Name the variable `log` consistently across the project.
- Never pass `__name__` — structlog auto-detects the caller module.

### Type hints for Pyright / ty

```python
import structlog

# When using make_filtering_bound_logger (recommended):
log: structlog.FilteringBoundLogger = structlog.get_logger()

# When using stdlib integration:
from structlog.stdlib import BoundLogger

log: BoundLogger = structlog.stdlib.get_logger()
```

## Logging Patterns

### Structured key-value pairs — always

```python
log.info("order created", order_id=order_id, user_id=user_id, total=total)
log.warning("rate limit exceeded", endpoint=endpoint, retry_after=30)
log.error("payment failed", order_id=order_id, error=str(exc))
```

### Never use string interpolation in log messages

```python
# BAD — defeats structured logging, wastes CPU if filtered
log.info(f"Processing order {order_id} for user {user_id}")
log.info("Processing order %s for user %s", order_id, user_id)
log.info(f"Processing order {order_id=}")

# GOOD
log.info("processing order", order_id=order_id, user_id=user_id)
```

### Event names: lowercase, descriptive, grep-friendly

```python
# Lowercase, no punctuation, action-oriented
log.info("processing started", batch_size=100)
log.info("user logged in", user_id=user_id)
log.info("cache miss", key=cache_key)
log.warning("connection retry", attempt=3, max_attempts=5)

# BAD: sentence-case, vague, or overly long messages
log.info("Processing has started for the batch.")
log.info("Something happened")
```

### Bind context for a scope

Use `log.bind()` to add context that applies to all subsequent log calls. Assign to a **new variable** to avoid shadowing:

```python
def process_order(order_id: str, user_id: str) -> None:
    order_log = log.bind(order_id=order_id, user_id=user_id)
    order_log.info("processing started")
    # ... work ...
    order_log.info("processing completed", duration_ms=elapsed)
```

**Critical**: never shadow the module-level `log` with `log = log.bind(...)` — Pyright will report "log is unbound". Use a descriptive name like `order_log`, `request_log`, etc.

### Context variables for cross-cutting context

Use `contextvars` for context that should appear in **all** log entries across function boundaries (request IDs, user IDs, correlation IDs):

```python
import uuid
from structlog.contextvars import bind_contextvars, clear_contextvars

# In middleware / request handler entry point:
clear_contextvars()
bind_contextvars(
    request_id=str(uuid.uuid4()),
    user_id=current_user.id,
)

# Now ALL log calls anywhere in the call stack include request_id and user_id
log.info("handling request")  # automatically has request_id, user_id
```

### Temporary context with `bound_contextvars`

```python
from structlog.contextvars import bound_contextvars

with bound_contextvars(batch_id=batch_id):
    process_batch()  # all logs inside include batch_id
# batch_id is removed from context after the block
```

### Exception logging

Use `exc_info=True` to capture the full traceback. **Never use `error=str(e)`** - it loses the stack trace and exception type, making debugging much harder.

```python
# BEST - log.exception() automatically attaches exc_info
try:
    risky_operation()
except SomeError:
    log.exception("operation failed", operation="risky_operation")

# ALSO GOOD - explicit exc_info=True on any log level
try:
    risky_operation()
except SomeError:
    log.error("operation failed", operation="risky_operation", exc_info=True)
    raise
```

When you don't need the exception variable for anything else (re-raising, extracting a field), drop the `as e` entirely:

```python
# GOOD - no unused variable
except ClientError:
    log.error("s3 upload failed", key=key, exc_info=True)
    return False

# BAD - error=str(e) loses the traceback and exception type
except ClientError as e:
    log.error("s3 upload failed", key=key, error=str(e))
    return False
```

If you need a truncated error string (e.g. for storing in a database field with a length limit), that's a separate concern from logging - still log with `exc_info=True`, and extract `str(e)` only for the storage path.

## Testing

### Capturing logs in pytest

```python
from structlog.testing import capture_logs


def test_order_processing():
    with capture_logs() as cap_logs:
        process_order("order-123", "user-456")

    assert cap_logs[0]["event"] == "processing started"
    assert cap_logs[0]["order_id"] == "order-123"
    assert cap_logs[-1]["event"] == "processing completed"
```

### Asserting log levels

```python
def test_warning_on_retry():
    with capture_logs() as cap_logs:
        do_something_with_retries()

    warnings = [entry for entry in cap_logs if entry["log_level"] == "warning"]
    assert len(warnings) == 1
    assert warnings[0]["attempt"] == 3
```

### Using CapturingLogger for detailed assertions

```python
import structlog
from structlog.testing import CapturingLogger


def test_registration_logging():
    cap_logger = CapturingLogger()
    test_log = structlog.wrap_logger(
        cap_logger,
        processors=[structlog.processors.add_log_level],
    )

    # Code under test using `test_log`
    test_log.info("registration_start", username="bob")
    test_log.info("registration_complete", username="bob", email="bob@example.com")

    assert len(cap_logger.calls) == 2
    assert cap_logger.calls[0].method_name == "info"
    assert cap_logger.calls[0].kwargs["username"] == "bob"
```

## Framework-Specific Patterns

### FastAPI middleware

```python
import uuid
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        clear_contextvars()
        bind_contextvars(
            request_id=request.headers.get("x-request-id", str(uuid.uuid4())),
            method=request.method,
            path=request.url.path,
        )
        log.info("request started")
        response = await call_next(request)
        log.info("request completed", status_code=response.status_code)
        return response
```

### Dagster integration

```python
import structlog
from dagster import op, OpExecutionContext
from structlog.contextvars import bind_contextvars, clear_contextvars

log = structlog.get_logger()


@op
def my_op(context: OpExecutionContext) -> None:
    clear_contextvars()
    bind_contextvars(
        dagster_run_id=context.run_id,
        op_name=context.op_def.name,
    )
    log.info("op started")
    # ... work ...
    log.info("op completed", row_count=result_count)
```

## Custom Processors

Write custom processors when you need to enrich, filter, or transform log events:

```python
import os
import structlog


def add_service_context(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Add service metadata to every log entry."""
    event_dict["service"] = "my-service"
    event_dict["environment"] = os.getenv("ENV", "development")
    return event_dict


def drop_health_checks(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Filter out noisy health check logs."""
    if event_dict.get("path") == "/health":
        raise structlog.DropEvent
    return event_dict
```

Add custom processors **before** the renderer in the processor chain:

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        add_service_context,
        drop_health_checks,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.dev.ConsoleRenderer(),
    ],
    # ...
)
```

## Performance Tips

1. **Set `cache_logger_on_first_use=True`** — avoids proxy logger assembly on every call.
2. **Use `make_filtering_bound_logger()`** — filtered-out levels become `return None` (zero-cost).
3. **Use `orjson` or `msgspec`** as JSON serializer instead of stdlib `json`.
4. **Use `BytesLoggerFactory`** with `orjson` — avoids decode/encode roundtrip.
5. **Avoid stdlib `logging`** for your own logs — use `PrintLoggerFactory` or `BytesLoggerFactory`.
6. **Bind to a local variable** in hot loops:
   ```python
   def process_items(items: list[Item]) -> None:
       loop_log = log.bind()  # resolve proxy once
       for item in items:
           loop_log.debug("processing item", item_id=item.id)
   ```
7. **Avoid logging in tight loops** at INFO+ in production — use DEBUG level and filter.

## Processor Chain Order

The order of processors matters. Recommended order:

```
1. merge_contextvars          — pull in context-local bindings first
2. Custom enrichment          — add service/env metadata
3. Custom filters             — drop noisy events early
4. add_log_level              — add level name to event dict
5. StackInfoRenderer          — render stack_info if present
6. format_exc_info / set_exc_info — handle exceptions
7. TimeStamper                — add timestamp
8. Renderer (last)            — ConsoleRenderer or JSONRenderer
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `log.info(f"msg {var}")` | `log.info("msg", key=var)` |
| `log.error("failed", error=str(e))` | `log.error("failed", exc_info=True)` - preserves full traceback |
| `log = log.bind(...)` shadowing | Use a new name: `order_log = log.bind(...)` |
| Configuring after first log call | Configure before any `get_logger()` usage |
| Using `logging.getLogger()` for app code | Use `structlog.get_logger()` everywhere |
| Missing `merge_contextvars` processor | Always include as first processor |
| `JSONRenderer()` without fast serializer | Add `serializer=orjson.dumps` |
| Forgetting `clear_contextvars()` in handlers | Always clear at request boundary |
| `import logging` for log levels | Use string levels: `"debug"`, `"info"`, `"warning"` |
