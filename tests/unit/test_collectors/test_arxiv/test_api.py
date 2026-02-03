"""Unit tests for arXiv API collector."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from src.collectors.arxiv.api import (
    ArxivApiCollector,
    ArxivApiConfig,
    ArxivApiRateLimiter,
)
from src.collectors.arxiv.metrics import ArxivMetrics
from src.collectors.state_machine import SourceState
from src.features.config.schemas.sources import SourceConfig, SourceKind, SourceMethod
from src.features.fetch.client import HttpFetcher
from src.features.fetch.models import FetchError, FetchErrorClass, FetchResult


class MockRateLimiter:
    """Mock rate limiter for testing without actual delays."""

    def wait_if_needed(self) -> None:
        """No-op implementation for tests."""


# Sample arXiv API Atom response
# Note: Published dates are set within a few hours of each other so both
# items pass the 24-hour lookback filter when using the matching run_timestamp.
SAMPLE_API_RESPONSE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <title type="html">ArXiv Query: DeepSeek</title>
  <id>http://arxiv.org/api/query</id>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">2</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2401.12345v1</id>
    <title>DeepSeek: A Large Language Model</title>
    <summary>This paper presents DeepSeek, a large language model...</summary>
    <author><name>Test Author</name></author>
    <published>2024-01-15T10:00:00Z</published>
    <updated>2024-01-15T12:00:00Z</updated>
    <arxiv:primary_category term="cs.CL" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.CL" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <link href="http://arxiv.org/abs/2401.12345v1" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2401.12345v1" rel="related" type="application/pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2401.12346v2</id>
    <title>DeepSeek-Coder: A Code Model</title>
    <summary>This paper presents DeepSeek-Coder...</summary>
    <author><name>Another Author</name></author>
    <published>2024-01-15T08:00:00Z</published>
    <updated>2024-01-15T10:00:00Z</updated>
    <arxiv:primary_category term="cs.SE" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.SE" scheme="http://arxiv.org/schemas/atom"/>
    <link href="http://arxiv.org/abs/2401.12346v2" rel="alternate" type="text/html"/>
  </entry>
</feed>"""


EMPTY_API_RESPONSE = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title type="html">ArXiv Query</title>
  <id>http://arxiv.org/api/query</id>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:totalResults>
</feed>"""


def make_source_config(
    source_id: str = "arxiv-cn-models",
    query: str = 'ti:"DeepSeek"',
    max_results: int = 50,
) -> SourceConfig:
    """Create a test source configuration for API queries."""
    return SourceConfig(
        id=source_id,
        name="arXiv CN Models",
        url="http://export.arxiv.org/api/query",  # API base URL
        method=SourceMethod.RSS_ATOM,  # Placeholder
        tier=0,
        kind=SourceKind.PAPER,
        max_items=max_results,
        query=query,
    )


class TestArxivApiConfig:
    """Tests for ArxivApiConfig class."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = ArxivApiConfig(query='ti:"test"')
        assert config.max_results == 50
        assert config.sort_by == "submittedDate"
        assert config.sort_order == "descending"

    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = ArxivApiConfig(
            query='ti:"test"',
            max_results=100,
            sort_by="relevance",
            sort_order="ascending",
        )
        assert config.max_results == 100
        assert config.sort_by == "relevance"
        assert config.sort_order == "ascending"


class TestArxivApiRateLimiter:
    """Tests for ArxivApiRateLimiter class."""

    def test_first_call_no_wait(self) -> None:
        """Test that first call doesn't wait."""
        limiter = ArxivApiRateLimiter(min_interval=1.0)
        import time

        start = time.monotonic()
        limiter.wait_if_needed()
        elapsed = time.monotonic() - start

        assert elapsed < 0.1  # Should be nearly instant

    def test_rapid_calls_wait(self) -> None:
        """Test that rapid calls are rate limited."""
        limiter = ArxivApiRateLimiter(min_interval=0.1)  # Short interval for testing
        import time

        limiter.wait_if_needed()
        start = time.monotonic()
        limiter.wait_if_needed()
        elapsed = time.monotonic() - start

        # Should wait close to the interval
        assert elapsed >= 0.08


class TestArxivApiCollector:
    """Tests for ArxivApiCollector class."""

    def setup_method(self) -> None:
        """Reset metrics before each test."""
        ArxivMetrics.reset()

    def test_successful_collection(self) -> None:
        """Test successful API query collection."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=SAMPLE_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        # Use a timestamp close to the sample data dates (2024-01-15/16)
        # so items aren't filtered out by the 24-hour lookback window
        run_timestamp = datetime(2024, 1, 15, 18, 0, 0, tzinfo=UTC)
        result = collector.collect(source_config, mock_client, run_timestamp)

        assert result.success
        assert result.state == SourceState.SOURCE_DONE
        assert len(result.items) == 2

    def test_canonical_url_format(self) -> None:
        """Test that URLs are normalized to canonical format."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=SAMPLE_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        # Use a timestamp close to the sample data dates
        run_timestamp = datetime(2024, 1, 15, 18, 0, 0, tzinfo=UTC)
        result = collector.collect(source_config, mock_client, run_timestamp)

        for item in result.items:
            assert item.url.startswith("https://arxiv.org/abs/")
            # Should not contain version suffix
            assert "v1" not in item.url
            assert "v2" not in item.url

    def test_empty_response_success(self) -> None:
        """Test that empty response returns success."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=EMPTY_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        result = collector.collect(source_config, mock_client, datetime.now(UTC))

        assert result.success
        assert len(result.items) == 0

    def test_fetch_error_returns_failed(self) -> None:
        """Test that fetch error returns failed state."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=503,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=b"",
            cache_hit=False,
            error=FetchError(
                error_class=FetchErrorClass.HTTP_5XX,
                message="Service unavailable",
                status_code=503,
            ),
        )

        result = collector.collect(source_config, mock_client, datetime.now(UTC))

        assert not result.success
        assert result.state == SourceState.SOURCE_FAILED
        assert result.error is not None

    def test_malformed_xml_handled(self) -> None:
        """Test that malformed XML is handled gracefully."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=b"<invalid xml",
            cache_hit=False,
            error=None,
        )

        result = collector.collect(source_config, mock_client, datetime.now(UTC))

        # Should succeed but with warnings and no items
        assert result.success
        assert len(result.items) == 0
        assert len(result.parse_warnings) > 0

    def test_metrics_recorded(self) -> None:
        """Test that metrics are recorded."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=SAMPLE_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        # Use a timestamp close to the sample data dates
        run_timestamp = datetime(2024, 1, 15, 18, 0, 0, tzinfo=UTC)
        collector.collect(source_config, mock_client, run_timestamp)

        metrics = ArxivMetrics.get_instance()
        assert metrics.get_items_total("api") == 2
        assert metrics.get_api_latency_stats()["count"] == 1.0

    def test_categories_extracted(self) -> None:
        """Test that categories are extracted from entries."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=SAMPLE_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        # Use a timestamp close to the sample data dates
        run_timestamp = datetime(2024, 1, 15, 18, 0, 0, tzinfo=UTC)
        result = collector.collect(source_config, mock_client, run_timestamp)

        import json

        # First item should have cs.CL and cs.AI categories
        raw = json.loads(result.items[0].raw_json)
        assert "categories" in raw
        assert "cs.CL" in raw["categories"]

    def test_date_extraction_high_confidence(self) -> None:
        """Test that published date gives high confidence."""
        collector = ArxivApiCollector(run_id="test", rate_limiter=MockRateLimiter())
        source_config = make_source_config()

        mock_client = MagicMock(spec=HttpFetcher)
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url="http://export.arxiv.org/api/query",
            headers={},
            body_bytes=SAMPLE_API_RESPONSE,
            cache_hit=False,
            error=None,
        )

        # Use a timestamp close to the sample data dates
        run_timestamp = datetime(2024, 1, 15, 18, 0, 0, tzinfo=UTC)
        result = collector.collect(source_config, mock_client, run_timestamp)

        assert result.items[0].published_at is not None
        from src.features.store.models import DateConfidence

        assert result.items[0].date_confidence == DateConfidence.HIGH
