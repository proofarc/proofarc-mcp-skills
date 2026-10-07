# Usability flows: UI (dogfood UI tests)

The same rules, checked on the screen. Each flow is a UI test in the trial project (dev: `dog-food-api`, 169), run on Playwright with the environment's `dogfood-admin` login (`{{username}}`/`{{password}}`, never literals). Build it with the `crawl-to-tests` skill.

## U1  Re-run a data-driven row offers a choice
- Open a "Row N" run of a data-driven scenario (one from `api/flows.md` U1.b), press Re-run.
- **Pass if:** a prompt offers re-run this row, run the whole data set, run without data. No run starts before a choice. proofarc/tspc-cloud-platform#569.

## U2  A failed run is red
- Open `/scans/<job>` of a failed API run (e.g. the run from `api/flows.md` U2.a).
- **Pass if:** the run shows as failed (red), never completed/green.

## U3  Steps are on the run page
- Same page.
- **Pass if:** each step is listed with its status, and the failed step's error is shown, without going through View Results > Test executions.
