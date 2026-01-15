# [Feature] add-collectors-framework - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-collectors-framework
- Feature Name: Add: Collector framework for RSS/Atom, HTML lists, and platform APIs

- Context:
Goal: Standardize ingestion across heterogeneous sources into a single normalized Item contract.
Why now: Ad-hoc scrapers break when sites change; a framework with typed collectors improves maintainability and QA coverage.
Scope: Collectors must emit Items with canonical URLs and best-effort dates; non-goal is full-text extraction.

- Requirements:
Each collector shall implement a common interface: collect(source_config, http_client, now) -> list[Item] and must populate: source_id, tier, kind, title, url, published_at(optional), date_confidence, raw_json.
Collectors shall normalize URLs to canonical form (strip tracking params, resolve relative URLs, remove fragments) and validate http(s) scheme.
Collectors shall enforce per-source max_items_per_source and return deterministically ordered Items (stable sort by published_at desc then url).
Collector execution shall be a state machine per source: SOURCE_PENDING -> SOURCE_FETCHING -> SOURCE_PARSING -> SOURCE_DONE|SOURCE_FAILED; illegal transitions shall be guarded and logged.
Idempotency: given identical HTTP responses and config, collectors shall output identical Items (stable ordering and stable raw_json normalization).
Concurrency: the runner may execute collectors in parallel up to a configured limit; store writes must remain transactionally safe.
Collector outputs shall never include secrets in raw_json; any Authorization-derived data must be removed.
Error model shall be typed: FetchError, ParseError, SchemaError; errors must be recorded in the run status table and sources status page input.
Audit logs shall include: source_id, method, items_emitted, parse_warnings_count.
All emitted Items shall be upserted into SQLite with first_seen_at/last_seen_at semantics and content_hash computed from normalized fields.
The framework shall emit per-source parse diagnostics and persist them to 'features/add-collectors-framework/STATE.md'.
Retention: raw_json stored in DB must be capped (e.g., 100 KB per item); oversized raw_json must be truncated with a 'raw_truncated=true' marker.
Structured logs shall include: run_id, component=collector, source_id, method, items_emitted, duration_ms, warnings.
Metrics shall include: collector_items_total{source_id,kind}, collector_failures_total{source_id,error_class}, collector_duration_ms{source_id}.
Tracing shall propagate a span per source, linking fetch and parse sub-spans.
Unit tests shall cover: URL canonicalization, stable ordering, max_items_per_source enforcement, and error typing.
Integration tests shall cover: running multiple collectors and upserting into SQLite with deterministic outcomes.
INT E2E shall clear DB and run a fixture set across rss_atom and html_list collectors; verify the per-source state machine completes and items are persisted.
Evidence capture shall write 'features/add-collectors-framework/E2E_RUN_REPORT.md' and 'features/add-collectors-framework/STATE.md' with per-source emitted counts and failure isolation proof.

- Acceptance Criteria:
- On INT, collectors produce deterministic Item lists given the same fixtures (byte-identical JSON exports).
- On INT, a single failing collector does not prevent other collectors from persisting items and producing output.
- INT clear-data E2E passes and archives evidence to features/add-collectors-framework/E2E_RUN_REPORT.md and features/add-collectors-framework/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-collectors-framework/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-collectors-framework
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
Create and maintain the following files under `features/add-collectors-framework/` (create if missing):
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
