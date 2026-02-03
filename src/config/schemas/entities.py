"""Compatibility shim for entity schemas."""

from src.features.config.schemas.entities import (
    EntitiesConfig,
    EntityConfig,
    EntityRegion,
    EntityType,
)


__all__ = ["EntityRegion", "EntityType", "EntityConfig", "EntitiesConfig"]
