---
name: webui-test
description: Reference for writing a single Playwright UI test YAML by hand when the user already has exact steps and selectors. Not a starting point — for any "test my website" / "create UI tests" request use crawl-to-tests, whose rules take precedence.
---

# Web UI test: one test by hand

Use this only when the user has given exact steps and selectors. Otherwise stop and use `crawl-to-tests`. Its **Non-negotiable test rules** apply here too: no record ids, wait for each page's content (`timeout:` in ms), `{{baseUrl}}/path`, `expectedText` for checks, `CLEAR` before `SEND_KEYS`, `SELECT_BY_TEXT` for dropdowns, selectors only from the crawl, and end with an outcome check.

## 1. Selectors come from the stored crawl

`get_crawl_digest(target, page=…, text=…, type=…)` returns just the elements you need. If the target has no crawl, use `crawl-to-tests`, which offers to crawl.

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
- action: CLEAR
  selector: "#search-query"
- action: SEND_KEYS
  selector: "#search-query"
  value: "pliers"
- action: CLICK
  selector: 'button:has-text("Search")'
- action: WAIT_FOR_VISIBLE
  selector: 'a.card:has-text("Pliers")'
  timeout: 15000
- action: VALIDATE_TEXT
  selector: 'a.card:has-text("Pliers")'
  expectedText: "Pliers"
- action: TAKE_SCREENSHOT
  filename: "search-results"
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
