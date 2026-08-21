---
name: test-review
description: Review unit tests for quality, identifying tautological tests, stdlib/framework testing, redundant coverage, and missing behavioural tests. Use when asked to review tests, audit test quality, or check if tests are meaningful.
---

# Test Quality Review

Review test files to determine whether each test earns its place in the suite. A good test protects against a real regression in *your* code. A bad test gives false confidence by asserting things that can't fail.

## Invocation

- `/test-review` -- Review all test files in the project
- `/test-review <path>` -- Review a specific test file or directory

## Process

### Phase 1: Discover

1. Find test files: glob for `**/test_*.py` and `**/*_test.py`
2. Find the source code each test file exercises (imports, fixture usage)
3. Read both the tests and the code under test -- never judge a test without seeing the implementation

### Phase 2: Classify Each Test

For every test function, assign one of these verdicts:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **Keeper** | Tests real business logic or an important edge case | Leave it |
| **Tautological** | Asserts something that is always true by construction (e.g., `isinstance(pd.read_csv(...), pd.DataFrame)`) | Recommend removal |
| **Framework test** | Tests that a library/stdlib works (e.g., Pydantic defaults, `pathlib.mkdir`, `pd.read_csv` returns a DataFrame) | Recommend removal |
| **Redundant** | Another test already covers this behaviour with equal or stronger assertions | Recommend removal, cite the covering test |
| **Weak** | Tests real logic but assertions are too loose (e.g., `len(result) > 0` when an exact count is knowable) | Recommend strengthening |
| **Missing** | Not a test -- a gap identified by reading the source code | Recommend adding |

### Phase 3: Report

Present findings grouped by test file. For each file:

1. **Summary**: one-line assessment of the file's overall quality
2. **Test-by-test table**: test name, verdict, one-line rationale
3. **Recommendations**: concrete actions -- which tests to drop, strengthen, or add

### Phase 4: Act (if requested)

If the user asks to fix the issues, make changes in this order:

1. Remove tautological, framework-testing, and redundant tests
2. Strengthen weak tests
3. Add missing tests for uncovered behaviours

## Classification Heuristics

### Signs a test is tautological

- Asserts the return type of a well-typed function
- Asserts `len(result) > 0` without checking specific content
- Asserts that a variable equals the value it was just assigned
- Asserts `result is not None` when the function signature doesn't return Optional
- Uses `hasattr(obj, "method_name")` to verify an interface exists instead of testing behaviour
- Asserts a Pydantic model field is `None` when it was constructed without that field and the default is `None`
- Asserts an `assert` keyword is missing -- the comparison evaluates but the result is discarded (e.g., `result == expected` without `assert`)

Examples:

```python
# BAD: reads back the value just passed into the constructor
source = InputSource(isbn="9780306406157", has_valid_isbn=True)
assert source.isbn == "9780306406157"       # tautological -- Pydantic stores what you give it
assert source.has_valid_isbn is True         # tautological -- same value, same field

# BAD: isinstance on a hard-coded module-level string literal
assert isinstance(__version_lyric__, str)    # __version_lyric__: str = "Above the Earth"
assert len(__version_lyric__) > 0            # also weak -- no check of actual content

# BAD: hasattr introspection instead of behavioural testing
service = DatabaseService.__new__(DatabaseService)  # bypasses __init__
assert hasattr(service, "execute_query")             # only fails if method is renamed

# BAD: asserting is not None on a value that was explicitly provided
response = JobStatusResponse(status="processing", started_at=datetime.now())
assert response.started_at is not None  # started_at was just passed in -- can never be None

# BAD: asserting a default None field is None after construction without that field
provider = VaultProvider(use_vault=True)
assert provider.username is None  # username defaults to None -- tests Pydantic defaults

# BAD: missing the assert keyword -- comparison evaluates but test can never fail
result = validate_deployment("prod")
result == Deployment.Prod  # no assert! This line does nothing
```

### Signs a test is testing the framework

- The assertion would still pass if you replaced the function body with a direct stdlib/library call
- The test is verifying that `mkdir` creates directories, `Path.exists()` returns True after writing, or that a Pydantic model has its declared defaults
- Removing the function under test and inlining the library call would not change the test outcome
- Tests that `StrEnum` values equal their names or that `isinstance(State.X.value, str)` -- these are guaranteed by `StrEnum`
- Tests that `raise CustomError("msg")` raises `CustomError` or that all exceptions inherit from `Exception`
- Tests that `json.dumps(data, cls=SafeEncoder)` correctly serializes standard types (str, int, list, dict, bool, None) -- these fall through to `json.JSONEncoder`
- Tests that SHA-256 is deterministic or produces 64-character hex output -- these are properties of `hashlib`, not your code
- Tests that a Pydantic `model_validate()` with field aliases maps `camelCase` to `snake_case` -- this is Pydantic's alias mechanism
- Tests that `GenreClassificationCache.base_path.exists()` after construction -- tests `os.makedirs`, not your logic
- Tests that `isinstance(factory_result, ExpectedType)` when the factory's only job is to call a constructor

Examples:

```python
# BAD: testing that StrEnum behaves like StrEnum
for state in State:
    assert state.value == state.name    # guaranteed by StrEnum
assert isinstance(State.RECEIVED.value, str)  # StrEnum values are always strings

# BAD: testing that raise/except works in Python
with pytest.raises(Exception):
    raise BelgardError("test")  # all exceptions inherit from Exception -- language guarantee

# BAD: testing stdlib json serialization through a custom encoder
data = {"key": "value"}
result = json.dumps(data, cls=SafeEncoder)
assert result == '{"key": "value"}'  # SafeEncoder doesn't override behaviour for strings

# BAD: testing Pydantic model hydration from a dict
config = Config(**{"snowflake": {"database": "TEST_DB"}, ...})
assert config.snowflake.database == "TEST_DB"  # Pydantic stores what you give it

# BAD: testing that hashlib produces consistent hex output
hash1 = hash_bytes(b"test data")
hash2 = hash_bytes(b"test data")
assert hash1 == hash2           # SHA-256 is deterministic by definition
assert len(hash1) == 64         # SHA-256 always produces 64 hex chars

# BAD: testing that a directory was created during __init__
cache = GenreClassificationCache(base_path=tmp_path / "cache")
assert cache.base_path.exists()   # tests os.makedirs, not your logic
assert cache.base_path.is_dir()   # same
```

### Signs a test is redundant

- Two tests call the same function with the same inputs and assert overlapping properties
- A "shape" test (checks columns exist) is followed by a "content" test (checks actual values) -- the content test subsumes the shape test
- Two assertions within the same test body that are logically equivalent (e.g., `assert x == {}` followed by `assert len(x) == 0`)
- A test asserts `isinstance(result, PaginatedResult)` when the next line accesses `result.items[0]` -- the access would raise `AttributeError` if the type were wrong
- A `len` check followed by an indexed content check -- `assert result[0] == doc` would raise `IndexError` on an empty list, making `assert len(result) == 1` redundant
- Multiple tests that verify the same `assert_called_once()` mock with identical setup, differing only in assertion phrasing
- N parametrized cases testing the same code path that a single case already covers (e.g., 5 different truncation lengths when one already tests the branch)
- Six individual tests for six entries in a data list (e.g., redaction patterns) when each exercises the same `if pattern in key` code path -- one representative test plus the edge cases (case-insensitive, substring match) is sufficient

Examples:

```python
# BAD: logically equivalent assertions in the same test
assert claimed == {}
assert len(claimed) == 0  # already implied by == {}

# BAD: isinstance check before content access that would fail anyway
assert isinstance(result, PaginatedResult)  # redundant
assert result.items[0].description == "Main Description"  # would raise if wrong type

# BAD: len check before indexed content check
assert len(result) == 1      # redundant -- next line would IndexError on empty
assert result[0] == doc

# BAD: two tests with identical mock setup asserting the same thing differently
async def test_acknowledges_message(self):
    mock.xack = AsyncMock(return_value=1)
    ack_count = await acknowledge_message(...)
    assert ack_count == 1
    mock.xack.assert_called_once()

async def test_returns_acknowledgment_count(self):  # subsumed by the test above
    mock.xack = AsyncMock(return_value=1)
    result = await acknowledge_message(...)
    assert result == 1
```

### Signs a test is weak

- Asserts `is not None` on a mock that was configured to return a non-None value -- the mock guarantees the result
- Asserts `len(result) > 0` or `result != ""` when the mock returns a hardcoded non-empty value
- Asserts `isinstance(value, str)` on a value that should be a specific string (e.g., an ISO timestamp)
- Uses `or` in assertions like `assert "A" in output or "B" in output` -- the test passes regardless of which branch is true, so neither is enforced
- Uses `any(...)` with a substring check on log records instead of asserting specific log level, message, and payload
- Tests two different configurations (e.g., `creativity="minimal"` vs `creativity="experimental"`) with identical assertions -- neither verifies that the configuration actually *changed* the output
- Asserts on a mock's return value without testing that the mock was called with the right arguments

Examples:

```python
# BAD: mock guarantees the result, assertion is vacuous
model = make_json_response({"source": "NYT", "text": "A gripping tale."})
result = await praise_extractor_agent.run(text, deps=deps)
assert result.output.source is not None  # mock always returns "NYT" -- check == "NYT" instead

# BAD: != "" on a hardcoded non-empty mock response
assert result.output.style != ""  # mock returns "minimalist" -- assert == "minimalist"
assert len(result.output.mood_keywords) > 0  # mock returns ["clean", "modern"]

# BAD: isinstance(str) when a specific format is expected
call_args = mock_client.set.call_args[0]
assert isinstance(call_args[1], str)  # should assert ISO timestamp format

# BAD: or in assertion -- neither branch is enforced
assert "Fetching work_ids" in out or "Successfully fetched" in out

# BAD: two configs, same assertion -- doesn't verify the config matters
deps_minimal = ImageDeps(creativity="minimal")
deps_experimental = ImageDeps(creativity="experimental")
# both tests just assert len(result.output.generated_images) > 0
# neither checks that prompts differ between creativity levels
```

### What makes a test a keeper

- It would fail if someone introduced a real bug in the business logic
- It documents an edge case that isn't obvious from reading the code (e.g., null handling, empty input, boundary conditions)
- It exercises a code path with branching logic (if/else, match, filter predicates)
- The assertion checks a *computed* output, not a passthrough
- It tests a precedence or override rule where two signals conflict (e.g., kwarg overrides config value, thema code overrides is_fiction flag)
- It verifies security-relevant cache invalidation (e.g., cached credential must not be returned after identity changes)
- It asserts exact wire-level values at integration boundaries (e.g., the Redis `">"` sentinel, the `SortBy` query parameter key)
- It tests both the happy path and the error path of a validator, including the error message content
- It verifies multiple distinct post-conditions on a failure path (state set, error stored, message moved to DLQ, original acknowledged)
- It tests that a `@cached_property` returns the same object identity (`is` not just `==`)
- It uses a deliberately failing test to expose a known bug with a precise expected value

Examples:

```python
# GOOD: tests a business override rule -- two signals conflict, one wins
mock_result = {"is_fiction": False, "thema_code": "FBC"}  # thema F-prefix overrides
result = await get_isbn_metadata_from_snowflake(conn, isbn)
assert result.genre == Genre.FICTION  # thema code wins over is_fiction flag

# GOOD: security-relevant cache invalidation
vault._write_key(sample_key_bytes)
vault.username = "different_user"
assert vault._cached_key_bytes() is None  # stale credential must not be returned

# GOOD: exact wire-level value at integration boundary
keys_and_ids = mock_client.xreadgroup.call_args.kwargs["keys_and_ids"]
assert keys_and_ids == {"test:stream": ">"}  # ">" means new messages only

# GOOD: custom validator with both valid and invalid cases + error message
img = SelectedImage(quote_matching_key="2f8479", pipeline_type="ai", version=1)
assert img.quote_matching_key == "2f8479"
with pytest.raises(ValidationError):
    SelectedImage(quote_matching_key="abc", ...)  # too short -- rejected

# GOOD: multiple distinct post-conditions on failure path
mock_handler = AsyncMock(side_effect=ValueError("Test error"))
await process_and_ack_message(...)
mock_state_manager.set_state.assert_called()   # state -> FAILED
mock_state_manager.set_error.assert_called()    # error stored
mock_valkey.xadd.assert_called_once()           # moved to DLQ
mock_valkey.xack.assert_called_once()           # still acknowledged

# GOOD: testing data transformation with a non-obvious edge case
analysis = AnalysisData(source_isbn13="NO_ISBN_The_Winter_Fair", ...)
row = analysis.to_database_row()
assert row[1] is None  # synthetic placeholder must become NULL in the database

# GOOD: precedence rule -- kwarg overrides config field
dummy_config.role = "my_role"
dummy_config.connect(role="other_role")
assert captured.kwargs["role"] == "other_role"  # connect() kwarg wins

# GOOD: error message content matters for UX
with pytest.raises(ValueError) as err:
    DummyConfig.load("dummy.b", config_path=toml_file.name)
assert err.match(r".* has no \[dummy.b\] section \(got as far as \[dummy\]\).*")

# GOOD: caching contract -- shared cache across methods
await domain.get(1)
await domain.get_by_name("Test")
await domain.get_all()
mock_api._get.assert_called_once()  # all three share one cache; only one API call
```

### What's worth adding

- Untested branches in if/else or match statements
- Error paths and exception handling
- Boundary conditions (empty input, single element, max size)
- Integration between multiple functions in a pipeline
- The failure case of a validation that only has a happy-path test (e.g., character limit enforcement when the value *exceeds* the limit, not just when it's under)
- Health/status endpoints that only assert HTTP 200 but never test degraded state, response body content, or dependency failures
- Stream/queue consumers that only test the empty-stream path but not malformed data or message decoding errors
- Empty test files that import source modules but define no test functions -- a sign of deferred work that was forgotten
- Custom serializers (e.g., for numpy types, NaN, or non-JSON-native types) with zero coverage
- Fallback chains where only the primary path is tested but not the secondary or tertiary fallbacks
- Author/name parsing edge cases like names containing "and" (e.g., "Kell and Sons"), comma-separated lists with a final "and", or both fields being None

## Behavioral Principles

- Always read the source before judging the tests
- Be specific: "this test is tautological because X" not just "this test is weak"
- Don't recommend removing tests that serve as documentation of important edge cases, even if technically redundant
- Prefer strengthening over removing when a test covers real logic but has weak assertions
- Count the net change: if removing 3 tests and adding 2, the suite should have strictly better coverage of real behaviours
