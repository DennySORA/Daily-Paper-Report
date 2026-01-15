STATUS: READY

# STATE.md - add-sources-status-and-degradation-reporting

## Feature State Machine

| Field | Value |
|-------|-------|
| FEATURE_KEY | add-sources-status-and-degradation-reporting |
| STATUS | READY |
| RUN_ID | (generated at runtime) |
| GIT_COMMIT | (pending - code ready, not yet committed) |
| LAST_UPDATED | 2026-01-15 |
| TESTS_PASSED | 63 unit + 5 integration + 1 E2E = 69 total |
| E2E_VALIDATED | 2026-01-15 |
| E2E_CONSOLE_ERRORS | 0 |
| E2E_NETWORK_FAILURES | 0 |
| LINT_STATUS | All checks passed |
| TYPE_CHECK | Success: no issues found |
| REFACTORED | 2026-01-15 |

## Decisions Made

### Status Classification Rules
1. **HAS_UPDATE**: fetch+parse succeeded AND (items_new > 0 OR items_updated > 0)
2. **NO_UPDATE**: fetch+parse succeeded AND items_new = 0 AND items_updated = 0
3. **FETCH_FAILED**: HTTP fetch failed (timeout, 4xx, 5xx, network error)
4. **PARSE_FAILED**: Parse failed after successful fetch
5. **CANNOT_CONFIRM**: fetch+parse succeeded BUT all dates missing AND no stable ordering
6. **STATUS_ONLY**: Source method is status_only

### Illegal Transition Guards
- Cannot assign NO_UPDATE if fetch or parse failed (enforced by `IllegalStatusTransitionError`)

### Source Categories
- `INTL_LABS`: International research labs (OpenAI, Google, Anthropic, etc.)
- `CN_ECOSYSTEM`: Chinese/CN ecosystem (Alibaba, Baidu, Tencent, etc.)
- `PLATFORMS`: Development platforms (HuggingFace, GitHub, OpenReview)
- `PAPER_SOURCES`: Academic paper sources (arXiv)
- `OTHER`: Uncategorized sources

### Reason Codes (Stable Enum)
All reason codes are defined in `src/status/models.py:ReasonCode` with:
- Machine-readable code (e.g., `FETCH_PARSE_OK_HAS_NEW`)
- Human-readable text mapped via `REASON_TEXT_MAP`
- Optional remediation hints via `REMEDIATION_HINT_MAP`

## Completed Items

- [x] Created `src/status/` module structure
- [x] Implemented `ReasonCode` enum with 18 reason codes
- [x] Implemented `SourceCategory` enum with 5 categories
- [x] Implemented `StatusComputer` class with classification rules
- [x] Added illegal transition guards
- [x] Added `StatusMetrics` for failure/cannot-confirm tracking
- [x] Updated `SourceStatus` model to include `category` field
- [x] Updated `sources.html` template with category grouping and summary stats
- [x] Updated JSON renderer to include category in output
- [x] Added structured logging for audit trail (rule path)
- [x] Created unit tests for models, computer, and metrics
- [x] Created integration tests for status rendering

### Prompt #3 Refactoring (Completed)
- [x] Added `StatusSummary` model for pre-computed summary statistics
- [x] Extracted error mapping to `src/status/error_mapper.py` module
- [x] Added `compute_summary()` method to StatusComputer
- [x] Refactored HTML template with CSS classes (removed inline styles)
- [x] Added hover/focus states and transitions
- [x] Added ARIA labels for accessibility
- [x] Added responsive design improvements
- [x] Added 22 new unit tests for StatusSummary and error mapper
- [x] Created REFACTOR_NOTES.md
- [x] Created DESIGN_GUIDE.md

## Files Changed

### New Files (Prompt #1)
- `src/status/__init__.py` - Module exports
- `src/status/models.py` - ReasonCode, SourceCategory, StatusRulePath, StatusSummary
- `src/status/computer.py` - StatusComputer class
- `src/status/metrics.py` - StatusMetrics class
- `tests/unit/test_status/__init__.py`
- `tests/unit/test_status/test_models.py`
- `tests/unit/test_status/test_computer.py`
- `tests/unit/test_status/test_metrics.py`
- `tests/integration/test_status_rendering.py`

### New Files (Prompt #3)
- `src/status/error_mapper.py` - Error-to-reason-code mapping functions
- `tests/unit/test_status/test_error_mapper.py` - Error mapper tests
- `features/add-sources-status-and-degradation-reporting/REFACTOR_NOTES.md`
- `features/add-sources-status-and-degradation-reporting/DESIGN_GUIDE.md`
- `features/add-sources-status-and-degradation-reporting/screenshot_refactored_sources.png`

### Modified Files
- `src/renderer/models.py` - Added `category` field to SourceStatus
- `src/renderer/json_renderer.py` - Added category to JSON output
- `src/renderer/templates/sources.html` - CSS classes, accessibility, hover states

## Validation in Verification Environment

### How to Validate
1. Run `uv run pytest tests/unit/test_status/` for unit tests
2. Run `uv run pytest tests/integration/test_status_rendering.py` for integration tests
3. Run `uv run python main.py` or render command to generate output
4. Check `public/sources.html` for grouped status display
5. Check `public/api/daily.json` for `sources_status` array

### Expected Outputs
- JSON API: `sources_status` array with all required fields per source
- HTML: Sources grouped by category with status badges and summary counts
- Logs: Audit trail with `status_computed` events containing rule path

## Risks

1. **Category mapping not yet integrated**: Source categories must be provided to StatusComputer; currently defaults to OTHER
2. **HTTP status code not captured**: `last_fetch_status_code` is currently None; requires fetch client enhancement

## Checksum

| File | SHA-256 |
|------|---------|
| api/daily.json | 26a8ecd312cdb3cadaccc05b5632db93efb042847e062525960dbd4a5551519a |

## E2E Validation Evidence

### Prompt #2 (Initial E2E)
- E2E_RUN_REPORT.md: Complete with all acceptance criteria verified
- Screenshot: screenshot_sources_html.png
- Console errors: 0
- Network failures: 0
- All 6 acceptance criteria: PASSED

### Prompt #3 (Post-Refactor E2E)
- Screenshot: screenshot_refactored_sources.png
- Console errors: 0
- Network failures: 0
- All tests: 63 unit + 5 integration = 68 passed
- Visual improvements: CSS classes, hover states, accessibility

### Prompt #4 (Final Regression E2E)
- Screenshot: screenshot_final_e2e.png
- Console errors: 0
- Network failures: 0
- All tests: 63 unit + 5 integration + 1 E2E = 69 passed
- All acceptance criteria: PASSED
- STATUS: READY

## Refactoring Summary

| Improvement | Description |
|-------------|-------------|
| StatusSummary model | Pre-computed summary statistics for template |
| Error mapper module | Extensible error-to-reason-code mapping |
| CSS classes | Replaced inline styles with reusable classes |
| Hover/focus states | Added transitions for interactivity |
| Accessibility | ARIA labels, proper heading hierarchy |
| Responsive design | Mobile-friendly table columns |

---

*This file is auto-maintained by the implementation process.*
