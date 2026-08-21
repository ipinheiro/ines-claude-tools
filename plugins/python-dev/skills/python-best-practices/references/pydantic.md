# Pydantic Best Practices

## Core Principle

**Pydantic is your first choice for structured data.** It provides validation, serialization, and type safety in one package.

## Model Definition

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class User(BaseModel):
    """User account information."""

    id: int
    email: str
    name: str = Field(min_length=1, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.lower()
```

## Field Configuration

### Use `Annotated` for field metadata (preferred)

**Always use `Annotated[type, Field(...)]` instead of `type = Field(...)`.** This is the Pydantic v2 recommended pattern. It cleanly separates the type from its metadata, makes fields reusable as type aliases, and keeps defaults visually distinct from validation.

```python
from typing import Annotated
from pydantic import Field

class Product(BaseModel):
    # Required field - no default needed
    name: str

    # Required with validation
    price: Annotated[float, Field(gt=0, description="Price in USD")]

    # Required with alias
    product_id: Annotated[str, Field(alias="productId")]

    # Optional with default
    description: str = ""

    # Optional with validation + default
    tags: Annotated[list[str], Field(min_length=1, description="At least one tag")] = []

    # Computed default
    created: Annotated[datetime, Field(default_factory=datetime.utcnow)]

    # Exclude from serialization
    internal_code: Annotated[str, Field(exclude=True)]
```

**Key rules:**
- Default values go at the end of the line (`= None`, `= []`), not inside `Field(default=...)`
- Never use `Field(...)` (the ellipsis) - it's redundant with `Annotated`; the field is required by default
- For required fields with no metadata, plain `name: str` is fine - no need for `Annotated`

### Reusable type aliases with `Annotated`

One of the biggest wins of `Annotated` is creating reusable validated types:

```python
from typing import Annotated
from pydantic import AfterValidator, BeforeValidator, Field

# Define once, reuse everywhere
Asin = Annotated[str, BeforeValidator(str.strip), AfterValidator(_validate_asin)]
PositiveInt = Annotated[int, Field(gt=0)]
ShortStr = Annotated[str, Field(min_length=1, max_length=100)]

class Order(BaseModel):
    asin: Asin                    # reused validated type
    quantity: PositiveInt          # reused constraint
    title: ShortStr               # reused constraint
```

### Legacy pattern (avoid in new code)

The old `= Field(...)` style still works but should not be used in new code:

```python
# OLD - avoid this
price: float = Field(..., gt=0, description="Price in USD")
tags: list[str] = Field(default_factory=list)

# NEW - use this
price: Annotated[float, Field(gt=0, description="Price in USD")]
tags: Annotated[list[str], Field(default_factory=list)]
```

## Configuration with model_config

```python
from pydantic import BaseModel, ConfigDict

class APIResponse(BaseModel):
    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Validate on assignment, not just init
        validate_assignment=True,
        # Extra fields are errors
        extra="forbid",
        # Use enum values, not enum objects
        use_enum_values=True,
        # Strip whitespace from strings
        str_strip_whitespace=True,
    )

    status: str
    data: dict[str, str]
```

## Validation Patterns

### Field Validators

```python
from pydantic import field_validator, model_validator

class Order(BaseModel):
    items: list[str]
    quantity: int
    discount: float = 0

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Order must have at least one item")
        return v

    @field_validator("discount")
    @classmethod
    def discount_range(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError("Discount must be between 0 and 1")
        return v
```

### Model Validators (Cross-Field)

```python
from pydantic import model_validator

class DateRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def end_after_start(self) -> "DateRange":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
```

## Serialization

```python
user = User(id=1, email="TEST@Example.com", name="Alice")

# To dict
user.model_dump()
# {'id': 1, 'email': 'test@example.com', 'name': 'Alice', ...}

# To JSON string
user.model_dump_json()

# Exclude fields
user.model_dump(exclude={"created_at", "metadata"})

# Include only specific fields
user.model_dump(include={"id", "email"})

# By alias
user.model_dump(by_alias=True)
```

## Parsing External Data

```python
# From dict
user = User.model_validate({"id": 1, "email": "a@b.com", "name": "Test"})

# From JSON string
user = User.model_validate_json('{"id": 1, "email": "a@b.com", "name": "Test"}')

# Strict mode (no coercion)
user = User.model_validate(data, strict=True)
```

## Settings Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
    )

    database_url: str
    debug: bool = False
    api_key: str
    max_connections: int = 10

# Loads from environment variables:
# APP_DATABASE_URL, APP_DEBUG, APP_API_KEY, APP_MAX_CONNECTIONS
settings = AppSettings()
```

## Composition and Inheritance

```python
class Address(BaseModel):
    street: str
    city: str
    country: str = "US"

class Person(BaseModel):
    name: str
    address: Address  # Nested model

class Employee(Person):
    employee_id: str
    department: str

# Nested parsing works automatically
data = {
    "name": "Alice",
    "address": {"street": "123 Main", "city": "Boston"},
    "employee_id": "E001",
    "department": "Engineering",
}
employee = Employee.model_validate(data)
```

## Discriminated Unions

```python
from typing import Literal
from pydantic import BaseModel

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meow_volume: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    bark_volume: int

class Owner(BaseModel):
    name: str
    pet: Cat | Dog = Field(discriminator="pet_type")

# Automatically routes to correct model
owner = Owner.model_validate({
    "name": "Alice",
    "pet": {"pet_type": "cat", "meow_volume": 5}
})
assert isinstance(owner.pet, Cat)
```

## Generic Models

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None

class UserData(BaseModel):
    id: int
    name: str

# Type-safe response
response: Response[UserData] = Response(
    success=True,
    data=UserData(id=1, name="Alice")
)
```

## Common Anti-Patterns

```python
# WRONG - Using dict when structure is known
def get_user() -> dict[str, Any]:
    return {"id": 1, "name": "Alice"}

# CORRECT - Use a model
def get_user() -> User:
    return User(id=1, name="Alice")


# WRONG - Manual validation
def create_user(data: dict) -> User:
    if "email" not in data:
        raise ValueError("email required")
    if not isinstance(data["email"], str):
        raise ValueError("email must be string")
    # ... more manual checks
    return User(**data)

# CORRECT - Let Pydantic validate
def create_user(data: dict[str, Any]) -> User:
    return User.model_validate(data)


# WRONG - Catching validation errors to return None
def parse_user(data: dict) -> User | None:
    try:
        return User.model_validate(data)
    except ValidationError:
        return None  # Swallows useful error info

# CORRECT - Let validation errors propagate (or handle meaningfully)
def parse_user(data: dict[str, Any]) -> User:
    return User.model_validate(data)  # Raises with detailed error
```
