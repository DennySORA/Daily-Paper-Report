# Refactor Notes - add-http-fetch-layer

## Refactoring Summary

This document tracks the refactoring and optimization changes made during Prompt #3 of the add-http-fetch-layer feature implementation.

## Changes Made

### 1. Created Shared Constants Module (`src/fetch/constants.py`)

**Problem**: HTTP status code constants were duplicated in `models.py` and `client.py`, violating DRY principle.

**Solution**: Created a centralized `constants.py` module with all HTTP-related constants:
- `HTTP_STATUS_OK_MIN`, `HTTP_STATUS_OK_MAX` (200-300 range)
- `HTTP_STATUS_NOT_MODIFIED` (304)
- `HTTP_STATUS_BAD_REQUEST` (400)
- `HTTP_STATUS_TOO_MANY_REQUESTS` (429)
- `HTTP_STATUS_SERVER_ERROR_MIN`, `HTTP_STATUS_SERVER_ERROR_MAX` (500-600 range)
- `DEFAULT_MAX_RESPONSE_SIZE_BYTES` (10 MB)
- `DEFAULT_CHUNK_SIZE` (8192 bytes)
- `MAX_RETRY_AFTER_SECONDS` (60 seconds)

**Files modified**:
- `src/fetch/constants.py` (new)
- `src/fetch/models.py` (import from constants)
- `src/fetch/config.py` (import from constants)
- `src/fetch/client.py` (import from constants)
- `src/fetch/__init__.py` (export constants)
- `tests/unit/test_fetch/test_response_size.py` (update import)

**Risk**: Very low - additive change with no behavior modification.

### 2. Moved `ResponseSizeExceededError` to `models.py`

**Problem**: The exception class was at the bottom of `client.py`, separated from related error types.

**Solution**: Moved to `models.py` with other error-related classes (FetchError, FetchErrorClass).

**Files modified**:
- `src/fetch/models.py` (added exception class)
- `src/fetch/client.py` (removed duplicate, import from models)
- `src/fetch/__init__.py` (export from models)

**Risk**: Very low - pure reorganization.

### 3. Moved Inline Imports to Module Level

**Problem**: `_parse_retry_after` method imported `parsedate_to_datetime` inside the function body. `RetryPolicy.get_delay_ms` imported `random` inside the method.

**Solution**: Moved imports to module level for better performance and Python best practices.

**Files modified**:
- `src/fetch/client.py` (added `from email.utils import parsedate_to_datetime`)
- `src/fetch/models.py` (added `import random` at top)

**Risk**: Very low - performance improvement only.

### 4. Extracted `CacheManager` Class (`src/fetch/cache.py`)

**Problem**: `HttpFetcher` class had multiple responsibilities including cache management, violating SRP.

**Solution**: Created a dedicated `CacheManager` class that encapsulates:
- `get_conditional_headers(source_id)` - Get If-None-Match/If-Modified-Since headers
- `update_from_result(source_id, result)` - Update cache after fetch
- `get_cached_status(source_id)` - Get last HTTP status for a source

**Design decisions**:
- Uses `CacheStore` Protocol for dependency inversion (DIP)
- Own structured logging with `component="cache"`
- Injected into `HttpFetcher` via constructor

**Files modified**:
- `src/fetch/cache.py` (new)
- `src/fetch/client.py` (delegate to CacheManager, removed `_update_cache` method)
- `src/fetch/__init__.py` (export CacheManager)

**Risk**: Low - same behavior, better separation of concerns.

### 5. Test Improvements

**Problem**: Integration tests used tuple unpacking on `server.server_address` which mypy flagged as potentially unsafe.

**Solution**: Created `get_server_url(server, path)` helper function that safely extracts host/port and handles potential bytes->str conversion.

**Files modified**:
- `tests/integration/test_fetch_conditional.py`

**Risk**: Very low - test code only.

## SOLID Compliance

| Principle | Status | Evidence |
|-----------|--------|----------|
| **SRP** | Improved | CacheManager handles cache logic, HttpFetcher focuses on HTTP operations |
| **OCP** | Maintained | Protocol-based CacheStore allows extension without modification |
| **LSP** | Maintained | No inheritance issues |
| **ISP** | Maintained | CacheStore protocol has minimal interface |
| **DIP** | Improved | HttpFetcher depends on CacheStore abstraction, not concrete StateStore |

## Quality Verification

| Check | Status |
|-------|--------|
| `uv run ruff check .` | 0 errors |
| `uv run ruff format --check .` | All files formatted |
| `uv run mypy .` | 0 errors |
| `uv run pytest` | 289 passed in 7.82s |
| Coverage | 76% overall |

## Rollback Plan

Each refactoring change is independent and can be reverted individually:

1. **Constants module**: Revert `constants.py` and restore inline constants
2. **Exception move**: Move `ResponseSizeExceededError` back to `client.py`
3. **Import moves**: Move imports back into function bodies
4. **CacheManager**: Merge cache logic back into HttpFetcher

All changes preserve existing API signatures - no breaking changes to consumers.

## Future Considerations (Not Implemented)

The following were evaluated but deferred:

1. **HTTP Transport Abstraction**: Would improve testability but adds complexity. Current integration tests with local HTTP servers work well.

2. **Metrics Dependency Injection**: Current singleton pattern with `reset()` works fine for testing.

3. **Async Support**: Could add `AsyncHttpFetcher` in the future but not required for current use cases.

4. **OpenTelemetry Tracing**: Could add span context to fetch operations for distributed tracing.

## Files Created

- `src/fetch/constants.py` - Shared HTTP constants
- `src/fetch/cache.py` - CacheManager class
- `features/add-http-fetch-layer/REFACTOR_NOTES.md` - This file

## Files Modified

- `src/fetch/models.py` - Added ResponseSizeExceededError, moved random import
- `src/fetch/config.py` - Import DEFAULT_MAX_RESPONSE_SIZE_BYTES from constants
- `src/fetch/client.py` - Delegate to CacheManager, use constants, module-level imports
- `src/fetch/__init__.py` - Export new items
- `tests/unit/test_fetch/test_response_size.py` - Update constant import
- `tests/integration/test_fetch_conditional.py` - Add get_server_url helper
