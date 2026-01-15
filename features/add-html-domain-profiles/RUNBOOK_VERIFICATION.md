# Runbook: Verification Environment Deployment

## Feature: add-html-domain-profiles

---

## Pre-Deployment Checklist

- [ ] All unit tests pass: `uv run pytest tests/unit/test_collectors/test_html_profile/ -v`
- [ ] All integration tests pass: `uv run pytest tests/integration/test_html_list_collector.py -v`
- [ ] Lint check passes: `uv run ruff check .`
- [ ] Format check passes: `uv run ruff format --check`
- [ ] Type check passes: `uv run mypy .`
- [ ] No secrets in code (checked via `uv run bandit -r src/`)

---

## Deployment Steps

### 1. Install Dependencies
```bash
cd /path/to/project
uv sync
```

### 2. Verify Build
```bash
uv run ruff check .
uv run ruff format --check
uv run mypy .
uv run pytest
```

### 3. Run Application
```bash
uv run python main.py
```

---

## Configuration

### Environment Variables
No new environment variables required for this feature.

### Domain Profile Configuration

Profiles can be registered programmatically:

```python
from src.collectors.html_profile import DomainProfile, ProfileRegistry

# Get the singleton registry
registry = ProfileRegistry.get_instance()

# Register a custom profile
profile = DomainProfile(
    domain="example.com",
    name="Example Blog Profile",
    link_rules=LinkExtractionRule(
        container_selector=".blog-post",
        link_selector="a.post-link",
    ),
    max_item_page_fetches=5,
)
registry.register(profile)
```

### Default Behavior

Without explicit profile registration, the collector creates a default profile with:
- Container selector: `article`
- Link selector: `a[href]`
- K-cap: 10 item pages
- Item page recovery: enabled
- Allowed content types: text/html, application/xhtml+xml, application/xml

---

## Rollback Procedure

### Quick Rollback
```bash
# Revert to previous commit
git checkout <previous-commit>
uv sync
uv run python main.py
```

### Disable Feature
If immediate rollback is needed without code change:
1. Do not register any domain profiles
2. The default profile will be used with sensible defaults
3. To disable item page recovery globally, modify source configs to use a different method

---

## Monitoring

### Metrics Endpoints
```bash
# Get Prometheus-format metrics
from src.collectors.html_profile.metrics import HtmlProfileMetrics
metrics = HtmlProfileMetrics.get_instance()
print(metrics.to_prometheus_format())
```

### Key Metrics to Watch
- `html_list_links_total{domain}`: Total links extracted per domain
- `html_date_recovery_total{domain}`: Dates recovered from item pages
- `html_parse_failures_total{domain}`: Parse failures (should be low)

### Log Queries
```bash
# Search for html_profile logs
grep "component=html_profile" logs/*.log

# Search for date recovery
grep "date_recovered_count" logs/*.log

# Search for K-cap enforcement
grep "item_pages_fetched" logs/*.log
```

---

## Troubleshooting

### Issue: No items extracted from HTML page
**Check**:
1. Content-Type header is allowed (text/html)
2. Container selector matches the page structure
3. Link selector finds links within containers

**Debug**:
```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(html_content, "lxml")
print(soup.select("article"))  # Check containers
```

### Issue: Date recovery not working
**Check**:
1. `enable_item_page_recovery=True` in profile
2. K-cap > 0
3. Item pages return valid HTML with date metadata

### Issue: Cross-domain redirects blocked
**Resolution**:
Add trusted domains to `allowed_redirect_domains` in profile:
```python
profile = DomainProfile(
    domain="example.com",
    name="Example",
    allowed_redirect_domains=["cdn.example.com", "trusted.com"],
)
```

---

## Contact

For issues with this feature:
1. Check logs for error messages
2. Verify profile configuration
3. Review E2E_RUN_REPORT.md for known issues
