# [Feature] add-arxiv-rss-and-api-ingestion - Requirements, Implementation, Deployment (Verification Environment)

You are a senior full-stack engineer/Tech Lead. Implement this feature in the codebase and deploy it to the verification environment.
This round of work (Prompt #1-#4) must remain coherent; also write key state to files so it can be continued later.

## Planning Requirements (Must Follow)
- Complete structured planning before implementation (use any planning tool if available).

## Inputs
- Feature Key: add-arxiv-rss-and-api-ingestion
- Feature Name: Add: arXiv RSS category ingestion and arXiv API keyword queries for CN frontier models

- Context:
Goal: Reliably capture new papers across cs.AI/cs.LG/cs.CL/stat.ML and increase recall for CN frontier model technical reports via arXiv API keyword queries.
Why now: Category RSS alone may miss targeted CN model reports among high-volume daily feeds; keyword queries improve precision and recall.
Scope: Use RSS/Atom and arXiv API only; do not scrape arXiv HTML pages; INT is the source of truth for what was detected and when.

- Requirements:
The RSS collector shall ingest the following feeds: https://rss.arxiv.org/rss/cs.AI, https://rss.arxiv.org/rss/cs.LG, https://rss.arxiv.org/rss/cs.CL, https://rss.arxiv.org/rss/stat.ML.
The arXiv API collector shall execute a configurable query string (Atom response) with max_results, sort_by=submittedDate, sort_order=descending; it shall extract arXiv id, title, authors, abstract (truncated), categories, and published/updated timestamps.
Normalized URLs shall be canonical arXiv abstract URLs (https://arxiv.org/abs/<id>) when possible; html/ar5iv URLs shall be mapped back to /abs/<id>.
Deduplication shall treat arXiv id as the primary key across all arXiv sources; the same id must not produce multiple Stories in the same run.
If RSS and API disagree on published_at, the system shall prefer API timestamps and mark date_confidence=medium with a note in raw_json.
Idempotency: repeated ingestion of the same feed entries must not create duplicates; first_seen_at invariants shall hold.
The arXiv API collector shall not require credentials; it shall respect arXiv API etiquette by limiting request frequency (e.g., no more than 1 request per second per worker).
Error handling shall classify and record: API timeout, malformed Atom, and empty responses; empty response is not an error if HTTP 200.
Audit logs shall record query string, result_count, and the newest/oldest arXiv id observed.
The collector shall store raw metadata in raw_json and compute content_hash from {title, abstract_snippet, categories, updated_at}.
The feature shall write a daily arXiv ingestion summary (counts by category, counts by CN keyword hits) to 'features/add-arxiv-rss-and-api-ingestion/STATE.md'.
Retention: store at least 180 days of arXiv items; pruning must not remove items referenced by rendered archives.
Structured logs shall include: run_id, component=arxiv, mode=rss|api, source_id, items_emitted, deduped_count.
Metrics shall include: arxiv_items_total{mode,category}, arxiv_deduped_total, arxiv_api_latency_ms.
Tracing shall create a span for each arXiv source and for the keyword query execution.
Unit tests shall cover: arXiv id extraction, mapping html/ar5iv URLs to /abs, and cross-source dedupe.
Integration tests shall run RSS+API fixture feeds and verify stable deduplication and timestamp preference rules.
INT E2E shall clear DB, ingest fixtures for all four RSS feeds plus the API query, and verify exactly one item per arXiv id and correct 'since last run' delta computation.
Evidence capture shall write 'features/add-arxiv-rss-and-api-ingestion/E2E_RUN_REPORT.md' and 'features/add-arxiv-rss-and-api-ingestion/STATE.md' including sampled arXiv ids and deltas.

- Acceptance Criteria:
- On INT, the same arXiv id appearing in multiple categories produces exactly one Story and one persisted item keyed by canonical /abs URL.
- On INT, the keyword query collector returns deterministic results ordering and persists query diagnostics.
- INT clear-data E2E passes and archives evidence to features/add-arxiv-rss-and-api-ingestion/E2E_RUN_REPORT.md and features/add-arxiv-rss-and-api-ingestion/STATE.md.

- Verification URL (optional): 
- Verification Credentials / Login Method (if needed):
-（不需要或由環境變數/SSO/既有機制提供）


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-arxiv-rss-and-api-ingestion/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-arxiv-rss-and-api-ingestion
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
Create and maintain the following files under `features/add-arxiv-rss-and-api-ingestion/` (create if missing):
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
