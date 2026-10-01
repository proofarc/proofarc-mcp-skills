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

**Load the tools in one search at the start**, by full name: `select:mcp__<server>__list_applications,mcp__<server>__list_application_projects,…` for `list_applications`, `list_application_projects`, `list_environments`, `list_targets`, `get_crawl_digest`, `crawl_by_target`, `advise_ui`, `find_playbooks`, `get_playbook`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `run_ui_test`, `get_execution_status`. Short names without the prefix don't match.

## 1. Which application

- `list_applications`, then keep the ones with a web interface: `applicationInterfaces` contains `WEB_UI`, or `applicationType` is `WEB_APP`. Also keep any application **with no type**; it may still be a web app (some are saved without one). Ask about those rather than hiding them.
- **The user gave a site address or a run link `…/scans/<n>`:** read the site from it. For a run link, call `get_execution_status(execution_id="<n>", kind="ui_job")` and take `items[0].target`; pass the number as a string. Recommend the application whose targets point at that host.
- Offer the applications as a numbered list, plus *"New application"*.
- New application: hand off to `project-setup`. It asks before creating anything.

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
> **Tests I suggest:**
> 1. Main pages open with the right title *(recommended to start)*
> 2. Search "pliers" shows Pliers (B)
> 3. Product page shows *Add to cart* (A, read-only)
> 4. Wrong password shows an error (C, creates nothing)
> 5. Contact form shows required-field errors (D, sends nothing)
> 6. Sort by price changes the order
>
> Pick tests (`1,2`) or a scenario (`A`), or type `find <text>` to explore.

**Rules:**
- **Every claim comes from the crawl or `advise_ui`.** Say "looks like" for anything you infer.
- **Scenarios cross pages; tests are single checks.** Ask whether a scenario should be one test or several.
- **Read-only first.** Label anything that sends data. Never offer purchases or deletions.
- **Six tests at most per list.** Say what the crawl didn't reach: login-only pages, or pages past `max_depth`.

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
| `more` / `done` | | next suggestions / finish |

## 7. Settle each chosen test (one question per reply)

1. **Follow ProofArc's playbook for it.** Call `find_playbooks(<the user's words>)`.
   - Use "UI Flow — crawl → compose → run" for public pages.
   - Use "Authenticated Web UI Flow" for anything behind a login.
   - Then `get_playbook(id)` and keep to its beats and gotchas.
2. **Fetch just the elements it needs:** `get_crawl_digest(target, page=…, type=…, text=…)`.
3. **Ask the one open detail, as options.** For example: *"Search for which product? 1. Pliers (on the site) 2. Your own"*.
4. **Show the plan in plain words, then confirm:**
   > *Search finds pliers*: open home → type `pliers` in **Search** → press **Search** → wait → check **Pliers** appears.
   > 1. Create it 2. Change something

## 8. Build, run, prove

**Selectors:**
- Only use selectors from the crawl. Prefer unique attributes: `#id`, `input[name="…"]`, `a[href="/exact/path"]`.
- The crawl's `sel` is often a shared class that matches many elements; don't use that.
- Never invent `data-test` selectors.

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

One line: the tests created and passed, the project and environment, and the tag `from-crawl`.
