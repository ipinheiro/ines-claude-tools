# Code Review Standards Quick Reference

Quick checklist for both review agents. Detailed explanations in the agent files.

## Code Quality Standards

### Typing
- [ ] All parameters typed
- [ ] All return types annotated
- [ ] Modern syntax: `list[str]`, `X | None`
- [ ] No unnarrowed `Any`
- [ ] No unjustified `# type: ignore`
- [ ] Pydantic for structured data

### Logging (structlog)
- [ ] Key-value pairs, not f-strings
- [ ] Lowercase messages
- [ ] Appropriate levels (debug/info/warning/error)
- [ ] No print() except CLI output

### Error Handling
- [ ] Minimal try/except
- [ ] Specific exception types
- [ ] No empty catch blocks
- [ ] No broad Exception without re-raise

### Organization
- [ ] Named constants for magic numbers
- [ ] Guard clauses over nesting
- [ ] Single responsibility
- [ ] Imports at top, grouped

## Logic Verification Checks

### Contract Verification
- [ ] Implementation honors return type for ALL inputs
- [ ] Edge cases handled (None, empty, invalid)
- [ ] Exceptions documented or prevented

### Control Flow
- [ ] All paths enumerated
- [ ] No unreachable code
- [ ] Loop invariants maintained

### Assumptions
- [ ] Input assumptions documented
- [ ] Assumptions validated at boundaries
- [ ] Failure modes explicit

### Silent Failures (Data Pipeline Critical)
- [ ] No swallowed exceptions
- [ ] No default values masking missing data
- [ ] Truthy checks don't conflate None/empty
- [ ] Dropped records logged and counted
- [ ] Aggregations handle missing values explicitly

### Boundaries
- [ ] Empty collection handling
- [ ] Off-by-one checks
- [ ] Single element edge case
- [ ] Zero/negative number handling

## Security

### Injection Prevention
- [ ] No string interpolation in SQL queries
- [ ] No `shell=True` with user-controlled input
- [ ] No `eval()`/`exec()` on untrusted data
- [ ] Template rendering uses auto-escaping

### Secrets Management
- [ ] No hardcoded credentials, API keys, or tokens
- [ ] Secrets loaded from environment or secret manager
- [ ] Sensitive data not logged or included in error messages

### Data Exposure
- [ ] API responses use explicit field selection or response models
- [ ] Error handlers don't leak stack traces or internal details
- [ ] Sensitive fields excluded from serialization

### Path Safety
- [ ] User-controlled paths resolved and checked for containment
- [ ] No direct concatenation of user input into file paths

### Deserialization
- [ ] No `pickle.loads()` on untrusted data
- [ ] YAML uses `safe_load` / `SafeLoader`
- [ ] No `eval()` on external input

### Authentication & Authorization
- [ ] Sensitive endpoints have auth decorators/middleware
- [ ] Token comparison uses timing-safe functions
- [ ] No auth bypass via default/fallback values

## Severity Guide

### Critical (must fix)
- Data corruption possible
- Contract violations (wrong return type)
- Silent failures in data pipelines
- Security issues

### Important (should fix)
- Missing type annotations on public APIs
- Inconsistent error handling
- Undocumented assumptions
- Magic numbers in business logic

### Suggestions (consider)
- Code organization improvements
- Refactoring opportunities
- Pattern consistency
- Documentation gaps
