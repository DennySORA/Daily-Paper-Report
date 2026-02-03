"""Compatibility shims for store imports."""

from src.features.store import (
    ConnectionError,
    DateConfidence,
    HttpCacheEntry,
    Item,
    ItemEventType,
    ItemNotFoundError,
    MetricsRecorder,
    MigrationError,
    NullMetricsRecorder,
    Run,
    RunNotFoundError,
    RunState,
    RunStateError,
    RunStateMachine,
    StateStore,
    StateStoreError,
    StoreMetrics,
    UpsertResult,
    canonicalize_url,
    compute_content_hash,
)


__all__ = [
    # Errors
    "ConnectionError",
    "ItemNotFoundError",
    "MigrationError",
    "RunNotFoundError",
    "StateStoreError",
    # Hash utilities
    "compute_content_hash",
    # Metrics
    "MetricsRecorder",
    "NullMetricsRecorder",
    "StoreMetrics",
    # Models
    "DateConfidence",
    "HttpCacheEntry",
    "Item",
    "ItemEventType",
    "Run",
    "UpsertResult",
    # State machine
    "RunState",
    "RunStateMachine",
    "RunStateError",
    # Store
    "StateStore",
    # URL utilities
    "canonicalize_url",
]
