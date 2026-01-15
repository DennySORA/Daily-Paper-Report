# CHANGELOG.md - Feature Change Summary

## Feature: add-sources-status-and-degradation-reporting

### Version 1.0.0 (2026-01-15)

#### Summary

This feature introduces explicit source status classification and degradation reporting to distinguish between "no update", "cannot confirm", and "fetch failed" states per source. The status is visible in both HTML and JSON outputs.

#### New Features

1. **Source Status Classification**
   - Per-source status computed for each run
   - Six status codes: NO_UPDATE, HAS_UPDATE, FETCH_FAILED, PARSE_FAILED, STATUS_ONLY, CANNOT_CONFIRM
   - Deterministic classification rules with clear precedence

2. **Reason Codes**
   - Machine-readable reason codes (e.g., `FETCH_PARSE_OK_HAS_NEW`)
   - Human-readable reason text in English
   - Optional remediation hints for failure states

3. **Source Categories**
   - Sources grouped by category for UI display
   - Categories: International Labs, CN/Chinese Ecosystem, Platforms, Paper Sources, Other

4. **Enhanced HTML Rendering**
   - Summary statistics showing counts per status type
   - Sources grouped by category in tables
   - Status badges with semantic colors

5. **Enhanced JSON API**
   - `sources_status` array in `api/daily.json`
   - Full status metadata per source including category

6. **Observability**
   - Audit logging with rule path for each status decision
   - Metrics: `sources_failed_total`, `sources_cannot_confirm_total`

#### Files Added

| File | Description |
|------|-------------|
| `src/status/__init__.py` | Module exports |
| `src/status/models.py` | ReasonCode, SourceCategory, StatusRulePath models |
| `src/status/computer.py` | StatusComputer class |
| `src/status/metrics.py` | StatusMetrics singleton |
| `tests/unit/test_status/__init__.py` | Test package |
| `tests/unit/test_status/test_models.py` | Unit tests for models |
| `tests/unit/test_status/test_computer.py` | Unit tests for StatusComputer |
| `tests/unit/test_status/test_metrics.py` | Unit tests for metrics |
| `tests/integration/test_status_rendering.py` | Integration tests |

#### Files Modified

| File | Changes |
|------|---------|
| `src/renderer/models.py` | Added `category` field to SourceStatus |
| `src/renderer/json_renderer.py` | Include category in JSON output |
| `src/renderer/templates/sources.html` | Category grouping, summary stats, status badges |

#### Breaking Changes

None. This is a backward-compatible feature addition.

#### Migration Notes

- Existing code using `SourceStatus` will work unchanged
- New `category` field defaults to `None` for backward compatibility
- JSON API `sources_status` is additive; existing consumers unaffected

#### Known Limitations

1. Source categories must be explicitly provided to `StatusComputer`
2. `last_fetch_status_code` is not yet populated (requires fetch client enhancement)
3. Retention/archival of per-run status not yet implemented

#### Reviewers

Please verify:
- [ ] Status classification logic matches requirements
- [ ] Reason codes are stable and well-documented
- [ ] HTML rendering is accessible and responsive
- [ ] JSON schema is compatible with existing consumers

---

*Generated as part of P1 implementation*
