<#-- run-report: one section per test. Runs of the same test (e.g. one per engine) sit side by side
     as engine cards, then the steps of the run that went worst, then a panel per failed step. -->
<#assign tests=[]><#assign seen={}>
<#list report.runs as r><#assign key=(r.testId!r.testName!r.runNumber)?string>
  <#if !(seen[key])??><#assign seen=seen+{key:true}><#assign tests=tests+[key]></#if></#list>
<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${report.title!'Run report'}</title>
<style>
:root{--bg:#f4f5f7;--surface:#fff;--surface-2:#eceef2;--fg:#171a21;--fg-dim:#5b6472;--rule:#d9dde4;--accent:#3a4fb8;
--pass:#1a7f5a;--fail:#b5283a;--skip:#8a93a1;--warn-bg:#fdf4e3;--warn-fg:#7a5614;
--display:'Archivo','Helvetica Neue',Arial,sans-serif;--body:'Source Sans 3',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root{--bg:#14161b;--surface:#1b1e25;--surface-2:#22262f;--fg:#e8eaee;--fg-dim:#98a1b0;--rule:#2e333d;
--accent:#8c9cf0;--pass:#45c096;--fail:#f2808f;--skip:#6f7786;--warn-bg:#2d2616;--warn-fg:#e3c177}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 var(--body)}
.wrap{max-width:1000px;margin:0 auto;padding:20px 16px 56px}
h1,h2,h3{font-family:var(--display);margin:0}
.eyebrow{font-family:var(--display);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--fg-dim)}
section.test{margin-bottom:40px}
header.run{display:flex;flex-wrap:wrap;gap:12px 28px;align-items:flex-end;border-bottom:2px solid var(--fg);padding-bottom:12px}
header.run h1{font-size:24px;font-weight:700;letter-spacing:-.015em}
.runmeta{display:flex;gap:22px;flex-wrap:wrap;margin-left:auto}.runmeta div{display:flex;flex-direction:column;gap:2px}
.runmeta b{font-family:var(--mono);font-size:13px;font-weight:500;word-break:break-all}
.verdict{display:inline-block;font-family:var(--display);font-weight:600;font-size:13px;padding:4px 11px;border-radius:3px;background:var(--fail);color:#fff}
.verdict.ok{background:var(--pass)}
.engines{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:16px 0}
.engine{background:var(--surface);border:1px solid var(--rule);border-left:3px solid var(--accent);border-radius:4px;padding:11px 13px;display:flex;flex-direction:column;gap:7px}
.engine .top{display:flex;gap:9px;align-items:center}.engine h3{font-size:13px;font-weight:600}
.engine .t{margin-left:auto;font-family:var(--mono);font-size:12px;color:var(--fg-dim)}
.bar{display:flex;height:5px;border-radius:3px;overflow:hidden;background:var(--surface-2)}
.engine small{color:var(--fg-dim);font-size:12px}
.note{background:var(--warn-bg);color:var(--warn-fg);border-radius:4px;padding:10px 13px;font-size:13px;margin-bottom:16px}
ol.steps{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:1px;background:var(--rule);border:1px solid var(--rule);border-radius:5px;overflow:hidden}
li.step{background:var(--surface);display:grid;grid-template-columns:26px 1fr auto;gap:11px;padding:10px 13px}
li.step.failed{box-shadow:inset 3px 0 0 var(--fail)}
.num,.dur{font-family:var(--mono);font-size:12px;color:var(--fg-dim);font-variant-numeric:tabular-nums}
.act{font-family:var(--display);font-weight:600;font-size:13px}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:7px;vertical-align:middle}
.d-PASSED{background:var(--pass)}.d-FAILED{background:var(--fail)}.d-SKIPPED{background:var(--skip)}
.target{font-family:var(--mono);font-size:12px;color:var(--fg-dim);margin-top:3px;word-break:break-word}
.skipped .act,.skipped .target{color:var(--skip)}
.fail-panel{margin-top:10px;border:1px solid var(--fail);border-radius:5px;overflow:hidden}
.fail-panel h3{background:var(--fail);color:#fff;font-size:12px;font-weight:600;padding:7px 13px}
.fail-body{background:var(--surface);padding:13px;display:flex;flex-direction:column;gap:9px}
.msg{font-family:var(--mono);font-size:12.5px;line-height:1.55;word-break:break-word}
a{color:var(--accent)}.foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--fg-dim)}
</style></head><body><div class="wrap">
<p class="eyebrow">${report.title!'ProofArc run report'} · ${report.environment!''} · generated ${report.generatedAt!''}</p>
<#if tests?size == 0><p>No runs selected.</p></#if>
<#list tests as key>
<#assign runs=report.runs?filter(r -> (r.testId!r.testName!r.runNumber)?string == key)>
<#-- the run to show steps for: the first failed one, else the first -->
<#assign worst=runs[0]><#list runs as r><#if (r.outcome!'') != 'PASSED'><#assign worst=r><#break></#if></#list>
<#assign nFail=worst.failed!0><#assign nSteps=worst.totalSteps!0>
<section class="test">
<header class="run">
  <div><div class="eyebrow">Run<#if runs?size gt 1>s</#if> <#list runs as r>${r.runNumber!'—'}<#sep>, </#list> · ${worst.startedAt!''}</div>
  <h1>${worst.testName!'(unnamed test)'}</h1></div>
  <div class="runmeta">
    <#if (worst.testId)??><div><span class="eyebrow">Test</span><b><#if worst.testId?is_number>${worst.testId?c}<#else>${worst.testId}</#if></b></div></#if>
    <div><span class="eyebrow">Target</span><b>${worst.target!'—'}</b></div>
    <div><span class="eyebrow">Verdict</span>
      <#if (worst.outcome!'') == 'PASSED'><span class="verdict ok">All ${nSteps} steps passed</span>
      <#elseif nSteps == 0><span class="verdict">Failed before any step</span>
      <#else><span class="verdict">${nFail} of ${nSteps} steps failed</span></#if></div>
  </div>
</header>
<div class="engines">
<#list runs as r><#assign p=r.passed!0><#assign f=r.failed!0><#assign s=r.skipped!0>
  <article class="engine"><div class="top"><h3>${r.engine!'—'}<#if (r.browser)?has_content> · ${r.browser}</#if></h3><span class="t">${r.duration!'—'}s</span></div>
  <div class="bar"><#if p gt 0><i style="flex:${p};background:var(--pass)"></i></#if><#if f gt 0><i style="flex:${f};background:var(--fail)"></i></#if><#if s gt 0><i style="flex:${s};background:var(--skip)"></i></#if></div>
  <small>run ${r.runNumber!'—'} · ${p} passed · ${f} failed · ${s} skipped</small></article>
</#list>
</div>
<#if runs?size gt 1>
  <#assign outs=[]><#list runs as r><#if !outs?seq_contains(r.outcome!'')><#assign outs=outs+[r.outcome!'']></#if></#list>
  <#if outs?size gt 1><div class="note"><b>The engines disagree:</b> <#list runs as r>${r.engine!'—'} ${r.outcome!'—'}<#sep>, </#list>. Check whether the test or one engine is at fault.</div></#if>
</#if>
<#if (worst.errorMessage)?has_content && ((worst.steps)![])?filter(x -> (x.status!'')=='FAILED')?size == 0><div class="fail-panel"><h3>Run failed<#if nSteps == 0> before any step</#if></h3><div class="fail-body"><div class="msg">${worst.errorMessage}</div></div></div></#if>
<#if (worst.steps)?? && worst.steps?size gt 0>
<ol class="steps">
<#list worst.steps as st>
  <li class="step<#if (st.status!'')=='FAILED'> failed</#if><#if (st.status!'')=='SKIPPED'> skipped</#if>">
    <span class="num">${(st.index!st?index)+1}</span>
    <span><span class="act"><span class="dot d-${st.status!'SKIPPED'}"></span>${st.action!''}</span>
      <div class="target"><#if (st.detail)?has_content>${st.detail}<#elseif (st.status!'')=='SKIPPED'>earlier step failed</#if></div></span>
    <span class="dur"><#if st.status!='SKIPPED'>${st.duration!'—'}s<#else>—</#if></span>
  </li>
</#list>
</ol>
<#assign bare=worst.steps?filter(x -> x.status!='SKIPPED' && !(x.detail)?has_content)?size>
<#if bare gt 0><p class="eyebrow" style="margin-top:6px">${bare} step<#if bare gt 1>s</#if> without a selector or value: ${worst.engine!'this engine'} doesn't record them yet</p></#if>
<#list worst.steps as st><#if (st.status!'')=='FAILED'>
<div class="fail-panel"><h3>Step ${(st.index!st?index)+1} failed — ${st.action!''}</h3><div class="fail-body">
  <div class="msg">${st.errorMessage!'(no message)'}</div>
  <#if (st.screenshotName)?has_content><div>Screenshot at the moment it failed: <#if (st.screenshotUrl)?has_content><a href="${st.screenshotUrl}">${st.screenshotName}</a><#else>${st.screenshotName}</#if> <span class="eyebrow">(opens with a ProofArc login)</span></div></#if>
</div></div>
</#if></#list>
</#if>
</section>
</#list>
<p class="foot">Rendered by ProofArc from the stored run data.</p>
</div></body></html>
