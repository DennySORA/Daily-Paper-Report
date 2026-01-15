# E2E Test Plan: Story Linker and Dedupe

## Overview

This document provides the end-to-end test plan for verifying the Story Linker feature. Follow these steps in sequence for Prompt #2.

## Prerequisites

1. Python 3.13+ with uv installed
2. Repository cloned and dependencies synced: `uv sync`
3. Clean test environment

## Test Fixtures

The following fixture data should be prepared/used:

### Fixture 1: Duplicate arXiv Items
- 3 items with same arXiv ID (2401.12345) from different sources
- Expected: Merge into 1 Story

### Fixture 2: Cross-Platform Items
- 1 HuggingFace model page
- 1 GitHub release
- 1 Official blog post referencing same model
- Expected: Separate Stories unless linked by stable ID

### Fixture 3: Entity Matching
- Items containing OpenAI, Anthropic, and DeepMind keywords
- Expected: Correct entity assignment

---

## E2E Test Steps

### Step 1: Clear Prior State
```bash
# Clear any previous test artifacts
rm -rf /tmp/linker-e2e-test
mkdir -p /tmp/linker-e2e-test/public
mkdir -p /tmp/linker-e2e-test/features
```

### Step 2: Run Unit Tests
```bash
uv run pytest tests/unit/test_linker/ -v --tb=short
```

**Expected**: All tests pass

### Step 3: Run Integration Tests
```bash
uv run pytest tests/integration/test_linker.py -v --tb=short
```

**Expected**: All tests pass

### Step 4: Verify Lint and Type Checks
```bash
uv run ruff check src/linker/
uv run mypy src/linker/
```

**Expected**: No errors

### Step 5: Verify Story ID Determinism

Run the following Python script:
```python
# test_determinism.py
from datetime import UTC, datetime
from src.linker.linker import StoryLinker
from src.store.models import Item, DateConfidence

items = [
    Item(
        url="https://arxiv.org/abs/2401.12345",
        source_id="arxiv",
        tier=1,
        kind="paper",
        title="Test Paper",
        published_at=datetime(2024, 1, 15, tzinfo=UTC),
        date_confidence=DateConfidence.HIGH,
        content_hash="hash1",
        raw_json="{}",
    )
]

# Run twice
linker1 = StoryLinker(run_id="run1")
result1 = linker1.link_items(items)

linker2 = StoryLinker(run_id="run2")
result2 = linker2.link_items(items)

assert result1.stories[0].story_id == result2.stories[0].story_id
print("Determinism check PASSED")
```

### Step 6: Verify Primary Link Precedence

Create test with multiple link types and verify official is selected over arxiv.

### Step 7: Verify Duplicate Link Collapse

Create items with same arXiv ID and verify only one link per type in output Story.

### Step 8: Verify Entity Matching

Create items with entity keywords and verify entities list is populated.

### Step 9: Verify Persistence

```python
from pathlib import Path
from src.linker.persistence import LinkerPersistence

# Verify daily.json is created with correct schema
# Verify STATE.md is created with statistics
```

### Step 10: Verify State Machine Transitions

Attempt invalid transitions and verify LinkerStateTransitionError is raised.

---

## Acceptance Verification

| Criterion | Test Method | Expected Result |
|-----------|-------------|-----------------|
| Same arXiv ID = 1 Story | Integration test | Single Story with merged links |
| Stable ordering | Run twice, compare | Byte-identical daily.json |
| E2E evidence archived | Check files | E2E_RUN_REPORT.md exists |

---

## Evidence Capture

After successful E2E run:

1. Update `features/add-story-linker-and-dedupe/E2E_RUN_REPORT.md` with:
   - Run ID
   - Git commit
   - Test results summary
   - Sample merge rationales

2. Update `features/add-story-linker-and-dedupe/STATE.md` with:
   - STATUS: P2_E2E_PASSED
   - Statistics from run

---

## Rollback Plan

If E2E fails:
1. Identify failing test
2. Fix issue in src/linker/
3. Re-run full test suite
4. Do not update STATUS until all tests pass
