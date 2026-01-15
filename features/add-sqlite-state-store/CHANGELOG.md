# CHANGELOG.md - add-sqlite-state-store

## [1.0.0] - 2026-01-14

### Added

#### Core Store Module (`src/store/`)

- **StateStore class** (`store.py`)
  - SQLite-based persistent storage for items, runs, and HTTP cache headers
  - WAL mode enabled for reliability
  - Transactional APIs with automatic rollback on failure
  - Context manager support for automatic connection management

- **Data Models** (`models.py`)
  - `Item` - Stored content item with canonicalized URL as primary key
  - `Run` - Run lifecycle tracking record
  - `HttpCacheEntry` - HTTP cache headers for conditional requests
  - `UpsertResult` - Result of item upsert operations
  - `DateConfidence` enum - HIGH, MEDIUM, LOW confidence levels
  - `ItemEventType` enum - NEW, UPDATED, UNCHANGED event types

- **Run State Machine** (`state_machine.py`)
  - `RunStateMachine` - Enforces valid run lifecycle transitions
  - `RunState` enum - RUN_STARTED, RUN_COLLECTING, RUN_RENDERING, RUN_FINISHED_SUCCESS, RUN_FINISHED_FAILURE
  - `RunStateError` - Raised on illegal state transitions
  - Invariant violation logging for debugging

- **URL Canonicalization** (`url.py`)
  - `canonicalize_url()` - Normalizes URLs for deduplication
  - Strips UTM and social tracking parameters
  - Removes URL fragments by default
  - Normalizes arXiv URLs to canonical /abs/ form
  - Upgrades HTTP to HTTPS for known secure sites
  - Configurable strip params from topics.yaml

- **Schema Migrations** (`migrations.py`)
  - `MigrationManager` - Manages SQLite schema versioning
  - Version 1 schema: runs, items, http_cache tables
  - Rollback support for previous versions
  - Idempotent migration application

- **Metrics Collection** (`metrics.py`)
  - `StoreMetrics` - Singleton metrics collector
  - Tracks upserts, updates, unchanged operations
  - Records transaction duration and count
  - Tracks retention pruning operations

#### Transactional APIs

- `begin_run(run_id)` - Start a new pipeline run
- `end_run(run_id, success, error_summary)` - Complete a run
- `upsert_item(item)` - Idempotent item ingestion with update detection
- `get_item(url)` - Retrieve item by canonicalized URL
- `get_items_since(timestamp)` - Get items first seen since a timestamp
- `get_items_by_source(source_id)` - Get items filtered by source
- `get_last_successful_run_finished_at()` - Delta detection support
- `upsert_http_cache_headers(entry)` - Store HTTP cache headers
- `get_http_cache(source_id)` - Retrieve HTTP cache entry
- `prune_old_items(days)` - Retention pruning for items
- `prune_old_runs(days)` - Retention pruning for runs
- `get_stats()` - Get row counts for all tables
- `get_schema_version()` - Get current schema version

#### CLI Integration

- Updated `digest run` command to initialize state store
- Automatic run tracking (begin_run/end_run)
- Last successful run detection for delta computation
- Store statistics logging on run completion
- New `db-stats` command for viewing database statistics

#### Test Coverage

- 78 unit tests covering:
  - Model validation and enum values
  - State machine transitions and guards
  - URL canonicalization edge cases
  - Migration idempotency and rollback

- 33 integration tests covering:
  - Full run lifecycle with items
  - Idempotent upsert verification
  - Update detection (content_hash changes)
  - HTTP cache operations
  - Retention/pruning
  - Two-run idempotency (acceptance criteria)

### Technical Details

#### SQLite Schema (Version 1)

```sql
-- runs table
CREATE TABLE runs (
    run_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    success INTEGER,
    error_summary TEXT
);

-- items table
CREATE TABLE items (
    url TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    tier INTEGER NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    published_at TEXT,
    date_confidence TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    raw_json TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

-- http_cache table
CREATE TABLE http_cache (
    source_id TEXT PRIMARY KEY,
    etag TEXT,
    last_modified TEXT,
    last_status INTEGER,
    last_fetch_at TEXT NOT NULL
);
```

#### Key Invariants

1. **first_seen_at is immutable**: Once set, never modified
2. **URL canonicalization is consistent**: Same input always produces same canonical URL
3. **Idempotent ingestion**: Same URL + same content_hash = UNCHANGED (only last_seen_at updated)
4. **Update detection**: Same URL + different content_hash = UPDATED (content updated, first_seen_at preserved)

### Dependencies

No new dependencies added. Uses Python standard library `sqlite3` module.

### Breaking Changes

None. This is a new feature.

### Migration Notes

None required. Database is automatically initialized on first use.
