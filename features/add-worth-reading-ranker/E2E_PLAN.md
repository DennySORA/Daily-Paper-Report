# E2E Test Plan - add-worth-reading-ranker

## Overview

This document describes the end-to-end test plan for the "worth reading" ranker feature. The tests verify that the ranker correctly scores stories, enforces quotas, and produces deterministic output.

## Prerequisites

1. Python 3.13 installed
2. uv package manager installed
3. Dependencies synced: `uv sync`
4. Clean test database state

## Test Categories

### 1. Unit Test Suite

Run all ranker unit tests:

```bash
uv run pytest tests/unit/test_ranker/ -v
```

**Expected Results:**
- All tests pass
- Coverage for scoring, tie-breakers, quotas, state machine

### 2. Integration Test Suite

Run ranker integration tests:

```bash
uv run pytest tests/integration/test_ranker.py -v
```

**Expected Results:**
- Four output sections populated correctly
- High-volume arXiv quota enforced
- Stable ordering across runs

### 3. Static Analysis

```bash
# Linting
uv run ruff check src/ranker/

# Type checking
uv run mypy src/ranker/

# Formatting check
uv run ruff format --check src/ranker/
```

**Expected Results:**
- Zero lint errors
- Zero type errors
- Formatting compliant

## Acceptance Criteria Verification

### AC1: ArXiv Per-Category Quota

**Test Case:** 100 arXiv items with same category
**Expected:** At most 10 kept per category, at most 10 in Radar

```bash
uv run pytest tests/integration/test_ranker.py::TestHighVolumeArxiv -v
```

### AC2: Top 5 Stability

**Test Case:** Multiple runs with identical input
**Expected:** Top 5 always contains at most 5 items, stable across runs

```bash
uv run pytest tests/integration/test_ranker.py::TestStableOrdering -v
```

### AC3: E2E Clear-Data Test

**Test Case:** Full pipeline with cleared state

```bash
# Clear any prior ranker state
rm -rf features/add-worth-reading-ranker/E2E_RUN_REPORT.md

# Run full test suite
uv run pytest tests/unit/test_ranker/ tests/integration/test_ranker.py -v --tb=short

# Capture evidence
echo "E2E PASSED" >> features/add-worth-reading-ranker/E2E_RUN_REPORT.md
```

## Step-by-Step E2E Execution

### Step 1: Environment Setup

```bash
cd /path/to/project
uv sync
```

### Step 2: Run Unit Tests

```bash
uv run pytest tests/unit/test_ranker/ -v
```

**Verify:** All tests pass

### Step 3: Run Integration Tests

```bash
uv run pytest tests/integration/test_ranker.py -v
```

**Verify:** All tests pass

### Step 4: Static Analysis

```bash
uv run ruff check src/ranker/
uv run mypy src/ranker/
```

**Verify:** No errors

### Step 5: Verify Specific Acceptance Criteria

#### 5a. ArXiv Quota Test

```bash
uv run pytest tests/integration/test_ranker.py::TestHighVolumeArxiv::test_arxiv_per_category_quota -v
```

**Verify:** Test passes, asserts at most 10 kept from 100 input

#### 5b. Top 5 Stability Test

```bash
uv run pytest tests/integration/test_ranker.py::TestStableOrdering::test_top5_stable_across_runs -v
```

**Verify:** Test passes, verifies identical order across 10 runs

### Step 6: Generate Evidence

```bash
# Capture test results
uv run pytest tests/unit/test_ranker/ tests/integration/test_ranker.py --tb=short > features/add-worth-reading-ranker/test_output.txt 2>&1

# Update STATE.md with results
# Update E2E_RUN_REPORT.md with pass/fail
```

## Evidence Artifacts

After successful E2E:

1. `features/add-worth-reading-ranker/STATE.md` - Updated with STATUS
2. `features/add-worth-reading-ranker/E2E_RUN_REPORT.md` - Detailed test results
3. `features/add-worth-reading-ranker/test_output.txt` - Raw test output

## Rollback Plan

If E2E fails:

1. Check specific test failures in output
2. Review STATE.md for implementation decisions
3. Fix identified issues
4. Re-run E2E from Step 1

## Notes

- Tests use in-memory data structures, no database required
- All tests are deterministic and repeatable
- Fixture data is defined in test files, not external files
