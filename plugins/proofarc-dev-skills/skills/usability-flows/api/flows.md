# Usability flows: API (through MCP, no UI)

Project 169, environment 125 (`dev`) for every call.

## U1.a  Run a data-driven scenario without a row
- **Needs:** scenario 179 `dogfood-10060345-dd` (`dataColumns: [mode, want]`, data set `dogfood-plan-dd`, version `v1.0`).
- **Call:** `execute_scenario(scenario=179, environment=125, wait=True)`. No row values, no data set.
- **Pass if:** the call is refused (no `executionId` comes back), and the message names the data set or says to pass row values.
- **Verdict:** an `executionId` came back → **U1.a FAIL**, whatever the run's status. No exceptions.
- **Fail looks like:** an `executionId` comes back. Read it with `get_execution_status(execution_id=<executionId>, kind="api_scenario")`: `status` FAILED, step 1 "Nothing supplied a value for {{mode}}". Keep this execution for U4.a.

## U1.b  Run the data set
- **Needs:** as U1.a.
- **Call:** `run_data_driven(name="dogfood-plan-dd", version="v1.0", environment=125)`, then `get_data_driven_execution(execution=<id it returns>)`. Its `entryResults` has one entry per row, each with a `scenarioExecutionId`. Read each of those with `get_execution_status(execution_id=<scenarioExecutionId>, kind="api_scenario")`. The fields below are on that execution, not on the data-driven summary (which has `testName` and `variablesUsed` instead).
- **Pass if:** one execution per row of the set, and each execution has `runName` "Row N", `tags` containing `dataset:Row N`, and the row's `mode` and `want` in `variablesSnapshot`. Report each row's `status`, but it isn't a pass condition.

## U1.c  Login without what it needs (to define)
- Not runnable yet. Environment 125 is shared and already has a login flow, so "no token endpoint" can't be set up without changing shared state. Needs a trial environment of its own.

## U2.a  A failed run reads as failed
- **Needs:** `usability-u2-fail` (below), in project 169.
- **Call:** `execute_scenario(scenario=<its id>, environment=125, wait=True)`, then `get_execution_status(execution_id=<executionId>, kind="api_scenario")`. Don't pass `stop_on_failure`.
- **Pass if:** `status` is FAILED, not COMPLETED.
- This checks the execution record only. The scan page in the UI reads the job, which can still say COMPLETED (job 1661). That's checked by `ui/flows.md` U2.

```yaml
name: "usability-u2-fail"
baseUrl: "{{baseUrl}}"
appTag: "proofarc-api"
credentialTag: "dogfood-admin"
steps:
- name: "list projects, wrong expectation"
  method: "GET"
  path: "/api/projects"
  expect: [418]
- name: "list again"
  method: "GET"
  path: "/api/projects"
  expect: [200]
- name: "list third"
  method: "GET"
  path: "/api/projects"
  expect: [200]
```

## U3.a  Steps after a failure are reported, with a reason
- **Needs:** the U2.a execution (3 steps, step 1 fails, `stop_on_failure` not passed).
- **Call:** `get_execution_status(execution_id=<U2.a executionId>, kind="api_scenario")`.
- **Pass if:** `totalSteps` is 3, and the step list has all 3: step 1 FAILED with its error ("Expected status [418] but got 200"), steps 2–3 SKIPPED with a reason that says an earlier step failed.

## U4.a  The unresolved-variable error points to the data set
- **Needs:** the execution U1.a started. If U1.a passed (no run), U4.a is N/A. Don't start a second red run.
- **Call:** `get_execution_status(execution_id=<U1.a executionId>, kind="api_scenario")`.
- **Pass if:** step 1's error mentions the scenario's data set (`dogfood-plan-dd`) or running it as a data set, because `mode` is one of its `dataColumns`.
