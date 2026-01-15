# ACCEPTANCE.md - add-platform-release-collectors

## Acceptance Criteria Checklist

### AC-1: Platform collectors ingest fixtures with correct canonical URLs and stable IDs
- [x] GitHub releases collector produces items with HTML URL as canonical URL
- [x] HuggingFace org collector produces items with model page URL as canonical URL
- [x] OpenReview venue collector produces items with forum URL as canonical URL
- [x] All items have stable IDs derived from platform identifiers
- [x] No duplicates after two identical runs (verified by content_hash and first_seen_at invariance)

### AC-2: Simulated 401/403 surfaced as source failure with remediation guidance
- [x] 401 response returns source failure with message containing token env var name
- [x] 403 response returns source failure with message containing token env var name
- [x] Other sources continue to complete when one source has auth failure
- [x] Failure is logged with error_class=FETCH and remediation hint

### AC-3: INT clear-data E2E passes and archives evidence
- [x] E2E_RUN_REPORT.md generated with pass/fail status
- [x] STATE.md updated with per-platform summary
- [x] Sampled items included in evidence
- [x] Rate-limit behavior documented
- [x] DB cleared before test run
- [x] Two consecutive runs produce no duplicates

---
**E2E Verification Date:** 2026-01-15
**All Acceptance Criteria: PASSED**
