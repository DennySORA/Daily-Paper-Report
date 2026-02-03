"""Compatibility shim for status error mapping."""

from src.features.status.error_mapper import (
    map_fetch_error_to_reason_code,
    map_http_status_to_reason_code,
    map_parse_error_to_reason_code,
)


__all__ = [
    "map_fetch_error_to_reason_code",
    "map_http_status_to_reason_code",
    "map_parse_error_to_reason_code",
]
