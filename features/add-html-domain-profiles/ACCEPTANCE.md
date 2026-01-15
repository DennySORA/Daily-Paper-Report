# Acceptance Criteria Checklist: add-html-domain-profiles

## From Requirements

### AC1: Items emitted even when date recovery fails
- [x] On INT, html_list parsing emits items even when item-page date recovery fails
- [x] Items with failed date recovery are marked `date_confidence=low`

**Verification**:
```python
# In test: Create items without dates, mock item page fetches to fail
# Verify: Items are still returned, just with LOW confidence
```

### AC2: Item page fetch count never exceeds K-cap
- [x] On INT, item-page fetch count never exceeds the configured per-source cap
- [x] Proven by logs showing `item_pages_fetched <= max_item_page_fetches`
- [x] Proven by metrics showing bounded fetch counts

**Verification**:
```python
# In test: 20 items need recovery, K-cap=5
# Verify: Only 5 item pages fetched
```

### AC3: E2E passes and archives evidence
- [x] INT clear-data E2E passes
- [x] Evidence archived to `features/add-html-domain-profiles/E2E_RUN_REPORT.md`
- [x] Evidence archived to `features/add-html-domain-profiles/STATE.md`

**Verification**:
```bash
uv run pytest tests/integration/test_html_list_collector.py -v
# Capture output and write to E2E_RUN_REPORT.md
```

---

## Detailed Requirements Checklist

### Domain Profile System
- [x] Each profile defines: list_url_patterns, link_extraction_rules, date_extraction_rules, canonical URL normalization rules
- [x] Profiles stored in `DomainProfile` Pydantic model
- [x] Profile registry provides lookup by domain or URL

### Date Extraction
- [x] Best-effort published_at extraction from:
  - [x] `<time datetime>`
  - [x] `meta[property='article:published_time']`
  - [x] JSON-LD `Article.datePublished`
- [x] If none found: `published_at=NULL`, `date_confidence=low`

### K-Cap Enforcement
- [x] Maximum K item pages fetched per source per run
- [x] Default K=10, configurable via `max_item_page_fetches`
- [x] Bound latency by limiting item page fetches

### Execution Flow
- [x] First parse list page links
- [x] Then optionally fetch item pages for date recovery
- [x] Failures in item-page fetching do not invalidate list-page results

### Idempotency
- [x] Given identical HTML content, extracted items and ordering must be stable
- [x] Sorting: published_at DESC (nulls last), then URL ASC

### State Machine Guard
- [x] Source cannot enter `SOURCE_PARSING_ITEM_PAGES` unless `SOURCE_PARSING_LIST` has succeeded
- [x] Illegal transitions raise `SourceStateTransitionError`

### Security
- [x] HTML parsing does not execute JavaScript (using BeautifulSoup)
- [x] Never follow cross-domain redirects unless explicitly allowlisted
- [x] Forbid downloading binary assets (images/videos)
- [x] Only text/html and application/xml responses allowed

### Audit Logs
- [x] Logs include: domain, links_found, links_filtered_out, item_pages_fetched, date_recovered_count
- [x] Structured logs include: run_id, component=html_profile, source_id, domain, stage=list|item, duration_ms

### Metrics
- [x] `html_list_links_total{domain}` - Total links found
- [x] `html_date_recovery_total{domain}` - Dates recovered from item pages
- [x] `html_parse_failures_total{domain}` - Parse failures

### raw_json
- [x] Includes: extracted_title
- [x] Includes: extracted_date_raw
- [x] Includes: extraction_method
- [x] Includes: candidate_dates (list of all candidates attempted)

### Profile Execution Report
- [x] Persist to `features/add-html-domain-profiles/STATE.md`
- [x] Include per-domain recovery rates
- [ ] Keep 30 days of snapshots (tracking not implemented in P1)

### Tests
- [x] Unit tests: date extraction precedence, JSON-LD parsing, canonical URL normalization
- [x] Integration tests: profile parsing over stored HTML fixtures
- [x] E2E: clear DB and run html_list collectors with fixtures for at least 3 domains

---

## Sign-off

| Criterion | Status | Evidence |
|-----------|--------|----------|
| AC1: Items emitted with LOW confidence | **PASSED** | See E2E_RUN_REPORT.md - Scenario 4 |
| AC2: K-cap enforced | **PASSED** | See E2E_RUN_REPORT.md - Scenario 5 |
| AC3: E2E passes with evidence | **PASSED** | See E2E_RUN_REPORT.md - All 10 scenarios |

**Sign-off Date**: 2026-01-15
**Verified By**: Claude Code (E2E Automation)
