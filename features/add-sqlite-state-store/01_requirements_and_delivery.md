# [Feature] add-sqlite-state-store - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-sqlite-state-store
- Feature Name: Add: SQLite state store for items, runs, and HTTP cache headers

- Context:
Goal: Enable precise delta detection ('since last successful run') and replay-safe ingestion across all sources.
Why now: Without persisted state, daily outputs depend on unstable page ordering and cannot guarantee correctness across runs.
Scope: SQLite is the only required persistence for INT; schema migrations must be deterministic; non-goal is multi-tenant support.

- Requirements:
The system shall implement a SQLite schema with tables: runs(run_id, started_at, finished_at, success, error_summary), http_cache(source_id, etag, last_modified, last_status, last_fetch_at), items(url PK, source_id, tier, kind, title, published_at nullable, date_confidence, content_hash, raw_json, first_seen_at, last_seen_at).
The items.url shall be canonicalized and treated as the unique primary key; canonicalization must strip known tracking params per topics.yaml and normalize fragments.
Date confidence shall be one of {high, medium, low}; if published_at is missing, date_confidence must be low and published_at must be NULL.
Run lifecycle shall be a state machine: RUN_STARTED -> RUN_COLLECTING -> RUN_RENDERING -> RUN_FINISHED_SUCCESS|RUN_FINISHED_FAILURE; illegal transitions shall raise and be logged as invariant violations.
Item ingestion shall be idempotent: upserting the same canonical URL with identical content_hash shall not change first_seen_at; it shall update last_seen_at only.
Update detection shall be supported: if canonical URL exists and content_hash differs, the system shall update raw_json/content_hash and record an UPDATED event for ranking.
The store layer shall provide transactional APIs: begin_run(), end_run(success), upsert_item(), get_last_successful_run_finished_at(), get_items_since(timestamp), upsert_http_cache_headers().
The store shall not store secrets; raw_json must exclude authorization headers and tokens.
Audit logs shall record DB path, schema version, and migration steps applied.
SQLite shall use WAL mode for reliability; migrations shall be applied with explicit versioning and rollback scripts for the previous version.
Retention: items shall retain at least 180 days of first_seen_at history; runs shall retain at least 90 days; pruning shall be deterministic and logged.
The feature shall archive a DB summary to 'features/add-sqlite-state-store/STATE.md' including row counts and last_success timestamp.
Structured logs shall include: run_id, component=store, tx_id, op=upsert_item|get_items_since, affected_rows, duration_ms.
Metrics shall include: db_upserts_total, db_updates_total, db_tx_duration_ms, last_success_age_seconds.
Tracing shall annotate DB operations with spans tagged by source_id.
Unit tests shall cover: canonical URL uniqueness, first_seen_at invariants, update detection, and migration idempotency.
Integration tests shall cover: a full run lifecycle writing RUN_STARTED then RUN_FINISHED_SUCCESS and retrieving last_success timestamp.
INT E2E shall clear the SQLite file and any prior evidence, run a deterministic ingestion of fixture items twice, and verify no duplicate items and stable first_seen_at.
Evidence capture shall write 'features/add-sqlite-state-store/E2E_RUN_REPORT.md' and 'features/add-sqlite-state-store/STATE.md' with DB stats and queries executed.

- Acceptance Criteria:
- On INT, two consecutive runs ingesting identical fixtures produce exactly the same item count and do not modify first_seen_at for existing URLs.
- On INT, content_hash changes for an existing canonical URL are recorded as UPDATED and reflected in the run summary.
- INT clear-data E2E passes and archives evidence to features/add-sqlite-state-store/E2E_RUN_REPORT.md and features/add-sqlite-state-store/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-sqlite-state-store/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-sqlite-state-store
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
Create and maintain the following files under `features/add-sqlite-state-store/` (create if missing):
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
