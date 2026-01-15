# [Fixed] Verification Environment E2E Regression (Post-Refactor, Until Passing)

You are continuing the same feature context.
Goal: for the refactored version, run full regression E2E in the verification environment using a real browser until `ACCEPTANCE.md` is fully satisfied.

## Tooling Requirements (Must Follow)
- Use structured planning to identify regression scope and risks.
- Use a real browser and developer tools for comprehensive E2E (including console/network/error checks).


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-collectors-framework/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-collectors-framework
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


## Required Files
- `features/add-collectors-framework/E2E_PLAN.md`
- `features/add-collectors-framework/ACCEPTANCE.md`
- `features/add-collectors-framework/STATE.md`
- `features/add-collectors-framework/REFACTOR_NOTES.md`
- (If present) `features/add-collectors-framework/DESIGN_GUIDE.md`

## Execution Steps (Must Follow)
1) Structured planning: list regression areas and decide order
2) Developer tools: run the full E2E plan and check console/network/perf/layout/interaction
3) Fix loop on failure: minimal fix -> test -> deploy to the verification environment -> re-validate
4) When all pass:
   - Update `E2E_RUN_REPORT.md`
   - Update `STATE.md` and set STATUS to `READY`

## Final Response Format (Required)
- Regression E2E pass summary (aligned with `ACCEPTANCE.md`)
- STATE.md status (include STATUS=READY)
- Feature close-out summary
