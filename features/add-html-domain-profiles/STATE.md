# Feature State: add-html-domain-profiles

## Status
**STATUS: READY

## Feature Key
`add-html-domain-profiles`

## Feature Name
Add: Domain profiles for stable HTML list and article parsing

## Decisions Made

### Architecture
1. **Domain Profile System**: Created a new module `src/collectors/html_profile/` containing:
   - `models.py`: Pydantic models for DomainProfile, LinkExtractionRule, DateExtractionRule
   - `registry.py`: Thread-safe singleton registry for profile management
   - `date_extractor.py`: Date extraction with configurable precedence
   - `item_fetcher.py`: Item page fetcher with K-cap enforcement
   - `metrics.py`: Prometheus-style metrics for HTML profile parsing

2. **Date Extraction Precedence**: Implemented in order:
   1. `<time datetime>` element (HIGH confidence)
   2. `<meta property="article:published_time">` (HIGH confidence)
   3. JSON-LD `datePublished` (HIGH confidence)
   4. JSON-LD `dateModified`/`dateCreated` (MEDIUM confidence)
   5. Text regex patterns (MEDIUM confidence)
   6. No date found (LOW confidence, published_at=NULL)

3. **State Machine Extension**: Added two new states:
   - `SOURCE_PARSING_LIST`: For parsing HTML list pages
   - `SOURCE_PARSING_ITEM_PAGES`: For fetching item pages for date recovery
   - Guard: Cannot enter PARSING_ITEM_PAGES unless PARSING_LIST succeeded

4. **K-Cap Enforcement**: Default 10 item pages per source per run, configurable via `max_item_page_fetches` in DomainProfile

5. **Security Guards**:
   - Content-type validation (only text/html, application/xhtml+xml, application/xml)
   - Cross-domain redirect blocking unless allowlisted
   - Binary content rejection (images, videos, PDFs, etc.)

### raw_json Fields
Items now include:
- `extracted_title`: Title extracted from HTML
- `extracted_date_raw`: Raw date string before parsing
- `extraction_method`: Method used (time_element, meta_published_time, json_ld, text_pattern, none)
- `candidate_dates`: List of all candidate dates found

## Completed Items
- [x] Domain profile models (DomainProfile, LinkExtractionRule, DateExtractionRule)
- [x] Profile registry with thread-safe singleton
- [x] Date extractor with precedence-based extraction
- [x] Item page fetcher with K-cap enforcement
- [x] Extended state machine with new states
- [x] Updated HtmlListCollector with profile integration
- [x] Metrics (html_list_links_total, html_date_recovery_total, html_parse_failures_total)
- [x] Security guards (content-type, cross-domain, binary rejection)
- [x] HTML fixture files for testing
- [x] Unit tests for date extraction, models, registry
- [x] Integration tests with HTML fixtures

## TODOs (Prompt #2)
- [ ] Execute E2E tests following E2E_PLAN.md
- [ ] Validate acceptance criteria
- [ ] Write E2E_RUN_REPORT.md with evidence

## Risks
1. **Date parsing ambiguity**: Some date formats may be ambiguous (e.g., 01/02/2024 could be Jan 2 or Feb 1). Using `dateutil.parser` which defaults to US format.
2. **Profile maintenance**: Domain profiles may need updates as sites change structure. Consider adding version tracking.

## Validation in Verification Environment
To validate this feature:
1. Run `uv run pytest tests/unit/test_collectors/test_html_profile/ -v`
2. Run `uv run pytest tests/integration/test_html_list_collector.py -v`
3. Run full test suite: `uv run pytest`
4. Verify lint/format/typecheck pass: `uv run ruff check . && uv run ruff format --check && uv run mypy .`

## Deployment Information
- **Commit/Tag**: (To be filled after commit)
- **Target Environment**: INT/Verification
- **Deployment Method**: Standard uv-based deployment
- **Configuration Changes**: None required (new feature with sensible defaults)

## Recovery Rate Snapshots
Per-domain recovery rates from E2E run on 2026-01-15.

| Date | Domain | Links Found | Dates Recovered | Recovery Rate |
|------|--------|-------------|-----------------|---------------|
| 2026-01-15 | localhost (time fixture) | 3 | 3 | 100% |
| 2026-01-15 | localhost (meta fixture) | 2 | 2 | 100% |
| 2026-01-15 | localhost (json-ld fixture) | 2 | 2 | 100% |
| 2026-01-15 | localhost (no dates fixture) | 3 | 0 | 0% (expected) |

## E2E Validation Summary
- **E2E Run Date**: 2026-01-15
- **All 10 E2E Scenarios**: PASSED
- **All 3 Acceptance Criteria**: PASSED
- **Tests**: 53 passed (45 unit + 8 integration)
- **Evidence**: See `E2E_RUN_REPORT.md`

## P3 Refactoring Summary (2026-01-15)

### Refactoring Changes
1. **Exception Hierarchy** (`exceptions.py`): Structured domain-specific exceptions
2. **Regex Caching** (`utils.py`): LRU-cached regex compilation for performance
3. **YAML Profile Loading** (`loader.py`): Configuration-driven profile management
4. **Timing Metrics** (`metrics.py`): Phase duration tracking for profiling

### Test Results
- **Unit Tests**: 78 passed, 1 skipped
- **Lint/Format**: All checks passed
- **Type Check**: No issues (html_profile module)

### Evidence
- See `REFACTOR_NOTES.md` for detailed changes and rollback plan

### Guidance for P4
1. Run regression E2E: `uv run pytest tests/integration/test_html_list_collector.py -v`
2. Verify all P2 scenarios still pass
3. Update STATE.md to `READY` on success

## P4 Regression E2E Summary (2026-01-15)

### Regression Test Results
- **Unit Tests**: 78 passed, 1 skipped (up from 53 in P2)
- **Integration Tests**: 8 passed (stable)
- **Lint/Format/Type**: All checks passed
- **Browser Testing**: All 5 fixtures loaded, 0 console errors

### Refactored Component Verification
| Component | Status | Evidence |
|-----------|--------|----------|
| Exception Hierarchy | VERIFIED | Inheritance chain works correctly |
| Regex Caching | VERIFIED | LRU cache hits confirmed |
| YAML Profile Loading | VERIFIED | Dict loading works |
| Timing Metrics | VERIFIED | Singleton available |

### E2E Scenario Regression
All 10 E2E scenarios from P2 continue to pass:
- Scenarios 1-4: Date extraction methods (TIME, META, JSON-LD, NONE)
- Scenario 5: K-Cap enforcement
- Scenario 6: State machine transitions
- Scenario 7: Content-Type security
- Scenario 8: Cross-domain redirect blocking
- Scenario 9: Idempotent parsing
- Scenario 10: Metrics recording

### Acceptance Criteria Regression
- **AC1**: Items emitted with LOW confidence - NO REGRESSION
- **AC2**: K-Cap enforced - NO REGRESSION
- **AC3**: E2E evidence archived - NO REGRESSION

### Evidence
- See `E2E_RUN_REPORT.md` for full regression report
- Screenshot: `e2e_regression_screenshot.png`

---

## Feature Close-Out

**Feature Key**: `add-html-domain-profiles`
**Final Status**: READY
**Completion Date**: 2026-01-15

### Prompt Workflow Summary
| Prompt | Status | Deliverables |
|--------|--------|--------------|
| P1 | DONE_DEPLOYED | Core implementation, tests, documentation |
| P2 | E2E_PASSED | E2E validation, acceptance criteria signed |
| P3 | REFACTORED_DEPLOYED | Exception hierarchy, regex caching, YAML loading, timing metrics |
| P4 | READY | Regression E2E passed, feature closed |

### Final Metrics
- **Total Unit Tests**: 78 (html_profile module)
- **Integration Tests**: 8
- **Code Coverage**: 100% for models, registry, utils, exceptions
- **Lines of Code**: ~600 (new code in html_profile module)
