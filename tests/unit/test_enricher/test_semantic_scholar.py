"""Unit tests for Semantic Scholar enricher."""

import json
from unittest.mock import MagicMock

import pytest

from src.enricher.semantic_scholar import (
    SemanticScholarEnricher,
    extract_arxiv_id,
)
from src.fetch.models import FetchError, FetchErrorClass, FetchResult
from src.store.models import DateConfidence, Item


def _make_fetch_result(
    status_code: int = 200,
    body: str = "{}",
    error: FetchError | None = None,
) -> FetchResult:
    """Create a test FetchResult."""
    return FetchResult(
        status_code=status_code,
        final_url="https://api.semanticscholar.org/test",
        body_bytes=body.encode("utf-8"),
        error=error,
    )


def _make_item(
    url: str = "https://arxiv.org/abs/2301.12345",
    raw_json: str = "{}",
) -> Item:
    """Create a test Item."""
    return Item(
        url=url,
        source_id="test-source",
        tier=0,
        kind="paper",
        title="Test Paper",
        content_hash="test-hash",
        raw_json=raw_json,
        date_confidence=DateConfidence.LOW,
    )


class TestExtractArxivId:
    """Tests for extract_arxiv_id function."""

    def test_extract_from_arxiv_url(self) -> None:
        """Extract arXiv ID from arxiv.org URL."""
        item = _make_item(url="https://arxiv.org/abs/2301.12345")
        arxiv_id = extract_arxiv_id(item)
        assert arxiv_id == "2301.12345"

    def test_extract_from_arxiv_pdf_url(self) -> None:
        """Extract arXiv ID from PDF URL."""
        item = _make_item(url="https://arxiv.org/pdf/2301.12345.pdf")
        arxiv_id = extract_arxiv_id(item)
        assert arxiv_id == "2301.12345"

    def test_extract_from_raw_json(self) -> None:
        """Extract arXiv ID from raw_json field."""
        raw_json = json.dumps({"arxiv_id": "2301.12345"})
        item = _make_item(url="https://example.com/paper", raw_json=raw_json)
        arxiv_id = extract_arxiv_id(item)
        assert arxiv_id == "2301.12345"

    def test_extract_with_version(self) -> None:
        """Extract arXiv ID with version suffix (version stripped for API lookups)."""
        item = _make_item(url="https://arxiv.org/abs/2301.12345v2")
        arxiv_id = extract_arxiv_id(item)
        # Semantic Scholar API expects IDs without version suffix
        assert arxiv_id == "2301.12345"

    def test_returns_none_for_non_arxiv(self) -> None:
        """Return None for non-arXiv URL."""
        item = _make_item(url="https://example.com/paper")
        arxiv_id = extract_arxiv_id(item)
        assert arxiv_id is None

    def test_raw_json_takes_precedence(self) -> None:
        """raw_json arxiv_id field takes precedence over URL."""
        raw_json = json.dumps({"arxiv_id": "2302.00001"})
        item = _make_item(url="https://arxiv.org/abs/2301.12345", raw_json=raw_json)
        arxiv_id = extract_arxiv_id(item)
        assert arxiv_id == "2302.00001"


class TestSemanticScholarEnricher:
    """Tests for SemanticScholarEnricher class."""

    def test_enrich_without_http_client(self) -> None:
        """Enrichment fails gracefully without HTTP client."""
        rate_limiter = MagicMock()
        enricher = SemanticScholarEnricher(run_id="test", rate_limiter=rate_limiter)
        item = _make_item()
        result = enricher.enrich(item)
        assert result.success is False
        assert "HTTP client not configured" in (result.error_message or "")

    def test_enrich_non_arxiv_item(self) -> None:
        """Non-arXiv items are skipped."""
        http_client = MagicMock()
        rate_limiter = MagicMock()
        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        item = _make_item(url="https://example.com/paper")
        result = enricher.enrich(item)
        assert result.success is True
        assert result.enriched_data == {}
        http_client.fetch.assert_not_called()

    def test_enrich_success(self) -> None:
        """Successful enrichment returns citation data."""
        api_response = json.dumps(
            {
                "citationCount": 100,
                "influentialCitationCount": 25,
                "publicationDate": "2023-01-15",
                "venue": "NeurIPS 2023",
            }
        )

        http_client = MagicMock()
        http_client.fetch.return_value = _make_fetch_result(
            status_code=200,
            body=api_response,
        )
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        item = _make_item()
        result = enricher.enrich(item)

        assert result.success is True
        assert result.enriched_data["citation_count"] == 100
        assert result.enriched_data["influential_citation_count"] == 25
        assert result.enriched_data["publication_date"] == "2023-01-15"
        assert result.enriched_data["venue"] == "NeurIPS 2023"

    def test_enrich_paper_not_found(self) -> None:
        """Paper not found returns empty enrichment."""
        http_client = MagicMock()
        http_client.fetch.return_value = _make_fetch_result(
            status_code=404,
            body="",
            error=FetchError(
                error_class=FetchErrorClass.HTTP_4XX,
                message="Not Found",
                status_code=404,
            ),
        )
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        item = _make_item()
        result = enricher.enrich(item)

        assert result.success is True
        assert result.enriched_data == {}

    def test_enrich_api_error(self) -> None:
        """API error returns empty enrichment (graceful degradation)."""
        http_client = MagicMock()
        http_client.fetch.return_value = _make_fetch_result(
            status_code=500,
            body="Internal Server Error",
            error=FetchError(
                error_class=FetchErrorClass.HTTP_5XX,
                message="Internal Server Error",
                status_code=500,
            ),
        )
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        item = _make_item()
        result = enricher.enrich(item)

        # Graceful degradation - returns success with empty data
        assert result.success is True
        assert result.enriched_data == {}

    def test_enrich_partial_response(self) -> None:
        """Partial API response is handled correctly."""
        api_response = json.dumps(
            {
                "citationCount": 50,
            }
        )

        http_client = MagicMock()
        http_client.fetch.return_value = _make_fetch_result(
            status_code=200,
            body=api_response,
        )
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        item = _make_item()
        result = enricher.enrich(item)

        assert result.success is True
        assert result.enriched_data["citation_count"] == 50
        assert "influential_citation_count" not in result.enriched_data
        assert "publication_date" not in result.enriched_data


class TestSemanticScholarEnricherBatch:
    """Tests for batch enrichment."""

    def test_batch_enrichment(self) -> None:
        """Batch enrichment processes multiple items."""
        api_response = json.dumps({"citationCount": 100})

        http_client = MagicMock()
        http_client.fetch.return_value = _make_fetch_result(
            status_code=200,
            body=api_response,
        )
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        items = [
            _make_item(url="https://arxiv.org/abs/2301.00001"),
            _make_item(url="https://arxiv.org/abs/2301.00002"),
            _make_item(url="https://example.com/paper"),  # non-arXiv
        ]

        batch_result = enricher.enrich_batch(items)

        assert batch_result.total_items == 3
        assert batch_result.successful == 2
        assert batch_result.skipped == 1
        assert batch_result.failed == 0

    def test_batch_mixed_results(self) -> None:
        """Batch handles mixed success/failure."""
        http_client = MagicMock()

        # First call succeeds, second fails
        http_client.fetch.side_effect = [
            _make_fetch_result(
                status_code=200,
                body=json.dumps({"citationCount": 100}),
            ),
            _make_fetch_result(
                status_code=500,
                body="",
                error=FetchError(
                    error_class=FetchErrorClass.HTTP_5XX,
                    message="Internal Server Error",
                    status_code=500,
                ),
            ),
        ]
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(
            run_id="test", http_client=http_client, rate_limiter=rate_limiter
        )
        items = [
            _make_item(url="https://arxiv.org/abs/2301.00001"),
            _make_item(url="https://arxiv.org/abs/2301.00002"),
        ]

        batch_result = enricher.enrich_batch(items)

        assert batch_result.total_items == 2
        assert batch_result.successful == 1
        # Second one returns empty enrichment (graceful degradation)
        assert batch_result.skipped == 1


class TestSemanticScholarHeaders:
    """Tests for API header building."""

    def test_headers_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Headers without API key."""
        monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(run_id="test", rate_limiter=rate_limiter)
        headers = enricher._build_headers()

        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "x-api-key" not in headers

    def test_headers_with_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Headers with API key include authorization."""
        monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "test-api-key")
        rate_limiter = MagicMock()

        enricher = SemanticScholarEnricher(run_id="test", rate_limiter=rate_limiter)
        headers = enricher._build_headers()

        assert headers["x-api-key"] == "test-api-key"
