# E2E Test Plan: add-html-domain-profiles

## Overview
This plan covers end-to-end testing of the HTML domain profiles feature, verifying that html_list collectors can parse list pages, extract dates with proper precedence, and recover dates from item pages within K-cap limits.

## Pre-requisites
1. All unit tests passing: `uv run pytest tests/unit/test_collectors/test_html_profile/`
2. All integration tests passing: `uv run pytest tests/integration/test_html_list_collector.py`
3. Lint/format/typecheck passing: `uv run ruff check . && uv run ruff format --check && uv run mypy .`

---

## Test Scenarios

### Scenario 1: Date Extraction Precedence
**Goal**: Verify date extraction follows the correct precedence order.

**Steps**:
1. Use the fixture `blog_list_with_time.html` containing `<time datetime>` elements
2. Run the collector and verify:
   - [ ] All items have `published_at` set
   - [ ] All items have `date_confidence=HIGH`
   - [ ] Items are sorted by date descending (newest first)
   - [ ] `raw_json` contains `extraction_method=time_element`

**Expected Result**: All 3 items extracted with HIGH confidence dates from `<time>` elements.

---

### Scenario 2: Meta Tag Date Extraction
**Goal**: Verify date extraction from `<meta property="article:published_time">`.

**Steps**:
1. Use the fixture `blog_list_with_meta.html`
2. Run the collector and verify:
   - [ ] All items have `published_at` set
   - [ ] All items have `date_confidence=HIGH`
   - [ ] `raw_json` contains `extraction_method=meta_published_time`

**Expected Result**: All 2 items extracted with HIGH confidence dates from meta tags.

---

### Scenario 3: JSON-LD Date Extraction
**Goal**: Verify date extraction from JSON-LD `datePublished`.

**Steps**:
1. Use the fixture `blog_list_with_json_ld.html`
2. Run the collector and verify:
   - [ ] All items have `published_at` set
   - [ ] All items have `date_confidence=HIGH`
   - [ ] `raw_json` contains `extraction_method=json_ld`

**Expected Result**: All 2 items extracted with HIGH confidence dates from JSON-LD.

---

### Scenario 4: Low Confidence When No Date Found
**Goal**: Verify items without dates are marked with LOW confidence.

**Steps**:
1. Use the fixture `blog_list_no_dates.html`
2. Disable item page recovery in profile
3. Run the collector and verify:
   - [ ] All items have `published_at=NULL`
   - [ ] All items have `date_confidence=LOW`
   - [ ] `raw_json` contains `extraction_method=none`

**Expected Result**: All 3 items extracted with NULL dates and LOW confidence.

---

### Scenario 5: K-Cap Enforcement
**Goal**: Verify item page recovery respects max_item_page_fetches limit.

**Steps**:
1. Create HTML with 20 items without dates
2. Set profile `max_item_page_fetches=5`
3. Enable item page recovery
4. Run the collector and verify:
   - [ ] List page fetched successfully
   - [ ] Exactly 5 item pages fetched (not more)
   - [ ] Up to 5 items have dates recovered
   - [ ] Remaining items still have `date_confidence=LOW`
   - [ ] Logs show `item_pages_fetched=5`

**Expected Result**: Only 5 item pages fetched despite 20 items needing recovery.

---

### Scenario 6: State Machine Transitions
**Goal**: Verify illegal transition guard.

**Steps**:
1. Create a test that attempts to transition directly from `SOURCE_FETCHING` to `SOURCE_PARSING_ITEM_PAGES`
2. Verify:
   - [ ] `SourceStateTransitionError` is raised
   - [ ] Cannot enter `PARSING_ITEM_PAGES` without first completing `PARSING_LIST`

**Expected Result**: State machine enforces valid transitions.

---

### Scenario 7: Content-Type Security Guard
**Goal**: Verify binary content types are rejected.

**Steps**:
1. Mock HTTP response with `Content-Type: image/png`
2. Run the collector and verify:
   - [ ] Collection fails with `SOURCE_FAILED` state
   - [ ] Error message contains "Content-Type not allowed"
   - [ ] No items emitted

**Expected Result**: Binary content types are rejected.

---

### Scenario 8: Cross-Domain Redirect Blocking
**Goal**: Verify cross-domain redirects are blocked unless allowlisted.

**Steps**:
1. Create profile for `example.com` without `allowed_redirect_domains`
2. Attempt to fetch item page that redirects to `malicious.com`
3. Verify:
   - [ ] Item page fetch fails
   - [ ] Error contains "Cross-domain fetch blocked"
   - [ ] Main collection succeeds (item page failure doesn't invalidate list)

**Expected Result**: Cross-domain redirects blocked, list results preserved.

---

### Scenario 9: Idempotent Parsing
**Goal**: Verify parsing produces stable, deterministic output.

**Steps**:
1. Run collector 3 times with same input
2. Compare output items
3. Verify:
   - [ ] Same items extracted each time
   - [ ] Same order each time
   - [ ] Same `content_hash` values

**Expected Result**: Parsing is idempotent.

---

### Scenario 10: Metrics Recording
**Goal**: Verify metrics are recorded correctly.

**Steps**:
1. Run collector with fixture
2. Check metrics via `HtmlProfileMetrics.get_instance()`
3. Verify:
   - [ ] `html_list_links_total{domain}` > 0
   - [ ] `html_date_recovery_total{domain}` matches recovered count
   - [ ] Prometheus format export works

**Expected Result**: All metrics recorded correctly.

---

## Execution Commands

```bash
# Run unit tests
uv run pytest tests/unit/test_collectors/test_html_profile/ -v

# Run integration tests
uv run pytest tests/integration/test_html_list_collector.py -v

# Run all tests
uv run pytest -v

# Check lint/format/types
uv run ruff check .
uv run ruff format --check
uv run mypy .
```

---

## Evidence Capture

After running E2E tests, capture:
1. Test output logs
2. Metrics snapshot
3. Per-domain recovery rates
4. Any failures with root cause

Write results to:
- `features/add-html-domain-profiles/E2E_RUN_REPORT.md`
- Update `features/add-html-domain-profiles/STATE.md` with recovery rate snapshots
