"""Compatibility shim for configuration state machine."""

from src.features.config.state_machine import (
    ConfigState,
    ConfigStateError,
    ConfigStateMachine,
)


__all__ = ["ConfigState", "ConfigStateError", "ConfigStateMachine"]
