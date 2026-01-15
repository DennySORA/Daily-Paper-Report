# RUNBOOK_VERIFICATION.md - Deployment and Operations Guide

## Overview

This runbook describes how to deploy, verify, and operate the GitHub Actions workflow for the Daily Digest pipeline.

## Prerequisites

### Repository Settings

1. **GitHub Actions**: Must be enabled
2. **GitHub Pages**:
   - Source: "GitHub Actions"
   - Settings > Pages > Build and deployment > Source: "GitHub Actions"
3. **Secrets** (optional):
   - `HF_TOKEN`: Hugging Face API token (for authenticated requests)
   - `OPENREVIEW_TOKEN`: OpenReview API token (for authenticated requests)

### Branch Protection (recommended)

- Protect `main` branch with required reviews
- Protect `state` branch from direct pushes (workflow only)

## Deployment

### Initial Deployment

1. **Commit workflow files:**
   ```bash
   git add .github/workflows/daily-digest.yaml
   git add .github/workflows/lint-workflow.yaml
   git commit -m "feat(ci): add daily digest workflow with Pages deployment"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Navigate to Settings > Pages
   - Under "Build and deployment", select "GitHub Actions"

3. **Trigger first run:**
   - Navigate to Actions > Daily Digest
   - Click "Run workflow" > "Run workflow"

4. **Verify deployment:**
   - Check workflow completes successfully
   - Verify Pages site is accessible
   - Confirm `state` branch was created

### Subsequent Updates

1. Make changes to workflow or application code
2. Commit and push to `main`
3. Workflow runs automatically on schedule or trigger manually

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Auto | Automatically provided by Actions |
| `HF_TOKEN` | Optional | Hugging Face API token |
| `OPENREVIEW_TOKEN` | Optional | OpenReview API token |

### Schedule

- **Cron**: `0 23 * * *` (UTC)
- **Local time**: 07:00 Asia/Taipei (next day)

### Paths

| Path | Description |
|------|-------------|
| `state.sqlite` | SQLite database (in state branch) |
| `public/` | Static site output |
| `tests/fixtures/config/` | Configuration files |

## Operations

### Manual Trigger

```bash
# Via GitHub CLI
gh workflow run daily-digest.yaml

# Or via web UI
# Actions > Daily Digest > Run workflow
```

### Check Workflow Status

```bash
# List recent runs
gh run list --workflow=daily-digest.yaml

# View specific run
gh run view <run-id>

# Watch live run
gh run watch <run-id>
```

### View State Branch

```bash
# List state branch contents
git fetch origin state
git ls-tree origin/state

# Download state.sqlite
git show origin/state:state.sqlite > state.sqlite
```

### Check Pages Deployment

```bash
# Get Pages URL
gh api repos/:owner/:repo/pages --jq '.html_url'

# Check deployment status
gh api repos/:owner/:repo/pages/deployments
```

## Rollback

### Rollback State

```bash
# Find previous good commit on state branch
git log origin/state --oneline

# Reset state branch to previous commit
git push origin <commit-sha>:refs/heads/state --force
```

### Rollback Pages

1. Revert the problematic commit on `main`
2. Push revert commit
3. Trigger workflow to redeploy

### Disable Workflow

```bash
# Disable workflow
gh workflow disable daily-digest.yaml

# Re-enable
gh workflow enable daily-digest.yaml
```

## Troubleshooting

### Workflow Fails at "Restore state" Step

**Cause**: State branch corrupted or inaccessible

**Fix**:
```bash
# Delete and recreate state branch
git push origin --delete state
# Next run will create fresh state
```

### Pages Deployment Fails

**Cause**: Pages not configured correctly

**Fix**:
1. Check Settings > Pages is set to "GitHub Actions"
2. Verify permissions in workflow YAML
3. Check artifact upload step succeeded

### State Not Persisting

**Cause**: Pipeline failing before success state

**Fix**:
1. Check pipeline logs for errors
2. Fix underlying issue
3. State persists only on RUN_FINISHED_SUCCESS

### Concurrent Run Issues

**Cause**: Concurrency control not working

**Fix**:
1. Verify concurrency group in workflow
2. Check `cancel-in-progress: false`
3. Manually cancel stuck runs if needed

## Monitoring

### Key Metrics

- `workflow_success_total`: Successful workflow runs
- `workflow_failure_total`: Failed workflow runs
- `workflow_duration_ms`: Total workflow duration

### Log Queries

```bash
# Find runs with errors
gh run list --workflow=daily-digest.yaml --status=failure

# Get logs from failed run
gh run view <run-id> --log-failed
```

## Maintenance

### State Branch Cleanup

Per requirements, state branch history is retained for 90 days. To clean older history:

```bash
# Only with explicit operator action
# This squashes history older than 90 days
git checkout state
git rebase -i HEAD~<commits-to-keep>
git push origin state --force
```

### Updating Secrets

```bash
# Update secret via CLI
gh secret set HF_TOKEN --body "<token>"
gh secret set OPENREVIEW_TOKEN --body "<token>"
```

## Emergency Contacts

- Repository maintainer: Check CODEOWNERS file
- GitHub Status: https://www.githubstatus.com/
