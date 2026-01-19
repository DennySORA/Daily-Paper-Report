"""Semantic Scholar enricher for citation data."""

import json

import structlog

from src.collectors.arxiv.utils import extract_arxiv_id as _extract_arxiv_id_from_url
from src.collectors.platform.constants import (
    PLATFORM_SEMANTIC_SCHOLAR,
    SEMANTIC_SCHOLAR_API_BASE_URL,
    SEMANTIC_SCHOLAR_AUTHENTICATED_MAX_QPS,
    SEMANTIC_SCHOLAR_DEFAULT_MAX_QPS,
)
from src.collectors.platform.helpers import get_auth_token
from src.collectors.platform.rate_limiter import (
    TokenBucketRateLimiter,
    get_platform_rate_limiter,
)
from src.enricher.base import BaseEnricher, EnricherResult, EnrichmentBatchResult
from src.fetch.client import HttpFetcher
from src.store.models import Item


logger = structlog.get_logger()

# Semantic Scholar API fields to retrieve
CITATION_FIELDS = "citationCount,influentialCitationCount,publicationDate,venue"

# HTTP status codes
HTTP_NOT_FOUND = 404


def extract_arxiv_id(item: Item) -> str | None:
    """Extract arXiv ID from an item.

    Delegates to central arXiv utility for URL extraction, but also
    checks raw_json for explicit arxiv_id field.

    Checks:
    1. raw_json "arxiv_id" field
    2. URL containing arxiv.org (via central utility)

    Args:
        item: Item to extract arXiv ID from.

    Returns:
        arXiv ID string or None if not found.
    """
    # Check raw_json first for explicit arxiv_id
    try:
        raw = json.loads(item.raw_json)
        if arxiv_id := raw.get("arxiv_id"):
            return str(arxiv_id)
    except (json.JSONDecodeError, KeyError):
        pass

    # Check item URL using central utility
    return _extract_arxiv_id_from_url(item.url)


class SemanticScholarEnricher(BaseEnricher):
    """Enricher that fetches citation data from Semantic Scholar API.

    Uses the Semantic Scholar Graph API to fetch:
    - citationCount: Total number of citations
    - influentialCitationCount: Citations from influential papers
    - publicationDate: Official publication date
    - venue: Publication venue (conference/journal)

    Rate limiting:
    - Unauthenticated: 100 requests per 5 minutes (~0.33 QPS)
    - With API key: 100 requests per minute (~1.67 QPS)
    """

    def __init__(
        self,
        run_id: str = "",
        http_client: HttpFetcher | None = None,
        rate_limiter: TokenBucketRateLimiter | None = None,
    ) -> None:
        """Initialize the Semantic Scholar enricher.

        Args:
            run_id: Run identifier for logging.
            http_client: HTTP client for API calls.
            rate_limiter: Rate limiter for API throttling.
        """
        super().__init__(run_id)
        self._http_client = http_client
        self._log = logger.bind(
            component="enricher",
            subcomponent="semantic_scholar",
            run_id=run_id,
        )

        # Determine QPS based on auth
        has_api_key = bool(get_auth_token(PLATFORM_SEMANTIC_SCHOLAR))
        max_qps = (
            SEMANTIC_SCHOLAR_AUTHENTICATED_MAX_QPS
            if has_api_key
            else SEMANTIC_SCHOLAR_DEFAULT_MAX_QPS
        )

        self._rate_limiter = rate_limiter or get_platform_rate_limiter(
            platform=PLATFORM_SEMANTIC_SCHOLAR,
            max_qps=max_qps,
        )
        self._has_api_key = has_api_key

    def enrich(self, item: Item) -> EnricherResult:
        """Enrich a single item with Semantic Scholar citation data.

        Args:
            item: Item to enrich.

        Returns:
            EnricherResult with citation data or error.
        """
        arxiv_id = extract_arxiv_id(item)

        if not arxiv_id:
            return EnricherResult(
                item_url=item.url,
                success=True,
                enriched_data={},
            )

        if self._http_client is None:
            return EnricherResult(
                item_url=item.url,
                success=False,
                error_message="HTTP client not configured",
            )

        # Apply rate limiting
        self._rate_limiter.acquire()

        try:
            result = self._fetch_paper_data(arxiv_id)
            if result is None:
                return EnricherResult(
                    item_url=item.url,
                    success=True,
                    enriched_data={},
                )

            return EnricherResult(
                item_url=item.url,
                success=True,
                enriched_data=result,
            )

        except Exception as e:
            self._log.warning(
                "enrichment_failed",
                arxiv_id=arxiv_id,
                error=str(e),
            )
            return EnricherResult(
                item_url=item.url,
                success=False,
                error_message=str(e),
            )

    def _fetch_paper_data(self, arxiv_id: str) -> dict[str, object] | None:
        """Fetch paper data from Semantic Scholar API.

        Args:
            arxiv_id: arXiv paper ID.

        Returns:
            Dictionary with citation data or None if not found.
        """
        if self._http_client is None:
            return None

        url = f"{SEMANTIC_SCHOLAR_API_BASE_URL}/paper/arXiv:{arxiv_id}?fields={CITATION_FIELDS}"
        headers = self._build_headers()

        result = self._http_client.fetch(
            source_id=PLATFORM_SEMANTIC_SCHOLAR,
            url=url,
            extra_headers=headers,
        )

        if not result.is_success:
            if result.status_code == HTTP_NOT_FOUND:
                # Paper not found in Semantic Scholar
                self._log.debug(
                    "paper_not_found",
                    arxiv_id=arxiv_id,
                )
                return None
            self._log.warning(
                "api_request_failed",
                arxiv_id=arxiv_id,
                status_code=result.status_code,
            )
            return None

        try:
            data = json.loads(result.body_bytes.decode("utf-8"))
            return self._parse_response(data)
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError) as e:
            self._log.warning(
                "response_parse_failed",
                arxiv_id=arxiv_id,
                error=str(e),
            )
            return None

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers for Semantic Scholar API.

        Returns:
            Headers dictionary with API key if available.
        """
        headers: dict[str, str] = {
            "Accept": "application/json",
        }

        if api_key := get_auth_token(PLATFORM_SEMANTIC_SCHOLAR):
            headers["x-api-key"] = api_key

        return headers

    def _parse_response(self, data: dict[str, object]) -> dict[str, object]:
        """Parse Semantic Scholar API response.

        Args:
            data: Raw API response.

        Returns:
            Parsed citation data.
        """
        result: dict[str, object] = {}

        if "citationCount" in data:
            result["citation_count"] = data["citationCount"]

        if "influentialCitationCount" in data:
            result["influential_citation_count"] = data["influentialCitationCount"]

        if "publicationDate" in data and data["publicationDate"]:
            result["publication_date"] = data["publicationDate"]

        if "venue" in data and data["venue"]:
            result["venue"] = data["venue"]

        return result

    def enrich_batch(self, items: list[Item]) -> EnrichmentBatchResult:
        """Enrich multiple items with Semantic Scholar data.

        Uses individual API calls with rate limiting.
        Future optimization: Use batch API endpoint for efficiency.

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

        self._log.info(
            "batch_enrichment_complete",
            total=len(items),
            successful=successful,
            failed=failed,
            skipped=skipped,
        )

        return EnrichmentBatchResult(
            results=results,
            total_items=len(items),
            successful=successful,
            failed=failed,
            skipped=skipped,
        )
