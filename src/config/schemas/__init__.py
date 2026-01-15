"""Configuration schema definitions."""

from src.config.schemas.base import LinkType, SourceKind, SourceMethod, SourceTier
from src.config.schemas.entities import EntitiesConfig, EntityConfig
from src.config.schemas.sources import SourceConfig, SourcesConfig
from src.config.schemas.topics import (
    DedupeConfig,
    ScoringConfig,
    TopicConfig,
    TopicsConfig,
)


__all__ = [
    "DedupeConfig",
    "EntitiesConfig",
    "EntityConfig",
    "LinkType",
    "ScoringConfig",
    "SourceConfig",
    "SourceKind",
    "SourceMethod",
    "SourcesConfig",
    "SourceTier",
    "TopicConfig",
    "TopicsConfig",
]
