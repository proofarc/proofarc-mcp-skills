# crawl-to-tests: reference

Detail for `SKILL.md`. The rules at the top of `SKILL.md` win if anything here seems to differ.

## Commands

All of these read the target's stored crawl with `get_crawl_digest(target, …)`. Each takes under a second.

| the user types | call | show |
|---|---|---|
| `find <text>` | `page="*<text>*", level="index"`, then `text="<text>"` | screens whose address contains it, then elements whose label contains it, each with its page |
| `show <page>` | `page="<path or *part*>"`, then `type="form"`, `type="input"`, `type="button"` | that page's fields and buttons, marking which have stable ids |
| `stable <page>` | `page=…, stable_only=true` | only controls with an id a developer chose |
| `explain` | the SKILL.md step 4 results you already have | page groups with counts, forms by page, testability examples |
| `scenario <in your words>` | `get_crawl_digest` per step (`page=`, `text=`, `type=`) | the user's journey mapped onto the crawl, step by step (*Scenarios in the user's own words*, below) |
| `test <screen or idea>` | | 2–3 test ideas for it |
| `where` | | go back to SKILL.md steps 1–2 |
| `fixlist` | `advise_ui(target, full=true)` | a list for the developers: each control with no stable id, its page, and the `data-testid` to add, ranked by how many tests would use it |
| `more` / `done` | | next suggestions / finish |

## Wrong vs right, the same journey
❌ **Wrong** (built in a real trial; it broke):
```yaml
- action: NAVIGATE_TO
  url: "{{baseUrl}}/product/01M3FZ5CD4BXK3PFN6RCYZ3SXY"   # record id: breaks when the data changes
- action: CLICK
  selector: "#btn-add-to-cart"                            # no wait: the page isn't loaded yet
- action: TAKE_SCREENSHOT                                 # no check: proves nothing
```

✅ **Right** (validated, passed on Playwright, and failed when the expected count was changed to 7):
```yaml
name: "Search pliers, open Combination Pliers, add to cart"
appTag: "toolshop-web-trial"
config:
  timeout: 15000
steps:
- action: NAVIGATE_TO
  url: "{{baseUrl}}/"
- action: WAIT_FOR_VISIBLE
  selector: "#search-query"
- action: CLEAR
  selector: "#search-query"
- action: SEND_KEYS
  selector: "#search-query"
  value: "pliers"
- action: CLICK
  selector: 'button:has-text("Search")'
- action: WAIT_FOR_TEXT
  selector: '[data-test="search-caption"]'
  expectedText: "pliers"
# ^ this caption is the search's proof (the home page has none); the click below continues the journey to the cart
- action: WAIT_FOR_VISIBLE
  selector: 'a.card:has-text("Combination Pliers")'
- action: CLICK
  selector: 'a.card:has-text("Combination Pliers")'
- action: WAIT_FOR_VISIBLE
  selector: "#btn-add-to-cart"
- action: CLICK
  selector: "#btn-add-to-cart"
- action: WAIT_FOR_VISIBLE
  selector: 'a[href="/checkout"]'
- action: VALIDATE_TEXT
  selector: 'a[href="/checkout"]'
  expectedText: "1"
- action: TAKE_SCREENSHOT
  filename: "cart-has-one"
```
The cart link `a[href="/checkout"]` isn't in the crawl: it only appears **after** something is added. For an outcome like that, run the test once, look at the result (a screenshot or the failing step's message), and then add the check. Say in the plan that this one selector came from the run, not the crawl.

## Selectors and parameters

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
- **Wait time: set it once.** `config:` → `timeout: 15000` (**milliseconds**: `config.timeout: 15` would mean 15 ms) at the top of the test applies to every wait and navigation. Put `timeout:` on a single step only to override it there. A top-level `timeout:` or `defaultTimeout:` outside `config:` is ignored (the wait falls back to 30 s), and so is a wait time given as `value:`. On a **step** `timeout:` only, 600 or less is read as seconds (`timeout: 5` = 5 s); `config.timeout` is always milliseconds.
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
name: "Hand Tools page opens with the right title"
appTag: "toolshop-web-trial"
config:
  timeout: 15000
steps:
- action: NAVIGATE_TO
  url: "{{baseUrl}}/category/hand-tools"
- action: WAIT_FOR_VISIBLE
  selector: '[aria-label="Sort products"]'
- action: VALIDATE_TITLE
  expectedText: "Hand Tools - Practice Software Testing - Toolshop - v5.0"
- action: TAKE_SCREENSHOT
  filename: "hand-tools"
```

**Steps:**
- Navigate, wait, act, wait, then assert the **outcome**, not just a click.
- `CLEAR` before `SEND_KEYS`.
- Wait time once in `config: timeout:`; a step's own `timeout:` only to override it.
- **A tip or banner on every page** (e.g. a "Got it" pop-up, which shows up on every screenshot): dismiss it once, right after login (`WAIT_FOR_VISIBLE`, `CLICK`, `WAIT_FOR_INVISIBLE`), but only if dismissing it changes nothing on the account (it only sets a cookie or local-storage flag and sends no request; if unsure, ask the user). Each run starts a fresh browser, so the pop-up shows on every run (to confirm per app: if it only sometimes appears, the `WAIT_FOR_VISIBLE` on it would fail the test).
- `TAKE_SCREENSHOT` early.
- `WAIT_FOR_URL` isn't valid; use `VALIDATE_URL`.

## Common actions and their parameters

Call `list_ui_test_actions` for the full, current list.

| Action | Parameters |
|---|---|
| `NAVIGATE_TO` | `url` |
| `NAVIGATE_BACK`, `NAVIGATE_FORWARD`, `REFRESH` | — |
| `CLICK`, `DOUBLE_CLICK`, `RIGHT_CLICK` | `selector` |
| `SEND_KEYS` | `selector`, `value` |
| `WAIT_FOR_VISIBLE`, `WAIT_FOR_CLICKABLE`, `WAIT_FOR_ELEMENT`, `WAIT_FOR_INVISIBLE` | `selector`, optional `timeout` (overrides `config.timeout`) |
| `WAIT_FOR_TEXT` | `selector`, `expectedText`, optional `timeout` |
| `VALIDATE_TITLE`, `VALIDATE_URL` | `expectedText` (contains) |
| `VALIDATE_TEXT` | `selector`, `expectedText` (contains) |
| `VALIDATE_VISIBLE`, `VALIDATE_NOT_VISIBLE`, `VALIDATE_ELEMENT_VISIBLE`, `VALIDATE_ELEMENT_EXISTS` | `selector` |
| `VALIDATE_ATTRIBUTE` | `selector`, `attribute`, `expectedText` |
| `EXECUTE_JS` | `script` |
| `TAKE_SCREENSHOT` | `filename` (optional) |

## Errors and what to do

| The tool says | Fix |
|---|---|
| `create_application` … `project` field required | Create the project first, then the application. |
| `Target URL is required` / `Multiple WEB_APP targets … match this test` | Pass `target` (the target id as a string) to `run_ui_test`. |
| `references {{username}}/{{password}} but no credentials are available` | The environment needs a credential; pass its tag as `credential_tag`. Ask the user for the login — never invent one. |
| `has no driver set … specify drivers` | Pass `drivers=["PLAYWRIGHT"]`. |
| `NAVIGATE_TO` fails in under a second with `ERR_NAME_NOT_RESOLVED at https://site.compath` | Missing slash: write `{{baseUrl}}/path`. |
| `DUPLICATE_BASE_URL` / `DUPLICATE_TARGET` | A website target for that address already exists in the environment — use it. |
| `UNKNOWN_PARAMETER … Its parameters are: …` | Use the parameter names the error lists. |
| `missing_required` with `ask_user` and `candidates` | Show the user the candidates and ask; then call again with their answer. |
| Crawl found almost nothing | Login page (add a credential), bot protection (HTTP 403 or a captcha — ask for a staging URL), or the crawl was too shallow (raise `max_depth`). |
| A test is red | Report the failing step and message. Don't change the expectation to make it pass. |

## More detail for SKILL.md steps

### Step 1: app by address or run link
- When the user pastes an address, match it against the targets' `baseUrl` by host, ignoring `www.` and any trailing `/`. If several apps match, show only those.
- **A run link `…/scans/<n>`:** call `get_execution_status(execution_id="<n>", kind="ui_job")` and use `items[0].target`. Send the number **as a string**.
- **An ad-hoc crawl** (not made from a target) can be read with `get_crawl_results(job_id)`, but it doesn't say where tests should run. Use it only to understand the site.
- A web target with no application is listed under its address, marked *"not linked to an application"*.

### Step 2: adding a login
Follow `find_playbooks("authenticated web UI")`:
1. The user gives the username and password.
2. Save them with `add_environment_credential(environment, tag, username, password)`.
3. Set the target to sign in with `set_target_auth(target, auth_config={"authType": "UI_LOGIN", "credentialTag": "<tag>"})`.
4. Crawl. Check that the pages found are app routes, not just `/login`.

### Step 3: crawl
- `crawl_by_target` waits until the crawl finishes (1–2 minutes). If it returns `timedOut`, read `get_crawl_digest` again in a minute.
- Call `advise_ui` only after **this** target has a crawl, and pass its id. On a target that was never crawled, it can report another environment's crawl of the same address.

### Step 4: building the suggested set
- **Edge cases:** check with `get_crawl_digest(target, text="<word>")` **and** by reading card names, because the crawl cuts long labels short. Toolshop's "Long Nose Pliers" card ends in "Out…" (out of stock); a search for "stock" finds nothing.
- When the expected result isn't in the crawl (what an empty search shows), ask the user, or run the test once and ask *"Is this right?"* before asserting it.
- When the user asks to trim or improve the set, reply with **the changed list itself**: merge overlaps, fold title checks into the smoke test, and drop anything the crawl can't support.
- Every claim about the app comes from the crawl or `advise_ui`. Say "looks like" for anything you infer.

### Scenarios in the user's own words
1. Split the scenario into steps, and look each one up with `get_crawl_digest(target, page=…, text=…, type=…)`.
2. Show the mapping with ✓ for each step the crawl covers, plus any open question. Offer *1. Build it 2. Change a step*.
3. For a step the crawl didn't reach (behind a login, or past the crawl's depth), say so and offer a deeper crawl or a crawl with a login. Never invent its selectors.
4. Example scenarios you offer must name only pages and controls the crawl has.

### `fixlist`
`advise_ui(target, full=true)` gives the controls with no stable id and the `data-testid` to add to each. Offer this at the end when testability is below 70.
