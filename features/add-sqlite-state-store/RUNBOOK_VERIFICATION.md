# RUNBOOK_VERIFICATION.md - add-sqlite-state-store

## Overview

This runbook describes how to deploy, verify, and rollback the SQLite state store feature.

## Environment

- **Target**: INT (Integration Testing / Local Development)
- **Requirements**: Python 3.13, uv package manager

## Pre-Deployment Checklist

- [ ] All tests pass: `uv run pytest`
- [ ] Type check passes: `uv run mypy src/`
- [ ] Lint check passes: `uv run ruff check .`
- [ ] Format check passes: `uv run ruff format --check .`

## Deployment Steps

### Step 1: Install Dependencies

```bash
uv sync
```

### Step 2: Verify Module Installation

```bash
uv run python -c "from src.store import StateStore; print('Store module OK')"
```

### Step 3: Initialize Database

The database is automatically initialized when first accessed:

```bash
# Option A: Use the CLI (requires valid config files)
uv run digest run --config sources.yaml --entities entities.yaml --topics topics.yaml --state /path/to/state.sqlite --out ./output --tz Asia/Taipei

# Option B: Use db-stats to create and inspect
uv run python -c "
from pathlib import Path
from src.store.store import StateStore

with StateStore(Path('/tmp/test_state.sqlite')) as store:
    print('Schema version:', store.get_schema_version())
    print('Stats:', store.get_stats())
"
```

### Step 4: Verify Database Structure

```bash
sqlite3 /path/to/state.sqlite ".schema"
```

Expected tables:
- `schema_version`
- `runs`
- `items`
- `http_cache`

### Step 5: Run Verification Tests

```bash
# Unit tests
uv run pytest tests/unit/test_store/ -v

# Integration tests
uv run pytest tests/integration/test_store.py -v

# Full test suite
uv run pytest
```

## Configuration

### CLI Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `--state` | Path to SQLite database file | Yes |

### Environment Variables

None required for the store module.

### Configuration File Integration

The store reads `canonical_url_strip_params` from `topics.yaml`:

```yaml
dedupe:
  canonical_url_strip_params:
    - utm_source
    - utm_medium
    - utm_campaign
    # ... additional params
```

## Rollback Procedures

### Schema Rollback

If a migration fails or needs to be rolled back:

```python
from pathlib import Path
from src.store.store import StateStore
from src.store.migrations import MigrationManager

db_path = Path("/path/to/state.sqlite")

# Connect without auto-migration
import sqlite3
conn = sqlite3.connect(str(db_path))

# Rollback to version 0 (empty schema)
manager = MigrationManager(conn)
manager.rollback_to(0)

conn.close()
```

### Full Database Reset

```bash
# Backup existing database
mv /path/to/state.sqlite /path/to/state.sqlite.backup

# New database will be created on next run
```

## Monitoring

### Log Messages

Key log events to monitor:

| Event | Description | Level |
|-------|-------------|-------|
| `connecting_to_database` | Store initializing | INFO |
| `database_connected` | Successful connection with migration info | INFO |
| `applying_migration` | Migration being applied | INFO |
| `migration_applied` | Migration completed | INFO |
| `transaction_complete` | DB transaction committed | INFO |
| `invariant_violation` | Illegal state transition | ERROR |

### Metrics

Access metrics programmatically:

```python
from src.store.metrics import StoreMetrics

metrics = StoreMetrics.get_instance()
print(metrics.to_dict())
```

### Database Health Checks

```bash
# Check database integrity
sqlite3 /path/to/state.sqlite "PRAGMA integrity_check"

# Check WAL mode
sqlite3 /path/to/state.sqlite "PRAGMA journal_mode"
# Expected: wal

# Check table counts
uv run digest db-stats --state /path/to/state.sqlite
```

## Troubleshooting

### Issue: Database locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solution**:
1. Check for other processes accessing the database
2. Ensure WAL mode is enabled
3. Increase busy_timeout if needed

### Issue: Migration failed

**Symptom**: Error during `apply_migrations()`

**Solution**:
1. Check `schema_version` table for partial migration
2. Rollback to previous version
3. Fix migration script
4. Re-apply

### Issue: first_seen_at changed unexpectedly

**Symptom**: Items showing as "NEW" when they should be "UNCHANGED"

**Solution**:
1. Check URL canonicalization is consistent
2. Verify `canonical_url_strip_params` hasn't changed
3. Check content_hash computation

## Version Information

| Component | Version |
|-----------|---------|
| Schema Version | 1 |
| Feature Key | add-sqlite-state-store |
| Status | P1_DONE_DEPLOYED |
