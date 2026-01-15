# [Feature] add-yaml-config-contracts - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-yaml-config-contracts
- Feature Name: Add: Declarative YAML configuration contracts for sources, entities, and topics

- Context:
Goal: Provide a single source of truth for monitored sources, entity mapping, and ranking rules to enable repeatable daily digests.
Why now: Manual edits and ad-hoc parsing logic cause drift and make daily output non-deterministic and hard to audit.
Scope: INT is the source of truth; configuration must be validated strictly at startup; configuration changes must be traceable; non-goal is a UI editor for YAML.

- Requirements:
The system shall load sources.yaml, entities.yaml, and topics.yaml and validate them against strict schemas before any network calls.
Schema contracts shall enforce: unique source id; required URL fields; tier in {0,1,2}; method in {rss_atom, arxiv_api, openreview_venue, github_releases, hf_org, html_list, html_single, status_only}; kind enum; timezone string; and numeric limits as non-negative integers.
Schema contracts shall enforce: unique entity id; region in {cn,intl}; non-empty keyword list; prefer_links must be a non-empty list of known link types.
Schema contracts shall enforce: dedupe canonical_url_strip_params as a list of strings; scoring weights in [0.0, 5.0]; and topic keywords as a list of strings with length >= 1.
Configuration loading shall be a state machine with allowed transitions: UNLOADED -> LOADING -> VALIDATED -> READY; any validation failure shall transition to FAILED and halt the run with a non-zero exit code.
Configuration parsing shall be idempotent: repeated loads of identical files shall yield byte-for-byte identical normalized in-memory objects (stable key ordering, stable defaults application).
Configuration versions shall be immutable per run: once VALIDATED, the run must not reload or mutate configuration even if files change during execution.
The CLI shall expose: 'digest run --config sources.yaml --entities entities.yaml --topics topics.yaml --state <db> --out <dir> --tz <tz>' with strict argument validation.
No secrets shall be stored in YAML; tokens shall be provided via environment variables only (e.g., HF_TOKEN, GITHUB_TOKEN, OPENREVIEW_TOKEN).
Audit logging shall record config file checksums (SHA-256) and absolute/relative paths used for the run.
The system shall persist the effective normalized configuration snapshot to 'features/add-yaml-config-contracts/STATE.md' per run, including file hashes and validation results.
The system shall retain at least the latest 30 configuration snapshots (by date) under the repository artifacts directory; older snapshots may be pruned deterministically.
Structured logs shall include fields: run_id, component=config, phase, file_path, file_sha256, validation_error_count.
Metrics shall include: config_validation_duration_ms, config_validation_errors_total.
Tracing shall propagate run_id and source_pack identifiers across all components.
Unit tests shall cover: schema validation (positive/negative), defaults application, uniqueness constraints, and stable normalization determinism.
Integration tests shall cover: loading three YAML files together and producing a single effective configuration object.
INT E2E shall start by clearing prior config snapshot artifacts for this feature, then run 'digest run' with a minimal mock configuration and verify the snapshot is produced.
Evidence capture shall write 'features/add-yaml-config-contracts/E2E_RUN_REPORT.md' and 'features/add-yaml-config-contracts/STATE.md' with pass/fail and links to logs.

- Acceptance Criteria:
- On INT, invalid YAML or schema violations cause the run to fail before any HTTP requests and produce a validation summary in logs.
- On INT, valid YAML results in a normalized configuration snapshot whose SHA-256 matches the expected test fixture.
- INT clear-data E2E passes and archives evidence to features/add-yaml-config-contracts/E2E_RUN_REPORT.md and features/add-yaml-config-contracts/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-yaml-config-contracts/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-yaml-config-contracts
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
Create and maintain the following files under `features/add-yaml-config-contracts/` (create if missing):
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
