# RUNBOOK_VERIFICATION.md - add-yaml-config-contracts

## Deployment Guide for Verification Environment

### Prerequisites

1. Python 3.13+
2. `uv` package manager
3. Git repository cloned

### Installation

```bash
# Navigate to repository
cd /path/to/repo

# Sync dependencies
uv sync
```

### Configuration Files

The following configuration files are required:

1. **sources.yaml** - Source definitions
2. **entities.yaml** - Entity definitions
3. **topics.yaml** - Topic and scoring definitions

### Environment Variables

The following environment variables may be required (optional for config validation):

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_TOKEN` | Hugging Face API token | No |
| `GITHUB_TOKEN` | GitHub API token | No |
| `OPENREVIEW_TOKEN` | OpenReview API token | No |

**Note**: These tokens are NOT stored in YAML files. They are only used at runtime for API calls.

### Running the Application

```bash
# Basic run with all required arguments
uv run python -m src.cli.digest run \
  --config sources.yaml \
  --entities entities.yaml \
  --topics topics.yaml \
  --state state.db \
  --out ./public \
  --tz Asia/Taipei
```

### Verifying Deployment

1. **Check Exit Code**:
   ```bash
   echo $?  # Should be 0 for success
   ```

2. **Check Logs**:
   ```bash
   # Logs should contain structured fields
   grep "component=config" logs/digest.log
   ```

3. **Check STATE.md**:
   ```bash
   cat features/add-yaml-config-contracts/STATE.md
   # Should show STATUS=READY or P1_DONE_DEPLOYED
   ```

### Rollback Procedure

1. **Revert to Previous Version**:
   ```bash
   git checkout <previous-commit> -- src/
   uv sync
   ```

2. **Clear State** (if needed):
   ```bash
   rm -f state.db
   rm -rf public/
   ```

### Configuration Differences (INT vs PROD)

| Setting | INT | PROD |
|---------|-----|------|
| Log Level | DEBUG | INFO |
| State DB | test_state.db | state.db |
| Output Dir | /tmp/test_output | ./public |

### Monitoring

- Check structured logs for:
  - `validation_error_count > 0` indicates config issues
  - `config_validation_duration_ms` for performance
  - `phase=FAILED` indicates configuration failure

### Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Exit code 1 | Validation failure | Check logs for validation_error messages |
| Missing STATE.md | Evidence capture failed | Check write permissions on features/ directory |
| Checksum mismatch | Config file modified | Ensure config files are not modified during run |
