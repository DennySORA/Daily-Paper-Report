# [Feature] add-platform-release-collectors - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-platform-release-collectors
- Feature Name: Add: Platform collectors for GitHub releases, Hugging Face org updates, and OpenReview venue monitoring

- Context:
Goal: Capture model/tech-report releases and version iterations from primary distribution platforms with stable identifiers and metadata.
Why now: Platform updates often precede or complement official blogs; they provide canonical weights/model cards and release notes needed for deployment hints.
Scope: Focus on Releases/lastModified/venue submissions; do not crawl arbitrary repo content beyond release metadata and selected files (README/model card) within size limits.

- Requirements:
GitHub releases collector shall monitor configured repos and ingest release tag, published_at, prerelease flag, and release notes URL; canonical URL shall be the release HTML URL.
Hugging Face org collector shall list models for configured orgs and ingest model_id, lastModified, pipeline_tag, license (if present), and model card URL; canonical URL shall be the model page URL.
OpenReview venue collector shall list notes/papers for a given venue_id and ingest paper title, submission date/last update (if available), forum URL, and PDF URL when provided by OpenReview.
Deduplication shall use stable IDs: GitHub release id or URL; HF model_id; OpenReview forum/note id mapped to canonical URL; duplicates across sources shall merge at Story layer.
Idempotency: repeated collection shall not duplicate items; content_hash shall change only when key metadata changes (e.g., release notes updated).
Concurrency: platform collectors may run in parallel; API rate limits shall be enforced via token-bucket with configured max QPS per platform.
API authentication shall use environment tokens; tokens must never be written to raw_json or logs.
Error model shall include explicit handling for 401/403 (auth), 429 (rate limit), and 5xx; 401/403 shall mark the source as failed with a clear remediation hint.
Audit logs shall include: platform, org/repo/venue_id, request_count, rate_limit_remaining (if provided), items_emitted.
For models/releases, the system shall optionally fetch a small set of referenced documents (model card/README) within a strict size cap (e.g., 200 KB) and store only extracted fields in raw_json.
The feature shall record a per-platform summary to 'features/add-platform-release-collectors/STATE.md' including counts by org/repo/venue.
Retention: keep at least 180 days of platform items; pruning must preserve items referenced by HTML archives.
Structured logs shall include: run_id, component=platform, platform, source_id, items_emitted, api_calls, rate_limited(boolean).
Metrics shall include: github_api_calls_total, hf_api_calls_total, openreview_api_calls_total, platform_rate_limit_events_total.
Tracing shall annotate spans with platform and resource identifiers (repo/org/venue).
Unit tests shall cover: ID extraction, pagination handling, and content_hash change detection for updated release notes/model cards.
Integration tests shall simulate paginated API responses and rate limiting to verify token-bucket enforcement.
INT E2E shall clear DB and run fixture collectors for at least one GitHub repo, one HF org, and one OpenReview venue; verify stable dedupe and delta detection since last successful run.
Evidence capture shall write 'features/add-platform-release-collectors/E2E_RUN_REPORT.md' and 'features/add-platform-release-collectors/STATE.md' including sampled items and rate-limit behavior.

- Acceptance Criteria:
- On INT, platform collectors ingest fixtures with correct canonical URLs and stable IDs, and no duplicates after two identical runs.
- On INT, a simulated 401/403 is surfaced as a source failure with remediation guidance while other sources still complete.
- INT clear-data E2E passes and archives evidence to features/add-platform-release-collectors/E2E_RUN_REPORT.md and features/add-platform-release-collectors/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
Use GITHUB_TOKEN for GitHub API; set HF_TOKEN for Hugging Face if rate-limited; set OPENREVIEW_TOKEN if required by venue policy.


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-platform-release-collectors/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-platform-release-collectors
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
Create and maintain the following files under `features/add-platform-release-collectors/` (create if missing):
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
