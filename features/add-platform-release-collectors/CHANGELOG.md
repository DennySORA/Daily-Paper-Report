# CHANGELOG.md - add-platform-release-collectors

## Feature Summary

**Feature Key**: `add-platform-release-collectors`
**Feature Name**: Add: Platform collectors for GitHub releases, Hugging Face org updates, and OpenReview venue monitoring

## Changes

### Added
- `src/collectors/platform/` - New platform collectors module
  - `rate_limiter.py` - Token-bucket rate limiter for per-platform QPS control
  - `metrics.py` - Platform-specific metrics tracking
  - `constants.py` - API URLs, rate limits, and default configurations
  - `github.py` - GitHub releases collector
  - `huggingface.py` - Hugging Face org models collector
  - `openreview.py` - OpenReview venue papers collector

- Unit tests in `tests/unit/test_collectors/test_platform/`
  - `test_rate_limiter.py` - Token bucket rate limiting tests
  - `test_github.py` - GitHub collector tests
  - `test_huggingface.py` - HuggingFace collector tests
  - `test_openreview.py` - OpenReview collector tests

- Integration tests in `tests/integration/`
  - `test_platform_collectors.py` - End-to-end platform collector tests

### Modified
- `src/collectors/runner.py` - Added platform collectors to runner
- `src/collectors/__init__.py` - Exported platform collector classes

### Configuration
- Sources can now use methods: `github_releases`, `hf_org`, `openreview_venue`
- Rate limiting configurable per platform via token bucket

### Metrics Added
- `github_api_calls_total` - Total GitHub API calls
- `hf_api_calls_total` - Total HuggingFace API calls
- `openreview_api_calls_total` - Total OpenReview API calls
- `platform_rate_limit_events_total` - Rate limit events by platform

## Breaking Changes
None

## Migration Guide
No migration needed. New collectors are additive.

## Testing Instructions
```bash
# Run all tests
uv run pytest

# Run platform-specific tests
uv run pytest tests/unit/test_collectors/test_platform/ -v
uv run pytest tests/integration/test_platform_collectors.py -v
```
