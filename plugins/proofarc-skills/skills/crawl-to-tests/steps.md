# crawl-to-tests: more detail for the steps

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
