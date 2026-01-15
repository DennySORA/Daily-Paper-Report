"""Unit tests for the main StaticRenderer orchestrator."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.config.schemas.base import LinkType
from src.linker.models import Story, StoryLink
from src.ranker.models import RankerOutput
from src.renderer.metrics import RendererMetrics
from src.renderer.models import RunInfo, SourceStatus, SourceStatusCode
from src.renderer.renderer import StaticRenderer, render_static
from src.renderer.state_machine import RenderState


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
def sample_ranker_output(sample_story: Story) -> RankerOutput:
    """Create sample ranker output."""
    return RankerOutput(
        top5=[sample_story],
        model_releases_by_entity={"openai": [sample_story]},
        papers=[],
        radar=[sample_story],
        output_checksum="abc123",
    )


@pytest.fixture
def sample_run_info() -> RunInfo:
    """Create sample run info."""
    return RunInfo(
        run_id="test-run-123",
        started_at=datetime(2026, 1, 15, 9, 0, 0, tzinfo=UTC),
        finished_at=datetime(2026, 1, 15, 9, 5, 0, tzinfo=UTC),
        success=True,
        items_total=100,
        stories_total=20,
    )


@pytest.fixture
def sample_source_status() -> SourceStatus:
    """Create sample source status."""
    return SourceStatus(
        source_id="test-source",
        name="Test Source",
        tier=0,
        method="rss_atom",
        status=SourceStatusCode.HAS_UPDATE,
        reason_code="ok",
        reason_text="Success",
        items_new=5,
        items_updated=2,
    )


class TestStaticRenderer:
    """Tests for StaticRenderer orchestrator."""

    def test_initial_state_is_pending(self, temp_output_dir: Path) -> None:
        """Renderer starts in RENDER_PENDING state."""
        RendererMetrics.reset()
        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)
        assert renderer.state == RenderState.RENDER_PENDING

    def test_successful_render_transitions_to_done(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
        sample_source_status: SourceStatus,
    ) -> None:
        """Successful render ends in RENDER_DONE state."""
        RendererMetrics.reset()
        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)

        result = renderer.render(
            ranker_output=sample_ranker_output,
            sources_status=[sample_source_status],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        assert result.success
        assert renderer.state == RenderState.RENDER_DONE

    def test_render_produces_all_files(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
        sample_source_status: SourceStatus,
    ) -> None:
        """Render produces all expected files."""
        RendererMetrics.reset()
        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)

        result = renderer.render(
            ranker_output=sample_ranker_output,
            sources_status=[sample_source_status],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        assert result.success
        assert (temp_output_dir / "api" / "daily.json").is_file()
        assert (temp_output_dir / "index.html").is_file()
        assert (temp_output_dir / "archive.html").is_file()
        assert (temp_output_dir / "sources.html").is_file()
        assert (temp_output_dir / "status.html").is_file()
        # day/YYYY-MM-DD.html should exist
        day_files = list((temp_output_dir / "day").glob("*.html"))
        assert len(day_files) >= 1

    def test_render_manifest_contains_all_files(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
        sample_source_status: SourceStatus,
    ) -> None:
        """Manifest lists all generated files."""
        RendererMetrics.reset()
        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)

        result = renderer.render(
            ranker_output=sample_ranker_output,
            sources_status=[sample_source_status],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        assert len(result.manifest.files) == 6  # JSON + 5 HTML files
        paths = [f.path for f in result.manifest.files]
        assert "api/daily.json" in paths
        assert "index.html" in paths
        assert "archive.html" in paths
        assert "sources.html" in paths
        assert "status.html" in paths

    def test_render_manifest_has_checksums(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
        sample_source_status: SourceStatus,
    ) -> None:
        """All files in manifest have SHA-256 checksums."""
        RendererMetrics.reset()
        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)

        result = renderer.render(
            ranker_output=sample_ranker_output,
            sources_status=[sample_source_status],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        for file_info in result.manifest.files:
            assert len(file_info.sha256) == 64  # SHA-256 hex

    def test_render_empty_output(
        self,
        temp_output_dir: Path,
        sample_run_info: RunInfo,
    ) -> None:
        """Can render with empty ranker output."""
        RendererMetrics.reset()
        empty_output = RankerOutput(
            top5=[],
            model_releases_by_entity={},
            papers=[],
            radar=[],
        )

        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)
        result = renderer.render(
            ranker_output=empty_output,
            sources_status=[],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        assert result.success

    def test_archive_dates_include_current(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
    ) -> None:
        """Archive dates include current run date."""
        RendererMetrics.reset()

        # Create a pre-existing day page
        day_dir = temp_output_dir / "day"
        day_dir.mkdir(parents=True)
        (day_dir / "2026-01-14.html").write_text("<html>old</html>")

        renderer = StaticRenderer(run_id="test", output_dir=temp_output_dir)
        renderer.render(
            ranker_output=sample_ranker_output,
            sources_status=[],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        # Archive should list both dates
        archive_content = (temp_output_dir / "archive.html").read_text()
        assert "2026-01-14" in archive_content


class TestRenderStaticFunction:
    """Tests for render_static pure function."""

    def test_render_static_works(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
    ) -> None:
        """render_static function works with minimal args."""
        RendererMetrics.reset()

        result = render_static(
            ranker_output=sample_ranker_output,
            output_dir=temp_output_dir,
            run_id="test-pure",
        )

        assert result.success
        assert (temp_output_dir / "index.html").is_file()

    def test_render_static_with_all_args(
        self,
        temp_output_dir: Path,
        sample_ranker_output: RankerOutput,
        sample_run_info: RunInfo,
        sample_source_status: SourceStatus,
    ) -> None:
        """render_static works with all arguments."""
        RendererMetrics.reset()

        result = render_static(
            ranker_output=sample_ranker_output,
            output_dir=temp_output_dir,
            run_id="test-full",
            timezone="Asia/Taipei",
            sources_status=[sample_source_status],
            run_info=sample_run_info,
            recent_runs=[sample_run_info],
        )

        assert result.success
