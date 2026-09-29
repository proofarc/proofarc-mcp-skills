---
name: webui-test
description: Write ProofArc web UI tests for behaviours the user already chose — reuse or run a crawl of the site, take selectors from it, and create one validated Playwright test per behaviour. Use after create-test and project-setup, when the user wants a UI test for a website or single-page app.
---

# Web UI test — from the crawl to a validated test

Start with: the target (from `project-setup`) and the list of behaviours to prove (from `create-test`).

## 1. Crawl — reuse before you wait

`ensure_crawl_for_authoring(url)` returns a stored crawl instantly when one is recent (under `maxAgeHours`, 24) and deep enough; otherwise it crawls (1–2 minutes for ~40 pages). Tell the user which happened — e.g. "Reused a crawl from 40 minutes ago: 40 pages, 162 elements." Pass `force_refresh=True` only if they want the latest version of the site.

- Selectors attached to the target: `crawl_by_target(target, max_depth)`, then `get_crawl_digest(project, environment, target)`.
- Crawls use a real browser (Playwright): single-page apps (React, Angular, Vue) work, and an almost empty HTML page is normal for them.
- A site behind a login stops at the login page unless the environment has a credential.
- A running crawl can't be stopped. Keep `max_depth` at 1–2 unless the user asks for more.

## 2. Choose selectors from the crawl

Never guess. Prefer, in order: the site's test hooks (`[data-test=…]`, `[data-testid=…]`), a stable `#id`, `[name=…]`, a role or label. Avoid auto-generated ids such as `#_r_1_` and position-based selectors — they break on the next deploy. Don't hard-code URLs of items the site regenerates (product or order ids).

## 3. Write one test per behaviour

```yaml
name: "Toolshop — search finds pliers"
appTag: "toolshop-web"
steps:
- action: NAVIGATE_TO
  url: "{{baseUrl}}/"
- action: WAIT_FOR_VISIBLE
  selector: "#search-query"
  timeout: 15
- action: SEND_KEYS
  selector: "#search-query"
  value: "pliers"
- action: CLICK
  selector: '[data-test="search-submit"]'
- action: VALIDATE_TEXT
  selector: '[data-test="product-name"]'
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
