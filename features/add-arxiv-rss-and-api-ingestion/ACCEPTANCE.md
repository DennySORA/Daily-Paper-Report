# ACCEPTANCE.md - add-arxiv-rss-and-api-ingestion

## Acceptance Criteria Checklist

### Criterion 1: Single Story Per arXiv ID
- [x] **On INT**: The same arXiv ID appearing in multiple categories produces exactly one Story and one persisted item keyed by canonical /abs URL.

**Verification Steps:**
1. Clear database
2. Ingest fixtures containing the same arXiv ID in multiple RSS feeds
3. Query database for items with the arXiv ID
4. Verify exactly one row exists with canonical URL format

### Criterion 2: Deterministic API Query Results
- [x] **On INT**: The keyword query collector returns deterministic results ordering and persists query diagnostics.

**Verification Steps:**
1. Execute API query with test fixtures
2. Run query twice with same parameters
3. Verify identical ordering of results
4. Verify query diagnostics logged (query string, result_count, newest/oldest ID)

### Criterion 3: E2E Clear-Data Test Passes
- [x] **INT clear-data E2E passes** and archives evidence to:
  - features/add-arxiv-rss-and-api-ingestion/E2E_RUN_REPORT.md
  - features/add-arxiv-rss-and-api-ingestion/STATE.md

**Verification Steps:**
1. Clear all prior state (DB, cache)
2. Run full pipeline with test fixtures
3. Verify E2E_RUN_REPORT.md generated
4. Verify STATE.md updated with run results
5. Verify sampled arXiv IDs documented
6. Verify delta computation is correct

## Test Evidence Requirements

### Unit Tests Must Cover:
- [x] arXiv ID extraction from various URL formats
- [x] Mapping html/ar5iv URLs to /abs/<id>
- [x] Cross-source deduplication logic
- [x] Content hash computation for arXiv items

### Integration Tests Must Cover:
- [x] RSS+API fixture feeds ingestion
- [x] Stable deduplication behavior
- [x] Timestamp preference rules (API over RSS)
- [x] Date confidence marking

### Metrics to Verify:
- [x] `arxiv_items_total{mode,category}` emitted correctly
- [x] `arxiv_deduped_total` reflects actual deduplication
- [x] `arxiv_api_latency_ms` recorded

### Logs to Verify:
- [x] `run_id`, `component=arxiv`, `mode=rss|api` present
- [x] `source_id`, `items_emitted`, `deduped_count` logged
- [x] Query diagnostics (query_string, result_count, newest/oldest ID) logged
