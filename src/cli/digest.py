"""CLI commands for the digest system."""

import logging
import subprocess
import sys
import uuid
import zoneinfo
from dataclasses import dataclass
from pathlib import Path

import click
import structlog

from src.config.constants import (
    COMPONENT_CLI,
    FEATURE_KEY,
    STATUS_P1_DONE,
    VALIDATION_PASSED,
)
from src.config.error_hints import format_validation_error
from src.config.loader import ConfigLoader
from src.config.state_machine import ConfigState
from src.evidence.capture import EvidenceCapture
from src.observability.logging import bind_run_context, configure_logging
from src.store.store import StateStore


logger = structlog.get_logger()


def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(  # noqa: S603, S607
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()[:12]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


@dataclass
class RunOptions:
    """Options for the run command."""

    config_path: Path
    entities_path: Path
    topics_path: Path
    state_path: Path
    output_dir: Path
    timezone: str
    json_logs: bool
    verbose: bool
    dry_run: bool = False


def _execute_run(options: RunOptions) -> None:
    """Execute the run command with given options."""
    # Generate run ID
    run_id = str(uuid.uuid4())

    # Configure logging
    log_level = logging.DEBUG if options.verbose else logging.INFO
    configure_logging(level=log_level, json_format=options.json_logs)
    bind_run_context(run_id)

    log = logger.bind(
        run_id=run_id,
        component=COMPONENT_CLI,
        command="run",
        dry_run=options.dry_run,
    )

    log.info(
        "digest_run_started",
        config_path=str(options.config_path),
        entities_path=str(options.entities_path),
        topics_path=str(options.topics_path),
        state_path=str(options.state_path),
        output_dir=str(options.output_dir),
        timezone=options.timezone,
    )

    # Validate timezone format
    try:
        zoneinfo.ZoneInfo(options.timezone)
    except (KeyError, zoneinfo.ZoneInfoNotFoundError):
        log.warning("invalid_timezone", timezone=options.timezone)
        click.echo(f"Error: Invalid timezone '{options.timezone}'", err=True)
        sys.exit(1)

    # Load and validate configuration
    loader = ConfigLoader(run_id=run_id)

    try:
        effective_config = loader.load(
            sources_path=options.config_path,
            entities_path=options.entities_path,
            topics_path=options.topics_path,
        )
    except Exception as e:
        log.warning(
            "config_load_failed",
            error=str(e),
            validation_errors=loader.validation_errors,
        )

        # Print validation summary to stderr with hints
        click.echo("Configuration validation failed:", err=True)
        for error in loader.validation_errors:
            formatted = format_validation_error(
                location=error["loc"],
                message=error["msg"],
                error_type=error.get("type", "unknown"),
                include_hint=True,
            )
            click.echo(f"  - {formatted}", err=True)

        sys.exit(1)

    # Configuration is now validated and ready
    if loader.state != ConfigState.READY:
        log.error("unexpected_state", state=loader.state.name)
        sys.exit(1)

    log.info(
        "config_validated",
        sources_count=len(effective_config.sources.sources),
        entities_count=len(effective_config.entities.entities),
        topics_count=len(effective_config.topics.topics),
        config_checksum=effective_config.compute_checksum(),
    )

    # Initialize state store (skip in dry-run mode)
    if not options.dry_run:
        # Get strip params from topics config for URL canonicalization
        strip_params = list(effective_config.topics.dedupe.canonical_url_strip_params)

        with StateStore(
            db_path=options.state_path,
            strip_params=strip_params,
            run_id=run_id,
        ) as store:
            log.info(
                "store_connected",
                db_path=str(options.state_path),
                schema_version=store.get_schema_version(),
            )

            # Begin run tracking
            run_record = store.begin_run(run_id)
            log.info(
                "run_started_in_store",
                run_id=run_record.run_id,
                started_at=run_record.started_at.isoformat(),
            )

            # Get last successful run for delta detection
            last_success = store.get_last_successful_run_finished_at()
            if last_success:
                log.info(
                    "last_successful_run",
                    finished_at=last_success.isoformat(),
                )
            else:
                log.info("no_previous_successful_run")

            # TODO: Actual collection and rendering will happen here in future features

            # End run successfully
            run_record = store.end_run(run_id, success=True)
            log.info(
                "run_finished_in_store",
                run_id=run_record.run_id,
                success=run_record.success,
                finished_at=run_record.finished_at.isoformat()
                if run_record.finished_at
                else None,
            )

            # Get stats for logging
            stats = store.get_stats()
            log.info(
                "store_stats",
                runs=stats["runs"],
                items=stats["items"],
                http_cache=stats["http_cache"],
            )

    # Write evidence (skip in dry-run mode)
    if not options.dry_run:
        git_commit = get_git_commit()
        evidence = EvidenceCapture(
            feature_key=FEATURE_KEY,
            run_id=run_id,
            git_commit=git_commit,
        )

        evidence.write_state_md(
            config=effective_config,
            status=STATUS_P1_DONE,
            validation_result=VALIDATION_PASSED,
        )
    else:
        log.info(
            "dry_run_skip_evidence", message="Skipping evidence capture in dry-run mode"
        )

    log.info(
        "digest_run_complete",
        state="READY",
        config_checksum=effective_config.compute_checksum(),
    )

    click.echo(f"Configuration validated successfully. Run ID: {run_id}")


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Research Report digest system CLI."""


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to sources.yaml configuration file.",
)
@click.option(
    "--entities",
    "entities_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to entities.yaml configuration file.",
)
@click.option(
    "--topics",
    "topics_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to topics.yaml configuration file.",
)
@click.option(
    "--state",
    "state_path",
    required=True,
    type=click.Path(path_type=Path),
    help="Path to SQLite state database.",
)
@click.option(
    "--out",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Output directory for generated files.",
)
@click.option(
    "--tz",
    "timezone",
    required=True,
    type=str,
    help="Timezone for date handling (e.g., Asia/Taipei).",
)
@click.option(
    "--json-logs/--no-json-logs",
    default=True,
    help="Use JSON format for logs (default: true).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Validate configuration without writing state or evidence.",
)
def run(  # noqa: PLR0913
    config_path: Path,
    entities_path: Path,
    topics_path: Path,
    state_path: Path,
    output_dir: Path,
    timezone: str,
    json_logs: bool,
    verbose: bool,
    dry_run: bool,
) -> None:
    """Run the digest pipeline.

    Loads and validates configuration, then executes the digest pipeline.
    Configuration validation happens before any network calls.

    Use --dry-run to validate configuration without writing any state files.
    This is useful for CI/CD pipelines to validate configs before deployment.
    """
    options = RunOptions(
        config_path=config_path,
        entities_path=entities_path,
        topics_path=topics_path,
        state_path=state_path,
        output_dir=output_dir,
        timezone=timezone,
        json_logs=json_logs,
        verbose=verbose,
        dry_run=dry_run,
    )
    _execute_run(options)


@cli.command()
@click.option(
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to sources.yaml configuration file.",
)
@click.option(
    "--entities",
    "entities_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to entities.yaml configuration file.",
)
@click.option(
    "--topics",
    "topics_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to topics.yaml configuration file.",
)
def validate(
    config_path: Path,
    entities_path: Path,
    topics_path: Path,
) -> None:
    """Validate configuration files without running the pipeline."""
    run_id = str(uuid.uuid4())
    configure_logging(json_format=False)
    bind_run_context(run_id)

    loader = ConfigLoader(run_id=run_id)

    try:
        effective_config = loader.load(
            sources_path=config_path,
            entities_path=entities_path,
            topics_path=topics_path,
        )

        click.echo("Configuration is valid!")
        click.echo(f"  Sources: {len(effective_config.sources.sources)}")
        click.echo(f"  Entities: {len(effective_config.entities.entities)}")
        click.echo(f"  Topics: {len(effective_config.topics.topics)}")
        click.echo(f"  Checksum: {effective_config.compute_checksum()}")

    except Exception:
        click.echo("Configuration validation failed:", err=True)
        for error in loader.validation_errors:
            formatted = format_validation_error(
                location=error["loc"],
                message=error["msg"],
                error_type=error.get("type", "unknown"),
                include_hint=True,
            )
            click.echo(f"  - {formatted}", err=True)
        sys.exit(1)


@cli.command("db-stats")
@click.option(
    "--state",
    "state_path",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Path to SQLite state database.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output as JSON.",
)
def db_stats(state_path: Path, json_output: bool) -> None:
    """Display state database statistics.

    Shows row counts for all tables, schema version, and last successful run.
    """
    import json

    configure_logging(json_format=False)

    with StateStore(db_path=state_path) as store:
        stats = store.get_stats()
        schema_version = store.get_schema_version()
        last_success = store.get_last_successful_run_finished_at()

        if json_output:
            output = {
                "schema_version": schema_version,
                "tables": stats,
                "last_successful_run": (
                    last_success.isoformat() if last_success else None
                ),
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo("State Database Statistics")
            click.echo("=" * 40)
            click.echo(f"  Schema Version: {schema_version}")
            click.echo(
                f"  Last Successful Run: {last_success.isoformat() if last_success else 'None'}"
            )
            click.echo("")
            click.echo("Table Row Counts:")
            for table, count in sorted(stats.items()):
                click.echo(f"  {table}: {count}")


@cli.command()
@click.option(
    "--out",
    "output_dir",
    required=True,
    type=click.Path(path_type=Path),
    help="Output directory for generated files.",
)
@click.option(
    "--tz",
    "timezone",
    default="UTC",
    type=str,
    help="Timezone for date display (default: UTC).",
)
@click.option(
    "--json-logs/--no-json-logs",
    default=True,
    help="Use JSON format for logs (default: true).",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging.",
)
def render(
    output_dir: Path,
    timezone: str,
    json_logs: bool,
    verbose: bool,
) -> None:
    """Render static HTML pages from fixture data.

    This command is primarily for testing the renderer with sample data.
    In production, rendering happens as part of the full pipeline run.
    """
    from datetime import UTC, datetime

    from src.config.schemas.base import LinkType
    from src.linker.models import Story, StoryLink
    from src.ranker.models import RankerOutput
    from src.renderer import RenderResult, RunInfo, StaticRenderer

    run_id = str(uuid.uuid4())

    log_level = logging.DEBUG if verbose else logging.INFO
    configure_logging(level=log_level, json_format=json_logs)
    bind_run_context(run_id)

    log = logger.bind(run_id=run_id, component=COMPONENT_CLI, command="render")
    log.info("render_started", output_dir=str(output_dir), timezone=timezone)

    # Create sample data for testing
    sample_story = Story(
        story_id="sample-story-1",
        title="Sample Story for Testing",
        primary_link=StoryLink(
            url="https://example.com/sample",
            link_type=LinkType.OFFICIAL,
            source_id="sample-source",
            tier=0,
            title="Sample Story for Testing",
        ),
        links=[
            StoryLink(
                url="https://example.com/sample",
                link_type=LinkType.OFFICIAL,
                source_id="sample-source",
                tier=0,
                title="Sample Story for Testing",
            )
        ],
        entities=["sample-entity"],
        published_at=datetime.now(UTC),
    )

    ranker_output = RankerOutput(
        top5=[sample_story],
        model_releases_by_entity={"sample-entity": [sample_story]},
        papers=[],
        radar=[sample_story],
        output_checksum="sample-checksum",
    )

    run_info = RunInfo(
        run_id=run_id,
        started_at=datetime.now(UTC),
        items_total=1,
        stories_total=1,
    )

    renderer = StaticRenderer(
        run_id=run_id,
        output_dir=output_dir,
        timezone=timezone,
    )

    result: RenderResult = renderer.render(
        ranker_output=ranker_output,
        sources_status=[],
        run_info=run_info,
        recent_runs=[run_info],
    )

    if result.success:
        log.info(
            "render_complete",
            files_count=len(result.manifest.files),
            total_bytes=result.manifest.total_bytes,
            duration_ms=round(result.manifest.duration_ms, 2),
        )
        click.echo(f"Render complete. {len(result.manifest.files)} files generated.")
        click.echo(f"Output directory: {output_dir}")
        for file_info in result.manifest.files:
            click.echo(f"  {file_info.path} ({file_info.bytes_written} bytes)")
    else:
        log.error("render_failed", error=result.error_summary)
        click.echo(f"Render failed: {result.error_summary}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
