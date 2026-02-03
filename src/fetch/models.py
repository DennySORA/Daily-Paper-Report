"""Compatibility shim for fetch models."""

from src.features.fetch.models import (
    FetchError,
    FetchErrorClass,
    FetchResult,
    ResponseSizeExceededError,
    RetryPolicy,
)


__all__ = [
    "FetchErrorClass",
    "FetchError",
    "FetchResult",
    "RetryPolicy",
    "ResponseSizeExceededError",
]
