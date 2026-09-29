# Report fields for custom templates

Templates are FreeMarker. Every `${…}` is HTML-escaped automatically. Fields confirmed on dev, 2026-09-29.

## `report`
| field | example |
|---|---|
| `report.title` | `Nightly regression` (from the `title` argument) |
| `report.generatedAt` | `2026-09-29 20:59` |
| `report.environment` | `default` |
| `report.runs` | the list of runs |

## Each run — `<#list report.runs as r>`
| field | example | note |
|---|---|---|
| `r.testName` | `Toolshop — search for pliers` | |
| `r.kind` | `UI`, `MOBILE`, `API`, `PERFORMANCE`, `SECURITY`, `CRAWL`, `OTHER` | for grouping / logic |
| `r.kindLabel` | `UI test`, `Mobile test`, `API scenario` | for display |
| `r.engine` | `PLAYWRIGHT`, `WEBDRIVER`, `APPIUM`, `REST` | |
| `r.browser` | `chrome` | UI only |
| `r.target` | `https://practicesoftwaretesting.com` | |
| `r.outcome` | `PASSED`, `FAILED` | |
| `r.passed`, `r.failed`, `r.skipped`, `r.totalSteps` | `6`, `1`, `2`, `9` | step counts |
| `r.runNumber`, `r.jobId` | `490`, `99a55ab8-…` | |
| `r.startedAt` | `2026-09-29 04:49` | |
| `r.duration` | `32.62` (seconds) | missing on some runs — use `!` |
| `r.errorMessage` | `Nothing supplied a value for {{password}}…` | run-level reason, e.g. failed before any step |
| `r.steps` | list of steps | empty when nothing ran |

## Each step — `<#list r.steps as s>`
| field | example | note |
|---|---|---|
| `s.index` | `0` | |
| `s.action` | `NAVIGATE_TO`, `CLICK`, `VALIDATE_TEXT`, `CREATE — POST /api/users` | |
| `s.detail` | `GET http://…/api/users -> 200` | empty for Playwright runs |
| `s.status` | `PASSED`, `FAILED`, `SKIPPED` | |
| `s.duration` | `0.7` (seconds) | |
| `s.errorMessage` | `…was not visible after 30000ms` | on a failed step |
| `s.screenshotUrl` | `/api/screenshots/…png` | needs a ProofArc login to open |

## FreeMarker you'll need

```ftl
<#list report.runs as r>…</#list>          loop
${r.duration!'—'}                          value, or '—' when missing
<#if (r.errorMessage)?has_content>…</#if>  only when present
<#if r.outcome == 'FAILED'>…</#if>         condition
${report.runs?size}                        count
<#assign n=0><#list report.runs as r><#if r.outcome=='PASSED'><#assign n++></#if></#list>${n}   count matching
```

Any field that can be missing needs `!` — otherwise the render fails with a 400 naming the field.

## Minimal example — one line per run

```ftl
<h1>${report.title}</h1>
<table><tr><th>Test</th><th>Type</th><th>Result</th><th>Steps</th></tr>
<#list report.runs as r>
<tr><td>${r.testName}</td><td>${r.kindLabel!''}</td><td>${r.outcome}</td><td>${r.passed}/${r.totalSteps}</td></tr>
</#list></table>
```
