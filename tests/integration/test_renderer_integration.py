"""Integration tests for static renderer."""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.config.schemas.base import LinkType
from src.linker.models import Story, StoryLink
from src.ranker.models import RankerOutput
from src.renderer.metrics import RendererMetrics
from src.renderer.models import RunInfo, SourceStatus, SourceStatusCode
from src.renderer.renderer import StaticRenderer


@pytest.fixture
def temp_output_dir() -> Path:
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def create_story(  # noqa: PLR0913
    story_id: str,
    title: str,
    url: str,
    published_at: datetime | None = None,
    entities: list[str] | None = None,
    arxiv_id: str | None = None,
) -> Story:
    """Helper to create a Story for testing."""
    return Story(
        story_id=story_id,
        title=title,
        primary_link=StoryLink(
            url=url,
            link_type=LinkType.OFFICIAL,
            source_id="test-source",
            tier=0,
            title=title,
        ),
        links=[
            StoryLink(
                url=url,
                link_type=LinkType.OFFICIAL,
                source_id="test-source",
                tier=0,
                title=title,
            ),
        ],
        entities=entities or [],
        published_at=published_at,
        arxiv_id=arxiv_id,
    )


class TestRendererIntegration:
    """Integration tests for complete rendering flow."""

    def test_end_to_end_render_with_stories(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Full render produces complete, valid output."""
        RendererMetrics.reset()

        # Create realistic ranker output
        stories = [
            create_story(
                "story-1",
                "New GPT-5 Model Released",
                "https://openai.com/gpt5",
                datetime(2026, 1, 15, 10, 0, 0, tzinfo=UTC),
                ["openai"],
            ),
            create_story(
                "story-2",
                "Claude 4 Announcement",
                "https://anthropic.com/claude4",
                datetime(2026, 1, 14, 12, 0, 0, tzinfo=UTC),
                ["anthropic"],
            ),
            create_story(
                "story-3",
                "Attention Is All You Need v2",
                "https://arxiv.org/abs/2601.00001",
                datetime(2026, 1, 13, 8, 0, 0, tzinfo=UTC),
                arxiv_id="2601.00001",
            ),
        ]

        ranker_output = RankerOutput(
            top5=stories[:2],
            model_releases_by_entity={"openai": stories[:1], "anthropic": stories[1:2]},
            papers=[stories[2]],
            radar=[],
            output_checksum="test-checksum",
        )

        sources_status = [
            SourceStatus(
                source_id="openai-blog",
                name="OpenAI Blog",
                tier=0,
                method="rss_atom",
                status=SourceStatusCode.HAS_UPDATE,
                items_new=1,
            ),
            SourceStatus(
                source_id="arxiv-cs-ai",
                name="arXiv cs.AI",
                tier=1,
                method="arxiv_api",
                status=SourceStatusCode.HAS_UPDATE,
                items_new=10,
            ),
        ]

        run_info = RunInfo(
            run_id="integration-test-run",
            started_at=datetime(2026, 1, 15, 9, 0, 0, tzinfo=UTC),
            finished_at=datetime(2026, 1, 15, 9, 10, 0, tzinfo=UTC),
            success=True,
            items_total=50,
            stories_total=3,
        )

        renderer = StaticRenderer(
            run_id="integration-test-run",
            output_dir=temp_output_dir,
            timezone="UTC",
        )

        result = renderer.render(
            ranker_output=ranker_output,
            sources_status=sources_status,
            run_info=run_info,
            recent_runs=[run_info],
        )

        # Verify success
        assert result.success
        assert result.error_summary is None

        # Verify all files exist
        assert (temp_output_dir / "api" / "daily.json").is_file()
        assert (temp_output_dir / "index.html").is_file()
        assert (temp_output_dir / "archive.html").is_file()
        assert (temp_output_dir / "sources.html").is_file()
        assert (temp_output_dir / "status.html").is_file()

        # Verify JSON content
        json_data = json.loads((temp_output_dir / "api" / "daily.json").read_text())
        assert json_data["run_id"] == "integration-test-run"
        assert len(json_data["top5"]) == 2
        assert json_data["top5"][0]["title"] == "New GPT-5 Model Released"

        # Verify HTML content
        index_html = (temp_output_dir / "index.html").read_text()
        assert "New GPT-5 Model Released" in index_html
        assert "Claude 4 Announcement" in index_html
        assert "openai.com" in index_html

        # Verify sources page
        sources_html = (temp_output_dir / "sources.html").read_text()
        assert "OpenAI Blog" in sources_html
        assert "HAS_UPDATE" in sources_html

        # Verify manifest
        assert len(result.manifest.files) == 6
        assert result.manifest.total_bytes > 0

    def test_render_with_xss_content_is_safe(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Malicious content is properly escaped."""
        RendererMetrics.reset()

        xss_story = create_story(
            "xss-story",
            '<img src=x onerror="alert(1)">',
            "https://example.com/xss",
        )

        ranker_output = RankerOutput(
            top5=[xss_story],
            model_releases_by_entity={},
            papers=[],
            radar=[],
        )

        run_info = RunInfo(
            run_id="xss-test",
            started_at=datetime.now(UTC),
        )

        renderer = StaticRenderer(
            run_id="xss-test",
            output_dir=temp_output_dir,
        )

        result = renderer.render(
            ranker_output=ranker_output,
            sources_status=[],
            run_info=run_info,
            recent_runs=[run_info],
        )

        assert result.success

        html_content = (temp_output_dir / "index.html").read_text()
        # Raw script should not appear
        assert 'onerror="alert(1)"' not in html_content
        # Should be escaped
        assert "&lt;" in html_content or "&#" in html_content

    def test_render_preserves_existing_day_pages(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Existing day pages are preserved (within retention)."""
        RendererMetrics.reset()

        # Create pre-existing day pages
        day_dir = temp_output_dir / "day"
        day_dir.mkdir(parents=True)
        (day_dir / "2026-01-14.html").write_text("<html>yesterday</html>")
        (day_dir / "2026-01-13.html").write_text("<html>older</html>")

        ranker_output = RankerOutput(
            top5=[],
            model_releases_by_entity={},
            papers=[],
            radar=[],
        )

        run_info = RunInfo(
            run_id="test",
            started_at=datetime.now(UTC),
        )

        renderer = StaticRenderer(
            run_id="test",
            output_dir=temp_output_dir,
            retention_days=90,
        )

        result = renderer.render(
            ranker_output=ranker_output,
            sources_status=[],
            run_info=run_info,
            recent_runs=[run_info],
        )

        assert result.success

        # Previous day pages should still exist
        assert (day_dir / "2026-01-14.html").is_file()
        assert (day_dir / "2026-01-13.html").is_file()

        # Archive should list all dates
        archive_content = (temp_output_dir / "archive.html").read_text()
        assert "2026-01-14" in archive_content
        assert "2026-01-13" in archive_content

    def test_json_output_is_deterministic(
        self,
        temp_output_dir: Path,
    ) -> None:
        """Same input produces same JSON output structure."""
        RendererMetrics.reset()

        story = create_story(
            "determinism-test",
            "Test Story",
            "https://example.com/test",
            datetime(2026, 1, 15, tzinfo=UTC),
        )

        ranker_output = RankerOutput(
            top5=[story],
            model_releases_by_entity={},
            papers=[],
            radar=[],
        )

        run_info = RunInfo(
            run_id="determinism",
            started_at=datetime(2026, 1, 15, tzinfo=UTC),
        )

        # Render twice
        dir1 = temp_output_dir / "run1"
        dir2 = temp_output_dir / "run2"

        for out_dir in [dir1, dir2]:
            RendererMetrics.reset()
            renderer = StaticRenderer(
                run_id="determinism",
                output_dir=out_dir,
            )
            renderer.render(
                ranker_output=ranker_output,
                sources_status=[],
                run_info=run_info,
                recent_runs=[run_info],
            )

        # Compare JSON (excluding generated_at which changes)
        json1 = json.loads((dir1 / "api" / "daily.json").read_text())
        json2 = json.loads((dir2 / "api" / "daily.json").read_text())

        del json1["generated_at"]
        del json2["generated_at"]

        assert json1 == json2
