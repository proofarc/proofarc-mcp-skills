---
name: webui-test
description: Reference for writing a single Playwright UI test YAML by hand when the user already has exact steps and selectors. Not a starting point — for any "test my website" / "create UI tests" request use crawl-to-tests, whose rules take precedence.
---

# Web UI test — from the crawl to a validated test

Start with: the target (from `project-setup`) and the list of behaviours to prove (from `create-test`).

## 1. Crawl — reuse before you wait

`ensure_crawl_for_authoring(url, max_depth=1)` returns a stored crawl instantly when one is recent (under `maxAgeHours`, 24) and deep enough; otherwise it crawls (1–2 minutes for ~40 pages). Tell the user which happened — e.g. "Reused a crawl from 40 minutes ago: 18 pages." Pass `force_refresh=True` only if they want the latest version of the site.

**Search the crawl — never read all of it.** A full crawl is 70–120k characters; a search for the elements you need is a few hundred.
1. From `ensure_crawl_for_authoring` take only `jobId`, `fresh`, `ageHours` and the stats. For the page list: `ensure_crawl_for_authoring(url, level="index")` or `get_crawl_results(job_id)` (url, title, element count per page).
2. Search for exactly the elements the test needs: `get_crawl_results(job_id, page_url=…, text=…, type=…, role=…, stable_only=…, limit=…, fields=[…])` — e.g. `text="Search", type="button"` on the home page returns one element in ~270 characters.
3. If a result is still too large to display and gets saved to a file, **don't dig through the file** — narrow the search instead.

- Crawls use a real browser (Playwright): single-page apps (React, Angular, Vue) work, and an almost empty HTML page is normal for them.
- A site behind a login stops at the login page unless the environment has a credential.
- A running crawl can't be stopped. Keep `max_depth` at 1 unless the user asks for more.

## 2. Choose selectors from the crawl

Never guess. Use each element's `primarySelector` and `alternates`, preferring a stable `#id`, `[name=…]`, or a role/label (`aria-label`) over a class or text.

**Test hooks may be missing from the crawl.** The crawl doesn't always record `data-test` / `data-testid` attributes, so a site that has them can look as if it doesn't. Don't tell the user the site has no test hooks, and don't invent `data-test` selectors; use only selectors the crawl returned. If a key element can only be found by class or text, use that — and say plainly that the test depends on that text or layout.

Avoid auto-generated ids such as `#_r_1_` and position-based selectors — they break on the next deploy. Don't hard-code URLs of items the site regenerates (product or order ids).

## 3. Write one test per behaviour

```yaml
name: "Toolshop — search finds pliers"
appTag: "toolshop-web"
steps:
- action: NAVIGATE_TO
  url: "{{baseUrl}}/"
- action: WAIT_FOR_VISIBLE
  selector: "#search-query"
  timeout: 15000
- action: SEND_KEYS
  selector: "#search-query"
  value: "pliers"
- action: CLICK
  selector: 'button.btn:has-text("Search")'   # as returned by the crawl
- action: WAIT_FOR_TEXT
  selector: body
  expectedText: "Pliers"
- action: TAKE_SCREENSHOT
```

- `{{baseUrl}}/path` — always with the leading slash; `{{baseUrl}}` has no trailing slash.
- Wait for an element before typing into or clicking it.
- Assert the behaviour the user asked for, not just that the page loaded.
- Login steps use `{{username}}` / `{{password}}` — never real values.
- Read-only by default: no form submits, purchases or deletions unless the user asks.
- Actions and parameters: `reference.md`, or call `list_ui_test_actions`.

## 4. Validate and create

`validate_ui_test_yaml(yaml_text)` saves nothing — iterate until it's valid. Then `create_ui_test_from_yaml(project, yaml_text, name, driver="PLAYWRIGHT", tags, description, credential_tag)` (`credential_tag` only when a login is needed).

Hand the created test ids to `run-test`.
