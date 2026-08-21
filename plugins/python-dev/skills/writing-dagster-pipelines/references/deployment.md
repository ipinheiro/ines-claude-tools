# Deploying a code location

End-to-end path from working pipeline code to running on the platform. Source: [Deploying a Code Location](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4805132388), [Terraform Configuration](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4805132340), [The Shared Helm Chart](https://prh-uk.atlassian.net/wiki/spaces/BB/pages/4805427242). Reference repos: `uk-bookseller-automation` (clean template), `uk-vearsa-inputs` (multiple secrets, FTP volumes).

## Overview of the steps

1. Dockerfile builds the image and runs the gRPC server
2. Platform team registers the code location in the uk-dagster Terraform map (merge to `develop`)
3. Create project secrets in the namespace with kubectl
4. Add the four-file Helm chart consuming the shared `dagster-code-location` chart
5. CI builds, pushes, and helm-upgrades on push to `develop`
6. Verify LOADED in the dev UI, materialise an asset, check the pod ran in your namespace
7. Promote to prod

## 1. Dockerfile

Multi-stage: build a wheel with uv, install it in a slim runtime image, run the gRPC server as non-root user `dagster` (uid 1000). SSH + `ssh-keyscan git.us.randomhouse.com` are needed because dependencies include private git repos (shucks, dagster-shared-resources).

```dockerfile
CMD ["dagster", "api", "grpc", "-h", "0.0.0.0", "-p", "4000", "-m", "my_project.definitions"]
```

Port 4000 is the standard gRPC port. The `-m` module path must match `dagsterModule` in the Helm values AND `dagster_module` in the Terraform map - three places, one value. Copy the full Dockerfile from the Confluence page or uk-bookseller-automation.

Required deps for the platform to work: `dagster`, `dagster-aws` (S3 IO), `dagster-k8s` (step pods), `dagster-postgres` (metadata reporting).

## 2. Terraform registration (uk-dagster repo)

Someone with access adds an entry to `terraform/dev/code-locations/terragrunt.hcl`:

```hcl
my-project = {
  namespace            = "my-project"          # becomes my-project-dev / my-project-prod
  dagster_module       = "my_project.definitions"
  enable_step_executor = true                  # required for k8s_job_executor (which you use)
}
```

Optional fields: `service_name` (if the gRPC service name differs from the map key), `create_namespace = false` (namespace already exists, e.g. Rancher-created), `create_pg_secret = false` (another location in the same namespace already has it - see scythia/dke), `use_orchestrator_namespace = true` (control-plane residents like alerting-system only).

Merging to `develop` auto-applies and creates: namespace, IRSA-annotated service account, Role + RoleBindings (control plane access + step executor), PostgreSQL secret copy, S3 trust policy update, and a control-plane redeploy with your gRPC address in the workspace. The location then shows as **NOT LOADED** in the UI until you deploy the server - expected.

## 3. Secrets

Not Terraform-managed (sensitive values). Create per namespace:

```bash
kubectl create secret generic shucks-config \
  --from-file=config.toml=/path/to/config.toml -n my-project-dev
kubectl create secret generic shucks-private-key \
  --from-file=private_key.pem=/path/to/key.pem -n my-project-dev
```

Names must match the `volumes:` entries in your Helm values. Repeat in the prod namespace at promotion time.

## 4. Helm chart - four files, no templates directory

The shared chart `dagster-code-location` templates the Deployment, Service, and the three ConfigMaps. Your repo only supplies values.

`charts/Chart.yaml`:

```yaml
apiVersion: v2
name: my-project
version: 1.0.0
dependencies:
  - name: dagster-code-location
    version: "1.3.0"      # pinned; upgrading is a per-repo decision
    repository: "oci://651818016290.dkr.ecr.us-east-1.amazonaws.com/uk-dagster-charts"
```

`charts/values.yaml` (everything nests under the `dagster-code-location:` key):

```yaml
dagster-code-location:
  nameOverride: "my-project"
  fullnameOverride: "my-project"
  dagsterModule: "my_project.definitions"
  image:
    repository: 651818016290.dkr.ecr.us-east-1.amazonaws.com/my-project
    tag: "latest"
  serviceAccount:
    name: "my-project"          # must match what Terraform created
  orchestrator:
    serviceAccountName: "uk-dagster"
  extraEnv:
    - name: SNOWFLAKE_CONFIG_PATH
      value: /var/run/secrets/shucks/config/SHUCKS_CONFIG
  volumes:
    - name: shucks-config
      secret:
        secretName: shucks-config
  volumeMounts:
    - name: shucks-config
      mountPath: /var/run/secrets/shucks/config
      readOnly: true
```

`charts/values-dev.yaml` / `charts/values-prod.yaml`:

```yaml
dagster-code-location:
  dagsterEnv: "development"            # "production" in prod file - exact strings
  deploymentNamespace: "my-project-dev"
  orchestrator:
    namespace: "uk-dagster-dev"
  image:
    tag: "dagster-dev"                 # "dagster-prod" + pullPolicy: IfNotPresent in prod
```

`.gitignore` additions (created by `helm dependency build`): `charts/charts/` and `charts/Chart.lock`.

Key facts: `dagsterEnv` is injected as `DAGSTER_ENV` into all pods and derives `DAGSTER_S3_IO_BUCKET` automatically (`uk-dagster-io-storage-dev`/`-prod`) - never hardcode bucket names. `extraEnv`, `volumes`, and `volumeMounts` apply to both the gRPC server and the run/step pods (propagated via the container context).

## 5. CI

Deploy job `before_script` additions:

```yaml
- aws ecr get-login-password --region ${AWS_REGION} |
  helm registry login --username AWS --password-stdin ${ECR_REGISTRY_HOSTNAME}
- helm dependency build charts/
```

Deploy command:

```yaml
- helm upgrade --install my-project charts/ -f charts/values-dev.yaml --namespace my-project-dev
```

Copy the working `.gitlab-ci.yml` from uk-bookseller-automation. Check `git remote -v` before any glab operation - projects use different GitLab instances.

## 6. Verify

Push to `develop` → CI builds image, pulls shared chart, helm upgrades. Within a minute the location shows **LOADED** at dagster-dev.gdh.aws.prh.com. Then: materialise one asset, watch the run create a job pod, `kubectl get pods -n my-project-dev`, confirm success in the UI.

## 7. Promote to prod

1. Add the same entry to `terraform/prod/code-locations/terragrunt.hcl`, merge to `main`
2. Manually trigger `apply:code-locations:prod`, then `apply:control-plane:prod` (in that order - namespace and RBAC must exist before the control plane registers the location)
3. Create secrets in `my-project-prod`
4. Add a prod deploy job (branch `main`, `values-prod.yaml`)
5. Merge to `main`, trigger deploy

Dev auto-applies on merge to `develop`; every prod apply is a manual click on `main`.

## After deployment: alerting and RBAC

**Alerting** (uk-dagster repo, `alerting-system/config/alerts-dev.yaml` + `alerts-prod.yaml`): you're covered by the wildcard rule immediately; add a contact group and location entry for team-specific routing plus a `custom_message`. Location keys use underscores (`my_project`), not hyphens.

**RBAC** (`charts/control-plane/rbac-dev.yaml` + `rbac-prod.yaml`): the custom `dagster-rbac-webserver` default-denies anyone not in the policy. Add users with `locations: {my_project: write}` (underscores again). Users must also be in the Okta AD group first - ServiceNow request to IAM, contact Simon Percivall. `write` = trigger runs, toggle schedules; `read` = view only; `"*"` = admin.
