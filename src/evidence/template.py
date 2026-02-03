"""Compatibility shim for evidence templates."""

from src.features.evidence.template import (
    E2EReportTemplateData,
    StateTemplateData,
    render_e2e_report,
    render_state_md,
)


__all__ = [
    "E2EReportTemplateData",
    "StateTemplateData",
    "render_e2e_report",
    "render_state_md",
]
