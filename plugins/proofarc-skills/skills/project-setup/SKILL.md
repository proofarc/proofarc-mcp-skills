---
name: project-setup
description: Make sure a ProofArc project has what a test needs — project, application, environment, target, and a credential if the site needs a login — reusing what already exists and creating only what's missing. Use after create-test has settled what to test, or when the user asks to onboard or set up a project, app, environment or target.
---

# Project setup — reuse first, create only what's missing

A test needs four things: a **project**, an **application**, an **environment**, and a **target** (the address being tested). Check each one; create only the missing ones.

## 1. Look before creating

- `list_projects` — offer the existing ones, or take a new name.
- For an existing project, `get_project_setup_status(project)` says what's done and what's missing.
- `list_project_applications(project)`, `list_environments(project)`, `list_targets(environment)` show the pieces.
- A target for the same URL already in the environment means the site is set up there — use it.
- **Shared environments:** if that environment also holds targets for *other* sites, don't link it into a new project — the project would inherit those sites, and running tests by tag there can't pick a target. Reuse the application, but create a project-specific environment (e.g. `skill-trial-toolshop`) with its own target for the same URL, or ask the user which they prefer.

## 2. Create what's missing — in this order

**Project before application**: an application can't be created without a project.

1. **Project** — `create_project(name, description)`.
2. **Application** — `create_application(project, name, app_tag, application_interfaces, auth_requirement)`, then **always** `link_application_to_project(application, project)`; it doesn't show on the project until linked.
   - `application_interfaces`: what the app exposes — `["WEB_UI"]` for a website, `["REST"]` for an API (also `GRAPHQL`, `SOAP`, `GRPC`, `MESSAGING`, `WEBSOCKET`, `MOBILE_UI`, …). Without it the call is refused.
   - `app_tag`: a short slug (`toolshop-web`) that connects the application, its target and its tests.
   - Application names are shared across projects — an existing name links that application (`linkedExisting: true`). Tell the user.
3. **Environment** — `create_environment(name, auth_requirement, project)`, then `link_environment(environment, project)`.
   - Environment names are shared across projects. Use a specific name (`toolshop-staging`); don't reuse `development` or `production` unless the user means that shared one.
   - `auth_requirement`: `PUBLIC` if anyone can open the site, `AUTHENTICATED` if tests log in.
4. **Credential** (login needed only) — ask the user for it, or ask them to add it, then `add_environment_credential(environment, tag, username, password, is_default=true)`. Tests refer to it by tag only. Never write a login into a test; never borrow one from another environment.
   - **Several logins in one environment:** mark exactly one as default, or every run must name its login — otherwise runs are refused with `CREDENTIAL_AMBIGUOUS`. A run signs in as: the login named on the run → the one saved on the test → the one set on the target → the environment default.
   - **Login for a website target** (used by suites and crawls when nothing more specific is named): `set_target_auth(target, auth_config={"authType": "UI_LOGIN", "credentialTag": "<tag>"})`. `authType` is required; without it the call is refused.
   - An API environment needs the login call once: `set_environment_auth_endpoint(environment, login_endpoint="/auth/login", auth_type="BEARER", token_json_path="$.accessToken")` (adjust to the app).
5. **Target** — `add_target(environment, name, target_type, base_url, app_tag, application)`.
   - `target_type`: `WEB_APP` for a website, `REST_SERVICE` for an API.
   - `base_url` without a trailing slash.
   - `app_tag` exactly the application's.
   - One target per address **per type** per environment — a website and an API may share an address.

**Shortcut for a brand-new setup:** `onboard_project(project_name, applications=[…], environments=[{name, authRequirement, targets:[…]}])` does steps 1–3 and 5 in one call.

## 3. Check

`get_project_setup_status(project)` returns `setupComplete: true`, and `list_targets(environment)` shows the URL and app tag. Tell the user in one line what was reused and what was created.
