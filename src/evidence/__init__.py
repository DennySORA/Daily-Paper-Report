"""Compatibility shims for evidence imports."""

from src.features.evidence import (
    ArtifactInfo,
    ArtifactManifest,
    E2EReportTemplateData,
    EvidenceCapture,
    EvidenceMetrics,
    EvidenceState,
    EvidenceStateError,
    EvidenceStateMachine,
    EvidenceWriteError,
    EvidenceWriter,
    StateTemplateData,
    contains_secrets,
    get_secret_patterns,
    redact_content,
    render_e2e_report,
    render_state_md,
    scan_for_secrets,
)


__all__ = [
    # capture.py
    "ArtifactManifest",
    "EvidenceCapture",
    # writer.py
    "ArtifactInfo",
    "EvidenceWriteError",
    "EvidenceWriter",
    # template.py
    "E2EReportTemplateData",
    "StateTemplateData",
    "render_e2e_report",
    "render_state_md",
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
