# E2E_PLAN.md - End-to-End Validation Plan

## Prerequisites

- GitHub repository with Actions enabled
- GitHub Pages enabled (source: GitHub Actions)
- Optional secrets configured: `HF_TOKEN`, `OPENREVIEW_TOKEN`

## Test Scenarios

### Scenario 1: First Run (Clean State)

**Objective:** Verify workflow handles missing state branch gracefully.

**Steps:**
1. Ensure no `state` branch exists in the repository
2. Navigate to Actions tab in GitHub
3. Select "Daily Digest" workflow
4. Click "Run workflow" > "Run workflow" (main branch)
5. Monitor workflow execution

**Expected Results:**
- [ ] Workflow starts successfully
- [ ] "Restore state" step shows "No state branch found, starting fresh"
- [ ] Pipeline runs to completion
- [ ] Pages artifact is uploaded
- [ ] Pages deployment succeeds
- [ ] New `state` branch is created
- [ ] `state.sqlite` exists in state branch
- [ ] STATE.md shows checksums

### Scenario 2: Subsequent Run (Existing State)

**Objective:** Verify state is properly restored and updated.

**Steps:**
1. Wait for Scenario 1 to complete
2. Note the item count from first run
3. Trigger another workflow_dispatch
4. Monitor workflow execution

**Expected Results:**
- [ ] "Restore state" step shows "State restored from branch"
- [ ] Pipeline uses existing state.sqlite
- [ ] Idempotent: no duplicate items created
- [ ] State branch updated with new commit
- [ ] Pages redeployed

### Scenario 3: Failed Run (State Protection)

**Objective:** Verify failed runs do not corrupt state.

**Steps:**
1. Create a temporary invalid config (or simulate failure)
2. Trigger workflow_dispatch
3. Note the state branch commit SHA before run
4. Monitor workflow execution

**Expected Results:**
- [ ] Workflow fails at pipeline step
- [ ] "Persist state" step is skipped
- [ ] State branch commit SHA unchanged
- [ ] Pages not redeployed
- [ ] Error logged with run_id

### Scenario 4: Scheduled Run

**Objective:** Verify cron trigger works correctly.

**Steps:**
1. Wait for scheduled time (UTC 23:00)
2. Check Actions tab for automatic run

**Expected Results:**
- [ ] Workflow triggered automatically
- [ ] Same behavior as manual trigger
- [ ] Audit log includes schedule trigger info

### Scenario 5: Concurrent Run Prevention

**Objective:** Verify concurrency control serializes runs.

**Steps:**
1. Trigger workflow_dispatch
2. Immediately trigger another workflow_dispatch
3. Monitor both runs

**Expected Results:**
- [ ] Second run waits for first to complete (or queued)
- [ ] No race conditions in state branch updates
- [ ] Both runs complete successfully

## Verification Checklist

### Workflow YAML
- [ ] Triggers: schedule + workflow_dispatch
- [ ] Permissions: contents:write, pages:write, id-token:write
- [ ] Concurrency group configured
- [ ] All required steps present

### State Management
- [ ] State branch created if missing
- [ ] State restored before pipeline
- [ ] State persisted only on success
- [ ] SHA-256 checksum recorded

### Pages Deployment
- [ ] Artifact uploaded from public/
- [ ] Pages deployed successfully
- [ ] Site accessible at GitHub Pages URL

### Logging & Observability
- [ ] run_id printed once and reused
- [ ] Structured JSON logs
- [ ] No secrets in logs
- [ ] Step durations recorded

### Evidence
- [ ] E2E_RUN_REPORT.md created
- [ ] STATE.md updated with checksums
- [ ] Links to Actions run logs

## Browser Verification (Chrome DevTools)

1. Open deployed GitHub Pages site
2. Open DevTools (F12)
3. Check Console tab:
   - [ ] 0 errors
4. Check Network tab:
   - [ ] 0 failed requests
5. Verify page content displays correctly

## Evidence Capture

After successful E2E run, update:
- `features/add-github-actions-pages-and-state-branch/E2E_RUN_REPORT.md`
- `features/add-github-actions-pages-and-state-branch/STATE.md`

Include:
- Actions run URL
- Pages deployment URL
- State branch commit SHA
- Checksums for state.sqlite and public/ artifacts
