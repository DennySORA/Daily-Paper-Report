"""Compatibility shim for status computation."""

from src.features.status.computer import IllegalStatusTransitionError, StatusComputer


__all__ = ["IllegalStatusTransitionError", "StatusComputer"]
