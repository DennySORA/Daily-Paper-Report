"""HTML renderer using Jinja2 templates."""

import time
from pathlib import Path

import structlog
from jinja2 import Environment, PackageLoader, select_autoescape

from src.renderer.io import AtomicWriter
from src.renderer.metrics import RendererMetrics
from src.renderer.models import (
    RenderContext,
    RenderManifest,
)


logger = structlog.get_logger()


class HtmlRenderer:
    """Renders HTML pages using Jinja2 templates.

    Templates are loaded from src/renderer/templates/ with auto-escaping enabled
    to prevent XSS from source content.
    """

    def __init__(
        self,
        run_id: str,
        output_dir: Path,
        metrics: RendererMetrics | None = None,
    ) -> None:
        """Initialize the HTML renderer.

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

        # Set up Jinja2 with auto-escaping for security
        self._env = Environment(
            loader=PackageLoader("src.renderer", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, context: RenderContext, manifest: RenderManifest) -> None:
        """Render all HTML pages.

        Args:
            context: Render context with data for templates.
            manifest: Manifest to record generated files.
        """
        start_time = time.perf_counter()
        self._log.info("html_render_started", run_date=context.run_date)

        # Ensure directories exist
        self._output_dir.mkdir(parents=True, exist_ok=True)
        day_dir = self._output_dir / "day"
        day_dir.mkdir(parents=True, exist_ok=True)

        # Common template context
        common_context = {
            "run_id": context.run_id,
            "run_date": context.run_date,
            "generated_at": context.generated_at,
            "timezone": context.timezone,
        }

        # Render index.html (latest)
        self._render_template(
            "index.html",
            self._output_dir / "index.html",
            manifest,
            {
                **common_context,
                "current_page": "index",
                "top5": context.top5,
                "model_releases_by_entity": context.model_releases_by_entity,
                "papers": context.papers,
                "radar": context.radar,
            },
        )

        # Render day/YYYY-MM-DD.html
        self._render_template(
            "day.html",
            day_dir / f"{context.run_date}.html",
            manifest,
            {
                **common_context,
                "current_page": "day",
                "top5": context.top5,
                "model_releases_by_entity": context.model_releases_by_entity,
                "papers": context.papers,
                "radar": context.radar,
            },
        )

        # Render archive.html
        self._render_template(
            "archive.html",
            self._output_dir / "archive.html",
            manifest,
            {
                **common_context,
                "current_page": "archive",
                "archive_dates": context.archive_dates,
            },
        )

        # Render sources.html
        self._render_template(
            "sources.html",
            self._output_dir / "sources.html",
            manifest,
            {
                **common_context,
                "current_page": "sources",
                "sources_status": context.sources_status,
            },
        )

        # Render status.html
        self._render_template(
            "status.html",
            self._output_dir / "status.html",
            manifest,
            {
                **common_context,
                "current_page": "status",
                "recent_runs": context.recent_runs,
            },
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        self._metrics.record_html_duration(duration_ms)

        self._log.info(
            "html_render_complete",
            files_count=len(manifest.files),
            duration_ms=round(duration_ms, 2),
        )

    def _render_template(
        self,
        template_name: str,
        output_path: Path,
        manifest: RenderManifest,
        context: dict[str, object],
    ) -> None:
        """Render a single template to file.

        Args:
            template_name: Name of the template file.
            output_path: Path to write output.
            manifest: Manifest to record the file.
            context: Template context data.
        """
        start_time = time.perf_counter()

        template = self._env.get_template(template_name)
        content = template.render(**context)

        file_info = self._writer.write(output_path, content)
        manifest.add_file(file_info)

        duration_ms = (time.perf_counter() - start_time) * 1000
        self._metrics.record_template_duration(template_name, duration_ms)
        self._metrics.record_bytes(file_info.bytes_written)
        self._metrics.record_file_generated()

        self._log.debug(
            "template_rendered",
            template=template_name,
            file_path=file_info.path,
            bytes_written=file_info.bytes_written,
            duration_ms=round(duration_ms, 2),
        )
