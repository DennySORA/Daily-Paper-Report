# [Feature] add-http-fetch-layer - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-http-fetch-layer
- Feature Name: Add: Robust HTTP fetch layer with caching, retries, and failure isolation

- Context:
Goal: Provide reliable, observable network I/O with ETag/Last-Modified support and deterministic retry behavior.
Why now: Some sources intermittently return 403/5xx; without standard handling, runs become flaky and non-auditable.
Scope: INT is the source of truth; failures must not block unrelated sources; non-goal is headless browser rendering.

- Requirements:
The fetch layer shall implement GET with configurable timeout, max retries, exponential backoff, and optional conditional requests using stored ETag/Last-Modified.
The fetch layer shall enforce a maximum response size threshold (e.g., 10 MB) and fail with a typed error if exceeded.
The fetch layer shall return a typed result: {status_code, final_url, headers, body_bytes, cache_hit(boolean), error(optional)}.
Each source fetch shall be independent; a failure in one source shall not abort the overall run unless a configurable 'fail_fast' flag is enabled (default: false).
Retry policy shall only retry on network timeouts and 5xx; it shall not retry on deterministic 4xx except 429, which shall retry with respect to Retry-After if present.
Idempotency: repeated fetch calls with identical URL and headers shall not mutate http_cache except updating last_fetch_at and last_status.
The fetch layer shall support per-domain headers profiles and a fixed User-Agent string configured in sources.yaml defaults.
Tokens shall be passed via Authorization headers only and must never be logged; logs must redact header values for Authorization and Cookie.
Audit logging shall record: source_id, url, method, attempt_count, cache_hit, status_code, and error_class.
The fetch layer shall persist ETag/Last-Modified and last_status in http_cache for each source_id.
For each run, the system shall write a per-source fetch summary (status_code, cache_hit) into 'features/add-http-fetch-layer/STATE.md'.
Retention: per-source fetch summaries shall retain 30 days and be pruned deterministically.
Structured logs shall include: run_id, component=fetch, source_id, url, status_code, cache_hit, bytes, duration_ms, attempt.
Metrics shall include: http_requests_total{status}, http_cache_hits_total, http_retry_total, http_failures_total{error_class}.
Tracing shall create a span per fetch with tags: source_id, domain, status_code, cache_hit.
Unit tests shall cover: retry policy decisions, 429 handling, header redaction, and response size enforcement.
Integration tests shall use a local HTTP test server to validate ETag/Last-Modified conditional requests and 304 behavior.
INT E2E shall clear http_cache state and run two consecutive fetches against a controlled test endpoint to verify cache headers are stored and reused.
Evidence capture shall write 'features/add-http-fetch-layer/E2E_RUN_REPORT.md' and 'features/add-http-fetch-layer/STATE.md' including request/response headers (redacted) and metrics snapshot.

- Acceptance Criteria:
- On INT, a controlled 5xx endpoint is retried exactly N times per configuration and then recorded as a source failure without aborting other sources.
- On INT, conditional requests reduce payload bytes by at least 80% for unchanged resources in the integration test.
- INT clear-data E2E passes and archives evidence to features/add-http-fetch-layer/E2E_RUN_REPORT.md and features/add-http-fetch-layer/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-http-fetch-layer/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-http-fetch-layer
- STATUS: <one of>
  - P1_DONE_DEPLOYED
  - P2_E2E_PASSED
  - P3_REFACTORED_DEPLOYED
  - READY

Required end status for each prompt:
- Prompt #1 end: STATUS must be `P1_DONE_DEPLOYED`
- Prompt #2 end: STATUS must be `P2_E2E_PASSED`
- Prompt #3 end: STATUS must be `P3_REFACTORED_DEPLOYED`
- Prompt #4 end: STATUS must be `READY`

If you cannot meet the requirement (for example, failed acceptance items remain), keep the previous STATUS and clearly record the reason and next steps in STATE.md.


## Required Artifacts (Must Produce)
Create and maintain the following files under `features/add-http-fetch-layer/` (create if missing):
1) `STATE.md`: Current state (decisions, completed items, TODOs, risks, how to validate in the verification environment; include STATUS field)
2) `E2E_PLAN.md`: Browser-executable end-to-end checklist (steps must be precise)
3) `ACCEPTANCE.md`: Convert acceptance criteria into a checklist
4) `RUNBOOK_VERIFICATION.md`: How to deploy, rollback, and required configuration
5) `CHANGELOG.md`: Feature change summary (reviewer-facing)

## Execution Flow (Strict Order)
1) Structured planning:
   - Review codebase structure, related modules, and current behavior
   - Clarify requirements and boundaries (if missing info, make reasonable assumptions and record in `STATE.md`)
   - Design the solution: data flow, module boundaries, error handling, observability, test strategy
   - Break into minimal deliverable steps (each step should build, test, and be reversible)

2) Implementation:
   - Implement required backend/frontend changes following codebase conventions
   - Add necessary tests (unit/integration; cover key success and failure paths)
   - Ensure lint/format/typecheck/build pass

3) Deploy to the verification environment:
   - Follow the codebase deployment approach
   - Record deployment method, version/commit, and config differences in `RUNBOOK_VERIFICATION.md` and `STATE.md`

4) Wrap-up:
   - Update `E2E_PLAN.md` (so Prompt #2 can follow it directly)
   - Update `STATE.md` and set STATUS to `P1_DONE_DEPLOYED`

## Important Constraints
- Credentials/keys/tokens must not be committed to the codebase. Use environment variables or existing secret mechanisms.

## Final Response Format (Required)
- Summary of work completed (include evidence of verification deployment: version/commit/tag and target location)
- STATE.md status (including STATUS)
- Guidance for Prompt #2 (aligned with `E2E_PLAN.md`)
