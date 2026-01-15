# E2E_PLAN.md - Collector Framework

## Overview

End-to-end validation plan for the `add-collectors-framework` feature. This document provides executable test scenarios to verify the collector framework functions correctly in an integrated environment.

## Prerequisites

- Python 3.13 with uv installed
- All dependencies synced: `uv sync`
- SQLite available (built into Python)

## Test Scenarios

### Scenario 1: RSS/Atom Feed Collection

**Objective**: Verify RSS/Atom collector correctly parses feeds and persists items.

**Steps**:
1. Start with a clean test database
2. Configure an RSS source pointing to a mock or real RSS feed
3. Run the collector via CollectorRunner
4. Verify items are persisted to SQLite with correct fields

**Expected Results**:
- [ ] Items extracted with title, url, published_at
- [ ] URLs canonicalized (no tracking params)
- [ ] Items sorted by published_at DESC, url ASC
- [ ] State transitions: PENDING -> FETCHING -> PARSING -> DONE

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_rss_collector_upserts_items -v
```

### Scenario 2: HTML List Collection

**Objective**: Verify HTML list collector extracts articles from blog-style pages.

**Steps**:
1. Start with a clean test database
2. Configure an HTML_LIST source
3. Run the collector
4. Verify items extracted from article containers

**Expected Results**:
- [ ] Article links extracted from containers (<article>, .post, etc.)
- [ ] Titles extracted from headings or link text
- [ ] Date extraction with confidence levels
- [ ] Navigation links filtered out

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_html_collector_upserts_items -v
```

### Scenario 3: Multiple Source Collection

**Objective**: Verify multiple sources can be collected in a single run.

**Steps**:
1. Configure both RSS and HTML sources
2. Run CollectorRunner with both sources
3. Verify all items from both sources persisted

**Expected Results**:
- [ ] Both sources processed successfully
- [ ] Items from each source correctly attributed (source_id)
- [ ] Total item count matches expected

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_multiple_collectors_sequential -v
```

### Scenario 4: Failure Isolation

**Objective**: Verify one failing source doesn't prevent others from succeeding.

**Steps**:
1. Configure two sources: one that will fail (500 error), one that succeeds
2. Run CollectorRunner
3. Verify successful source still persists items

**Expected Results**:
- [ ] Failed source marked with SOURCE_FAILED state
- [ ] Successful source marked with SOURCE_DONE state
- [ ] Items from successful source persisted
- [ ] Error properly recorded for failed source

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_failing_source_isolated -v
```

### Scenario 5: Idempotent Upserts

**Objective**: Verify running the same collection twice doesn't create duplicates.

**Steps**:
1. Run collector with RSS source
2. Note item count (should be 3)
3. Run collector again with same source
4. Verify item count unchanged

**Expected Results**:
- [ ] First run: 3 new items inserted
- [ ] Second run: 0 new items, 3 items seen
- [ ] Database still contains exactly 3 items

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_idempotent_upsert -v
```

### Scenario 6: max_items Enforcement

**Objective**: Verify max_items configuration limits collected items.

**Steps**:
1. Configure source with max_items=1
2. Run collector against feed with 3 items
3. Verify only 1 item persisted

**Expected Results**:
- [ ] Only 1 item collected despite 3 available
- [ ] Most recent item selected (by published_at)

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_max_items_enforced -v
```

### Scenario 7: Cache Hit (304 Not Modified)

**Objective**: Verify cache hit returns success with zero items.

**Steps**:
1. Configure source with HTTP client returning 304
2. Run collector
3. Verify success state with empty items

**Expected Results**:
- [ ] Source marked as succeeded
- [ ] Zero items collected
- [ ] No error recorded

**Verification Command**:
```bash
uv run pytest tests/integration/test_collectors.py::TestCollectorRunnerIntegration::test_cache_hit_no_items -v
```

## Full Test Suite

Run all integration tests:
```bash
uv run pytest tests/integration/test_collectors.py -v
```

Run all unit tests for collectors:
```bash
uv run pytest tests/unit/test_collectors/ -v
```

Run complete test suite:
```bash
uv run pytest -v
```

## Validation Checklist

Before marking P1_DONE_DEPLOYED:

- [ ] All unit tests pass: `uv run pytest tests/unit/`
- [ ] All integration tests pass: `uv run pytest tests/integration/`
- [ ] Ruff format check passes: `uv run ruff format --check .`
- [ ] Ruff lint check passes: `uv run ruff check .`
- [ ] Mypy type check passes: `uv run mypy .`
- [ ] No new security vulnerabilities: `uv run bandit -r src/`
