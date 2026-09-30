# Which login a run signs in as

Verified on proofarc-dev, 2026-09-30 (#454; fixes #437, #450).

## The rule, same for every run type

1. the login named on the run: `credential_tag=` on `execute_scenario`, `run_ui_test`, `run_ui_test_suite`, `run_mobile_test`, `run_canary_performance`
2. the login saved on the test: an API scenario's `credentialTag` (YAML `credentialTag: <tag>`), a UI test's `credential_tag`, a mobile app's `login_config.credentialTag`
3. the login set on the target: `set_target_auth(target, auth_config={"authType": "UI_LOGIN", "credentialTag": "<tag>"})`
4. the environment default (`is_default=true`)

The login used is recorded:
- API: the execution's `credentialTag`
- UI: the job's `parameters.credentialTag`
- mobile: the job record's `credentialTag`

Check it there. A pass alone doesn't prove which login ran.

## Refusals: nothing runs, nothing is booked

| error | cause | fix |
|---|---|---|
| 400 `CREDENTIAL_AMBIGUOUS` | 2+ active logins, none default, none named | name one with `credential_tag`, or mark one default |
| 400 `CREDENTIAL_TAG_NOT_FOUND` | named or saved login doesn't exist, or is switched off (message says DEACTIVATED) | fix the name, or `set_environment_credential_active(environment, tag, active=true)` |

A missing or switched-off login is **never** replaced with the default. Mobile currently returns this refusal as HTTP 500 with the same message (to be fixed).

A public app, `allow_unauthenticated=true`, or a UI/mobile test that never types `{{username}}`/`{{password}}`/`{{token}}`/`{{apiKey}}` is not refused for having no default.

## Running without a login

`execute_scenario(..., allow_unauthenticated=true)`:
- sends no `Authorization` header
- still fills `{{username}}` in step bodies from the login that would apply
- leaves the execution's `credentialTag` null

Use it for "wrong password → 401" steps.

## Retry

`POST /api/agent/jobs/{jobId}/retry` (the Retry button):
- Only jobs whose **status** is FAILED, ERROR or CANCELLED can be retried. A test that failed a check is `COMPLETED` with outcome FAILED, and retrying it gives 409.
- A retry uses the same login as the original run. If that login is gone or switched off, you get 400 `CREDENTIAL_TAG_NOT_FOUND` ("it ran as login 'X', which no longer exists or is switched off"). Start a new run and pick a login.
- An unknown job gives 404.
- In the UI, the **Retry Job** button appears only when the job status is FAILED, which normal runs don't reach (#456). Retry through the API instead.

## Proving a run used the right login

Put a **wrong-password login as the environment default**, and the right one on the test or run. If the wrong login is used, the run fails. Example setup: project `qa-454-login-rule` (179) on dev. Environment 136 has default `bad-admin` plus `demo-admin`. Environment 137 has two logins and no default.
