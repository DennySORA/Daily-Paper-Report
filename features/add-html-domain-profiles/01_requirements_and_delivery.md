# [Feature] add-html-domain-profiles - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-html-domain-profiles
- Feature Name: Add: Domain profiles for stable HTML list and article parsing

- Context:
Goal: Provide resilient, minimal-maintenance HTML parsing for official blogs/news pages when RSS/API are unavailable.
Why now: Several key sources are dynamic or lack feeds; naive selectors break frequently, reducing daily correctness.
Scope: Parse list pages for item links and best-effort dates; for missing dates, fall back to item page metadata (JSON-LD/meta) within caps; do not use headless browsers by default.

- Requirements:
Each domain profile shall define: list_url_patterns, link_extraction_rules, date_extraction_rules (list-level and item-level), and canonical URL normalization rules.
Profiles shall support best-effort published_at extraction from: <time datetime>, meta[property='article:published_time'], JSON-LD Article.datePublished; if none found, set published_at=NULL and date_confidence=low.
Profiles shall enforce a maximum of K item pages fetched per source per run (e.g., 10) for item-level date recovery to bound latency.
For html_list sources, execution shall first parse list page links; only then optionally fetch item pages for date recovery; failures in item-page fetching shall not invalidate list-page results.
Idempotency: given identical HTML content, the extracted items and their ordering must be stable.
Illegal transition guard: a source cannot enter SOURCE_PARSING_ITEM_PAGES unless SOURCE_PARSING_LIST has succeeded.
HTML parsing shall not execute JavaScript; it shall never follow cross-domain redirects to unknown domains unless explicitly allowlisted per profile.
Audit logs shall include: domain, links_found, links_filtered_out, item_pages_fetched, and date_recovered_count.
Security: forbid downloading binary assets (images/videos); only text/html and application/xml responses are allowed.
raw_json for html_list items shall include: extracted_title, extracted_date_raw, extraction_method, and a list of candidate dates attempted.
The feature shall persist a profile execution report to 'features/add-html-domain-profiles/STATE.md' including per-domain recovery rates.
Retention: keep at least 30 days of per-domain recovery rate snapshots to detect regressions.
Structured logs shall include: run_id, component=html_profile, source_id, domain, stage=list|item, duration_ms, recovered_dates.
Metrics shall include: html_list_links_total{domain}, html_date_recovery_total{domain}, html_parse_failures_total{domain}.
Tracing shall create spans for list parsing and for each item-page fetch (when enabled).
Unit tests shall cover: date extraction precedence, JSON-LD parsing, and canonical URL normalization.
Integration tests shall run profile parsing over stored HTML fixtures for representative domains and validate stable outputs.
INT E2E shall clear DB and run html_list collectors with fixtures for at least three domains; verify date recovery bounds (K max item pages) and correct low-confidence labeling.
Evidence capture shall write 'features/add-html-domain-profiles/E2E_RUN_REPORT.md' and 'features/add-html-domain-profiles/STATE.md' with domain-by-domain results.

- Acceptance Criteria:
- On INT, html_list parsing emits items even when item-page date recovery fails, and marks date_confidence=low when required.
- On INT, item-page fetch count never exceeds the configured per-source cap, proven by logs and metrics.
- INT clear-data E2E passes and archives evidence to features/add-html-domain-profiles/E2E_RUN_REPORT.md and features/add-html-domain-profiles/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-html-domain-profiles/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-html-domain-profiles
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
Create and maintain the following files under `features/add-html-domain-profiles/` (create if missing):
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
