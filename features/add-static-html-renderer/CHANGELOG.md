# Changelog - add-static-html-renderer

## [Unreleased]

### Added

#### Core Renderer Module
- **State Machine** (`src/renderer/state_machine.py`): Implements render lifecycle with states RENDER_PENDING -> RENDERING_JSON -> RENDERING_HTML -> RENDER_DONE|RENDER_FAILED. Illegal transitions raise `RenderStateError`.

- **Models** (`src/renderer/models.py`): Data models for renderer including:
  - `SourceStatusCode`: Enum for source status (NO_UPDATE, HAS_UPDATE, FETCH_FAILED, etc.)
  - `SourceStatus`: Per-source status information
  - `RunInfo`: Pipeline run information
  - `DailyDigest`: Schema for api/daily.json
  - `GeneratedFile`: Metadata about generated files
  - `RenderManifest`: Manifest of all generated files with checksums
  - `RenderContext`: Context for template rendering
  - `RenderResult`: Success/failure result with manifest

- **Metrics** (`src/renderer/metrics.py`): Singleton metrics collector for:
  - `render_duration_ms`: Total render time
  - `render_failures_total`: Number of failed renders
  - `render_bytes_total`: Total bytes written
  - Per-template durations

- **JSON Renderer** (`src/renderer/json_renderer.py`): Generates `api/daily.json` with:
  - Deterministic output (sort_keys=True, stable formatting)
  - Atomic writes (temp file + rename)
  - SHA-256 checksums

- **HTML Renderer** (`src/renderer/html_renderer.py`): Generates HTML pages using Jinja2 with:
  - Auto-escaping enabled for XSS prevention
  - Atomic writes for crash safety
  - Support for all page types

- **Templates** (`src/renderer/templates/`):
  - `base.html`: Shared layout with navigation
  - `index.html`: Latest digest page
  - `day.html`: Per-date archive page
  - `archive.html`: Date index page
  - `sources.html`: Per-source status table
  - `status.html`: Recent run history

- **Orchestrator** (`src/renderer/renderer.py`): `StaticRenderer` class that:
  - Orchestrates JSON + HTML rendering
  - Manages state machine transitions
  - Implements 90-day retention for day pages
  - Provides pure function API via `render_static()`

#### CLI Integration
- **render command** (`src/cli/digest.py`): New `render` subcommand for testing renderer with sample data

#### Dependencies
- Added `jinja2>=3.1.0` to project dependencies

### Tests Added

#### Unit Tests (`tests/unit/test_renderer/`)
- `test_state_machine.py`: 17 tests for state machine transitions
- `test_models.py`: 15 tests for data models
- `test_json_renderer.py`: 6 tests for JSON rendering
- `test_html_renderer.py`: 8 tests for HTML rendering
- `test_renderer.py`: 9 tests for orchestrator

#### Integration Tests (`tests/integration/`)
- `test_renderer_integration.py`: 4 tests for end-to-end rendering

**Total: 59 new tests, all passing**

### Security

- HTML templates use Jinja2 autoescape by default to prevent XSS
- No client-side JavaScript fetches external resources
- All links use canonical URLs

### Observability

- Structured logs with: run_id, component=renderer, file_count, total_bytes, duration_ms
- Metrics for: render_duration_ms, render_failures_total, render_bytes_total
- Per-template timing for performance analysis

### Technical Notes

- Atomic write semantics: All files written to .tmp first, then renamed
- Deterministic output: Identical inputs produce identical outputs (except generated_at timestamp)
- Retention: Day pages older than 90 days are pruned on each render
- Error handling: Template errors transition to RENDER_FAILED state

## Files Changed

### New Files
```
src/renderer/__init__.py
src/renderer/html_renderer.py
src/renderer/json_renderer.py
src/renderer/metrics.py
src/renderer/models.py
src/renderer/renderer.py
src/renderer/state_machine.py
src/renderer/templates/archive.html
src/renderer/templates/base.html
src/renderer/templates/day.html
src/renderer/templates/index.html
src/renderer/templates/sources.html
src/renderer/templates/status.html
tests/unit/test_renderer/__init__.py
tests/unit/test_renderer/test_html_renderer.py
tests/unit/test_renderer/test_json_renderer.py
tests/unit/test_renderer/test_models.py
tests/unit/test_renderer/test_renderer.py
tests/unit/test_renderer/test_state_machine.py
tests/integration/__init__.py
tests/integration/test_renderer_integration.py
```

### Modified Files
```
pyproject.toml (added jinja2 dependency)
src/cli/digest.py (added render command)
```
