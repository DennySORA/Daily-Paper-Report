# Runbook: Verification Environment - add-worth-reading-ranker

## Overview

This runbook describes how to deploy, validate, and rollback the "worth reading" ranker feature in the verification environment.

## Prerequisites

- Python 3.13
- uv package manager
- Git access to repository

## Deployment Steps

### Step 1: Sync Dependencies

```bash
uv sync
```

### Step 2: Verify Static Analysis

```bash
# Lint check
uv run ruff check src/ranker/

# Type check
uv run mypy src/ranker/

# Format check
uv run ruff format --check src/ranker/
```

**Expected:** All checks pass with zero errors

### Step 3: Run Test Suite

```bash
# Unit tests
uv run pytest tests/unit/test_ranker/ -v

# Integration tests
uv run pytest tests/integration/test_ranker.py -v
```

**Expected:** All tests pass

### Step 4: Verify Acceptance Criteria

```bash
# AC1: ArXiv quota enforcement
uv run pytest tests/integration/test_ranker.py::TestHighVolumeArxiv -v

# AC2: Top 5 stability
uv run pytest tests/integration/test_ranker.py::TestStableOrdering -v
```

**Expected:** All acceptance tests pass

## Configuration

### Required Configuration (topics.yaml)

The ranker reads configuration from `topics.yaml`:

```yaml
scoring:
  tier_0_weight: 3.0      # Weight for Tier 0 sources
  tier_1_weight: 2.0      # Weight for Tier 1 sources
  tier_2_weight: 1.0      # Weight for Tier 2 sources
  topic_match_weight: 1.5 # Multiplier for topic keyword matches
  entity_match_weight: 2.0 # Bonus per matched entity
  recency_decay_factor: 0.1 # Exponential decay factor

quotas:
  top5_max: 5              # Maximum items in Top 5
  radar_max: 10            # Maximum items in Radar
  per_source_max: 10       # Maximum items per source
  arxiv_per_category_max: 10 # Maximum arXiv items per category
```

### Environment Variables

No environment variables required for the ranker module.

## Usage

### Programmatic Usage

```python
from src.ranker import StoryRanker, rank_stories_pure
from src.config.schemas.topics import TopicsConfig

# Using the pure function API
result = rank_stories_pure(
    stories=stories,           # list[Story] from linker
    topics_config=topics,      # TopicsConfig from loader
    entities_config=entities,  # EntitiesConfig from loader
)

# Access output sections
top5 = result.output.top5
papers = result.output.papers
radar = result.output.radar
model_releases = result.output.model_releases_by_entity

# Check statistics
print(f"Stories in: {result.stories_in}")
print(f"Stories out: {result.stories_out}")
print(f"Dropped: {result.dropped_total}")
```

### Class-Based Usage

```python
ranker = StoryRanker(
    run_id="run-123",
    topics_config=topics_config,
    entities_config=entities_config,
)

result = ranker.rank_stories(stories)

# Check state
assert ranker.state == RankerState.ORDERED_OUTPUTS
```

## Rollback Procedure

If issues are found:

1. **Stop using ranker**: Revert to previous story ordering logic

2. **Identify issue**: Check test failures, logs

3. **Fix or revert**: Either fix the issue or revert the code changes

4. **Re-validate**: Run full test suite again

## Monitoring

### Logs to Watch

```
ranker_started       - Run begins
scoring_complete     - Scoring phase done
quota_filtering_complete - Quota phase done
ranker_complete      - Run finished
```

### Metrics to Monitor

- `stories_in` / `stories_out` ratio
- `dropped_total` - sudden increases may indicate config issues
- `scoring_duration_ms` - performance tracking
- `score_percentiles` - distribution changes may indicate scoring issues

## Troubleshooting

### Issue: Too Many Stories Dropped

**Symptom:** `dropped_total` is unexpectedly high

**Check:**
1. Verify `per_source_max` is set appropriately
2. Verify `arxiv_per_category_max` for arXiv-heavy runs
3. Review dropped_entries for patterns

### Issue: Non-Deterministic Output

**Symptom:** Same input produces different output checksums

**Check:**
1. Ensure `now` parameter is fixed for testing
2. Verify no external time dependencies
3. Check for any randomness in input data

### Issue: State Machine Error

**Symptom:** `RankerStateTransitionError` raised

**Check:**
1. Ensure `rank_stories()` is called only once per ranker instance
2. Verify proper initialization with correct initial state

## Version Information

| Component | Version |
|-----------|---------|
| Feature Key | add-worth-reading-ranker |
| Implementation Date | 2026-01-15 |
| Python Version | 3.13 |
| Test Framework | pytest 8.x |
