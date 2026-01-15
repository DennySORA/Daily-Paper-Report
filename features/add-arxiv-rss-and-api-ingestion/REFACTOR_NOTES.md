# REFACTOR_NOTES.md - add-arxiv-rss-and-api-ingestion

## Refactoring Summary

This document describes the refactoring performed on the arXiv collectors module to improve code quality, maintainability, and testability.

---

## Changes Made

### 1. Constants Extraction (Low Risk)

**File Created**: `src/collectors/arxiv/constants.py`

Centralized all magic strings and configuration values:

| Constant | Value | Purpose |
|----------|-------|---------|
| `SOURCE_TYPE_API` | `"api"` | Source type identifier for API |
| `SOURCE_TYPE_RSS` | `"rss"` | Source type identifier for RSS |
| `FIELD_SOURCE` | `"source"` | JSON field name |
| `FIELD_ARXIV_ID` | `"arxiv_id"` | JSON field name |
| `FIELD_MERGED_FROM_SOURCES` | `"merged_from_sources"` | JSON field name |
| `FIELD_SOURCE_IDS` | `"source_ids"` | JSON field name |
| `FIELD_TIMESTAMP_NOTE` | `"timestamp_note"` | JSON field name |
| `TIMESTAMP_NOTE_API_PREFERRED` | Full message | Timestamp note message |
| `ARXIV_API_BASE_URL` | `"http://export.arxiv.org/api/query"` | API URL |
| `ARXIV_API_RATE_LIMIT_SECONDS` | `1.0` | Rate limit interval |
| `MIN_TIMESTAMPS_FOR_COMPARISON` | `2` | Dedup threshold |
| `TIMESTAMP_DIFF_THRESHOLD_SECONDS` | `86400` | 1 day threshold |

**Benefit**: Eliminates magic strings, enables centralized configuration, improves searchability.

### 2. TypedDict for Metrics (Medium Risk)

**File Modified**: `src/collectors/arxiv/metrics.py`

Added type-safe return types for metrics:

```python
class LatencyStats(TypedDict):
    p50: float
    p90: float
    p99: float
    count: float

class MetricsSnapshot(TypedDict):
    items_by_mode_category: dict[str, int]
    deduped_total: int
    api_latency: LatencyStats
    errors_by_type: dict[str, int]
```

- `get_api_latency_stats()` now returns `LatencyStats`
- `get_snapshot()` now returns `MetricsSnapshot`

**Benefit**: Type-safe access to metrics, no more `isinstance()` checks in tests, better IDE support.

### 3. Protocol for Rate Limiter (Low Risk)

**File Modified**: `src/collectors/arxiv/api.py`

Added `RateLimiterProtocol` for dependency injection:

```python
class RateLimiterProtocol(Protocol):
    def wait_if_needed(self) -> None: ...
```

**Benefit**: Enables testing without real sleep(), follows DIP principle.

### 4. Dependency Injection (Low Risk)

**Files Modified**:
- `src/collectors/arxiv/deduper.py`
- `src/collectors/arxiv/api.py`

Added optional DI parameters:

```python
# ArxivDeduplicator
def __init__(
    self,
    run_id: str = "",
    metrics: MetricsRecorder | None = None,  # NEW
) -> None:

# ArxivApiCollector
def __init__(
    self,
    strip_params: list[str] | None = None,
    run_id: str = "",
    rate_limiter: RateLimiterProtocol | None = None,  # NEW
) -> None:
```

**Benefit**:
- Enables unit testing with mock dependencies
- Follows SOLID DIP (Dependency Inversion Principle)
- Maintains backward compatibility (optional parameters with defaults)

---

## SOLID Compliance

| Principle | Implementation |
|-----------|----------------|
| **SRP** | Each module has single responsibility (utils, deduper, metrics, api) |
| **OCP** | New behavior via protocols and DI, not modifying core logic |
| **LSP** | Protocols ensure mock implementations are substitutable |
| **ISP** | Small, focused protocols (`MetricsRecorder`, `RateLimiterProtocol`) |
| **DIP** | High-level modules depend on abstractions (protocols) not concretions |

---

## Risks and Mitigations

### Risk: Breaking Existing Tests
- **Mitigation**: All constructor changes use optional parameters with defaults
- **Verification**: Lint, mypy, and E2E tests pass

### Risk: Import Cycles
- **Mitigation**: Moved imports inside constructors where needed
- **Verification**: All imports resolve correctly

### Risk: Type Errors from TypedDict
- **Mitigation**: Updated tests to use proper TypedDict access patterns
- **Verification**: mypy passes with no errors

---

## Rollback Plan

Each change is isolated and can be reverted independently:

1. **Constants**: Revert `constants.py` creation and inline strings back
2. **TypedDict**: Revert to `dict[str, int | float | dict[str, int | float]]` return type
3. **Protocol**: Remove `RateLimiterProtocol`, use concrete `ArxivApiRateLimiter` type
4. **DI**: Remove optional parameters, use direct singleton access

All changes can be reverted with:
```bash
git checkout HEAD~1 -- src/collectors/arxiv/
```

---

## Quality Status

| Check | Status |
|-------|--------|
| `ruff check` | PASSED |
| `mypy` | PASSED (no issues in 7 files) |
| E2E Verification | PASSED |
| Backward Compatibility | Maintained |

---

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `src/collectors/arxiv/constants.py` | NEW | Constants for magic strings |
| `src/collectors/arxiv/metrics.py` | MODIFIED | Added TypedDict, updated return types |
| `src/collectors/arxiv/deduper.py` | MODIFIED | Added Protocol, DI for metrics, use constants |
| `src/collectors/arxiv/api.py` | MODIFIED | Added Protocol, DI for rate limiter, use constants |
| `tests/unit/test_collectors/test_arxiv/test_metrics.py` | MODIFIED | Removed isinstance checks |
| `tests/integration/test_arxiv.py` | MODIFIED | Removed isinstance checks |

---

## Future Improvements

For Prompt #4 regression testing, consider:

1. **Mock Rate Limiter Test**: Add test using injected mock to avoid real sleep()
2. **Mock Metrics Test**: Add test using injected mock to verify metric recording
3. **Edge Case Coverage**: Add tests for malformed XML, network errors, rate limiting
