---
name: crawl-to-tests
description: Use for ANY request to test a website or web app with ProofArc — "test my website", "test <url>", "create/build/write UI tests", "web tests for <app>", "what can I test on <site>", "suggest tests", "build tests from the crawl", "find the screen with …", or a link to a crawl run. Interactive: picks the application, project and environment, reads or runs the crawl of that site, explains what the app does and how testable it is, suggests scenarios and tests (or maps the user's own scenario onto the crawl), then builds, runs and proves the ones the user picks. Web UI only.
---

# From crawl to web UI tests: an interactive guide

Web UI only. We automate an **application**, so start there, then the **project**, then the **environment** to work in. The environment's **website target** is where the crawl lives and where the tests run.

## Non-negotiable test rules (check every plan against these, without asking the user)

1. **No record ids.** No id from the data in a URL or selector (`/product/01M3…`). Reach records through the UI, starting where a user starts (home, a category, search), and click them **by visible name** (`a:has-text("Combination Pliers")`), never "the first result". Only fixed routes (`/contact`, `/category/hand-tools`) may be opened directly.
2. **Wait for that page's content before every interaction**, using `WAIT_FOR_VISIBLE`/`WAIT_FOR_TEXT` with `timeout:` in **milliseconds** (`15000`). Wait for a form, list or heading of that page, not the site's header.
3. **Addresses are `{{baseUrl}}/path`**, with the application's `appTag:` at the top. Never the site's URL.
4. **Parameters:** `NAVIGATE_TO` takes `url:`. `VALIDATE_*` and `WAIT_FOR_TEXT` take `expectedText:`. `value:` is only for `SEND_KEYS` and `SELECT_BY_TEXT`.
5. **`CLEAR`, then `SEND_KEYS`.** Never `CLICK` a field before typing.
6. **Dropdowns use `SELECT_BY_TEXT`** with the option text copied exactly from the crawl. `SEND_KEYS` fails on a `<select>`.
7. **Selectors only from the crawl**, with one exception: an element that exists only **after** an action (a cart badge, a toast) may be taken from the first run's screenshot or failing step. Say so in the plan.
8. **The test ends by asserting the outcome** the user asked about. A screenshot is evidence, not a check.
9. **Logins** are `{{username}}`/`{{password}}` from the environment's saved login, never literal values.

`target` always means the target's **id** from `list_targets`. Names repeat across environments.
Full selector and parameter detail, a wrong-vs-right example, and the command table are in `reference.md`, in this skill's folder.

**Every reply ends with numbered choices** the user can answer with a number. If the `AskUserQuestion` tool is available, use it. Mark a sensible default *(recommended)*. Ask one thing per reply.

**ProofArc not connected?** A "failed to connect" notice at the start of a session isn't final: the server may only have been unreachable for a moment. Before telling the user anything is unavailable, check whether any `mcp__proofarc…` tools are listed.
- If none are, ask the user to type `/mcp`, pick their ProofArc server and choose **Reconnect**, then continue.
- If it answers 401, use the `connect` skill.
- Ignore a failing `claude.ai proofarc` connector when another ProofArc server works.

**Which ProofArc first.** If more than one ProofArc server is connected (tool names `mcp__<server>__…`), ask which instance to use before anything else, and use only that server's tools from then on. With one server, use it without asking.

**Load the tools in one search at the start** (note that `list_targets` is called with no arguments in step 1), by full name: `select:mcp__<server>__list_applications,mcp__<server>__list_application_projects,…` for `list_applications`, `list_application_projects`, `list_environments`, `list_targets`, `get_crawl_digest`, `crawl_by_target`, `advise_ui`, `find_playbooks`, `get_playbook`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `run_ui_test`, `get_execution_status`, `get_crawl_results`, `set_target_auth`, `list_ui_test_actions`, `update_ui_test_from_yaml`, `add_environment_credential`, `list_environment_credentials`, `run_by_tag`. Short names without the prefix don't match.

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

- `list_environments(project)`. Filter the step-1 `list_targets()` result by `environmentName`; don't call `list_targets` again.
- Offer only environments that have a **`WEB_APP` target bound to this application**. Show each one's target address and whether it has a login saved (`list_environment_credentials(environment)`):
  > 1. **staging**: `https://shop.example.com`, login `qa-user` *(recommended)*
  > 2. **dev**: `https://dev.shop.example.com`, no login
  > 3. New environment
- New environment, or no web target: hand off to `project-setup`.

**Logins, asked now and not later.** If the app has a login page or the crawl hit a login wall, and the chosen environment has **no login saved**, say so here:
> This environment has no login saved, so tests behind the login can't run yet. 1. Add one now (you give the username and password; they're saved in ProofArc, not in tests) 2. Only build tests that don't need a login

For option 1, follow `find_playbooks("authenticated web UI")` (the Authenticated Web UI Flow): the user gives the login, `add_environment_credential`, then `set_target_auth(target, auth_config={"authType": "UI_LOGIN", "credentialTag": …})` so the crawl and the tests can get behind it. Never invent or reuse a password.

Confirm in one line: *"Working on **Toolshop web**, project **X**, environment **Y**, target `https://…`."*
The user can type `where` at any time to change this.

## 4. The crawl of that target

1. `get_crawl_digest(target, level="index")` reads the stored crawl in under a second. It returns the pages, with their element counts, and when the target was crawled.
2. **No stored crawl** (`cached: false`), or it's older than the user wants: offer to crawl.
   - Call `crawl_by_target(target, mode="digest", max_depth=2, max_urls=40)`. It waits until the crawl finishes (1–2 minutes) and returns the digest; say so before starting. If it returns `timedOut`, the crawl is still going: read `get_crawl_digest` again in a minute.
   - **App needs a login:** the target needs one first. Set it up as in step 3 (the Authenticated Web UI Flow), then crawl.
   - After crawling, check that the pages are app routes, not just `/login`.
3. **A run link to an ad-hoc crawl** (one not made from a target) can be read with `get_crawl_results(job_id)`, but it doesn't say where tests should run. Use it only to understand the site; build from the target's crawl.
4. `advise_ui(target)` returns the testability score, band, and examples of controls with no stable id. Call it **only once this target has a crawl**, and pass the target's **id** from `list_targets`, not its name; names repeat across environments. On a target that was never crawled, `advise_ui` can report another environment's crawl of the same address. Don't present that as this target's analysis.

**No crawl at all is a normal start, not a dead end.** The user doesn't need a crawl to begin. Say *"There's no crawl of `<address>` in `<environment>` yet. A crawl takes 1–2 minutes and finds the pages and controls to build tests from."*, then offer:
1. Crawl now *(recommended)*
2. Describe what you want to test first. Take their scenario in their own words, then crawl and map it onto the result.

Never write selectors before a crawl exists.

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
> Pick tests (`1,3`), a scenario (`A`), the whole set (`all`), describe your own scenario, or type `find <text>` to explore.

### How to build the suggested set

Work through this checklist **before** writing the list. Weaker models skip it, so do every step.

1. **One page, one test per behaviour.** List the behaviours the crawl shows: pages opening, search, sort or filter, each form, each journey. Each gets exactly one test.
   - Never suggest two tests that only load the same page.
   - "Page opens with the right title" is never a test of its own. All of those go into **one smoke test** that visits every main page once.
2. **Journeys are tests too.** A scenario that crosses pages (browse → product → add to cart) is one test with several steps. Don't also suggest each of its pages separately.
3. **Each item says what it covers** (pages, feature) and **what it changes**: *nothing*, *this browser's cart only*, or *sends data*. Read-only and browser-only items come first. Never offer purchases, deletions or account creation unless the user asks.
4. **Edge cases only where the crawl shows the input exists.**
   - An empty search is fine if there's a search box. An invalid email is fine if there's an email field.
   - **Never** suggest a case the crawl gives no sign of, such as "payment declined". Check first with `get_crawl_digest(target, text="<word>")` **and** by reading the matching cards' names: the crawl cuts long labels short. For example, Toolshop's "Long Nose Pliers" card ends in "Out…" (out of stock), but a search for "stock" finds nothing.
   - When the expected result isn't in the crawl (what an empty search shows), **ask the user**, or run the test once, show the result, and ask *"Is this right?"* before asserting it.
5. **Every suggestion already obeys the Non-negotiable test rules.**
   - Nothing like "open a specific product directly": products are reached by search or a category, then clicked by name.
   - **Each item names the check it ends with**, for example *"→ the cart shows 1"*, *"→ Pliers is in the results"* or *"→ each field shows its error"*. An item that ends with a click or "check the button" isn't a test yet.
6. **Five or six items at most**, deduplicated. If more behaviours exist, say how many and offer `more`.
7. **Say what the crawl didn't reach**, such as login-only pages or pages past `max_depth`, and offer a deeper crawl or a crawl with a login.

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

The user can type these at any time: `find <text>`, `show <page>`, `stable <page>`, `explain`, `scenario <in your words>`, `test <idea>`, `where`, `fixlist`, `more` and `done`. Each one, and the call behind it, is in `reference.md`, under Commands. They all read the stored crawl with `get_crawl_digest(target, …)` and take under a second. `find` matches a screen's **address** (`page="*<text>*"`) and an element's **label** (`text=`).

### Scenarios in the user's own words

The user can describe a journey instead of picking from the list, for example *"filter products by brand and check the results change"*. You can invite it in any reply: *"…or describe a scenario in your own words."* **Example scenarios you offer must come from the crawl.** Name only pages and controls you've seen in it: *"Filter by brand"* because the crawl has `brand_id` filters, *"Add to cart"* because it has `#btn-add-to-cart`. Label anything that creates data, for example *"Register a new account (creates an account)"*.

When the user describes one:
1. **Split it into steps**, then look each one up in the crawl with `get_crawl_digest(target, page=…, text=…, type=…)`.
2. **Show the mapping**, marking what the crawl covers and what it doesn't:
   > *Filter by brand, results change:*
   > 1. Open **Hand Tools** (`/category/hand-tools`) ✓
   > 2. Tick a brand: `input[name="brand_id"]` ✓ *(the crawl doesn't show which brand is which; I'll pick the first one unless you name one)*
   > 3. Check that the product list changes ✓ (the listing is on the page)
   >
   > 1. Build it 2. Change a step
3. **A step the crawl didn't reach** (a page behind a login, or past the crawl's depth): say so, and offer a deeper crawl, or a crawl with a login. Never invent its selectors.
4. Then continue as for any chosen test (section 7).

## 7. Settle each chosen test (one question per reply)

1. **Follow ProofArc's playbook for it.** Call `find_playbooks(<the user's words>)`.
   - Use "UI Flow — crawl → compose → run" for public pages.
   - Use "Authenticated Web UI Flow" for anything behind a login.
   - Then `get_playbook(id)` and keep to its beats and gotchas.
2. **Fetch just the elements it needs:** `get_crawl_digest(target, page=…, type=…, text=…)`.
3. **Ask the one open detail, as options.** For example: *"Search for which product? 1. Pliers (on the site) 2. Your own"*.
4. **Draft, check, then show the plan in plain words (not YAML).** Before drafting the first test of the session, read `reference.md` in this skill's folder. Check the draft against the **Non-negotiable test rules** and run `validate_ui_test_yaml` on it, so you never offer a test the platform would refuse:
   > *Search finds pliers*: open home → type `pliers` in **Search** → press **Search** → wait → check **Pliers** appears.
   > 1. Create it 2. Change something

## 8. Build, run, prove

### Build and run
1. If the plan changed after §7, run `validate_ui_test_yaml` again. Then `create_ui_test_from_yaml(project, yaml_text, name, target="<target id>", tags="from-crawl")`.
2. `run_ui_test(test, environment, target="<target id>", drivers=["PLAYWRIGHT"], wait=True)`. Read `testOutcome`, not `status`.
3. **Prove it can fail.** Use `update_ui_test_from_yaml` to change the final expected value, run the test and see it fail, then restore it, re-run, and **confirm it's green again** before reporting.
4. Report in one line: *✓ Search finds pliers: passed, and fails when the expected name is wrong.*
5. If it fails, follow "When a run fails" below. Never loosen a check just to make it pass.

### When a run fails: fix your own mistakes, ask only about the site
1. Read the failing step and its message.
2. **If it's a test-writing mistake**, fix it with `update_ui_test_from_yaml` and re-run without asking. That covers a missing wait, a wrong parameter, a selector not from the crawl, a record id, or the wrong action for a dropdown. Then report once: *"Step 7 failed because it didn't wait for the product page; added the wait; ✓ passes now."*
3. **Ask only when the site itself behaves unexpectedly**, with the correct steps in place: *"The page loads but shows no Add to cart button. 1. The site is wrong, keep it as a finding 2. I misread the page, tell me what should happen"*.
4. **Never offer options that break the rules**, such as "use another product id", "skip the wait" or "skip this test" as a fix.

Then offer the remaining tests, `run all` (`run_by_tag(tags=["from-crawl"], project, environment, kinds=["ui"], dry_run=True)` to show what would run, then again without `dry_run`), `report` (hand off to `test-report`), or `done`.


## 9. Done

One line: the tests created and passed, the project and environment, and the tag `from-crawl`. If testability was below 70, offer `fixlist`: adding `data-testid` to those controls makes every test on them sturdier.
