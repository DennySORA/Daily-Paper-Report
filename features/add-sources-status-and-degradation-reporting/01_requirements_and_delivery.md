# [Feature] add-sources-status-and-degradation-reporting - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-sources-status-and-degradation-reporting
- Feature Name: Enhance: Source status classification and explicit degradation reasons in output

- Context:
Goal: Make 'no update' vs 'cannot confirm' vs 'fetch failed' explicit per source and visible in HTML and JSON outputs.
Why now: Some sources are dynamic or intermittently unreachable; without explicit classification, users misinterpret missing updates as 'no updates'.
Scope: INT truth is derived from run logs and persisted run/source status; no client-side inference; non-goal is automatic remediation.

- Requirements:
The system shall compute per-source status for each run: NO_UPDATE, HAS_UPDATE, FETCH_FAILED, PARSE_FAILED, STATUS_ONLY, CANNOT_CONFIRM (e.g., date missing or dynamic content).
Each status shall include a machine-readable reason_code and human-readable reason_text in English, and optional remediation_hint.
The renderer shall present per-source status grouped by category (International labs, CN/Chinese ecosystem, Platforms, Paper sources).
Status computation shall be deterministic: HAS_UPDATE iff at least one NEW or UPDATED item is observed for that source since last success; NO_UPDATE iff fetch+parse succeeded and zero items are NEW/UPDATED.
CANNOT_CONFIRM shall be used only when fetch+parse succeed but published dates are missing for all items and no stable ordering identifier exists; this must be justified with logged diagnostics.
Illegal transitions shall be guarded: a source cannot be marked NO_UPDATE if fetch or parse failed.
The JSON API shall include a per-source status block containing: source_id, name, tier, method, status, reason_code, newest_item_date(optional), last_fetch_status_code(optional).
Audit logs shall record the exact rule path leading to each status (e.g., 'fetch_ok+parse_ok+delta=0 => NO_UPDATE').
Security: status payload must not include response bodies or secrets; only metadata and redacted error summaries.
Per-source status for each run shall be persisted in a run artifact file and referenced by status.html; it shall be archived to 'features/add-sources-status-and-degradation-reporting/STATE.md'.
Retention: keep at least 90 days of per-run status blocks to support historical diagnostics.
Checksum: store SHA-256 of the per-run status JSON in STATE.md.
Structured logs shall include: run_id, component=status, source_id, status, reason_code.
Metrics shall include: sources_failed_total{source_id,reason_code}, sources_cannot_confirm_total{source_id}.
Tracing shall link status computation span to collector spans via run_id.
Unit tests shall cover: status classification rules and illegal transition guards.
Integration tests shall cover: end-to-end from collector results to JSON status blocks and HTML rendering.
INT E2E shall clear DB and output dir, run with fixtures containing: (a) zero deltas, (b) missing dates, (c) fetch failure; verify statuses and reason codes are rendered.
Evidence capture shall write 'features/add-sources-status-and-degradation-reporting/E2E_RUN_REPORT.md' and 'features/add-sources-status-and-degradation-reporting/STATE.md' with source-by-source expected vs actual status.

- Acceptance Criteria:
- On INT, the system distinguishes NO_UPDATE from CANNOT_CONFIRM and FETCH_FAILED, and renders those states consistently in sources.html and api/daily.json.
- On INT, reason_code values match the documented enum and are stable across runs for identical fixtures.
- INT clear-data E2E passes and archives evidence to features/add-sources-status-and-degradation-reporting/E2E_RUN_REPORT.md and features/add-sources-status-and-degradation-reporting/STATE.md.
- Chrome DevTools: console 0 error AND network 0 failure.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-sources-status-and-degradation-reporting/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-sources-status-and-degradation-reporting
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
Create and maintain the following files under `features/add-sources-status-and-degradation-reporting/` (create if missing):
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
