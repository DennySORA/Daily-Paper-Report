"""Compatibility shim for topic schemas."""

from src.features.config.schemas.topics import (
    DedupeConfig,
    QuotasConfig,
    ScoringConfig,
    TopicConfig,
    TopicsConfig,
)


__all__ = [
    "DedupeConfig",
    "ScoringConfig",
    "TopicConfig",
    "QuotasConfig",
    "TopicsConfig",
]
