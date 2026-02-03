"""Compatibility shim for evidence writer."""

from src.features.evidence.writer import (
    ArtifactInfo,
    EvidenceWriteError,
    EvidenceWriter,
)


__all__ = ["ArtifactInfo", "EvidenceWriteError", "EvidenceWriter"]
