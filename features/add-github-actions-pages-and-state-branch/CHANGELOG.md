# CHANGELOG.md - Feature Change Summary

## [Unreleased] - add-github-actions-pages-and-state-branch

### Added

#### GitHub Actions Workflow
- **Daily Digest Workflow** (`.github/workflows/daily-digest.yaml`)
  - Scheduled trigger: UTC 23:00 (Asia/Taipei 07:00)
  - Manual trigger: `workflow_dispatch`
  - Full pipeline execution with state persistence
  - GitHub Pages deployment from `public/` directory

- **Workflow Linting CI** (`.github/workflows/lint-workflow.yaml`)
  - Validates workflow YAML syntax with actionlint
  - Runs on pull requests and pushes

#### State Management
- **State Branch Persistence**
  - Dedicated `state` orphan branch for `state.sqlite`
  - Best-effort restore at start of each run
  - Guarded commit: only on RUN_FINISHED_SUCCESS
  - 90-day history retention

#### Pages Deployment
- **Static Site Deployment**
  - Uploads `public/` as Pages artifact
  - Uses official `actions/deploy-pages` action
  - OIDC authentication for deployment

#### Security & Observability
- **Least Privilege Permissions**
  - `contents:write` for state branch only
  - `pages:write` for deployment
  - `id-token:write` for OIDC

- **Concurrency Control**
  - Single concurrency group prevents overlapping runs
  - `cancel-in-progress: false` serializes runs

- **Audit Logging**
  - run_id included in all step outputs
  - Commit SHA and checksums recorded
  - Structured JSON logs with component/step/duration

- **Secrets Handling**
  - Optional `HF_TOKEN` and `OPENREVIEW_TOKEN`
  - Environment variable only (no inline secrets)
  - No `set -x` to prevent log exposure

#### Testing
- **Workflow Validation Tests**
  - actionlint integration in CI
  - Permission verification tests

#### Documentation
- `STATE.md`: Feature state tracking
- `E2E_PLAN.md`: End-to-end test plan
- `ACCEPTANCE.md`: Acceptance criteria checklist
- `RUNBOOK_VERIFICATION.md`: Operations guide
- `CHANGELOG.md`: This file

### Technical Details

| Component | Implementation |
|-----------|----------------|
| Workflow engine | GitHub Actions |
| Python runtime | 3.13 via uv |
| State storage | SQLite on `state` branch |
| Pages source | `public/` directory |
| Concurrency | Single group, serialized |

### Migration Notes

- No breaking changes
- First run creates `state` branch automatically
- Existing local state.sqlite is not affected

### Dependencies

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/upload-pages-artifact@v3`
- `actions/deploy-pages@v4`
- `astral-sh/setup-uv@v5`

### Known Limitations

1. State branch must be managed via workflow only
2. Manual state modifications require force push
3. Concurrent runs are serialized (may queue)
