"""Shared helper functions for platform collectors.

This module provides utility functions used across platform collectors
to reduce code duplication and improve maintainability.
"""

import os
from typing import Any

from src.collectors.platform.constants import (
    AUTH_TOKEN_ENV_VARS,
    HTTP_STATUS_FORBIDDEN,
    HTTP_STATUS_UNAUTHORIZED,
)
from src.fetch.models import FetchErrorClass, FetchResult


def is_auth_error(result: FetchResult) -> bool:
    """Check if a fetch result represents an authentication error.

    Args:
        result: The fetch result to check.

    Returns:
        True if the result indicates a 401 or 403 auth error.
    """
    if not result.error:
        return False

    return result.status_code in (HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_FORBIDDEN) or (
        result.error.error_class == FetchErrorClass.HTTP_4XX
        and result.status_code in (HTTP_STATUS_UNAUTHORIZED, HTTP_STATUS_FORBIDDEN)
    )


def get_auth_token(platform: str) -> str | None:
    """Get the authentication token for a platform from environment.

    Args:
        platform: Platform identifier (e.g., 'github', 'huggingface').

    Returns:
        Token value or None if not set.
    """
    env_var = AUTH_TOKEN_ENV_VARS.get(platform)
    if env_var:
        return os.environ.get(env_var)
    return None


def build_bearer_auth_header(token: str | None) -> dict[str, str]:
    """Build Authorization header with Bearer token if provided.

    Args:
        token: Optional Bearer token.

    Returns:
        Dictionary with Authorization header, or empty dict if no token.
    """
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def extract_nested_value(field: Any) -> Any:
    """Extract value from potentially nested OpenReview-style field.

    OpenReview API returns some fields as either direct values or
    as objects with a 'value' key. This helper handles both cases.

    Args:
        field: Field value that may be nested.

    Returns:
        Extracted value (unwrapped from dict if needed).

    Examples:
        >>> extract_nested_value("direct value")
        'direct value'
        >>> extract_nested_value({"value": "nested value"})
        'nested value'
    """
    if isinstance(field, dict):
        return field.get("value")
    return field


def build_pdf_url(pdf_field: Any, forum_id: str) -> str | None:
    """Build full PDF URL from OpenReview PDF field.

    Handles various PDF URL formats:
    - Relative paths starting with /pdf
    - Full HTTP URLs
    - Falls back to constructed URL if neither

    Args:
        pdf_field: PDF field value (may be nested dict or string).
        forum_id: Forum ID for fallback URL construction.

    Returns:
        Full PDF URL or None if no PDF field.
    """
    pdf = extract_nested_value(pdf_field)
    if not pdf:
        return None

    if isinstance(pdf, str):
        if pdf.startswith("/pdf"):
            return f"https://openreview.net{pdf}"
        if pdf.startswith("http"):
            return pdf
        return f"https://openreview.net/pdf?id={forum_id}"

    return None


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to a maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum allowed length.

    Returns:
        Truncated text if longer than max_length, otherwise original.
    """
    if len(text) > max_length:
        return text[:max_length]
    return text
