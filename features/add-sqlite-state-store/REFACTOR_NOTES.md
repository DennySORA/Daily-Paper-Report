# REFACTOR_NOTES.md - add-sqlite-state-store

## Refactoring Summary

**Date**: 2026-01-14
**Status**: P3_REFACTORED_DEPLOYED

This document describes the refactoring work performed in Prompt #3 to improve code quality, maintainability, and adherence to SOLID principles.

---

## Changes Made

### 1. Extracted Content Hash Utility (SRP)

**File**: `src/store/hash.py` (NEW)

Moved `compute_content_hash` function from `store.py` to a dedicated utility module:

- Improves Single Responsibility: store.py focuses on database operations
- Better testability: hash function can be tested independently
- Clearer intent: module name reflects purpose

**Backward Compatibility**: Re-export added in `store.py` for existing imports.

---

### 2. Created Domain Exception Hierarchy (Error Layering)

**File**: `src/store/errors.py` (NEW)

Introduced structured exception types:

| Exception | Purpose |
|-----------|---------|
| `StateStoreError` | Base exception for all store errors |
| `ConnectionError` | Database connection failures |
| `RunNotFoundError` | Run record not found |
| `ItemNotFoundError` | Item not found by URL |
| `MigrationError` | Schema migration failures |

**Benefits**:
- Separates infrastructure errors from domain errors
- Enables granular error handling at call sites
- Improves error traceability with context (run_id, url, version)

---

### 3. Refactored `upsert_item` Method (SRP, DRY)

**File**: `src/store/store.py`

Extracted helper methods to reduce complexity:

| Method | Purpose | Lines Saved |
|--------|---------|-------------|
| `_build_result_item()` | Creates Item with stored values | 40+ lines |
| `_insert_new_item()` | INSERT SQL for new items | 15 lines |
| `_update_item_content()` | UPDATE SQL for changed items | 15 lines |

**Before**: 150+ line method with duplicated Item construction
**After**: 70 line method with clear separation of concerns

---

### 4. Added MetricsRecorder Protocol (DIP)

**File**: `src/store/metrics.py`

Introduced `MetricsRecorder` Protocol:

```python
class MetricsRecorder(Protocol):
    def record_upsert(self) -> None: ...
    def record_update(self) -> None: ...
    def record_unchanged(self) -> None: ...
    def record_tx_duration(self, duration_ms: float) -> None: ...
    def record_last_success_age(self, age_seconds: float) -> None: ...
    def record_items_pruned(self, count: int) -> None: ...
    def record_runs_pruned(self, count: int) -> None: ...
```

Added `NullMetricsRecorder` for testing scenarios where metrics are not needed.

**Benefits**:
- Dependency Inversion: Store can work with any MetricsRecorder implementation
- Improved testability: Tests can inject NullMetricsRecorder
- Future extensibility: Easy to add Prometheus, StatsD, or custom recorders

---

### 5. Updated Module Exports

**File**: `src/store/__init__.py`

Extended public API with new modules:

```python
__all__ = [
    # Errors (NEW)
    "ConnectionError", "ItemNotFoundError", "MigrationError",
    "RunNotFoundError", "StateStoreError",
    # Hash utilities (NEW)
    "compute_content_hash",
    # Metrics (EXPANDED)
    "MetricsRecorder", "NullMetricsRecorder", "StoreMetrics",
    # Models (unchanged)
    "DateConfidence", "HttpCacheEntry", "Item", "ItemEventType",
    "Run", "UpsertResult",
    # State machine (unchanged)
    "RunState", "RunStateMachine", "RunStateError",
    # Store (unchanged)
    "StateStore",
    # URL utilities (unchanged)
    "canonicalize_url",
]
```

---

## SOLID Compliance

| Principle | Implementation |
|-----------|----------------|
| **SRP** | Hash utility extracted; upsert_item simplified |
| **OCP** | MetricsRecorder protocol allows extension without modification |
| **LSP** | NullMetricsRecorder substitutable for StoreMetrics |
| **ISP** | Protocol defines minimal interface for metrics |
| **DIP** | Store depends on MetricsRecorder abstraction |

---

## Quality Status

| Check | Status |
|-------|--------|
| `ruff check .` | ✅ All checks passed |
| `ruff format --check .` | ✅ 44 files formatted |
| `mypy .` | ✅ No issues in 44 source files |
| `pytest` | ✅ 208 tests passed in 1.26s |

---

## Risks and Rollback Plan

### Risks

1. **Import path changes**: Code importing `compute_content_hash` from `store.store` continues to work via re-export
2. **Exception type changes**: Callers catching `StateStoreError` will catch all new subtypes
3. **No breaking changes to public API**: All changes are additive

### Rollback Plan

If issues are discovered:

1. **Revert errors.py**: Delete file, restore `StateStoreError` to store.py
2. **Revert hash.py**: Delete file, restore `compute_content_hash` to store.py
3. **Revert metrics.py**: Remove Protocol and NullMetricsRecorder
4. **Revert store.py**: Inline helper methods back into upsert_item

All changes are isolated and can be reverted independently.

---

## Files Changed

| File | Change Type |
|------|-------------|
| `src/store/hash.py` | NEW |
| `src/store/errors.py` | NEW |
| `src/store/metrics.py` | MODIFIED (added Protocol, NullMetricsRecorder) |
| `src/store/store.py` | MODIFIED (refactored upsert_item, updated imports) |
| `src/store/__init__.py` | MODIFIED (expanded exports) |
| `tests/integration/test_store.py` | MODIFIED (import fix) |
| `tests/unit/test_store/test_models.py` | MODIFIED (removed unused type ignore) |
| `tests/unit/test_store/test_migrations.py` | MODIFIED (Generator type annotations) |

---

## Guidance for Prompt #4 Regression E2E

For the regression E2E in Prompt #4:

1. **Re-run E2E_PLAN.md Steps 4-9** to verify refactoring didn't break functionality
2. **Verify error handling**: Test that `RunNotFoundError` is raised appropriately
3. **Verify metrics still work**: Check `StoreMetrics.get_instance()` collects data
4. **Verify hash consistency**: Same inputs produce same hash outputs
5. **Update STATE.md to READY** after all acceptance criteria pass

Commands for quick verification:

```bash
# Unit tests
uv run pytest tests/unit/test_store/ -v --no-cov

# Integration tests
uv run pytest tests/integration/test_store.py -v --no-cov

# E2E verification (Python script)
# Run the script from E2E_PLAN.md Steps 4-8
```
