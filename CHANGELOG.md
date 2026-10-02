# Changelog — proofarc-skills

## 0.3.3 — 2026-10-02
- **webui-test removed.** "create UI tests for Toolshop" was starting it instead of `crawl-to-tests`, because its description quoted that phrase to redirect it. It then asked for the project, URL and behaviours. Its action and error tables moved to `crawl-to-tests/reference.md`. There's now one way into web UI testing.
- **crawl-to-tests:** §8 is in order (build and run, then what to do when a run fails). The skill reads `reference.md` before drafting the first test. A login being saved is checked with `list_environment_credentials`. The preload list adds `add_environment_credential`, `list_environment_credentials` and `run_by_tag`.
- **crawl-to-tests/reference.md:** cross-references name SKILL.md sections.
- **connect-proofarc.sh:** prints the address and server name it uses.
- **crawl-to-tests:** `run all` names its call: `run_by_tag` (dry run first).
- Reviewed by Fable before release: 9 findings on 0.3.2 fixed, then 2 must-fix and 4 should-fix on 0.3.3 fixed. "`target` is the id" was confirmed live on dev and OutpostQA.

## 0.3.2 — 2026-10-02
- **crawl-to-tests:** nine non-negotiable test rules now come first. Command table, selector and parameter detail, and the wrong-vs-right example moved to `crawl-to-tests/reference.md`.
- **crawl-to-tests:** suggested tests must follow the rules (no opening a record directly) and name the check they end with.
- **crawl-to-tests:**
  - one login setup (the Authenticated Web UI Flow)
  - `target` always means the target's id
  - every tool used is in the preload list
  - failed runs: the skill fixes its own mistakes and asks only about the site
- **create-test:** a website or URL goes straight to crawl-to-tests.
- **webui-test:** now a reference for writing one test by hand. Timeouts are in milliseconds.
- **project-setup:** `create_application` signature includes `application_type`.
- **run-test:** proving a test can fail names the update tools, and the test must be green again afterwards.
- **connect-proofarc.sh:** handles `host:port`, paths and addresses without `https://`.
- Fixes the 20 findings from Fable's review of 0.3.1. 0.3.2 itself was pushed before its own review; that review's findings are fixed in 0.3.3.

## 0.3.1 — 2026-10-02
- **crawl-to-tests:**
  - rules made mandatory: no record ids, journeys start from real entry points, wait before every interaction
  - wrong-vs-right journey example, proven on Toolshop
  - checks for elements that appear only after an action
  - crawl labels can be truncated

## 0.3.0 — 2026-10-02
- **New skill: crawl-to-tests.** An interactive guide from application → project → environment → crawl, to a summary, testability score, suggested tests or your own scenario, then build, run and prove. Commands: `find`, `show`, `stable`, `explain`, `scenario`, `test`, `where`, `fixlist`, `more`, `done`.

## 0.2.0 — 2026-10-01
- Plugin renamed `proofarc-skills`.
- New skills: api-test, mobile-test, performance-test, connect (with `connect-proofarc.sh`).
- MIT licence.

## 0.1.0 — 2026-09-29
- First skills: create-test, project-setup, webui-test, run-test, test-report.
