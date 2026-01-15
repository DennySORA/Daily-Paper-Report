# ACCEPTANCE.md - Acceptance Criteria Checklist

## Feature: add-sources-status-and-degradation-reporting

## Acceptance Criteria

### AC1: Status Distinction
- [ ] On INT, the system distinguishes NO_UPDATE from CANNOT_CONFIRM and FETCH_FAILED
- [ ] Verification: Check sources.html displays different badges for each status
- [ ] Verification: Check api/daily.json has distinct status values per source

### AC2: Consistent Rendering
- [ ] States render consistently in sources.html and api/daily.json
- [ ] Verification: Compare status in HTML badge with status in JSON
- [ ] Verification: Verify same source shows same status in both outputs

### AC3: Reason Code Stability
- [ ] reason_code values match the documented enum in `src/status/models.py`
- [ ] Verification: Cross-check JSON reason_code values against ReasonCode enum
- [ ] Verification: Values are all uppercase with underscores (e.g., FETCH_PARSE_OK_HAS_NEW)

### AC4: Reason Code Consistency
- [ ] reason_code values are stable across runs for identical fixtures
- [ ] Verification: Run twice with same input, compare reason_code values
- [ ] Verification: No randomization or timestamp-dependent codes

### AC5: Browser Validation
- [ ] Chrome DevTools: console 0 error
- [ ] Chrome DevTools: network 0 failure
- [ ] Verification: Open sources.html in Chrome, check DevTools console and network tabs

### AC6: E2E Evidence
- [ ] INT clear-data E2E passes
- [ ] Evidence archived to features/add-sources-status-and-degradation-reporting/E2E_RUN_REPORT.md
- [ ] Evidence archived to features/add-sources-status-and-degradation-reporting/STATE.md

## Per-Source Status Requirements

### Status Computation Rules
- [ ] HAS_UPDATE iff at least one NEW or UPDATED item observed
- [ ] NO_UPDATE iff fetch+parse succeeded and zero items are NEW/UPDATED
- [ ] CANNOT_CONFIRM only when fetch+parse succeed but dates missing and no stable ordering
- [ ] FETCH_FAILED when HTTP fetch fails
- [ ] PARSE_FAILED when parsing fails after successful fetch
- [ ] STATUS_ONLY for status-only method sources

### Illegal Transition Guards
- [ ] Source cannot be marked NO_UPDATE if fetch failed
- [ ] Source cannot be marked NO_UPDATE if parse failed

### Required Fields in JSON
- [ ] source_id (string)
- [ ] name (string)
- [ ] tier (integer 0-2)
- [ ] method (string)
- [ ] status (enum string)
- [ ] reason_code (enum string)
- [ ] reason_text (human-readable string)
- [ ] remediation_hint (optional string)
- [ ] newest_item_date (optional ISO timestamp)
- [ ] last_fetch_status_code (optional integer)
- [ ] items_new (integer)
- [ ] items_updated (integer)
- [ ] category (string)

### Audit Logging
- [ ] Logs record rule path for each status decision
- [ ] Log includes: run_id, component=status, source_id, status, reason_code

### Metrics
- [ ] sources_failed_total{source_id, reason_code} counter available
- [ ] sources_cannot_confirm_total{source_id} counter available

## Testing Requirements

### Unit Tests
- [ ] Status classification rules covered
- [ ] Illegal transition guards covered

### Integration Tests
- [ ] End-to-end from collector results to JSON status blocks
- [ ] End-to-end from JSON to HTML rendering

### E2E Tests
- [ ] Fixture A: zero deltas → NO_UPDATE
- [ ] Fixture B: missing dates → CANNOT_CONFIRM
- [ ] Fixture C: fetch failure → FETCH_FAILED
- [ ] Statuses and reason codes verified in output

## Sign-off

| Criterion | Status | Verified By | Date |
|-----------|--------|-------------|------|
| AC1 | [ ] | | |
| AC2 | [ ] | | |
| AC3 | [ ] | | |
| AC4 | [ ] | | |
| AC5 | [ ] | | |
| AC6 | [ ] | | |

---

*Complete this checklist during E2E validation (Prompt #2)*
