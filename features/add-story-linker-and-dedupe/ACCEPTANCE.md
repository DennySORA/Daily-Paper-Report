# Acceptance Criteria Checklist: Story Linker and Dedupe

## Feature Key: add-story-linker-and-dedupe

---

## Acceptance Criteria

### AC1: Same arXiv ID Produces Single Story
- [x] **Criterion**: On INT, fixtures with the same arXiv id across multiple sources result in exactly one Story and a single primary_link selected per precedence rules.
- **Test Method**: Create 3 items with same arXiv ID from different sources (arxiv-rss, arxiv-api, arxiv-cs-ai)
- **Expected Result**: `stories_out == 1`, `merges_total == 1`
- **Verification**:
  ```python
  result = linker.link_items(items_with_same_arxiv_id)
  assert result.stories_out == 1
  assert result.stories[0].story_id == "arxiv:2401.12345"
  ```

### AC2: Story Ordering is Stable and Deterministic
- [x] **Criterion**: On INT, Story ordering is stable and deterministic between two identical runs (byte-identical daily.json).
- **Test Method**: Run linker twice with identical inputs, compare JSON output
- **Expected Result**: Byte-identical daily.json files
- **Verification**:
  ```python
  import hashlib

  json1 = write_daily_json(result1.stories, ...)
  json2 = write_daily_json(result2.stories, ...)

  hash1 = hashlib.sha256(json1.read_bytes()).hexdigest()
  hash2 = hashlib.sha256(json2.read_bytes()).hexdigest()
  assert hash1 == hash2
  ```

### AC3: INT Clear-Data E2E Passes
- [x] **Criterion**: INT clear-data E2E passes and archives evidence to features/add-story-linker-and-dedupe/E2E_RUN_REPORT.md and features/add-story-linker-and-dedupe/STATE.md.
- **Test Method**: Clear DB, run pipeline on fixtures with intentional duplicates
- **Expected Result**:
  - All tests pass
  - E2E_RUN_REPORT.md contains run summary
  - STATE.md contains merge statistics
- **Verification**:
  ```bash
  # Clear state
  rm -f state.sqlite

  # Run tests
  uv run pytest tests/ -v

  # Verify evidence files exist
  ls features/add-story-linker-and-dedupe/E2E_RUN_REPORT.md
  ls features/add-story-linker-and-dedupe/STATE.md
  ```

---

## Requirement Coverage

| Requirement | Status | Test Coverage |
|-------------|--------|---------------|
| Story objects with story_id, primary_link, links, entities | Implemented | test_linker.py |
| Deterministic story_id from stable identifiers | Implemented | test_story_id.py |
| Primary link follows prefer_primary_link_order | Implemented | test_linker.py |
| State machine ITEMS_READY -> STORIES_FINAL | Implemented | test_state_machine.py |
| Idempotency: identical inputs = identical outputs | Implemented | test_linker.py::test_idempotency |
| No duplicate links (same type + URL) | Implemented | test_linker.py::TestDedupeLinks |
| Pure function API for testability | Implemented | test_linker.py::TestLinkItemsPure |
| Audit logs capture merge rationale | Implemented | MergeRationale dataclass |
| Allowlisted link types | Implemented | constants.py |
| Persist to daily.json | Implemented | persistence.py |
| Persist to STATE.md | Implemented | persistence.py |
| SHA-256 checksum | Implemented | persistence.py |
| Unit tests for story_id determinism | Implemented | test_story_id.py |
| Unit tests for primary link precedence | Implemented | test_linker.py |
| Unit tests for duplicate link collapse | Implemented | test_linker.py |
| Unit tests for entity keyword matching | Implemented | test_entity_matcher.py |
| Integration tests for fixture Items | Implemented | test_linker.py (integration) |

---

## Sign-off

- [x] All acceptance criteria verified
- [x] All tests pass
- [x] Documentation updated
- [x] Evidence captured

**Verified By**: Claude Code (E2E Validation)
**Date**: 2026-01-15
