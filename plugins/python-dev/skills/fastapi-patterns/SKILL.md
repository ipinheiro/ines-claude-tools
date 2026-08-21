---
name: fastapi-patterns
description: This skill should be used when writing FastAPI endpoints, routers, dependencies, middleware, or lifespan handlers. Triggers on "fastapi", "APIRouter", "Depends", "HTTPException", "Query", "Path", "lifespan", "endpoint", "router".
---

# FastAPI patterns

**Follow these rules when writing FastAPI code.** These patterns come from the official FastAPI docs and from real bugs caught in code review.

## 1. Use `Annotated` everywhere

FastAPI's recommended pattern since 0.95+ is `Annotated` for all parameter metadata. This applies to `Query`, `Path`, `Header`, `Depends`, and `Body`.

```python
from typing import Annotated
from fastapi import Depends, Header, Path, Query

# GOOD - Annotated separates type from metadata
async def list_items(
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=500)] = 100,
    x_token: Annotated[str, Header()],
    db: Annotated[DatabaseService, Depends(get_db)],
) -> ItemListResponse:
    ...

# BAD - old style, mixes type with metadata
async def list_items(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=500),
    x_token: str = Header(...),
    db: DatabaseService = Depends(get_db),
) -> ItemListResponse:
    ...
```

### Reusable dependency aliases

The biggest win of `Annotated` is creating reusable dependency type aliases:

```python
from typing import Annotated
from fastapi import Depends

# Define once at module level
DbDep = Annotated[DatabaseService, Depends(get_db)]
ValkeyDep = Annotated[ValkeyService, Depends(get_valkey)]
CurrentUser = Annotated[str, Depends(get_user_email)]

# Reuse across all endpoints - clean and consistent
@router.post("/items")
async def create_item(
    request_body: CreateItemRequest,
    db: DbDep,
    valkey: ValkeyDep,
    user: CurrentUser,
) -> CreateItemResponse:
    ...
```

## 2. Optional query parameters: `None`, not empty string

Use `None` as the default for optional parameters. Never use empty string `""` as a "not provided" sentinel.

```python
# GOOD - None means "not provided", clean call sites
@router.get("/items")
async def list_items(
    division: Annotated[str | None, Query(description="Division filter")] = None,
    status: Annotated[str | None, Query(description="Status filter")] = None,
) -> ItemListResponse:
    # division is None or a real value - no ambiguity
    results = await db.query(division=division, status=status)
    ...

# BAD - empty string as sentinel, forces `or None` at every call site
@router.get("/items")
async def list_items(
    division: str = Query("", description="Division filter"),
    status: str = Query("", description="Status filter"),
) -> ItemListResponse:
    # Now every consumer has to do this dance:
    results = await db.query(
        division=division or None,  # repeated everywhere
        status=status or None,
    )
    ...
```

Why this matters:
- `None` correctly distinguishes "parameter not sent" from "parameter sent as empty string"
- Eliminates the `or None` conversion at every call site
- OpenAPI schema correctly marks the parameter as optional

## 3. Lifespan over startup/shutdown events

Use the `lifespan` context manager, not the deprecated `on_event("startup")` / `on_event("shutdown")` decorators.

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: initialise resources
    app.state.db = DatabaseService(...)
    app.state.valkey = await ValkeyService.connect(...)
    yield
    # Shutdown: clean up resources
    app.state.db.close()
    await app.state.valkey.close()

app = FastAPI(lifespan=lifespan)
```

Benefits:
- Single place for both startup and shutdown logic
- Resources created before `yield` are guaranteed to be cleaned up after
- The deprecated `@app.on_event` pattern has no such guarantee

## 4. Response model and return type

Prefer return type annotations over `response_model` when the types match:

```python
# GOOD - return type annotation, FastAPI uses it for docs + validation
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: DbDep) -> ItemResponse:
    ...

# ALSO GOOD - response_model when the return type differs from the model
# (e.g. returning an ORM object that gets filtered through the response model)
@router.get("/items/{item_id}", response_model=ItemPublic)
async def get_item(item_id: int, db: DbDep) -> Item:
    ...

# BAD - redundant: both response_model and return type saying the same thing
@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: DbDep) -> ItemResponse:
    ...
```

## 5. HTTPException patterns

Raise `HTTPException` directly - don't wrap it in try/except or return error dicts.

```python
# GOOD - direct, clear
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: DbDep) -> ItemResponse:
    result = await db.get_item(item_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return ItemResponse.model_validate(result)

# BAD - returning error dicts instead of raising
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: DbDep):
    result = await db.get_item(item_id)
    if not result:
        return {"error": "not found"}  # loses status code, breaks OpenAPI contract
    return result
```

Keep error messages short and useful. Include the identifier that wasn't found but don't leak internal details.

## 6. Pagination

Calculate `total_pages` correctly - return `0` for empty results, not `1`.

```python
total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
```

## 7. Router organisation

Group related endpoints into routers with clear tags:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
async def list_items(...) -> ItemListResponse: ...

@router.get("/{item_id}")
async def get_item(...) -> ItemResponse: ...

@router.post("/")
async def create_item(...) -> CreateItemResponse: ...
```

Include the router in the app with a versioned prefix:

```python
app.include_router(items.router, prefix="/api/v1")
```

## 8. Magic strings: extract header names and constants

Don't scatter string literals for header names, status values, or other constants across files.

```python
# GOOD - defined once, grep-friendly
OIDC_DATA_HEADER = "x-amzn-oidc-data"

def get_user_info(request: Request) -> UserInfo | None:
    oidc_data = request.headers.get(OIDC_DATA_HEADER)
    ...

# BAD - duplicated string literal
def get_user_info(request: Request) -> UserInfo | None:
    oidc_data = request.headers.get("x-amzn-oidc-data")
    ...

def check_auth(request: Request) -> bool:
    has_oidc = "x-amzn-oidc-data" in request.headers  # duplicated
    ...
```
