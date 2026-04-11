"""arXiv API collector for keyword-based queries.

This module provides a collector for querying the arXiv API with keyword searches
to find targeted papers (e.g., CN frontier model technical reports).
"""

import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol
from urllib.parse import urlencode
from xml.etree.ElementTree import Element, ParseError

import defusedxml.ElementTree as DefusedET
import structlog

from src.collectors.arxiv.constants import (
    ARXIV_API_BASE_URL,
    ARXIV_API_RATE_LIMIT_SECONDS,
    ARXIV_API_DEFAULT_MAX_RESULTS,
    FIELD_ARXIV_ID,
    FIELD_SOURCE,
    SOURCE_TYPE_API,
)
from src.collectors.arxiv.utils import extract_arxiv_id
from src.collectors.base import BaseCollector, CollectorResult
from src.collectors.errors import CollectorErrorClass, ErrorRecord
from src.collectors.state_machine import SourceState, SourceStateMachine
from src.features.config.schemas.sources import SourceConfig
from src.features.fetch.client import HttpFetcher
from src.features.store.hash import compute_content_hash
from src.features.store.models import DateConfidence, Item


logger = structlog.get_logger()

# Atom namespace
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
ARXIV_API_MAX_PAGES = 100
ARXIV_API_MAX_KEYWORD_BACKFILL_PAGES = 2


class RateLimiterProtocol(Protocol):
    """Protocol for rate limiting.

    Allows dependency injection of rate limiter for testing.
    """

    def wait_if_needed(self) -> None:
        """Wait if needed to respect rate limit."""
        ...


@dataclass
class ArxivApiConfig:
    """Configuration for arXiv API queries.

    Attributes:
        query: Search query string.
        max_results: Maximum results to return.
        sort_by: Field to sort by (submittedDate, lastUpdatedDate, relevance).
        sort_order: Sort order (ascending, descending).
    """

    query: str
    max_results: int = 50
    start: int = 0
    sort_by: str = "submittedDate"
    sort_order: str = "descending"


class ArxivApiRateLimiter:
    """Rate limiter for arXiv API requests.

    Enforces a minimum interval between requests to respect arXiv API etiquette.
    Implements RateLimiterProtocol for dependency injection support.
    """

    def __init__(self, min_interval: float = ARXIV_API_RATE_LIMIT_SECONDS) -> None:
        """Initialize the rate limiter.

        Args:
            min_interval: Minimum interval between requests in seconds.
                         Defaults to 1 second per arXiv API guidelines.
        """
        self._min_interval = min_interval
        self._last_request_time: float = 0.0

    def wait_if_needed(self) -> None:
        """Wait if needed to respect rate limit."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            sleep_time = self._min_interval - elapsed
            time.sleep(sleep_time)
        self._last_request_time = time.monotonic()


class ArxivApiCollector(BaseCollector):
    """Collector for arXiv API keyword queries.

    Queries the arXiv API with configurable search terms and returns papers
    matching the query. Respects arXiv API rate limits.

    API documentation: https://info.arxiv.org/help/api/index.html
    """

    # Default shared rate limiter across all instances
    _default_rate_limiter: RateLimiterProtocol = ArxivApiRateLimiter()

    def __init__(
        self,
        strip_params: list[str] | None = None,
        run_id: str = "",
        rate_limiter: RateLimiterProtocol | None = None,
    ) -> None:
        """Initialize the arXiv API collector.

        Args:
            strip_params: URL parameters to strip (not used for arXiv).
            run_id: Run identifier for logging.
            rate_limiter: Optional rate limiter for dependency injection.
                         Defaults to shared ArxivApiRateLimiter singleton.
        """
        # Import here to avoid circular import and allow DI
        from src.collectors.arxiv.metrics import ArxivMetrics

        super().__init__(strip_params)
        self._run_id = run_id
        self._rate_limiter = rate_limiter or self._default_rate_limiter
        self._metrics = ArxivMetrics.get_instance()

    def collect(
        self,
        source_config: SourceConfig,
        http_client: HttpFetcher,
        now: datetime,
        lookback_hours: int = 24,
        max_items_override: int | None = None,
    ) -> CollectorResult:
        """Collect items from arXiv API.

        Args:
            source_config: Configuration for the source.
            http_client: HTTP client for fetching.
            now: Current timestamp for consistency.

        Returns:
            CollectorResult with items and status.
        """
        log = logger.bind(
            component="arxiv",
            run_id=self._run_id,
            source_id=source_config.id,
            mode="api",
        )

        state_machine = SourceStateMachine(
            source_id=source_config.id,
            run_id=self._run_id,
        )

        parse_warnings: list[str] = []

        resolved_max_items = self.resolve_max_items(
            source_config.max_items,
            max_items_override,
        )
        fetch_max_items = self.resolve_fetch_limit(
            max_items=(
                resolved_max_items
                if resolved_max_items > 0
                else source_config.max_items
            ),
            fallback_limit=ARXIV_API_DEFAULT_MAX_RESULTS,
        )

        try:
            state_machine.to_fetching()

            try:
                items, newest_id, oldest_id = self._collect_query_window(
                    source_config=source_config,
                    http_client=http_client,
                    now=now,
                    lookback_hours=lookback_hours,
                    fetch_max_items=fetch_max_items,
                    max_pages=self._resolve_max_pages(source_config, lookback_hours),
                    resolved_max_items=resolved_max_items,
                    parse_warnings=parse_warnings,
                )
            except RuntimeError as e:
                state_machine.to_failed()
                return CollectorResult(
                    items=[],
                    error=ErrorRecord(
                        error_class=CollectorErrorClass.FETCH,
                        message=str(e),
                        source_id=source_config.id,
                    ),
                    parse_warnings=parse_warnings,
                    state=SourceState.SOURCE_FAILED,
                )

            state_machine.to_parsing()

            if not items:
                log.info("empty_response")
                state_machine.to_done()
                return CollectorResult(
                    items=[],
                    parse_warnings=parse_warnings,
                    state=SourceState.SOURCE_DONE,
                )

            # Filter by time: only keep items published in the last 24 hours
            items = self.filter_items_by_time(
                items=items,
                now=now,
                lookback_hours=lookback_hours,
                source_id=source_config.id,
            )

            items = self.sort_items_deterministically(items)
            items = self.enforce_max_items(items, resolved_max_items)

            self._metrics.record_items(len(items), "api")

            log.info(
                "collection_complete",
                items_emitted=len(items),
                query=str(source_config.query or ""),
                result_count=len(items),
                newest_id=newest_id,
                oldest_id=oldest_id,
            )

            state_machine.to_done()
            return CollectorResult(
                items=items,
                parse_warnings=parse_warnings,
                state=SourceState.SOURCE_DONE,
            )

        except Exception as e:  # noqa: BLE001
            log.warning("unexpected_error", error=str(e))
            self._metrics.record_error("parse")
            state_machine.to_failed()
            return CollectorResult(
                items=[],
                error=ErrorRecord(
                    error_class=CollectorErrorClass.PARSE,
                    message=f"Unexpected error: {e}",
                    source_id=source_config.id,
                ),
                parse_warnings=parse_warnings,
                state=SourceState.SOURCE_FAILED,
            )

    def _build_api_config(
        self,
        source_config: SourceConfig,
        max_results: int,
        start: int = 0,
    ) -> ArxivApiConfig:
        """Build API configuration from source config.

        Args:
            source_config: Source configuration.
            max_results: Maximum results for API request.

        Returns:
            ArxivApiConfig instance.
        """
        # Get query from source_config.query field
        return ArxivApiConfig(
            query=str(source_config.query or ""),
            max_results=max(1, max_results),
            start=max(0, start),
            sort_by="submittedDate",
            sort_order="descending",
        )

    def _build_api_url(self, config: ArxivApiConfig) -> str:
        """Build arXiv API URL from config.

        Args:
            config: API configuration.

        Returns:
            Full API URL.
        """
        params = {
            "search_query": config.query,
            "start": config.start,
            "max_results": config.max_results,
            "sortBy": config.sort_by,
            "sortOrder": config.sort_order,
        }
        return f"{ARXIV_API_BASE_URL}?{urlencode(params)}"

    def _is_keyword_backfill(
        self,
        source_config: SourceConfig,
        lookback_hours: int,
    ) -> bool:
        """Whether this query is a supplementary keyword backfill."""
        if lookback_hours <= 24:
            return False
        query = str(source_config.query or "").strip()
        return not query.startswith("cat:")

    def _resolve_max_pages(
        self,
        source_config: SourceConfig,
        lookback_hours: int,
    ) -> int:
        """Resolve pagination budget for this query window."""
        if self._is_keyword_backfill(source_config, lookback_hours):
            return ARXIV_API_MAX_KEYWORD_BACKFILL_PAGES
        return ARXIV_API_MAX_PAGES

    def _collect_query_window(
        self,
        source_config: SourceConfig,
        http_client: HttpFetcher,
        now: datetime,
        lookback_hours: int,
        fetch_max_items: int,
        max_pages: int,
        resolved_max_items: int,
        parse_warnings: list[str],
    ) -> tuple[list[Item], str | None, str | None]:
        """Fetch paginated arXiv results until the lookback window is covered."""
        log = logger.bind(
            component="arxiv",
            run_id=self._run_id,
            source_id=source_config.id,
            mode="api",
        )
        cutoff = now - timedelta(hours=lookback_hours)
        if cutoff.tzinfo is None:
            cutoff = cutoff.replace(tzinfo=UTC)

        items: list[Item] = []
        seen_urls: set[str] = set()
        newest_id: str | None = None
        oldest_id: str | None = None
        partial_fetch_fail_ok = self._is_keyword_backfill(
            source_config,
            lookback_hours,
        )

        for page_index in range(max_pages):
            start = page_index * fetch_max_items
            api_config = self._build_api_config(
                source_config=source_config,
                max_results=fetch_max_items,
                start=start,
            )
            api_url = self._build_api_url(api_config)

            log.info(
                "api_query",
                query=api_config.query,
                max_results=api_config.max_results,
                start=api_config.start,
                resolved_max_items=resolved_max_items,
            )

            self._rate_limiter.wait_if_needed()

            start_time = time.monotonic()
            try:
                result = http_client.fetch(
                    source_id=source_config.id,
                    url=api_url,
                    extra_headers={"Accept": "application/atom+xml"},
                )
            except Exception as e:
                if partial_fetch_fail_ok and page_index > 0 and items:
                    log.warning(
                        "api_page_fetch_failed_after_partial_success",
                        start=api_config.start,
                        error=str(e),
                    )
                    break
                raise RuntimeError(str(e)) from e
            latency_ms = (time.monotonic() - start_time) * 1000
            self._metrics.record_api_latency(latency_ms)

            if result.error or result.status_code >= 400:
                error_message = (
                    str(result.error)
                    if result.error
                    else f"HTTP {result.status_code}"
                )
                log.warning(
                    "fetch_failed",
                    error_class=(
                        result.error.error_class.value
                        if hasattr(result.error, "error_class")
                        else "unknown"
                    ),
                    status_code=result.status_code,
                    start=api_config.start,
                )
                self._metrics.record_error(
                    "timeout" if "timeout" in error_message.lower() else "fetch"
                )
                if partial_fetch_fail_ok and page_index > 0 and items:
                    log.warning(
                        "api_page_fetch_failed_after_partial_success",
                        start=api_config.start,
                        status_code=result.status_code,
                        error=error_message,
                    )
                    break
                raise RuntimeError(error_message)

            page_items, page_newest_id, page_oldest_id = self._parse_atom_response(
                body=result.body_bytes,
                source_config=source_config,
                parse_warnings=parse_warnings,
            )

            if not page_items:
                break

            if newest_id is None:
                newest_id = page_newest_id
            if page_oldest_id is not None:
                oldest_id = page_oldest_id

            oldest_published_at: datetime | None = None
            for item in page_items:
                if item.url in seen_urls:
                    continue
                seen_urls.add(item.url)
                items.append(item)
                if item.published_at is None:
                    continue
                item_published = item.published_at
                if item_published.tzinfo is None:
                    item_published = item_published.replace(tzinfo=UTC)
                if oldest_published_at is None or item_published < oldest_published_at:
                    oldest_published_at = item_published

            if len(page_items) < fetch_max_items:
                break
            if oldest_published_at is not None and oldest_published_at < cutoff:
                break
        else:
            log.warning(
                "api_pagination_limit_reached",
                max_pages=max_pages,
                fetch_max_items=fetch_max_items,
                items_collected=len(items),
            )

        return items, newest_id, oldest_id

    def _parse_atom_response(
        self,
        body: bytes,
        source_config: SourceConfig,
        parse_warnings: list[str],
    ) -> tuple[list[Item], str | None, str | None]:
        """Parse Atom API response.

        Args:
            body: Response body bytes.
            source_config: Source configuration.
            parse_warnings: List to append warnings to.

        Returns:
            Tuple of (items, newest_id, oldest_id).
        """
        items: list[Item] = []
        newest_id: str | None = None
        oldest_id: str | None = None

        try:
            root = DefusedET.fromstring(body)
        except ParseError as e:
            parse_warnings.append(f"Failed to parse Atom response: {e}")
            self._metrics.record_error("malformed_atom")
            return [], None, None

        # Find all entry elements
        entries = root.findall(f"{ATOM_NS}entry")

        for entry in entries:
            try:
                item = self._parse_entry(entry, source_config)
                if item:
                    items.append(item)
                    arxiv_id = extract_arxiv_id(item.url)
                    if arxiv_id:
                        if newest_id is None:
                            newest_id = arxiv_id
                        oldest_id = arxiv_id
            except Exception as e:  # noqa: BLE001
                parse_warnings.append(f"Failed to parse entry: {e}")

        return items, newest_id, oldest_id

    def _parse_entry(
        self,
        entry: Element,
        source_config: SourceConfig,
    ) -> Item | None:
        """Parse a single entry element.

        Args:
            entry: Entry XML element.
            source_config: Source configuration.

        Returns:
            Item if parsing succeeded, None otherwise.
        """
        # Extract ID
        id_elem = entry.find(f"{ATOM_NS}id")
        if id_elem is None or id_elem.text is None:
            return None

        arxiv_id = extract_arxiv_id(id_elem.text)
        if not arxiv_id:
            return None

        canonical_url = f"https://arxiv.org/abs/{arxiv_id}"

        # Extract title
        title_elem = entry.find(f"{ATOM_NS}title")
        title = (
            title_elem.text.strip()
            if title_elem is not None and title_elem.text
            else f"Untitled {arxiv_id}"
        )

        # Extract dates
        published_at, date_confidence = self._extract_dates(entry)

        # Build raw_json
        raw_data = self._build_raw_data(entry, arxiv_id)
        raw_json, _ = self.truncate_raw_json(raw_data)

        # Compute content hash
        content_hash = self._compute_content_hash(entry, arxiv_id)

        return Item(
            url=canonical_url,
            source_id=source_config.id,
            tier=source_config.tier,
            kind=source_config.kind.value,
            title=title,
            published_at=published_at,
            date_confidence=date_confidence,
            content_hash=content_hash,
            raw_json=raw_json,
        )

    def _extract_dates(
        self,
        entry: Element,
    ) -> tuple[datetime | None, DateConfidence]:
        """Extract publication date from entry.

        Args:
            entry: Entry XML element.

        Returns:
            Tuple of (datetime or None, confidence level).
        """
        # Try published first (most reliable for API)
        published_elem = entry.find(f"{ATOM_NS}published")
        if published_elem is not None and published_elem.text:
            try:
                dt = datetime.fromisoformat(published_elem.text.replace("Z", "+00:00"))
                return dt, DateConfidence.HIGH
            except ValueError:
                pass

        # Try updated
        updated_elem = entry.find(f"{ATOM_NS}updated")
        if updated_elem is not None and updated_elem.text:
            try:
                dt = datetime.fromisoformat(updated_elem.text.replace("Z", "+00:00"))
                return dt, DateConfidence.MEDIUM
            except ValueError:
                pass

        return None, DateConfidence.LOW

    def _extract_authors(self, entry: Element) -> list[str]:
        """Extract author names from entry.

        Args:
            entry: Entry XML element.

        Returns:
            List of author names.
        """
        authors = []
        for author_elem in entry.findall(f"{ATOM_NS}author"):
            name_elem = author_elem.find(f"{ATOM_NS}name")
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text)
        return authors

    def _extract_categories(self, entry: Element) -> list[str]:
        """Extract categories from entry.

        Args:
            entry: Entry XML element.

        Returns:
            List of category terms.
        """
        categories = []
        for cat_elem in entry.findall(f"{ARXIV_NS}primary_category"):
            term = cat_elem.get("term")
            if term:
                categories.append(term)
        for cat_elem in entry.findall(f"{ATOM_NS}category"):
            term = cat_elem.get("term")
            if term and term not in categories:
                categories.append(term)
        return categories

    def _build_raw_data(
        self,
        entry: Element,
        arxiv_id: str,
    ) -> dict[str, Any]:
        """Build raw_json data from entry.

        Args:
            entry: Entry XML element.
            arxiv_id: Extracted arXiv ID.

        Returns:
            Dictionary of raw metadata.
        """
        raw_data: dict[str, Any] = {
            FIELD_ARXIV_ID: arxiv_id,
            FIELD_SOURCE: SOURCE_TYPE_API,
        }

        title_elem = entry.find(f"{ATOM_NS}title")
        if title_elem is not None and title_elem.text:
            raw_data["title"] = title_elem.text.strip()

        authors = self._extract_authors(entry)
        if authors:
            raw_data["authors"] = authors

        summary_elem = entry.find(f"{ATOM_NS}summary")
        if summary_elem is not None and summary_elem.text:
            raw_data["abstract_snippet"] = summary_elem.text.strip()[:500]

        categories = self._extract_categories(entry)
        if categories:
            raw_data["categories"] = categories

        published_elem = entry.find(f"{ATOM_NS}published")
        if published_elem is not None and published_elem.text:
            raw_data["published_at"] = published_elem.text

        updated_elem = entry.find(f"{ATOM_NS}updated")
        if updated_elem is not None and updated_elem.text:
            raw_data["updated_at"] = updated_elem.text

        return raw_data

    def _compute_content_hash(
        self,
        entry: Element,
        arxiv_id: str,
    ) -> str:
        """Compute content hash for entry.

        Hash is computed from: title, abstract_snippet, categories, updated_at.

        Args:
            entry: Entry XML element.
            arxiv_id: arXiv ID.

        Returns:
            Content hash string.
        """
        title_elem = entry.find(f"{ATOM_NS}title")
        title = (
            title_elem.text.strip()
            if title_elem is not None and title_elem.text
            else ""
        )

        summary_elem = entry.find(f"{ATOM_NS}summary")
        summary = (
            summary_elem.text.strip()[:200]
            if summary_elem is not None and summary_elem.text
            else ""
        )

        categories = []
        for cat_elem in entry.findall(f"{ATOM_NS}category"):
            term = cat_elem.get("term")
            if term:
                categories.append(term)
        categories_str = ",".join(sorted(categories))

        extra = {}
        if summary:
            extra["abstract_snippet"] = summary
        if categories_str:
            extra["categories"] = categories_str

        updated_elem = entry.find(f"{ATOM_NS}updated")
        if updated_elem is not None and updated_elem.text:
            extra["updated_at"] = updated_elem.text

        return compute_content_hash(
            title=title,
            url=f"https://arxiv.org/abs/{arxiv_id}",
            extra=extra if extra else None,
        )
