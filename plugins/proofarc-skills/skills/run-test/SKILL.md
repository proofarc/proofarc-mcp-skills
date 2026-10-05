---
name: run-test
description: Run ProofArc tests, prove each assertion can fail, and report the result — for UI tests, API scenarios and mobile tests. Use after a test is created, or when the user asks to run, re-run or report on tests.
---

# Run, prove, report

## 1. Run

**Playwright only, for now.** Every UI run uses `drivers=["PLAYWRIGHT"]`, and every UI test is saved with `driver="PLAYWRIGHT"`. Never run or save a UI test for `WEBDRIVER`, even if the user asks: say *"Web tests run on Playwright for now; WebDriver isn't supported yet."* and run it on Playwright. The two engines don't behave the same yet (`:has-text()` fails on WebDriver; a page that never loads passes there).
- **UI suite:** `run_ui_test_suite(suite, environment, target, drivers=["PLAYWRIGHT"])`.
- **`run_by_tag` with UI tests** has no engine parameter: it uses each test's saved driver. Run it only when every UI test it would queue is saved as PLAYWRIGHT (`get_ui_test` → `driver`); otherwise run each with `run_ui_test(..., drivers=["PLAYWRIGHT"])`.

- **UI test:** `run_ui_test(test, environment, target="<target id, as a string>", drivers=["PLAYWRIGHT"], wait=True)` waits for the result. Without `wait`, poll `get_execution_status(execution_id=<jobId>, kind="ui_job")` until it's `COMPLETED`.
- **API scenario:** `execute_scenario(scenario, environment)`; poll `get_execution_status(execution_id=<executionId>, kind="api_scenario")`.
- **Several tests:** tag them (e.g. `suite:search`), then `run_by_tag(tags, project, environment, dry_run=True)` to see what would run, then without `dry_run`. For UI tests this works when the environment has one website target; with several, run each test with its `target`. For UI tests also check that every entry in the dry run's `would_queue` is saved as `driver: PLAYWRIGHT` (`get_ui_test`); otherwise run each with `run_ui_test(..., drivers=["PLAYWRIGHT"])`.
- **Mobile test:** `run_mobile_test(mobile_test, environment, credential_tag, wait=True)`; read the result with `get_mobile_test_executions(mobile_test)` (`get_execution_status` doesn't take mobile runs).
- Always pass `target` for UI tests when the environment has more than one website target.
- **Which login it signs in as:** the one named on the run → saved on the test → set on the target → the environment default. Name it (`credential_tag=`) whenever the environment has more than one. Refusals, retries and "no login" runs: `logins.md`.

## 2. Prove the assertion once

Change the expected value with `update_ui_test_from_yaml(test, yaml_text)` (UI) or `update_api_scenario_from_yaml(scenario, yaml_text)` (API), run, and confirm the test **fails** at that step. Then restore it, **re-run, and confirm it's green again** before reporting. A test that passes both ways tests nothing.

## 3. Read the result

- **Green:** say so in one line — test, steps passed, run id.
- **Red:** it's a finding. Report the failing step and its message. **Never** change the expectation to make it pass.
- A step failing in under a second with `ERR_NAME_NOT_RESOLVED at https://site.compath` means a missing slash — `{{baseUrl}}/path`.
- An error that names a fix (missing credential, no driver, which target) — apply it and run again. `references {{username}}/{{password}} but no credentials are available` means the environment needs a login: ask the user for it, add it, and pass its tag as `credential_tag`.
- `CREDENTIAL_AMBIGUOUS` or `CREDENTIAL_TAG_NOT_FOUND` — the run was refused before anything ran; it's a setup question, not a test result. See `logins.md`.

## 4. Report

Summarise from the run record (`get_execution_status` → the steps with status and time) — that's always complete. For a shareable report, or a layout of the user's own, follow the `test-report` skill.
