# Changelog — proofarc-skills

## 0.3.3 — 2026-10-02
- **webui-test:** the body now matches its reference-only role. It points to `crawl-to-tests`, applies the same rules, and reads selectors from the stored crawl. Its example uses `CLEAR`, a page-specific wait, and an outcome check.
- **crawl-to-tests:** §8 is in order (build and run, then what to do when a run fails). The skill reads `reference.md` before drafting the first test. A login being saved is checked with `list_environment_credentials`. The preload list adds `add_environment_credential`, `list_environment_credentials` and `run_by_tag`.
- **crawl-to-tests/reference.md:** cross-references name SKILL.md sections.
- **connect-proofarc.sh:** prints the address and server name it uses.

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
- Reviewed by Fable before it was released (20 findings on 0.3.1). **0.3.2 itself was pushed before its own review**, which broke the new rule; that review's findings are fixed in 0.3.3.

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
