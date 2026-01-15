# CHANGELOG.md - add-yaml-config-contracts

## Overview

This feature adds declarative YAML configuration contracts for sources, entities, and topics, providing a single source of truth for monitored sources, entity mapping, and ranking rules.

## Changes

### Added

- **Configuration Schemas** (Pydantic v2)
  - `SourceConfig`: Validates source definitions with strict schema
    - Unique source id enforcement
    - Required URL fields
    - Tier validation (0, 1, 2)
    - Method validation (rss_atom, arxiv_api, openreview_venue, github_releases, hf_org, html_list, html_single, status_only)
    - Kind enum validation
    - Timezone string validation
    - Non-negative integer limits
  - `EntityConfig`: Validates entity definitions
    - Unique entity id enforcement
    - Region validation (cn, intl)
    - Non-empty keyword list
    - prefer_links as non-empty list of known link types
  - `TopicsConfig`: Validates topic and scoring definitions
    - dedupe canonical_url_strip_params as list of strings
    - Scoring weights in [0.0, 5.0]
    - Topic keywords with length >= 1

- **Configuration State Machine**
  - States: UNLOADED, LOADING, VALIDATED, READY, FAILED
  - Strict transition guards
  - Immutable configuration per run

- **CLI Commands**
  - `digest run`: Main entry point with strict argument validation
    - `--config`: Path to sources.yaml
    - `--entities`: Path to entities.yaml
    - `--topics`: Path to topics.yaml
    - `--state`: Path to state database
    - `--out`: Output directory
    - `--tz`: Timezone string

- **Observability**
  - Structured logging with fields: run_id, component, phase, file_path, file_sha256, validation_error_count
  - Metrics: config_validation_duration_ms, config_validation_errors_total
  - Audit logging with SHA-256 checksums

- **Evidence Capture**
  - Normalized configuration snapshot persistence
  - STATE.md updates per run
  - E2E_RUN_REPORT.md generation

### Security

- No secrets in YAML files
- Tokens via environment variables only (HF_TOKEN, GITHUB_TOKEN, OPENREVIEW_TOKEN)
- Safe YAML loading only

### Testing

- Unit tests for schema validation (positive/negative)
- Unit tests for defaults application
- Unit tests for uniqueness constraints
- Unit tests for stable normalization determinism
- Integration tests for loading three YAML files
- E2E tests with clear-data prerequisites

## Breaking Changes

None (new feature).

## Migration Guide

No migration required (new feature).

## Dependencies Added

- pydantic >= 2.0
- pyyaml >= 6.0
- click >= 8.0
- structlog >= 24.0
