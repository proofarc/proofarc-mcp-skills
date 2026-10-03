---
name: crawl-to-tests
description: Use whenever the user asks to create, write, build or suggest UI / web / browser tests for a site or app — "create UI tests for Toolshop", "test my website", "test https://…", "web tests for <app>", "write some web tests for the shop", "what can I test on <site>", "find the screen with …" — even when ProofArc isn't mentioned. The tests are built and run on the connected ProofArc platform (its mcp__…proofarc… tools), not as Playwright/Cypress files on disk, so don't search the local folder for code. Interactive: pick the app, project and environment, read or run the crawl, suggest tests or map the user's scenario, then build, run and prove them. Web UI only. Skip it only when no ProofArc MCP server is configured and the user wants test code written into their own repo.
---

# Web UI tests from the crawl

## FIRST: do exactly this, in this order

1. **Find the ProofArc servers** in your tool list: tool names `mcp__<server>__…` where `<server>` contains `proofarc` (e.g. `proofarc-staging`, `proofarc-prod`). Ignore `claude.ai proofarc`.
2. **More than one?** If the user named an app, you may call `list_applications` on each server. If exactly one server has that app, use it and say *"On proofarc-…:"*. Otherwise your **first reply is only this question**, with no other tool calls before it:
   > Which ProofArc do you want to work in?
   > 1. **proofarc-staging**
   > 2. **proofarc-prod**

   Use the real names you found (the ones above are only examples), then wait. `AskUserQuestion` is fine for this question. **One server:** use it without asking. **None:** follow the `connect` skill. **Configured but failed to connect:** ask the user to run `/mcp` → Reconnect.
3. **Load that server's tools with one `ToolSearch`:** `select:` followed by `mcp__<server>__` plus each of `list_applications`, `list_application_projects`, `list_environments`, `list_targets`, `list_environment_credentials`, `get_crawl_digest`, `crawl_by_target`, `advise_ui`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `update_ui_test_from_yaml`, `run_ui_test`, `get_execution_status`, `find_ui_tests`, `get_crawl_results`, `list_ui_test_actions`, `find_playbooks`, `add_environment_credential`, `set_target_auth`, `run_by_tag`.
4. **Call them as tools.** Never reach ProofArc through Bash, curl or Python, and never ask the user how to call tools. Don't use Bash to print status messages either; just write the text.

**Every reply ends with numbered choices.** Ask one thing per reply and mark a sensible default *(recommended)*.

## Test rules (check every plan against these yourself; don't ask the user)

1. **No record ids** in a URL or selector (`/product/01M3…`). Reach records through the UI from a real entry point (home, category, search) and click them **by visible name** (`a:has-text("Combination Pliers")`). Only fixed routes (`/contact`, `/category/hand-tools`) may be opened directly.
2. **Wait for that page's content before every interaction:** `WAIT_FOR_VISIBLE` on a form, list or heading of that page. When the page loads data, wait for the data itself (a list row, a known item), not a search box or toolbar that appears before it. Set the wait time **once** in a top-level `config:` block containing `timeout: 15000` (milliseconds; `15` would mean 15 ms), and put `timeout:` on a step only to override it. A top-level `timeout:` or `defaultTimeout:` (outside `config:`) is ignored, and the wait falls back to 30 s.
3. **`{{baseUrl}}/path`**, with the application's `appTag:` at the top. Never the site's URL.
4. **Parameters:** `NAVIGATE_TO` takes `url:`. `VALIDATE_*` and `WAIT_FOR_TEXT` take `expectedText:`. `value:` only for `SEND_KEYS` and `SELECT_BY_TEXT`.
5. **`CLEAR`, then `SEND_KEYS`.** Dropdowns use `SELECT_BY_TEXT` with the option text exactly as in the crawl.
6. **Selectors only from the crawl, and unique.** Prefer `#id` → `[name=…]` → `[aria-label=…]` → `a[href="/fixed/path"]` → text. A crawl `sel` that is only a shared class (`button.btn`, `a.card`, `button.nav-link`) matches many elements, so add the visible text: `button:has-text("Search")`, `a.card:has-text("Combination Pliers")`. Exception: an element that appears only after an action (cart badge, toast) may come from the first run; say so.
7. **End by asserting the outcome** the user asked about, and choose a check that would **fail if the action did nothing**. A search test checks for a result that isn't on the page before the search (or for "Searched for: pliers"), not a product that is already on the home page. The fail-proof (rule in step 5) breaks that outcome. A screenshot is not a check.
8. **Logins are `{{username}}`/`{{password}}`** from the environment's saved login. Never invent or type a password.

`target` always means the target's **id** from `list_targets`. Details, examples and commands: `reference.md` in this skill's folder. Read it once before drafting the first test.

## 1. Which app

Call `list_applications` and `list_targets()` (no arguments: every target, with `applicationId`, `environmentName`, `targetType`, `baseUrl`). Show the apps that have a `WEB_APP` target, each as **name: host, envs**:
> Which app do you want to test?
> 1. **Toolshop web**: `practicesoftwaretesting.com`, env `staging`
> 2. **Shop admin**: `admin.example.com`, envs `dev`, `staging`
> 3. A different app or address

- **The user didn't name an app:** show the whole list as above.
- **The user named an app (by name or host) and exactly one matches:** don't ask. Say *"Toolshop web (`practicesoftwaretesting.com`)"* in one line and go straight to step 2, as if they had picked it from the list.
- **Several match:** show only those, as the list.
- **None match:** show the whole list, plus *"N. A new app at <address>"*, which hands off to `project-setup`.

## 2. Project and environment

- **Project:** `list_application_projects(application)`. Confirm it if there's one; ask if there are several.
- **Environment:** only environments with a web target for this app, taken from the step-1 targets. Show whether each has a login saved (`list_environment_credentials`). Confirm it if there's one; ask if there are several.
- **No login saved** and the app needs one: offer *1. Add a login now (you give it; it's saved in ProofArc) 2. Only tests that don't need a login*.

Then say in one line: *"Working on **app** (`host`), project **X**, environment **Y**, target `https://…`."* Use the real **names** (not ids): the project from `list_application_projects`, the environment from `list_environments`. Never call an environment a project.

## 3. The crawl

- `get_crawl_digest(target, level="index")` reads the stored crawl in under a second.
- **No crawl yet:** say so and offer *1. Crawl now (1–2 minutes) (recommended) 2. Describe what to test first*. Crawl with `crawl_by_target(target, mode="digest", max_depth=2, max_urls=40)`.
- Once a crawl exists, call `advise_ui(target)` for the testability score.

## 4. Summary and suggestions (one screen)

- **What the app looks like.** One sentence, plus 3 bullets, from the crawl's pages and forms.
- **Testability:** the score and what it means.
- **Up to 6 suggested tests with no overlap.** All "page opens" checks go into **one smoke test**, which opens **each main page** (home, each category, contact, login…) and for each one waits for something specific to that page, then checks its title with `VALIDATE_TITLE`. The site header or menu proves nothing, because it's on every page. A journey is one test. **Each item names the check it ends with** (*"→ cart shows 1"*). Each item says what it changes (*nothing*, *this browser's cart*, *sends data*). Never offer purchases, deletions or sign-ups unless asked. Edge cases only where the crawl shows the input exists.
- **Close with:** *"Pick tests (`1,3`), `all`, or describe your own scenario."*

The user may also type `find <text>`, `show <page>`, `scenario <words>`, `where` or `done`. See `reference.md`, Commands.

## 5. Build each chosen test

1. Fetch only the elements it needs: `get_crawl_digest(target, page=…, text=…, type=…)`.
2. Draft the YAML, check it against the **Test rules**, and run `validate_ui_test_yaml`. Show the plan **in plain words** and **stop. Don't create anything until the user answers**: *open home → type `pliers` in Search → press Search → check Pliers appears. 1. Create it 2. Change something*. Choosing a test from the list isn't approval of its plan.
3. **A test with that name already exists?** Say so and ask: *1. Run the existing test 2. Create it as "<name> (2)"*. Don't silently reuse it.
4. After the user answers **1**: `create_ui_test_from_yaml(project, yaml_text, name, target="<target id>", tags="from-crawl")`, then `run_ui_test(test, environment, target="<target id>", drivers=["PLAYWRIGHT"], wait=True)`. Read `testOutcome`.
5. **Prove it can fail:** change the final expected value with `update_ui_test_from_yaml`, run it (it must fail), restore it, and run again (it must pass).
6. Report in one line that says **both** results: *✓ Search finds pliers: passed, and fails when the expected name is wrong.* A report that only says "passed" is incomplete.

**If a run fails:** if it's your mistake (a missing wait, a wrong parameter, a selector not from the crawl), fix it and re-run **without asking**. Ask only when the site itself behaves unexpectedly: *"1. The site is wrong, keep it as a finding 2. I misread the page"*. Never loosen a check to make it pass.

## 6. Done

Offer the remaining tests, `run all` (`run_by_tag(tags=["from-crawl"], project, environment, kinds=["ui"])`), or `done`. Finish with one line: the tests created and passed, the project, the environment, and the tag `from-crawl`.
