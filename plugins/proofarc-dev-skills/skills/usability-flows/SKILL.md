---
name: usability-flows
description: "Internal, for the ProofArc team: check the ProofArc platform's own usability rules (U1, U2, …) by running usability flows through MCP, with no UI. Use when asked to run the usability flows, check the usability rules, or verify a usability fix landed on ProofArc. It tests ProofArc itself, never a customer's app: for a customer's tests use proofarc-skills (create-test, run-test)."
---

# Usability flows

The rules are in `rules.md` (U1, U2, …). Each rule has flows in `api/flows.md`, which this skill runs through MCP with no UI, and `ui/flows.md`, which are built as dogfood UI tests with the `crawl-to-tests` skill and run on Playwright. The UI can read a different record than the API does (U2: the execution is FAILED while the scan job shows COMPLETED), so a PASS here doesn't prove the screen.

## 1. Where to run

- Only on dev: the `proofarc-dev` MCP server (tools named `mcp__proofarc-dev__…`). Never call another ProofArc server's tools (e.g. `proofarc-outpostqa`): its ids differ and its project 169 doesn't exist. If its tools aren't loaded yet, call `ToolSearch` for them (it waits while the server connects); never use Bash or `sleep` to wait. If it still isn't there, report every flow BLOCKED (server not connected). Then use project `dog-food-api` (169) and environment `dev` (125), unless the user names another trial project Claude created. Never a customer's project.
- Each flow lists what it needs. Find a scenario with `find_scenarios(project=169, …)`. `usability-u2-fail` can be created from its YAML in `api/flows.md` (validate first with `validate_scenario_yaml(yaml_text=…)`). Scenario 179 and data set `dogfood-plan-dd` can't be recreated from this skill: if they're missing, U1.a, U1.b and U4.a are BLOCKED.
- Flows never delete or change a record they didn't create, never add or change a credential or anything on environment 125, and never set a default credential. U1.a deliberately adds a red execution to scenario 179; that's expected.

## 2. Run a flow

1. Do the **Setup**.
2. Make the **Call** exactly as written. Pass `wait=True` to `execute_scenario`; if a run is still going, call the status tool again. Never use Bash or `sleep` to wait. Call the ProofArc tools yourself: never through Bash, curl or a script, and never hand a flow to a sub-agent (Agent/Task). A sub-agent's summary is not a result.
3. Read the answer: the error text, the status and the fields named in **Pass if**. Success is a field in the response, not the absence of an exception.
4. Compare with **Pass if**. Every condition must hold. Partial is a FAIL; say which condition broke.

## 3. Report

Every PASS or FAIL quotes what a call in this conversation returned: the execution id and `status`, or the refusal message. A flow you didn't call yourself is BLOCKED, never PASS. Don't infer a result from a rule's description or from an earlier run.

The final reply is the report: one line per flow, starting with the flow id and the result (`U2.a PASS: …`), with ids from the calls you just made, never from this file. Example shape: `U1.a FAIL: execute_scenario(179) started execution <id> (FAILED, "Nothing supplied a value for {{mode}}"); expected a refusal naming the data set. proofarc/tspc-cloud-platform#569`.
- PASS in one line, no detail.
- FAIL: the call, what came back (ids, status, message), the rule, and the open issue if `rules.md` lists one. If none is open, offer to file one; don't file unasked.
- BLOCKED: the flow couldn't run (missing setup, server down), with the reason. Never PASS.
- N/A: the flow doesn't apply on this build (e.g. U4.a when U1.a passed and no run started).
- Report every flow in `api/flows.md`, in order (today 6: U1.a, U1.b, U1.c, U2.a, U3.a, U4.a; U1.c is BLOCKED until it's defined).
- End with one summary line that names the flows in each group, copied from your lines above, without numbers: `Pass: U1.b, U2.a, U3.a · Fail: U1.a, U4.a · Blocked: U1.c`.

## 4. Adding a rule

A new usability case becomes a rule in `rules.md` (id, rule, why, where it was seen) and at least one flow in `api/flows.md` whose Pass if is something a call returns, plus one in `ui/flows.md` when the screen matters. A rule no call can check goes only in `ui/flows.md`.
