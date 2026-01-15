# E2E_PLAN.md - End-to-End Validation Plan

## Overview

This document provides browser-executable steps to validate the source status and degradation reporting feature.

## Prerequisites

- [ ] Code is deployed to verification environment
- [ ] Python dependencies installed (`uv sync`)
- [ ] Output directory is writable

## Test Fixtures

### Fixture A: Zero Deltas (NO_UPDATE)
A source that succeeds but has no new items.

### Fixture B: Missing Dates (CANNOT_CONFIRM)
A source that succeeds but all items lack published dates and no stable ordering.

### Fixture C: Fetch Failure (FETCH_FAILED)
A source that times out or returns error.

## E2E Validation Steps

### Step 1: Run Tests
```bash
# Run all status-related tests
uv run pytest tests/unit/test_status/ -v
uv run pytest tests/integration/test_status_rendering.py -v
```
- [ ] All tests pass

### Step 2: Generate Output with Render Command
```bash
uv run python -m src.cli.digest render --out public --tz UTC
```
- [ ] Command completes without error

### Step 3: Validate sources.html in Browser

Open `public/sources.html` in Chrome DevTools:

1. **Console Check**
   - [ ] Open DevTools (F12) → Console tab
   - [ ] Verify: 0 console errors
   - [ ] Verify: 0 console warnings (excluding optional vendor warnings)

2. **Network Check**
   - [ ] Open DevTools → Network tab
   - [ ] Reload page
   - [ ] Verify: 0 failed requests (no red entries)

3. **Visual Verification**
   - [ ] Summary section shows status counts
   - [ ] Sources grouped by category (if categories assigned)
   - [ ] Status badges display correctly:
     - Green for HAS_UPDATE
     - Blue for NO_UPDATE
     - Red for FETCH_FAILED / PARSE_FAILED
     - Yellow for CANNOT_CONFIRM

4. **Content Verification**
   - [ ] Each source row shows: name, tier, method, status, new, updated, details
   - [ ] Remediation hints appear for failed sources
   - [ ] Reason text is human-readable

### Step 4: Validate api/daily.json

Open `public/api/daily.json` and verify:

1. **Structure**
   - [ ] `sources_status` array exists
   - [ ] Each entry has required fields:
     - `source_id`
     - `name`
     - `tier`
     - `method`
     - `status`
     - `reason_code`
     - `reason_text`
     - `items_new`
     - `items_updated`
     - `category`

2. **Values**
   - [ ] `status` values match enum: NO_UPDATE, HAS_UPDATE, FETCH_FAILED, PARSE_FAILED, CANNOT_CONFIRM, STATUS_ONLY
   - [ ] `reason_code` values are stable enum values (all caps with underscores)
   - [ ] `category` values are: intl_labs, cn_ecosystem, platforms, paper_sources, other

3. **Consistency**
   - [ ] Reason codes match status (e.g., FETCH_* for FETCH_FAILED)
   - [ ] items_new and items_updated are non-negative integers

### Step 5: Validate Logs (if running full pipeline)

Check structured logs for:
```
grep "status_computed" logs/run.log
```

- [ ] Each source has a `status_computed` log entry
- [ ] Log includes: source_id, status, reason_code, rule_path

### Step 6: Clear Data E2E Test

```bash
# Clear output directory
rm -rf public/*

# Run with test fixtures (if available)
uv run python -m src.cli.digest render --out public --tz UTC

# Verify outputs
ls -la public/
cat public/api/daily.json | jq '.sources_status | length'
```

- [ ] sources.html generated
- [ ] daily.json contains sources_status
- [ ] Source statuses match expected fixtures

## Acceptance Verification

Cross-reference with ACCEPTANCE.md checklist:

- [ ] System distinguishes NO_UPDATE from CANNOT_CONFIRM and FETCH_FAILED
- [ ] States render consistently in sources.html and api/daily.json
- [ ] reason_code values match documented enum
- [ ] reason_code values are stable across runs for identical fixtures
- [ ] Chrome DevTools: console 0 error AND network 0 failure

## Evidence Collection

After validation, record:
1. Screenshot of sources.html summary section
2. JSON snippet of sources_status from daily.json
3. Log excerpt showing status_computed entries
4. SHA-256 checksum of daily.json

Write findings to `E2E_RUN_REPORT.md`.
