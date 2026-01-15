# [Feature] add-github-actions-pages-and-state-branch - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-github-actions-pages-and-state-branch
- Feature Name: Add: GitHub Actions schedule, state branch persistence, and GitHub Pages deployment

- Context:
Goal: Execute the pipeline daily in INT and publish the static site via GitHub Pages while persisting SQLite state across runs.
Why now: Local runs are not a reliable operational mechanism; scheduled automation ensures consistent coverage and audit history.
Scope: Use a dedicated 'state' branch for state.sqlite and Pages artifacts from 'public/'; INT is the source of truth; non-goal is multi-environment promotion.

- Requirements:
The workflow shall run on a fixed UTC cron corresponding to Asia/Taipei 07:00 and also support manual workflow_dispatch.
The workflow shall check out the main branch code and best-effort check out the 'state' branch to restore state.sqlite; missing state branch must not fail the first run.
The workflow shall produce a Pages artifact from 'public/' and deploy using official GitHub Pages actions.
The workflow shall be idempotent: rerunning the same commit with the same state.sqlite must produce identical outputs and not duplicate DB items.
State persistence shall be guarded: only commit state.sqlite if the run reaches RUN_FINISHED_SUCCESS; failed runs shall not overwrite state.sqlite.
Concurrency shall be controlled via a single group to prevent overlapping deployments; overlapping runs must be prevented or serialized.
The workflow shall follow least privilege: contents:write only for pushing state branch, pages:write for deployment, id-token:write for Pages deployment.
Secrets shall be optional and referenced only via env vars; logs must not echo secrets; shell steps must avoid 'set -x'.
Audit logs shall include workflow run ID, commit SHA, and artifact checksums for public outputs.
The workflow shall archive run evidence under 'features/add-github-actions-pages-and-state-branch/' in the repository (or as build artifacts) including E2E_RUN_REPORT.md and STATE.md.
Retention: keep Pages artifacts per GitHub default, and keep state branch history for at least 90 days; older history may be squashed only with explicit operator action.
Checksum: store SHA-256 of state.sqlite and the Pages artifact manifest in STATE.md.
Structured logs shall include: run_id, component=workflow, step_name, duration_ms, exit_code.
Metrics shall include: workflow_success_total, workflow_failure_total, workflow_duration_ms.
Tracing propagation is not required in Actions, but run_id must be printed once and reused by all steps.
Unit tests shall validate workflow YAML syntax via CI linting (e.g., actionlint) and enforce required permissions.
Integration tests shall validate that state branch restore and commit steps behave correctly under success/failure simulations.
INT E2E shall clear state.sqlite (delete or move aside), run workflow via workflow_dispatch, verify deployment artifacts exist, and verify state branch contains updated SQLite after success.
Evidence capture shall write 'features/add-github-actions-pages-and-state-branch/E2E_RUN_REPORT.md' and 'features/add-github-actions-pages-and-state-branch/STATE.md' with links to Actions run logs and Pages deployment status.

- Acceptance Criteria:
- On INT, a successful workflow run updates GitHub Pages with newly generated HTML and updates state.sqlite on the state branch.
- On INT, a forced failing run does not overwrite the previous successful state.sqlite and does not deploy partial outputs.
- INT clear-data E2E passes and archives evidence to features/add-github-actions-pages-and-state-branch/E2E_RUN_REPORT.md and features/add-github-actions-pages-and-state-branch/STATE.md.
- Chrome DevTools: console 0 error AND network 0 failure.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
Use GitHub Actions OIDC and repository permissions; use GITHUB_TOKEN; configure optional HF_TOKEN and OPENREVIEW_TOKEN secrets.


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-github-actions-pages-and-state-branch/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-github-actions-pages-and-state-branch
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
Create and maintain the following files under `features/add-github-actions-pages-and-state-branch/` (create if missing):
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
