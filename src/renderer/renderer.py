"""Main static HTML renderer orchestrator."""

import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import structlog

from src.ranker.models import RankerOutput
from src.renderer.html_renderer import HtmlRenderer
from src.renderer.json_renderer import JsonRenderer
from src.renderer.metrics import RendererMetrics
from src.renderer.models import (
    RenderContext,
    RenderManifest,
    RenderResult,
    RunInfo,
    SourceStatus,
)
from src.renderer.state_machine import RenderState, RenderStateMachine


logger = structlog.get_logger()


class StaticRenderer:
    """Orchestrates static HTML and JSON rendering.

    Implements the rendering state machine:
        RENDER_PENDING -> RENDERING_JSON -> RENDERING_HTML -> RENDER_DONE|RENDER_FAILED

    Produces:
        - api/daily.json
        - index.html
        - day/YYYY-MM-DD.html
        - archive.html
        - sources.html
        - status.html
    """

    def __init__(
        self,
        run_id: str,
        output_dir: Path,
        timezone: str = "UTC",
        metrics: RendererMetrics | None = None,
        retention_days: int = 90,
    ) -> None:
        """Initialize the static renderer.

        Args:
            run_id: Unique run identifier.
            output_dir: Output directory for rendered files.
            timezone: Timezone for date display.
            metrics: Optional metrics instance.
            retention_days: Number of days to retain day pages.
        """
        self._run_id = run_id
        self._output_dir = Path(output_dir)
        self._timezone = timezone
        self._metrics = metrics or RendererMetrics.get_instance()
        self._retention_days = retention_days

        self._state_machine = RenderStateMachine(run_id)
        self._log = logger.bind(run_id=run_id, component="renderer")

    @property
    def state(self) -> RenderState:
        """Get current render state."""
        return self._state_machine.state

    def render(
        self,
        ranker_output: RankerOutput,
        sources_status: list[SourceStatus],
        run_info: RunInfo,
        recent_runs: list[RunInfo],
    ) -> RenderResult:
        """Render all static pages.

        Args:
            ranker_output: Output from the ranker.
            sources_status: Per-source status list.
            run_info: Current run information.
            recent_runs: Recent run history for status page.

        Returns:
            RenderResult indicating success/failure and manifest.
        """
        start_time = time.perf_counter()
        run_date = datetime.now(UTC).strftime("%Y-%m-%d")
        generated_at = datetime.now(UTC).isoformat()

        manifest = RenderManifest(
            run_id=self._run_id,
            run_date=run_date,
            generated_at=generated_at,
        )

        self._log.info(
            "render_started",
            run_date=run_date,
            output_dir=str(self._output_dir),
        )

        try:
            # Phase 1: Render JSON
            self._state_machine.to_rendering_json()
            json_renderer = JsonRenderer(
                run_id=self._run_id,
                output_dir=self._output_dir,
                metrics=self._metrics,
            )
            json_file = json_renderer.render(
                ranker_output=ranker_output,
                sources_status=sources_status,
                run_info=run_info,
                run_date=run_date,
            )
            manifest.add_file(json_file)

            # Phase 2: Render HTML
            self._state_machine.to_rendering_html()

            # Collect archive dates before rendering
            archive_dates = self._get_archive_dates(run_date)

            context = RenderContext(
                run_id=self._run_id,
                run_date=run_date,
                generated_at=generated_at,
                timezone=self._timezone,
                top5=list(ranker_output.top5),
                model_releases_by_entity=dict(ranker_output.model_releases_by_entity),
                papers=list(ranker_output.papers),
                radar=list(ranker_output.radar),
                sources_status=sources_status,
                recent_runs=recent_runs,
                archive_dates=archive_dates,
            )

            html_renderer = HtmlRenderer(
                run_id=self._run_id,
                output_dir=self._output_dir,
                metrics=self._metrics,
            )
            html_renderer.render(context, manifest)

            # Prune old day pages if needed
            self._prune_old_day_pages()

            # Complete
            self._state_machine.to_done()
            duration_ms = (time.perf_counter() - start_time) * 1000
            manifest.duration_ms = duration_ms
            self._metrics.record_render_duration(duration_ms)

            self._log.info(
                "render_complete",
                file_count=len(manifest.files),
                total_bytes=manifest.total_bytes,
                duration_ms=round(duration_ms, 2),
            )

            return RenderResult(
                success=True,
                manifest=manifest,
            )

        except Exception as e:
            self._state_machine.to_failed()
            self._metrics.record_failure()

            error_summary = f"{type(e).__name__}: {e}"
            self._log.error(
                "render_failed",
                error=error_summary,
            )

            return RenderResult(
                success=False,
                manifest=manifest,
                error_summary=error_summary,
            )

    def _get_archive_dates(self, current_date: str) -> list[str]:
        """Get list of existing archive dates.

        Args:
            current_date: Current run date (will be included).

        Returns:
            List of date strings in descending order.
        """
        day_dir = self._output_dir / "day"
        dates: set[str] = {current_date}

        if day_dir.exists():
            for html_file in day_dir.glob("*.html"):
                # Extract date from filename (YYYY-MM-DD.html)
                date_str = html_file.stem
                if self._is_valid_date(date_str):
                    dates.add(date_str)

        return sorted(dates, reverse=True)

    def _is_valid_date(self, date_str: str) -> bool:
        """Check if string is a valid YYYY-MM-DD date.

        Args:
            date_str: String to check.

        Returns:
            True if valid date format.
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _prune_old_day_pages(self) -> int:
        """Prune day pages older than retention period.

        Returns:
            Number of files pruned.
        """
        day_dir = self._output_dir / "day"
        if not day_dir.exists():
            return 0

        cutoff_date = datetime.now(UTC) - timedelta(days=self._retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        pruned = 0

        for html_file in day_dir.glob("*.html"):
            date_str = html_file.stem
            if self._is_valid_date(date_str) and date_str < cutoff_str:
                html_file.unlink()
                pruned += 1
                self._log.debug("day_page_pruned", file=str(html_file))

        if pruned > 0:
            self._log.info(
                "day_pages_pruned",
                count=pruned,
                retention_days=self._retention_days,
            )

        return pruned


def render_static(  # noqa: PLR0913
    ranker_output: RankerOutput,
    output_dir: Path,
    run_id: str,
    timezone: str = "UTC",
    sources_status: list[SourceStatus] | None = None,
    run_info: RunInfo | None = None,
    recent_runs: list[RunInfo] | None = None,
) -> RenderResult:
    """Pure function API for static rendering.

    Args:
        ranker_output: Output from the ranker.
        output_dir: Output directory for rendered files.
        run_id: Unique run identifier.
        timezone: Timezone for date display.
        sources_status: Per-source status list.
        run_info: Current run information.
        recent_runs: Recent run history.

    Returns:
        RenderResult indicating success/failure.
    """
    if sources_status is None:
        sources_status = []

    if run_info is None:
        run_info = RunInfo(
            run_id=run_id,
            started_at=datetime.now(UTC),
        )

    if recent_runs is None:
        recent_runs = [run_info]

    renderer = StaticRenderer(
        run_id=run_id,
        output_dir=output_dir,
        timezone=timezone,
    )

    return renderer.render(
        ranker_output=ranker_output,
        sources_status=sources_status,
        run_info=run_info,
        recent_runs=recent_runs,
    )
