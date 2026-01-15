# E2E_PLAN.md - add-platform-release-collectors

## Browser-Executable End-to-End Checklist

### Prerequisites
1. Clone repository and checkout feature branch
2. Install dependencies: `uv sync`
3. Ensure environment variables are set (or use fixture mocking):
   - GITHUB_TOKEN (optional for fixture-backed tests)
   - HF_TOKEN (optional for fixture-backed tests)
   - OPENREVIEW_TOKEN (optional for fixture-backed tests)

### Test Environment Setup
1. Clear SQLite database: `rm -f state.sqlite`
2. Clear prior evidence: `rm -f features/add-platform-release-collectors/E2E_RUN_REPORT.md`
3. Verify clean state: `ls -la *.sqlite` should show no files

### Test Execution Steps

#### Step 1: Run Unit Tests
```bash
uv run pytest tests/unit/test_collectors/test_platform/ -v
```
Expected: All tests pass

#### Step 2: Run Integration Tests
```bash
uv run pytest tests/integration/test_platform_collectors.py -v
```
Expected: All tests pass

#### Step 3: Run Fixture-Based Collection (First Run)
```bash
uv run python -c "
from src.collectors.platform import GitHubReleasesCollector, HuggingFaceOrgCollector, OpenReviewVenueCollector
# Test with fixtures
print('Collectors imported successfully')
"
```
Expected: No import errors

#### Step 4: Verify Deduplication (Second Run)
- Run the same collection again
- Verify items have same first_seen_at
- Verify no duplicate URLs in items table

#### Step 5: Verify Auth Error Handling
```bash
# Simulate 401 by using invalid token
GITHUB_TOKEN=invalid_token uv run pytest tests/integration/test_platform_collectors.py::test_github_auth_failure -v
```
Expected: Source marked as failed with remediation hint

#### Step 6: Verify Rate Limiting
```bash
uv run pytest tests/integration/test_platform_collectors.py::test_rate_limiting -v
```
Expected: Token bucket enforces max QPS

### Validation Checks

#### Check 1: Canonical URL Format
- GitHub: `https://github.com/{owner}/{repo}/releases/tag/{tag}`
- HuggingFace: `https://huggingface.co/{model_id}`
- OpenReview: `https://openreview.net/forum?id={forum_id}`

#### Check 2: Stable ID Extraction
- GitHub: Release ID from API response
- HuggingFace: model_id from API response
- OpenReview: forum/note id from API response

#### Check 3: Content Hash Stability
- Same input produces same content_hash
- Different input (e.g., updated release notes) produces different content_hash

#### Check 4: No Secrets in raw_json
- Verify raw_json does not contain tokens
- Verify logs do not contain tokens

### Evidence Collection
1. Run full test suite: `uv run pytest --tb=short`
2. Capture test output to E2E_RUN_REPORT.md
3. Update STATE.md with platform summary
4. Commit evidence files

### Success Criteria
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Canonical URLs are correctly formatted
- [ ] Stable IDs are extracted
- [ ] Deduplication works (no duplicates on second run)
- [ ] Auth errors produce remediation hints
- [ ] Rate limiting is enforced
- [ ] No secrets in output
