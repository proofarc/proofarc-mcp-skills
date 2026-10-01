---
name: mobile-test
description: Set up and write ProofArc mobile (Appium) tests — register the app on the device farm, find element ids from the uploaded APK/IPA, write one validated test per behaviour, and run it on a real device with the right app login. Use when the test is about a mobile app, an APK/IPA, or "on the phone".
---

# Mobile test: app → elements → test → device run

Two different logins, easy to mix up:
- **The device-farm account** (BrowserStack user + access key) lives on the app record's `cloud_config`.
- **The app login**, what the test types into the app, is a login in the environment, referenced by tag.

Never put either into a test.

## 1. The app

- `list_mobile_apps` first. Reuse the app if it's there.
- New app:
  ```
  create_mobile_app(project, name, platform="ANDROID" | "IOS",
                    app_package=<e.g. com.example.app>,     # Android
                    bundle_id=<e.g. com.example.app>,       # iOS
                    cloud_provider="BROWSERSTACK",
                    cloud_config={"appUrl": "bs://…", "userName": …, "accessKey": …,
                                  "deviceName": "Google Pixel 7", "osVersion": "13.0"})
  ```
  - Ask the user for the farm user and key, and for the `bs://` app URL from their BrowserStack upload.
  - `osVersion` must be a full version: `"13.0"`, not `"13"`. A short version fails within about a second, before any device is booked. If that happens, it's this setting, not the farm.
- App login: `add_environment_credential(environment, tag, username, password)` with values **the user gives you**. Never fill in a password yourself, not even a public demo one; ask. The test refers to the tag.

## 2. Element ids

- The build (APK/IPA) must be uploaded once. There is no MCP tool for it: ask the user to upload it in ProofArc under **Mobile Testing → Mobile Apps → Upload Binary** on the app's row. Without it, skip the scan and take selectors from the user or an existing test.
- `inspect_mobile_app_static(mobile_app, level="index")` reads ids from the build. No device is used and it costs nothing.
  - Filter with `screen=`, `name=` or `text=`, and `stable_only=true`.
  - The stored result can be read again later with `get_mobile_inspection_digest` and the same filters.
- Take selectors from that inventory, never from guesses or memory. If the scan has no ids (common for React Native and Flutter builds), use selectors from the app's existing tests or ask the user. Say which source each selector came from.

## 3. Write the test

```yaml
name: standard user login shows products
steps:
  - action: type
    selector: accessibility:test-Username
    value: "{{username}}"
  - action: type
    selector: accessibility:test-Password
    value: "{{password}}"
  - action: tap
    selector: accessibility:test-LOGIN
  - action: assert_visible
    selector: accessibility:test-PRODUCTS
```

- Selectors are `strategy:value`: `accessibility:`, `id:`, `xpath:` or `class:`.
- Don't `tap` a field before `type`; `type` already focuses and clears it. An extra tap costs device time.
- Logins only as `{{username}}` / `{{password}}`. A literal in a password field is refused.
- Write steps in block style, one key per line.
- End with an `assert_visible` for the behaviour the user asked about.

1. `validate_mobile_test_yaml(yaml_text)` checks the YAML and saves nothing.
2. `create_mobile_test(mobile_app, name, yaml_text, project, tags)` saves it.

## 4. Run

```
run_mobile_test(mobile_test, environment, credential_tag=<app login tag>, wait=True)
```

- Read the result with `get_mobile_test_executions(mobile_test)`. Each row has `status`, `testOutcome` and `error`.
- **Several devices at once:** `devices=[{"device": "Google Pixel 7", "osVersion": "13.0"}, …]`. That makes one run per device.
- **Refused before booking a device:** a login tag that doesn't exist or is switched off (400 `CREDENTIAL_TAG_NOT_FOUND`), or several logins and none named (400 `CREDENTIAL_AMBIGUOUS`).
- **`error` names an unknown device:** fix the device name against BrowserStack's device list.

Device time is metered. Run once to see it pass, once with the final assertion changed to prove it can fail, then restore it.
