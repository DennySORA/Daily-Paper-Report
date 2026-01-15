# RUNBOOK_VERIFICATION.md - Collector Framework

## Overview

Deployment and operational verification runbook for the Collector Framework feature.

## Pre-Deployment Checklist

### Code Quality

```bash
# Format check
uv run ruff format --check .

# Lint check
uv run ruff check .

# Type check
uv run mypy .

# Security scan
uv run bandit -r src/
```

All checks must pass with zero errors.

### Test Suite

```bash
# Run full test suite
uv run pytest -v

# Expected: All tests pass (355+ tests)
```

### Dependency Verification

Required packages in pyproject.toml:
- feedparser >= 6.0.0
- beautifulsoup4 >= 4.12.0
- lxml >= 5.0.0
- python-dateutil >= 2.8.0

Dev dependencies:
- types-python-dateutil
- types-beautifulsoup4

## Deployment Steps

### Step 1: Sync Dependencies

```bash
uv sync
```

Verify no errors during dependency resolution.

### Step 2: Database Migration

No schema changes required. Existing `items` table schema compatible with collector output.

Verify table exists:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='items';
```

### Step 3: Smoke Test

```python
from src.collectors import CollectorRunner, RssAtomCollector
from src.store.store import StateStore
from src.fetch.client import HttpFetcher
from src.config.schemas.sources import SourceConfig
from src.config.schemas.base import SourceTier, SourceMethod, SourceKind

# Create store
store = StateStore("test.db", run_id="smoke-test")
store.connect()

# Create HTTP client
client = HttpFetcher()

# Create source config
source = SourceConfig(
    id="smoke-test",
    name="Smoke Test",
    url="https://example.com/feed.xml",
    tier=SourceTier.TIER_0,
    method=SourceMethod.RSS_ATOM,
    kind=SourceKind.BLOG,
    max_items=10
)

# Run collector
runner = CollectorRunner(store=store, http_client=client, run_id="smoke-test")
result = runner.run([source])

print(f"Sources succeeded: {result.sources_succeeded}")
print(f"Total items: {result.total_items}")

store.close()
```

### Step 4: Verify Metrics

```python
from src.collectors import CollectorMetrics

metrics = CollectorMetrics.get_instance()
print(metrics.to_dict())
```

## Operational Verification

### Health Check Commands

```bash
# Verify collector module loads
uv run python -c "from src.collectors import CollectorRunner; print('OK')"

# Verify RSS collector
uv run python -c "from src.collectors import RssAtomCollector; print('OK')"

# Verify HTML collector
uv run python -c "from src.collectors import HtmlListCollector; print('OK')"
```

### Log Verification

Collectors log with structured format. Key log events:
- `collection_started` - Source processing begins
- `fetch_completed` - HTTP fetch finished
- `parse_completed` - Parsing finished
- `collection_complete` - Source fully processed
- `fetch_failed` - HTTP error occurred
- `parse_error` - Parsing failed

Example log query:
```bash
grep "component.*collector" logs/app.log
```

### Metrics Endpoints

If Prometheus metrics exposed:
```
collector_items_total{source_id="...",kind="..."}
collector_failures_total{source_id="...",error_class="..."}
collector_duration_ms{source_id="..."}
```

## Rollback Procedure

### Immediate Rollback

If critical issues discovered:

1. Stop any running collection jobs
2. Revert to previous commit: `git revert HEAD`
3. Redeploy previous version
4. Verify system stability

### Data Rollback

Items table uses upsert semantics. To remove items from a specific run:

```sql
DELETE FROM items WHERE run_id = 'problematic-run-id';
```

Note: first_seen_at/last_seen_at will be inconsistent after deletion. Full re-collection recommended.

## Troubleshooting

### Common Issues

#### Issue: "No items collected"

Causes:
1. Feed URL returns 304 Not Modified (cache hit)
2. Feed is empty
3. HTML page structure changed

Resolution:
- Check `cache_hit` in logs
- Verify feed URL returns content
- Update selectors in domain profiles

#### Issue: "Parse error"

Causes:
1. Malformed RSS/Atom feed
2. HTML structure doesn't match expected patterns
3. Encoding issues

Resolution:
- Check `bozo_exception` in logs for RSS
- Verify HTML page loads correctly in browser
- Check Content-Type header matches actual encoding

#### Issue: "Duplicate items"

Causes:
1. URL canonicalization not stripping all tracking params
2. Different URLs resolve to same content

Resolution:
- Add tracking params to strip_params list
- Implement content-based deduplication

#### Issue: "SQLite locked"

Causes:
1. Multiple writers to same database
2. Long-running transaction

Resolution:
- Ensure single writer at a time
- Use WAL mode for better concurrency
- Reduce transaction scope

## Monitoring Alerts

Recommended alert thresholds:

| Metric | Threshold | Severity |
|--------|-----------|----------|
| collector_failures_total (per hour) | > 10 | Warning |
| collector_failures_total (per hour) | > 50 | Critical |
| collector_duration_ms (p99) | > 60000 | Warning |
| collector_items_total (per day) | < 10 | Warning |

## Contact

For issues with the collector framework, check:
1. Unit test logs
2. Integration test logs
3. Application logs with component=collector filter
