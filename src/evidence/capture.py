"""Compatibility shim for evidence capture."""

from src.features.evidence.capture import (
    ArtifactInfo,
    ArtifactManifest,
    EvidenceCapture,
    EvidenceWriteError,
)


__all__ = ["ArtifactInfo", "ArtifactManifest", "EvidenceCapture", "EvidenceWriteError"]
