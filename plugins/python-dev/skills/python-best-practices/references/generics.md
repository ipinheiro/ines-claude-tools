# Generic Types Guide

## Why Generics?

Generics let you write reusable code that preserves type information. Without generics, you lose type safety or repeat code.

```python
# ❌ WITHOUT GENERICS - Loses type info
def first_item(items: list) -> object | None:
    return items[0] if items else None

result = first_item([1, 2, 3])  # result is 'object | None', not 'int | None'


# ✅ WITH GENERICS - Preserves type info
from typing import TypeVar

T = TypeVar("T")

def first_item(items: list[T]) -> T | None:
    return items[0] if items else None

result = first_item([1, 2, 3])  # result is 'int | None'
```

## TypeVar Basics

```python
from typing import TypeVar

# Create a type variable
T = TypeVar("T")  # Name string must match variable name

# Use in function
def identity(x: T) -> T:
    return x

# Type is preserved through the function
s: str = identity("hello")  # T = str
n: int = identity(42)       # T = int
```

## Bounded TypeVars

Restrict a TypeVar to subtypes of a specific class:

```python
from typing import TypeVar

class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "woof"

class Cat(Animal):
    def speak(self) -> str:
        return "meow"

# T must be Animal or a subclass
AnimalT = TypeVar("AnimalT", bound=Animal)

def make_speak(animal: AnimalT) -> AnimalT:
    print(animal.speak())
    return animal

dog: Dog = make_speak(Dog())  # Returns Dog, not Animal
cat: Cat = make_speak(Cat())  # Returns Cat, not Animal
```

## Constrained TypeVars

Restrict to specific types (not subtypes):

```python
from typing import TypeVar

# Must be exactly int or float (not subclasses)
Number = TypeVar("Number", int, float)

def add(a: Number, b: Number) -> Number:
    return a + b

add(1, 2)      # OK: int
add(1.0, 2.0)  # OK: float
add(1, 2.0)    # Error: mixed types
```

## Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Single type parameter
class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

# Multiple type parameters
class Pair(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value

# Usage with explicit types
box: Box[int] = Box(42)
pair: Pair[str, int] = Pair("age", 30)

# Type inference
box2 = Box("hello")  # Box[str]
```

## Generic Protocols

Combine protocols with generics for flexible interfaces:

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Comparable(Protocol[T]):
    def __lt__(self, other: T) -> bool: ...
    def __gt__(self, other: T) -> bool: ...

def max_value(a: T, b: T) -> T:
    return a if a > b else b

# Works with any type that implements comparison
max_value(1, 2)           # int
max_value("a", "b")       # str
max_value(1.0, 2.0)       # float
```

## ParamSpec for Decorators

Preserve function signatures in decorators:

```python
from typing import ParamSpec, TypeVar, Callable
from functools import wraps

P = ParamSpec("P")
R = TypeVar("R")

def retry(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for _ in range(times - 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    continue
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry(3)
def fetch_data(url: str, timeout: int = 30) -> dict[str, str]:
    ...

# Signature is preserved: (url: str, timeout: int = 30) -> dict[str, str]
```

## Concatenate for Partial Application

Add parameters to a callable:

```python
from typing import Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

class Logger:
    def log(self, message: str) -> None:
        print(message)

def with_logging(
    func: Callable[Concatenate[Logger, P], R]
) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger = Logger()
        return func(logger, *args, **kwargs)
    return wrapper

@with_logging
def process_data(logger: Logger, data: str) -> int:
    logger.log(f"Processing: {data}")
    return len(data)

# Callable is now: (data: str) -> int
result = process_data("hello")  # Logger is injected
```

## TypeVarTuple (Python 3.11+)

For variadic generics:

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")

def make_tuple(*args: Unpack[Ts]) -> tuple[Unpack[Ts]]:
    return args

# Preserves exact tuple type
result = make_tuple(1, "hello", 3.14)
# type: tuple[int, str, float]
```

## Common Patterns

### Repository Pattern

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

class Repository(Generic[ModelT]):
    def __init__(self, model_class: type[ModelT]) -> None:
        self._model_class = model_class
        self._storage: dict[int, ModelT] = {}

    def get(self, id: int) -> ModelT | None:
        return self._storage.get(id)

    def save(self, item: ModelT) -> ModelT:
        # Assumes item has an 'id' attribute
        self._storage[item.id] = item  # type: ignore[attr-defined]
        return item

    def all(self) -> list[ModelT]:
        return list(self._storage.values())

# Usage
class User(BaseModel):
    id: int
    name: str

user_repo: Repository[User] = Repository(User)
user_repo.save(User(id=1, name="Alice"))
user: User | None = user_repo.get(1)  # Correctly typed
```

### Builder Pattern

```python
from typing import Generic, TypeVar, Self

T = TypeVar("T")

class Builder(Generic[T]):
    def __init__(self) -> None:
        self._config: dict[str, object] = {}

    def with_option(self, key: str, value: object) -> Self:
        self._config[key] = value
        return self

    def build(self) -> T:
        raise NotImplementedError

class UserBuilder(Builder["User"]):
    def with_name(self, name: str) -> Self:
        return self.with_option("name", name)

    def with_email(self, email: str) -> Self:
        return self.with_option("email", email)

    def build(self) -> "User":
        return User(
            name=str(self._config["name"]),
            email=str(self._config["email"]),
        )
```

### Service Locator

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class ServiceLocator:
    _services: dict[type, object] = {}

    @classmethod
    def register(cls, service_type: type[T], instance: T) -> None:
        cls._services[service_type] = instance

    @classmethod
    def get(cls, service_type: type[T]) -> T:
        service = cls._services.get(service_type)
        if service is None:
            raise KeyError(f"Service {service_type} not registered")
        return service  # type: ignore[return-value]

# Usage
class DatabaseService:
    def query(self, sql: str) -> list[dict[str, str]]:
        ...

ServiceLocator.register(DatabaseService, DatabaseService())
db: DatabaseService = ServiceLocator.get(DatabaseService)
```

## Anti-Patterns

```python
# ❌ WRONG - TypeVar used only once (useless)
T = TypeVar("T")
def process(items: list[T]) -> int:  # T not in return type
    return len(items)

# ✅ CORRECT - Just use concrete type or Any
def process(items: list[object]) -> int:
    return len(items)


# ❌ WRONG - TypeVar with no constraints when needed
T = TypeVar("T")
def sort_items(items: list[T]) -> list[T]:
    return sorted(items)  # Error: T may not be comparable

# ✅ CORRECT - Add bound or constraint
from typing import Protocol

class Comparable(Protocol):
    def __lt__(self, other: object) -> bool: ...

CT = TypeVar("CT", bound=Comparable)
def sort_items(items: list[CT]) -> list[CT]:
    return sorted(items)
```
