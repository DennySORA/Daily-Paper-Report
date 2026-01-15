# CHANGELOG.md - Collector Framework

## [1.0.0] - 2026-01-14

### Added

#### Core Framework
- **Collector Interface**: Protocol-based collector interface with `collect(source_config, http_client, now) -> CollectorResult` signature
- **BaseCollector**: Abstract base class providing common utilities for URL canonicalization, validation, sorting, and truncation
- **CollectorResult**: Dataclass containing items, parse_warnings, optional error, and final state

#### State Machine
- **SourceState**: Enum defining source processing states (PENDING, FETCHING, PARSING, DONE, FAILED)
- **SourceStateMachine**: Per-source state machine with transition guards and structured logging
- **SourceStateTransitionError**: Exception for invalid state transitions

#### Error Handling
- **CollectorErrorClass**: Enum for error classification (FETCH, PARSE, SCHEMA)
- **CollectorError**: Base exception with error_class, message, source_id, and optional details
- **ParseError**: Specialized error for parsing failures with line/column context
- **SchemaError**: Specialized error for schema validation with field/expected/actual info
- **ErrorRecord**: Pydantic model for serializable error persistence

#### Collectors
- **RssAtomCollector**: Collector for RSS 2.0 and Atom 1.0 feeds using feedparser
  - Extracts title, link, published_at, summary, author, categories
  - Handles malformed feeds with bozo warnings
  - Date extraction with confidence levels (HIGH, MEDIUM, LOW)

- **HtmlListCollector**: Collector for HTML list pages using BeautifulSoup
  - Finds article containers via semantic selectors (article, .post, .card, etc.)
  - Falls back to link extraction from main content
  - Multi-strategy date extraction (time element, meta tags, JSON-LD, text patterns)
  - Navigation link filtering to exclude menus/footers

#### Runner
- **CollectorRunner**: Orchestrates collection across multiple sources
  - ThreadPoolExecutor for parallel collection
  - Automatic collector selection by source.method
  - Failure isolation (one failing source doesn't stop others)
  - Upserts items to StateStore

- **RunnerResult**: Aggregated results with per-source details
  - sources_succeeded, sources_failed counts
  - total_items, total_new, total_updated counts
  - source_results dict with individual SourceRunResult

#### Metrics
- **CollectorMetrics**: Thread-safe singleton for metrics collection
  - Items collected by source and kind
  - Failures by source and error class
  - Duration per source
  - Prometheus-format export

#### Utilities
- URL canonicalization with tracking param stripping
- URL validation (http(s) scheme only)
- Deterministic sorting (published_at DESC NULLS LAST, url ASC)
- max_items enforcement
- Raw JSON truncation at 100KB with secret redaction

### Testing

#### Unit Tests
- `tests/unit/test_collectors/test_state_machine.py` - 17 tests for state machine
- `tests/unit/test_collectors/test_errors.py` - Error type tests
- `tests/unit/test_collectors/test_base.py` - Base collector utility tests

#### Integration Tests
- `tests/integration/test_collectors.py` - SQLite integration tests
  - RSS collector upsert
  - HTML collector upsert
  - Multiple collectors sequential
  - Failure isolation
  - Idempotent upsert
  - Deterministic ordering
  - max_items enforcement
  - Cache hit (304) handling

### Dependencies Added
- feedparser >= 6.0.0
- beautifulsoup4 >= 4.12.0
- lxml >= 5.0.0
- python-dateutil >= 2.8.0
- types-python-dateutil (dev)
- types-beautifulsoup4 (dev)

### Technical Notes

- All collectors share the same interface for consistent usage
- State machine provides auditable source processing lifecycle
- Error typing enables structured error handling and persistence
- Thread-safe metrics allow concurrent collection with accurate counting
- Raw JSON size limits prevent database bloat
- Deterministic ordering ensures idempotent results across runs

### Migration Notes

No database schema changes required. The collector framework outputs items compatible with the existing `items` table schema in StateStore.

### Breaking Changes

None. This is a new feature with no modifications to existing APIs.
