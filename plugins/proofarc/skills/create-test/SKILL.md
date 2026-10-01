---
name: create-test
description: Start here whenever a ProofArc user wants to create, write or build a test, or says "test my website", "test this app", "test this API" — work out what kind of test they want and what it should prove, then hand off to the right skill. Use before project-setup and the test-writing skills (webui-test, api-test, mobile-test, performance-test).
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

A URL on its own ("test https://shop.example.com") most likely means **Web UI**, but confirm what to prove (step 2).

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
| Web UI | `project-setup` (interface `WEB_UI`) → `webui-test` → `run-test` |
| API | `project-setup` (interface `REST`) → `api-test` → `run-test` |
| Mobile | `project-setup` (interface `MOBILE_UI`) → `mobile-test` (it runs the test too) |
| Performance | an API scenario that passes (`api-test` if there isn't one) → `performance-test` |
| Security | `find_playbooks(intent=<the user's words>)` and follow the playbook it returns |

If ProofArc tools aren't available or answer 401, use `connect` first.

Carry forward what you learned — the URL, the kind, the list of behaviours, whether a login is needed — so the next step doesn't ask again.
