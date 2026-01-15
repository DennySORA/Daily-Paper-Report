# CHANGELOG.md - add-arxiv-rss-and-api-ingestion

## [Unreleased]

### Added
- arXiv RSS collector for category feeds (cs.AI, cs.LG, cs.CL, stat.ML)
- arXiv API collector for keyword-based queries
- arXiv ID extraction utilities supporting old and new ID formats
- URL normalization to canonical /abs/<id> format
- Cross-source deduplication using arXiv ID as primary key
- Rate limiting (1 req/sec) for arXiv API compliance
- Timestamp preference: API timestamps preferred over RSS
- Metrics: arxiv_items_total, arxiv_deduped_total, arxiv_api_latency_ms
- Structured logging with component=arxiv, mode, items_emitted, deduped_count
- Unit tests for ID extraction, URL normalization, deduplication
- Integration tests for RSS+API ingestion and deduplication

### Changed
- Extended base collector framework to support arXiv-specific normalization

### Technical Details
- New module: `src/collectors/arxiv/`
  - `utils.py`: ID extraction and URL canonicalization
  - `rss.py`: ArxivRssCollector class
  - `api.py`: ArxivApiCollector class
  - `deduper.py`: ArxivDeduplicator class
  - `metrics.py`: ArxivMetrics class
- Test fixtures in `tests/fixtures/arxiv/`
- Integration tests in `tests/integration/test_arxiv*.py`
- Unit tests in `tests/unit/test_collectors/test_arxiv*.py`
