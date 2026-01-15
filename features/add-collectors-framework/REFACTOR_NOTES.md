# REFACTOR_NOTES.md - add-collectors-framework

## Refactoring Summary

Date: 2026-01-14
Prompt: P3 of 4

This document details the refactoring and optimization work performed on the collector framework during P3.

## Changes Made

### 1. Simplified `sort_items_deterministically` in `base.py`

**Before (complex multi-pass approach):**
- Used multiple list comprehensions to separate dated and null items
- Performed separate sorts on each list
- Combined results at the end
- ~30 lines of code

**After (single-pass approach):**
- Single `sorted()` call with a tuple key function
- Tuple key: `(priority, -timestamp, url)`
  - Priority 0 = dated items (first), priority 1 = nulls (last)
  - Negative timestamp for descending date order
  - URL for alphabetical tie-breaking
- ~15 lines of code

**Benefits:**
- Cleaner, more Pythonic implementation
- Single-pass algorithm (O(n log n) instead of multiple passes)
- Easier to understand and maintain

### 2. Fixed Singleton Pattern in `metrics.py`

**Before (problematic pattern):**
```python
@dataclass
class CollectorMetrics:
    _instance: "CollectorMetrics | None" = field(default=None, ...)
```
- Singleton state stored as dataclass field
- Not properly isolated from instance state
- Potential issues with dataclass inheritance

**After (proper module-level singleton):**
```python
_metrics_instance: "CollectorMetrics | None" = None
_metrics_lock: Lock = Lock()

@dataclass
class CollectorMetrics:
    @classmethod
    def get_instance(cls) -> "CollectorMetrics":
        global _metrics_instance  # noqa: PLW0603
        # Double-checked locking pattern
        ...
```

**Benefits:**
- Proper separation of singleton state from instance state
- Thread-safe with double-checked locking
- Follows Python singleton best practices

### 3. Added Comprehensive Test Coverage

#### `test_metrics.py` (NEW - 29 tests)

Coverage improvement: 58% → 100%

Test categories:
- **Singleton Pattern**: Instance creation, reset, thread-safety
- **Record Methods**: `record_items`, `record_failure`, `record_duration`
- **Query Methods**: `get_items_total`, `get_failures_total`, `get_duration`
- **Export Methods**: `to_prometheus_format`, `to_dict`
- **Thread Safety**: Concurrent access with ThreadPoolExecutor
- **Integration**: Full workflow simulation

#### `test_rss_atom.py` (NEW - 21 tests)

Coverage improvement: 61% → 80%

Test categories:
- **Initialization**: Default and custom parameters
- **Fetch Errors**: Error handling, state transitions
- **Cache Handling**: 304 Not Modified responses
- **Feed Parsing**: Empty feeds, malformed feeds, RSS 2.0, Atom 1.0
- **Entry Parsing**: Links (alternate, fallback), titles, relative URLs, categories, authors
- **Date Extraction**: published_parsed, updated_parsed, no date handling
- **Max Items**: Enforcement and selection of newest items

## Coverage Improvements

| Module | Before | After | Change |
|--------|--------|-------|--------|
| `src/collectors/metrics.py` | 58% | 100% | +42% |
| `src/collectors/rss_atom.py` | 61% | 80% | +19% |
| `src/collectors/state_machine.py` | 80% | 100% | +20% |
| `src/collectors/errors.py` | 43% | 100% | +57% |
| `src/collectors/base.py` | 89% | 88% | -1% |
| **Overall Project** | **74%** | **76%** | **+2%** |

## Quality Validation

All checks passed:

| Check | Command | Result |
|-------|---------|--------|
| Ruff Format | `uv run ruff format --check .` | 72 files formatted |
| Ruff Lint | `uv run ruff check .` | All checks passed |
| Mypy Type Check | `uv run mypy .` | No issues in 72 files |
| Pytest | `uv run pytest` | 405 passed |

## SOLID Principles Applied

### Single Responsibility (SRP)
- `sort_items_deterministically` now has a single, clear purpose
- Test files organized by module responsibility

### Open/Closed (OCP)
- Singleton pattern uses module-level state that doesn't affect class extension

### Dependency Inversion (DIP)
- Collectors depend on abstract `HttpFetcher` interface, not concrete implementations
- Test mocks verify the interface contract

## Files Modified

### Source Files
- `src/collectors/base.py` - Simplified sorting method
- `src/collectors/metrics.py` - Fixed singleton pattern

### Test Files (NEW)
- `tests/unit/test_collectors/test_metrics.py` - 29 tests, 100% coverage
- `tests/unit/test_collectors/test_rss_atom.py` - 21 tests, 80% coverage

## Risks Mitigated

1. **Thread Safety**: Singleton now properly uses double-checked locking with module-level lock
2. **Test Isolation**: Metrics fixture resets singleton between tests
3. **Pydantic Validation**: Tests use proper model construction instead of MagicMock

## Recommendations for Future Work

1. **HTML List Collector**: Coverage still at 49%, could benefit from additional edge case tests
2. **Runner Coverage**: At 86%, could add tests for concurrent execution paths
3. **Date Parsing**: Consider extracting common date parsing logic to shared utility (DRY principle)
