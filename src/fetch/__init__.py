"""Compatibility shims for fetch imports."""

from src.features.fetch import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_MAX_RESPONSE_SIZE_BYTES,
    HTTP_STATUS_NOT_MODIFIED,
    HTTP_STATUS_OK_MAX,
    HTTP_STATUS_OK_MIN,
    HTTP_STATUS_TOO_MANY_REQUESTS,
    MAX_RETRY_AFTER_SECONDS,
    CacheManager,
    DomainProfile,
    FetchConfig,
    FetchError,
    FetchErrorClass,
    FetchMetrics,
    FetchResult,
    HttpFetcher,
    ResponseSizeExceededError,
    RetryPolicy,
    redact_headers,
    redact_url_credentials,
)


__all__ = [
    # Client
    "HttpFetcher",
    # Cache
    "CacheManager",
    # Config
    "FetchConfig",
    "DomainProfile",
    # Models
    "FetchResult",
    "FetchError",
    "FetchErrorClass",
    "RetryPolicy",
    "ResponseSizeExceededError",
    # Constants
    "HTTP_STATUS_OK_MIN",
    "HTTP_STATUS_OK_MAX",
    "HTTP_STATUS_NOT_MODIFIED",
    "HTTP_STATUS_TOO_MANY_REQUESTS",
    "DEFAULT_MAX_RESPONSE_SIZE_BYTES",
    "DEFAULT_CHUNK_SIZE",
    "MAX_RETRY_AFTER_SECONDS",
    # Metrics
    "FetchMetrics",
    # Redaction
    "redact_headers",
    "redact_url_credentials",
]
