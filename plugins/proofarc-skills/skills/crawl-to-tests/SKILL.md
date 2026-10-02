---
name: crawl-to-tests
description: Interactive guide for web UI tests built from ProofArc's crawl of an application — pick the application, project and environment, read (or run) the crawl of that environment's website target, explain what the app does and how testable it is, suggest scenarios and tests, answer "find …" questions about screens and elements, then build, run and prove the tests the user picks. Use when the user wants web UI tests for an app, shares a crawl or run link (…/scans/<id>), or says "build tests from the crawl", "what can I test", "suggest tests", "find the screen with …".
---

# From crawl to web UI tests: an interactive guide

Web UI only. We automate an **application**, so start there, then the **project**, then the **environment** to work in. The environment's **website target** is where the crawl lives and where the tests run.

**Every reply ends with numbered choices** the user can answer with a number. If the `AskUserQuestion` tool is available, use it. Mark a sensible default *(recommended)*. Ask one thing per reply.

**ProofArc not connected?** A "failed to connect" notice at the start of a session isn't final: the server may only have been unreachable for a moment. Before telling the user anything is unavailable, check whether any `mcp__proofarc…` tools are listed.
- If none are, ask the user to type `/mcp`, pick their ProofArc server and choose **Reconnect**, then continue.
- If it answers 401, use the `connect` skill.
- Ignore a failing `claude.ai proofarc` connector when another ProofArc server works.

**Which ProofArc first.** If more than one ProofArc server is connected (tool names `mcp__<server>__…`), ask which instance to use before anything else, and use only that server's tools from then on. With one server, use it without asking.

**Load the tools in one search at the start** (note that `list_targets` is called with no arguments in step 1), by full name: `select:mcp__<server>__list_applications,mcp__<server>__list_application_projects,…` for `list_applications`, `list_application_projects`, `list_environments`, `list_targets`, `get_crawl_digest`, `crawl_by_target`, `advise_ui`, `find_playbooks`, `get_playbook`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `run_ui_test`, `get_execution_status`. Short names without the prefix don't match.

## 1. Which application: shown by its address

People know their app by its address, not by its ProofArc name. These are MCP tools: call them directly as tools, not through the shell. Make two calls at once:
- `list_applications`
- `list_targets()` with no arguments. It returns **every** target with its `applicationId`, `environmentName`, `targetType` and `baseUrl`, in under a second.

Join them, and keep the applications that have a `WEB_APP` target (or a web type or interface). Show **the application's name as it is**, then its **target host**, then the **environments that have that target**. Those environments are where it can run:

> Which app do you want to test?
> 1. **Toolshop web (trial)**: `practicesoftwaretesting.com`, env `toolshop-trial`
> 2. **user-service-ui**: `user-service-ui-devdemo.proofarc.ai`, envs `production`, `qa454-lite`
> 3. **coppel**: `www.coppel.com`, env `dev`
> 4. A different app or address
>
> Or just paste the address.

- **The user pastes an address**, or gave one earlier, or a run link `…/scans/<n>`: match it against the targets' `baseUrl` by host, ignoring `www.` and any trailing `/`.
  - For a run link, call `get_execution_status(execution_id="<n>", kind="ui_job")` and use `items[0].target`; send the number as a string.
  - One match: confirm it in a line. Several (the same site in several applications): show only those.
- **No match:** it's a new application. Hand off to `project-setup`, which asks before creating anything.
- A web target with no application (`applicationId` empty) is listed under its address too, marked *"not linked to an application"*.

## 2. Which project

- `list_application_projects(application)` returns the projects that use this application.
- One project: confirm it in a line. Several: offer them. None: hand off to `project-setup`.

## 3. Which environment

- `list_environments(project)`, then `list_targets(environment)` for each one.
- Offer only environments that have a **`WEB_APP` target bound to this application**. Show each one's target address and whether it has a login saved:
  > 1. **staging**: `https://shop.example.com`, login `qa-user` *(recommended)*
  > 2. **dev**: `https://dev.shop.example.com`, no login
  > 3. New environment
- New environment, or no web target: hand off to `project-setup`.

**Logins, asked now and not later.** If the app has a login page or the crawl hit a login wall, and the chosen environment has **no login saved**, say so here:
> This environment has no login saved, so tests behind the login can't run yet. 1. Add one now (you give the username and password; they're saved in ProofArc, not in tests) 2. Only build tests that don't need a login

For option 1, use `project-setup` to add the login, then `set_target_auth` (`UI_LOGIN`) so the crawl can get behind it. Never invent or reuse a password.

Confirm in one line: *"Working on **Toolshop web**, project **X**, environment **Y**, target `https://…`."*
The user can type `where` at any time to change this.

## 4. The crawl of that target

1. `get_crawl_digest(target, level="index")` reads the stored crawl in under a second. It returns the pages, with their element counts, and when the target was crawled.
2. **No stored crawl** (`cached: false`), or it's older than the user wants: offer to crawl.
   - Call `crawl_by_target(target, mode="digest", max_depth=2, max_urls=40)`. It takes 1–2 minutes; say so before starting.
   - **App needs a login:** the target needs one first. Follow the playbook from `find_playbooks("authenticated web UI")`: a saved login, then `set_target_auth` with `authType: "UI_LOGIN"`. Never type a password yourself.
   - After crawling, check that the pages are app routes, not just `/login`.
3. **A run link to an ad-hoc crawl** (one not made from a target) can be read with `get_crawl_results(job_id)`, but it doesn't say where tests should run. Use it only to understand the site; build from the target's crawl.
4. `advise_ui(target)` returns the testability score, band, and examples of controls with no stable id.

## 5. First reply: what the app is, how testable, what to test

One screen. For example, for Toolshop:

> **Toolshop web**, environment **toolshop-trial** (`https://practicesoftwaretesting.com`), crawled today: 40 pages, 6 forms.
>
> **What it looks like:** an online hardware shop.
> - Products are in 4 categories, with product pages (`/product/…`) that have *Add to cart*.
> - Search and sorting are on the listing pages.
> - It has login, register and a contact form, and a rentals section.
>
> **Testability: 51/100 (needs work).** 440 of 855 controls have a stable id. The shop's main controls do (`#btn-add-to-cart`, `#email`, `#password`); navigation links and the Search button don't, so those tests depend on their text.
>
> **Scenarios:**
> - A. Browse a category → open a product → add it to the cart
> - B. Search → open a product
> - C. Wrong password → error
> - D. Contact form with missing fields → required errors
>
> **Suggested set: 5 tests, no overlap.**
> 1. **Smoke**: home, 4 categories, contact and login each open with the right title *(one test, every main page once; recommended to start)*
> 2. **Journey A**: category → product → *Add to cart* → the cart count goes to 1 *(changes only this browser's cart)*
> 3. **Search**: "pliers" lists Pliers *(home page search)*
> 4. **Sort**: on a category page, Price (Low - High) puts the cheapest first
> 5. **Contact validation**: send empty → each required field shows its error *(sends nothing)*
>
> **Edge cases the crawl supports:** empty search (the search box is there; I'll ask what it should show). Login is not covered: the crawl didn't go behind it.
>
> Pick tests (`1,3`), take the whole set (`all`), or type `find <text>` to explore.

### How to build the suggested set

Work through this checklist **before** writing the list. Weaker models skip it, so do every step.

1. **One page, one test per behaviour.** List the behaviours the crawl shows: pages opening, search, sort or filter, each form, each journey. Each gets exactly one test.
   - Never suggest two tests that only load the same page.
   - "Page opens with the right title" is never a test of its own. All of those go into **one smoke test** that visits every main page once.
2. **Journeys are tests too.** A scenario that crosses pages (browse → product → add to cart) is one test with several steps. Don't also suggest each of its pages separately.
3. **Each item says what it covers** (pages, feature) and **what it changes**: *nothing*, *this browser's cart only*, or *sends data*. Read-only and browser-only items come first. Never offer purchases, deletions or account creation unless the user asks.
4. **Edge cases only where the crawl shows the input exists.**
   - An empty search is fine if there's a search box. An invalid email is fine if there's an email field.
   - **Never** suggest a case the crawl gives no sign of, such as "out of stock" or "payment declined". Check with `get_crawl_digest(target, text="<word>")` first. If it finds nothing, don't suggest it.
   - When the expected result isn't in the crawl (what an empty search shows), **ask the user**, or run the test once, show the result, and ask *"Is this right?"* before asserting it.
5. **Five or six items at most**, deduplicated. If more behaviours exist, say how many and offer `more`.
6. **Say what the crawl didn't reach**, such as login-only pages or pages past `max_depth`, and offer a deeper crawl or a crawl with a login.

### When the user asks to improve or trim the set

Apply the same checklist to the list you suggested, and answer with **the changed list itself**, not advice:
- merge overlaps
- fold title checks into the smoke test
- drop anything the crawl can't support

Then ask *"Use this set? 1. Yes 2. Change something"*.

**Rules:**
- **Every claim comes from the crawl or `advise_ui`.** Say "looks like" for anything you infer.
- If a scenario could be one test or several, ask which.

## 6. Commands, any time

All of these read the target's stored crawl with `get_crawl_digest(target, …)`. Each takes under a second.

| the user types | call | show |
|---|---|---|
| `find <text>` | `page="*<text>*", level="index"`, then `text="<text>"` | screens whose address contains it, then elements whose label contains it, each with its page |
| `show <page>` | `page="<path or *part*>"`, then `type="form"`, `type="input"`, `type="button"` | that page's fields and buttons, marking which have stable ids |
| `stable <page>` | `page=…, stable_only=true` | only controls with an id a developer chose |
| `explain` | the step 4 results you already have | page groups with counts, forms by page, testability examples |
| `test <screen or idea>` | | 2–3 test ideas for it |
| `where` | | go back to steps 1–3 |
| `fixlist` | `advise_ui(target, full=true)` | a list for the developers: each control with no stable id, its page, and the `data-testid` to add, ranked by how many tests would use it |
| `more` / `done` | | next suggestions / finish |

## 7. Settle each chosen test (one question per reply)

1. **Follow ProofArc's playbook for it.** Call `find_playbooks(<the user's words>)`.
   - Use "UI Flow — crawl → compose → run" for public pages.
   - Use "Authenticated Web UI Flow" for anything behind a login.
   - Then `get_playbook(id)` and keep to its beats and gotchas.
2. **Fetch just the elements it needs:** `get_crawl_digest(target, page=…, type=…, text=…)`.
3. **Ask the one open detail, as options.** For example: *"Search for which product? 1. Pliers (on the site) 2. Your own"*.
4. **Show the plan in plain words, not YAML, then confirm.** Run `validate_ui_test_yaml` on the draft before showing the plan, so you never offer a test the platform would refuse:
   > *Search finds pliers*: open home → type `pliers` in **Search** → press **Search** → wait → check **Pliers** appears.
   > 1. Create it 2. Change something

## 8. Build, run, prove

**Selectors:**
- **No record ids in a test.** A URL or selector containing an id from the data (`/product/01M3FZ5CD4BXK3PFN6RCYZ3SXY`, `#order-4711`) breaks when the data changes. Get to the record **through the UI**: open the listing, then click the item by its visible name (`a:has-text("Combination Pliers")`). Its name is unique and readable. A bare pattern like `a[href^="/product/"]` matches every product, and clicks only the first one on Playwright, which differs from WebDriver.
- **Never use framework state or generated classes**: `ng-untouched`, `ng-pristine`, `ng-valid`, `is-active`, `Mui-focused`, or hashed names like `css-1x2y3z`. They change as the user interacts or with every build. `form.ng-untouched` stops matching the moment a field is touched.
- **Order of preference:** `#id` → `[name="…"]` → `[aria-label="…"]` → `a[href="/exact/path"]` (fixed routes only) → visible text. Say in the plan when a step depends on text.
- Only use selectors from the crawl. Prefer unique attributes: `#id`, `input[name="…"]`, `a[href="/exact/path"]`.
- The crawl's `sel` is often a shared class that matches many elements; don't use that.
- Never invent `data-test` selectors.

**Addresses: always `{{baseUrl}}`, never the site's URL.**
- Write `url: "{{baseUrl}}/category/hand-tools"`, not `https://practicesoftwaretesting.com/category/hand-tools`.
- Put the application's app tag at the top (`appTag: "<appTag>"`). Then `{{baseUrl}}` resolves to the environment's target at run time, and the same test runs on dev, staging or prod unchanged.
- `{{baseUrl}}` has no trailing slash, so always write `{{baseUrl}}/path`.

**Parameters each action really takes** (the validator refuses the wrong ones):
- `NAVIGATE_TO` takes `url:`.
- Waits take `timeout:` in **milliseconds** (`10000`). A `value: "5"` on a wait does nothing and falls back to 30 s.
- `VALIDATE_TITLE`, `VALIDATE_TEXT` and `WAIT_FOR_TEXT` take `expectedText:`. `value:` is only for typing (`SEND_KEYS`).
- **Dropdowns (`<select>`) use `SELECT_BY_TEXT`.** Set `value:` to the option's visible text **copied character for character from the crawl**. Toolshop's option is `"Price (Low - High)"` with a plain hyphen; a dash (`–`) or extra spaces won't match, and the step times out.
  - `SEND_KEYS` fails on a select.
  - The crawl may list a dropdown as `type: input`, so treat a sort, filter or category control as a dropdown.
  - If the crawl doesn't show the full option text, ask the user for it. Don't fall back to `SELECT_BY_INDEX`: option order changes, and the test would quietly pick something else.
  - **Custom dropdowns**, built from `div`s rather than a `<select>`, don't work with the `SELECT_*` actions. `CLICK` the control, then `CLICK` the option by its text.
- **Wait before checking a title.** Single-page apps set the page title after the page loads, so `VALIDATE_TITLE` straight after `NAVIGATE_TO` can read the generic title. Wait for an element on that page first, as in the example. The same goes for validation messages: `WAIT_FOR_TEXT` before asserting them.
- **Other actions** (hover, double-click, read a value, check an attribute, frames, alerts, uploads): `list_ui_test_actions` gives each action's required parameters. Check it before using an action not listed here.
- **More detail on one element**, such as its alternate selectors or xpath: use `get_crawl_results(job_id, element=<selector>)` rather than re-crawling at a higher level.
- **Wait for something on the page you navigated to**, such as its form, list or heading from the crawl, not the site's header or menu. A header element is on every page, so waiting for it proves nothing.

Example (validated):
```yaml
name: "Main pages open with the right title"
appTag: "toolshop-web-trial"
steps:
- action: NAVIGATE_TO
  url: "{{baseUrl}}/category/hand-tools"
- action: WAIT_FOR_VISIBLE
  selector: '[aria-label="Sort products"]'
  timeout: 10000
- action: VALIDATE_TITLE
  expectedText: "Hand Tools - Practice Software Testing - Toolshop - v5.0"
- action: TAKE_SCREENSHOT
  filename: "hand-tools"
```

**Steps:**
- Navigate, wait, act, wait, then assert the **outcome**, not just a click.
- `CLEAR` before `SEND_KEYS`.
- Wait times go in `timeout:` (milliseconds).
- `TAKE_SCREENSHOT` early.
- `WAIT_FOR_URL` isn't valid; use `VALIDATE_URL`.

**Logins:** `{{username}}`/`{{password}}` from the environment's saved login. Never literal values.

**Then:**
1. `validate_ui_test_yaml`, then `create_ui_test_from_yaml(project, yaml_text, name, target=<target>, tags="from-crawl")`.
2. `run_ui_test(test, environment, drivers=["PLAYWRIGHT"], wait=True)`. Read `testOutcome`, not `status`.
3. Prove the test can fail, as in `run-test`.
4. Report in one line: *✓ Search finds pliers: passed, and fails when the expected name is wrong.*
5. If it fails, the run's result stands. Show the step and its message, then ask: *"1. The site is wrong, keep it as a finding 2. The test is wrong, fix it"*. Never loosen a check just to make it pass.

Then offer the remaining tests, `run all` (by the `from-crawl` tag), `report` (hand off to `test-report`), or `done`.

## 9. Done

One line: the tests created and passed, the project and environment, and the tag `from-crawl`. If testability was below 70, offer `fixlist`: adding `data-testid` to those controls makes every test on them sturdier.
