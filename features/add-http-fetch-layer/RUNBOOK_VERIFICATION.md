# Runbook - add-http-fetch-layer

## Deployment Guide

### Prerequisites

1. Python 3.13+
2. `uv` package manager
3. Git repository access

### Installation

```bash
# 1. Sync dependencies (includes new httpx dependency)
uv sync

# 2. Verify installation
uv run python -c "import httpx; print(httpx.__version__)"
```

### Configuration

The fetch layer is configured via `FetchConfig`. Default values:

| Parameter | Default | Description |
|-----------|---------|-------------|
| user_agent | "research-report/1.0" | User-Agent header |
| default_timeout_seconds | 30.0 | Request timeout |
| max_response_size_bytes | 10485760 (10 MB) | Max response size |
| retry_policy.max_retries | 3 | Maximum retry attempts |
| retry_policy.base_delay_ms | 1000 | Initial retry delay |
| retry_policy.max_delay_ms | 30000 | Maximum retry delay |
| fail_fast | False | Abort on first failure |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| HF_TOKEN | No | Hugging Face API token |
| GITHUB_TOKEN | No | GitHub API token |
| OPENREVIEW_TOKEN | No | OpenReview API token |

Tokens are passed via Authorization headers and never logged.

### Deployment Steps

1. **Pull latest code**:
   ```bash
   git pull origin master
   ```

2. **Sync dependencies**:
   ```bash
   uv sync
   ```

3. **Run quality checks**:
   ```bash
   uv run ruff check .
   uv run mypy .
   uv run pytest
   ```

4. **Verify fetch layer**:
   ```bash
   uv run python -c "
   from src.fetch.client import HttpFetcher
   from src.fetch.config import FetchConfig
   print('Fetch layer loaded successfully')
   "
   ```

### Version/Commit Information

- **Git Branch**: master
- **Commit**: (to be filled after implementation)
- **Version Tag**: v0.1.0-http-fetch

### Rollback Procedure

If issues are encountered:

1. **Revert to previous commit**:
   ```bash
   git revert HEAD
   git push origin master
   ```

2. **Or checkout previous version**:
   ```bash
   git checkout <previous-commit-hash>
   uv sync
   ```

3. **Verify rollback**:
   ```bash
   uv run pytest
   ```

### Monitoring

Check logs for fetch-related entries:

```bash
# Filter for fetch component logs
grep '"component":"fetch"' logs/*.log | jq .
```

Check metrics:

```python
from src.fetch.metrics import FetchMetrics
metrics = FetchMetrics.get_instance()
print(metrics.to_dict())
```

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Import error for httpx | Dependency not synced | Run `uv sync` |
| Timeout errors | Network issues | Check connectivity, increase timeout |
| 429 errors | Rate limiting | Check Retry-After, reduce request rate |
| Memory issues | Large responses | Check max_response_size_bytes setting |

### Health Check

```bash
# Quick health check script
uv run python -c "
from src.fetch.client import HttpFetcher
from src.fetch.config import FetchConfig, RetryPolicy
from src.store.store import StateStore
import tempfile
from pathlib import Path

# Create temp store
with tempfile.TemporaryDirectory() as tmpdir:
    store = StateStore(Path(tmpdir) / 'test.sqlite')
    store.connect()

    config = FetchConfig(
        user_agent='health-check/1.0',
        retry_policy=RetryPolicy(max_retries=0),
    )

    fetcher = HttpFetcher(config=config, store=store, run_id='health-check')
    result = fetcher.fetch(
        source_id='health-check',
        url='https://httpbin.org/get',
    )

    print(f'Status: {result.status_code}')
    print(f'Cache hit: {result.cache_hit}')
    print('Health check PASSED' if result.status_code == 200 else 'Health check FAILED')

    store.close()
"
```
