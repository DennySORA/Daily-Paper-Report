# RUNBOOK_VERIFICATION.md - add-platform-release-collectors

## Deployment to Verification Environment

### Prerequisites
1. Python 3.13+ installed
2. uv package manager installed
3. Git repository cloned

### Configuration

#### Environment Variables (Required for Live API Calls)
```bash
# GitHub API token (for github_releases sources)
export GITHUB_TOKEN="ghp_..."

# HuggingFace API token (optional, for rate-limited orgs)
export HF_TOKEN="hf_..."

# OpenReview API token (if required by venue policy)
export OPENREVIEW_TOKEN="..."
```

#### Source Configuration
Add platform sources to `sources.yaml`:
```yaml
sources:
  - id: github-meta-llama
    name: "Meta Llama GitHub Releases"
    url: "https://github.com/meta-llama/llama"
    tier: 0
    method: github_releases
    kind: release
    max_items: 50

  - id: hf-meta-llama
    name: "Meta Llama HuggingFace Models"
    url: "https://huggingface.co/meta-llama"
    tier: 0
    method: hf_org
    kind: model
    max_items: 100

  - id: openreview-iclr2025
    name: "ICLR 2025 Submissions"
    url: "https://openreview.net/group?id=ICLR.cc/2025/Conference"
    tier: 1
    method: openreview_venue
    kind: paper
    query: "ICLR.cc/2025/Conference/-/Blind_Submission"
    max_items: 100
```

### Deployment Steps

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Run linting checks**
   ```bash
   uv run ruff check .
   uv run ruff format --check .
   ```

3. **Run type checking**
   ```bash
   uv run mypy .
   ```

4. **Run tests**
   ```bash
   uv run pytest
   ```

5. **Run the digest command (if implemented)**
   ```bash
   uv run digest run --config sources.yaml --state state.sqlite --out public/
   ```

### Rollback Procedure

1. **Revert source code changes**
   ```bash
   git checkout HEAD~1 -- src/collectors/platform/
   ```

2. **Restore database (if needed)**
   ```bash
   cp state.sqlite.backup state.sqlite
   ```

3. **Re-run tests to verify rollback**
   ```bash
   uv run pytest
   ```

### Verification Checklist

- [ ] All tests pass
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Platform collectors produce items
- [ ] Canonical URLs are correct
- [ ] No secrets in logs or raw_json
- [ ] Rate limiting works as expected

### Version/Commit Information
- Commit: (to be filled after implementation)
- Branch: main
- Date: (to be filled)

### Config Differences from Production
- This is INT (verification) environment
- Uses test fixtures for fixture-backed tests
- Live API calls require valid tokens
