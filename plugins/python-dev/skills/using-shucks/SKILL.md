---
name: using-shucks
description: This skill should be used when a project requires a Snowflake connection, when writing code that queries Snowflake, when setting up database credentials, or when loading data to/from Snowflake. Triggers on "snowflake connection", "connect to snowflake", "snowflake credentials", "SnowflakeConfig", "shucks", "database credentials", "snowflake query".
---

# Using shucks for Snowflake Connections

**Use shucks for ALL Snowflake connections in Python projects.** shucks is our internal library for managing structured database credentials. It provides secure credential storage, multiple authentication methods, and a clean interface for connecting to Snowflake.

## Installation

```bash
# From GitLab
pip install git+ssh://git@git.us.randomhouse.com/prh-uk/shucks.git

# With uv
uv add "shucks @ git+ssh://git@git.us.randomhouse.com/prh-uk/shucks.git"

# With specific version tag
pip install git+ssh://git@git.us.randomhouse.com/prh-uk/shucks.git@v1.27.0
```

**pyproject.toml dependency:**
```toml
[project]
dependencies = [
    "shucks @ git+ssh://git@git.us.randomhouse.com/prh-uk/shucks.git",
]
```

## Quick Start

### 1. Generate Config File

```bash
uv run python -m shucks generate
# Creates ~/.credentials/config.toml
```

### 2. Edit Credentials

```toml
# ~/.credentials/config.toml
[snowflake]
account = "your-account"
region = "eu-west-1"
user = "your-username"
password = "your-password"
```

### 3. Connect

```python
from shucks import SnowflakeConfig

with SnowflakeConfig.load().connect() as conn:
    df = pd.read_sql("SELECT * FROM my_table", conn)
```

## The Rules

### 1. ALWAYS Use Context Managers

```python
# ✅ CORRECT - Context manager ensures connection closes
with SnowflakeConfig.load().connect() as conn:
    df = pd.read_sql("SELECT * FROM table", conn)

# ✅ CORRECT - SQLAlchemy engine pattern
with SnowflakeConfig.load().create_engine().connect() as conn:
    df = pd.read_sql("SELECT * FROM table", conn)

# ❌ FORBIDDEN - Connection may leak
conn = SnowflakeConfig.load().connect()
df = pd.read_sql("SELECT * FROM table", conn)
# forgot to close!
```

### 2. Use Named Sections for Multiple Environments

```toml
# ~/.credentials/config.toml
[snowflake]
account = "prod-account"
user = "prod-user"
password = "prod-pass"

[snowflake-dev]
account = "dev-account"
user = "dev-user"
password = "dev-pass"

[edp]
account = "edp-account"
user = "svc-user"
private_key = "/path/to/key.pem"
```

```python
# Load specific section
prod_cfg = SnowflakeConfig.load()  # defaults to [snowflake]
dev_cfg = SnowflakeConfig.load("snowflake-dev")
edp_cfg = SnowflakeConfig.load("edp")
```

### 3. Use Environment Variables in Production

```python
# Default prefix: SHUCKS_SNOWFLAKE_
# e.g., SHUCKS_SNOWFLAKE_ACCOUNT, SHUCKS_SNOWFLAKE_USER, etc.
cfg = SnowflakeConfig.load_from_env()

# Custom prefix for multiple configs
gdh_cfg = SnowflakeConfig.load_from_env(env_prefix="GDH_")
edp_cfg = SnowflakeConfig.load_from_env(env_prefix="EDP_")
```

### 4. Use Private Key Auth for Service Accounts

```toml
# Path to key file (default)
[snowflake]
account = "account"
user = "svc-user"
private_key = "/path/to/key.pem"

# Base64-encoded key (for secrets managers)
[snowflake]
account = "account"
user = "svc-user"
private_key = "MIIEvAIBADANBgkqhkiG9w0B..."
private_key_type = "base64"

# Literal PEM string
[snowflake]
account = "account"
user = "svc-user"
private_key = "-----BEGIN PRIVATE KEY-----\n..."
private_key_type = "string"

# With passphrase
[snowflake]
account = "account"
user = "svc-user"
private_key = "/path/to/encrypted-key.pem"
private_key_passphrase = "your-passphrase"
```

Generate key pair with:
```bash
uv run python -m shucks create-key-pair myusername --with-passphrase
```

### 5. Use Okta SSO When Required

```toml
[snowflake-okta]
account = "your-account"
region = "eu-west-1"
user = "you@company.com"
password = "your-okta-password"
authenticator = "https://company.okta.com/"
```

## Authentication Methods

shucks auto-detects authentication method based on config:

| Method | Config Fields |
|--------|---------------|
| Password | `password` only |
| Private Key | `private_key` only |
| Private Key + Passphrase | `private_key` + `private_key_passphrase` |
| Okta SSO | `password` + `authenticator` |
| External Browser | `authenticator = "externalbrowser"` |

## Common Patterns

### Basic Query with Pandas

```python
import pandas as pd
from shucks import SnowflakeConfig

with SnowflakeConfig.load().connect() as conn:
    df = pd.read_sql("""
        SELECT *
        FROM database.schema.table
        WHERE created_at > %(start_date)s
    """, conn, params={"start_date": "2024-01-01"})
```

### SQLAlchemy Engine

```python
from shucks import SnowflakeConfig

# Create engine (connection factory)
engine = SnowflakeConfig.load().create_engine()

# Use with context manager
with engine.connect() as conn:
    df = pd.read_sql("SELECT * FROM table", conn)

# Or with transaction
with engine.begin() as conn:
    conn.execute(text("INSERT INTO table VALUES (...)"))
```

### Override Connection Parameters

```python
# Override role/warehouse at connection time
with SnowflakeConfig.load().connect(
    role="ETL_ROLE",
    warehouse="LARGE_WH"
) as conn:
    df = pd.read_sql("SELECT * FROM big_table", conn)
```

### Databricks Integration

```python
from shucks import SnowflakeConfig

# Load from Databricks secret scope
cfg = SnowflakeConfig.load_from_databricks_secrets(
    dbutils,
    scope="my-secret-scope",
    # Expects keys: snowflake-user, snowflake-password, snowflake-account, etc.
)

# Custom key mapping
cfg = SnowflakeConfig.load_from_databricks_secrets(
    dbutils,
    scope="custom-scope",
    keymap={
        "sf-user": "user",
        "sf-pass": "password",
        "sf-account": "account",
    }
)
```

### AWS Secrets Manager

```python
from shucks import SnowflakeConfig

# Load from AWS SecretsManager (secret must contain TOML data)
cfg = SnowflakeConfig.load_from_aws_secret(
    secret_name="prod/snowflake/credentials",
    section_name="snowflake",
    region_name="eu-west-1",  # passed to boto3.Session
)
```

### Fallback to Environment Variables

```python
# Try config file first, fall back to env vars
cfg = SnowflakeConfig.load(env_fallback=True)
```

## Extra Utilities

### Chunked Uploads (Large DataFrames)

Snowflake limits expressions to 16,384 per statement. Use chunked operations for large data:

```python
from shucks import SnowflakeConfig
from shucks.extras import chunked_executemany_df

with SnowflakeConfig.load().connect() as conn:
    cur = conn.cursor()

    # Insert large DataFrame in chunks
    sql = "INSERT INTO table (col1, col2) VALUES (%s, %s)"
    chunked_executemany_df(
        cur, sql, df,
        chunk_size=10000,
        with_progress=True  # Shows tqdm progress bar
    )
```

### Temporary Stages (Bulk Loading)

For large data loads, use temporary stages with Parquet:

```python
from shucks import SnowflakeConfig
from shucks.extras import TmpStage

with SnowflakeConfig.load().connect() as conn:
    # Create stage and upload DataFrame
    stage = TmpStage.create("my_upload")
    stage.put(conn, df)

    # Copy into table (column names matched case-insensitively)
    rows_inserted = stage.copy_into(conn, "target_table")
```

### Pandas Utilities

```python
from shucks.extras.pandas import (
    snake_case_column_names,
    suggest_ddl,
)

# Normalize column names for Snowflake
df = snake_case_column_names(df, transform="alnum")

# Generate CREATE TABLE DDL from DataFrame
ddl = suggest_ddl(df, name="my_table", schema="my_schema")
print(ddl)
```

## CLI Commands

```bash
# Generate config file
uv run python -m shucks generate

# Test connectivity
uv run python -m shucks test snowflake --config-path ~/.credentials/config.toml

# Generate key pair for auth
uv run python -m shucks create-key-pair myuser --with-passphrase

# Verify SSL certificates (for corporate environments)
uv run python -m shucks verify-certs

# Dump query results to parquet
uv run python -m shucks dump "SELECT * FROM table" --section-name snowflake
```

## Config File Reference

```toml
[snowflake]
# Required
account = "account-name"         # Snowflake account identifier
user = "username"                # Username or UserPath object

# Authentication (one of these)
password = "secret"              # Password auth
private_key = "/path/to/key"     # Key pair auth (path)
private_key = "base64string"     # Key pair auth (base64)
private_key_type = "path"        # "path" (default), "base64", or "string"
private_key_passphrase = "pass"  # If key is encrypted
authenticator = "https://..."    # Okta SSO URL or "externalbrowser"

# Optional
region = "eu-west-1"             # Snowflake region
role = "MY_ROLE"                 # Default role
warehouse = "MY_WH"              # Default warehouse
database = "MY_DB"               # Default database
schema = "MY_SCHEMA"             # Default schema (note: 'schema' not 'db_schema')
```

## Typing Query Results

Snowflake results arrive as `list[dict[str, Any]]`. **Never let `Any` leak into business logic.** For the full pattern — overloaded `execute_query` with `model=`, `validation_alias`, anti-patterns, and test fixtures — see `../python-best-practices/references/snowflake-row-type-safety.md`.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll just hardcode credentials" | Use shucks config files. Hardcoded creds leak. |
| "I don't need a context manager" | Connections leak without `with`. Always use it. |
| "I'll use snowflake-connector directly" | shucks handles auth complexity. Use it. |
| "Environment variables are fine inline" | Use `load_from_env()` for consistent parsing and validation. |

## Troubleshooting

### SSL Certificate Errors

Corporate proxies (Netskope, ZScaler) can cause SSL errors:

```bash
python -m shucks verify-certs
```

### Config File Not Found

Default path: `~/.credentials/config.toml`

```python
# Check default path
print(SnowflakeConfig.default_config_path())

# Use custom path
cfg = SnowflakeConfig.load(config_path="/custom/path/config.toml")
```

### Section Not Found

```python
# Check default section name
print(SnowflakeConfig.default_section_name())  # "snowflake"

# Ensure section exists in TOML
cfg = SnowflakeConfig.load("my-section")  # Looks for [my-section]
```
