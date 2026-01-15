# Changelog - add-http-fetch-layer

## [Unreleased]

### Added

- **New `src/fetch/` module** - Robust HTTP fetch layer with caching, retries, and failure isolation

#### Models (`src/fetch/models.py`)
- `FetchErrorClass` enum - Categorizes fetch errors (NETWORK_TIMEOUT, HTTP_5XX, RATE_LIMITED, etc.)
- `FetchError` dataclass - Typed error with error_class, message, status_code, retry_after
- `FetchResult` dataclass - Typed result with status_code, final_url, headers, body_bytes, cache_hit, error
- `RetryPolicy` model - Configurable retry behavior (max_retries, base_delay_ms, exponential_base)

#### Configuration (`src/fetch/config.py`)
- `DomainProfile` model - Per-domain header configuration
- `FetchConfig` model - Main configuration with user_agent, timeout, max_response_size, retry_policy

#### Metrics (`src/fetch/metrics.py`)
- `FetchMetrics` singleton - Tracks http_requests_total, http_cache_hits_total, http_retry_total, http_failures_total

#### Client (`src/fetch/client.py`)
- `HttpFetcher` class - Main HTTP client with:
  - Configurable timeout and retry policy
  - Exponential backoff with jitter
  - ETag/Last-Modified conditional request support
  - Maximum response size enforcement (default 10 MB)
  - Header redaction for logging (Authorization, Cookie)
  - Integration with StateStore for http_cache persistence
  - Failure isolation (fail_fast=False by default)

#### Security (`src/fetch/redact.py`)
- `redact_headers()` function - Redacts Authorization and Cookie headers in logs

### Dependencies

- Added `httpx>=0.27.0` for HTTP client functionality

### Tests

- Unit tests for retry policy decisions
- Unit tests for 429 Retry-After handling
- Unit tests for header redaction
- Unit tests for response size enforcement
- Integration tests for ETag/Last-Modified conditional requests
- Integration tests for 304 cache hit behavior

## Migration Notes

No breaking changes. The fetch layer is a new addition that integrates with existing `StateStore.http_cache` functionality.

## Usage Example

```python
from src.fetch.client import HttpFetcher
from src.fetch.config import FetchConfig, RetryPolicy
from src.store.store import StateStore

# Configure
config = FetchConfig(
    user_agent='my-app/1.0',
    default_timeout_seconds=30.0,
    max_response_size_bytes=10 * 1024 * 1024,  # 10 MB
    retry_policy=RetryPolicy(
        max_retries=3,
        base_delay_ms=1000,
    ),
)

# Create fetcher with store for caching
store = StateStore('state.sqlite')
store.connect()

fetcher = HttpFetcher(config=config, store=store, run_id='my-run-id')

# Fetch with caching
result = fetcher.fetch(
    source_id='my-source',
    url='https://example.com/api/data',
)

if result.error:
    print(f'Error: {result.error.error_class} - {result.error.message}')
else:
    print(f'Status: {result.status_code}, Cache hit: {result.cache_hit}')
    print(f'Body size: {len(result.body_bytes)} bytes')
```
