"""Base enricher protocol and result models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from src.store.models import Item


@dataclass(frozen=True)
class EnricherResult:
    """Result of enrichment for a single item.

    Attributes:
        item_url: URL of the enriched item (primary key).
        success: Whether enrichment succeeded.
        enriched_data: Dictionary of enriched fields to merge into raw_json.
        error_message: Error message if enrichment failed.
    """

    item_url: str
    success: bool
    enriched_data: dict[str, object] = field(default_factory=dict)
    error_message: str | None = None


@dataclass
class EnrichmentBatchResult:
    """Result of batch enrichment operation.

    Attributes:
        results: List of individual enrichment results.
        total_items: Total number of items processed.
        successful: Number of successfully enriched items.
        failed: Number of failed enrichments.
        skipped: Number of items skipped (e.g., no arxiv_id).
    """

    results: list[EnricherResult]
    total_items: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0


@runtime_checkable
class Enricher(Protocol):
    """Protocol for item enrichers."""

    def enrich(self, item: Item) -> EnricherResult:
        """Enrich a single item with external data.

        Args:
            item: Item to enrich.

        Returns:
            EnricherResult with enriched data or error.
        """
        ...

    def enrich_batch(self, items: list[Item]) -> EnrichmentBatchResult:
        """Enrich multiple items with external data.

        Args:
            items: Items to enrich.

        Returns:
            EnrichmentBatchResult with all results.
        """
        ...


class BaseEnricher(ABC):
    """Abstract base class for item enrichers.

    Provides common functionality for enrichers that augment items
    with data from external sources (e.g., Semantic Scholar, OpenAlex).
    """

    def __init__(self, run_id: str = "") -> None:
        """Initialize the enricher.

        Args:
            run_id: Run identifier for logging and metrics.
        """
        self._run_id = run_id

    @abstractmethod
    def enrich(self, item: Item) -> EnricherResult:
        """Enrich a single item with external data.

        Args:
            item: Item to enrich.

        Returns:
            EnricherResult with enriched data or error.
        """
        ...

    def enrich_batch(self, items: list[Item]) -> EnrichmentBatchResult:
        """Enrich multiple items with external data.

        Default implementation calls enrich() for each item.
        Subclasses may override for batch API calls.

        Args:
            items: Items to enrich.

        Returns:
            EnrichmentBatchResult with all results.
        """
        results: list[EnricherResult] = []
        successful = 0
        failed = 0
        skipped = 0

        for item in items:
            result = self.enrich(item)
            results.append(result)

            if result.success:
                if result.enriched_data:
                    successful += 1
                else:
                    skipped += 1
            else:
                failed += 1

        return EnrichmentBatchResult(
            results=results,
            total_items=len(items),
            successful=successful,
            failed=failed,
            skipped=skipped,
        )
