# Changelog — proofarc-skills

## 0.3.6 — 2026-10-05
- **Web UI tests run on Playwright only, for now.** `crawl-to-tests` (new Test rule 9) and `run-test` always run with `drivers=["PLAYWRIGHT"]` and save tests with `driver="PLAYWRIGHT"`, and refuse WebDriver even when asked, explaining why. The engines don't behave the same yet: `:has-text()` is rejected on WebDriver, and a page load that times out is reported as passed there. `run_ui_test_suite` gets `drivers=["PLAYWRIGHT"]`; `run_by_tag` (no engine parameter) is used only when every UI test it queues is saved as Playwright.

## 0.3.5 — 2026-10-05
- **crawl-to-tests: a fixed first move at the very top.** Find the ProofArc servers. If there's more than one, the first reply is only "Which ProofArc do you want to work in?". Then load that server's tools and call them as tools, never through Bash. In the user's real setup (installed plugin, ordinary folder, Haiku, two ProofArc servers), 0.3.4 asked the instance question in 1 of 3 runs, and in one run tried Bash and gave up. 0.3.5 asks it in 5 of 5 runs (8–19 s), and the full flow instance → app → environment → suggested tests passed in 2 of 2 runs (about 60 s).
- **New: `tools/drive_agent.py`** plays the user through a scripted conversation (`claude -p --resume`), checks each reply against regexes, the skill started and forbidden tools, and writes a transcript. Scenarios are in `tools/scenarios/`.
- Release rule: the driver scenarios must pass in the user's real setup before a push.
- **crawl-to-tests: approval gate.** `create_ui_test_from_yaml` and `run_ui_test` are never called in the same reply as the plan; a test the user names that isn't on the list gets a plan and a stop.
- **crawl-to-tests: never show a plan that breaks a Test rule**, not even as one option beside a better one.
- **crawl-to-tests: platform gotchas first.** Before the first draft the skill calls `get_tool_gotchas("create_ui_test_from_yaml")` and treats them as binding.
- **crawl-to-tests: tests are saved as Playwright** (`driver="PLAYWRIGHT"`), because the selectors it writes (`:has-text()`, `text=`, `:visible`) don't work on WebDriver.
- **crawl-to-tests: tools are called directly**, never through Bash, curl or a sub-agent; one failing server (or `claude.ai proofarc`) says nothing about the others.
- **tools/drive_agent.py: goal mode and a controlled setup.** `goal` (answer rules, `until` + `until_tools`, `approve_say`), `mcp_servers` (only the named servers, from a 0600 file), automatic updates off during a drive, and a retry when `claude` is briefly missing.
- **crawl-to-tests: one wait time per test.** Rule 2 and `reference.md` now set the wait time once in a `config:` block with `timeout: 15000` (milliseconds) and use a step's `timeout:` only to override it. The examples drop their per-step timeouts. Measured on a live instance, Playwright: no timeout → 30 s; top-level `timeout:`/`defaultTimeout:` → ignored (30 s); `config.timeout: 5000` → 5 s; plus a step `timeout: 2000` → 2 s; `config.timeout: 5` → 5 **ms**, because config is never read as seconds. (Playwright; WebDriver step-override timing to confirm.)
- **crawl-to-tests: wait for the data, not the frame.** On a page that loads a list, the final check waits for a row or known item. A search box or toolbar that renders before the data proves nothing, and the screenshot shows an empty page.
- **crawl-to-tests: the final check must fail if the action did nothing.** In a driven trial, the skill built two search tests that pass even when search is broken: one checked "Pliers" anywhere on the page, the other a Pliers card, and the home page already shows both. The skill's own plan example ("check Pliers appears") taught it. Rule 7 now says: look at the starting page in the crawl, never check something already there or text on `body`, check what the action creates (a results caption, count, toast or badge). Every plan carries a **Fails if … did nothing** line. On Toolshop, `[data-test="search-caption"]` containing "pliers" was confirmed to appear only after a search (a wait for it on the home page failed).
- **crawl-to-tests: one failing server is only that server.** A 503 from one connector made the agent tell the user that ProofArc was down, while another server worked.
- **crawl-to-tests: a shared name ("Toolshop") lists the matching apps.** The agent had picked one of two Toolshop apps itself.
- **tools/drive_agent.py: checks the YAML the agent creates**, not only its replies: `SEND_KEYS` without `CLEAR`, a text check on `body`, and (per scenario, `start_page_rx`) a final check on something already on the starting page. Both weak tests from the trial are caught (also when steps are written in flow style or with `selector` before `action`); a correct test passes.
- **crawl-to-tests: text selectors and hidden copies.** `text=Foo` waits on the first element containing Foo, which on a real app was a closed menu item or a hidden duplicate label (even with exact text), so the wait timed out while the text was on screen. Rule 6 now says to add `>> visible=true`. Gotcha #192.
- **crawl-to-tests: when a run fails, read its screenshot first.** Two causes seen on a real app: an element the crawl lists but that is hidden on load (the crawl has no visibility flag), and a dialog covering the page (closed with Cancel/X, never Skip/Save). The deliberately broken proof run is named in the report so it isn't mistaken for a real failure. Platform gotchas #190 and #191 carry the same rules for agents without the plugin.
- **test-report: new `templates/run-report.ftl`** (the run report layout). One section per test: its runs side by side (one card per engine), a note when engines disagree, the steps of the worst run, and a panel per failed step with its error and screenshot name. Rendered by the platform via `render_report(template_source=…)`; custom templates can't be saved on the platform, so the skill ships it. Tested on real runs (WebDriver + Playwright pair, a passing run, a failed navigation).
- **crawl-to-tests/reference.md: tips and banners.** A pop-up shown on every page (e.g. "Got it") is dismissed once after login, but only if dismissing it changes nothing on the account.

## 0.3.4 — 2026-10-02
- **No need to say "ProofArc":** plain requests such as "create UI tests for Toolshop" or "write some web tests for the shop" start `crawl-to-tests` in an ordinary folder. Before, Haiku treated them as "write test code locally" and searched the disk. A/B-tested with Haiku: 12 of 12 runs over 4 phrasings with ProofArc connected. A developer asking for Playwright code in their own repo with no ProofArc server doesn't trigger it (0 of 6), and the skill body says to stop in that case. `create-test` no longer requires the word ProofArc either.
- **Connecting with environment variables:** `connect-proofarc.sh` reads `PROOFARC_URL`, `PROOFARC_USERNAME` and `PROOFARC_PASSWORD` when they're set and asks only for what's missing, so Claude can connect for you. It never prints the username or password. Without a terminal, a missing value is reported instead of hanging. Tested non-interactively against a live instance.
- **connect skill:** checks which variables are set, using `printenv` in the user's own shell (works in zsh and bash) and showing only the address. If the user names a different address than `PROOFARC_URL`, it asks first and never sends saved credentials elsewhere. If variables are missing, it shows the lines to add to the shell profile.
- **crawl-to-tests:** "not connected" now separates a configured server that failed (`/mcp` → Reconnect) from no server or a 401 (the `connect` skill). The app-list example uses neutral names.
- Reviewed by Fable: 2 must-fix and 6 should-fix found, all addressed.

## 0.3.3 — 2026-10-02
- **webui-test removed.** "create UI tests for Toolshop" was starting it instead of `crawl-to-tests`, because its description quoted that phrase to redirect it. It then asked for the project, URL and behaviours. Its action and error tables moved to `crawl-to-tests/reference.md`. There's now one way into web UI testing.
- **crawl-to-tests:** §8 is in order (build and run, then what to do when a run fails). The skill reads `reference.md` before drafting the first test. A login being saved is checked with `list_environment_credentials`. The preload list adds `add_environment_credential`, `list_environment_credentials` and `run_by_tag`.
- **crawl-to-tests/reference.md:** cross-references name SKILL.md sections.
- **connect-proofarc.sh:** prints the address and server name it uses.
- **crawl-to-tests:** `run all` names its call: `run_by_tag` (dry run first).
- Reviewed by Fable before release: 9 findings on 0.3.2 fixed, then 2 must-fix and 4 should-fix on 0.3.3 fixed. "`target` is the id" was confirmed on live instances.

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
