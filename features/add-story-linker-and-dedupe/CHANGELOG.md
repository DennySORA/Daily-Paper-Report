# Changelog: Story Linker and Dedupe

## Feature Key: add-story-linker-and-dedupe

---

## [Unreleased]

### Added

- **Story Linker Module** (`src/linker/`)
  - Core linking functionality for cross-source deduplication
  - Merges items from arXiv, GitHub, HuggingFace, and official sources into unified Stories

- **Data Models** (`src/linker/models.py`)
  - `Story`: Unified story object with story_id, primary_link, links, entities
  - `StoryLink`: Typed link with URL, link_type, source_id, tier
  - `StorySection`: Enum for display sections (top5, model_releases, papers, radar)
  - `MergeRationale`: Audit record for merge decisions
  - `LinkerResult`: Result container with statistics

- **State Machine** (`src/linker/state_machine.py`)
  - `LinkerState`: Enum with states ITEMS_READY -> ENTITY_TAGGED -> CANDIDATE_GROUPED -> STORIES_MERGED -> STORIES_FINAL
  - `LinkerStateMachine`: Enforces valid state transitions
  - `LinkerStateTransitionError`: Exception for illegal transitions

- **Story ID Generation** (`src/linker/story_id.py`)
  - Deterministic ID generation from stable identifiers
  - Priority: arXiv ID > GitHub release > HF model > fallback hash
  - Extractors for arXiv, HuggingFace, GitHub, ModelScope URLs
  - Title normalization for fallback IDs

- **Entity Matching** (`src/linker/entity_matcher.py`)
  - Keyword-based entity matching in title and abstract
  - Alias support
  - Word boundary matching to prevent false positives

- **Constants** (`src/linker/constants.py`)
  - URL patterns for stable ID extraction
  - Allowlisted link types for primary link selection
  - Default primary link order

- **Metrics** (`src/linker/metrics.py`)
  - `LinkerMetrics`: Tracks items_in, stories_out, merges_total, fallback_merges
  - Singleton pattern for global metrics

- **Persistence** (`src/linker/persistence.py`)
  - `write_daily_json`: Atomic write to public/api/daily.json
  - `write_linker_state_md`: Write STATE.md with statistics
  - `LinkerPersistence`: Combined persistence handler
  - SHA-256 checksum computation

- **Unit Tests** (`tests/unit/test_linker/`)
  - `test_story_id.py`: Story ID extraction and generation tests
  - `test_state_machine.py`: State machine transition tests
  - `test_linker.py`: Core linker functionality tests
  - `test_entity_matcher.py`: Entity matching tests

- **Integration Tests** (`tests/integration/test_linker.py`)
  - End-to-end linking with duplicates
  - Entity matching integration
  - Primary link selection verification
  - Persistence workflow tests

### Technical Details

- **Idempotency**: Same inputs produce identical outputs (story_id, ordering, primary_link)
- **Determinism**: Story IDs are derived from stable identifiers, not random values
- **Dedupe Rules**: No Story contains duplicate links (same type + URL)
- **Primary Link Selection**: Follows topics.yaml `prefer_primary_link_order` with tier as tiebreaker

---

## Reviewer Notes

1. The linker is designed as a pure transformation layer between Items and Stories
2. State machine prevents skipping phases and ensures consistent processing
3. All merge decisions are recorded in `MergeRationale` for auditability
4. The module is fully testable via `link_items_pure` function

---

## Migration Notes

None - this is a new feature with no breaking changes to existing code.
