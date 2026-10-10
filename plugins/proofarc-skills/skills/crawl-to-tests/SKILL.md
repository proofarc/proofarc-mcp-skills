---
name: crawl-to-tests
description: Use whenever the user asks to create, write, build or suggest UI / web / browser tests for a site or app — "create UI tests for Toolshop", "test my website", "test https://…", "web tests for <app>", "write some web tests for the shop", "what can I test on <site>", "find the screen with …" — even when ProofArc isn't mentioned. The tests are built and run on the connected ProofArc platform (its mcp__…proofarc… tools), not as Playwright/Cypress files on disk, so don't search the local folder for code. Interactive: pick the app, project and environment, read or run the crawl, suggest tests or map the user's scenario, then build, run and prove them. Web UI only. Skip it only when no ProofArc MCP server is configured and the user wants test code written into their own repo.
---

# Web UI tests from the crawl

## FIRST: do exactly this, in this order

1. **Find the ProofArc servers** in your tool list: tool names `mcp__<server>__…` where `<server>` contains `proofarc` (e.g. `proofarc-staging`, `proofarc-prod`). Ignore `claude.ai proofarc`.
2. **More than one?** If the user named an app, project or address, you may call `get_working_context` with it on each server **yourself** (`list_applications` on a server that has no `get_working_context`): one direct tool call per server (in parallel is fine), never through `Agent`/`Task`, `Bash` or `echo`. If exactly one server has it, use it and say *"On proofarc-…:"*. Otherwise your **first reply is only this question**, with no other tool calls before it:
   > Which ProofArc do you want to work in?
   > 1. **proofarc-staging**
   > 2. **proofarc-prod**

   Use the real names you found (the ones above are only examples), then wait. `AskUserQuestion` is fine for this question. **One server:** use it without asking. **None:** follow the `connect` skill. **Configured but failed to connect:** ask the user to run `/mcp` → Reconnect.

   **One server failing is only that server.** An error or 503 from one (or from `claude.ai proofarc`) says nothing about the others: try each ProofArc server's tools before saying anything is unavailable, and never conclude "ProofArc is down" from one failure.
3. **Load that server's tools with one `ToolSearch`:** `select:` followed by `mcp__<server>__` plus each of `get_working_context`, `list_applications`, `list_application_projects`, `list_environments`, `list_targets`, `list_environment_credentials`, `get_crawl_digest`, `crawl_by_target`, `advise_ui`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `update_ui_test_from_yaml`, `run_ui_test`, `get_execution_status`, `find_ui_tests`, `get_ui_test`, `get_crawl_results`, `list_ui_test_actions`, `find_playbooks`, `add_environment_credential`, `set_target_auth`, `run_by_tag`, `get_tool_gotchas`.
4. **Call them as tools, yourself.** Never reach ProofArc through Bash, curl, Python or a sub-agent (`Agent`/`Task`): a sub-agent may not have these tools, and its failure is not a lost connection. Never ask the user how to call tools. Don't use Bash to print status messages either; just write the text. A result too large to show is saved to a file: read it with `Read` (`offset`/`limit`), or ask the tool for less (`page=`, `text=`, `type=`), not with Bash.

**Every reply ends with numbered choices.** Ask one thing per reply and mark a sensible default *(recommended)*.

## Test rules (check every plan against these yourself; don't ask the user)

1. **No record ids** in a URL or selector (`/product/01M3…`). Reach records through the UI from a real entry point (home, category, search) and click them **by visible name** (`a:has-text("Combination Pliers")`). Only fixed routes (`/contact`, `/category/hand-tools`) may be opened directly.
2. **Wait for that page's content before every interaction:** `WAIT_FOR_VISIBLE` on a form, list or heading of that page. When the page loads data, wait for the data itself (a list row, a known item), not a search box or toolbar that appears before it. Set the wait time **once** in a top-level `config:` block containing `timeout: 15000` (milliseconds; `15` would mean 15 ms), and put `timeout:` on a step only to override it. A top-level `timeout:` or `defaultTimeout:` (outside `config:`) is ignored, and the wait falls back to 30 s.
3. **`{{baseUrl}}/path`**, with the application's `appTag:` at the top. Never the site's URL.
4. **Parameters:** `NAVIGATE_TO` takes `url:`. `VALIDATE_*` and `WAIT_FOR_TEXT` take `expectedText:`. `value:` only for `SEND_KEYS` and `SELECT_BY_TEXT`.
5. **`CLEAR`, then `SEND_KEYS`.** Dropdowns use `SELECT_BY_TEXT` with the option text exactly as in the crawl.
6. **Selectors only from the crawl, and unique.** Prefer `#id` → `[name=…]` → `[aria-label=…]` → `a[href="/fixed/path"]` → text. A crawl `sel` that is only a shared class (`button.btn`, `a.card`, `button.nav-link`) matches many elements, so add the visible text: `button:has-text("Search")`, `a.card:has-text("Combination Pliers")`. Text selectors (`text=…`, `:has-text(…)`) match by *contains* and wait on the **first** match, which may be a hidden copy (a closed menu item, a hidden duplicate label): add `>> visible=true` to waits and checks on text that can appear more than once. Exception: an element that appears only after an action (cart badge, toast, results caption) may come from the first run or a known pattern; say so.
7. **End by asserting the outcome** the user asked about, with a check that would **fail if the action did nothing**. **Look it up first:** `get_crawl_digest(target, page=<starting page>, text=<what you'd check>)`. Anything the starting page already shows (a card, the header, any text on `body`) is **not allowed**, whatever the reason. Check what the action creates instead: a results caption or count, a toast, a changed badge, or a result that isn't on the starting page. On Toolshop the home page shows every pliers card, so a search test searches `saw` and ends on the Circular Saw card (or on `[data-test="search-caption"]`). The fail-proof (section 5, item 5) breaks that outcome. A screenshot is not a check.
8. **Logins are `{{username}}`/`{{password}}`** from the environment's saved login. Never invent or type a password.
9. **Playwright only, for now.** Every UI run uses `drivers=["PLAYWRIGHT"]`, and every UI test is saved with `driver="PLAYWRIGHT"`. Never run or save a UI test for `WEBDRIVER`, even if the user asks: say *"Web tests run on Playwright for now; WebDriver isn't supported yet."* and run it on Playwright. The two engines don't behave the same yet (`:has-text()` fails on WebDriver; a page that never loads passes there).

`target` always means the target's **id** from `get_working_context` (or `list_targets`). Details, examples and commands: `reference.md` in this skill's folder. Read it once before drafting the first test.

## 1. Which app, project and environment: one call

**The user named an app, a project or an address:** call `get_working_context(application=…)`, `get_working_context(project=…)` or `get_working_context(url=…)`. One call returns the project, its environments (each with `loginSaved`), their targets (`id`, `baseUrl`, `appTag`, `targetType`, and for web targets the latest `crawl`: when, pages, elements) and the project's applications. Use those ids for every later call; don't list anything else.
- **`CHOOSE_PROJECT`:** show the `candidates` as a numbered list and ask. **Never pick one yourself.**
- **`NOT_FOUND`:** offer *"N. A new app at <address>"*, which hands off to `project-setup`.

**The user named nothing:** call `list_applications()`. On a small instance it lists the apps; show those with a web target as **name**. On a large one it answers `TOO_MANY_TO_LIST`: then ask *"Which app do you want to test? Paste its address or its name."*, and call `get_working_context` with the answer.

**Never call `list_targets()` or `list_applications()` hoping for everything:** they refuse a whole large instance, and that is what they are meant to do.

**Older ProofArc** (the server has no `get_working_context`): call `list_applications` and `list_targets(project=…)` once you know the project, and build the same picture from them.

## 2. Confirm the environment and the login

- **Environment:** only environments in the context that have a `WEB_APP` target. Confirm it if there's one; ask if there are several.
- **No login saved** (`loginSaved: false`) and the app needs one: offer *1. Add a login now (you give it; it's saved in ProofArc) 2. Only tests that don't need a login*.

Then say in one line: *"Working on **app** (`host`), project **X**, environment **Y**, target `https://…`."* Use the real **names** from the context (not ids). Never call an environment a project.

## 3. The crawl

- The target's `crawl` in the context says whether one exists and how big it is; `null` means never crawled. To read it: `get_crawl_digest(target, level="index")`, under a second.
- **No crawl yet:** say so and offer *1. Crawl now (1–2 minutes) (recommended) 2. Describe what to test first*. Crawl with `crawl_by_target(target, mode="digest", max_depth=2, max_urls=40)`.
- Once a crawl exists, call `advise_ui(target)` for the testability score.

## 4. Summary and suggestions (one screen)

- **What the app looks like.** One sentence, plus 3 bullets, from the crawl's pages and forms.
- **Testability:** the score and what it means.
- **Up to 6 suggested tests with no overlap.** All "page opens" checks go into **one smoke test**, which opens **each main page** (home, each category, contact, login…) and for each one waits for something specific to that page, then checks its title with `VALIDATE_TITLE`. The site header or menu proves nothing, because it's on every page. A journey is one test. **Each item names the check it ends with** (*"→ cart shows 1"*). Each item says what it changes (*nothing*, *this browser's cart*, *sends data*). Never offer purchases, deletions or sign-ups unless asked. Edge cases only where the crawl shows the input exists.
- **Close with:** *"Pick tests (`1,3`), `all`, or describe your own scenario."*

The user may also type `find <text>`, `show <page>`, `scenario <words>`, `where` or `done`. See `reference.md`, Commands.

## 5. Build each chosen test

**Never call `create_ui_test_from_yaml` or `run_ui_test` in the same reply as the plan.** The order is always: plan → the user answers **1** → create and run. A test the user asks for that isn't on your list ("build the search test") gets the same treatment: draft its plan and stop. If you can't build what they named, say so and offer the closest test; don't build a different one.

1. Once per session, before the first draft: `get_tool_gotchas("create_ui_test_from_yaml")`. These are the platform's rules for UI tests, and they are as binding as the Test rules here. Then fetch only the elements the test needs: `get_crawl_digest(target, page=…, text=…, type=…)`.
2. Draft the YAML, check it against the **Test rules**, and run `validate_ui_test_yaml`. Show the plan **in plain words** and **stop. Don't create anything until the user answers**: *open home → type `saw` in Search → press Search → check the **Circular Saw** card appears. **Fails if search did nothing:** the crawl shows Circular Saw only on Power Tools, not on the home page. 1. Create it 2. Change something*. Every plan has that **Fails if … did nothing** line, saying the starting page does **not** show the checked thing. If that line would say the thing is already there, the check is wrong: change it before showing the plan (rule 7). **Never show a plan that breaks a Test rule**, not even as one option with a better one beside it: fix it first, then show only the fixed plan. Choosing a test from the list isn't approval of its plan.
3. **A test with that name already exists?** Say so and ask: *1. Run the existing test 2. Create it as "<name> (2)"*. Don't silently reuse it.
4. After the user answers **1**: `create_ui_test_from_yaml(project, yaml_text, name, target="<target id>", tags="from-crawl", driver="PLAYWRIGHT")` (the selectors here, such as `:has-text()`, work on Playwright only), then `run_ui_test(test, environment, target="<target id>", drivers=["PLAYWRIGHT"], wait=True)`. Read `testOutcome`.
5. **Prove it can fail:** change the final expected value with `update_ui_test_from_yaml`, run it (it must fail), restore it, and run again (it must pass).
6. The deliberately broken run shows in the run list as a failure. Name it so nobody mistakes it for a real one: *"run 875 failed on purpose (expected 'Circular Saw X')"*.
7. Report in one line that says **both** results: *✓ Search finds Circular Saw: passed, and fails when the expected name is wrong.* A report that only says "passed" is incomplete.

**If a run fails:** read the failing step's **screenshot** first. Two common causes: the element is in the crawl but hidden when the page loads (the crawl has no visibility flag), or a dialog or tip is on top of it (close it with Cancel or X, never Skip or Save). If it's your mistake (a missing wait, a wrong parameter, a selector not from the crawl, a hidden element, an overlay), fix it and re-run **without asking**. Ask only when the site itself behaves unexpectedly: *"1. The site is wrong, keep it as a finding 2. I misread the page"*. Never loosen a check to make it pass.

## 6. Done

Offer the remaining tests, `run all` (`run_by_tag(tags=["from-crawl"], project, environment, kinds=["ui"])`: it uses each test's saved driver, so first check every test is saved as PLAYWRIGHT with `get_ui_test`; otherwise run them one by one with `run_ui_test(..., drivers=["PLAYWRIGHT"])`), or `done`. Finish with one line: the tests created and passed, the project, the environment, and the tag `from-crawl`.
