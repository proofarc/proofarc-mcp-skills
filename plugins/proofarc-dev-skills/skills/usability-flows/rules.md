# Usability rules

Each rule is something the platform must do. The flows that check it are in `api/flows.md` and `ui/flows.md`.

## U1. Never start a run that can't pass
If a run is missing something it needs (data set row, login, login flow, token endpoint), the platform asks how to run it (UI) or refuses with a 400 that names what's missing (API/MCP). It never starts a run that ends red because of setup.
- Seen: re-running data-driven scenario 179 started plain runs 760/761 that failed on `{{mode}}`. proofarc/tspc-cloud-platform#569.
- Already holds for: OAuth2 login without a token endpoint, username/password without a login flow (both refused with 400 on `c59e38eb`).

## U2. The status says what happened
A failed test is never shown as done/green. The run's status separates passed, failed, blocked (a step skipped because an earlier one failed), not run, and auth failed.
- Seen: `/scans/1312` showed an API scenario as completed in green with no steps; job 1661 is `COMPLETED` with `testOutcome: FAILED`.

## U3. Every result shows its steps
A finished run lists each step with its status and, for a failed or skipped step, the reason.
- Seen: `/scans/1312` (no steps); `/scans/1500` has them, but only under View Results > Test executions.

## U4. An error names its fix
An error says what's wrong and what to do next, in the user's terms.
- Seen: "Nothing supplied a value for {{mode}}" lists env property / extraction, but not "this scenario has a data set: run it". proofarc/tspc-cloud-platform#569.
