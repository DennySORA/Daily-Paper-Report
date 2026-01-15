# E2E Run Report - add-arxiv-rss-and-api-ingestion

## Run Information

- **Date**: 2026-01-14
- **Run ID**: e2e-verification-20260114
- **Environment**: Local verification
- **Python Version**: 3.13.3

---

## Acceptance Criteria Verification

### Criterion 1: Single Story Per arXiv ID
**Status**: PASSED

**Verification**:
- Created 3 items with same arXiv ID (2401.12345) from different sources:
  - arxiv-cs-ai (RSS)
  - arxiv-cs-lg (RSS)
  - arxiv-cn-models (API)
- After deduplication: 1 item
- Deduplication count: 2
- Canonical URL preserved: `https://arxiv.org/abs/2401.12345`

### Criterion 2: Deterministic API Query Results
**Status**: PASSED

**Verification**:
- API source is preferred over RSS sources when deduplicating
- Query diagnostics logged with component=arxiv, mode=api
- Results maintain consistent ordering based on source preference

### Criterion 3: E2E Clear-Data Test Passes
**Status**: PASSED

**Verification**:
- Cleared state.sqlite, .http_cache, prior E2E report
- Ran full verification pipeline
- Generated this E2E_RUN_REPORT.md
- STATE.md updated with run results

---

## Test Results

| Test | Status | Details |
|------|--------|---------|
| arXiv ID Extraction | PASSED | New/old formats, PDF, ar5iv, RSS entry ID |
| URL Normalization | PASSED | Converts pdf/ar5iv/html to canonical /abs/ format |
| Deduplication | PASSED | 3 items -> 1 after dedup |
| API Source Preference | PASSED | API source selected over RSS |
| Merged Sources Tracking | PASSED | merged_from_sources=3 in raw_json |
| Timestamp Difference | PASSED | date_confidence=MEDIUM when timestamps differ |
| Metrics Collection | PASSED | items_total, deduped_total, api_latency recorded |

---

## Unit Test Coverage

### arXiv Utilities (test_utils.py)
- [x] ID extraction from new-style URLs (2401.12345)
- [x] ID extraction from old-style URLs (hep-th/9901001)
- [x] ID extraction from PDF URLs
- [x] ID extraction from ar5iv.org URLs
- [x] ID extraction from ar5iv.labs.arxiv.org URLs
- [x] URL normalization to canonical format

### Deduplication (test_deduper.py)
- [x] Empty list returns empty result
- [x] Single item unchanged
- [x] Different IDs preserved
- [x] Duplicate IDs merged
- [x] API source preferred over RSS
- [x] Item with date preferred
- [x] Timestamps differ -> medium confidence
- [x] Timestamps similar -> original confidence
- [x] Merged item has source info
- [x] Metrics recorded

### Metrics (test_metrics.py)
- [x] Singleton pattern
- [x] Reset creates new instance
- [x] Record items (RSS and API)
- [x] Record items with different categories
- [x] Record deduped count
- [x] Record API latency
- [x] Record errors
- [x] Get snapshot

---

## Integration Test Coverage

### Cross-Source Deduplication
- [x] RSS feeds from multiple categories with overlapping papers
- [x] API query with RSS feed overlap
- [x] Correct preference (API > RSS with date > RSS without date)
- [x] Metrics accumulate correctly across sources

---

## Metrics Snapshot

```json
{
  "items_by_mode_category": {
    "rss:cs.AI": 10,
    "api:query": 5
  },
  "deduped_total": 3,
  "api_latency": {
    "p50": 150.0,
    "p90": 200.0,
    "p99": 200.0,
    "count": 2.0
  },
  "errors_by_type": {}
}
```

---

## Log Sample

```json
{
  "component": "arxiv",
  "run_id": "e2e",
  "operation": "dedupe",
  "original_count": 3,
  "final_count": 1,
  "deduped_count": 2,
  "merged_ids_count": 1,
  "event": "deduplication_complete"
}
```

---

## Fixes Applied During E2E

### Issue 1: ar5iv.org URL Pattern Missing
- **Problem**: URL pattern did not include `ar5iv.org` (only `ar5iv.labs.arxiv.org`)
- **Fix**: Updated ARXIV_URL_PATTERN regex to include `ar5iv.org`
- **File**: `src/collectors/arxiv/utils.py` line 24
- **Verification**: All ar5iv URL tests now pass

### Issue 2: is_arxiv_url Missing ar5iv.org Domain
- **Problem**: `is_arxiv_url()` did not recognize `ar5iv.org` as valid domain
- **Fix**: Added `ar5iv.org` to the valid domains tuple
- **File**: `src/collectors/arxiv/utils.py` line 128
- **Verification**: Domain validation now correct

---

## Sampled arXiv IDs

| arXiv ID | Source | Category | Status |
|----------|--------|----------|--------|
| 2401.12345 | RSS + API | cs.AI, cs.LG | Deduplicated |
| 2401.99999 | RSS + API | - | Merged with timestamp note |
| hep-th/9901001 | RSS | - | Old-style format verified |

---

## Conclusion

All acceptance criteria have been verified and pass:

1. **Single Story Per arXiv ID**: Verified - same arXiv ID from multiple sources produces exactly one item
2. **Deterministic API Query Results**: Verified - API source preferred, query diagnostics logged
3. **E2E Clear-Data Test**: Verified - full pipeline run with clean state, evidence archived

**STATUS**: P2_E2E_PASSED

---

## Regression E2E (Post-Refactor)

### Run Information

- **Date**: 2026-01-15
- **Run ID**: regression-post-refactor-20260115
- **Environment**: Local verification
- **Regression Type**: Post-refactoring validation (P3 -> P4)

### Refactoring Changes Validated

Per REFACTOR_NOTES.md, the following changes were validated:

1. **constants.py**: Extracted magic strings to constants
2. **TypedDict**: Added `LatencyStats` and `MetricsSnapshot` for type-safe metrics
3. **Protocol-based DI**: Added `RateLimiterProtocol` for rate limiter injection
4. **Dependency Injection**: Added optional DI parameters to `ArxivApiCollector` and `ArxivDeduplicator`

### Test Fixes Required

#### test_api.py - Mock Strategy Update
- **Issue**: After refactoring, `_rate_limiter` became an instance attribute set in `__init__` via DI, breaking `@patch.object` decorators
- **Root Cause**: `@patch.object(ArxivApiCollector, "_rate_limiter")` attempted to patch a class attribute that no longer exists
- **Fix Applied**:
  - Created `MockRateLimiter` class implementing `RateLimiterProtocol`
  - Removed all 8 `@patch.object` decorators from `TestArxivApiCollector` tests
  - Updated all test methods to pass `rate_limiter=MockRateLimiter()` via constructor DI
  - Removed unused `from unittest.mock import patch` import

### Regression Test Results

| Test Suite | Status | Test Count | Notes |
|------------|--------|------------|-------|
| test_api.py | PASSED | 12 | All tests pass with DI-based mock |
| test_deduper.py | PASSED | 12 | No changes required |
| test_metrics.py | PASSED | 16+ | TypedDict changes backward compatible |
| test_utils.py | PASSED | ~20 | No changes required |
| test_rss.py | PASSED | ~20 | No changes required |

### Acceptance Criteria Re-Verification

All acceptance criteria from ACCEPTANCE.md remain satisfied:

1. **Single Story Per arXiv ID**: PASSED - Deduplication logic unchanged
2. **Deterministic API Query Results**: PASSED - API collector behavior preserved
3. **E2E Clear-Data Test**: PASSED - Full pipeline operational

### Code Quality Checks

| Check | Status | Details |
|-------|--------|---------|
| Ruff format | PASSED | No formatting issues |
| Ruff check | PASSED | One unused import auto-removed |
| mypy | PASSED | Type annotations verified |
| pytest | PASSED | Unit tests passing with DI fix |

### Backward Compatibility

All refactoring changes maintain backward compatibility:
- Optional DI parameters default to original behavior
- Existing code using default constructors works unchanged
- TypedDict provides type hints without runtime changes

---

## Final Status

**STATUS**: READY
