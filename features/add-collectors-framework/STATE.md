# STATE.md - add-collectors-framework

## Feature Metadata

- **FEATURE_KEY**: add-collectors-framework
- **STATUS**: READY
- **Last Updated**: 2026-01-14T17:35:00Z
- **Prompt**: P4 of 4 (COMPLETE)

## Decisions

1. **Collector Interface**: Use a Protocol-based interface with `collect(source_config, http_client, now) -> CollectorResult`
2. **State Machine**: Per-source states: SOURCE_PENDING -> SOURCE_FETCHING -> SOURCE_PARSING -> SOURCE_DONE|SOURCE_FAILED
3. **Error Hierarchy**: CollectorError base with ParseError, SchemaError subtypes; FetchError reused from fetch layer
4. **Ordering**: Deterministic sort by (published_at DESC NULLS LAST, url ASC)
5. **Raw JSON Cap**: 100KB limit with `raw_truncated: true` marker
6. **Concurrency**: ThreadPoolExecutor with configurable max_workers

## Completed Items (P1)

- [x] Feature directory created
- [x] Initial STATE.md created
- [x] Collector errors module (`src/collectors/errors.py`)
- [x] Collector state machine (`src/collectors/state_machine.py`)
- [x] Collector metrics (`src/collectors/metrics.py`)
- [x] Base collector interface and utilities (`src/collectors/base.py`)
- [x] RSS/Atom collector (`src/collectors/rss_atom.py`)
- [x] HTML list collector (`src/collectors/html_list.py`)
- [x] Collector runner (`src/collectors/runner.py`)
- [x] Module exports (`src/collectors/__init__.py`)
- [x] Unit tests for state machine, errors, base utilities
- [x] Integration tests for collector + SQLite
- [x] Lint, format, type check pass
- [x] All 355 tests pass
- [x] E2E_PLAN.md created
- [x] ACCEPTANCE.md created
- [x] RUNBOOK_VERIFICATION.md created
- [x] CHANGELOG.md created

## Completed Items (P2)

- [x] Pre-deployment checks (format, lint, type, security)
- [x] E2E Scenario 1: RSS/Atom Feed Collection - PASS
- [x] E2E Scenario 2: HTML List Collection - PASS
- [x] E2E Scenario 3: Multiple Source Collection - PASS
- [x] E2E Scenario 4: Failure Isolation - PASS
- [x] E2E Scenario 5: Idempotent Upserts - PASS
- [x] E2E Scenario 6: max_items Enforcement - PASS
- [x] E2E Scenario 7: Cache Hit (304) - PASS
- [x] Health check commands - PASS
- [x] Browser verification (coverage report) - PASS
- [x] E2E_RUN_REPORT.md created

## Files Created

### Source Files
- `src/collectors/__init__.py` - Module exports
- `src/collectors/errors.py` - Error types (CollectorError, ParseError, SchemaError, ErrorRecord)
- `src/collectors/state_machine.py` - State machine (SourceState, SourceStateMachine)
- `src/collectors/metrics.py` - Thread-safe metrics (CollectorMetrics)
- `src/collectors/base.py` - Base collector (BaseCollector, CollectorResult, Collector protocol)
- `src/collectors/rss_atom.py` - RSS/Atom collector (RssAtomCollector)
- `src/collectors/html_list.py` - HTML list collector (HtmlListCollector)
- `src/collectors/runner.py` - Runner (CollectorRunner, RunnerResult, SourceRunResult)

### Test Files
- `tests/unit/test_collectors/test_state_machine.py` - State machine tests (17 tests)
- `tests/unit/test_collectors/test_errors.py` - Error type tests
- `tests/unit/test_collectors/test_base.py` - Base collector utility tests
- `tests/integration/test_collectors.py` - SQLite integration tests

### Documentation
- `features/add-collectors-framework/E2E_PLAN.md` - End-to-end test plan
- `features/add-collectors-framework/ACCEPTANCE.md` - Acceptance criteria checklist
- `features/add-collectors-framework/RUNBOOK_VERIFICATION.md` - Deployment runbook
- `features/add-collectors-framework/CHANGELOG.md` - Feature changelog
- `features/add-collectors-framework/E2E_RUN_REPORT.md` - E2E validation report

## Dependencies Added

```toml
[project.dependencies]
feedparser = ">=6.0.0"
beautifulsoup4 = ">=4.12.0"
lxml = ">=5.0.0"
python-dateutil = ">=2.8.0"

[tool.uv.dev-dependencies]
types-python-dateutil = ">=2.8.0"
types-beautifulsoup4 = ">=4.12.0"
```

## Validation Results (P2)

| Check | Status |
|-------|--------|
| Ruff format | PASS |
| Ruff check | PASS |
| Mypy | PASS |
| Pytest (355 tests) | PASS |
| E2E Scenarios (7/7) | PASS |
| Health Checks | PASS |
| Browser Verification | PASS |

## E2E Fixes Applied

1. Fixed `Mapping` import from `collections.abc` instead of `typing`
2. Fixed `Generator` return type for pytest fixtures
3. Fixed Pydantic `ValidationError` expectation in immutability test
4. Fixed unnecessary variable assignments (ruff RET504)
5. Added `# type: ignore[import-untyped]` for feedparser

## Risks Mitigated

1. **RSS/Atom parsing complexity** - Mitigated by using feedparser library with bozo handling
2. **HTML parsing fragility** - Mitigated by container selectors with link fallback strategy
3. **SQLite thread safety** - Mitigated by using max_workers=1 in tests; production uses thread-local connections

## Per-Source Parse Diagnostics (E2E Results)

| source_id | method | items_emitted | parse_warnings_count | state |
|-----------|--------|---------------|---------------------|-------|
| test-rss | RSS_ATOM | 3 | 0 | SOURCE_DONE |
| test-html | HTML_LIST | 2 | 0 | SOURCE_DONE |
| test-limited | RSS_ATOM | 1 | 0 | SOURCE_DONE |
| test-fail | RSS_ATOM | 0 | 0 | SOURCE_FAILED |

## Completed Items (P3)

- [x] Simplified `sort_items_deterministically` in `base.py` (30 lines → 15 lines)
- [x] Fixed singleton pattern in `metrics.py` (module-level state with double-checked locking)
- [x] Added comprehensive tests for `metrics.py` (29 tests, 58% → 100% coverage)
- [x] Added comprehensive tests for `rss_atom.py` (21 tests, 61% → 80% coverage)
- [x] All quality checks pass (ruff format, ruff check, mypy)
- [x] All 405 tests pass
- [x] REFACTOR_NOTES.md created

## Validation Results (P3)

| Check | Status |
|-------|--------|
| Ruff format | PASS (72 files) |
| Ruff check | PASS |
| Mypy | PASS (72 files) |
| Pytest (405 tests) | PASS |
| Overall Coverage | 76% |

## Coverage Improvements (P3)

| Module | Before | After | Change |
|--------|--------|-------|--------|
| `src/collectors/metrics.py` | 58% | 100% | +42% |
| `src/collectors/rss_atom.py` | 61% | 80% | +19% |
| `src/collectors/state_machine.py` | 80% | 100% | +20% |
| `src/collectors/errors.py` | 43% | 100% | +57% |

## Files Modified (P3)

### Source Files
- `src/collectors/base.py` - Simplified sorting method
- `src/collectors/metrics.py` - Fixed singleton pattern

### Test Files (NEW)
- `tests/unit/test_collectors/test_metrics.py` - 29 tests
- `tests/unit/test_collectors/test_rss_atom.py` - 21 tests

### Documentation
- `features/add-collectors-framework/REFACTOR_NOTES.md` - Refactoring details

## Completed Items (P4)

- [x] Pre-deployment checks (format, lint, type, security) - PASS
- [x] Re-run all 7 E2E scenarios - ALL PASS
- [x] Run health check commands - PASS
- [x] Verify browser coverage report (76%, no console errors) - PASS
- [x] All 405 tests pass - PASS
- [x] E2E_RUN_REPORT.md updated with P4 results
- [x] STATE.md updated to STATUS=READY

## Validation Results (P4)

| Check | Status |
|-------|--------|
| Ruff format | PASS (72 files) |
| Ruff check | PASS |
| Mypy | PASS (72 files) |
| Pytest (405 tests) | PASS |
| E2E Scenarios (7/7) | PASS |
| Health Checks | PASS |
| Browser Verification | PASS |
| Overall Coverage | 76% |

## Feature Close-Out Summary

The `add-collectors-framework` feature has completed all 4 prompts:

| Prompt | Description | Status |
|--------|-------------|--------|
| P1 | Implementation | P1_DONE_DEPLOYED |
| P2 | E2E Validation | P2_E2E_PASSED |
| P3 | Refactoring | P3_REFACTORED_DEPLOYED |
| P4 | Regression E2E | READY |

**Final Status**: READY for production deployment
