# Acceptance Criteria - add-http-fetch-layer

## Checklist

### AC1: 5xx Retry Behavior
- [x] Controlled 5xx endpoint is retried exactly N times per configuration
- [x] After max retries, recorded as source failure
- [x] Other sources continue and complete (failure isolation)
- [x] Retry attempts logged with attempt_count

**Evidence**: Integration test `test_5xx_exhausts_retries` shows retry_attempt logs with attempt=1, attempt=2, final error_class=HTTP_5XX. Test `test_one_source_failure_does_not_block_others` confirms failure isolation.

### AC2: Conditional Request Optimization
- [x] ETag header stored in http_cache after first fetch
- [x] Last-Modified header stored in http_cache after first fetch
- [x] Second fetch includes If-None-Match header
- [x] Second fetch includes If-Modified-Since header
- [x] 304 response correctly interpreted as cache hit
- [x] Payload bytes reduced by at least 80% on cache hit

**Evidence**: Integration test `test_payload_reduction_80_percent` shows:
- First fetch: bytes=36, cache_hit=False, status_code=200
- Second fetch: bytes=0, cache_hit=True, status_code=304
- Payload reduction: 100% (36 -> 0 bytes)

### AC3: E2E Evidence Capture
- [x] `features/add-http-fetch-layer/E2E_RUN_REPORT.md` created with pass/fail
- [x] `features/add-http-fetch-layer/STATE.md` updated with fetch summaries
- [x] Request/response headers included (redacted)
- [x] Metrics snapshot included

**Evidence**: All artifacts generated with E2E results, metrics snapshot, and per-source fetch summaries.

## Detailed Requirements Verification

### Scope and Contracts

| Requirement | Status | Evidence |
|-------------|--------|----------|
| GET with configurable timeout | [x] | FetchConfig.default_timeout_seconds, integration tests |
| Max retries with exponential backoff | [x] | RetryPolicy model, test_exponential_backoff, test_max_delay_cap |
| Conditional requests (ETag/Last-Modified) | [x] | test_first_fetch_stores_cache_headers, test_second_fetch_gets_304 |
| Max response size (10 MB) | [x] | test_default_max_size, test_size_exceeded_error_not_retryable |
| Typed result: status_code, final_url, headers, body_bytes, cache_hit, error | [x] | FetchResult model in models.py |

### Execution Semantics

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Independent source fetches | [x] | test_one_source_failure_does_not_block_others |
| Failure isolation | [x] | fail_fast=False default, integration test |
| Retry on network timeout | [x] | test_retry_on_network_timeout |
| Retry on 5xx | [x] | test_retry_on_5xx, test_retry_on_503 |
| Retry on 429 with Retry-After | [x] | test_retry_on_429_rate_limited, test_429_retried_with_retry_after |
| No retry on 4xx (except 429) | [x] | test_no_retry_on_4xx (7 status codes tested) |
| Idempotent cache updates | [x] | _update_cache preserves existing etag/last_modified on 304 |

### APIs and Security

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Per-domain header profiles | [x] | DomainProfile model, get_headers_for_domain() |
| Fixed User-Agent from config | [x] | FetchConfig.user_agent, _build_headers() |
| Authorization headers never logged | [x] | 36 header redaction tests, REDACTED_VALUE constant |
| Cookie headers never logged | [x] | test_redacts_cookie, test_redacts_set_cookie |
| Audit logging fields | [x] | fetch_complete log with source_id, url, status_code, etc. |

### Storage and Artifacts

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Persist ETag in http_cache | [x] | test_first_fetch_stores_cache_headers |
| Persist Last-Modified in http_cache | [x] | HttpCacheEntry.last_modified field |
| Persist last_status in http_cache | [x] | HttpCacheEntry.last_status field |
| Per-source fetch summary in STATE.md | [x] | E2E run logs captured |
| 30-day retention | [x] | Pruning logic inherited from StateStore |

### Observability

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Structured logs with run_id | [x] | All fetch logs include run_id field |
| Structured logs with component=fetch | [x] | All fetch logs include component=fetch |
| Structured logs with source_id, url, status_code, cache_hit, bytes, duration_ms, attempt | [x] | fetch_complete log format verified |
| Metrics: http_requests_total | [x] | FetchMetrics.http_requests_total dict |
| Metrics: http_cache_hits_total | [x] | FetchMetrics.http_cache_hits_total |
| Metrics: http_retry_total | [x] | FetchMetrics.http_retry_total |
| Metrics: http_failures_total | [x] | FetchMetrics.http_failures_total dict |

### Tests

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Unit test: retry policy decisions | [x] | test_retry_policy.py (20 tests) |
| Unit test: 429 handling | [x] | test_retry_on_429_rate_limited |
| Unit test: header redaction | [x] | test_header_redaction.py (36 tests) |
| Unit test: response size enforcement | [x] | test_response_size.py (17 tests) |
| Integration test: ETag/Last-Modified | [x] | test_fetch_conditional.py (4 conditional tests) |
| Integration test: 304 behavior | [x] | test_second_fetch_gets_304 |

## Sign-off

- [x] All acceptance criteria verified
- [x] Evidence artifacts generated
- [x] Ready for STATUS: P2_E2E_PASSED

## Regression Verification (Prompt #4)

- [x] All 289 tests pass after refactoring
- [x] No regressions in AC1 (5xx Retry Behavior)
- [x] No regressions in AC2 (Conditional Request Optimization)
- [x] No regressions in AC3 (E2E Evidence Capture)
- [x] Quality checks pass (ruff, mypy)
- [x] Ready for STATUS: READY
