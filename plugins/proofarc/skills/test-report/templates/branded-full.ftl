<#assign runsPassed=0><#assign totalSteps=0><#assign stepsPassed=0>
<#list report.runs as r>
  <#if (r.outcome!'') == 'PASSED'><#assign runsPassed++></#if>
  <#assign totalSteps += (r.totalSteps!0)><#assign stepsPassed += (r.passed!0)>
</#list>
<#assign totRuns=report.runs?size>
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${report.title!'Test report'}</title>
<style>
:root{--bg:#f5f6f8;--card:#fff;--soft:#eef0f4;--ink:#161a20;--muted:#5b6472;--line:#e2e5ec;--accent:#3355d1;
--pass:#1f8a4c;--pass-bg:#e3f2e8;--fail:#cc3243;--fail-bg:#fbe4e6;--skip:#8b93a1;--skip-bg:#ecedf1;
--k-API:#5a4bd6;--k-UI:#0f8a86;--k-MOBILE:#8a3fc0;--k-OTHER:#6b7280}
@media (prefers-color-scheme:dark){:root{--bg:#0f1216;--card:#171b21;--soft:#20252d;--ink:#e8ebf0;--muted:#9aa3b2;--line:#2b313b;
--accent:#7b93ff;--pass:#5cc98a;--pass-bg:#16301f;--fail:#f0808f;--fail-bg:#3a1c20;--skip-bg:#222831}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:36px 16px 56px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:600;margin:0}
h1{font-size:28px;margin:6px 0 4px;letter-spacing:-.01em}.sub{color:var(--muted);margin:0 0 22px;font-size:14px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:24px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.tile b{display:block;font-size:24px;font-variant-numeric:tabular-nums}.tile span{font-size:12px;color:var(--muted)}
.tile.p b{color:var(--pass)}.tile.f b{color:var(--fail)}
.run{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:14px}
.head{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}
.kind{display:inline-block;color:#fff;font-size:11px;font-weight:600;padding:2px 8px;border-radius:99px;text-transform:uppercase;margin-bottom:6px}
.k-API{background:var(--k-API)}.k-UI{background:var(--k-UI)}.k-MOBILE{background:var(--k-MOBILE)}.k-OTHER,.k-SECURITY,.k-PERFORMANCE,.k-CRAWL{background:var(--k-OTHER)}
h2{font-size:17px;margin:0}.meta{color:var(--muted);font-size:13px;margin:2px 0 0;font-family:ui-monospace,Menlo,monospace;word-break:break-all}
.badge{font-weight:600;font-size:12px;padding:4px 12px;border-radius:99px;height:fit-content}
.PASSED{background:var(--pass-bg);color:var(--pass)}.FAILED{background:var(--fail-bg);color:var(--fail)}.SKIPPED{background:var(--skip-bg);color:var(--skip)}
.why{margin-top:12px;background:var(--fail-bg);color:var(--fail);border-radius:8px;padding:10px 12px;font-size:14px}
.tbl{overflow-x:auto;margin-top:12px;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13px;min-width:480px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--soft);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em}
tr:last-child td{border-bottom:0}.mono{font-family:ui-monospace,Menlo,monospace}.num{text-align:right;font-variant-numeric:tabular-nums;color:var(--muted)}
.pill{font-size:11px;font-weight:600;padding:1px 8px;border-radius:99px}.err{color:var(--fail);font-size:12px;margin-top:2px}
.foot{color:var(--muted);font-size:12px;margin-top:28px}
</style></head><body><div class="wrap">
<p class="eyebrow">ProofArc · test report</p>
<h1>${report.title!'Test report'}</h1>
<p class="sub">${totRuns} run<#if totRuns != 1>s</#if> · ${report.environment!'—'} · generated ${report.generatedAt!'—'}</p>
<div class="tiles">
  <div class="tile"><b>${totRuns}</b><span>runs</span></div>
  <div class="tile p"><b>${runsPassed}</b><span>passed</span></div>
  <div class="tile f"><b>${totRuns-runsPassed}</b><span>failed</span></div>
  <div class="tile"><b>${stepsPassed}/${totalSteps}</b><span>steps passed</span></div>
</div>
<#list report.runs as r>
<div class="run">
  <div class="head"><div>
    <span class="kind k-${r.kind!'OTHER'}">${r.kindLabel!'Run'}</span>
    <h2>${r.testName!'(unnamed)'}</h2>
    <p class="meta">run ${r.runNumber!'—'} · ${r.engine!'—'}<#if (r.browser)?has_content> · ${r.browser}</#if> · ${r.startedAt!'—'}<#if (r.duration)?has_content> · ${r.duration}s</#if></p>
    <#if (r.target)?has_content><p class="meta">${r.target}</p></#if>
  </div><span class="badge ${r.outcome!'FAILED'}">${r.outcome!'FAILED'}</span></div>
  <#if (r.errorMessage)?has_content><div class="why">${r.errorMessage}</div></#if>
  <#if (r.steps)?? && r.steps?size gt 0>
  <div class="tbl"><table><thead><tr><th>#</th><th>Action</th><th>Detail</th><th>Status</th><th>Time</th></tr></thead><tbody>
  <#list r.steps as s><tr><td class="num">${s.index!''}</td><td class="mono">${s.action!''}</td>
    <td class="mono">${s.detail!''}<#if (s.errorMessage)?has_content><div class="err">${s.errorMessage}</div></#if></td>
    <td><span class="pill ${s.status!'SKIPPED'}">${s.status!'—'}</span></td><td class="num"><#if (s.duration)?has_content>${s.duration}s</#if></td></tr></#list>
  </tbody></table></div>
  <#elseif !(r.errorMessage)?has_content><p class="meta">No steps recorded for this run.</p></#if>
</div>
</#list>
<p class="foot">Rendered by ProofArc from run data · ${report.generatedAt!''}</p>
</div></body></html>
