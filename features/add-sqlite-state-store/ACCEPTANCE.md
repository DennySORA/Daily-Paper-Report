# ACCEPTANCE.md - add-sqlite-state-store

## Acceptance Criteria Checklist

This document tracks verification of acceptance criteria for the SQLite state store feature.

---

### AC1: Idempotent Ingestion - No Duplicates

**Requirement**: On INT, two consecutive runs ingesting identical fixtures produce exactly the same item count and do not modify first_seen_at for existing URLs.

**Verification Steps**:

1. [x] Clear the SQLite database file
2. [x] Run first ingestion with fixture items
3. [x] Record item count and first_seen_at timestamps
4. [x] Run second ingestion with identical fixture items
5. [x] Verify item count is unchanged
6. [x] Verify first_seen_at is identical for all items

**Test Evidence**:
- Unit test: `test_two_runs_identical_items_idempotent` in `tests/integration/test_store.py`
- Test result: ✅ PASSED
- E2E verification: ✅ PASSED (2026-01-14)

**Code Location**: `src/store/store.py:upsert_item()`

---

### AC2: Update Detection

**Requirement**: On INT, content_hash changes for an existing canonical URL are recorded as UPDATED and reflected in the run summary.

**Verification Steps**:

1. [x] Insert item with initial content_hash
2. [x] Upsert same URL with different content_hash
3. [x] Verify event_type is UPDATED
4. [x] Verify first_seen_at is preserved
5. [x] Verify new content_hash and raw_json are stored

**Test Evidence**:
- Unit test: `test_upsert_updated_item` in `tests/integration/test_store.py`
- Test result: ✅ PASSED
- E2E verification: ✅ PASSED (2026-01-14)

**Code Location**: `src/store/store.py:upsert_item()` lines 265-320

---

### AC3: E2E Clear-Data Test

**Requirement**: INT clear-data E2E passes and archives evidence to features/add-sqlite-state-store/E2E_RUN_REPORT.md and features/add-sqlite-state-store/STATE.md.

**Verification Steps**:

1. [x] Execute E2E_PLAN.md steps
2. [x] Capture all test output
3. [x] Generate E2E_RUN_REPORT.md
4. [x] Update STATE.md with DB stats and status

**Status**: ✅ COMPLETE (2026-01-14)

**E2E Evidence**:
- Report: `features/add-sqlite-state-store/E2E_RUN_REPORT.md`
- Final database stats: runs=4, items=6, http_cache=0

---

## Schema Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| runs table with run_id, started_at, finished_at, success, error_summary | ✅ | Migration V1 |
| http_cache table with source_id, etag, last_modified, last_status, last_fetch_at | ✅ | Migration V1 |
| items table with url PK, all required fields | ✅ | Migration V1 |
| URL canonicalization strips tracking params | ✅ | test_url.py |
| date_confidence enum {high, medium, low} | ✅ | DateConfidence enum |
| published_at nullable with low confidence when NULL | ✅ | Item model |

---

## API Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| begin_run() | ✅ | StateStore.begin_run() |
| end_run(success) | ✅ | StateStore.end_run() |
| upsert_item() | ✅ | StateStore.upsert_item() |
| get_last_successful_run_finished_at() | ✅ | StateStore method |
| get_items_since(timestamp) | ✅ | StateStore.get_items_since() |
| upsert_http_cache_headers() | ✅ | StateStore method |

---

## State Machine Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| RUN_STARTED -> RUN_COLLECTING | ✅ | RunStateMachine |
| RUN_COLLECTING -> RUN_RENDERING | ✅ | RunStateMachine |
| RUN_RENDERING -> RUN_FINISHED_SUCCESS | ✅ | RunStateMachine |
| RUN_RENDERING -> RUN_FINISHED_FAILURE | ✅ | RunStateMachine |
| Illegal transitions raise and log | ✅ | test_run_state_machine.py |

---

## Security Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| No secrets in raw_json | ✅ | Design constraint |
| No auth headers in logs | ✅ | Not implemented in store layer |

---

## Observability Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| Structured logs with run_id, component=store | ✅ | Store logging |
| Logs include tx_id, op, affected_rows, duration_ms | ✅ | _transaction() context manager |
| Metrics: db_upserts_total | ✅ | StoreMetrics |
| Metrics: db_updates_total | ✅ | StoreMetrics |
| Metrics: db_tx_duration_ms | ✅ | StoreMetrics |
| Metrics: last_success_age_seconds | ✅ | StoreMetrics |

---

## Storage Requirements

| Requirement | Status | Verification |
|------------|--------|--------------|
| WAL mode enabled | ✅ | PRAGMA journal_mode=WAL |
| Migrations with explicit versioning | ✅ | schema_version table |
| Rollback scripts for previous version | ✅ | Migration.down_sql |
| 180 days item retention | ✅ | prune_old_items(days=180) |
| 90 days run retention | ✅ | prune_old_runs(days=90) |

---

## Test Requirements

| Requirement | Status | Count |
|------------|--------|-------|
| Unit tests: canonical URL uniqueness | ✅ | test_url.py |
| Unit tests: first_seen_at invariants | ✅ | test_store.py |
| Unit tests: update detection | ✅ | test_store.py |
| Unit tests: migration idempotency | ✅ | test_migrations.py |
| Integration tests: full run lifecycle | ✅ | test_store.py |
| Total tests passing | ✅ | 208 |
