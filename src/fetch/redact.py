"""Compatibility shim for fetch redaction."""

from src.features.fetch.redact import (
    REDACTED_VALUE,
    is_sensitive_header,
    redact_headers,
    redact_url_credentials,
)


__all__ = [
    "REDACTED_VALUE",
    "redact_headers",
    "redact_url_credentials",
    "is_sensitive_header",
]
