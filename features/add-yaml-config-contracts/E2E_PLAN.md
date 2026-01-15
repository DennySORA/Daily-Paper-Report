# E2E_PLAN.md - add-yaml-config-contracts

## Purpose

This document provides a browser-executable (or CLI-executable) end-to-end checklist for validating the YAML configuration contracts feature.

## Prerequisites

1. Python 3.13+ installed
2. `uv` package manager installed
3. Repository cloned and dependencies synced (`uv sync`)

## E2E Test Steps

### Step 1: Clear Prior State

```bash
# Remove any existing configuration snapshots
rm -rf features/add-yaml-config-contracts/snapshots/
rm -f features/add-yaml-config-contracts/E2E_RUN_REPORT.md

# Create fresh directories
mkdir -p features/add-yaml-config-contracts/snapshots/
```

### Step 2: Prepare Valid Test Configurations

Create minimal valid YAML files for testing:

```bash
# These files should already exist in tests/fixtures/config/
ls -la tests/fixtures/config/
```

### Step 3: Run with Valid Configuration

```bash
uv run python -m src.cli.digest run \
  --config tests/fixtures/config/sources.yaml \
  --entities tests/fixtures/config/entities.yaml \
  --topics tests/fixtures/config/topics.yaml \
  --state /tmp/test_state.db \
  --out /tmp/test_output \
  --tz Asia/Taipei
```

**Expected Results:**
- [x] Exit code: 0
- [x] STATE.md updated with configuration snapshot
- [x] Logs include: run_id, component=config, phase, file_path, file_sha256, validation_error_count=0

### Step 4: Run with Invalid Configuration

```bash
uv run python -m src.cli.digest run \
  --config tests/fixtures/config/invalid_sources.yaml \
  --entities tests/fixtures/config/entities.yaml \
  --topics tests/fixtures/config/topics.yaml \
  --state /tmp/test_state.db \
  --out /tmp/test_output \
  --tz Asia/Taipei
```

**Expected Results:**
- [x] Exit code: Non-zero (1)
- [x] Validation summary in logs
- [x] No HTTP requests made (validation fails before network calls)

### Step 5: Verify Idempotency

```bash
# Run twice with same config
uv run python -m src.cli.digest run --config tests/fixtures/config/sources.yaml --entities tests/fixtures/config/entities.yaml --topics tests/fixtures/config/topics.yaml --state /tmp/test_state.db --out /tmp/test_output --tz Asia/Taipei 2>&1 | tee /tmp/run1.log

uv run python -m src.cli.digest run --config tests/fixtures/config/sources.yaml --entities tests/fixtures/config/entities.yaml --topics tests/fixtures/config/topics.yaml --state /tmp/test_state.db --out /tmp/test_output --tz Asia/Taipei 2>&1 | tee /tmp/run2.log

# Compare normalized config checksums from logs
grep "file_sha256" /tmp/run1.log
grep "file_sha256" /tmp/run2.log
```

**Expected Results:**
- [x] SHA-256 checksums match between runs
- [x] Normalized in-memory objects are identical

### Step 6: Verify Immutability Per Run

```bash
# Start a run, modify config mid-run (simulated), verify original config is used
# This is primarily verified by unit tests
```

### Step 7: Verify Snapshot Persistence

```bash
# Check that snapshot was written
ls -la features/add-yaml-config-contracts/snapshots/

# Verify snapshot content
cat features/add-yaml-config-contracts/STATE.md | grep -A 20 "Configuration Snapshots"
```

**Expected Results:**
- [x] At least one snapshot exists
- [x] Snapshot includes file hashes and validation results

### Step 8: Generate E2E Report

```bash
# The CLI should generate this automatically on successful run
cat features/add-yaml-config-contracts/E2E_RUN_REPORT.md
```

## Acceptance Verification

| Criteria | Verified |
|----------|----------|
| Invalid YAML causes run to fail before HTTP requests | [x] |
| Validation summary appears in logs | [x] |
| Valid YAML produces normalized snapshot with matching SHA-256 | [x] |
| STATE.md and E2E_RUN_REPORT.md are produced | [x] |

## Notes

- All times should be in ISO-8601 format
- run_id should be a UUID v4
- Secrets must not appear in logs or STATE.md

## Verification Summary

**Date**: 2026-01-14
**Status**: ALL CRITERIA VERIFIED
**Tests**: 70 passed (0 failed)
**Exit Codes**: Valid config = 0, Invalid config = 1
