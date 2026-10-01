---
name: api-test
description: Write ProofArc API tests (scenarios) for endpoints the user chose — find the spec, read only the operations needed, write one validated scenario per behaviour, with logins by tag. Use after create-test and project-setup when the test is about an API, an endpoint, status codes or a Swagger/OpenAPI file.
---

# API test: spec → scenario → validate → create

One scenario proves one behaviour. A scenario is a list of HTTP steps run in order, and each step checks its status code.

## 1. Find the spec

- `detect_api_spec(base_url=<the API's address>)` finds the OpenAPI document. It tries `/v3/api-docs`, `/openapi.json`, `/swagger/v1/swagger.json`, `/api-json` and `/v2/api-docs`. If the address can't be reached, it fails within a second with a clear error. Run it before writing anything.
- Read only what you need. `get_api_digest(app, environment, level="index")` gives one line per operation. Then filter:
  - `path="/api/users/*"` and `method="POST"` give the full details of matching operations
  - `field="email"` finds operations using that field
  - `status=404` finds operations that document that code
- No spec? Write the steps from what the user tells you, and say that the paths weren't checked against a spec.

## 2. Write the scenario

```yaml
name: "users — create, read, delete"
baseUrl: "{{baseUrl}}"
appTag: user-service          # the application's app tag
credentialTag: api-admin      # the login this scenario signs in as (omit for a public API)
hooks:
  before:
    - script: "suffix:randomString(8)"   # a new value on every run
steps:
  - name: create
    method: POST
    path: /api/users
    body: {"username": "qa_{{suffix}}", "email": "qa_{{suffix}}@example.com"}
    expect: [201]
    extract:
      _id: $.id               # capture a value for later steps
  - name: read
    method: GET
    path: /api/users/{{_id}}
    expect: [200]
  - name: delete
    method: DELETE
    path: /api/users/{{_id}}
    expect: [200, 204]
```

- `path` starts with `/`; `{{baseUrl}}` has no trailing slash.
- Logins:
  - Name the login once with `credentialTag:`.
  - Never write a username, password or token into a step.
  - A step that needs the login's own values uses `{{username}}` / `{{password}}`.
- **Unique values:**
  - `{{$uuid}}` (Postman syntax) is **not** supported and is refused by validation.
  - Declare a generated value in `hooks.before` as `- script: "name:generator"`, as above.
  - Generators: `uuid`, `timestamp`, `isoTimestamp`, `randomInt(min,max)`, `randomString(length)`, `env(NAME)`.
  - The `script:` key is required. The validator's hint shows the form without it, which it then rejects.
- Clean up what you create (the `delete` step above). Read-only is the default; write steps only when the user asked for them.
- **Negative checks (401, 403, 404):**
  - Probe ids that don't exist, never real records.
  - Put a "wrong password → 401" step in its own scenario and run it with `allow_unauthenticated=true`. That sends no `Authorization` header but still fills `{{username}}`.
- Steps that don't depend on each other (a list of input checks, say) must run with `stop_on_failure=False`. Otherwise the first failure hides the rest.

## 3. Validate, then create

1. `validate_scenario_yaml(yaml_text, environment)` checks the YAML and saves nothing. Pass `environment` so `{{envVariable}}` references count as known. Fix and repeat until it returns `valid: true`.
2. `create_scenario_from_yaml(yaml_text, project, environment, tags)` saves it.
3. To change it later, use `update_api_scenario_from_yaml(scenario, yaml_text)`. It keeps the saved login, target and project.

For many endpoints at once, `create_scenario_from_swagger(project, environment, url, path_globs=["/api/users/**"], credential_tag=<tag>)` generates one scenario per endpoint. Always pass `credential_tag`.

## 4. Run

Hand the scenario ids to `run-test`. In short:
- `execute_scenario(scenario, environment, wait=True, summarize=True)`.
- The execution's `credentialTag` shows which login was used.
- A 400 `CREDENTIAL_AMBIGUOUS` or `CREDENTIAL_TAG_NOT_FOUND` means the run was refused before it started. Fix the login setup; it's not a test result.

A red step is a finding. Never change `expect` to match what the API returned.
