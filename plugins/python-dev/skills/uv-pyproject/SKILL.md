---
name: uv-pyproject
description: This skill should be used when creating pyproject.toml files, setting up uv workspaces, auditing dependency versions, or diagnosing build/resolution issues. Triggers on "create pyproject", "pyproject.toml", "uv workspace", "dependency version mismatch", "build backend", "version floor", "workspace members".
---

# uv Pyproject Configuration

**Ensure pyproject.toml files follow uv best practices** for single projects and workspaces. This skill prevents dependency conflicts, build failures, and version misalignment.

Announce: "I'm using the uv-pyproject skill to [audit/create/fix] the pyproject configuration."

## The Rules

### 1. Use hatchling as Build Backend

**hatchling is the recommended build backend for uv projects.**

```toml
# CORRECT - hatchling backend
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
packages = ["src/mypackage"]

# For git dependencies, add:
[tool.hatch.metadata]
allow-direct-references = true
```

```toml
# AVOID - setuptools is legacy
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

**Why hatchling:**
- Native uv support, faster builds
- Simpler configuration
- Better error messages
- No need for `setup.py` or `setup.cfg`

### 2. Use dependency-groups, Not optional-dependencies

**uv prefers `[dependency-groups]` for dev/test dependencies.**

```toml
# CORRECT - dependency-groups
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pyright>=1.1.380",
    "ruff>=0.6.0",
]

# Install with: uv sync --group dev
```

```toml
# AVOID - optional-dependencies for dev tools
[project.optional-dependencies]
dev = ["pytest", "pyright"]

# This pattern is for library extras, not dev tools
```

### 3. Floor Versions to Known-Good Minimums

**Always specify lower bounds with `>=`, never unbounded.**

```toml
# CORRECT - floored versions
dependencies = [
    "pydantic>=2.9.0",
    "fastapi>=0.115.0",
    "structlog>=24.0.0",
]
```

```toml
# WRONG - no version bounds
dependencies = [
    "pydantic",
    "fastapi",
]

# WRONG - too permissive
dependencies = [
    "pydantic>=2.0",  # 2.0 is ancient, use actual minimum you need
]
```

**The version floor should be:**
- The version you actually tested with, OR
- A version that includes features you depend on

### 4. Align Version Floors Across Workspace Members

**In workspaces, shared dependencies MUST have aligned floors.**

```
# BAD - version floor mismatch
package-a/pyproject.toml:  pydantic>=2.0
package-b/pyproject.toml:  pydantic>=2.9.0

# Result: package-a could resolve pydantic==2.1.0, breaking package-b
```

```
# GOOD - aligned floors
package-a/pyproject.toml:  pydantic>=2.9.0
package-b/pyproject.toml:  pydantic>=2.9.0

# Result: consistent resolution across workspace
```

### 5. Workspace Configuration

**For multi-package repos, create a root pyproject.toml with workspace config.**

```toml
# Root pyproject.toml
[project]
name = "my-workspace"
version = "0.0.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["packages/*"]
# Or explicit:
# members = ["package-a", "package-b"]

# Exclude directories that aren't packages
exclude = ["scripts", "docs"]
```

**Member packages reference workspace deps:**

```toml
# packages/package-a/pyproject.toml
[project]
name = "package-a"
version = "0.1.0"
dependencies = [
    "package-b",  # Workspace member
    "pydantic>=2.9.0",
]

[tool.uv.sources]
package-b = { workspace = true }
```

### 6. Single Lock File for Workspaces

**Workspaces share one `uv.lock` at the root.** Delete member-level lock files.

```
my-workspace/
├── uv.lock              # Single lock file
├── pyproject.toml       # Workspace root
├── packages/
│   ├── package-a/
│   │   └── pyproject.toml   # No uv.lock here
│   └── package-b/
│       └── pyproject.toml   # No uv.lock here
```

## Audit Checklist

When auditing a pyproject.toml or workspace:

### Single Project

- [ ] Build backend is hatchling (not setuptools)
- [ ] All dependencies have version floors (`>=x.y.z`)
- [ ] Dev dependencies use `[dependency-groups]`
- [ ] `requires-python` specifies minimum version
- [ ] No `Any` version specifiers (bare package names)

### Workspace

- [ ] Root pyproject.toml exists with `[tool.uv.workspace]`
- [ ] Single `uv.lock` at root (none in members)
- [ ] Shared dependencies have aligned version floors
- [ ] Members use `{ workspace = true }` for internal deps
- [ ] `[tool.hatch.metadata] allow-direct-references = true` if using git deps

## Version Floor Alignment Process

When auditing a workspace for version misalignment:

1. **Find all pyproject.toml files:**
```bash
fd pyproject.toml --type f
```

2. **Extract shared dependencies:**
```bash
# Look for packages that appear in multiple pyproject files
rg "pydantic|fastapi|structlog" */pyproject.toml
```

3. **Identify the highest floor for each:**
```
pydantic: package-a says >=2.0, package-b says >=2.9.0
  -> Use >=2.9.0 everywhere
```

4. **Update all to match the highest floor**

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError` after sync | Build backend not configured | Add `[build-system]` with hatchling |
| Different versions in different packages | No workspace, separate locks | Create workspace root, single lock |
| `pydantic.ValidationError` in one package | Version floor mismatch | Align floors to highest needed |
| Build fails with git deps | Missing hatch config | Add `allow-direct-references = true` |
| `uv sync` ignores member | Not in workspace members | Add to `[tool.uv.workspace] members` |

## Red Flags

These thoughts mean STOP:

| Thought | Reality |
|---------|---------|
| "I'll just use setuptools, it's what I know" | hatchling is simpler and better supported by uv |
| "No version bound is fine, we'll pin in lock" | Lock doesn't protect CI or other developers |
| "Each package can have its own lock" | Workspaces MUST share one lock for consistency |
| ">=2.0 is safe, it's semver" | Libraries break within majors. Use what you tested. |
| "I'll align versions later" | Do it now. Misalignment causes subtle bugs. |

## Minimal pyproject.toml Template

### Single Project

```toml
[project]
name = "my-package"
version = "0.1.0"
description = "What this package does"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.9.0",
    "structlog>=24.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pyright>=1.1.380",
    "ruff>=0.6.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
packages = ["src/my_package"]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
```

### Workspace Root

```toml
[project]
name = "my-workspace"
version = "0.0.0"
requires-python = ">=3.12"

[tool.uv.workspace]
members = ["packages/*"]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pyright>=1.1.380",
    "ruff>=0.6.0",
]
```

### Workspace Member

```toml
[project]
name = "my-member"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "other-member",
    "pydantic>=2.9.0",
]

[tool.uv.sources]
other-member = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build]
packages = ["src/my_member"]

[tool.hatch.metadata]
allow-direct-references = true
```

## uv Resolution Settings

For workspace-wide constraints, add to root pyproject.toml:

```toml
[tool.uv]
# Set default version bounds when adding deps
add-bounds = "major"  # >=1.2.3, <2.0.0

# Force specific versions for build dependencies
build-constraint-dependencies = ["setuptools==60.0.0"]

# Override resolution for specific packages
override-dependencies = ["requests>=2.31.0"]
```

## References

- [uv Workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [uv Dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/)
- [uv Settings](https://docs.astral.sh/uv/reference/settings/)
- [hatchling Build Backend](https://hatch.pypa.io/latest/config/build/)
