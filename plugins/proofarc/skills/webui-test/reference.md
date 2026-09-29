# Web UI testing — reference

## Common actions

Call `list_ui_test_actions` for the full, current list.

| Action | Parameters |
|---|---|
| `NAVIGATE_TO` | `url` |
| `NAVIGATE_BACK`, `NAVIGATE_FORWARD`, `REFRESH` | — |
| `CLICK`, `DOUBLE_CLICK`, `RIGHT_CLICK` | `selector` |
| `SEND_KEYS` | `selector`, `value` |
| `WAIT_FOR_VISIBLE`, `WAIT_FOR_CLICKABLE`, `WAIT_FOR_ELEMENT`, `WAIT_FOR_INVISIBLE` | `selector`, `timeout` (seconds) |
| `WAIT_FOR_TEXT` | `selector`, `expectedText`, `timeout` |
| `VALIDATE_TITLE`, `VALIDATE_URL` | `expectedText` (contains) |
| `VALIDATE_TEXT` | `selector`, `expectedText` (contains) |
| `VALIDATE_VISIBLE`, `VALIDATE_NOT_VISIBLE`, `VALIDATE_ELEMENT_VISIBLE`, `VALIDATE_ELEMENT_EXISTS` | `selector` |
| `VALIDATE_ATTRIBUTE` | `selector`, `attribute`, `expectedText` |
| `EXECUTE_JS` | `script` |
| `TAKE_SCREENSHOT` | — |

## Errors and what to do

| The tool says | Fix |
|---|---|
| `create_application` … `project` field required | Create the project first, then the application. |
| `Target URL is required` / `Multiple WEB_APP targets … match this test` | Pass `target` (the target id as a string) to `run_ui_test`. |
| `references {{username}}/{{password}} but no credentials are available` | The environment needs a credential; pass its tag as `credential_tag`. Ask the user for the login — never invent one. |
| `has no driver set … specify drivers` | Pass `drivers=["PLAYWRIGHT"]`. |
| `NAVIGATE_TO` fails in under a second with `ERR_NAME_NOT_RESOLVED at https://site.compath` | Missing slash: write `{{baseUrl}}/path`. |
| `DUPLICATE_BASE_URL` / `DUPLICATE_TARGET` | A website target for that address already exists in the environment — use it. |
| `UNKNOWN_PARAMETER … Its parameters are: …` | Use the parameter names the error lists. |
| `missing_required` with `ask_user` and `candidates` | Show the user the candidates and ask; then call again with their answer. |
| Crawl found almost nothing | Login page (add a credential), bot protection (HTTP 403 or a captcha — ask for a staging URL), or the crawl was too shallow (raise `max_depth`). |
| A test is red | Report the failing step and message. Don't change the expectation to make it pass. |

## Rules

- Credentials only by tag from the environment's vault — never in a test, never borrowed.
- Tests are read-only unless the user asks for a write.
- Prove each assertion once by making it fail.
- Confirm with the user before deleting anything.
