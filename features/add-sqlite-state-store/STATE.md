# STATE.md - add-sqlite-state-store

## Status

- **FEATURE_KEY**: add-sqlite-state-store
- **STATUS**: READY
- **Last Updated**: 2026-01-14T15:51:00Z

## Run Information

- **Git Commit**: (no commits yet - new repository)
- **Implementation Phase**: Prompt #4 Complete (Feature Ready)

## Implementation Summary

### Completed Components

1. **Store Package Structure** (`src/store/`)
   - `__init__.py` - Package exports
   - `models.py` - Pydantic data models (Item, Run, HttpCacheEntry, UpsertResult)
   - `state_machine.py` - Run lifecycle state machine (RunStateMachine)
   - `url.py` - URL canonicalization utilities
   - `migrations.py` - SQLite schema migrations
   - `store.py` - Main StateStore class
   - `metrics.py` - Store metrics collection
   - `hash.py` - Content hashing utilities (NEW in P3)
   - `errors.py` - Domain exception hierarchy (NEW in P3)

2. **Data Models**
   - `DateConfidence` enum: HIGH, MEDIUM, LOW
   - `ItemEventType` enum: NEW, UPDATED, UNCHANGED
   - `Item` model with all required fields
   - `Run` model for run lifecycle tracking
   - `HttpCacheEntry` for cache headers
   - `UpsertResult` for upsert operation results

3. **Run Lifecycle State Machine**
   - States: RUN_STARTED → RUN_COLLECTING → RUN_RENDERING → RUN_FINISHED_SUCCESS|RUN_FINISHED_FAILURE
   - Illegal transition guards with logging
   - Invariant violation detection

4. **URL Canonicalization**
   - Strips tracking parameters (UTM, fbclid, gclid, etc.)
   - Removes fragments by default
   - Normalizes arXiv URLs to /abs/ form
   - Upgrades HTTP to HTTPS for known sites
   - Supports custom strip params from topics.yaml

5. **SQLite Schema (Version 1)**
   - `runs` table: run_id, started_at, finished_at, success, error_summary
   - `items` table: url (PK), source_id, tier, kind, title, published_at, date_confidence, content_hash, raw_json, first_seen_at, last_seen_at
   - `http_cache` table: source_id, etag, last_modified, last_status, last_fetch_at
   - WAL mode enabled for reliability

6. **Transactional APIs**
   - `begin_run()` / `end_run()` - Run lifecycle management
   - `upsert_item()` - Idempotent item ingestion with update detection
   - `get_last_successful_run_finished_at()` - Delta detection support
   - `get_items_since()` - Items since a timestamp
   - `upsert_http_cache_headers()` - HTTP cache management
   - `prune_old_items()` / `prune_old_runs()` - Retention management

7. **CLI Integration**
   - Updated `digest run` command to initialize store
   - Begin/end run tracking in store
   - Last successful run detection
   - Store stats logging
   - New `db-stats` command for viewing database statistics

## Test Coverage

- **Unit Tests**: 78 tests passing
  - `test_models.py` - Model validation tests
  - `test_run_state_machine.py` - State machine transition tests
  - `test_url.py` - URL canonicalization tests
  - `test_migrations.py` - Schema migration tests

- **Integration Tests**: 33 tests passing
  - Full run lifecycle with items
  - Idempotent upsert verification
  - Update detection (content_hash changes)
  - HTTP cache operations
  - Retention/pruning
  - Two-run idempotency verification

## Database Statistics

| Table | Expected Structure |
|-------|-------------------|
| runs | run_id TEXT PK, started_at TEXT, finished_at TEXT, success INTEGER, error_summary TEXT |
| items | url TEXT PK, source_id TEXT, tier INTEGER, kind TEXT, title TEXT, published_at TEXT, date_confidence TEXT, content_hash TEXT, raw_json TEXT, first_seen_at TEXT, last_seen_at TEXT |
| http_cache | source_id TEXT PK, etag TEXT, last_modified TEXT, last_status INTEGER, last_fetch_at TEXT |
| schema_version | version INTEGER PK, applied_at TEXT, description TEXT |

## Validation Results

- **Ruff Lint**: ✅ All checks passed
- **Ruff Format**: ✅ 44 files formatted
- **Mypy Type Check**: ✅ Success: no issues found in 44 source files
- **Pytest**: ✅ 208 passed in 1.26s

## Deployment Information

This is a library feature integrated into the CLI. "Deployment" means:
- Code is implemented and tested
- CLI integrates with the store
- Tests pass

To verify:
```bash
uv run pytest tests/unit/test_store/ tests/integration/test_store.py -v
uv run digest db-stats --state /path/to/state.sqlite
```

## Risks and Mitigations

1. **SQLite file locking**: WAL mode enabled to reduce locking contention
2. **Migration failures**: Explicit versioning with rollback support
3. **Data corruption**: Transactions ensure atomicity

## E2E Verification (Prompt #2)

All acceptance criteria verified on 2026-01-14:

1. ✅ Two consecutive runs with identical fixtures produce same item count (5)
2. ✅ `first_seen_at` is not modified for existing URLs
3. ✅ `content_hash` changes are recorded as UPDATED
4. ✅ URL canonicalization strips tracking parameters
5. ✅ Last successful run detection works correctly
6. ✅ db-stats CLI command displays correct statistics

Evidence archived to E2E_RUN_REPORT.md.

## Refactoring (Prompt #3)

Completed on 2026-01-14:

1. ✅ Extracted `compute_content_hash` to dedicated `hash.py` module (SRP)
2. ✅ Created domain exception hierarchy in `errors.py` (Error Layering)
3. ✅ Refactored `upsert_item` with helper methods (SRP, DRY)
4. ✅ Added `MetricsRecorder` Protocol for dependency injection (DIP)
5. ✅ Added `NullMetricsRecorder` for testing scenarios
6. ✅ Updated module exports in `__init__.py`

All 208 tests passing after refactoring.
See REFACTOR_NOTES.md for full details and rollback plan.

## Regression E2E (Prompt #4)

Completed on 2026-01-14:

1. ✅ Unit tests: 78 passed in 0.18s
2. ✅ Integration tests: 33 passed in 0.33s
3. ✅ E2E Steps 4-9 re-run: All passed
4. ✅ New error types verified (RunNotFoundError, ItemNotFoundError, etc.)
5. ✅ Hash module verified (deterministic, case-insensitive, extra fields)
6. ✅ Backward compatibility verified

All acceptance criteria verified. Feature is **READY** for release.

## Configuration

The store accepts configuration from:
- `--state` CLI argument: Path to SQLite database file
- `topics.yaml` `dedupe.canonical_url_strip_params`: URL parameters to strip

## Observability

### Structured Logs (component=store)
- `connecting_to_database` - Database connection initiated
- `database_connected` - Connection established with migration info
- `transaction_started` - Transaction begun with tx_id
- `transaction_complete` - Transaction committed with duration_ms
- `run_state_transition` - State machine transitions
- `invariant_violation` - Illegal state transitions

### Metrics (StoreMetrics)
- `db_upserts_total` - New item inserts
- `db_updates_total` - Item updates (changed hash)
- `db_unchanged_total` - Unchanged items
- `db_tx_duration_ms` - Transaction duration
- `last_success_age_seconds` - Age of last successful run
- `items_pruned_total` / `runs_pruned_total` - Retention pruning
