# How the platform executes your code

Read this when debugging runs, sizing resources, or reasoning about credentials and timeouts. Source: [Architecture](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4804608116), [How Jobs Run](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4810047682), [Kubernetes Resources](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4805394454), [Monitoring Dashboards](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4868931748).

## Hub and spoke

The control plane (webserver + daemon + PostgreSQL, in `uk-dagster-dev`/`uk-dagster-prod`) runs no pipeline code. Each code location is a gRPC server on port 4000 in its own namespace; the control plane's workspace lists every address and asks each "what do you have?". Dev and prod are separate EKS clusters (`gdh-test` / `gdh-highscale-c5-18xlarge`), fully walled off: own PostgreSQL, S3 bucket, namespaces, credentials.

## What happens on Materialize

1. The daemon reads the code location's **container context** - a JSON blob the gRPC server advertises (namespace, service account, default resources, ConfigMaps, volumes; built by the shared Helm chart from your values into the `{name}-user-env` ConfigMap).
2. The daemon creates a **run pod** (a Kubernetes Job) in your namespace, with your image - the image is inferred from the gRPC server pod, so a new image deploy automatically applies to job pods too.
3. The run pod plans execution order from the dependency graph.
4. With `k8s_job_executor`, the run pod creates one **step pod per asset**, in dependency order. Your `resources.yaml` op_tags become the step pod's requests/limits.
5. Each step pod runs one asset, writes output to S3, reports status/logs/metadata to PostgreSQL.
6. The run pod writes final status and exits.

Everything after step 2 happens in your namespace with your service account and secrets. Failed step = failed run immediately, no automatic retry; opt in per asset with `retry_policy=RetryPolicy(max_retries=2, delay=30)` for flaky external calls.

## Data between pods: S3 + IRSA

Step pods can't share memory, so the IO manager pickles asset outputs to the shared bucket (`uk-dagster-io-storage-dev`/`-prod`), one prefix per code location (`s3_prefix` - a convention, not IAM isolation). `DAGSTER_S3_IO_BUCKET` is injected by the Helm chart. AWS credentials come from IRSA: the service account is annotated with a shared per-environment IAM role, tokens are short-lived and auto-refreshed, no static keys anywhere. Note: assets exchanging large DataFrames through the IO manager is a smell - keep intermediates in Snowflake and pass nothing (use `deps=[...]`, return `MaterializeResult`).

## Timeouts

| Timeout | Default | Enforced by | Behaviour |
| --- | --- | --- | --- |
| `dagster/max_runtime` | 24h | Dagster daemon | Marks run failed, clean UI message. Set per job via `max_runtime` in resources.yaml + `get_job_tags` |
| `activeDeadlineSeconds` | 25h | Kubernetes | SIGTERM/SIGKILL the step pod. Safety net for orphaned pods when the run worker died without cleanup |
| Per-asset override | as set | resources.yaml `active_deadline_seconds` | For legitimately long runs (e.g. 172800 = 48h full-corpus jobs) |

The 25h default is deliberately 1h longer than max_runtime so the Dagster timeout fires first. `max_runtime` matters most for assets calling external APIs that can hang; pure computation is already protected by pod resource management.

## How pods report back

Run and step pods write to the control plane's PostgreSQL using the `uk-dagster-postgresql` secret (copied into your namespace by Terraform, mounted as `DAGSTER_PG_PASSWORD`) plus connection details from the `{name}-pipeline-env` ConfigMap (`DAGSTER_POSTGRES_HOST` etc.). All automatic - no application code. If pods can't report, check those two resources exist in the namespace.

## ConfigMaps per pod type

| Pod | Loads |
| --- | --- |
| gRPC server | `{name}-user-deployments-shared-env`, `{name}-user-env` (container context) |
| Run pod | `{name}-pipeline-env` |
| Step pod | `{name}-pipeline-env` + `extraEnv` from Helm values |

All three get the service account (IRSA), the PostgreSQL secret, and your Helm `volumes`/`volumeMounts`.

## Dashboards and right-sizing

Grafana at dagster-metrics[-dev].gdh.aws.prh.com (VPN, anonymous read-only). Two dashboards: **Dagster Platform** (health, failures, cost by code location) and **Dagster Code Location Detail** (per-asset memory/CPU percentiles vs configured request, OOMKills, durations).

Right-sizing method: open Code Location Detail → Resource Right-Sizing row, then set in `resources.yaml`:

- Memory request = observed max x 1.2-1.3 (sanity-check max against p95/p99 for one-off outliers)
- CPU request = observed average x 1.3 (CPU throttles, doesn't kill - size off average)
- No memory limit, no CPU limit (limits turn spikes into OOMKills; the old 1000m CPU limit default broke pods requesting >1 core and was removed from the shared chart)

Prometheus retention is ~120 days. No custom instrumentation needed - new pipelines get dashboard coverage for free.

## Alerting internals

The alerting system is itself a code location in the control plane namespace. Two sensors: `centralised_pipeline_failure_sensor` (`run_failure_sensor` with `monitor_all_code_locations=True`) and `asset_check_failure_sensor` (polls check evaluations every 60s, 24h dedup per check, cooldown clears on recovery). Routing config in `alerting-system/config/alerts-{dev,prod}.yaml`; wildcard `"*"` catches unregistered locations. Grafana has no alerting wired up on purpose - alerts come from Dagster, dashboards are for investigation.
