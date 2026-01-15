# [Feature] add-evidence-capture-and-audit-trail - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-evidence-capture-and-audit-trail
- Feature Name: Add: Evidence capture, audit trail, and archival for INT E2E and daily runs

- Context:
Goal: Make every run verifiable by capturing deterministic artifacts, checksums, and summarized decisions.
Why now: Without archived evidence, regressions in parsing/ranking cannot be diagnosed and INT correctness cannot be proven.
Scope: Evidence paths are standardized under features/<feature_key>/; INT is the source of truth; non-goal is external log aggregation.

- Requirements:
Each feature shall produce two mandatory evidence files per INT E2E: features/<feature_key>/E2E_RUN_REPORT.md and features/<feature_key>/STATE.md.
E2E_RUN_REPORT.md shall include: run_id, git commit SHA, start/end timestamps, cleared-data steps performed, pass/fail, and links to key artifacts.
STATE.md shall include: config hashes, DB stats, per-source counts, and SHA-256 checksums of produced artifacts.
Evidence generation shall be a state machine: EVIDENCE_PENDING -> EVIDENCE_WRITING -> EVIDENCE_DONE; if evidence writing fails, the run must fail.
Idempotency: rerunning the same E2E on the same fixtures shall overwrite evidence files with identical content except timestamp fields, which must be clearly separated.
Replay safety: evidence paths must be deterministic and not depend on wall-clock locale; date formatting must use ISO-8601.
Evidence files shall never include secrets; logs and reports must redact tokens and cookies.
Audit logs shall record the evidence file paths and checksums after writing.
Access control is enforced by repository permissions; no additional RBAC is required for static artifacts.
Artifact manifest shall list all generated public outputs (HTML/JSON) and the state.sqlite checksum for successful runs.
Retention policy shall keep evidence for at least 90 days; pruning must preserve the most recent successful run and the most recent failed run.
Checksum shall use SHA-256 and must be computed over raw bytes of artifacts.
Structured logs shall include: run_id, component=evidence, file_path, bytes_written, sha256, duration_ms.
Metrics shall include: evidence_write_failures_total, evidence_bytes_total.
Tracing shall include a span for evidence writing linked to run completion.
Unit tests shall cover: deterministic report formatting, checksum computation, and redaction rules.
Integration tests shall cover: generating evidence for a full pipeline run and validating required sections exist.
INT E2E shall clear prior evidence directories, run a full pipeline on fixtures, and verify both evidence files exist and include the required manifest/checksums.
Evidence capture shall write 'features/add-evidence-capture-and-audit-trail/E2E_RUN_REPORT.md' and 'features/add-evidence-capture-and-audit-trail/STATE.md' with verifiable checksums.

- Acceptance Criteria:
- On INT, every successful run produces a complete artifact manifest with SHA-256 checksums for HTML, JSON, and state.sqlite.
- On INT, evidence files contain no secret strings matching configured redaction patterns and pass an automated redaction scan.
- INT clear-data E2E passes and archives evidence to features/add-evidence-capture-and-audit-trail/E2E_RUN_REPORT.md and features/add-evidence-capture-and-audit-trail/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-evidence-capture-and-audit-trail/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-evidence-capture-and-audit-trail
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
Create and maintain the following files under `features/add-evidence-capture-and-audit-trail/` (create if missing):
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
