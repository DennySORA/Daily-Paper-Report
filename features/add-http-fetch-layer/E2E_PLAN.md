# E2E Plan - add-http-fetch-layer

## Overview

This document provides step-by-step instructions for end-to-end validation of the HTTP fetch layer.

## Prerequisites

1. Python 3.13+ installed
2. `uv` package manager installed
3. Project dependencies synced: `uv sync`

## E2E Test Scenarios

### Scenario 1: Retry Policy Validation (5xx endpoint)

**Objective**: Verify that 5xx errors are retried exactly N times per configuration.

**Steps**:

1. Start local test server with 5xx endpoint:
   ```bash
   uv run python -m tests.fixtures.http_server --port 8765
   ```

2. Configure fetch with max_retries=3

3. Execute fetch against 5xx endpoint:
   ```bash
   uv run pytest tests/integration/test_fetch_retry.py -k test_5xx_retry_count -v
   ```

4. **Expected**:
   - Total attempts = 1 (initial) + 3 (retries) = 4
   - Final result is FETCH_FAILED with error_class=HTTP_5XX
   - Other sources (if any) complete successfully

**Evidence**: Logs showing attempt_count=4, final status recorded in http_cache

---

### Scenario 2: Conditional Requests (304 behavior)

**Objective**: Verify ETag/Last-Modified caching reduces payload by 80%+.

**Steps**:

1. Clear http_cache table:
   ```bash
   uv run python -c "
   from src.store.store import StateStore
   store = StateStore(':memory:')
   store.connect()
   # Clear any existing cache
   "
   ```

2. Start local test server with caching headers:
   ```bash
   uv run python -m tests.fixtures.http_server --port 8765 --with-caching
   ```

3. First fetch (no cache):
   ```bash
   uv run pytest tests/integration/test_fetch_conditional.py -k test_first_fetch -v
   ```
   - **Expected**: Full response body received, ETag/Last-Modified stored

4. Second fetch (with cache):
   ```bash
   uv run pytest tests/integration/test_fetch_conditional.py -k test_second_fetch -v
   ```
   - **Expected**: 304 response, cache_hit=True, no body transferred

5. **Verification**:
   - First fetch bytes > 0
   - Second fetch bytes = 0 (or minimal 304 response)
   - Payload reduction >= 80%

**Evidence**: Metrics showing http_cache_hits_total incremented, bytes comparison in logs

---

### Scenario 3: Header Redaction

**Objective**: Verify Authorization and Cookie headers are never logged.

**Steps**:

1. Run fetch with Authorization header:
   ```bash
   uv run pytest tests/unit/test_fetch/test_header_redaction.py -v
   ```

2. Grep logs for "Authorization" or "Cookie" values:
   ```bash
   # Should find no actual token values in any output
   grep -r "Bearer" logs/ || echo "PASS: No tokens found"
   ```

**Evidence**: Test output showing [REDACTED] in place of sensitive values

---

### Scenario 4: Response Size Limit

**Objective**: Verify responses exceeding 10 MB are rejected.

**Steps**:

1. Start local test server with large response endpoint:
   ```bash
   uv run python -m tests.fixtures.http_server --port 8765 --large-response 15MB
   ```

2. Execute fetch against large endpoint:
   ```bash
   uv run pytest tests/unit/test_fetch/test_response_size.py -v
   ```

**Expected**: FetchError with error_class=RESPONSE_SIZE_EXCEEDED

---

### Scenario 5: Failure Isolation

**Objective**: Verify one source failure does not abort other sources.

**Steps**:

1. Configure multiple sources: one failing (5xx), others healthy

2. Run fetch for all sources with fail_fast=False (default)

3. **Expected**:
   - Failing source recorded as FETCH_FAILED
   - Other sources complete successfully
   - Run continues to completion

---

## Full E2E Run

```bash
# 1. Clear existing data
rm -f state.sqlite
rm -rf features/add-http-fetch-layer/snapshots/

# 2. Run all unit tests
uv run pytest tests/unit/test_fetch/ -v

# 3. Run integration tests
uv run pytest tests/integration/test_fetch_conditional.py -v

# 4. Type check
uv run mypy src/fetch/

# 5. Lint check
uv run ruff check src/fetch/

# 6. Format check
uv run ruff format --check src/fetch/
```

## Success Criteria

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] mypy reports no errors
- [ ] ruff check reports no errors
- [ ] Retry count matches configuration (3 retries + 1 initial)
- [ ] Conditional requests achieve 80%+ payload reduction
- [ ] No sensitive headers in logs
- [ ] Response size limits enforced
- [ ] Failure isolation verified

## Evidence Artifacts

After successful E2E:

1. `E2E_RUN_REPORT.md` - Updated with pass/fail status and timestamps
2. `STATE.md` - Updated with per-source fetch summaries
3. Test output logs
4. Metrics snapshot
