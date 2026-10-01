---
name: crawl-to-tests
description: Interactive guide from a finished ProofArc crawl to working UI tests — summarise what the crawl found and what the app appears to do, suggest user scenarios and tests, answer "find …" questions about screens and elements, then build, run and prove the tests the user picks. Use when the user shares a crawl or run link (…/scans/<id>), a crawl job id, or says "build tests from the crawl", "what can I test on this site", "suggest tests", "find the screen with …".
---

# From crawl to tests: an interactive guide

The crawl already knows the site: its pages, forms, inputs and buttons. Use it to explain the app, suggest what to test, and answer questions about it. The user chooses; you build.

**Pace:** the first answer comes within about 20 seconds.
- **Load tools in one go.** Use a single tool search for `get_execution_status`, `get_crawl_results`, `ensure_crawl_for_authoring`, `validate_ui_test_yaml`, `create_ui_test_from_yaml`, `run_ui_test`, `get_project_setup_status`.
- **Then make at most three calls** before speaking: the crawl id, the page list, the forms.
- **Read element details only for what the user picks or asks about.**

**Every reply ends with numbered choices** the user can answer with a number. If the `AskUserQuestion` tool is available, use it. Mark a sensible default *(recommended)*. Between choices the user can type a command (section 4) at any time.

## 1. Find the crawl (one call)

- **A run link `…/scans/<n>`:** call `get_execution_status(execution_id="<n>", kind="ui_job")`.
  - Pass the number **as a string**, `"149"`, not `149`. A bare number is refused with a message about UUIDs; ignore that message and resend it as a string.
  - The response's `jobId` is the crawl id, and `items[0].target` is the site.
- **A job id:** use it directly.
- **Only a site address:** call `ensure_crawl_for_authoring(url, level="index")`. It reuses a crawl from the last 24 hours, or runs a new one.

**Never swap in another crawl.** If this one can't be read, say so and ask.

## 2. Read the summary (two calls)

- `get_crawl_results(job_id)` returns:
  - the page list (url, title, element count)
  - `stats`: pages, forms, inputs, buttons, links
  - page speed: median load and first paint
  - `loginWall` / `authenticated`
  - `maxDepth`
- `get_crawl_results(job_id, type="form")` returns every form and the pages it appears on.

Work out the rest yourself from URL patterns, titles and form fields. Don't fetch more yet.

## 3. First reply: summary, what the app does, scenarios, tests

Keep it to one screen. The shape, for a real crawl:

> **Toolshop** (practicesoftwaretesting.com), crawled 25 Sep: 40 pages, 10 forms, 134 inputs, pages load in about 0.2 s, no login needed to browse.
>
> **What it looks like:** an online hardware shop.
> - Products are in 4 categories: Hand Tools, Power Tools, Other, Special Tools.
> - There are product pages (`/product/<id>`) with *Add to cart*, a search on the home page, and sorting.
> - It has accounts (login, register), a contact form, and a rentals section.
>
> **Scenarios a user goes through:**
> - A. Browse a category → open a product → add it to the cart
> - B. Search for a product → open it
> - C. Sign in with a wrong password → see the error
> - D. Send the contact form with fields missing → see what's required
>
> **Tests I suggest:**
> 1. Main pages open with the right title (home, 4 categories, contact, login) *(recommended to start)*
> 2. Search "pliers" shows matching products (scenario B)
> 3. Sort by price changes the order (home, categories)
> 4. Wrong password shows an error (scenario C, creates nothing)
> 5. Contact form shows required-field errors (scenario D, sends nothing)
> 6. Product page has *Add to cart* (scenario A, read-only)
>
> Pick tests (e.g. `1,2`) or a scenario (`A`), or type `find <text>` to explore. Before building, I'll ask which project and environment to use.

**Rules:**
- **Claims about the app come only from the crawl.** Say "looks like" for anything you infer. Don't invent features the crawl didn't see.
- **Scenarios are journeys across pages.** Tests are single checks. A scenario becomes one test with several steps, or several tests; ask which the user wants.
- **Read-only first.** Label anything that sends data (*"sends a message"*, *"creates an account"*). Never offer purchases or deletions.
- **Six tests at most per list.** Use `more` for the rest.
- **Say what the crawl didn't cover:** pages behind a login, or a depth limit reached. Offer a deeper crawl, or a crawl with a login, as an option.

## 4. Commands the user can type at any time

| the user types | you do |
|---|---|
| `find <text>` | **Screens:** filter the page list from step 2 yourself, matching `<text>` anywhere in the URL or title, ignoring case. `page_url` only takes a full address, so it can't do partial matches. **Elements:** `get_crawl_results(job_id, text="<text>")`, which matches partial text across all pages. Show both, at most 10 each, numbered. |
| `show <page or number>` | Make three calls to `get_crawl_results(job_id, page_url=<full url>, …)`: one with `type="form"`, one with `type="input"`, one with `type="button"`. List the fields and buttons with their labels, and mark which have stable ids. |
| `explain` | Repeat the summary and what the app looks like, in more detail: page groups with their counts, and which forms appear on which pages. |
| `test <page, element or idea>` | Suggest 2–3 tests for that screen or element, as a numbered list. |
| `more` | The next suggestions. |
| `where` | Change the project or environment (step 5). |
| `done` | Finish (step 8). |

Examples:
- `find cart` lists *Add to cart* (`#btn-add-to-cart`, on the product pages).
- `find rent` lists `/rentals` and its rental pages.
- `show contact` lists the contact form's fields and its Send button.

## 5. Where the tests go: ask before building anything

The summary only reads the crawl. Creating tests needs a **project** and an **environment**, and the user chooses both. Ask the moment they pick their first test, one question per reply, and never choose one silently.

1. **Project:** `list_projects`. Offer the projects as numbered options, plus *"New project"*. Recommend one only if the user named it earlier.
2. **Environment:**
   - `list_environments(project)`, then `list_targets(environment)` for each one.
   - Mark the environments that already have a **website target for the crawled site** (same host as `items[0].target`). Recommend one of those.
   - Show each environment's name, its target address, and whether it has a login saved:
     > Which environment should the tests run in?
     > 1. **staging-ui**: target `https://shop.example.com`, login `qa-user` *(recommended, it targets the crawled site)*
     > 2. **prod-smoke**: target `https://shop.example.com`, no login
     > 3. New environment for this site
   - Option 3, or no environment with a matching target: hand off to `project-setup`. It creates the environment, application and target, and asks before creating them.
3. **Confirm in one line** before the first test: *"Tests go to project **X**, environment **Y**, target `https://…`."*

Ask once per session; every later test reuses the choice. The user can type `where` at any time to change it.

## 6. Settle each chosen test (one question per reply)

1. **Fetch only what it needs:** `get_crawl_results(job_id, page_url=<full url>, type=…, text=…)`.
2. **Ask the one open detail, as options.** For example: *"Search for which product? 1. Pliers (on the site) 2. Hammer 3. Your own"*.
3. **Show the plan in plain words, then confirm:**
   > *Search finds pliers*: open the home page → type `pliers` in **Search** → press **Search** → check **Pliers** appears.
   > 1. Create it 2. Change something
4. **Logins** come from a login saved in the environment (`{{username}}`/`{{password}}`). If there isn't one, ask the user to provide it. Never type or invent one.

## 7. Build, run, prove

1. Use selectors **only from crawl results**. Don't invent `data-test` selectors.
2. `validate_ui_test_yaml`, then `create_ui_test_from_yaml(..., tags="from-crawl")`.
3. Run it, and prove it can fail, as in `run-test`.
4. Report in one line: *✓ Search finds pliers: passed, and fails when the expected name is wrong.*
5. **If it fails, the run's result counts.** Show the step and its message, then ask: *"1. The site is wrong, keep it as a finding 2. The test is wrong, fix it"*. Never loosen a check just to make it pass.

Then offer the remaining suggestions, `run all` (by the `from-crawl` tag), `report` (hand off to `test-report`), or `done`.

## 8. Done

One line: how many tests were created and how many passed, and the tag that finds them (`from-crawl`).
