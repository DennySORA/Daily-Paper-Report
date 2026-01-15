# STATE.md - add-arxiv-rss-and-api-ingestion

## Feature Key
FEATURE_KEY: add-arxiv-rss-and-api-ingestion

## Status
STATUS: READY

## Overview
Implement arXiv RSS category ingestion and arXiv API keyword queries for CN frontier models.

## Goals
- Ingest papers from cs.AI, cs.LG, cs.CL, stat.ML RSS feeds
- Execute arXiv API keyword queries for targeted CN model reports
- Deduplicate across sources using arXiv ID as primary key
- Normalize URLs to canonical /abs/<id> format

## Decisions Made
1. **arXiv ID Extraction**: Extract arXiv ID using regex patterns supporting both old (e.g., `hep-th/9901001`) and new (e.g., `2401.12345`) formats
2. **URL Normalization**: Map all arXiv URLs (html, ar5iv, pdf) to canonical `https://arxiv.org/abs/<id>` format
3. **Deduplication Strategy**: Use arXiv ID as the deduplication key across all arXiv sources
4. **Timestamp Preference**: Prefer API timestamps over RSS when both are available; mark as date_confidence=medium with note
5. **Rate Limiting**: Implement 1 request per second limit per arXiv API etiquette
6. **RSS Collector**: Extend existing RssAtomCollector with arXiv-specific URL normalization
7. **API Collector**: New collector class for arXiv Atom API queries

## Implementation Components
1. `src/collectors/arxiv/` - New arXiv collectors module
   - `utils.py` - arXiv ID extraction and URL normalization
   - `rss.py` - arXiv RSS collector
   - `api.py` - arXiv API collector
   - `deduper.py` - Cross-source deduplication
   - `metrics.py` - arXiv-specific metrics

## Configuration
RSS Feed URLs:
- https://rss.arxiv.org/rss/cs.AI
- https://rss.arxiv.org/rss/cs.LG
- https://rss.arxiv.org/rss/cs.CL
- https://rss.arxiv.org/rss/stat.ML

API Query Parameters:
- max_results: configurable
- sort_by: submittedDate
- sort_order: descending

## Risks and Mitigations
| Risk | Mitigation |
|------|------------|
| arXiv rate limiting | Implement 1 req/sec limit, respect Retry-After |
| Feed parsing errors | Use existing feedparser with bozo exception handling |
| API timeout | Configure timeout with retry, classify as transient error |
| Empty responses | Treat empty HTTP 200 as valid (not an error) |

## TODOs
- [x] Create feature directory structure
- [x] Create STATE.md (this file)
- [x] Implement arXiv utilities (ID extraction, URL normalization)
- [x] Implement arXiv RSS collector
- [x] Implement arXiv API collector
- [x] Implement cross-source deduplication
- [x] Add metrics
- [x] Write unit tests
- [x] Write integration tests
- [x] Run all checks (lint, format, typecheck, tests)
- [x] Update STATUS to P1_DONE_DEPLOYED

## Verification Environment
- Local verification with pytest
- Database: SQLite in-memory for tests, file-based for integration

## Daily Ingestion Summary
(To be populated after first run)
- Counts by category: TBD
- Counts by CN keyword hits: TBD

## Verification Results

### Lint
```
$ uv run ruff check src/collectors/arxiv/
All checks passed!
```

### Type Check
```
$ uv run mypy src/collectors/arxiv/
Success: no issues found in 6 source files
```

### Tests
Unit tests and integration tests implemented:
- 79 unit tests for arXiv collectors
- 6 integration tests for cross-source deduplication
- Key tests verified passing:
  - ID extraction for new/old formats
  - URL normalization to canonical format
  - API collector fetch and parse
  - RSS collector category extraction
  - Cross-source deduplication by arXiv ID
  - API source preference over RSS
  - Timestamp conflict handling
  - Metrics recording

## Changelog
- Initial STATE.md created
- Implemented arXiv utilities module (utils.py)
- Implemented arXiv RSS collector (rss.py)
- Implemented arXiv API collector with rate limiting (api.py)
- Implemented cross-source deduplicator (deduper.py)
- Implemented arXiv metrics (metrics.py)
- Added comprehensive unit tests
- Added integration tests for cross-source scenarios
- All lint/type checks passing
- STATUS updated to P1_DONE_DEPLOYED
- E2E verification run completed (2026-01-14)
- Fixed ar5iv.org URL pattern support
- All acceptance criteria verified passing
- E2E_RUN_REPORT.md generated
- STATUS updated to P2_E2E_PASSED
- Refactoring completed (2026-01-14):
  - Created constants.py for magic strings
  - Added TypedDict for metrics snapshot
  - Added Protocol for rate limiter DI
  - Added dependency injection for metrics/rate limiter
  - All refactors maintain backward compatibility
  - Created REFACTOR_NOTES.md
- STATUS updated to P3_REFACTORED_DEPLOYED
- Regression E2E completed (2026-01-15):
  - Fixed test_api.py to use DI-based mocking instead of patch.object
  - Created MockRateLimiter class for test injection
  - All unit tests passing (79 tests)
  - All acceptance criteria re-verified
  - E2E_RUN_REPORT.md updated with regression results
- STATUS updated to READY
