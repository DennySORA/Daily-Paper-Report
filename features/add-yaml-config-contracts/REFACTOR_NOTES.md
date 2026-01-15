# REFACTOR_NOTES.md - add-yaml-config-contracts

## Refactoring Summary

**Date**: 2026-01-14
**Status**: P3_REFACTORED_DEPLOYED
**Tests Before**: 70 | **Tests After**: 97 (+27 new tests)

## Pain Points Identified

| Issue | Location | Impact |
|-------|----------|--------|
| Magic strings scattered throughout code | digest.py:124, evidence/capture.py | Maintenance burden, inconsistency risk |
| Raw Pydantic error messages | CLI output | Poor user experience, no actionable guidance |
| No dry-run capability | CLI | Can't validate configs in CI without side effects |
| Repetitive test patterns | test_schemas.py | DRY violation, harder to maintain |

## Refactoring Changes

### 1. Constants Extraction (SRP, DIP)

**Files Changed**:
- Created `src/config/constants.py`
- Updated `src/cli/digest.py`

**What Changed**:
- Extracted magic strings to named constants
- Feature key, status values, component names, URL schemes, file types

**Benefits**:
- Single source of truth for values
- IDE autocomplete support
- Easier to update values consistently

**Rollback**: Delete `constants.py`, revert import changes in `digest.py`

### 2. Error Hints System (OCP, SRP)

**Files Changed**:
- Created `src/config/error_hints.py`
- Updated `src/cli/digest.py`

**What Changed**:
- Created `ERROR_HINTS` mapping for Pydantic error types
- Created `FIELD_HINTS` for field-specific guidance
- Added `get_error_hint()` and `format_validation_error()` functions
- Integrated hints into CLI error output

**Before**:
```
  - sources.1.url: Field required
  - sources.2.tier: Input should be 0, 1 or 2
```

**After**:
```
  - sources.1.url: Field required
    Hint: Must be a valid HTTP/HTTPS URL (e.g., 'https://example.com/feed.xml').
  - sources.2.tier: Input should be 0, 1 or 2
    Hint: Must be 0 (highest priority), 1, or 2 (lowest priority).
```

**Benefits**:
- User-friendly error messages with actionable guidance
- Field-specific hints take precedence over generic hints
- Extensible for new error types without modifying existing code (OCP)

**Rollback**: Delete `error_hints.py`, remove import and `format_validation_error()` calls in `digest.py`

### 3. --dry-run CLI Flag (OCP)

**Files Changed**:
- Updated `src/cli/digest.py`

**What Changed**:
- Added `--dry-run` flag to `run` command
- Added `dry_run` field to `RunOptions` dataclass
- Skip evidence writing when dry-run is enabled
- Log `dry_run_skip_evidence` event

**Usage**:
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

**Benefits**:
- Validate configs in CI/CD without writing state
- Useful for pre-commit hooks
- Non-destructive validation

**Rollback**: Remove `--dry-run` option and related code from `run()` and `_execute_run()`

### 4. New Unit Tests

**Files Added**:
- `tests/unit/test_error_hints.py` (14 tests)
- `tests/unit/test_constants.py` (13 tests)

**Coverage**:
- Error hints: 100% coverage
- Constants: 100% coverage

## Quality Gates Status

| Gate | Status | Details |
|------|--------|---------|
| Linting (ruff check) | PASSED | 0 errors |
| Formatting (ruff format) | PASSED | All files formatted |
| Type Checking (mypy) | PASSED | No issues in 29 files |
| Tests (pytest) | PASSED | 97/97 passed |

## SOLID Compliance

| Principle | Implementation |
|-----------|----------------|
| **SRP** | Constants module has single responsibility; error hints module handles only hints |
| **OCP** | Error hints can be extended without modifying existing code; CLI extended with new flag |
| **LSP** | No inheritance changes |
| **ISP** | Small, focused interfaces maintained |
| **DIP** | Constants imported as abstractions; no tight coupling to literal values |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Error hints might not cover all Pydantic error types | Low | Low | Default hint provided for unknown types |
| Constants might drift from actual usage | Low | Medium | Tests validate constant values exist and are non-empty |
| --dry-run might be forgotten in production | Low | None | Logs clearly indicate dry_run=true |

## Rollback Plan

Each refactoring is designed to be independently reversible:

1. **Constants**: Revert to inline strings (no functional change)
2. **Error Hints**: Remove hint formatting (CLI still works, just less user-friendly)
3. **Dry Run**: Remove flag (backward compatible, run command still works)

Full rollback:
```bash
git checkout HEAD~1 -- src/config/constants.py src/config/error_hints.py src/cli/digest.py
rm -f tests/unit/test_constants.py tests/unit/test_error_hints.py
```

## Files Changed Summary

| File | Change Type | Lines Added | Lines Removed |
|------|-------------|-------------|---------------|
| src/config/constants.py | New | 25 | 0 |
| src/config/error_hints.py | New | 88 | 0 |
| src/cli/digest.py | Modified | 35 | 15 |
| tests/unit/test_constants.py | New | 95 | 0 |
| tests/unit/test_error_hints.py | New | 115 | 0 |

## Next Steps (Prompt #4)

1. Run regression E2E to verify all acceptance criteria still pass
2. Verify --dry-run works correctly in E2E scenario
3. Verify error hints appear correctly for all error types
4. Update STATUS to READY if all checks pass
