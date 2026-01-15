# RUNBOOK_VERIFICATION.md - Deployment and Verification Runbook

## Overview

This runbook describes how to deploy, verify, and rollback the source status and degradation reporting feature.

## Deployment

### Prerequisites

1. Python 3.13+ installed
2. uv package manager installed
3. Git repository cloned

### Deployment Steps

1. **Sync Dependencies**
   ```bash
   uv sync
   ```

2. **Run Lint and Type Checks**
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy .
   ```

3. **Run Tests**
   ```bash
   uv run pytest tests/unit/test_status/ -v
   uv run pytest tests/integration/test_status_rendering.py -v
   ```

4. **Generate Output**
   ```bash
   uv run python -m src.cli.digest render --out public --tz UTC
   ```

5. **Verify Output**
   - Check `public/sources.html` exists
   - Check `public/api/daily.json` contains `sources_status`

## Configuration

### Required Configuration
- None (feature uses existing sources configuration)

### Optional Configuration
- Source categories can be provided to `StatusComputer` via `source_categories` dict
- Default category is `other` if not specified

### Environment Variables
- No new environment variables required

## Verification Checklist

### Code Quality
- [ ] `uv run ruff check .` passes
- [ ] `uv run ruff format --check .` passes
- [ ] `uv run mypy .` passes

### Tests
- [ ] `uv run pytest tests/unit/test_status/` - all pass
- [ ] `uv run pytest tests/integration/test_status_rendering.py` - all pass

### Output Validation
- [ ] `public/sources.html` renders correctly
- [ ] `public/api/daily.json` contains valid `sources_status`
- [ ] Chrome DevTools: 0 console errors
- [ ] Chrome DevTools: 0 network failures

## Rollback

### Rollback Procedure

If issues are discovered:

1. **Revert Code Changes**
   ```bash
   git revert <commit-sha>
   ```

2. **Regenerate Output**
   ```bash
   uv run python -m src.cli.digest render --out public --tz UTC
   ```

### Rollback Verification

- [ ] Old sources.html behavior restored (if applicable)
- [ ] daily.json schema unchanged (backward compatible)

## Troubleshooting

### Common Issues

1. **Import Error: src.status module not found**
   - Ensure `src/status/__init__.py` exists
   - Run `uv sync` to refresh environment

2. **Template Error in sources.html**
   - Check Jinja2 template syntax
   - Verify `sources_status` is passed to render context

3. **Test Failures**
   - Check StatusMetrics singleton is reset between tests
   - Verify test fixtures match expected model structure

### Logs to Check

```bash
# Check for status computation logs
grep "status_computed" logs/*.log

# Check for errors
grep "ERROR" logs/*.log
```

## Monitoring

### Metrics to Monitor

- `sources_failed_total{source_id, reason_code}` - Track source failures
- `sources_cannot_confirm_total{source_id}` - Track cannot-confirm cases

### Alerts (Future)

- Alert if `sources_failed_total` exceeds threshold
- Alert if `sources_cannot_confirm_total` increases significantly

## Version Information

| Component | Version |
|-----------|---------|
| Feature Key | add-sources-status-and-degradation-reporting |
| Status Module | 1.0.0 |
| Python | 3.13+ |

---

*Last updated: 2026-01-15*
