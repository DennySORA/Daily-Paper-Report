"""Enricher module for augmenting items with external data."""

from src.enricher.base import BaseEnricher, EnricherResult
from src.enricher.semantic_scholar import SemanticScholarEnricher


__all__ = [
    "BaseEnricher",
    "EnricherResult",
    "SemanticScholarEnricher",
]
