# Story Linker State

## Status

- FEATURE_KEY: add-story-linker-and-dedupe
- STATUS: READY

## Overview

The Story Linker feature merges duplicate items from multiple sources (arXiv, GitHub, HuggingFace, official blogs, etc.) into unified Story objects with deterministic story_id generation, primary link selection, and entity matching.

## Implementation Summary

### Modules Created

1. **`src/linker/models.py`**: Data models
   - `Story`: Main Story object with story_id, primary_link, links, entities
   - `StoryLink`: Typed link within a Story
   - `MergeRationale`: Audit record for merge decisions
   - `LinkerResult`: Result of linking operation with statistics

2. **`src/linker/state_machine.py`**: State machine
   - `LinkerState`: ITEMS_READY -> ENTITY_TAGGED -> CANDIDATE_GROUPED -> STORIES_MERGED -> STORIES_FINAL
   - `LinkerStateMachine`: Enforces valid transitions

3. **`src/linker/story_id.py`**: Deterministic ID generation
   - Priority: arXiv ID > GitHub release > HF model > fallback hash
   - Fallback uses normalized(title) + entity_id + date_bucket

4. **`src/linker/entity_matcher.py`**: Entity keyword matching
   - Matches items to entities based on keywords in title/abstract
   - Supports aliases and word boundary matching

5. **`src/linker/linker.py`**: Core linking logic
   - `StoryLinker`: Main class with state machine integration
   - `link_items_pure`: Pure function API for testing

6. **`src/linker/persistence.py`**: Snapshot persistence
   - Writes to `public/api/daily.json` with atomic semantics
   - Writes STATE.md with merge statistics

### Design Decisions

1. **Story ID Strategy**: Deterministic based on stable identifiers (arXiv ID, GitHub release URL, HF model ID) to ensure idempotency across runs.

2. **Primary Link Selection**: Follows `prefer_primary_link_order` from topics.yaml with tier as tiebreaker.

3. **Dedupe Rules**: Links with same type and canonical URL are collapsed; no Story contains duplicate links.

4. **State Machine**: Enforces linear progression through linking phases to prevent illegal state transitions.

5. **Audit Logging**: Every merge records rationale including matched entity IDs, stable IDs, and fallback heuristics used.

## Completed Items

- [x] Story data models (Story, StoryLink, MergeRationale)
- [x] Linker state machine with transition validation
- [x] Deterministic story_id generation
- [x] Entity keyword matching
- [x] Primary link selection with precedence rules
- [x] Duplicate link collapse
- [x] Persistence to daily.json
- [x] STATE.md writing
- [x] Unit tests for all components
- [x] Integration tests with fixture items

## TODOs for Future Prompts

- [x] E2E testing with actual database (Prompt #2) - COMPLETED 2026-01-15
- [ ] Performance optimization for large item sets
- [ ] Metrics collection integration
- [ ] Tracing span integration

## Risks

1. **Title-based fallback**: Fallback grouping using normalized title may create false positives for generic titles.
   - Mitigation: Combine with entity_id and date_bucket for uniqueness.

2. **Entity keyword ambiguity**: Short keywords may match unintended content.
   - Mitigation: Word boundary matching prevents partial matches.

## Validation in Verification Environment

1. Run tests: `uv run pytest tests/unit/test_linker/ tests/integration/test_linker.py -v`
2. Verify story_id determinism with identical inputs
3. Verify primary link follows precedence rules
4. Verify STATE.md is created with correct format

## Verification Results (Prompt #1)

```
uv run ruff check src/linker/      -> All checks passed!
uv run ruff format --check src/linker/  -> 9 files already formatted
uv run mypy src/linker/            -> Success: no issues found in 9 source files
uv run pytest tests/unit/test_linker/ tests/integration/test_linker.py -v -> 83 passed
```

## Deployment Status

- Environment: Local development (verification)
- Git Commit: Uncommitted (new files)
- All quality gates pass:
  - Ruff lint: PASS
  - Ruff format: PASS
  - Mypy type check: PASS
  - Unit tests: 77 PASS
  - Integration tests: 6 PASS

## E2E Validation Results (Prompt #2)

```
============================================================
Story Linker E2E Validation
============================================================
=== AC1: Same arXiv ID Produces Single Story ===
  PASS: stories_out == 1
  PASS: story_id == 'arxiv:2401.12345'
  PASS: item_count == 3
  PASS: merges_total == 1

=== AC2: Story Ordering is Deterministic ===
  PASS: stories_out identical (4)
  PASS: story_ids identical
  PASS: primary_links identical
  PASS: story content checksums identical

=== AC3: Persistence and Evidence ===
  PASS: daily.json exists
  PASS: daily.json has correct schema (2 stories)
  PASS: STATE.md exists
  PASS: STATE.md contains status
  PASS: SHA-256 checksum valid

=== Entity Matching ===
  PASS: OpenAI entity matched to 1 story
  PASS: Anthropic entity matched to 1 story

=== State Machine ===
  PASS: Linker reaches STORIES_FINAL state
  PASS: Invalid transition raises LinkerStateTransitionError

=== Duplicate Link Collapse ===
  PASS: 1 story from 3 duplicate items
  PASS: 1 link after deduplication

============================================================
SUMMARY
============================================================
  PASS: AC1: Same arXiv ID = Single Story
  PASS: AC2: Deterministic Ordering
  PASS: AC3: Persistence and Evidence
  PASS: Entity Matching
  PASS: State Machine
  PASS: Duplicate Link Collapse

ALL ACCEPTANCE CRITERIA PASSED
```

## Refactoring Results (Prompt #3)

### Changes Made

1. **Moved inline import to top of file** (story_id.py)
   - `import json` moved from inside function to module level

2. **Moved TaggedItem/CandidateGroup to models.py**
   - Better separation of concerns (SRP)
   - Models are now discoverable in one location

3. **Simplified _finalize_stories() sorting logic**
   - Reduced from double-sorting to single-pass partition and sort
   - Clearer intent, slightly better performance

4. **Consolidated stable ID extraction logic**
   - Created `ExtractedStableIds` dataclass
   - Created `extract_all_stable_ids()` function
   - Removed duplicate code in linker.py

5. **Added type aliases for clarity**
   - `StoryID`, `EntityID`, `SourceID` NewType aliases
   - Self-documenting code

6. **Added edge case tests**
   - 11 new tests for edge cases and new functionality
   - Total tests: 94 (was 83)

### Quality Gates

```
uv run ruff check src/linker/      -> All checks passed!
uv run mypy src/linker/            -> Success: no issues found in 9 source files
uv run pytest tests/unit/test_linker/ tests/integration/test_linker.py -> 94 passed
uv run python tests/e2e_linker_validation.py -> ALL ACCEPTANCE CRITERIA PASSED
```

### Rollback Plan

Each step is independent and can be rolled back by reverting the specific file:
- Full rollback: `git checkout HEAD~1 -- src/linker/`

See `REFACTOR_NOTES.md` for detailed rollback instructions.

## Regression E2E Results (Prompt #4)

### Verification Summary

| Check | Result |
|-------|--------|
| Ruff lint | PASS |
| Ruff format | PASS |
| Mypy type check | PASS |
| E2E validation script | ALL 6 CRITERIA PASSED |
| Unit tests | 88 passed |
| Integration tests | 6 passed |
| Edge case tests | 11 passed |
| **Total** | **94 tests passed** |

### Refactored Areas Verified

- `story_id.py` - New `ExtractedStableIds` dataclass: PASS
- `story_id.py` - New `extract_all_stable_ids()` function: PASS
- `models.py` - Moved `TaggedItem` and `CandidateGroup`: PASS
- `models.py` - New type aliases: PASS
- `linker.py` - Simplified `_finalize_stories()` sorting: PASS
- `linker.py` - Uses `extract_all_stable_ids()`: PASS

### No Regressions Found

All refactored code paths work correctly. The feature is ready for production.

## Last Updated

- Prompt: #4
- Date: 2026-01-15
- STATUS: READY
