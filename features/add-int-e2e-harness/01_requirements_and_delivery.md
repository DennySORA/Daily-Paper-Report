# [Feature] add-int-e2e-harness - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-int-e2e-harness
- Feature Name: Add: INT E2E harness with clear-data prerequisites and deterministic fixtures

- Context:
Goal: Provide a repeatable INT end-to-end test workflow that starts from cleared data and proves correctness via archived evidence.
Why now: Complex multi-source ingestion requires regression protection; unit tests alone cannot validate cross-component determinism.
Scope: INT harness runs locally and in CI; fixtures emulate source payloads; non-goal is live network E2E against production sites.

- Requirements:
The harness shall define deterministic fixtures for RSS/Atom, arXiv API Atom, GitHub releases JSON, Hugging Face model list JSON, OpenReview responses, and representative HTML list pages.
The harness shall provide a clear-data step that deletes/empties: SQLite state, output directory, and any cached HTTP headers for the run.
The harness shall validate outputs against schemas: SQLite schema version, daily.json schema, and required HTML file presence.
The harness shall implement a test-run state machine: CLEAR_DATA -> RUN_PIPELINE -> VALIDATE_DB -> VALIDATE_JSON -> VALIDATE_HTML -> ARCHIVE_EVIDENCE -> DONE; failures halt and archive partial evidence.
Idempotency: running the harness twice with the same fixtures must produce byte-identical daily.json and stable Story ordering.
Concurrency: the harness shall run collectors with parallelism set to 1 by default to reduce nondeterminism; a separate test may validate parallel mode determinism.
The harness shall run without external credentials by default, using fixture-backed HTTP responses; secrets must be optional.
Audit logs shall record fixture versions and fixture file checksums.
Security: the harness shall forbid outbound network access during fixture-backed runs (e.g., via a denylist or mock transport).
The harness shall store E2E artifacts under a predictable directory per feature and include a manifest with checksums.
Retention: keep the last 30 E2E runs for debugging; prune deterministically.
The harness shall capture a DB export (row counts by table) as part of STATE.md.
Structured logs shall include: run_id, component=e2e, step, status, duration_ms.
Metrics shall include: e2e_runs_total, e2e_failures_total{step}.
Tracing shall include spans per E2E step, linked to pipeline spans via run_id.
Unit tests shall cover: fixture loaders, mock transport, and JSON schema validation.
Integration tests shall cover: pipeline execution with fixtures and verification of the four digest sections (Top 5, model releases, papers, radar).
INT E2E steps must start with clearing data and must record the clear-data evidence explicitly in the report.
Evidence capture shall write 'features/add-int-e2e-harness/E2E_RUN_REPORT.md' and 'features/add-int-e2e-harness/STATE.md' including fixture checksums and output checksums.

- Acceptance Criteria:
- On INT, the harness enforces clear-data prerequisites and fails if any prior state is detected before CLEAR_DATA completes.
- On INT, two consecutive harness runs with identical fixtures produce byte-identical api/daily.json and stable HTML checksums.
- INT clear-data E2E passes and archives evidence to features/add-int-e2e-harness/E2E_RUN_REPORT.md and features/add-int-e2e-harness/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-int-e2e-harness/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-int-e2e-harness
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
Create and maintain the following files under `features/add-int-e2e-harness/` (create if missing):
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
