"""Compatibility shim for store errors."""

from src.features.store.errors import (
    ConnectionError,
    ItemNotFoundError,
    MigrationError,
    RunNotFoundError,
    StateStoreError,
)


__all__ = [
    "StateStoreError",
    "ConnectionError",
    "RunNotFoundError",
    "ItemNotFoundError",
    "MigrationError",
]
