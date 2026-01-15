# Changelog: add-html-domain-profiles

## [1.0.0] - 2024-01-15

### Added

#### Domain Profile System
- New module `src/collectors/html_profile/` with:
  - `DomainProfile` model for domain-specific extraction rules
  - `LinkExtractionRule` for configurable link extraction
  - `DateExtractionRule` for configurable date extraction
  - `ProfileRegistry` thread-safe singleton for profile management

#### Date Extraction with Precedence
- `DateExtractor` class with precedence-based extraction:
  1. `<time datetime>` element (HIGH confidence)
  2. `<meta property="article:published_time">` (HIGH confidence)
  3. JSON-LD `datePublished` (HIGH confidence)
  4. JSON-LD `dateModified/dateCreated` (MEDIUM confidence)
  5. Text regex patterns (MEDIUM confidence)
- Tracks all candidate dates attempted
- Returns `DateExtractionResult` with confidence level and method

#### Item Page Date Recovery
- `ItemPageFetcher` class for recovering dates from item pages
- K-cap enforcement (default 10, configurable per profile)
- Security: content-type validation, cross-domain blocking
- Does not invalidate list results on item page failures

#### State Machine Extensions
- Added `SOURCE_PARSING_LIST` state for list page parsing
- Added `SOURCE_PARSING_ITEM_PAGES` state for item page recovery
- Illegal transition guard: cannot enter item page state without list parsing

#### Metrics
- `html_list_links_total{domain}`: Links extracted per domain
- `html_date_recovery_total{domain}`: Dates recovered from item pages
- `html_parse_failures_total{domain}`: Parse failures per domain
- Prometheus-format export support

#### Security
- Content-type validation (text/html, application/xhtml+xml, application/xml only)
- Cross-domain redirect blocking with optional allowlist
- Binary content rejection (images, videos, PDFs)

#### raw_json Enhancements
- `extracted_title`: Title extracted from HTML
- `extracted_date_raw`: Raw date string before parsing
- `extraction_method`: Method used for extraction
- `candidate_dates`: List of all candidate dates found

### Changed

#### HtmlListCollector
- Integrated with domain profile system
- Uses `ProfileRegistry` for profile lookup
- Uses `DateExtractor` for date extraction
- Uses `ItemPageFetcher` for date recovery
- Enhanced structured logging with stage indicators

### Tests

#### Unit Tests
- `test_date_extractor.py`: Date extraction precedence, JSON-LD parsing
- `test_models.py`: DomainProfile, rules validation
- `test_registry.py`: Profile registration, lookup

#### Integration Tests
- `test_html_list_collector.py`: Fixture-based parsing tests
- K-cap enforcement verification
- Security guard testing
- Idempotency testing

#### Fixtures
- `blog_list_with_time.html`: `<time>` element dates
- `blog_list_with_meta.html`: Meta tag dates
- `blog_list_with_json_ld.html`: JSON-LD dates
- `blog_list_no_dates.html`: No date information
- `item_page_with_date.html`: Individual item page

---

## Migration Guide

### For Existing html_list Sources
No changes required. The collector will:
1. Create a default profile for the domain
2. Use sensible default selectors (article, a[href])
3. Enable item page recovery with K=10

### To Customize Extraction
Register a domain profile before running:
```python
from src.collectors.html_profile import DomainProfile, ProfileRegistry

profile = DomainProfile(
    domain="your-site.com",
    name="Your Site Profile",
    link_rules=LinkExtractionRule(container_selector=".your-class"),
)
ProfileRegistry.get_instance().register(profile)
```

### To Disable Item Page Recovery
```python
profile = DomainProfile(
    domain="your-site.com",
    name="Your Site Profile",
    enable_item_page_recovery=False,
)
```
