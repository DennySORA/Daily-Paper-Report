STATUS: READY

# STATE.md - add-platform-release-collectors

## Feature Key
`add-platform-release-collectors`

## STATUS
`READY`

## Overview
Platform collectors for GitHub releases, Hugging Face org updates, and OpenReview venue monitoring.

## Decisions Made

### Architecture
1. **Token-bucket rate limiter**: Per-platform QPS control with thread-safe implementation
2. **Collector pattern**: Following existing `ArxivApiCollector` pattern from `src/collectors/arxiv/api.py`
3. **Authentication**: Environment variables (GITHUB_TOKEN, HF_TOKEN, OPENREVIEW_TOKEN)
4. **Error handling**: 401/403 marked as source failure with remediation hints

### Platform-Specific Design

#### GitHub Releases
- API: `GET /repos/{owner}/{repo}/releases`
- Canonical URL: Release HTML URL (`https://github.com/{owner}/{repo}/releases/tag/{tag}`)
- Stable ID: Release ID or URL
- Content hash: Based on title, tag_name, body (release notes), updated_at

#### Hugging Face Org
- API: `GET https://huggingface.co/api/models?author={org}`
- Canonical URL: Model page URL (`https://huggingface.co/{model_id}`)
- Stable ID: model_id
- Content hash: Based on model_id, lastModified, pipeline_tag

#### OpenReview Venue
- API: `GET https://api2.openreview.net/notes?invitation={venue_id}`
- Canonical URL: Forum URL (`https://openreview.net/forum?id={forum_id}`)
- Stable ID: forum/note id
- Content hash: Based on title, mdate (last modified)

## Completed Items
- [x] Explored existing codebase patterns
- [x] Designed platform collectors architecture
- [x] Created feature directory structure
- [x] Implement token-bucket rate limiter
- [x] Implement platform metrics
- [x] Implement platform constants
- [x] Implement GitHub releases collector
- [x] Implement HuggingFace org collector
- [x] Implement OpenReview venue collector
- [x] Update collector runner to include platform collectors
- [x] Write unit tests (53 tests)
- [x] Write integration tests (8 tests)
- [x] Run linting (ruff check: clean)
- [x] Run type-checking (mypy: clean)
- [x] Run tests (61 passed)

## Test Summary (Post-Refactor)
- **Unit tests**: 82 passed
- **Integration tests**: 5 passed
- **Total**: 87 passed
- **Linting**: Clean (ruff check)
- **Type checking**: Clean (mypy)
- **New helper tests**: 26 added

## Refactoring Summary (2026-01-15)
- Created `helpers.py` with shared utility functions
- Extracted `is_auth_error()`, `get_auth_token()`, `extract_nested_value()`, `build_pdf_url()`, `truncate_text()`
- Reduced OpenReview `_build_raw_data` complexity from 12 to ~7
- Removed duplicated HTTP status constants across collectors
- Added 26 new tests for helper functions
- See `REFACTOR_NOTES.md` for full details

## E2E Verification Summary (2026-01-15)
- **All 10 E2E steps passed**
- **All 3 acceptance criteria verified**
- **E2E_RUN_REPORT.md generated**

## Risks
1. **API changes**: Platform APIs may change; mitigated by using stable API versions
2. **Rate limiting**: Platforms may throttle; mitigated by token-bucket rate limiter
3. **Authentication**: Tokens may be missing; mitigated by clear error messages

## Validation in Verification Environment
1. Run collectors with fixture data
2. Verify canonical URLs are correct
3. Verify no duplicates after two identical runs
4. Verify 401/403 handling with remediation hints
5. Verify rate limiting behavior

## Per-Platform Summary (E2E Verified)

| Platform | Default QPS | Canonical URL Format | Stable ID | Auth Hint |
|----------|-------------|---------------------|-----------|-----------|
| github   | 5.0 / 15.0  | `{owner}/{repo}/releases/tag/{tag}` | release_id | GITHUB_TOKEN |
| huggingface | 10.0     | `{model_id}` | model_id | HF_TOKEN |
| openreview | 5.0       | `forum?id={forum_id}` | forum_id | OPENREVIEW_TOKEN |

## Artifacts
- Source: `src/collectors/platform/`
- Tests: `tests/unit/test_collectors/test_platform/`
- Integration tests: `tests/integration/test_platform_collectors.py`
