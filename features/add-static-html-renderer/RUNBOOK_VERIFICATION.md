# Runbook: Verification Environment - add-static-html-renderer

## Overview

This runbook describes how to deploy and verify the static HTML renderer feature.

## Prerequisites

1. Python 3.13+
2. `uv` package manager
3. Git access to repository

## Deployment Steps

### 1. Install Dependencies

```bash
# Clone/checkout the repository
cd /path/to/project

# Sync dependencies
uv sync --all-groups
```

### 2. Verify Installation

```bash
# Check Jinja2 is installed
uv run python -c "import jinja2; print(f'Jinja2 {jinja2.__version__}')"

# Check renderer module imports
uv run python -c "from src.renderer import StaticRenderer, render_static; print('Renderer module OK')"
```

### 3. Run Smoke Test

```bash
# Create output directory
mkdir -p /tmp/renderer-verification

# Run the render CLI command
uv run python -m src.cli.digest render --out /tmp/renderer-verification --tz UTC --no-json-logs -v
```

Expected output:
```
Render complete. 6 files generated.
Output directory: /tmp/renderer-verification
  api/daily.json (XXXX bytes)
  index.html (XXXX bytes)
  day/YYYY-MM-DD.html (XXXX bytes)
  archive.html (XXXX bytes)
  sources.html (XXXX bytes)
  status.html (XXXX bytes)
```

### 4. Verify Generated Files

```bash
# List all generated files
find /tmp/renderer-verification -type f

# Validate JSON
python -m json.tool /tmp/renderer-verification/api/daily.json > /dev/null && echo "JSON valid"

# Check HTML files
for f in index.html archive.html sources.html status.html; do
  if [ -f "/tmp/renderer-verification/$f" ]; then
    echo "$f exists"
  else
    echo "MISSING: $f"
  fi
done
```

### 5. Run Automated Tests

```bash
# Run unit tests
uv run pytest tests/unit/test_renderer/ -v

# Run integration tests
uv run pytest tests/integration/test_renderer_integration.py -v

# Run all tests with coverage
uv run pytest tests/unit/test_renderer/ tests/integration/test_renderer_integration.py --cov=src/renderer
```

## Configuration

### Environment Variables

No environment variables are required for the renderer.

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--out` | Output directory path | Required |
| `--tz` | Timezone for date display | UTC |
| `--json-logs` | Use JSON format for logs | true |
| `--verbose` | Enable debug logging | false |

### Retention Settings

Day page retention is configured in the StaticRenderer constructor:
- Default: 90 days
- Day pages older than this are pruned on each render

## Rollback Procedure

Since the renderer produces static files only, rollback is simple:

1. Delete the generated files in the output directory
2. Revert to previous code version
3. Re-run the pipeline with the previous version

```bash
# Remove generated files
rm -rf /path/to/output/*

# Revert code
git checkout <previous-commit>

# Re-sync and re-run
uv sync
uv run python -m src.cli.digest run ...
```

## Troubleshooting

### Issue: Template Not Found

**Symptom:** `jinja2.exceptions.TemplateNotFound: base.html`

**Solution:** Ensure the renderer is invoked from the project root, or that templates are properly packaged.

### Issue: Permission Denied

**Symptom:** `PermissionError: [Errno 13] Permission denied`

**Solution:** Check that the output directory is writable.

### Issue: Encoding Errors

**Symptom:** `UnicodeEncodeError`

**Solution:** Ensure output directory filesystem supports UTF-8.

## Health Checks

After deployment, verify:

1. **File existence:** All 6 file types generated
2. **JSON validity:** `api/daily.json` parses without errors
3. **HTML validity:** No malformed tags (basic check)
4. **No XSS:** No unescaped `<script>` tags in HTML

```bash
# Quick health check script
OUTPUT_DIR=/tmp/renderer-verification

# Check files exist
[ -f "$OUTPUT_DIR/index.html" ] && echo "✓ index.html" || echo "✗ index.html"
[ -f "$OUTPUT_DIR/archive.html" ] && echo "✓ archive.html" || echo "✗ archive.html"
[ -f "$OUTPUT_DIR/sources.html" ] && echo "✓ sources.html" || echo "✗ sources.html"
[ -f "$OUTPUT_DIR/status.html" ] && echo "✓ status.html" || echo "✗ status.html"
[ -f "$OUTPUT_DIR/api/daily.json" ] && echo "✓ api/daily.json" || echo "✗ api/daily.json"
[ -n "$(ls -A $OUTPUT_DIR/day/)" ] && echo "✓ day/*.html" || echo "✗ day/*.html"

# Check JSON valid
python -m json.tool "$OUTPUT_DIR/api/daily.json" > /dev/null 2>&1 && echo "✓ JSON valid" || echo "✗ JSON invalid"

# Check no raw scripts
! grep -q '<script>' "$OUTPUT_DIR/index.html" && echo "✓ No XSS" || echo "✗ Possible XSS"
```

## Contact

For issues with this feature, check:
1. STATE.md for current status
2. E2E_RUN_REPORT.md for test results
3. CHANGELOG.md for recent changes
