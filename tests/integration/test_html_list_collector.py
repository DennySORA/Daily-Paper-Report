"""Integration tests for HTML list collector with domain profiles."""

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.collectors.html_list import HtmlListCollector
from src.collectors.html_profile.metrics import HtmlProfileMetrics
from src.collectors.html_profile.models import DomainProfile
from src.collectors.html_profile.registry import ProfileRegistry
from src.collectors.state_machine import SourceState
from src.config.schemas.base import SourceKind, SourceMethod, SourceTier
from src.config.schemas.sources import SourceConfig
from src.fetch.models import FetchResult
from src.store.models import DateConfidence


# Path to HTML fixtures
FIXTURES_PATH = Path(__file__).parents[1] / "fixtures" / "html"


@pytest.fixture
def source_config() -> SourceConfig:
    """Create test source configuration."""
    return SourceConfig(
        id="test-blog",
        name="Test Blog",
        url="https://example.com/blog",
        tier=SourceTier.TIER_0,
        method=SourceMethod.HTML_LIST,
        kind=SourceKind.BLOG,
        max_items=50,
    )


@pytest.fixture
def registry() -> ProfileRegistry:
    """Create clean profile registry."""
    ProfileRegistry.reset()
    return ProfileRegistry()


@pytest.fixture
def _reset_metrics() -> None:
    """Reset metrics before each test."""
    HtmlProfileMetrics.reset()


class TestHtmlListCollectorWithFixtures:
    """Integration tests using HTML fixture files."""

    def test_parse_blog_list_with_time_elements(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test parsing blog list with <time> elements."""
        fixture_path = FIXTURES_PATH / "blog_list_with_time.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        # Mock HTTP client
        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html; charset=utf-8"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        # Create collector
        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        # Collect items
        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        # Verify results
        assert result.success
        assert result.state == SourceState.SOURCE_DONE
        assert len(result.items) == 3

        # Check items have dates with HIGH confidence
        for item in result.items:
            assert item.published_at is not None
            assert item.date_confidence == DateConfidence.HIGH

        # Check items are sorted by date descending
        dates = [item.published_at for item in result.items if item.published_at]
        assert dates == sorted(dates, reverse=True)

    def test_parse_blog_list_with_meta_tags(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test parsing blog list with meta tags."""
        fixture_path = FIXTURES_PATH / "blog_list_with_meta.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        assert result.success
        assert len(result.items) == 2

        # Check dates were extracted from meta tags
        for item in result.items:
            assert item.published_at is not None
            assert item.date_confidence == DateConfidence.HIGH

    def test_parse_blog_list_with_json_ld(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test parsing blog list with JSON-LD."""
        fixture_path = FIXTURES_PATH / "blog_list_with_json_ld.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        assert result.success
        assert len(result.items) == 2

        # Check dates were extracted from JSON-LD
        for item in result.items:
            assert item.published_at is not None
            assert item.date_confidence == DateConfidence.HIGH

    def test_parse_blog_list_without_dates(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test parsing blog list without dates marks LOW confidence."""
        fixture_path = FIXTURES_PATH / "blog_list_no_dates.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        # Disable item page recovery for this test
        profile = DomainProfile(
            domain="example.com",
            name="Test Profile",
            enable_item_page_recovery=False,
        )
        registry.register(profile)

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        assert result.success
        assert len(result.items) == 3

        # Check items have LOW confidence
        for item in result.items:
            assert item.published_at is None
            assert item.date_confidence == DateConfidence.LOW


class TestHtmlListCollectorItemRecovery:
    """Tests for item page date recovery."""

    def test_item_page_recovery_respects_k_cap(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test that item page recovery respects K-cap."""
        # Create HTML with many items without dates
        html_items = "\n".join(
            [
                f'<article><h2><a href="/post/{i}">Post {i}</a></h2></article>'
                for i in range(20)
            ]
        )
        html_content = f"""
        <!DOCTYPE html>
        <html><body><main>{html_items}</main></body></html>
        """.encode()

        item_page_html = b"""
        <html><head>
            <meta property="article:published_time" content="2024-01-01T00:00:00Z">
        </head><body><article><h1>Item Page</h1></article></body></html>
        """

        # Set K-cap to 5
        profile = DomainProfile(
            domain="example.com",
            name="Test Profile",
            max_item_page_fetches=5,
            enable_item_page_recovery=True,
        )
        registry.register(profile)

        # Track fetch calls
        fetch_calls: list[str] = []

        def mock_fetch(
            source_id: str, url: str, extra_headers: dict[str, str] | None = None
        ) -> FetchResult:
            fetch_calls.append(url)
            if url == source_config.url:
                return FetchResult(
                    status_code=200,
                    final_url=url,
                    headers={"content-type": "text/html"},
                    body_bytes=html_content,
                    cache_hit=False,
                    error=None,
                )
            return FetchResult(
                status_code=200,
                final_url=url,
                headers={"content-type": "text/html"},
                body_bytes=item_page_html,
                cache_hit=False,
                error=None,
            )

        mock_client = MagicMock()
        mock_client.fetch.side_effect = mock_fetch

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        assert result.success

        # Count item page fetches (excluding the initial list page fetch)
        item_fetches = [url for url in fetch_calls if url != source_config.url]
        assert len(item_fetches) <= 5  # K-cap enforced


class TestHtmlListCollectorSecurity:
    """Security tests for HTML list collector."""

    def test_rejects_binary_content_type(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test that binary content types are rejected."""
        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "image/png"},
            body_bytes=b"fake image data",
            cache_hit=False,
            error=None,
        )

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        result = collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        assert not result.success
        assert result.state == SourceState.SOURCE_FAILED
        assert result.error is not None
        assert "Content-Type not allowed" in result.error.message


class TestHtmlListCollectorMetrics:
    """Tests for metrics collection."""

    def test_metrics_recorded(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test that metrics are recorded during collection."""
        fixture_path = FIXTURES_PATH / "blog_list_with_time.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        collector.collect(
            source_config=source_config,
            http_client=mock_client,
            now=datetime.now(UTC),
        )

        metrics = HtmlProfileMetrics.get_instance()

        # Check that links were recorded
        assert metrics.get_links_total("example.com") > 0


class TestHtmlListCollectorIdempotency:
    """Tests for idempotent parsing."""

    def test_stable_output_order(
        self,
        source_config: SourceConfig,
        registry: ProfileRegistry,
        _reset_metrics: None,
    ) -> None:
        """Test that output is stable across multiple runs."""
        fixture_path = FIXTURES_PATH / "blog_list_with_time.html"
        if not fixture_path.exists():
            pytest.skip("Fixture file not found")

        html_content = fixture_path.read_bytes()

        mock_client = MagicMock()
        mock_client.fetch.return_value = FetchResult(
            status_code=200,
            final_url=source_config.url,
            headers={"content-type": "text/html"},
            body_bytes=html_content,
            cache_hit=False,
            error=None,
        )

        collector = HtmlListCollector(
            run_id="test-run",
            profile_registry=registry,
        )

        # Run multiple times
        results = []
        for _ in range(3):
            result = collector.collect(
                source_config=source_config,
                http_client=mock_client,
                now=datetime.now(UTC),
            )
            results.append([item.url for item in result.items])

        # All runs should produce same order
        assert all(r == results[0] for r in results)
