# Pydantic v2 Facts

Verified behaviors to prevent false positives in code review.
All facts verified against Pydantic v2 documentation via Context7.

---

## ConfigDict Inheritance

**Fact:** When a child class defines its own `model_config`, it is *merged* with the parent's configuration - not replaced. Child settings override or combine with inherited parent settings.

**Source:** Pydantic v2 docs - `docs/concepts/config.md` (Change behaviour globally)

**Example:**
```python
from pydantic import BaseModel, ConfigDict

class Parent(BaseModel):
    model_config = ConfigDict(extra='allow', str_to_lower=False)

class Model(Parent):
    model_config = ConfigDict(str_to_lower=True)  # Only overrides str_to_lower
    x: str

m = Model(x='FOO', y='bar')
print(Model.model_config)
#> {'extra': 'allow', 'str_to_lower': True}  # Merged!
```

**Do NOT flag:** Child classes that define partial `model_config` without repeating parent settings. This is correct behavior - settings are merged.

---

## Mutable Default Values

**Fact:** Pydantic automatically creates a deep copy of mutable default values (lists, dicts) for each model instance. This prevents the shared mutable default bug common in Python.

**Source:** Pydantic v2 docs - `docs/concepts/fields.md` (Validate default values > Mutable default values)

**Example:**
```python
from pydantic import BaseModel

class Model(BaseModel):
    item_counts: list[dict[str, int]] = [{}]  # Mutable default - OK!

m1 = Model()
m1.item_counts[0]['a'] = 1
print(m1.item_counts)  #> [{'a': 1}]

m2 = Model()
print(m2.item_counts)  #> [{}]  # Separate instance!
```

**Do NOT flag:** Mutable defaults like `field: list[T] = []` in Pydantic models. Unlike regular Python classes, Pydantic handles this safely.

---

## default_factory Usage

**Fact:** `default_factory` accepts any callable that returns the default value. Common patterns include `default_factory=list`, `default_factory=dict`, and `default_factory=lambda: uuid4().hex`.

**Source:** Pydantic v2 docs - `docs/concepts/fields.md` (Default values > Default factory)

**Example:**
```python
from uuid import uuid4
from pydantic import BaseModel, Field

class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    tags: list[str] = Field(default_factory=list)
```

**Do NOT flag:** `default_factory=list` or `default_factory=dict` as incorrect. These are idiomatic Pydantic patterns.

---

## Optional vs Required Nullable

**Fact:** In Pydantic v2, `Optional[T]` (or `T | None`) does NOT imply a default value of `None`. It only means the field accepts `None` as a valid value.

- `field: str` - Required, cannot be None
- `field: str | None` - Required, CAN be None (but must be provided)
- `field: str | None = None` - Optional (has default), can be None
- `field: str = "default"` - Optional (has default), cannot be None

**Source:** Pydantic v2 docs - `docs/migration.md` (Required, optional, and nullable fields)

**Example:**
```python
from typing import Optional
from pydantic import BaseModel, ValidationError

class Foo(BaseModel):
    f1: str              # required, cannot be None
    f2: Optional[str]    # required, can be None
    f3: Optional[str] = None  # not required, can be None
    f4: str = 'Foobar'   # not required, cannot be None

# f2 is REQUIRED even though it's Optional[str]
try:
    Foo(f1="a")  # Missing f2!
except ValidationError as e:
    print(e)  # f2 field required
```

**Do NOT flag:** `field: Type | None` without a default as "missing default". This is intentional - it creates a required-but-nullable field.

---

## computed_field Behavior

**Fact:** The `@computed_field` decorator includes `@property` or `@cached_property` attributes in serialization output (`model_dump()`, `model_dump_json()`). Computed fields appear in JSON schema with `readOnly: True`.

**Source:** Pydantic v2 docs - `docs/concepts/fields.md` (The computed_field decorator)

**Example:**
```python
from pydantic import BaseModel, computed_field

class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth

b = Box(width=1, height=2, depth=3)
print(b.model_dump())
#> {'width': 1.0, 'height': 2.0, 'depth': 3.0, 'volume': 6.0}
```

**Do NOT flag:** `@computed_field` without `@property` - Pydantic implicitly converts the method to a property. However, explicit `@property` is preferred for type checker compatibility.

---

## computed_field Ignores Input Values

**Fact:** Values passed for computed fields during construction or `model_validate()` are silently ignored. The computed property always calculates its value.

**Source:** Verified via manual testing (Pydantic v2.11+)

**Example:**
```python
from pydantic import BaseModel, computed_field

class Box(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

# Passed value is ignored
b = Box(width=2, height=3, area=999)
print(b.area)  #> 6.0  (not 999)

# Same with model_validate
b2 = Box.model_validate({'width': 4, 'height': 5, 'area': 123})
print(b2.area)  #> 20.0  (not 123)
```

**Do NOT flag:** Code that passes computed field values to `model_validate()` - they are silently ignored, not errors.
