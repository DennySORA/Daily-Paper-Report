# Changelog - add-worth-reading-ranker

All notable changes for the "worth reading" ranker feature.

## [1.0.0] - 2026-01-15

### Added

#### Core Ranker Module (`src/ranker/`)

- **State Machine** (`state_machine.py`)
  - `RankerState` enum: STORIES_FINAL, SCORED, QUOTA_FILTERED, ORDERED_OUTPUTS
  - `RankerStateMachine` class enforcing valid state transitions
  - `RankerStateTransitionError` for illegal transitions

- **Scoring Engine** (`scorer.py`)
  - `StoryScorer` class computing numeric scores per Story
  - Score components: tier, kind, topic, recency, entity
  - Configurable weights from `topics.yaml`
  - Topic keyword matching with boost weights
  - Recency decay using exponential function

- **Quota Filtering** (`quota.py`)
  - `QuotaFilter` class enforcing output constraints
  - Per-source maximum quota
  - ArXiv per-category quota
  - Deterministic tie-breaker: score desc, published_at desc, URL asc
  - Section assignment: TOP5, MODEL_RELEASES, PAPERS, RADAR

- **Main Orchestrator** (`ranker.py`)
  - `StoryRanker` class coordinating scoring and quotas
  - `rank_stories_pure()` pure function API
  - Output checksum (SHA-256) for idempotency verification

- **Metrics** (`metrics.py`)
  - `RankerMetrics` singleton for metrics collection
  - Score percentiles (p50/p90/p99)
  - Dropped story tracking by source
  - Duration tracking for scoring and quota phases

- **Models** (`models.py`)
  - `ScoreComponents` dataclass for score breakdown
  - `ScoredStory` dataclass for scored stories
  - `DroppedEntry` dataclass for dropped story tracking
  - `RankerOutput` model for four output sections
  - `RankerResult` model for complete result

#### Tests

- **Unit Tests** (`tests/unit/test_ranker/`)
  - `test_state_machine.py`: State transition tests
  - `test_scorer.py`: Scoring formula tests
  - `test_quota.py`: Quota enforcement and tie-breaker tests
  - `test_ranker.py`: Orchestrator integration tests

- **Integration Tests** (`tests/integration/test_ranker.py`)
  - Four output sections test
  - High-volume arXiv quota test
  - Stable ordering test
  - End-to-end pipeline test

#### Feature Artifacts

- `features/add-worth-reading-ranker/STATE.md`
- `features/add-worth-reading-ranker/E2E_PLAN.md`
- `features/add-worth-reading-ranker/ACCEPTANCE.md`
- `features/add-worth-reading-ranker/RUNBOOK_VERIFICATION.md`
- `features/add-worth-reading-ranker/CHANGELOG.md` (this file)

### Configuration

Uses existing `topics.yaml` schema:
- `scoring` section for weights
- `quotas` section for limits
- `topics` section for keyword matching

### Dependencies

No new dependencies required. Uses existing:
- pydantic (models)
- structlog (logging)

### Breaking Changes

None. This is a new feature.

### Migration Notes

1. Integrate ranker after linker in pipeline
2. Pass linker output (list[Story]) to ranker
3. Use ranker output sections for rendering

---

## Reviewers

Please verify:
1. All unit tests pass
2. Integration tests pass
3. Static analysis clean (ruff, mypy)
4. Acceptance criteria met per ACCEPTANCE.md
