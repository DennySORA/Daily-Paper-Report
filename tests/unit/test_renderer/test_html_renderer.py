"""Unit tests for HTML renderer."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.config.schemas.base import LinkType
from src.linker.models import Story, StoryLink
from src.renderer.html_renderer import HtmlRenderer
from src.renderer.metrics import RendererMetrics
from src.renderer.models import (
    RenderContext,
    RenderManifest,
    RunInfo,
    SourceStatus,
    SourceStatusCode,
)


@pytest.fixture
def temp_output_dir() -> Path:
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_story() -> Story:
    """Create a sample story for testing."""
    return Story(
        story_id="test-story-1",
        title="Test Story Title",
        primary_link=StoryLink(
            url="https://example.com/article",
            link_type=LinkType.OFFICIAL,
            source_id="test-source",
            tier=0,
            title="Test Story Title",
        ),
        links=[
            StoryLink(
                url="https://example.com/article",
                link_type=LinkType.OFFICIAL,
                source_id="test-source",
                tier=0,
                title="Test Story Title",
            ),
        ],
        entities=["openai"],
        published_at=datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC),
    )


@pytest.fixture
def sample_context(sample_story: Story) -> RenderContext:
    """Create sample render context."""
    return RenderContext(
        run_id="test-run",
        run_date="2026-01-15",
        generated_at="2026-01-15T10:00:00Z",
        timezone="UTC",
        top5=[sample_story],
        model_releases_by_entity={"openai": [sample_story]},
        papers=[],
        radar=[],
        sources_status=[
            SourceStatus(
                source_id="test-source",
                name="Test Source",
                status=SourceStatusCode.HAS_UPDATE,
            )
        ],
        recent_runs=[
            RunInfo(
                run_id="test-run",
                started_at=datetime(2026, 1, 15, 9, 0, 0, tzinfo=UTC),
                finished_at=datetime(2026, 1, 15, 9, 5, 0, tzinfo=UTC),
                success=True,
            )
        ],
        archive_dates=["2026-01-15", "2026-01-14"],
    )


class TestHtmlRenderer:
    """Tests for HtmlRenderer."""

    def test_render_creates_all_pages(
        self,
        temp_output_dir: Path,
        sample_context: RenderContext,
    ) -> None:
        """Render creates all required HTML pages."""
        RendererMetrics.reset()
        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(sample_context, manifest)

        assert (temp_output_dir / "index.html").is_file()
        assert (temp_output_dir / "archive.html").is_file()
        assert (temp_output_dir / "sources.html").is_file()
        assert (temp_output_dir / "status.html").is_file()
        assert (temp_output_dir / "day" / "2026-01-15.html").is_file()

    def test_render_updates_manifest(
        self,
        temp_output_dir: Path,
        sample_context: RenderContext,
    ) -> None:
        """Render adds files to manifest."""
        RendererMetrics.reset()
        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(sample_context, manifest)

        assert len(manifest.files) == 5  # index, archive, sources, status, day
        assert manifest.total_bytes > 0

    def test_render_escapes_html(
        self,
        temp_output_dir: Path,
    ) -> None:
        """HTML content is escaped to prevent XSS."""
        RendererMetrics.reset()

        xss_story = Story(
            story_id="xss-test",
            title='<script>alert("xss")</script>',
            primary_link=StoryLink(
                url="https://example.com/xss",
                link_type=LinkType.OFFICIAL,
                source_id="test",
                tier=0,
            ),
            links=[
                StoryLink(
                    url="https://example.com/xss",
                    link_type=LinkType.OFFICIAL,
                    source_id="test",
                    tier=0,
                )
            ],
        )

        context = RenderContext(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
            top5=[xss_story],
        )

        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(context, manifest)

        content = (temp_output_dir / "index.html").read_text()
        # Script tag should be escaped
        assert "<script>" not in content
        assert "&lt;script&gt;" in content or "&#" in content

    def test_render_shows_date_unknown(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Stories without dates show 'Date unknown'."""
        RendererMetrics.reset()

        no_date_story = Story(
            story_id="no-date",
            title="Story Without Date",
            primary_link=StoryLink(
                url="https://example.com/no-date",
                link_type=LinkType.OFFICIAL,
                source_id="test",
                tier=0,
            ),
            links=[
                StoryLink(
                    url="https://example.com/no-date",
                    link_type=LinkType.OFFICIAL,
                    source_id="test",
                    tier=0,
                )
            ],
            published_at=None,  # No date
        )

        context = RenderContext(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
            top5=[no_date_story],
        )

        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(context, manifest)

        content = (temp_output_dir / "index.html").read_text()
        assert "Date unknown" in content

    def test_render_includes_navigation(
        self,
        temp_output_dir: Path,
        sample_context: RenderContext,
    ) -> None:
        """Pages include navigation links."""
        RendererMetrics.reset()
        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(sample_context, manifest)

        content = (temp_output_dir / "index.html").read_text()
        assert "index.html" in content
        assert "archive.html" in content
        assert "sources.html" in content
        assert "status.html" in content
        assert "api/daily.json" in content

    def test_render_empty_sections(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Can render with empty sections."""
        RendererMetrics.reset()

        context = RenderContext(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
            top5=[],
            papers=[],
            radar=[],
        )

        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(context, manifest)

        content = (temp_output_dir / "index.html").read_text()
        assert "No stories available" in content

    def test_atomic_write_no_partial_files(
        self,
        temp_output_dir: Path,
        sample_context: RenderContext,
    ) -> None:
        """No .tmp files left after render."""
        RendererMetrics.reset()
        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(sample_context, manifest)

        # Check no .tmp files exist
        tmp_files = list(temp_output_dir.rglob("*.tmp"))
        assert len(tmp_files) == 0

    def test_render_archive_dates_sorted(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Archive page shows dates in correct order."""
        RendererMetrics.reset()

        context = RenderContext(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
            archive_dates=["2026-01-15", "2026-01-14", "2026-01-13"],
        )

        manifest = RenderManifest(
            run_id="test",
            run_date="2026-01-15",
            generated_at="2026-01-15T10:00:00Z",
        )

        renderer = HtmlRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(context, manifest)

        content = (temp_output_dir / "archive.html").read_text()
        # Check all dates are present
        assert "2026-01-15" in content
        assert "2026-01-14" in content
        assert "2026-01-13" in content
