"""Compatibility shim for configuration loader."""

from src.features.config.loader import ConfigLoader, ConfigValidationError


__all__ = ["ConfigLoader", "ConfigValidationError"]
