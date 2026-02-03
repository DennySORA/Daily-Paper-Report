"""Compatibility shim for configuration error hints."""

from src.features.config.error_hints import (
    ERROR_HINTS,
    FIELD_HINTS,
    format_validation_error,
    get_error_hint,
)


__all__ = [
    "ERROR_HINTS",
    "FIELD_HINTS",
    "get_error_hint",
    "format_validation_error",
]
