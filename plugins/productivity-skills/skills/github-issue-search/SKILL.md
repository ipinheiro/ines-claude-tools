---
name: GitHub Issue Search
description: This skill should be used when the user encounters an error, bug, or unexpected behavior and wants to "search GitHub issues", "check if others had this problem", "find similar issues", "look for solutions on GitHub", "search for error messages", or needs to investigate whether a problem is known, has workarounds, or has been fixed in a library/tool.
---

# GitHub Issue Search for Troubleshooting

This skill provides patterns for using the GitHub CLI (`gh`) to search issues when encountering errors or unexpected behavior. Search public repositories to find if others encountered the same problem and what solutions exist.

## Prerequisites

```bash
# Install gh CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu/Debian

# Authenticate (required for searching)
gh auth login
```

## Quick Search Patterns

### Search for Error Messages

When encountering an error, extract the key error text and search:

```bash
# Basic error search
gh search issues "ConnectionResetError" --repo aio-libs/aiohttp --limit 10

# Search with state filter
gh search issues "timeout error" --repo psf/requests --state open --limit 10

# Search closed issues (often contain solutions)
gh search issues "SSL certificate" --repo urllib3/urllib3 --state closed --limit 10
```

### Search Across Organization

Search all repos in an organization:

```bash
gh search issues "memory leak" --owner dagster-io --limit 20
gh search issues "grpc connection" --owner weaviate --limit 20
```

### Search with JSON Output

Get structured output for programmatic use:

```bash
gh search issues "import error" --repo pandas-dev/pandas --json number,title,url,state,commentsCount --limit 10
```

**Important distinctions**:
- `gh search issues --state`: Only `{open|closed}` - omit flag to search both
- `gh issue list --state`: Supports `{open|closed|all}` - but only searches one repo
- JSON field for comment count is `commentsCount` (not `comments`)

## Search Strategy for Troubleshooting

### Step 1: Extract Search Terms

From the error:
```
weaviate.exceptions.WeaviateGRPCUnavailableError: gRPC health check failed
```

Extract key terms:
- `WeaviateGRPCUnavailableError`
- `gRPC health check`
- `grpc failed`

### Step 2: Search Progressively

Start specific, then broaden:

```bash
# Most specific - exact error class
gh search issues "WeaviateGRPCUnavailableError" --repo weaviate/weaviate-python-client

# Broader - error type
gh search issues "gRPC health check" --repo weaviate/weaviate-python-client

# Broadest - across org
gh search issues "grpc connection" --owner weaviate --limit 20
```

### Step 3: Filter by Relevance

Use labels and reactions to find high-quality issues:

```bash
# Issues with bug label
gh search issues "timeout" --repo fastapi/fastapi --label bug

# Highly discussed issues (likely well-documented)
gh search issues "async" --repo encode/httpx --comments ">10"

# Recently updated (active discussion)
gh search issues "memory" --repo dagster-io/dagster --sort updated
```

### Step 4: View Issue Details

Once you find relevant issues:

```bash
# View specific issue
gh issue view 1234 --repo owner/repo

# View with comments
gh issue view 1234 --repo owner/repo --comments

# Open in browser for full context
gh issue view 1234 --repo owner/repo --web
```

## Common Search Patterns by Error Type

### Connection/Network Errors

```bash
gh search issues "connection refused" --repo owner/repo
gh search issues "timeout" --repo owner/repo --label bug
gh search issues "SSL" OR "certificate" --repo owner/repo
gh search issues "ECONNRESET" --repo owner/repo
```

### Import/Module Errors

```bash
gh search issues "ImportError" --repo owner/repo
gh search issues "ModuleNotFoundError" --repo owner/repo
gh search issues "cannot import" --repo owner/repo
```

### Memory/Performance Issues

```bash
gh search issues "memory leak" --repo owner/repo
gh search issues "OOM" OR "out of memory" --repo owner/repo
gh search issues "slow" OR "performance" --repo owner/repo --label performance
```

### Async/Concurrency Issues

```bash
gh search issues "deadlock" --repo owner/repo
gh search issues "RuntimeError" "event loop" --repo owner/repo
gh search issues "asyncio" --repo owner/repo --label bug
```

### Database/Query Errors

```bash
gh search issues "connection pool" --repo owner/repo
gh search issues "query timeout" --repo owner/repo
gh search issues "transaction" --repo owner/repo --state closed
```

## Output Formatting

### Table Format (Default)

```bash
gh search issues "error" --repo owner/repo
```

### JSON for Processing

```bash
gh search issues "error" --repo owner/repo --json number,title,url,state,createdAt,commentsCount
```

### Custom Template

```bash
gh search issues "error" --repo owner/repo --template '{{range .}}#{{.number}} {{.title}} ({{.commentsCount}} comments){{"\n"}}{{end}}'
```

## Searching Multiple Repositories

### By Owner (Organization)

```bash
gh search issues "deprecation warning" --owner anthropics --limit 30
```

### Multiple Specific Repos

```bash
gh search issues "async" --repo encode/httpx --repo aio-libs/aiohttp --limit 20
```

### By Language

```bash
gh search issues "type hint" --language python --limit 20
```

## Advanced Filters

### By Date

```bash
# Created in last 30 days
gh search issues "bug" --repo owner/repo --created ">2024-01-01"

# Recently updated
gh search issues "fix" --repo owner/repo --updated ">2024-01-01"

# Closed issues with solutions
gh search issues "workaround" --repo owner/repo --state closed --closed ">2024-01-01"
```

### By User Involvement

```bash
# Issues where maintainer commented
gh search issues "error" --repo owner/repo --commenter maintainer-username

# Issues assigned to someone
gh search issues "priority" --repo owner/repo --assignee username
```

### By Reactions (Quality Signal)

```bash
# Popular issues (likely well-documented)
gh search issues "feature" --repo owner/repo --reactions ">10"
```

## Critical Rules

1. **Search closed issues first** - They often contain solutions and workarounds
2. **Use exact error class names** - Most specific search term
3. **Check issue comments** - Solutions often in discussion, not original post
4. **Note version numbers** - Issues may be version-specific
5. **Look for linked PRs** - May contain the fix
6. **Search org-wide for generic errors** - Issue might be in different repo
7. **Combine with release notes** - Error might be fixed in newer version
8. **Quote multi-word phrases** - `"connection reset"` not `connection reset`
9. **Use state filters strategically** - Open for ongoing, closed for solutions
10. **Check reactions** - High reactions often indicate widespread issue

## Workflow Integration

When encountering an error in development:

```bash
# 1. Search for the exact error
gh search issues "ExactErrorClass" --repo library/repo --limit 5

# 2. If no results, broaden search
gh search issues "general error terms" --owner org-name --limit 10

# 3. View promising issues
gh issue view ISSUE_NUMBER --repo owner/repo --comments

# 4. If issue exists, check for linked PRs or workarounds in comments

# 5. If new issue, create with context
gh issue create --repo owner/repo --title "Brief description" --body "Details..."
```

## Reference Files

For detailed patterns:
- `references/search-syntax.md` - GitHub search syntax reference
- `examples/` - Common search scenarios 