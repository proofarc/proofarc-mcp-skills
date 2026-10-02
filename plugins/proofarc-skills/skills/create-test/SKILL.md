---
name: create-test
description: Start here when the user wants (with a ProofArc MCP server connected, even if ProofArc isn't mentioned) to create a test but hasn't said what kind — "I want to create a test", "test my app", "add a test", "help me test this" — work out the kind (web UI, API, mobile, performance, security) and what it should prove, then hand off. A website or URL goes straight to crawl-to-tests.
---

# Create a test — find the intent first

Before setting anything up, know two things: **what kind of test**, and **what it should prove**. Don't start a crawl or create a project until both are clear.

## 1. What kind of test

Infer it from what the user said. Ask only when it's genuinely unclear.

| The user says… | Kind |
|---|---|
| a website or page URL, "the site", "the login page", "the checkout", "click", "form" | **Web UI** |
| an API, an endpoint, a Swagger/OpenAPI file, "status code", "request" | **API** |
| an app store app, an APK/IPA, "on the phone" | **Mobile** |
| "load", "how many users", "response time under load" | **Performance** |
| "vulnerabilities", "security scan", "is it safe" | **Security** |

A URL or website ("test https://shop.example.com") → hand off to `crawl-to-tests` now. Don't ask what to prove; it suggests tests from the crawl.

If it's still unclear, ask one question:

> What would you like to test?
> 1. Pages and flows on the website (web UI)
> 2. API endpoints
> 3. A mobile app
> 4. Performance under load
> 5. Security

## 2. What it should prove

A test proves one behaviour. If the user hasn't said which, ask — with examples that fit their site:

> What should the test check? For example:
> - the main pages open and show the right title
> - a flow works — search, login, add to cart
> - a form shows the right fields
> - one specific page or element

Several behaviours → several tests, one each. Write them down as a short list and confirm it with the user before building anything.

Note whether the behaviour **needs a login**. If it does, the setup needs a credential.

## 3. Hand off

| Kind | Next |
|---|---|
| Web UI | `crawl-to-tests`: it handles setup, the crawl, suggestions, building and running. |
| API | `project-setup` (interface `REST`) → `api-test` → `run-test` |
| Mobile | `project-setup` (interface `MOBILE_UI`) → `mobile-test` (it runs the test too) |
| Performance | an API scenario that passes (`api-test` if there isn't one) → `performance-test` |
| Security | `find_playbooks(intent=<the user's words>)` and follow the playbook it returns |

If ProofArc tools aren't available or answer 401, use `connect` first.

Carry forward what you learned — the URL, the kind, the list of behaviours, whether a login is needed — so the next step doesn't ask again.
