# Runbook: Story Linker Verification Deployment

## Feature Key: add-story-linker-and-dedupe

---

## Overview

This runbook describes how to deploy, validate, and rollback the Story Linker feature in the verification (INT) environment.

---

## Prerequisites

- Python 3.13+
- uv package manager
- Git access to repository
- No external credentials required for this feature

---

## Deployment Steps

### 1. Sync Dependencies

```bash
cd /path/to/repository
uv sync
```

### 2. Verify Code Quality

```bash
# Linting
uv run ruff check src/linker/
uv run ruff format --check src/linker/

# Type checking
uv run mypy src/linker/

# Security scan
uv run bandit -r src/linker/
```

### 3. Run Test Suite

```bash
# Unit tests
uv run pytest tests/unit/test_linker/ -v

# Integration tests
uv run pytest tests/integration/test_linker.py -v

# Full test suite
uv run pytest -v
```

### 4. Verify Module Import

```python
# Verify module can be imported
from src.linker import StoryLinker, Story, LinkerState
print("Module import successful")
```

---

## Configuration

### Environment Variables

None required for this feature.

### Configuration Files

The linker uses:
- `entities.yaml`: Entity definitions with keywords for matching
- `topics.yaml`: Primary link order via `prefer_primary_link_order`

Example topics.yaml configuration:
```yaml
prefer_primary_link_order:
  - official
  - arxiv
  - github
  - huggingface
  - paper
  - blog
```

---

## Validation Checklist

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Lint check passes (0 errors)
- [ ] Type check passes (0 errors)
- [ ] Security scan passes
- [ ] Module imports correctly

---

## Rollback Procedure

If issues are detected:

### 1. Identify Failure Point

```bash
# Check test output
uv run pytest -v --tb=long
```

### 2. Revert Code Changes

```bash
# If committed, revert the commit
git revert HEAD

# Or restore specific files
git checkout HEAD~1 -- src/linker/
```

### 3. Re-run Tests

```bash
uv run pytest -v
```

### 4. Update STATE.md

Set STATUS back to previous state and document the failure.

---

## Monitoring

### Logs

The linker produces structured logs with:
- `component=linker`
- `run_id=<run-id>`
- `items_in=<count>`
- `stories_out=<count>`
- `merges_total=<count>`

### Metrics (Future)

When metrics integration is complete:
- `linker_merges_total`
- `linker_story_count`
- `linker_fallback_ratio`

---

## Contact

For issues with this feature:
- Check existing tests for expected behavior
- Review CLAUDE.md for coding standards
- Consult STATE.md for implementation decisions

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-15 | Claude | Initial implementation |
