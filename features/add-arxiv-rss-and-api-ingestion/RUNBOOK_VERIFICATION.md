# RUNBOOK_VERIFICATION.md - add-arxiv-rss-and-api-ingestion

## Deployment Guide for Verification Environment

---

## Prerequisites

- Python 3.13+
- `uv` package manager
- Git access to repository

---

## Deployment Steps

### Step 1: Install Dependencies
```bash
uv sync
```

### Step 2: Verify Installation
```bash
uv run python -c "from src.collectors.arxiv import ArxivRssCollector, ArxivApiCollector; print('OK')"
```

---

## Configuration

### Environment Variables
No secrets required for arXiv (public API).

### Source Configuration (sources.yaml)
```yaml
sources:
  # arXiv RSS feeds
  - id: arxiv-cs-ai
    name: "arXiv cs.AI"
    url: "https://rss.arxiv.org/rss/cs.AI"
    method: arxiv_rss
    tier: 1
    kind: paper
    category: cs.AI
    max_items: 100

  - id: arxiv-cs-lg
    name: "arXiv cs.LG"
    url: "https://rss.arxiv.org/rss/cs.LG"
    method: arxiv_rss
    tier: 1
    kind: paper
    category: cs.LG
    max_items: 100

  - id: arxiv-cs-cl
    name: "arXiv cs.CL"
    url: "https://rss.arxiv.org/rss/cs.CL"
    method: arxiv_rss
    tier: 1
    kind: paper
    category: cs.CL
    max_items: 100

  - id: arxiv-stat-ml
    name: "arXiv stat.ML"
    url: "https://rss.arxiv.org/rss/stat.ML"
    method: arxiv_rss
    tier: 1
    kind: paper
    category: stat.ML
    max_items: 100

  # arXiv API query for CN models
  - id: arxiv-cn-models
    name: "arXiv CN Frontier Models"
    method: arxiv_api
    tier: 0
    kind: paper
    query: 'ti:"DeepSeek" OR ti:"Qwen" OR ti:"Yi" OR ti:"Baichuan"'
    max_results: 50
```

---

## Running the Pipeline

### Full Run
```bash
uv run digest run --config config/sources.yaml --state state.sqlite --out public/
```

### Test Run (Dry)
```bash
uv run pytest tests/integration/test_arxiv*.py -v
```

---

## Rollback Procedure

### Step 1: Restore Previous State
```bash
git checkout HEAD~1 -- src/collectors/arxiv/
```

### Step 2: Clear Corrupted Data (if needed)
```bash
rm state.sqlite
```

### Step 3: Re-run with Previous Version
```bash
uv sync
uv run digest run --config config/sources.yaml --state state.sqlite --out public/
```

---

## Monitoring

### Logs
Check structured logs for:
```json
{"component": "arxiv", "mode": "rss", "items_emitted": 42, "deduped_count": 5}
```

### Metrics
- `arxiv_items_total{mode="rss", category="cs.AI"}`
- `arxiv_items_total{mode="api"}`
- `arxiv_deduped_total`
- `arxiv_api_latency_ms`

---

## Troubleshooting

### Issue: Rate Limited by arXiv
**Symptoms:** HTTP 429 responses
**Solution:** The collector implements automatic backoff. Wait and retry.

### Issue: Malformed Feed
**Symptoms:** `bozo_exception` in logs
**Solution:** Check arXiv feed status. Feed may be temporarily unavailable.

### Issue: Duplicate Items
**Symptoms:** Same arXiv ID appears multiple times
**Solution:** Verify deduplication is running. Check that arXiv ID extraction is working correctly.

---

## Verification Checklist

- [ ] All dependencies installed
- [ ] Configuration valid
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Metrics emitting
- [ ] Logs structured correctly
- [ ] No rate limiting issues
