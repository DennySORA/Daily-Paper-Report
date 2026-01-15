# [Fixed] Verification Environment E2E Validation (Until Passing)

You are continuing the same feature context. Use the previous prompt outputs and codebase artifacts to run E2E.
Goal: validate the feature end-to-end in the verification environment using a real browser. If it fails, fix, redeploy, and retest until it passes.

## Tooling Requirements (Must Follow)
- Use structured planning to schedule E2E execution and remediation.
- Use a real browser and developer tools for comprehensive end-to-end testing (including console/network/error checks).


## State Machine (Required, for enforcing step order)
You must maintain the following fields in `features/add-http-fetch-layer/STATE.md` (create if missing) and update them at the end of each prompt:

- FEATURE_KEY: add-http-fetch-layer
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


## Operating Rules (Must Follow)
1) Read and follow:
   - `features/add-http-fetch-layer/E2E_PLAN.md`
   - `features/add-http-fetch-layer/ACCEPTANCE.md`
   - `features/add-http-fetch-layer/RUNBOOK_VERIFICATION.md`
   - `features/add-http-fetch-layer/STATE.md`

2) Execute tests in the verification environment with a real browser (step-by-step UI/interaction/console/network checks)
3) If failing: fix -> test -> deploy to the verification environment -> re-validate (until passing)
4) When passing:
   - Update `E2E_RUN_REPORT.md`
   - Update `STATE.md` and set STATUS to `P2_E2E_PASSED`

## Stop Condition
- You may only complete this prompt when all items in `ACCEPTANCE.md` are checked off and the core E2E flows plus key failure scenarios pass.

## Final Response Format (Required)
- E2E pass summary (aligned with `ACCEPTANCE.md`)
- STATE.md status (including STATUS)
- Guidance for Prompt #3 refactoring/optimization
