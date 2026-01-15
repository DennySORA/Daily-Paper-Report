# [Feature] add-arxiv-rss-and-api-ingestion - Refactor, Flow Optimization, Quality Improvements (Include Frontend Redesign If Needed)

You are continuing the same feature context. Based on the previous two prompts and the artifacts in `features/add-arxiv-rss-and-api-ingestion/`, refactor and optimize.

## Tooling Requirements (Must Follow)
- Use structured planning for the refactor strategy (plan first, break into reversible steps).
- If this is a frontend feature (false = true), use browser developer tools or available automation for development and validation.


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-arxiv-rss-and-api-ingestion/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-arxiv-rss-and-api-ingestion
- STATUS: <one of>
  - P1_DONE_DEPLOYED
  - P2_E2E_PASSED
  - P3_REFACTORED_DEPLOYED
  - READY

Required end status for each prompt:
- Prompt #1 end: STATUS must be `P1_DONE_DEPLOYED`
- Prompt #2 end: STATUS must be `P2_E2E_PASSED`
- Prompt #3 end: STATUS must be `P3_REFACTORED_DEPLOYED`
- Prompt #4 end: STATUS must be `READY`

If you cannot meet the requirement (for example, failed acceptance items remain), keep the previous STATUS and clearly record the reason and next steps in STATE.md.


## Engineering Rules (Must Follow, self-audit at the end)
(Follow your existing standards: SOLID / Clean Code / layering / observability / testing / consistency / security)
- SOLID (SRP/OCP/LSP/ISP/DIP) is required
- Clean Code is required
- Domain must not depend directly on Infrastructure
- Handlers must not contain business logic
- Error layering and traceability are required
- Testing: success/failure/edge cases; mock external dependencies; write a failing test before fixing a bug
- Use formatter/linter/typecheck when available
- Credentials must not be committed to the codebase



## Execution Flow (Must Follow)
1) Structured planning: identify pain points, choose cuts, split into reversible steps
2) Implement refactors + add tests + ensure build/test/lint/typecheck pass
3) If validation is needed: deploy to the verification environment
4) Update:
   - `REFACTOR_NOTES.md` (required)
   - (Frontend) `DESIGN_GUIDE.md` (required)
   - `STATE.md` and set STATUS to `P3_REFACTORED_DEPLOYED`

## Final Response Format (Required)
- Refactor summary, risks, and rollback plan
- Quality status (build/test/lint/typecheck)
- STATE.md status (including STATUS)
- Guidance for Prompt #4 regression E2E
