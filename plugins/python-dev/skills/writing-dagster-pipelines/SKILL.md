---
name: writing-dagster-pipelines
description: This skill should be used when writing, reviewing, debugging, or deploying Dagster pipeline code for the PRH UK centralised Dagster platform - assets, code locations, asset checks, dbt integration, scheduling, per-asset Kubernetes resources, or promoting to prod. Triggers on "dagster", "asset", "code location", "definitions.py", "MaterializeResult", "AutomationCondition", "dbt_assets", "resources.yaml", "ShucksSnowflakeResource", "make local", "materialise", "step pod".
---

# Writing Dagster pipelines (PRH UK centralised platform)

## Overview

We run one shared Dagster instance per environment on Kubernetes. Each project is a **code location**: its own repo, Docker image, namespace, and gRPC server, all plugged into a central control plane (UI, daemon, PostgreSQL). You write thin Dagster assets that call your own Python library; the platform handles scheduling, per-asset pods, S3 hand-off between steps, alerting, and dashboards.

Source of truth is the Blue Book on Confluence - this skill distils it, but when detail is missing or looks stale, fetch the page:

- [Centralised Dagster Platform](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4804739139) (index)
- [Writing Dagster Pipelines](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4820631553) (tutorial, pages 00-05)
- [Deploying a Code Location](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4805132388)

Working examples: `uk-bookseller-automation` (best template for new projects), `uk-vearsa-inputs`, `scythia`, `dynamic-keywords-engine`. Platform repo: `uk-dagster` on GitLab (owned by Liam Eloie). UIs: [dagster-dev.gdh.aws.prh.com](https://dagster-dev.gdh.aws.prh.com) / [dagster.gdh.aws.prh.com](https://dagster.gdh.aws.prh.com). Grafana: dagster-metrics[-dev].gdh.aws.prh.com.

## The one principle

**Your logic lives in a standalone library that never imports Dagster.** Assets are adapters: they receive config and resources, call library functions, and report what happened. The library takes DataFrames, config objects, and raw connections; it works from a notebook, a script, or pytest with no Dagster harness. If you ever swap orchestrators, only the thin adapter layer moves.

## Project layout

Two packages side by side in one repo:

```
regina/                        # repo root
├── pyproject.toml             # core library: name = "regina", no dagster deps
├── regina/                    # the library: training.py, validation.py, io.py ...
├── tests/                     # library tests, plain pytest
├── dagster/                   # the code location
│   ├── pyproject.toml         # name = "regina-dagster"
│   ├── definitions.py         # the single entry point
│   ├── assets/
│   │   ├── config.py          # the Config bridge class
│   │   ├── checks.py          # check names + thresholds (one module, imported by both sides)
│   │   ├── training.py        # assets grouped by pipeline stage, checks alongside
│   │   └── dbt_models.py      # dbt integration
│   ├── resources.yaml         # per-asset Kubernetes resources
│   └── resource_config.py     # loads resources.yaml
├── charts/                    # Helm (see references/deployment.md)
└── Dockerfile
```

The dagster package depends on the library locally:

```toml
# dagster/pyproject.toml
dependencies = [
    "dagster>=1.9.0", "dagster-aws>=0.25.0", "dagster-dbt>=0.25.0",
    "dagster-k8s>=0.25.0", "dagster-postgres>=0.25.0",
    "dagster-resource-config @ git+ssh://git@git.us.randomhouse.com/prh-uk/uk-dagster.git@main#subdirectory=packages/dagster-resource-config",
    "dagster-shared-resources @ git+ssh://...",   # copy exact URL from an existing repo
    "regina",
]
[tool.uv.sources]
regina = { path = "../" }
```

## Quick reference

| Decision | Rule |
| --- | --- |
| Config or resource? | Would someone change it for a backfill? Config. Same for every run in an environment? Resource. |
| Asset names | `{project}_{function}`, e.g. `regina_training_ebook` - the instance is shared, prefixes prevent collisions |
| Group names | `{project}_{stage}`, e.g. `regina_training` |
| Snowflake | `ShucksSnowflakeResource` from `dagster-shared-resources`. Never write your own connection resource. |
| Check severity | ERROR = data is broken, block downstream. WARN = quality dipped, continue but alert. |
| Checks placement | Inline via `MaterializeResult(check_results=...)` - the data is already in memory. Names and thresholds as constants in one `checks.py`. |
| Scheduling | `AutomationCondition.on_cron(...)` on the root asset, `AutomationCondition.eager()` downstream. No custom sensors or schedules for a daily fan-out. |
| Asset granularity | One asset = one observable output someone cares about. Don't split load/compute/upload for one output into separate assets. |
| K8s resources | `resources.yaml` + `dagster-resource-config`, applied via `op_tags`. Never hand-write `dagster-k8s/config` dicts. |
| Requests/limits | Set requests (memory = observed peak x 1.2-1.3, CPU = average x 1.3). Do NOT set memory or CPU limits - current platform guidance for batch pods; older doc examples still show limits. |
| Metadata keys | Use `/` to group: `pred/mean`, `feature_importance/rank_7d`, `config/max_depth` |
| Environments | `DAGSTER_ENV` unset = local, `development` / `production` on cluster (exact strings). Never set it in local `.env`. |
| External writes | Gate on environment: only send emails / write prod tables when `DAGSTER_ENV == "production"`, log a dry run otherwise |

## Config: the bridge pattern

Dagster's launchpad renders a form from flat primitives. Your library wants rich types (dates, enums, nested Pydantic models). Don't let either side leak into the other - write a thin Dagster `Config` class with a conversion method:

```python
from dagster import Config
from regina.config.base import Environment, ReginaConfig

class ReginaPipelineConfig(Config):
    """Per-run parameters editable from the Dagster launchpad."""

    env: str = Environment.DEV.value
    execution_date: str = ""          # empty = yesterday, resolved in the bridge
    training_start_date: str = "2024-01-01"
    window_days: int = 7

    def to_regina_config(self) -> ReginaConfig:
        execution = (
            date.fromisoformat(self.execution_date)
            if self.execution_date
            else date.today() - timedelta(days=1)
        )
        return ReginaConfig(env=Environment(self.env), execution_date=execution, ...)
```

Every asset calls `config.to_regina_config()` as its first line. Defaults must make a standard prod run need zero launchpad edits. One config class is shared by the whole pipeline (dbt assets included) - one source of truth for `env`, dates, and windows.

## Asset anatomy

The canonical shape - decorator declares wiring, body is bridge, connection block, library calls, then metadata and checks:

```python
@asset(
    deps=[regina_dbt_assets],
    group_name="regina_training",
    check_specs=[
        AssetCheckSpec(name=n, asset="regina_training_ebook")
        for n in TRAINING_CHECK_NAMES
    ],
    automation_condition=AutomationCondition.eager(),
    op_tags=RESOURCE_CONFIG.get_asset_tags("regina_training_ebook"),
)
def regina_training_ebook(
    context: OpExecutionContext,
    snowflake: ShucksSnowflakeResource,
    config: ReginaPipelineConfig,
) -> MaterializeResult:
    """Train ebook XGBoost model and upload competitor predictions."""
    regina_cfg = config.to_regina_config()

    with snowflake.get_connection() as conn:
        prh_df, comp_df = load_format_data(regina_cfg, BookFormat.EBOOK, conn)
        model, predictions = train_and_predict(regina_cfg, prh_df, comp_df, BookFormat.EBOOK)
        upload_predictions(regina_cfg, predictions, BookFormat.EBOOK, conn)

    metadata = _build_training_metadata(regina_cfg, prh_df, predictions, model)
    check_results = build_training_checks(
        training_rows=len(prh_df),
        predictions_max=float(predictions["pred"].max()),
        ...
    )
    return MaterializeResult(metadata=metadata, check_results=check_results)
```

Two levels of injection: Dagster injects the *resource* into the asset; the asset passes the raw *connection* into library functions. The library never sees a Dagster type.

## Checks and metadata

One `checks.py` module holds thresholds and names as constants; both the `@asset` decorator (`check_specs`) and the builder functions import them so they can't drift:

```python
MAX_PREDICTION_VALUE = 100_000
TRAINING_CHECK_NAMES = ["training_data_not_empty", "no_missing_features", "predictions_reasonable"]

def build_training_checks(training_rows: int, predictions_max: float, ...) -> list[AssetCheckResult]:
    return [
        AssetCheckResult(
            check_name="training_data_not_empty",
            passed=training_rows > 0,
            severity=AssetCheckSeverity.ERROR,
            metadata={"training_rows": training_rows},
        ),
        ...
    ]
```

- Training-style checks ("is the data present and sane?") get ERROR: a failure blocks downstream assets and emails the team.
- Validation-style checks ("is the model still good?") get WARN: the pipeline continues, an alert still goes out.
- Always attach the actual value as check metadata so a failure shows `predictions_max: 247000`, not just "failed".

Metadata is the numbers worth plotting across runs: row counts, distribution stats, accuracy, hyperparameters. Dagster stores every value as a time series. Both mechanisms feed the platform's centralised alerting automatically - never build your own notification logic.

## dbt models as assets

```python
_DBT_PROJECT_DIR = Path(os.environ.get("DBT_PROJECT_DIR", Path(__file__).resolve().parents[2]))
dbt_project = DbtProject(project_dir=_DBT_PROJECT_DIR)
dbt_project.prepare_if_dev()

class ReginaDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        return super().get_asset_key(dbt_resource_props).with_prefix("regina")

    def get_group_name(self, dbt_resource_props):
        fqn = dbt_resource_props.get("fqn", [])
        return f"regina_{fqn[1]}" if len(fqn) > 1 else "regina"

@dbt_assets(
    manifest=dbt_project.manifest_path,
    dagster_dbt_translator=ReginaDbtTranslator(),
    automation_condition=AutomationCondition.on_cron("0 18 * * *"),
)
def regina_dbt_assets(context, dbt: DbtCliResource, config: ReginaPipelineConfig):
    dbt_vars = {"window_days": config.window_days, ...}
    yield from dbt.cli(
        ["build", "--target", config.env, "--vars", json.dumps(dbt_vars)],
        context=context,
    ).stream()
```

The prefix translator is not optional on a shared instance - two projects with a `stg_sales` model would otherwise collide. Shared config fields cross into dbt as `--vars`.

## Automation

The standard daily fan-out needs zero sensor or schedule code:

```
18:00 UTC - dbt builds feature tables        AutomationCondition.on_cron("0 18 * * *")
         ↓
         - all downstream assets launch      AutomationCondition.eager() on each
           in parallel when dbt finishes
```

If a step fails, eager conditions downstream don't fire and the alerting system emails your contact group. Exception: pipelines that trigger a Databricks bundle must NOT use per-asset `eager()` (each stage would trigger its own Databricks run) - use `define_asset_job` selections with a sensor/schedule instead; see references/ml-pipelines.md.

## definitions.py and environments

One file registers everything. The current pattern asks the platform for its plumbing instead of choosing it:

```python
from dagster_shared_resources import Deployment, ShucksSnowflakeResource, build_definitions

defs = build_definitions(
    deployment=Deployment.from_env(),   # reads DAGSTER_ENV
    assets=[regina_dbt_assets, regina_training_ebook, ...],
    resources={
        "snowflake": ShucksSnowflakeResource(section_name="edp"),
        "dbt": DbtCliResource(project_dir=dbt_project),
    },
    jobs=[],
    schedules=[],
    s3_prefix="regina",
)
```

`build_definitions` picks the IO manager, executor, and metadata store from `DAGSTER_ENV`: unset = local (`fs_io_manager`, in-process, SQLite), `development`/`production` = cluster (`S3PickleIOManager` on the shared bucket, `k8s_job_executor`, PostgreSQL). The same code runs everywhere; never hand-swap plumbing for local runs. Older repos and older doc pages wire `Definitions(...)` with `S3PickleIOManager`/`k8s_job_executor` explicitly - if you see that, it predates `build_definitions`; prefer the factory in new code and copy the exact import from a current repo.

Resource dict keys must match asset parameter names (`snowflake:` key ↔ `snowflake:` parameter). An asset missing from the list simply doesn't exist in the UI - this file is the first place to look when something doesn't show up.

## Kubernetes resources per asset

Each asset runs in its own pod (`k8s_job_executor`). Defaults are 250m CPU / 512Mi memory - fine for SQL glue, not for training. Declare overrides in `resources.yaml`, keyed by asset function name:

```yaml
assets:
  regina_training_ebook:
    resources:
      requests:
        memory: "2Gi"
        cpu: "1000m"
```

```python
# resource_config.py
RESOURCE_CONFIG = load_resource_config(Path(__file__).parent / "resources.yaml")
# then on each asset: op_tags=RESOURCE_CONFIG.get_asset_tags("regina_training_ebook")
```

- Only list assets that need more than the defaults.
- Right-size from the Grafana code-location dashboard: memory request = observed max x 1.2-1.3, CPU request = average x 1.3, and **no memory or CPU limits** (a limit turns a transient spike into an OOMKill; the old 1000m CPU limit default silently broke pods requesting >1 core).
- `max_runtime: <seconds>` in the same YAML entry + `tags=RESOURCE_CONFIG.get_job_tags(...)` on a job kills hung runs (platform default 24h). A separate `active_deadline_seconds` (default 25h) is the Kubernetes safety net; override it only for legitimately longer runs.
- GPU work: add `nvidia.com/gpu` to requests/limits plus `node_selector` and `tolerations` in the same entry (see reviews-radar).

## Local development

```bash
make local          # first run creates .env and stops; set SNOWFLAKE_CONFIG_PATH, run again
```

Full Dagster UI at 127.0.0.1:3000, own SQLite metadata, nothing touches shared dev. Dagster plumbing is swapped to local equivalents; **data sources are real** - Snowflake reads run against the warehouse as you, and an asset that writes, writes for real. Gate side effects:

```python
if os.getenv("DAGSTER_ENV", "development") == "production":
    email_service.send_excel_report(...)
else:
    context.log.info("DRY RUN: skipping email send")
```

Troubleshooting: S3/Kubernetes errors on startup = `DAGSTER_ENV` is set in `.env` (remove it); `'dev' is not a recognised deployment` = only `development`/`production` are valid; Snowflake JWT errors = expired key or off VPN; `FileNotFoundError` for shucks config = `SNOWFLAKE_CONFIG_PATH` wrong.

## Alerting

Every failure (run or check) anywhere on the platform emails a contact group. New code locations are covered by a wildcard from day one. For team-specific routing, add contacts + a location entry to `alerting-system/config/alerts-dev.yaml` and `alerts-prod.yaml` in uk-dagster. Location keys use **underscores** (`uk_vearsa_inputs`), matching Dagster's normalised location names, not repo hyphens.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Writing a bespoke Snowflake resource wrapping shucks | `ShucksSnowflakeResource` from `dagster-shared-resources` - auth changes then roll out platform-wide |
| Hand-writing `dagster-k8s/config` op_tag dicts | `resources.yaml` + `RESOURCE_CONFIG.get_asset_tags(...)` |
| Setting memory limit = request "to be safe" | No memory/CPU limits on batch pods; requests only |
| Custom `asset_sensor` / cron-offset schedule for "run after dbt" | `on_cron` on dbt + `eager()` downstream |
| Splitting one output into load/compute/upload assets | One asset per observable output; intermediates in Snowflake, not the IO manager |
| Putting deploy-time constants in Config, or run-time knobs in a resource | Backfill test: changed per run = config, per environment = resource |
| Registering the code location via `dagster-user-deployments` Helm values | Platform uses a Terraform code-location map in uk-dagster + a shared OCI Helm chart consumed from your own repo - references/deployment.md |
| Library functions accepting strings "because the launchpad needs it" | Keep rich types in the library; convert in the Config bridge |
| Check names inline in decorator and builder separately | One constants list in `checks.py`, imported by both |
| Setting `DAGSTER_ENV` in local `.env` | Unset means local; the Helm chart sets it on the cluster |

## Going deeper

- **references/deployment.md** - shipping a code location: Dockerfile, Terraform registration, secrets, Helm chart files, CI, verification, prod promotion, RBAC and alerting registration.
- **references/platform.md** - how execution actually works: control plane, run/step pods, container context, S3 IO + IRSA, timeouts, retries, dashboards. Read when debugging "why didn't my run start" or right-sizing.
- **references/ml-pipelines.md** - ML on the platform: Databricks Asset Bundles, Dagster Pipes, landing assets, champion/challenger promotion, drift gates.
