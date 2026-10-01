---
name: test-report
description: Build a report of ProofArc test runs — pick which runs, pick a layout (a built-in one or a custom one the user describes), and have the platform render it. Use when the user asks for a report, summary or results page of their tests or runs, wants a failures-only view, or wants their own report layout or branding.
---

# Test report — the platform renders it, you choose runs and layout

Reports are rendered by ProofArc from the stored run data, so they cost a few dozen tokens instead of an agent writing HTML. Your job is to pick the **runs** and the **layout**.

## 1. Which runs

Ask only if it isn't clear. Typical answers and how to find them:

| The user wants… | Find the runs with |
|---|---|
| specific runs ("runs 473 and 481") | use them as given — run numbers, job ids, or `api:<n>` for API scenario runs |
| the latest run of each test in a project | `find_ui_tests(project)`, then `list_ui_test_executions(test, limit=1)` per test → its `jobId` |
| a suite, tag or change (`change:verify-storefront`) | `find_ui_tests(project, tags=[…])`, then the latest run of each |
| only what failed recently | `find_test_results(project, status="FAILED", size=…)` — rows are **per step**; collect the distinct `scanJobId` values (those are run numbers) |
| just the numbers (pass rate, counts) | `get_test_results_summary(project)` — no report needed |

Runs of different kinds (UI, mobile, API) can go in one report.

## 2. Which layout

**Built-in templates** — use one of these unless the user asks for something else:
- `ui-full` — every step of every run
- `ui-summary` — one line per run
- `ui-failures-only` — only failed runs; says "every run passed" when there are none

**Custom layout** — when the user wants different columns, grouping, wording or branding:
1. Ask what they want to see — e.g. "one line per test with name, result and time", "group by test type", "our logo colours".
2. Write a FreeMarker template over the report fields. The main ones:
   - report: `report.title`, `report.generatedAt`, `report.runs`
   - run (`<#list report.runs as r>`): `r.testName`, `r.kindLabel`, `r.outcome`, `r.passed`, `r.totalSteps`, `r.duration` (seconds), `r.startedAt`, `r.runNumber`, `r.errorMessage`, `r.steps`
   - step (`<#list r.steps as s>`): `s.action`, `s.status`, `s.duration`, `s.errorMessage`
   Put `!` after anything that can be missing (`${r.duration!'—'}`). Full list and examples: `fields.md`. For a polished full report, start from `templates/branded-full.ftl`.
3. Pass it as `template_source`. A mistake comes back as a 400 that names the field — fix it and render again.

The platform doesn't store custom templates yet: save the template file for the user (e.g. `reports/<name>.ftl` in their repo) so it can be reused.

## 3. Render

`render_report(runs=[…], template="ui-summary", title="…")` or `render_report(runs=[…], template_source=<ftl>, title="…")`.

- The default answer is counts only (`runs`, `passed`, `failed`, `htmlLength`) — about 70 tokens. Report those to the user.
- Ask for `include_html=True` **only** when the user wants the file: it brings the whole HTML into the conversation (~2k tokens for 3 runs, more for large reports). Save it to a file (e.g. `report-<date>.html`) and tell the user where it is; don't paste HTML into the chat.

## Things to know

- Everything from the application under test is escaped — text from the site can't break the report.
- Screenshots appear as file names/links, not embedded images; opening them needs a ProofArc login.
- UI step "detail" (selector or value) is empty for Playwright runs — the agent doesn't store it yet. Don't build a layout that depends on it.
- A run that failed before any step has no step rows; its reason is in the run's `errorMessage`.
