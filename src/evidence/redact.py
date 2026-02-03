"""Compatibility shim for evidence redaction."""

from src.features.evidence.redact import (
    SecretMatch,
    contains_secrets,
    get_secret_patterns,
    redact_content,
    scan_for_secrets,
)


__all__ = [
    "SecretMatch",
    "scan_for_secrets",
    "redact_content",
    "contains_secrets",
    "get_secret_patterns",
]
