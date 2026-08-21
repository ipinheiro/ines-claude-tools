# ML pipelines on the platform

How ML projects extend the standard pipeline pattern with Databricks, MLflow, and Unity Catalog. Source: [How we run data and ML pipelines](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4922638522), [The ML Lifecycle](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4922572947). Reference implementation: the `uk-mlops` repo. This builds on the base skill - read SKILL.md first.

## The stack and the lanes

- Snowflake EDP = system of record; business marts built with dbt-on-Snowflake as everywhere else
- Databricks = ML runtime, governed by Unity Catalog (per-environment catalogs `prh_gdh_{dev,stage,prod}_euw1`)
- MLflow = tracking + UC model registry; Postgres (CloudNativePG) = serving layer
- Dagster = control plane only: decides when things run, holds the single lineage graph, computes nothing

Data crosses each system boundary in exactly one governed way. Frontends read Postgres, never the lakehouse. Never train directly off Snowflake (no version pinning at the read path, credential sprawl, warehouse cost).

## Landing asset and training mart

One explicit Dagster **landing asset** per model project copies the final Snowflake mart into a UC Delta table. Feature engineering that belongs to the model is dbt-on-Databricks downstream of the landed table (staging/intermediate/marts layers + tests). The final **training mart** is the reproducibility anchor - Delta table with deliberate retention:

```sql
{{ config(tblproperties={
    'delta.logRetentionDuration': 'interval 365 days',
    'delta.deletedFileRetentionDuration': 'interval 90 days',
}) }}
```

Training logs the Delta version it read; `SELECT * FROM mart VERSION AS OF n` reconstructs the exact training data for 90 days.

## Bundle defines what, Dagster decides when

The Databricks job is defined by a **Databricks Asset Bundle** (YAML in the repo: tasks, dependencies, compute, wheel, MLflow experiment and registered model as bundle resources). No `schedule:` block in the bundle, ever - Dagster owns all scheduling. Test of the split: running the job from the Databricks UI with Dagster off behaves identically.

Dagster triggers the deployed job with `jobs.run_now` as **one connected run**; subset selections use `run_now(only=[...])`. Results stream back via **Dagster Pipes**: task logs appear live in the Dagster step log, metrics land as materialisation metadata, every asset links to its Databricks and MLflow runs. Tasks guard for empty Pipes payloads (`optional_pipes_session` yields None) so manual Databricks runs don't crash. Numbers go to Dagster metadata; figures and profiles go to MLflow.

Pin `dagster-pipes` to the same version across orchestrator, job environment, and notebooks - drift breaks the protocol first.

## The five stages and three gates

`eda → train → validate → inference → evaluate`. Gates fail the pipeline on purpose:

1. **EDA** (gate): schema/dtype contract, row floor, null/duplicate/label checks, leakage screen (feature correlating >0.98 with label fails the run). Cheapest possible place to stop bad data.
2. **Train**: MLflow-tracked, registers to the UC registry as **challenger**. Never promotes itself. Logs `training_table` and `training_data_version` params.
3. **Validate** (gate): absolute floors (RMSE, R²) plus 5% regression tolerance vs the current champion. Pass = flip the **champion** alias (the alias IS the deployment; rollback is one `set_registered_model_alias` call). Fail = stop, old champion keeps serving. First run: floors alone decide.
4. **Inference**: batch-scores `models:/<name>@champion` into a governed UC predictions table (model name/version/timestamp on every row).
5. **Evaluate** (gate): prediction quality via `mlflow.models.evaluate` plus drift on the output distribution (KS statistic, Wasserstein distance, PSI - under 0.1 noise, over 0.2 significant). Reports all numbers to Dagster before raising.

After inference, a serving asset publishes predictions into Postgres as an idempotent full replace.

## Automation - the eager() trap

Do NOT put per-asset `AutomationCondition.eager()` on bundle-backed stages: it evaluates stage by stage, so each stage triggers its own Databricks run - five fragmented runs per update. Instead, job-level selections over the same deployed job:

```python
ml_training_job = define_asset_job(
    "ml_training_job", selection=AssetSelection.assets("eda", "train", "validate")
)
ml_scoring_job = define_asset_job(
    "ml_scoring_job", selection=AssetSelection.assets("inference", "evaluate", "published_predictions")
)

@asset_sensor(asset_key=TRAINING_MART, job=ml_training_job)
def training_on_mart_update(context, asset_event):
    return RunRequest(run_key=context.cursor)
```

Retraining follows the data (sensor on the training mart - safe because the gates own promotion); scoring follows the clock (daily schedule with the current champion). Automation arms itself only in production:

```python
_AUTOMATED = Deployment.from_env() == Deployment.PROD
_SCHEDULE_STATUS = DefaultScheduleStatus.RUNNING if _AUTOMATED else DefaultScheduleStatus.STOPPED
```

Dev and local stay ad-hoc: materialise what you're working on, toggle automation on only to test it.

## Identity

Bundle targets dev/staging/prod map to the three UC catalogs. `dev` deploys under your user with a `[dev <you>]` prefix (no collisions); prod runs as a service principal via `run_as`. Dagster's identity holds only run permissions on the job - the orchestrator can start the pipeline but cannot read the tables. OAuth M2M everywhere, no personal tokens in anything deployed.

## New model project checklist

1. Copy the reference structure from uk-mlops: bundle, dbt project, code location
2. Point the landing asset at your Snowflake mart
3. Write feature models in dbt; training mart gets the retention properties and tests
4. Replace model code in train/predict; set gate thresholds (EDA contract, validation floors, drift bounds)
5. Name your experiment and registered model in the bundle variables

Local: `make local` as usual; bundle changes deploy with `databricks bundle deploy -t dev`. The serving demo wants a local Postgres (`docker run ... postgres:16`).
