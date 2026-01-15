# [Feature] add-story-linker-and-dedupe - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-story-linker-and-dedupe
- Feature Name: Add: Story linker for cross-source deduplication and link aggregation

- Context:
Goal: Merge the same event (model release, paper, technical report) across official posts, arXiv, Hugging Face, GitHub, ModelScope, and docs into a single Story.
Why now: Without aggregation, the digest becomes noisy and violates the 'avoid stacking' requirement, especially for high-volume sources.
Scope: Deterministic linking using canonical URL + stable IDs + entity keywords; no ML-based clustering in MVP; INT is the source of truth.

- Requirements:
The linker shall produce Story objects with: story_id, primary_link, links (typed), entities (matched), and derived fields for model/paper sections.
story_id shall be deterministic and derived from stable identifiers in priority order: arXiv id; GitHub release URL; HF model_id; else normalized(title)+entity_id+date_bucket.
Primary link selection shall follow topics.yaml prefer_primary_link_order and tier preference (Tier 0 preferred over Tier 1/2).
Linking shall be a state machine: ITEMS_READY -> ENTITY_TAGGED -> CANDIDATE_GROUPED -> STORIES_MERGED -> STORIES_FINAL; illegal transitions shall be rejected.
Idempotency: given identical input Items set, the Story set shall be identical (including ordering, story_id values, and primary_link choices).
Dedupe rules shall enforce: no Story may contain two links of the same type pointing to the same canonical URL; duplicates must be collapsed.
The linker shall expose a pure function API for testability and a runner integration that records merge decisions.
Audit logs shall capture merge rationale: matched_entity_ids, matched_ids(arxiv_id/hf_model_id/release_id), and any fallback heuristics used.
Security: link types must be allowlisted; unrecognized external domains must be tagged as 'external' and excluded from primary_link selection by default.
The system shall persist Story snapshots for each run to 'public/api/daily.json' and archive a copy under 'features/add-story-linker-and-dedupe/STATE.md' with story counts and merge stats.
Retention: keep at least 90 days of Story snapshots to support archive pages; prune older snapshots deterministically.
Checksum: each Story snapshot file shall include a SHA-256 checksum recorded in the run report.
Structured logs shall include: run_id, component=linker, items_in, stories_out, merges_total, fallback_merges_total.
Metrics shall include: linker_merges_total, linker_story_count, linker_fallback_ratio.
Tracing shall include a span for linker execution with tags: items_in, stories_out.
Unit tests shall cover: story_id determinism, primary link precedence, duplicate link collapse, and entity keyword matching.
Integration tests shall cover: end-to-end from fixture Items (official+arXiv+HF+GitHub) to merged Stories with correct fields.
INT E2E shall clear DB and run the pipeline on fixtures containing intentional duplicates; verify single Story output and stable ordering.
Evidence capture shall write 'features/add-story-linker-and-dedupe/E2E_RUN_REPORT.md' and 'features/add-story-linker-and-dedupe/STATE.md' with before/after counts and sample merge rationales.

- Acceptance Criteria:
- On INT, fixtures with the same arXiv id across multiple sources result in exactly one Story and a single primary_link selected per precedence rules.
- On INT, Story ordering is stable and deterministic between two identical runs (byte-identical daily.json).
- INT clear-data E2E passes and archives evidence to features/add-story-linker-and-dedupe/E2E_RUN_REPORT.md and features/add-story-linker-and-dedupe/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-story-linker-and-dedupe/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-story-linker-and-dedupe
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
Create and maintain the following files under `features/add-story-linker-and-dedupe/` (create if missing):
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
