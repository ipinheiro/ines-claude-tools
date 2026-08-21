# Common Typing Patterns

## JSON Type Alias

For JSON data, define a recursive type:

```python
from typing import TypeAlias

JsonValue: TypeAlias = (
    dict[str, "JsonValue"]
    | list["JsonValue"]
    | str
    | int
    | float
    | bool
    | None
)

def parse_config(raw: JsonValue) -> AppConfig:
    if not isinstance(raw, dict):
        raise TypeError("Config must be a dict")
    return AppConfig.model_validate(raw)
```

## Optional Parameters

```python
# ✅ CORRECT - Default None with union type
def fetch_user(
    user_id: int,
    include_deleted: bool = False,
    cache_ttl: int | None = None,
) -> User:
    ...

# ✅ CORRECT - Sentinel for "not provided" vs "provided as None"
_UNSET: object = object()

def update_field(
    value: str | None | object = _UNSET,
) -> None:
    if value is _UNSET:
        return  # Not provided
    # value is str | None here
```

## Callable Types

```python
from typing import Callable, ParamSpec, TypeVar

# Simple callback
Callback = Callable[[str, int], bool]

def register_handler(name: str, handler: Callback) -> None:
    ...

# Decorator preserving signature
P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

## Protocol for Structural Typing

```python
from typing import Protocol

class Renderable(Protocol):
    def render(self) -> str: ...

class HTMLWidget:
    def render(self) -> str:
        return "<div>widget</div>"

class MarkdownDoc:
    def render(self) -> str:
        return "# Doc"

def display(item: Renderable) -> None:
    print(item.render())

# Both work without explicit inheritance
display(HTMLWidget())
display(MarkdownDoc())
```

## TypeVar Constraints

```python
from typing import TypeVar

# Unconstrained - accepts any type
T = TypeVar("T")

# Bound - must be subtype of bound
UserT = TypeVar("UserT", bound=BaseUser)

# Constrained - must be one of these exact types
NumberT = TypeVar("NumberT", int, float)

def add_numbers(a: NumberT, b: NumberT) -> NumberT:
    return a + b  # Only works with int or float
```

## Self Type (Python 3.11+)

```python
from typing import Self

class Builder:
    def with_name(self, name: str) -> Self:
        self.name = name
        return self

    def with_value(self, value: int) -> Self:
        self.value = value
        return self

class ExtendedBuilder(Builder):
    def with_extra(self, extra: str) -> Self:
        self.extra = extra
        return self

# Returns ExtendedBuilder, not Builder
result = ExtendedBuilder().with_name("foo").with_extra("bar")
```

## Overloads for Different Return Types

```python
from typing import Literal, overload

@overload
def fetch(url: str, raw: Literal[True]) -> bytes: ...
@overload
def fetch(url: str, raw: Literal[False] = ...) -> str: ...
@overload
def fetch(url: str, raw: bool = False) -> bytes | str: ...

def fetch(url: str, raw: bool = False) -> bytes | str:
    response = requests.get(url)
    return response.content if raw else response.text
```

## Narrowing with Type Guards

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # items is now list[str]
        for s in items:
            print(s.upper())
```

## Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value: int = int_stack.pop()
```

## Covariance and Contravariance

```python
from typing import TypeVar

# Covariant - can use subtypes (for read-only)
T_co = TypeVar("T_co", covariant=True)

# Contravariant - can use supertypes (for write-only)
T_contra = TypeVar("T_contra", contravariant=True)

class Reader(Generic[T_co]):
    def read(self) -> T_co: ...

class Writer(Generic[T_contra]):
    def write(self, value: T_contra) -> None: ...

# Reader[Dog] is subtype of Reader[Animal] (covariant)
# Writer[Animal] is subtype of Writer[Dog] (contravariant)
```

## Async Types

```python
from typing import AsyncIterator, Awaitable
from collections.abc import Coroutine

# Async function return type
async def fetch_data() -> str:
    ...  # Returns Coroutine[Any, Any, str]

# Async generator
async def stream_lines(path: str) -> AsyncIterator[str]:
    async with aiofiles.open(path) as f:
        async for line in f:
            yield line

# Awaitable parameter
async def run_task(task: Awaitable[int]) -> int:
    return await task
```
