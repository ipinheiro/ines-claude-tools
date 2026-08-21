---
name: dbt-python-integration
description: This skill should be used when integrating dbt with Python projects, invoking dbt programmatically, parsing dbt artifacts, or structuring projects that combine dbt and Python. Triggers on "dbt", "dbt run", "dbtRunner", "manifest.json", "run_results.json", "dbt artifacts", "dbt python", "data transformation".
---

# dbt + Python Integration Best Practices

**Follow these rules when integrating dbt into Python projects.** This skill encodes lessons from real failures—broken invocations, unhandled errors, artifact parsing nightmares, and environment conflicts. Every rule exists because ignoring it caused pain.

## The Rules

### 1. Use `dbtRunner` for Programmatic Invocation (dbt 1.5+)

**Never shell out to dbt with `subprocess` when `dbtRunner` is available.** The programmatic API provides structured results, proper error handling, and manifest reuse.

```python
# ✅ CORRECT - dbtRunner (dbt 1.5+)
from dbt.cli.main import dbtRunner, dbtRunnerResult

dbt = dbtRunner()
result: dbtRunnerResult = dbt.invoke(["run", "--select", "my_model"])

if result.success:
    print("dbt run succeeded")
else:
    if result.exception:
        raise result.exception
    print(f"dbt run failed: {result.result}")

# ❌ WRONG - Subprocess invocation
import subprocess
subprocess.run(["dbt", "run", "--select", "my_model"], check=True)  # No structured output!
```

### 2. Always Check `dbtRunnerResult` Properly

**The `success` attribute alone is not enough.** Handle all three states: success, handled failure, and unhandled exception.

```python
# ✅ CORRECT - Full result handling
from dbt.cli.main import dbtRunner, dbtRunnerResult

def run_dbt_command(args: list[str]) -> dbtRunnerResult:
    dbt = dbtRunner()
    result = dbt.invoke(args)

    if result.exception:
        # Unhandled error - dbt didn't complete (exit code 2)
        raise RuntimeError(f"dbt crashed: {result.exception}") from result.exception

    if not result.success:
        # Handled error - e.g., test failures, model errors (exit code 1)
        # result.result contains details
        return result  # Let caller decide how to handle

    return result

# ❌ WRONG - Ignoring exception case
result = dbt.invoke(["run"])
if not result.success:
    print("Failed")  # But WHY? Was it a test failure or a crash?
```

### 3. Reuse Manifests for Performance

**Parsing the manifest is expensive.** If running multiple commands, parse once and reuse.

```python
# ✅ CORRECT - Manifest reuse
from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest

# Parse once
parse_result: dbtRunnerResult = dbtRunner().invoke(["parse"])
manifest: Manifest = parse_result.result

# Reuse for subsequent commands
dbt = dbtRunner(manifest=manifest)
dbt.invoke(["run", "--select", "tag:daily"])
dbt.invoke(["test", "--select", "tag:daily"])

# ❌ WRONG - Reparsing on every invocation
dbtRunner().invoke(["run", "--select", "tag:daily"])  # Parses manifest
dbtRunner().invoke(["test", "--select", "tag:daily"])  # Parses again!
```

### 4. Isolate dbt in Virtual Environments

**dbt has heavy dependencies that conflict with many packages.** Always isolate.

```python
# ✅ CORRECT - Project structure with isolated dbt
"""
my_project/
├── pyproject.toml          # Your main project deps (polars, etc.)
├── src/
│   └── my_project/
├── dbt_project/            # dbt project lives here
│   ├── dbt_project.yml
│   ├── models/
│   └── requirements.txt    # dbt-core, dbt-snowflake, etc.
└── scripts/
    └── run_dbt.py          # Invokes dbt (runs in dbt venv)
"""

# If you MUST run dbt from your main project, use subprocess with venv:
import subprocess
import sys

def run_dbt_isolated(args: list[str], dbt_venv: str = ".dbt-venv") -> int:
    """Run dbt in an isolated virtual environment."""
    python_path = f"{dbt_venv}/bin/python"
    return subprocess.run(
        [python_path, "-m", "dbt.cli.main"] + args,
        check=False
    ).returncode
```

### 5. Type Your dbt Integration Code

**Use proper types for dbt objects.** The contracts module provides the types.

```python
# ✅ CORRECT - Typed dbt integration
from dbt.cli.main import dbtRunner, dbtRunnerResult
from dbt.contracts.graph.manifest import Manifest
from dbt.contracts.results import RunExecutionResult, RunResult
from dbt.artifacts.schemas.freshness import FreshnessResult

def run_models(
    dbt: dbtRunner,
    selector: str,
    target: str = "dev",
) -> RunExecutionResult:
    """Run dbt models and return structured results."""
    result: dbtRunnerResult = dbt.invoke([
        "run",
        "--select", selector,
        "--target", target,
    ])

    if result.exception:
        raise result.exception

    # result.result is RunExecutionResult for 'run' command
    execution_result: RunExecutionResult = result.result  # type: ignore[assignment]
    return execution_result


def get_failed_models(execution_result: RunExecutionResult) -> list[str]:
    """Extract failed model names from run results."""
    return [
        r.node.name  # type: ignore[union-attr]
        for r in execution_result.results
        if r.status.value == "error"
    ]
```

### 6. Parse Artifacts with `dbt-artifacts-parser`

**Don't parse `manifest.json` manually.** Use the typed parser library.

```python
# ✅ CORRECT - Using dbt-artifacts-parser
import json
from pathlib import Path
from dbt_artifacts_parser.parser import parse_manifest, parse_run_results

def load_manifest(target_path: Path = Path("target")):
    """Load and parse manifest.json."""
    manifest_path = target_path / "manifest.json"
    with manifest_path.open() as f:
        manifest_dict = json.load(f)
    return parse_manifest(manifest=manifest_dict)

def load_run_results(target_path: Path = Path("target")):
    """Load and parse run_results.json."""
    results_path = target_path / "run_results.json"
    with results_path.open() as f:
        results_dict = json.load(f)
    return parse_run_results(run_results=results_dict)

# Usage
manifest = load_manifest()
for node_id, node in manifest.nodes.items():
    if node.resource_type == "model":
        print(f"Model: {node.name}, Schema: {node.schema_}")

# ❌ WRONG - Manual JSON parsing
with open("target/manifest.json") as f:
    data = json.load(f)
    for node in data["nodes"].values():  # No type safety!
        print(node["name"])
```

### 7. Handle dbt Project Paths Explicitly

**Never rely on the current working directory.** Always specify paths.

```python
# ✅ CORRECT - Explicit paths
from pathlib import Path

DBT_PROJECT_DIR = Path(__file__).parent.parent / "dbt_project"
PROFILES_DIR = Path.home() / ".dbt"  # Or project-local

def run_dbt(args: list[str]) -> dbtRunnerResult:
    dbt = dbtRunner()
    full_args = [
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(PROFILES_DIR),
        *args,
    ]
    return dbt.invoke(full_args)

# ❌ WRONG - Relying on cwd
import os
os.chdir("/path/to/dbt_project")  # Fragile!
dbt.invoke(["run"])
```

### 8. Use Environment Variables for Credentials

**Never hardcode credentials.** Use environment variables or profiles.yml with env_var().

```yaml
# profiles.yml - ✅ CORRECT
my_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      # ...
```

```python
# Python - ✅ CORRECT
import os

# Set before invoking dbt
os.environ["SNOWFLAKE_ACCOUNT"] = get_secret("snowflake/account")
os.environ["SNOWFLAKE_USER"] = get_secret("snowflake/user")
os.environ["SNOWFLAKE_PASSWORD"] = get_secret("snowflake/password")

result = dbt.invoke(["run"])
```

### 9. Structure Your dbt + Python Project Properly

**Keep dbt concerns separate from Python concerns.**

```
# ✅ CORRECT - Clean separation
my_data_project/
├── pyproject.toml              # Python project config
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── dbt_runner.py       # dbt invocation utilities
│       ├── artifact_parser.py  # Artifact parsing utilities
│       └── pipelines/          # Orchestration code
│           └── daily.py
├── dbt/                        # dbt project (can be separate repo)
│   ├── dbt_project.yml
│   ├── profiles.yml            # Or use ~/.dbt/profiles.yml
│   ├── packages.yml
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── tests/
│   ├── macros/
│   └── seeds/
└── tests/
    └── test_dbt_runner.py
```

### 10. Log dbt Output Properly

**Capture dbt's structured events, not just stdout.** Use callbacks for proper logging with structlog.

```python
# ✅ CORRECT - Structured logging with callbacks
import structlog
from dbt.cli.main import dbtRunner
from dbt.events.types import LogStartLine, LogModelResult

log = structlog.get_logger()

def log_dbt_event(event) -> None:
    """Callback to handle dbt events."""
    # Filter to important events
    if hasattr(event, "info"):
        if event.info.level == "error":
            log.error("dbt error", msg=event.info.msg)
        elif event.info.level == "warn":
            log.warning("dbt warning", msg=event.info.msg)
        # Skip debug/info to avoid noise

dbt = dbtRunner(callbacks=[log_dbt_event])
result = dbt.invoke(["run"])

# ❌ WRONG - Just printing
result = dbt.invoke(["run"])  # Output goes to stdout, not your logs
```

### 11. Don't Mix dbt Python Models with Python Orchestration

**dbt Python models run IN the warehouse.** Your orchestration Python runs locally. Don't confuse them.

```python
# dbt Python model (runs in Snowflake/Databricks/BigQuery)
# models/my_python_model.py
def model(dbt, session):
    """This runs REMOTELY in your data warehouse."""
    df = dbt.ref("upstream_model")
    # Transform with pandas/snowpark/pyspark
    return df.with_columns(...)  # Returns to warehouse

# Orchestration Python (runs locally)
# scripts/run_pipeline.py
def run_pipeline():
    """This runs LOCALLY on your machine/server."""
    dbt = dbtRunner()
    dbt.invoke(["run", "--select", "my_python_model"])  # Triggers remote execution
```

### 12. Handle dbt Failures in Pipelines Gracefully

**Don't just fail on any dbt error.** Distinguish between model failures and test failures.

```python
# ✅ CORRECT - Granular failure handling
from dbt.cli.main import dbtRunner, dbtRunnerResult

def run_dbt_pipeline(selector: str) -> dict[str, bool]:
    """Run dbt with granular status tracking."""
    dbt = dbtRunner()
    status = {"run": False, "test": False}

    # Run models
    run_result = dbt.invoke(["run", "--select", selector])
    if run_result.exception:
        raise RuntimeError(f"dbt run crashed: {run_result.exception}")
    status["run"] = run_result.success

    # Run tests even if some models failed (might want to test others)
    test_result = dbt.invoke(["test", "--select", selector])
    if test_result.exception:
        raise RuntimeError(f"dbt test crashed: {test_result.exception}")
    status["test"] = test_result.success

    return status

# Usage
status = run_dbt_pipeline("tag:daily")
if not status["run"]:
    alert_on_call("Model failures detected")
if not status["test"]:
    alert_data_quality_team("Test failures detected")
```

## Red Flags

These thoughts mean STOP—you're creating maintenance nightmares:

| Thought | Reality |
|---------|---------|
| "I'll just shell out with subprocess" | Use `dbtRunner`. You need structured results. |
| "I'll parse manifest.json with raw json.load" | Use `dbt-artifacts-parser`. It handles version differences. |
| "dbt and my ML code can share a venv" | No they can't. dbt's deps will conflict. Isolate. |
| "I'll cd into the dbt project directory" | Pass `--project-dir` explicitly. CWD is fragile. |
| "I'll run all my Python in dbt Python models" | dbt Python models are for warehouse transforms. Use them sparingly. |
| "result.success is all I need to check" | Check `result.exception` too. Crashes are different from failures. |
| "I'll store credentials in profiles.yml" | Use `env_var()` in profiles.yml. Never commit secrets. |

## Quick Reference

### dbtRunner Commands

```python
from dbt.cli.main import dbtRunner, dbtRunnerResult

dbt = dbtRunner()

# Common commands
dbt.invoke(["run"])                              # Run all models
dbt.invoke(["run", "--select", "model_name"])    # Run specific model
dbt.invoke(["run", "--select", "tag:daily"])     # Run by tag
dbt.invoke(["run", "--select", "+model_name"])   # Run model + ancestors
dbt.invoke(["run", "--select", "model_name+"])   # Run model + descendants
dbt.invoke(["test"])                             # Run all tests
dbt.invoke(["test", "--select", "model_name"])   # Test specific model
dbt.invoke(["build"])                            # Run + test in DAG order
dbt.invoke(["compile"])                          # Compile SQL without running
dbt.invoke(["parse"])                            # Parse project, return manifest
dbt.invoke(["docs", "generate"])                 # Generate docs
dbt.invoke(["source", "freshness"])              # Check source freshness
dbt.invoke(["seed"])                             # Load seed files
dbt.invoke(["snapshot"])                         # Run snapshots
```

### Result Types by Command

| Command | `result.result` Type |
|---------|---------------------|
| `run` | `RunExecutionResult` |
| `test` | `RunExecutionResult` |
| `build` | `RunExecutionResult` |
| `parse` | `Manifest` |
| `compile` | `RunExecutionResult` |
| `source freshness` | `FreshnessResult` |
| `docs generate` | `CatalogArtifact` |

### Artifact Files

| File | Generated By | Contains |
|------|-------------|----------|
| `manifest.json` | Most commands | Full project structure, DAG, configs |
| `run_results.json` | run, test, build | Execution results, timing, status |
| `catalog.json` | docs generate | Column types, stats, descriptions |
| `sources.json` | source freshness | Source freshness results |

### Python Dependencies

```toml
# pyproject.toml - For orchestration code
[project]
dependencies = [
    "dbt-core>=1.5",
    "dbt-snowflake>=1.5",  # Or your adapter
    "dbt-artifacts-parser>=0.8",
]

# Or requirements.txt
dbt-core>=1.5
dbt-snowflake>=1.5
dbt-artifacts-parser>=0.8
```

## See Also

- `python-best-practices` - General Python typing rules (apply these too!)
- [dbt Programmatic Invocations](https://docs.getdbt.com/reference/programmatic-invocations)
- [dbt Artifacts](https://docs.getdbt.com/reference/artifacts/dbt-artifacts)
- [dbt Project Structure](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
