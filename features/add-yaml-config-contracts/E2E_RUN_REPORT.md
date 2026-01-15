# E2E_RUN_REPORT.md - add-yaml-config-contracts

## Run Summary

| Field | Value |
|-------|-------|
| **Run ID** | regression-e2e-2026-01-14 |
| **Feature Key** | add-yaml-config-contracts |
| **Git Commit** | (uncommitted changes) |
| **Started At** | 2026-01-14T07:05:17Z |
| **Completed At** | 2026-01-14T07:06:48Z |
| **Status** | PASSED |
| **Type** | Regression E2E (Post-Refactor) |

## Environment

- **Python Version**: 3.13.3
- **Platform**: darwin (macOS)
- **Package Manager**: uv

## Test Results (Post-Refactor)

### Unit and Integration Tests

| Category | Count | Status |
|----------|-------|--------|
| Schema Validation (test_schemas.py) | 51 | PASSED |
| State Machine (test_state_machine.py) | 8 | PASSED |
| EffectiveConfig (test_effective_config.py) | 5 | PASSED |
| Integration (test_config_loading.py) | 6 | PASSED |
| **New: Error Hints (test_error_hints.py)** | **14** | **PASSED** |
| **New: Constants (test_constants.py)** | **13** | **PASSED** |
| **Total** | **97** | **PASSED** |

### E2E Regression Validation Steps

| Step | Description | Result |
|------|-------------|--------|
| 1 | Run full test suite (97 tests) | PASSED |
| 2 | Run quality gates (lint/format/typecheck) | PASSED |
| 3 | AC-1: Invalid config fails with hints | PASSED (exit code: 1) |
| 4 | AC-2: Verify checksum stability | PASSED (file_sha256 stable) |
| 5 | AC-3: Evidence writing | PASSED (state_md_written) |
| 6 | New: --dry-run skips evidence | PASSED (dry_run_skip_evidence) |
| 7 | New: Error hints display correctly | PASSED |

## Acceptance Criteria Verification (Regression)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| AC-1: Invalid config fails before HTTP | PASSED | Exit code 1, validation summary with hints, phase=FAILED |
| AC-2: Valid config produces stable checksum | PASSED | file_sha256 values identical across runs |
| AC-3: E2E passes and archives evidence | PASSED | 97 tests passed, STATE.md written, E2E_RUN_REPORT.md updated |

## New Functionality Verification

| Feature | Status | Evidence |
|---------|--------|----------|
| --dry-run flag | PASSED | dry_run=true in logs, dry_run_skip_evidence event, no state_md_written |
| Error hints | PASSED | User-friendly hints displayed for all error types |
| Constants module | PASSED | FEATURE_KEY, STATUS_P1_DONE used correctly |

## Structured Log Verification

All required structured log fields were verified:

- [x] `run_id` - UUID present in all log entries
- [x] `component=config` - Present in config-related logs
- [x] `phase` - LOADING/VALIDATED/READY/FAILED states logged
- [x] `file_path` - Paths to config files
- [x] `file_sha256` - SHA-256 checksums for each file
- [x] `validation_error_count` - 0 for valid, 3 for invalid
- [x] `dry_run` - Present when --dry-run flag used

## File Checksums (Stable Across All Runs)

| File | SHA-256 |
|------|---------|
| sources.yaml | 642df41d319f9dce36e30f432e5b63ce2cc64660929d745dba60b0e6c90e2bf1 |
| entities.yaml | b7cdf460fcd2793362d6d34ea6bd649f3d3d6afaa7431313bd9c5340da010500 |
| topics.yaml | 0ab411e138addddbad2bdb60fe690f562ca732ea177aa3ee9f686e5f28497545 |

## Quality Gates (Final)

| Gate | Status |
|------|--------|
| Linting (ruff check) | PASSED |
| Formatting (ruff format) | PASSED |
| Type Checking (mypy) | PASSED (29 files) |
| All Tests (pytest) | PASSED (97/97) |

## Artifacts

- `features/add-yaml-config-contracts/STATE.md` - Configuration state snapshot
- `features/add-yaml-config-contracts/ACCEPTANCE.md` - Acceptance criteria checklist
- `features/add-yaml-config-contracts/E2E_PLAN.md` - E2E test plan
- `features/add-yaml-config-contracts/REFACTOR_NOTES.md` - Refactoring documentation
- `src/config/constants.py` - Named constants
- `src/config/error_hints.py` - Error hints system
- `tests/unit/test_constants.py` - Constants tests
- `tests/unit/test_error_hints.py` - Error hints tests

## Error Hints Sample Output

```
Configuration validation failed:
  - sources.1.url: Field required
    Hint: Must be a valid HTTP/HTTPS URL (e.g., 'https://example.com/feed.xml').
  - sources.2.tier: Input should be 0, 1 or 2
    Hint: Must be 0 (highest priority), 1, or 2 (lowest priority).
  - sources.3.method: Input should be 'rss_atom', 'arxiv_api', ...
    Hint: Must be one of: rss_atom, arxiv_api, openreview_venue, ...
```

## Dry-Run Sample Output

```json
{"event": "dry_run_skip_evidence", "message": "Skipping evidence capture in dry-run mode", "dry_run": true}
{"event": "digest_run_complete", "state": "READY", "dry_run": true}
```

## Feature Close-Out Summary

This feature is now **READY** for production use:

1. **Core Functionality**: YAML config contracts validated with strict Pydantic schemas
2. **State Machine**: Enforces UNLOADED → LOADING → VALIDATED → READY transitions
3. **Fail Fast**: Invalid configs fail before any HTTP requests
4. **Audit Logging**: Structured logs with run_id, file checksums, validation results
5. **Immutability**: Frozen configs prevent modification after validation
6. **Error Hints**: User-friendly hints with actionable remediation steps
7. **Dry Run**: CI/CD-friendly validation without side effects
8. **Test Coverage**: 97 tests covering all functionality
9. **Quality Gates**: All passing (lint, format, typecheck, tests)

### Usage Examples

**Validate configuration (with hints on failure):**
```bash
uv run python -m src.cli.digest validate \
  --config sources.yaml \
  --entities entities.yaml \
  --topics topics.yaml
```

**Run with dry-run (CI/CD validation):**
```bash
uv run python -m src.cli.digest run \
  --config sources.yaml \
  --entities entities.yaml \
  --topics topics.yaml \
  --state state.db \
  --out ./public \
  --tz Asia/Taipei \
  --dry-run
```

**Production run:**
```bash
uv run python -m src.cli.digest run \
  --config sources.yaml \
  --entities entities.yaml \
  --topics topics.yaml \
  --state state.db \
  --out ./public \
  --tz Asia/Taipei
```
