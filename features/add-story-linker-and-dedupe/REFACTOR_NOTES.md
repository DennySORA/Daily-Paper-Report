# Refactor Notes: Story Linker and Dedupe

## Feature Key: add-story-linker-and-dedupe

## Refactor Summary

This document describes the refactoring changes made in Prompt #3 to improve code quality, maintainability, and adherence to SOLID principles.

---

## Changes Made

### 1. Moved Inline Import to Top of File (story_id.py)

**Issue**: `import json` was inside the `extract_stable_id()` function.

**Fix**: Moved to top-level imports for consistency and slight performance improvement.

**Risk**: None - pure structural change.

**Rollback**: Revert `src/linker/story_id.py` import section.

---

### 2. Moved TaggedItem and CandidateGroup to models.py

**Issue**: Internal dataclasses were defined in `linker.py`, mixing data models with business logic.

**Fix**:
- Moved `TaggedItem` and `CandidateGroup` to `src/linker/models.py`
- Updated imports in `linker.py`
- Exported from `src/linker/__init__.py`

**Benefits**:
- Better separation of concerns (SRP)
- Models are now discoverable in one location
- Enables reuse in other modules

**Risk**: Low - no logic changes.

**Rollback**: Revert `models.py`, `linker.py`, and `__init__.py`.

---

### 3. Simplified _finalize_stories() Sorting Logic

**Issue**: The method had redundant double-sorting:
1. First sorted by a key function
2. Then partitioned and sorted again

**Fix**: Replaced with single-pass partition and sort:
```python
# Before: 40 lines with redundant sorting
# After: Clean partition and sort
dated = [s for s in stories if s.published_at is not None]
undated = [s for s in stories if s.published_at is None]

dated.sort(key=lambda s: (s.published_at, s.story_id), reverse=True)
undated.sort(key=lambda s: s.story_id)

return dated + undated
```

**Benefits**:
- Reduced complexity
- Clearer intent
- Slightly better performance

**Risk**: Low - logic remains the same.

**Rollback**: Revert `_finalize_stories()` method.

---

### 4. Consolidated Stable ID Extraction Logic

**Issue**: `_extract_stable_ids_from_items()` duplicated logic from `extract_arxiv_id()`, `extract_hf_model_id()`, etc.

**Fix**:
- Created `ExtractedStableIds` dataclass in `story_id.py`
- Created `extract_all_stable_ids()` function
- Removed `_extract_stable_ids_from_items()` and `_build_matched_stable_ids()` methods
- Updated `_create_story_from_group()` to use new function

**Benefits**:
- DRY principle - single source of truth for ID extraction
- `ExtractedStableIds.to_dict()` replaces `_build_matched_stable_ids()`
- Easier to add new ID types in the future

**Risk**: Medium - logic consolidation.

**Rollback**: Revert `story_id.py` and `linker.py`.

---

### 5. Added Type Aliases for Clarity

**Issue**: String types used for story IDs, entity IDs, source IDs - no type distinction.

**Fix**: Added NewType aliases in `models.py`:
```python
StoryID = NewType("StoryID", str)
EntityID = NewType("EntityID", str)
SourceID = NewType("SourceID", str)
```

**Benefits**:
- Self-documenting code
- IDE autocompletion improvements
- Future-proofing for stronger typing

**Risk**: None - purely additive.

**Rollback**: Remove type aliases from `models.py` and `__init__.py`.

---

### 6. Added Edge Case Tests

**New Tests**:
- `TestExtractAllStableIds` - 6 tests for new `extract_all_stable_ids()` function
- `TestEdgeCases` - 5 tests for edge cases:
  - Malformed URLs
  - Special characters in titles
  - Empty title normalization
  - Very long title truncation
  - Malformed raw_json handling

**Test Count**: 94 total (was 83, +11 new tests)

---

## SOLID Compliance Improvements

| Principle | Before | After |
|-----------|--------|-------|
| SRP | TaggedItem/CandidateGroup in linker.py | Moved to models.py |
| OCP | N/A | Type aliases enable extension |
| DIP | N/A | `extract_all_stable_ids()` is a pure function |
| DRY | Duplicate extraction logic | Consolidated in story_id.py |

---

## Quality Status

| Check | Result |
|-------|--------|
| Ruff lint | PASS |
| Ruff format | PASS |
| Mypy typecheck | PASS |
| Unit tests | 88 PASS |
| Integration tests | 6 PASS |
| E2E validation | ALL PASS |

---

## Rollback Plan

Each refactoring step is independent and can be rolled back:

1. **If regression in Step 4** (stable ID extraction):
   - Revert `src/linker/story_id.py`
   - Revert `src/linker/linker.py`

2. **If regression in Step 3** (sorting):
   - Revert `_finalize_stories()` method only

3. **Full rollback**:
   - `git checkout HEAD~1 -- src/linker/`

---

## Performance Impact

- **_finalize_stories()**: Reduced from O(n log n * 2) to O(n log n)
- **extract_all_stable_ids()**: Same complexity, but code reuse
- **Memory**: Negligible change

---

## Guidance for Prompt #4 (Regression E2E)

1. Run full E2E validation:
   ```bash
   uv run python tests/e2e_linker_validation.py
   ```

2. Run all tests:
   ```bash
   uv run pytest tests/unit/test_linker/ tests/integration/test_linker.py -v
   ```

3. Verify quality gates:
   ```bash
   uv run ruff check src/linker/
   uv run mypy src/linker/
   ```

4. Check for regressions in:
   - Story ID determinism
   - Primary link selection
   - Entity matching
   - State machine transitions

5. Update `STATE.md` to `READY` if all checks pass.

---

## Files Modified

| File | Change Type |
|------|-------------|
| `src/linker/story_id.py` | Import moved, new dataclass and function |
| `src/linker/models.py` | Added TaggedItem, CandidateGroup, type aliases |
| `src/linker/linker.py` | Simplified, removed redundant methods |
| `src/linker/__init__.py` | Updated exports |
| `tests/unit/test_linker/test_story_id.py` | Added 11 new tests |
| `tests/unit/test_linker/test_linker.py` | Added noqa comment |
