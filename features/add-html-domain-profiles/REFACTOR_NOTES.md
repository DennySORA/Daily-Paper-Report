# Refactor Notes: add-html-domain-profiles

## Refactor Date
2026-01-15 (Prompt #3 - P3_REFACTORED_DEPLOYED)

## Summary

This document records all refactoring changes made during P3 of the feature workflow. All changes are:
- Reversible (no breaking changes to existing APIs)
- Incremental (each change builds on the previous)
- Tested (78 unit tests pass, quality checks clean)

---

## Refactoring Changes

### 1. Exception Hierarchy (`src/collectors/html_profile/exceptions.py`)

**What Changed:**
- Created a structured exception hierarchy for domain-specific error handling
- Base class `HtmlProfileError` inherits from standard `Exception`
- Specialized exceptions for different error conditions:
  - `ProfileNotFoundError`: Profile or URL not found
  - `DateExtractionError`: Date parsing failures
  - `ContentTypeError`: Invalid content type responses
  - `CrossDomainRedirectError`: Security - blocked cross-domain redirects
  - `ItemPageFetchError`: Item page fetching failures

**Why:**
- Follows LSP (Liskov Substitution Principle) - all exceptions are substitutable
- Enables targeted catch blocks for different error types
- Improves observability by capturing context (url, domain, expected vs actual values)

**Rollback:**
- Replace specialized exceptions with generic `ValueError`/`RuntimeError`
- No API changes required

**Files:**
- `src/collectors/html_profile/exceptions.py` (new)
- `src/collectors/html_profile/__init__.py` (updated exports)

---

### 2. Compiled Regex Caching (`src/collectors/html_profile/utils.py`)

**What Changed:**
- Added `compile_regex()` function with `@lru_cache(maxsize=128)` for global caching
- Added `compile_patterns()` helper for batch compilation
- Added `RegexCache` class for instance-level caching when patterns vary by instance

**Why:**
- Avoids recompiling the same regex patterns repeatedly
- LRU cache at module level for patterns used across multiple instances
- Instance-level cache for configuration-driven patterns that may differ

**Performance Impact:**
- Reduces regex compilation overhead in hot paths
- Pattern reuse across multiple date extraction calls

**Rollback:**
- Replace `compile_regex()` calls with `re.compile()` directly
- Remove `RegexCache` usage

**Files:**
- `src/collectors/html_profile/utils.py` (new)
- `src/collectors/html_profile/__init__.py` (updated exports)

---

### 3. YAML-Based Profile Loading (`src/collectors/html_profile/loader.py`)

**What Changed:**
- Added `load_profiles_from_yaml()` function accepting file path or dict
- Added `load_profiles_from_directory()` for batch loading from directories
- Supports multiple input formats:
  - Single profile dict: `{"domain": "...", "name": "..."}`
  - List of profiles: `[{...}, {...}]`
  - Wrapped format: `{"profiles": [...]}`
- Automatic registration with `ProfileRegistry` (optional)

**Why:**
- Enables configuration-driven profile management
- Supports loading profiles from external YAML files
- Follows OCP (Open/Closed Principle) - new profiles added via config, not code

**Rollback:**
- Construct `DomainProfile` objects directly in code
- No API changes to registry

**Files:**
- `src/collectors/html_profile/loader.py` (new)
- `src/collectors/html_profile/__init__.py` (updated exports)

---

### 4. Timing Metrics for Extraction Phases (`src/collectors/html_profile/metrics.py`)

**What Changed:**
- Added `record_phase_duration()` method for timing extraction phases
- Added `@timed_phase()` context manager for automatic timing
- Phases tracked: `list_parse`, `item_fetch`, `date_extract`, `url_normalize`
- Metrics include domain label for per-domain analysis

**Why:**
- Enables performance profiling of extraction operations
- Identifies slow phases for optimization
- Prometheus-style metrics for dashboarding

**Rollback:**
- Remove timing calls from extraction code
- No impact on extraction logic

**Files:**
- `src/collectors/html_profile/metrics.py` (enhanced)

---

## Tests Added

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `test_exceptions.py` | 6 | Exception hierarchy |
| `test_utils.py` | 8 | Regex caching |
| `test_loader.py` | 12 | YAML loading |
| Total html_profile | 78 | 100% models, registry, utils, exceptions |

---

## Quality Checks

| Check | Status |
|-------|--------|
| `uv run ruff check .` | PASS (0 errors) |
| `uv run ruff format --check` | PASS (120 files formatted) |
| `uv run mypy src/collectors/html_profile/` | PASS (10 files, no issues) |
| `uv run pytest tests/unit/test_collectors/test_html_profile/` | PASS (78 passed, 1 skipped) |

---

## Risks and Mitigations

### Risk 1: LRU Cache Memory
**Risk:** LRU cache could grow if many unique patterns are compiled.
**Mitigation:** Cache size limited to 128 patterns. Clear with `compile_regex.cache_clear()` if needed.

### Risk 2: YAML Parsing Errors
**Risk:** Malformed YAML files could cause load failures.
**Mitigation:** `load_profiles_from_directory()` catches and logs exceptions per file, continues loading others.

### Risk 3: Type Signature Change
**Risk:** `load_profiles_from_yaml()` type signature updated to include `list[dict[str, Any]]`.
**Mitigation:** Backward compatible - existing `dict` and `str`/`Path` inputs still work.

---

## Rollback Plan

If issues are discovered:

1. **Full Rollback:** Revert to P2_E2E_PASSED commit
   ```bash
   git revert HEAD
   ```

2. **Partial Rollback:** Remove specific refactoring:
   - Exceptions: Replace with `ValueError`/`RuntimeError`
   - Utils: Replace `compile_regex()` with `re.compile()`
   - Loader: Construct profiles directly in code
   - Metrics: Remove timing calls

3. **Test Rollback:**
   ```bash
   uv run pytest tests/unit/test_collectors/test_html_profile/ -v
   ```

---

## Guidance for Prompt #4 (Regression E2E)

For Prompt #4, verify:

1. **All P2 E2E scenarios still pass:**
   - Run integration tests: `uv run pytest tests/integration/test_html_list_collector.py -v`
   - Verify 10 scenarios from E2E_RUN_REPORT.md

2. **Refactored code is exercised:**
   - Exceptions are raised and caught correctly
   - Regex caching is utilized
   - Profile loading works from both dict and file sources

3. **Performance baseline:**
   - Compare extraction timing with P2 baseline
   - Verify no regression in extraction speed

4. **Update STATE.md:**
   - Change status from `P3_REFACTORED_DEPLOYED` to `P4_REGRESSION_PASSED`

---

## Sign-off

| Item | Status |
|------|--------|
| All refactoring reversible | CONFIRMED |
| All tests pass | CONFIRMED (78 passed) |
| Lint/Format/Typecheck clean | CONFIRMED |
| REFACTOR_NOTES.md created | CONFIRMED |
| STATE.md updated | PENDING (next step) |

**Refactored By:** Claude Code (P3 Automation)
**Date:** 2026-01-15
