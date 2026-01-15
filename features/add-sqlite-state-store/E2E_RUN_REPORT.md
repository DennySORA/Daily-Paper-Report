# E2E_RUN_REPORT.md - add-sqlite-state-store

## Execution Summary

- **Date**: 2026-01-14
- **Environment**: INT (Local Development)
- **Python Version**: 3.13.3
- **Database**: /tmp/e2e_test_state.sqlite

## Test Results

### Step 1: Clear Prior State
- **Status**: ✅ PASSED
- **Evidence**: File `/tmp/e2e_test_state.sqlite` confirmed not to exist

### Step 2: Run Unit Tests
- **Status**: ✅ PASSED
- **Result**: 78 passed in 0.17s
- **Command**: `uv run pytest tests/unit/test_store/ -v --no-cov`

### Step 3: Run Integration Tests
- **Status**: ✅ PASSED
- **Result**: 33 passed in 0.32s
- **Command**: `uv run pytest tests/integration/test_store.py -v --no-cov`

### Step 4: Verify Idempotent Ingestion (Fixture Run 1)
- **Status**: ✅ PASSED
- **Result**: 5 NEW items inserted, 5 total items
- **Evidence**: All items created with ItemEventType.NEW

### Step 5: Verify Idempotent Ingestion (Fixture Run 2)
- **Status**: ✅ PASSED
- **Result**: 5 UNCHANGED items, 5 total items (no duplicates)
- **Evidence**:
  - All items marked as ItemEventType.UNCHANGED
  - `first_seen_at` preserved for all 5 items
  - No duplicate rows created

### Step 6: Verify Update Detection
- **Status**: ✅ PASSED
- **Result**: 1 UPDATED item detected
- **Evidence**:
  - Item with changed `content_hash` correctly identified as UPDATED
  - `first_seen_at` preserved despite update
  - New `raw_json` and title stored

### Step 7: Verify URL Canonicalization
- **Status**: ✅ PASSED
- **Input URL**: `https://example.com/new-article?utm_source=test&utm_medium=email`
- **Canonicalized URL**: `https://example.com/new-article`
- **Evidence**: UTM parameters successfully stripped

### Step 8: Verify Last Successful Run Detection
- **Status**: ✅ PASSED
- **Result**: `2026-01-14T07:36:34.867339+00:00`
- **Evidence**: `get_last_successful_run_finished_at()` returns correct timestamp

### Step 9: Verify db-stats CLI Command
- **Status**: ✅ PASSED
- **Command**: `uv run python -m src.cli.digest db-stats --state /tmp/e2e_test_state.sqlite`
- **Output**:
  ```
  State Database Statistics
  ========================================
    Schema Version: 1
    Last Successful Run: 2026-01-14T07:36:34.867339+00:00

  Table Row Counts:
    http_cache: 0
    items: 6
    runs: 4
  ```

## Acceptance Criteria Verification

### AC1: Idempotent Ingestion - No Duplicates
- ✅ Two consecutive runs with identical fixtures produce exactly the same item count (5)
- ✅ `first_seen_at` is not modified for existing URLs

### AC2: Update Detection
- ✅ `content_hash` changes are recorded as UPDATED
- ✅ `first_seen_at` is preserved on update
- ✅ New content is stored correctly

### AC3: E2E Clear-Data Test
- ✅ E2E test executed successfully
- ✅ Evidence archived to this file
- ✅ STATE.md updated with P2_E2E_PASSED status

## Final Database State

| Table | Row Count |
|-------|-----------|
| schema_version | 1 |
| runs | 4 |
| items | 6 |
| http_cache | 0 |

## Cleanup

```bash
rm -f /tmp/e2e_test_state.sqlite
```

---

# Prompt #4: Post-Refactor Regression E2E

## Execution Summary

- **Date**: 2026-01-14
- **Environment**: INT (Local Development)
- **Python Version**: 3.13.3
- **Database**: /tmp/e2e_regression_state.sqlite
- **Status**: All acceptance criteria verified after refactoring

## Regression Test Results

### Unit Tests
- **Status**: ✅ PASSED
- **Result**: 78 passed in 0.18s
- **Command**: `uv run pytest tests/unit/test_store/ -v --no-cov`

### Integration Tests
- **Status**: ✅ PASSED
- **Result**: 33 passed in 0.33s
- **Command**: `uv run pytest tests/integration/test_store.py -v --no-cov`

### E2E Steps 4-9 (Re-run)
| Step | Description | Status |
|------|-------------|--------|
| 4 | Idempotent Ingestion Run 1 | ✅ 5 NEW items |
| 5 | Idempotent Ingestion Run 2 | ✅ 5 UNCHANGED, first_seen_at preserved |
| 6 | Update Detection | ✅ UPDATED detected, first_seen_at preserved |
| 7 | URL Canonicalization | ✅ UTM params stripped |
| 8 | Last Successful Run Detection | ✅ Correct timestamp |
| 9 | db-stats | ✅ Schema v1, 4 runs, 6 items |

## Refactoring Verification

### New Modules Tested
| Module | Test | Status |
|--------|------|--------|
| `src/store/hash.py` | Deterministic hashing | ✅ PASSED |
| `src/store/hash.py` | Case-insensitive title | ✅ PASSED |
| `src/store/hash.py` | Extra field ordering | ✅ PASSED |
| `src/store/hash.py` | Package import | ✅ PASSED |
| `src/store/errors.py` | RunNotFoundError | ✅ PASSED |
| `src/store/errors.py` | ItemNotFoundError | ✅ PASSED |
| `src/store/errors.py` | StoreConnectionError | ✅ PASSED |
| `src/store/errors.py` | MigrationError | ✅ PASSED |
| `src/store/errors.py` | Exception hierarchy | ✅ PASSED |
| `src/store/metrics.py` | MetricsRecorder Protocol | ✅ PASSED |
| `src/store/metrics.py` | NullMetricsRecorder | ✅ PASSED |

### Backward Compatibility
- ✅ `compute_content_hash` importable from `src.store.store` (re-export)
- ✅ `compute_content_hash` importable from `src.store` (package)
- ✅ All existing tests pass without modification

## Final Acceptance Criteria Status

| AC | Requirement | Status |
|----|-------------|--------|
| AC1 | Idempotent ingestion - no duplicates | ✅ VERIFIED |
| AC2 | Update detection | ✅ VERIFIED |
| AC3 | E2E clear-data test | ✅ VERIFIED |

## Quality Checks

| Check | Result |
|-------|--------|
| `ruff check .` | ✅ All checks passed |
| `ruff format --check .` | ✅ 44 files formatted |
| `mypy .` | ✅ No issues in 44 source files |
| `pytest` | ✅ 208 tests passed |

## Conclusion

All acceptance criteria verified after refactoring. Feature is ready for release.

**STATUS: READY**
