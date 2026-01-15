"""Evidence capture module."""

from src.evidence.capture import (
    ArtifactInfo,
    ArtifactManifest,
    EvidenceCapture,
    EvidenceWriteError,
)
from src.evidence.metrics import EvidenceMetrics
from src.evidence.redact import (
    contains_secrets,
    get_secret_patterns,
    redact_content,
    scan_for_secrets,
)
from src.evidence.state_machine import (
    EvidenceState,
    EvidenceStateError,
    EvidenceStateMachine,
)


__all__ = [
    # capture.py
    "ArtifactInfo",
    "ArtifactManifest",
    "EvidenceCapture",
    "EvidenceWriteError",
    # metrics.py
    "EvidenceMetrics",
    # redact.py
    "contains_secrets",
    "get_secret_patterns",
    "redact_content",
    "scan_for_secrets",
    # state_machine.py
    "EvidenceState",
    "EvidenceStateError",
    "EvidenceStateMachine",
]
