# E2E Test Plan - add-static-html-renderer

## Overview

End-to-end test plan for validating the static HTML renderer feature.

## Prerequisites

1. Python 3.13+ installed
2. `uv` package manager installed
3. Project dependencies installed (`uv sync --all-groups`)
4. A test output directory (will be created by CLI)

## Test Steps

### Step 1: Run Renderer CLI Command

```bash
# Create a test output directory
mkdir -p /tmp/test-renderer-output

# Run the render command with sample data
uv run python -m src.cli.digest render --out /tmp/test-renderer-output --tz UTC --no-json-logs -v
```

**Expected Result:**
- Command exits with code 0
- Output shows: "Render complete. 6 files generated."
- Lists all generated files with byte counts

### Step 2: Verify Generated Files Exist

```bash
# Check all required files exist
ls -la /tmp/test-renderer-output/
ls -la /tmp/test-renderer-output/api/
ls -la /tmp/test-renderer-output/day/
```

**Expected Files:**
- `/tmp/test-renderer-output/index.html`
- `/tmp/test-renderer-output/archive.html`
- `/tmp/test-renderer-output/sources.html`
- `/tmp/test-renderer-output/status.html`
- `/tmp/test-renderer-output/api/daily.json`
- `/tmp/test-renderer-output/day/YYYY-MM-DD.html` (current date)

### Step 3: Validate JSON Schema

```bash
# Check JSON is valid
cat /tmp/test-renderer-output/api/daily.json | python -m json.tool > /dev/null && echo "Valid JSON"

# Check required fields
python -c "
import json
data = json.load(open('/tmp/test-renderer-output/api/daily.json'))
assert 'run_id' in data
assert 'run_date' in data
assert 'generated_at' in data
assert 'top5' in data
assert isinstance(data['top5'], list)
print('JSON schema validation passed')
"
```

**Expected Result:**
- JSON is valid
- Contains required fields: run_id, run_date, generated_at, top5

### Step 4: Validate HTML Content

```bash
# Check index.html has required sections
grep -q "Research Digest" /tmp/test-renderer-output/index.html && echo "Title present"
grep -q "Top 5" /tmp/test-renderer-output/index.html && echo "Top 5 section present"
grep -q "archive.html" /tmp/test-renderer-output/index.html && echo "Navigation present"
```

**Expected Result:**
- All grep commands succeed (exit code 0)

### Step 5: Verify HTML Escaping (Security)

```bash
# No raw script tags should appear in any HTML
! grep -r '<script>' /tmp/test-renderer-output/*.html && echo "No unescaped scripts"
```

**Expected Result:**
- No unescaped `<script>` tags found

### Step 6: Verify Links Are Clickable

```bash
# Check links in index.html
grep -o 'href="[^"]*"' /tmp/test-renderer-output/index.html | head -10
```

**Expected Result:**
- Links to archive.html, sources.html, status.html, api/daily.json are present

### Step 7: Verify Date Unknown Display

Run tests that verify items without dates display "Date unknown":

```bash
uv run pytest tests/unit/test_renderer/test_html_renderer.py::TestHtmlRenderer::test_render_shows_date_unknown -v
```

**Expected Result:**
- Test passes

### Step 8: Run All Renderer Tests

```bash
uv run pytest tests/unit/test_renderer/ tests/integration/test_renderer_integration.py -v
```

**Expected Result:**
- All tests pass (59 tests)

### Step 9: Browser Validation (Manual)

1. Open `/tmp/test-renderer-output/index.html` in Chrome
2. Open DevTools (F12)
3. Check Console tab - should have 0 errors
4. Check Network tab - should have 0 failures
5. Click all navigation links and verify they work

**Expected Result:**
- Console: 0 errors
- Network: 0 failures
- All links navigate correctly

### Step 10: Idempotency Check

```bash
# Run renderer twice and compare JSON (excluding generated_at)
mkdir -p /tmp/render1 /tmp/render2
uv run python -m src.cli.digest render --out /tmp/render1 --tz UTC --no-json-logs
uv run python -m src.cli.digest render --out /tmp/render2 --tz UTC --no-json-logs

# Compare structure (excluding timestamps)
python -c "
import json
d1 = json.load(open('/tmp/render1/api/daily.json'))
d2 = json.load(open('/tmp/render2/api/daily.json'))
del d1['generated_at'], d2['generated_at']
assert d1 == d2
print('Idempotency check passed')
"
```

**Expected Result:**
- Both renders produce identical JSON structure

## Acceptance Criteria Checklist

- [ ] index.html exists and contains Top 5 section
- [ ] archive.html exists with date links
- [ ] sources.html exists with source status table
- [ ] status.html exists with run history
- [ ] api/daily.json exists with valid schema
- [ ] day/YYYY-MM-DD.html exists for current date
- [ ] HTML content is properly escaped (no XSS)
- [ ] All navigation links work
- [ ] Chrome DevTools: 0 console errors
- [ ] Chrome DevTools: 0 network failures
- [ ] All automated tests pass

## Evidence Collection

After completing all steps, capture:

1. Screenshot of index.html in browser
2. Screenshot of Chrome DevTools showing 0 errors
3. Copy of test output showing all tests pass
4. SHA-256 checksums of generated files
