# [Feature] add-static-html-renderer - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-static-html-renderer
- Feature Name: Add: Static HTML renderer with archive, sources, status pages, and JSON API output

- Context:
Goal: Publish a deterministic, navigable HTML site that reflects backend/DB truth for the latest digest and historical archives.
Why now: Stakeholders need a stable, shareable view; HTML output must be reproducible and auditable from stored state.
Scope: Static generation only (no client-side data as source of truth); the UI must read from rendered JSON produced by the backend pipeline; non-goal is interactive editing.

- Requirements:
The renderer shall generate: index.html (latest), day/YYYY-MM-DD.html (per run date), archive.html (date index), sources.html (per source update status), status.html (recent runs), and api/daily.json (machine-readable).
Rendered pages shall include only data derived from SQLite and the run's ordered outputs; the browser must not infer 'updates' client-side.
All links shall be clickable and must use canonical URLs; items with uncertain dates must explicitly display 'Date unknown' and include a verification hint.
Rendering shall be a state machine: RENDER_PENDING -> RENDERING_JSON -> RENDERING_HTML -> RENDER_DONE|RENDER_FAILED; illegal transitions shall be rejected.
Idempotency: given identical ordered outputs, the renderer shall produce byte-identical HTML and JSON artifacts (stable formatting and sorting).
Failure isolation: a template rendering error shall fail the run and mark RUN_FINISHED_FAILURE with an error summary.
No runtime API server is required; api/daily.json is a static artifact. Any client-side JS must be optional and must not fetch third-party resources.
Security headers should be set via Pages configuration where possible; templates must escape HTML by default to prevent injection from source content.
Audit logs shall record the list of generated files and their SHA-256 checksums.
The renderer shall write artifacts into the output directory and ensure atomic replace semantics (write to temp then rename) to avoid partial outputs.
Retention: keep at least 90 day pages and JSON snapshots; prune deterministically by date if configured.
The feature shall store a rendering manifest under 'features/add-static-html-renderer/STATE.md' containing file paths and checksums.
Structured logs shall include: run_id, component=renderer, file_count, total_bytes, duration_ms.
Metrics shall include: render_duration_ms, render_failures_total, render_bytes_total.
Tracing shall include spans for JSON rendering and HTML rendering with per-template sub-spans.
Unit tests shall cover: template rendering with escaping, deterministic output ordering, and atomic write behavior.
Integration tests shall cover: end-to-end rendering from fixture ordered outputs to expected HTML snapshots.
INT E2E shall clear output directory and DB, run the full pipeline, and verify required pages exist, links are present, and api/daily.json validates against a JSON schema.
Evidence capture shall write 'features/add-static-html-renderer/E2E_RUN_REPORT.md' and 'features/add-static-html-renderer/STATE.md' including screenshotless HTML diff checks and checksum manifest.

- Acceptance Criteria:
- On INT, the build produces index.html, archive.html, sources.html, status.html, at least one day page, and api/daily.json with non-empty Top 5 when fixtures include eligible items.
- On INT, UI content reflects DB truth: removing an item from DB and re-rendering removes it from all pages without client-side inference.
- INT clear-data E2E passes and archives evidence to features/add-static-html-renderer/E2E_RUN_REPORT.md and features/add-static-html-renderer/STATE.md.
- Chrome DevTools: console 0 error AND network 0 failure.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-static-html-renderer/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-static-html-renderer
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
Create and maintain the following files under `features/add-static-html-renderer/` (create if missing):
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
