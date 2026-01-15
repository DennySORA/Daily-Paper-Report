# [Feature] add-worth-reading-ranker - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-worth-reading-ranker
- Feature Name: Add: Deterministic 'worth reading' ranking, quotas, and source throttling

- Context:
Goal: Enforce the digest output constraints (Top 5, per-source caps, radar max) while prioritizing frontier topics and first-hand sources.
Why now: High-volume sources (especially arXiv) can overwhelm the digest; deterministic ranking is required for consistency and QA.
Scope: Rule-based scoring with explicit weights; non-goal is LLM-based ranking.

- Requirements:
The ranker shall compute a numeric score per Story using: tier_weight, kind_weight, topic keyword matches, recency decay, and entity match bonus per topics.yaml.
The ranker shall implement explicit quotas: Top 5 max=5; Radar max=10; per-source max keep=10; arXiv per category max=10; and enforce them deterministically.
The ranker shall output four ordered lists: top5, model_releases_grouped_by_entity, papers, radar; each entry must include required fields for rendering.
Ranking shall be a state machine: STORIES_FINAL -> SCORED -> QUOTA_FILTERED -> ORDERED_OUTPUTS; illegal transitions shall be rejected.
Idempotency: identical input Stories and config must yield identical ordered outputs.
Source throttling: if a source exceeds the cap, the system shall keep the highest-scoring items and record how many were dropped, per source.
The ranker shall provide a deterministic tie-breaker: score desc, published_at desc (NULL last), primary_link URL asc.
Audit logs shall record per Story: score components (tier/kind/topic/recency/entity) and whether it was dropped by quota.
Security: no external calls; ranker must be pure computation over in-memory Stories.
The system shall persist a ranker summary artifact per run under 'features/add-worth-reading-ranker/STATE.md' including dropped counts by source and top topic hits.
Retention: keep at least 90 days of ranker summaries to analyze drift and regressions.
Checksum: record SHA-256 of the ordered output JSON used for HTML rendering.
Structured logs shall include: run_id, component=ranker, stories_in, top5_count, radar_count, dropped_total.
Metrics shall include: ranker_dropped_total{source_id}, ranker_score_distribution (p50/p90/p99).
Tracing shall include a span for scoring and a span for quota filtering.
Unit tests shall cover: scoring math, tie-breakers, quota enforcement, and deterministic ordering.
Integration tests shall cover: producing all four output sections from a mixed fixture set and validating required fields.
INT E2E shall clear DB, ingest a high-volume arXiv fixture, and verify that per-source caps and radar max are enforced with correct dropped counts.
Evidence capture shall write 'features/add-worth-reading-ranker/E2E_RUN_REPORT.md' and 'features/add-worth-reading-ranker/STATE.md' with score breakdown samples and quota results.

- Acceptance Criteria:
- On INT, a fixture with 100 arXiv items results in at most 10 kept per configured arXiv category and at most 10 in Radar.
- On INT, Top 5 always contains at most 5 items and is stable across repeated runs.
- INT clear-data E2E passes and archives evidence to features/add-worth-reading-ranker/E2E_RUN_REPORT.md and features/add-worth-reading-ranker/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-worth-reading-ranker/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-worth-reading-ranker
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
Create and maintain the following files under `features/add-worth-reading-ranker/` (create if missing):
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
