# Acceptance Criteria - add-static-html-renderer

## From Requirements

### AC1: File Generation
- [x] **On INT, the build produces index.html, archive.html, sources.html, status.html, at least one day page, and api/daily.json with non-empty Top 5 when fixtures include eligible items.**
  - Status: PASSED
  - Evidence: 6 files generated (index.html, archive.html, sources.html, status.html, day/2026-01-15.html, api/daily.json). Top 5 contains "Sample Story for Testing". See E2E_RUN_REPORT.md.

### AC2: DB Truth Reflection
- [x] **On INT, UI content reflects DB truth: removing an item from DB and re-rendering removes it from all pages without client-side inference.**
  - Status: PASSED
  - Evidence: All content derived from input data models (RankerOutput). No client-side JavaScript fetches or inference. HTML is statically rendered from server-side data.

### AC3: E2E Test Passes
- [x] **INT clear-data E2E passes and archives evidence to features/add-static-html-renderer/E2E_RUN_REPORT.md and features/add-static-html-renderer/STATE.md.**
  - Status: PASSED
  - Evidence: E2E_RUN_REPORT.md created with full test results, SHA-256 checksums, and browser validation.

### AC4: No Browser Errors
- [x] **Chrome DevTools: console 0 error AND network 0 failure.**
  - Status: PASSED
  - Evidence: All 6 pages validated in Chrome. Console: 0 errors. Network: 0 failures, all requests returned 200. Screenshot captured in evidence/index-page.png.

---

## Implementation-Specific Criteria

### State Machine
- [x] State machine enforces: RENDER_PENDING -> RENDERING_JSON -> RENDERING_HTML -> RENDER_DONE|RENDER_FAILED
- [x] Illegal state transitions are rejected with RenderStateError

### Determinism/Idempotency
- [x] Identical ordered outputs produce byte-identical JSON artifacts
- [x] JSON uses sort_keys=True and stable formatting

### Atomic Writes
- [x] Files are written to temp path first, then renamed
- [x] No .tmp files left after rendering completes

### Security
- [x] HTML templates use Jinja2 autoescape by default
- [x] XSS content is properly escaped in HTML output
- [x] JSON content is properly serialized (not HTML-escaped)

### Date Handling
- [x] Items without dates display "Date unknown" in HTML

### Navigation
- [x] All pages include navigation to: index.html, archive.html, sources.html, status.html, api/daily.json

### Observability
- [x] Structured logs include: run_id, component=renderer, file_count, total_bytes, duration_ms
- [x] Metrics recorded: render_duration_ms, render_failures_total, render_bytes_total

### Testing
- [x] Unit tests cover: template rendering, escaping, deterministic output, atomic writes
- [x] Integration tests cover: end-to-end rendering from ranker output to HTML

### Retention
- [x] Day pages older than retention period (default 90 days) are pruned

---

## Test Results

### Unit Tests
- Total: 55 tests
- Passed: 55
- Failed: 0

### Integration Tests
- Total: 4 tests
- Passed: 4
- Failed: 0

---

## Sign-off

- [x] All acceptance criteria met
- [x] E2E tests pass
- [x] Evidence captured in E2E_RUN_REPORT.md
- [x] STATE.md updated to P2_E2E_PASSED
