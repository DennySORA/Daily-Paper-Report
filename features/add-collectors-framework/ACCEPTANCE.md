# ACCEPTANCE.md - Collector Framework

## Feature: add-collectors-framework

Acceptance criteria checklist for the Collector Framework feature.

## Functional Requirements

### Core Interface

- [x] **AC-1**: Collectors implement common interface: `collect(source_config, http_client, now) -> CollectorResult`
- [x] **AC-2**: CollectorResult contains: items list, parse_warnings list, optional error, state
- [x] **AC-3**: Items conform to existing Item model with all required fields

### State Machine

- [x] **AC-4**: Each source has its own state machine instance
- [x] **AC-5**: Valid states: SOURCE_PENDING, SOURCE_FETCHING, SOURCE_PARSING, SOURCE_DONE, SOURCE_FAILED
- [x] **AC-6**: Valid transitions enforced (invalid transitions raise SourceStateTransitionError)
- [x] **AC-7**: Terminal states: SOURCE_DONE, SOURCE_FAILED (no further transitions allowed)

### Error Handling

- [x] **AC-8**: Errors typed as FetchError, ParseError, or SchemaError
- [x] **AC-9**: ErrorRecord provides serializable error details for persistence
- [x] **AC-10**: Failing sources don't prevent other sources from succeeding (isolation)

### URL Processing

- [x] **AC-11**: URLs canonicalized (relative URLs resolved, tracking params stripped)
- [x] **AC-12**: Invalid URLs (non-http(s), javascript:, mailto:) rejected
- [x] **AC-13**: Duplicate URLs within a collection run deduplicated

### Ordering & Limits

- [x] **AC-14**: Items sorted deterministically: published_at DESC NULLS LAST, url ASC
- [x] **AC-15**: max_items per source enforced after sorting
- [x] **AC-16**: Ordering stable across multiple runs

### Persistence

- [x] **AC-17**: Items upserted to SQLite via StateStore
- [x] **AC-18**: first_seen_at set on insert, last_seen_at updated on every upsert
- [x] **AC-19**: Idempotent: running twice with same data doesn't create duplicates
- [x] **AC-20**: content_hash used for change detection

### Raw JSON Handling

- [x] **AC-21**: raw_json capped at 100KB
- [x] **AC-22**: Truncated entries marked with `raw_truncated: true`
- [x] **AC-23**: Sensitive fields (password, token, secret, key) redacted

### Collectors

- [x] **AC-24**: RSS/Atom collector parses standard RSS 2.0 and Atom 1.0 feeds
- [x] **AC-25**: RSS/Atom collector extracts: title, link, published_at, summary, author, categories
- [x] **AC-26**: HTML list collector finds article containers via semantic selectors
- [x] **AC-27**: HTML list collector falls back to link extraction if no containers found
- [x] **AC-28**: HTML list collector attempts date extraction via multiple strategies

### Runner

- [x] **AC-29**: CollectorRunner processes multiple sources
- [x] **AC-30**: Runner supports configurable max_workers for parallelism
- [x] **AC-31**: Runner automatically selects collector based on source.method
- [x] **AC-32**: Runner returns aggregated RunnerResult with per-source details

## Non-Functional Requirements

### Observability

- [x] **NFR-1**: Structured logging with source_id, run_id, component context
- [x] **NFR-2**: Metrics tracked: items collected, failures, duration per source
- [x] **NFR-3**: Prometheus-format metric export available

### Performance

- [x] **NFR-4**: Parallel collection via ThreadPoolExecutor
- [x] **NFR-5**: No blocking operations in main collection loop

### Security

- [x] **NFR-6**: No credentials in raw_json (redaction in place)
- [x] **NFR-7**: URLs validated before processing

## Testing Requirements

### Unit Tests

- [x] **TEST-1**: URL canonicalization edge cases tested
- [x] **TEST-2**: State machine transitions tested (valid and invalid)
- [x] **TEST-3**: Error class hierarchy tested
- [x] **TEST-4**: Deterministic ordering tested
- [x] **TEST-5**: max_items enforcement tested
- [x] **TEST-6**: raw_json truncation tested

### Integration Tests

- [x] **TEST-7**: RSS collector + SQLite tested
- [x] **TEST-8**: HTML collector + SQLite tested
- [x] **TEST-9**: Multiple collectors in single run tested
- [x] **TEST-10**: Failure isolation tested
- [x] **TEST-11**: Idempotent upsert tested

## Verification Status

| Category | Passed | Total | Status |
|----------|--------|-------|--------|
| Functional | 32 | 32 | PASS |
| Non-Functional | 7 | 7 | PASS |
| Testing | 11 | 11 | PASS |

**Overall Status**: ALL ACCEPTANCE CRITERIA MET
