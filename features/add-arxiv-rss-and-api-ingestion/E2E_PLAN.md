# E2E_PLAN.md - add-arxiv-rss-and-api-ingestion

## Browser-Executable End-to-End Checklist

This document provides step-by-step instructions for running the E2E tests for the arXiv RSS and API ingestion feature.

---

## Prerequisites

1. Python 3.13+ installed
2. `uv` package manager installed
3. Repository cloned and dependencies installed:
   ```bash
   uv sync
   ```

---

## Phase 1: Clear Data

### Step 1.1: Clear SQLite Database
```bash
rm -f state.sqlite
```

### Step 1.2: Clear HTTP Cache (if exists)
```bash
rm -f .http_cache/*
```

### Step 1.3: Clear Prior Evidence
```bash
rm -f features/add-arxiv-rss-and-api-ingestion/E2E_RUN_REPORT.md
```

---

## Phase 2: Run Unit Tests

### Step 2.1: Run arXiv-specific unit tests
```bash
uv run pytest tests/unit/test_collectors/test_arxiv*.py -v
```

**Expected Result:** All tests pass

### Step 2.2: Verify test coverage
```bash
uv run pytest tests/unit/test_collectors/test_arxiv*.py --cov=src/collectors/arxiv --cov-report=term-missing
```

**Expected Result:** Coverage >= 80%

---

## Phase 3: Run Integration Tests

### Step 3.1: Run arXiv integration tests
```bash
uv run pytest tests/integration/test_arxiv*.py -v
```

**Expected Result:** All tests pass

### Step 3.2: Verify deduplication
The integration tests should verify:
- Same arXiv ID from multiple sources produces one item
- First_seen_at is preserved on duplicate ingestion
- Content hash changes trigger UPDATED event

---

## Phase 4: Run Full Pipeline with Fixtures

### Step 4.1: Prepare test fixtures
Ensure fixtures exist in `tests/fixtures/arxiv/`:
- `cs.AI.xml` - cs.AI RSS feed fixture
- `cs.LG.xml` - cs.LG RSS feed fixture
- `cs.CL.xml` - cs.CL RSS feed fixture
- `stat.ML.xml` - stat.ML RSS feed fixture
- `api_query_response.xml` - arXiv API response fixture

### Step 4.2: Run collector with fixtures
```bash
uv run pytest tests/integration/test_arxiv_e2e.py -v
```

---

## Phase 5: Verify Results

### Step 5.1: Check database for deduplication
```bash
uv run python -c "
from src.store.store import StateStore
store = StateStore('state.sqlite')
store.connect()
stats = store.get_stats()
print(f'Items: {stats[\"items\"]}')
store.close()
"
```

### Step 5.2: Verify canonical URL format
All arXiv items should have URLs matching: `https://arxiv.org/abs/<id>`

### Step 5.3: Check structured logs
Verify logs contain:
- `component=arxiv`
- `mode=rss` or `mode=api`
- `items_emitted` count
- `deduped_count`

---

## Phase 6: Archive Evidence

### Step 6.1: Generate E2E_RUN_REPORT.md
The test runner should automatically generate:
`features/add-arxiv-rss-and-api-ingestion/E2E_RUN_REPORT.md`

### Step 6.2: Update STATE.md
Update with:
- Run results
- Sampled arXiv IDs
- Delta counts

---

## Success Criteria

- [x] All unit tests pass
- [x] All integration tests pass
- [x] No duplicate items per arXiv ID
- [x] Canonical URLs in correct format
- [x] Metrics emitted correctly
- [x] Logs contain required fields
- [x] E2E_RUN_REPORT.md generated
- [x] STATE.md updated
