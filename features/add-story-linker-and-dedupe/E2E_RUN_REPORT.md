# E2E Run Report: Story Linker and Dedupe

## Run Metadata

| Field | Value |
|-------|-------|
| Feature Key | add-story-linker-and-dedupe |
| Run Date | 2026-01-15 |
| Run ID | e2e-validation-20260115 |
| Git Commit | uncommitted (new feature files) |
| Python Version | 3.13 |
| Test Environment | Local development |

---

## Test Summary

| Test Suite | Result | Count |
|------------|--------|-------|
| Unit Tests (test_linker/) | PASS | 77 |
| Integration Tests (test_linker.py) | PASS | 6 |
| E2E Validation Script | PASS | 6/6 |
| **Total Tests** | **PASS** | **83** |

---

## Acceptance Criteria Results

### AC1: Same arXiv ID Produces Single Story

**Status**: PASS

**Evidence**:
```
=== AC1: Same arXiv ID Produces Single Story ===
  PASS: stories_out == 1
  PASS: story_id == 'arxiv:2401.12345'
  PASS: item_count == 3
  PASS: merges_total == 1
```

**Test Details**:
- Created 3 items with arXiv ID `2401.12345` from sources: arxiv-cs-ai, arxiv-cs-lg, arxiv-api
- Linker merged all 3 into a single Story
- Story ID correctly generated as `arxiv:2401.12345`

---

### AC2: Story Ordering is Stable and Deterministic

**Status**: PASS

**Evidence**:
```
=== AC2: Story Ordering is Deterministic ===
  PASS: stories_out identical (4)
  PASS: story_ids identical
  PASS: primary_links identical
  PASS: story content checksums identical (fc5ab1708701fbfb...)
```

**Test Details**:
- Ran linker twice with identical inputs (4 items from different platforms)
- Story IDs, ordering, and primary links are byte-identical
- Story content checksums match exactly

---

### AC3: Persistence and Evidence

**Status**: PASS

**Evidence**:
```
=== AC3: Persistence and Evidence ===
  PASS: daily.json exists at /tmp/linker-e2e-test/api/daily.json
  PASS: daily.json has correct schema (2 stories)
  PASS: STATE.md exists
  PASS: STATE.md contains status
  PASS: SHA-256 checksum valid (70f0c567c8b93c02...)
```

**Test Details**:
- daily.json created with version 1.0 schema
- STATE.md created with P1_DONE_DEPLOYED status
- SHA-256 checksum included for integrity verification

---

## Additional Verification Results

### Entity Matching

**Status**: PASS

```
=== Entity Matching ===
  PASS: OpenAI entity matched to 1 story
  PASS: Anthropic entity matched to 1 story
```

### State Machine

**Status**: PASS

```
=== State Machine ===
  PASS: Linker reaches STORIES_FINAL state
  PASS: Invalid transition raises LinkerStateTransitionError
```

### Duplicate Link Collapse

**Status**: PASS

```
=== Duplicate Link Collapse ===
  PASS: 1 story from 3 duplicate items
  PASS: 1 link after deduplication
```

---

## Quality Gate Results

| Gate | Command | Result |
|------|---------|--------|
| Ruff Lint | `uv run ruff check src/linker/` | All checks passed! |
| Ruff Format | `uv run ruff format --check src/linker/` | 9 files already formatted |
| Mypy Type Check | `uv run mypy src/linker/` | Success: no issues found in 9 source files |
| Pytest | `uv run pytest tests/unit/test_linker/ tests/integration/test_linker.py -v` | 83 passed |

---

## Sample Merge Rationale

Example merge rationale from AC1 test:

```json
{
  "merged_item_urls": [
    "https://arxiv.org/abs/2401.12345",
    "https://arxiv.org/abs/2401.12345",
    "https://arxiv.org/abs/2401.12345"
  ],
  "stable_id": "arxiv:2401.12345",
  "stable_id_type": "arxiv",
  "matched_entity_ids": [],
  "merge_reason": "Same arXiv ID from multiple sources"
}
```

---

## Files Verified

| File | Exists | Valid |
|------|--------|-------|
| `src/linker/__init__.py` | Yes | Exports all public API |
| `src/linker/models.py` | Yes | Story, StoryLink, MergeRationale, LinkerResult |
| `src/linker/state_machine.py` | Yes | LinkerState, LinkerStateMachine |
| `src/linker/story_id.py` | Yes | Deterministic ID generation |
| `src/linker/entity_matcher.py` | Yes | Entity keyword matching |
| `src/linker/linker.py` | Yes | StoryLinker class |
| `src/linker/persistence.py` | Yes | daily.json and STATE.md writing |
| `src/linker/constants.py` | Yes | Patterns and defaults |
| `src/linker/metrics.py` | Yes | Prometheus metrics |
| `tests/unit/test_linker/` | Yes | 4 test modules |
| `tests/integration/test_linker.py` | Yes | Integration tests |
| `tests/e2e_linker_validation.py` | Yes | E2E validation script |

---

## Conclusion

**ALL ACCEPTANCE CRITERIA PASSED**

The Story Linker feature has been verified to meet all acceptance criteria:

1. Same arXiv ID correctly produces a single Story with merged links
2. Story ordering is deterministic and stable across runs
3. Persistence to daily.json and STATE.md works correctly with evidence

The feature is ready for production deployment.

---

## Prompt #4 Regression E2E Results (Post-Refactor)

### Regression Scope

Verified the following refactored areas for regressions:

| Refactored Area | Test Result |
|-----------------|-------------|
| `story_id.py` - New `ExtractedStableIds` dataclass | PASS |
| `story_id.py` - New `extract_all_stable_ids()` function | PASS (11 edge case tests) |
| `models.py` - Moved `TaggedItem` and `CandidateGroup` | PASS |
| `models.py` - New type aliases (`StoryID`, `EntityID`, `SourceID`) | PASS |
| `linker.py` - Simplified `_finalize_stories()` sorting | PASS |
| `linker.py` - Uses `extract_all_stable_ids()` | PASS |

### Test Results

| Test Suite | Result | Count |
|------------|--------|-------|
| Unit Tests (test_linker/) | PASS | 88 |
| Integration Tests (test_linker.py) | PASS | 6 |
| E2E Validation Script | PASS | 6/6 |
| Edge Case Tests (new) | PASS | 11 |
| **Total Tests** | **PASS** | **94** |

### Quality Gates

```
uv run ruff check src/linker/        -> All checks passed!
uv run ruff format --check src/linker/ -> 9 files already formatted
uv run mypy src/linker/              -> Success: no issues found in 9 source files
uv run python tests/e2e_linker_validation.py -> ALL ACCEPTANCE CRITERIA PASSED
```

### Regression Verification

- **Story ID Determinism**: PASS - Story IDs are identical across runs
- **Primary Link Selection**: PASS - Primary links follow precedence rules
- **Entity Matching**: PASS - Entities correctly matched to stories
- **State Machine**: PASS - All transitions work correctly
- **Duplicate Link Collapse**: PASS - Links correctly deduplicated
- **Persistence**: PASS - daily.json and STATE.md written correctly

### No Regressions Found

All refactored code paths work correctly. The refactoring improved code quality without introducing any regressions.

---

## Sign-off

- **Verified By**: Claude Code (Regression E2E Validation)
- **Date**: 2026-01-15
- **Prompt**: #4 (Regression E2E)
- **Status**: READY
