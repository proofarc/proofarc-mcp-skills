---
name: run-test
description: Run ProofArc tests, prove each assertion can fail, and report the result — for UI tests and API scenarios. Use after a test is created, or when the user asks to run, re-run or report on tests.
---

# Run, prove, report

## 1. Run

- **UI test:** `run_ui_test(test, environment, target="<target id, as a string>", drivers=["PLAYWRIGHT"], wait=True)` waits for the result. Without `wait`, poll `get_execution_status(execution_id=<jobId>, kind="ui_job")` until it's `COMPLETED`.
- **API scenario:** `execute_scenario(scenario, environment)`; poll `get_execution_status(execution_id=<executionId>, kind="api_scenario")`.
- **Several tests:** tag them (e.g. `suite:search`), then `run_by_tag(tags, project, environment, dry_run=True)` to see what would run, then without `dry_run`. For UI tests this works when the environment has one website target; with several, run each test with its `target`.
- Always pass `target` for UI tests when the environment has more than one website target.

## 2. Prove the assertion once

Change the expected value, run, and confirm the test **fails** at that step. Then change it back. A test that passes both ways tests nothing.

## 3. Read the result

- **Green:** say so in one line — test, steps passed, run id.
- **Red:** it's a finding. Report the failing step and its message. **Never** change the expectation to make it pass.
- A step failing in under a second with `ERR_NAME_NOT_RESOLVED at https://site.compath` means a missing slash — `{{baseUrl}}/path`.
- An error that names a fix (missing credential, no driver, which target) — apply it and run again; see `webui-test/reference.md`.

## 4. Report

Summarise from the run record (`get_execution_status` → the steps with status and time) — that's always complete. For a shareable report, or a layout of the user's own, follow the `test-report` skill.
