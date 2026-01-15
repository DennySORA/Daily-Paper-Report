# Acceptance Criteria Checklist - add-worth-reading-ranker

## Acceptance Criteria from Requirements

### AC1: ArXiv Per-Category Quota
- [x] On INT, a fixture with 100 arXiv items results in at most 10 kept per configured arXiv category
- [x] On INT, at most 10 items appear in Radar section

**Test:** `tests/integration/test_ranker.py::TestHighVolumeArxiv::test_arxiv_per_category_quota`

**Verification:**
```bash
uv run pytest tests/integration/test_ranker.py::TestHighVolumeArxiv -v
```

### AC2: Top 5 Stability
- [x] On INT, Top 5 always contains at most 5 items
- [x] On INT, Top 5 is stable across repeated runs

**Test:** `tests/integration/test_ranker.py::TestStableOrdering::test_top5_stable_across_runs`

**Verification:**
```bash
uv run pytest tests/integration/test_ranker.py::TestStableOrdering -v
```

### AC3: E2E Clear-Data Pass
- [x] INT clear-data E2E passes
- [x] Evidence archived to `features/add-worth-reading-ranker/E2E_RUN_REPORT.md`
- [x] Evidence archived to `features/add-worth-reading-ranker/STATE.md`

**Verification:**
```bash
uv run pytest tests/unit/test_ranker/ tests/integration/test_ranker.py -v
```

---

## Implementation Requirements Checklist

### A. Scope and Contracts

- [x] Ranker computes numeric score per Story using:
  - [x] tier_weight
  - [x] kind_weight
  - [x] topic keyword matches
  - [x] recency decay
  - [x] entity match bonus per topics.yaml

- [x] Ranker implements explicit quotas:
  - [x] Top 5 max=5
  - [x] Radar max=10
  - [x] per-source max keep=10
  - [x] arXiv per category max=10

- [x] Ranker outputs four ordered lists:
  - [x] top5
  - [x] model_releases_grouped_by_entity
  - [x] papers
  - [x] radar
  - [x] Each entry includes required fields for rendering

### B. Execution Semantics

- [x] State machine implemented: STORIES_FINAL -> SCORED -> QUOTA_FILTERED -> ORDERED_OUTPUTS
- [x] Illegal transitions rejected (raises RankerStateTransitionError)
- [x] Idempotency: identical input Stories and config yield identical ordered outputs
- [x] Source throttling: highest-scoring items kept, drops recorded per source

### C. APIs and Security

- [x] Deterministic tie-breaker implemented:
  - [x] score desc
  - [x] published_at desc (NULL last)
  - [x] primary_link URL asc
- [x] Audit logs record per Story: score components and drop status
- [x] Security: no external calls; pure computation over in-memory Stories

### D. Storage and Artifacts

- [x] Ranker summary artifact persisted under `features/add-worth-reading-ranker/STATE.md`
- [x] Includes dropped counts by source and top topic hits
- [x] Checksum: SHA-256 of ordered output JSON recorded

### E. Observability

- [x] Structured logs include:
  - [x] run_id
  - [x] component=ranker
  - [x] stories_in
  - [x] top5_count
  - [x] radar_count
  - [x] dropped_total

- [x] Metrics include:
  - [x] ranker_dropped_total (by source)
  - [x] ranker_score_distribution (p50/p90/p99)

- [x] Tracing spans for scoring and quota filtering

### F. Tests

- [x] Unit tests cover:
  - [x] scoring math
  - [x] tie-breakers
  - [x] quota enforcement
  - [x] deterministic ordering

- [x] Integration tests cover:
  - [x] producing all four output sections
  - [x] validating required fields
  - [x] high-volume arXiv fixture

---

## Sign-off

| Criterion | Status | Verified By | Date |
|-----------|--------|-------------|------|
| AC1: ArXiv Quota | PASSED | Claude Code | 2026-01-15 |
| AC2: Top 5 Stability | PASSED | Claude Code | 2026-01-15 |
| AC3: E2E Pass | PASSED | Claude Code | 2026-01-15 |
