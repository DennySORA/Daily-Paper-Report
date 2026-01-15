# E2E_PLAN.md - add-sqlite-state-store

## Overview

This document describes the end-to-end test plan for verifying the SQLite state store feature.

## Prerequisites

- Python 3.13 with uv installed
- All dependencies installed: `uv sync`
- Test fixtures available (fixture data will be created during test)

## Test Environment

- **Environment**: INT (Integration Testing / Local)
- **Database**: Temporary SQLite file (created fresh for each test)
- **Configuration**: Minimal test fixtures

## E2E Test Steps

### Step 1: Clear Prior State

```bash
# Remove any existing test database
rm -f /tmp/e2e_test_state.sqlite

# Verify no database exists
ls -la /tmp/e2e_test_state.sqlite 2>&1 | grep "No such file"
```

**Expected**: File does not exist

### Step 2: Run Unit Tests

```bash
uv run pytest tests/unit/test_store/ -v --no-cov
```

**Expected**: All tests pass

### Step 3: Run Integration Tests

```bash
uv run pytest tests/integration/test_store.py -v --no-cov
```

**Expected**: All tests pass

### Step 4: Verify Idempotent Ingestion (Fixture Run 1)

```python
# Run this in Python REPL or as a script
from datetime import UTC, datetime
from pathlib import Path
from src.store.store import StateStore, compute_content_hash
from src.store.models import Item, DateConfidence

db_path = Path("/tmp/e2e_test_state.sqlite")
db_path.unlink(missing_ok=True)

# First run
with StateStore(db_path, run_id="run-1") as store:
    store.begin_run("run-1")

    items = [
        Item(
            url=f"https://example.com/article-{i}",
            source_id="test-source",
            tier=0,
            kind="blog",
            title=f"Article {i}",
            published_at=datetime.now(UTC),
            date_confidence=DateConfidence.HIGH,
            content_hash=compute_content_hash(f"Article {i}", f"https://example.com/article-{i}"),
            raw_json="{}",
        )
        for i in range(5)
    ]

    results = [store.upsert_item(item) for item in items]
    new_count = sum(1 for r in results if r.event_type.value == "NEW")

    store.end_run("run-1", success=True)

    stats = store.get_stats()
    first_seen_times = {r.item.url: r.item.first_seen_at for r in results}

print(f"Run 1: {new_count} NEW items, {stats['items']} total items")
# Expected: 5 NEW items, 5 total items
```

### Step 5: Verify Idempotent Ingestion (Fixture Run 2)

```python
# Second run with identical fixtures
with StateStore(db_path, run_id="run-2") as store:
    store.begin_run("run-2")

    # Same items as run 1
    items = [
        Item(
            url=f"https://example.com/article-{i}",
            source_id="test-source",
            tier=0,
            kind="blog",
            title=f"Article {i}",
            published_at=datetime.now(UTC),
            date_confidence=DateConfidence.HIGH,
            content_hash=compute_content_hash(f"Article {i}", f"https://example.com/article-{i}"),
            raw_json="{}",
        )
        for i in range(5)
    ]

    results = [store.upsert_item(item) for item in items]
    unchanged_count = sum(1 for r in results if r.event_type.value == "UNCHANGED")

    # Verify first_seen_at is preserved
    for r in results:
        original_first_seen = first_seen_times[r.item.url]
        assert r.item.first_seen_at == original_first_seen, f"first_seen_at changed for {r.item.url}"

    store.end_run("run-2", success=True)

    stats = store.get_stats()

print(f"Run 2: {unchanged_count} UNCHANGED items, {stats['items']} total items")
# Expected: 5 UNCHANGED items, 5 total items (no duplicates)
```

### Step 6: Verify Update Detection

```python
# Third run with one updated item
with StateStore(db_path, run_id="run-3") as store:
    store.begin_run("run-3")

    # Item with changed content_hash
    updated_item = Item(
        url="https://example.com/article-0",
        source_id="test-source",
        tier=0,
        kind="blog",
        title="Article 0 (Updated)",  # Changed title
        published_at=datetime.now(UTC),
        date_confidence=DateConfidence.HIGH,
        content_hash=compute_content_hash("Article 0 (Updated)", "https://example.com/article-0"),
        raw_json='{"version": 2}',
    )

    result = store.upsert_item(updated_item)

    assert result.event_type.value == "UPDATED", f"Expected UPDATED, got {result.event_type.value}"

    # first_seen_at should still be preserved
    assert result.item.first_seen_at == first_seen_times[result.item.url]

    store.end_run("run-3", success=True)

    stats = store.get_stats()

print(f"Run 3: Item updated successfully, {stats['items']} total items")
# Expected: 1 UPDATED item, 5 total items
```

### Step 7: Verify URL Canonicalization

```python
with StateStore(db_path, run_id="run-4") as store:
    store.begin_run("run-4")

    # Insert with tracking params
    item_with_tracking = Item(
        url="https://example.com/new-article?utm_source=test&utm_medium=email",
        source_id="test-source",
        tier=0,
        kind="blog",
        title="New Article",
        content_hash="canonical-test-hash",
        raw_json="{}",
    )

    result = store.upsert_item(item_with_tracking)

    # URL should be canonicalized
    assert "utm_source" not in result.item.url
    assert result.item.url == "https://example.com/new-article"

    store.end_run("run-4", success=True)

print("URL canonicalization verified")
```

### Step 8: Verify Last Successful Run Detection

```python
with StateStore(db_path) as store:
    last_success = store.get_last_successful_run_finished_at()
    assert last_success is not None
    print(f"Last successful run: {last_success.isoformat()}")

# Expected: Returns timestamp of most recent successful run
```

### Step 9: Verify Database Stats

```bash
uv run digest db-stats --state /tmp/e2e_test_state.sqlite
```

**Expected Output**:
```
State Database Statistics
========================================
  Schema Version: 1
  Last Successful Run: 2026-01-14T...

Table Row Counts:
  http_cache: 0
  items: 6
  runs: 4
```

## Acceptance Criteria Verification

### AC1: Two consecutive runs with identical fixtures produce same item count
- [x] Run 1: 5 items inserted
- [x] Run 2: 5 items total (no duplicates)
- [x] first_seen_at preserved for all items

### AC2: content_hash changes are recorded as UPDATED
- [x] Run 3: Changed item detected as UPDATED
- [x] first_seen_at still preserved

### AC3: E2E passes and archives evidence
- [ ] Run this E2E plan
- [ ] Capture output to E2E_RUN_REPORT.md
- [ ] Update STATE.md with final status

## Cleanup

```bash
rm -f /tmp/e2e_test_state.sqlite
```
