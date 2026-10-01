---
name: performance-test
description: Load-test an API with ProofArc — turn a working API scenario into a performance scenario, set response-time and error-rate limits, dry-run it once, then run it and report p95 and error rate. Use when the user asks about load, "how many users", or response time under load.
---

# Performance test: working API scenario → load → verdict

Start from an API scenario that already passes. If there isn't one, write it first with `api-test` and run it green.

## 1. Pick the scenario

Load repeats every step, so check the scenario first.
- **Remove steps that expect an error.** A step expecting 404 counts as an error under load. A "gone → 404" check in a lifecycle scenario turns a healthy run into a 20% error rate.
- **Bodies that create records need unique values.** Otherwise the repeated requests collide on unique fields. See `data` below.

## 2. Convert

```
convert_api_to_performance_scenario(scenario, name,
    load_mode="quick", vus=10, duration=60,
    p95_threshold_ms=2000, max_error_rate=1.0)
```

- `load_mode` options:
  - `quick` is a flat `vus` × `duration` (seconds).
  - `phased` takes `phase_pattern` = `ramp-up`, `spike` or `soak`.
  - `custom` takes `phases=[{name, duration, arrivalRate, rampTo?, maxVusers?}]`.
  - Other values are refused.
- `max_error_rate` is a **percent** here (`1.0` = 1%). `slo_preset` = `strict`, `standard` or `relaxed` sets all three limits at once.
- `data` gives each virtual user its own values, for example `[{"step": 1, "field": "email", "strategy": "unique-uuid"}]`. Strategies: `static`, `unique-uuid`, `unique-pattern`, `unique-sequence`, `csv-feed`.
- `per_endpoint_slos=[{"endpoint": "/api/search", "p95": 300}]` gates one slow endpoint on its own.
- The new scenario keeps the API scenario's login, base URL, project and environment.

Ask the user for the load and the limits if they haven't said. Start small (10 users, 60 s) on anything that isn't theirs to load.

## 3. Dry-run once

`validate_performance_scenario(scenario)` runs the flow once with one user. It returns the exact step and reason for any of these:
- an unresolved `{{var}}`
- a capture path that doesn't match, such as `$.token` when the response has `$.accessToken`
- a login that didn't work

Fix the problem before a full run.

## 4. Run and read

1. `run_performance_scenario(scenario, environment, wait=True)` returns the verdict. If `timedOut: true`, the run is still going, not failed.
2. `get_performance_result(scenario, job_id)` returns `verdict` (PASS/FAIL) and the metrics: `totalRequests`, `errorRate`, `p95ResponseTime` and `p99ResponseTime`, each against its limit.

Report in one line: verdict, requests, error rate and p95 against the limit. A FAIL is a finding: say which limit it broke. Don't raise the limit to make it pass.
