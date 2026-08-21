---
name: dispatching-parallel-agents
description: This skill should be used when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies, such as "fix multiple test failures", "investigate several bugs", "process multiple ISBNs", "analyze different data sources", or "implement parallel features".
---

# Dispatching Parallel Agents

Dispatch multiple agents concurrently when tasks are independent. Each agent works on a focused problem domain without interfering with others.

## When to Use

**Use when:**
- 3+ test files failing with different root causes
- Multiple Pydantic AI agents need fixes independently
- Processing multiple ISBNs/records that don't share state
- Several subsystems broken independently
- Independent pipeline stages need investigation
- Each problem can be understood without context from others

**Don't use when:**
- Failures are related (fix one might fix others)
- Agents would edit same files
- Need to understand full system state first
- Sequential dependencies exist between tasks
- Shared resources (same database table, same S3 path)

## The Pattern

### 1. Identify Independent Domains

Group by what's broken:
- `copy_workflow.py` tests: Endorsement extraction failures
- `ai_image_workflow.py` tests: Cover analysis timeouts
- `overlay/` tests: Typography rendering issues

Each domain is independent - fixing copy extraction doesn't affect typography.

### 2. Create Focused Agent Tasks

Each agent gets:
- **Specific scope:** One test file, one pipeline stage, one agent
- **Clear goal:** Make these tests pass / fix this specific issue
- **Constraints:** Don't change unrelated code
- **Expected output:** Summary of root cause and changes

### 3. Dispatch in Parallel

Issue every `Agent` call in a **single message**. Calls sent in one message run concurrently; calls split across messages run one after another and you lose the parallelism.

```
Agent(subagent_type="general-purpose",
      description="Fix copy_workflow tests",
      prompt="Fix endorsement extraction failures in tests/copy/...")
Agent(subagent_type="general-purpose",
      description="Fix ai_image_workflow tests",
      prompt="Fix cover analysis timeouts in tests/ai_image/...")
Agent(subagent_type="general-purpose",
      description="Fix typography_engine tests",
      prompt="Fix rendering issues in tests/typography/...")
```

Agents run in the background by default and notify you as each finishes. Pass `run_in_background: false` when you need a result before you can continue. If agents will edit files that overlap, add `isolation: "worktree"` so each gets its own checkout instead of fighting over the working tree.

### 4. Review and Integrate

When agents return:
- Read each summary
- Verify fixes don't conflict
- Run full test suite: `uv run pytest`
- Integrate all changes

## Agent Prompt Structure

Good prompts are focused, self-contained, and specific about output.

**Example - Fixing test failures:**
```markdown
Fix the 3 failing tests in tests/copy/test_endorsement_extractor.py:

1. "test_extract_praise_with_attribution" - expects author in attribution field
2. "test_handle_empty_content" - returns None instead of empty list
3. "test_retry_on_model_error" - ModelRetry not raised

These tests verify the praise_extractor_agent behavior.

Your task:
1. Read the test file and understand what each test verifies
2. Read src/pkg/extraction/endorsement_extractor.py
3. Identify root cause - agent logic bug or test expectation issue?
4. Fix the actual issue, don't just make tests pass

Return: Summary of root cause and what you changed.
```

**Example - Processing multiple ISBNs:**
```markdown
Generate AI images for ISBN 9781529927344:

1. Run copy extraction to get endorsements
2. Analyze book cover with cover_analyzer_agent
3. Generate 4 background images with Nova Canvas
4. Score images with image_qa_agent

Constraints:
- Output to ./static/output/9781529927344/
- Use creativity level "normal"
- Don't modify any source code

Return: Summary of generated images and QA scores.
```

**Example - Investigating pipeline failures:**
```markdown
Investigate why non_ai_image_workflow fails for banners:

The pipeline returns empty results when image_type="banner".

Your task:
1. Read src/pkg/imaging/image_workflow.py
2. Trace the data flow for banner type
3. Check S3 histogram cache for banner images
4. Identify why no matches are found

Do NOT fix yet - just investigate and report findings.

Return: Root cause analysis with specific file:line references.
```

## Common Mistakes

**Too broad:** "Fix all the tests"
**Better:** "Fix tests/copy/test_endorsement_extractor.py"

**No context:** "Fix the agent"
**Better:** Paste error messages, test names, expected vs actual

**No constraints:** Agent might refactor everything
**Better:** "Only modify the agent file, not tests"

**Vague output:** "Fix it"
**Better:** "Return summary of root cause and changes made"

**Wrong parallelization:** Agents editing same Pydantic model
**Better:** Ensure agents work on separate files

## Verification Checklist

After agents return:

1. **Review summaries** - Understand what each agent found/changed
2. **Check for conflicts** - Did agents edit overlapping code?
3. **Run tests** - `uv run pytest` to verify all fixes work together
4. **Type check** - `uv run pyright` if you use it
5. **Spot check** - Agents can make systematic errors, review key changes

## Real-World Scenarios

### Scenario: Multiple Test File Failures

```
Failures:
- tests/copy/test_copy_workflow.py: 3 failures (async handling)
- tests/image/test_ai_image_workflow.py: 2 failures (QA scoring)
- tests/overlay/test_typography.py: 1 failure (font rendering)

Decision: Independent domains - copy, image, overlay don't interact

Dispatch:
  Agent 1 -> Fix copy workflow async failures
  Agent 2 -> Fix AI image QA scoring
  Agent 3 -> Fix typography font rendering

Results:
  Agent 1: Fixed await missing on agent.run() calls
  Agent 2: Adjusted QA threshold from 3.0 to 2.5
  Agent 3: Added fallback font path for missing Shift font
```

### Scenario: Batch ISBN Processing

```
Task: Generate assets for 5 ISBNs

Decision: Each ISBN is independent, no shared state

Dispatch:
  Agent 1 -> Process ISBN 9781529927344
  Agent 2 -> Process ISBN 9780241555522
  Agent 3 -> Process ISBN 9780241566343
  Agent 4 -> Process ISBN 9780140449136
  Agent 5 -> Process ISBN 9780141988511

Results: All 5 complete in parallel, ~3x faster than sequential
```

### Scenario: Multi-Agent System Debugging

```
Failures across Pydantic AI agents:
- content_analyzer_agent: Wrong content_type classification
- praise_extractor_agent: Missing attribution parsing
- qa_validator_agent: Not raising ModelRetry on low confidence

Decision: Each agent is independent, different system prompts

Dispatch:
  Agent 1 -> Fix content analyzer classification
  Agent 2 -> Fix praise extractor attribution
  Agent 3 -> Fix QA validator retry logic
```

## Key Benefits

1. **Parallelization** - Multiple investigations run simultaneously
2. **Focus** - Each agent has narrow scope, less context confusion
3. **Independence** - Agents don't step on each other's changes
4. **Speed** - N problems solved in time of 1 (roughly)
5. **Clarity** - Easier to review focused changes than monolithic fixes
