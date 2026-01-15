"""JSON renderer for api/daily.json output."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import structlog

from src.linker.models import Story
from src.ranker.models import RankerOutput
from src.renderer.io import AtomicWriter
from src.renderer.metrics import RendererMetrics
from src.renderer.models import (
    DailyDigest,
    GeneratedFile,
    RunInfo,
    SourceStatus,
)


logger = structlog.get_logger()


class JsonRenderer:
    """Renders JSON API output (api/daily.json).

    Produces deterministic JSON output with stable formatting and ordering.
    """

    def __init__(
        self,
        run_id: str,
        output_dir: Path,
        metrics: RendererMetrics | None = None,
    ) -> None:
        """Initialize the JSON renderer.

        Args:
            run_id: Unique run identifier.
            output_dir: Output directory for rendered files.
            metrics: Optional metrics instance.
        """
        self._run_id = run_id
        self._output_dir = output_dir
        self._metrics = metrics or RendererMetrics.get_instance()
        self._log = logger.bind(run_id=run_id, component="renderer")
        self._writer = AtomicWriter(output_dir, run_id)

    def render(
        self,
        ranker_output: RankerOutput,
        sources_status: list[SourceStatus],
        run_info: RunInfo,
        run_date: str,
    ) -> GeneratedFile:
        """Render api/daily.json.

        Args:
            ranker_output: Output from the ranker.
            sources_status: Per-source status list.
            run_info: Run information.
            run_date: Date string (YYYY-MM-DD).

        Returns:
            GeneratedFile with path and checksum.
        """
        start_time = time.perf_counter()

        self._log.info("json_render_started", run_date=run_date)

        # Build the digest structure
        generated_at = datetime.now(UTC).isoformat()

        digest = DailyDigest(
            run_id=self._run_id,
            run_date=run_date,
            generated_at=generated_at,
            top5=[self._story_to_dict(s) for s in ranker_output.top5],
            model_releases_by_entity={
                entity: [self._story_to_dict(s) for s in stories]
                for entity, stories in sorted(
                    ranker_output.model_releases_by_entity.items()
                )
            },
            papers=[self._story_to_dict(s) for s in ranker_output.papers],
            radar=[self._story_to_dict(s) for s in ranker_output.radar],
            sources_status=[self._source_status_to_dict(s) for s in sources_status],
            run_info=self._run_info_to_dict(run_info),
        )

        # Serialize with stable formatting
        json_content = json.dumps(
            digest.model_dump(),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )

        # Ensure api directory exists
        api_dir = self._output_dir / "api"
        api_dir.mkdir(parents=True, exist_ok=True)

        # Write with atomic semantics
        output_path = api_dir / "daily.json"
        file_info = self._writer.write(output_path, json_content)

        duration_ms = (time.perf_counter() - start_time) * 1000
        self._metrics.record_json_duration(duration_ms)
        self._metrics.record_bytes(file_info.bytes_written)
        self._metrics.record_file_generated()

        self._log.info(
            "json_render_complete",
            file_path=file_info.path,
            bytes_written=file_info.bytes_written,
            sha256=file_info.sha256,
            duration_ms=round(duration_ms, 2),
        )

        return file_info

    def _story_to_dict(self, story: Story) -> dict[str, object]:
        """Convert a Story to a JSON-serializable dictionary.

        Args:
            story: Story to convert.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return story.to_json_dict()

    def _source_status_to_dict(self, status: SourceStatus) -> dict[str, object]:
        """Convert a SourceStatus to a JSON-serializable dictionary.

        Args:
            status: SourceStatus to convert.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "source_id": status.source_id,
            "name": status.name,
            "tier": status.tier,
            "method": status.method,
            "status": status.status.value,
            "reason_code": status.reason_code,
            "reason_text": status.reason_text,
            "remediation_hint": status.remediation_hint,
            "newest_item_date": (
                status.newest_item_date.isoformat() if status.newest_item_date else None
            ),
            "last_fetch_status_code": status.last_fetch_status_code,
            "items_new": status.items_new,
            "items_updated": status.items_updated,
            "category": status.category,
        }

    def _run_info_to_dict(self, run_info: RunInfo) -> dict[str, object]:
        """Convert RunInfo to a JSON-serializable dictionary.

        Args:
            run_info: RunInfo to convert.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "run_id": run_info.run_id,
            "started_at": run_info.started_at.isoformat(),
            "finished_at": (
                run_info.finished_at.isoformat() if run_info.finished_at else None
            ),
            "success": run_info.success,
            "error_summary": run_info.error_summary,
            "items_total": run_info.items_total,
            "stories_total": run_info.stories_total,
        }

