from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ui", tags=["ui"])

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TraceBack — Incident Evaluation</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172033;background:#f5f7fb;line-height:1.45}
*{box-sizing:border-box}body{margin:0}button,input,select{font:inherit}
.shell{max-width:1240px;margin:auto;padding:28px 22px 56px}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:28px}
.brand{display:flex;align-items:center;gap:12px}.mark{width:38px;height:38px;border-radius:11px;background:#172033;color:white;display:grid;place-items:center;font-weight:800}
h1{font-size:24px;letter-spacing:-.03em;margin:0}h2{font-size:17px;margin:0}h3{font-size:14px;margin:0}p{color:#667085;margin:5px 0 0;font-size:13px}
.pill{font-size:12px;padding:6px 10px;border:1px solid #dbe1ea;border-radius:999px;background:white;color:#475467}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.wide{grid-column:1/-1}
.card{background:#fff;border:1px solid #e1e6ee;border-radius:16px;padding:20px;box-shadow:0 2px 8px #1018280a}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:16px}
label{display:block;font-size:12px;font-weight:700;color:#475467;margin:12px 0 5px}
input,select{width:100%;padding:10px 11px;border:1px solid #d0d5dd;border-radius:9px;background:#fff;color:#172033;outline:none}
input:focus,select:focus{border-color:#98a2b3;box-shadow:0 0 0 3px #66708514}
button{border:1px solid #172033;border-radius:9px;padding:10px 13px;background:#172033;color:#fff;font-weight:700;cursor:pointer}
button:hover{opacity:.92}button.secondary{background:#fff;color:#172033;border-color:#d0d5dd}
.actions{display:flex;gap:8px;margin-top:14px}.actions button{flex:1}
.status{font-size:12px;font-weight:700;margin-top:10px;min-height:18px}.status.good{color:#067647}.status.bad{color:#b42318}.status.muted{color:#667085}
.result{margin:10px 0 0;padding:12px;border-radius:10px;background:#f8fafc;border:1px solid #edf0f4;white-space:pre-wrap;overflow:auto;max-height:280px;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;color:#344054}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}.metric{padding:13px;border-radius:11px;background:#f8fafc;border:1px solid #edf0f4}.metric span{display:block;font-size:11px;color:#667085}.metric strong{display:block;font-size:19px;margin-top:3px}
.table-wrap{overflow:auto;margin-top:8px}table{width:100%;border-collapse:collapse;font-size:13px}th{text-transform:uppercase;font-size:10px;letter-spacing:.06em;color:#667085}th,td{text-align:left;padding:11px 9px;border-bottom:1px solid #eef1f5}tbody tr:hover{background:#fafbfc}
.good{color:#067647}.bad{color:#b42318}.muted{color:#667085}.empty{text-align:center;padding:24px;color:#667085}
.config{display:grid;grid-template-columns:1.2fr 150px 1fr 38px;gap:8px;margin-bottom:8px}.config button{background:#fff;color:#b42318;border-color:#f0c4c4;padding:8px}
.section-note{padding:10px 12px;background:#f8fafc;border-radius:9px;color:#667085;font-size:12px;margin-bottom:12px}
.hidden{display:none}.loading{opacity:.65}
@media(max-width:820px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}.metric-grid{grid-template-columns:repeat(2,1fr)}.config{grid-template-columns:1fr 1fr}.topbar{align-items:flex-start}}
</style>
</head>
<body>
<div class="shell">
<header class="topbar">
<div class="brand"><div class="mark">T</div><div><h1>Traceback</h1><p>LLM incident evaluation workspace</p></div></div>
<span class="pill">Backend connected</span>
</header>

<div class="grid">
<section class="card">
<div class="card-head"><div><h2>Investigate an incident</h2><p>Run one scenario through the live investigation contract.</p></div></div>
<label>Scenario</label><select id="scenario"></select>
<label>Mode</label><select id="investMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select>
<label>Model <span class="muted">(LLM only)</span></label><input id="investModel" placeholder="llama3.2">
<button style="margin-top:14px;width:100%" onclick="investigate()">Run investigation</button>
<div id="investStatus" class="status muted">Ready.</div><pre id="investResult" class="result">Choose a scenario and run an investigation.</pre>
</section>

<section class="card">
<div class="card-head"><div><h2>Run a benchmark</h2><p>Persist a repeatable experiment against the core dataset.</p></div></div>
<label>Experiment name</label><input id="benchName" value="ui-benchmark">
<label>Mode</label><select id="benchMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select>
<label>Model <span class="muted">(LLM only)</span></label><input id="benchModel" placeholder="llama3.2">
<label>Repetitions</label><input id="benchReps" type="number" min="1" max="100" value="3">
<button style="margin-top:14px;width:100%" onclick="benchmark()">Run benchmark</button>
<div id="benchStatus" class="status muted">Ready.</div><pre id="benchResult" class="result">No benchmark run yet.</pre>
</section>

<section class="card wide">
<div class="card-head"><div><h2>Experiment matrix</h2><p>Compare multiple configurations on the same immutable dataset.</p></div><span class="pill">Comparison-ready</span></div>
<div class="config" style="grid-template-columns:1fr 1fr">
<div><label>Matrix name</label><input id="matrixName" value="ui-matrix"></div>
<div><label>Repetitions</label><input id="matrixReps" type="number" min="1" max="100" value="3"></div>
</div>
<div class="section-note">The first configuration is the comparison baseline. Add candidates to test different modes or models.</div>
<div id="configs"></div>
<div class="actions"><button class="secondary" onclick="addConfig()">+ Add configuration</button><button onclick="matrix()">Run matrix</button></div>
<div id="matrixStatus" class="status muted">Ready.</div><pre id="matrixResult" class="result">Add configurations, then run the matrix.</pre>
</section>

<section class="card wide">
<div class="card-head"><div><h2>Experiment history</h2><p>Persisted results from the experiment repository.</p></div><div class="actions" style="margin:0"><button class="secondary" onclick="loadExperiments()">Refresh</button><button class="secondary" onclick="compareSelected()">Compare selected</button></div></div>
<div id="experiments"><div class="empty">Loading experiments…</div></div>
<div id="compareResult" class="hidden"><h3 style="margin-top:18px">Comparison</h3><div id="compareMetrics" class="metric-grid"></div><pre id="compareDetails" class="result"></pre></div>
</section>

<section class="card"><div class="card-head"><div><h2>Recent jobs</h2><p>Operational queue state</p></div></div><pre id="jobs" class="result">Loading…</pre></section>
<section class="card"><div class="card-head"><div><h2>Recent investigation runs</h2><p>Latest persisted evaluations</p></div></div><pre id="runs" class="result">Loading…</pre></section>
</div>
</div>

<script>
const $=id=>document.getElementById(id);
async function api(path,options={}){const r=await fetch(path,options);const text=await r.text();let data;try{data=JSON.parse(text)}catch{data=text}if(!r.ok)throw Error(typeof data==="string"?data:(data.detail||data.message||JSON.stringify(data)));return data}
function setStatus(id,msg,kind="muted"){const e=$(id);e.textContent=msg;e.className="status "+kind}
function pct(v){return (Number(v)*100).toFixed(1)+"%"} function ms(v){return Number(v).toFixed(1)+" ms"}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
async function scenarioIds(){return [...$("scenario").options].map(o=>o.value)}
async function init(){const scenarios=await api("/scenarios");$("scenario").innerHTML=scenarios.map(x=>'<option value="'+x.id+'">'+escapeHtml(x.title)+'</option>').join("");addConfig("baseline","baseline","");addConfig("candidate","llm","");await refreshOperational();await loadExperiments()}
function addConfig(name="",mode="baseline",model=""){const row=document.createElement("div");row.className="config";row.innerHTML='<input class="cfg-name" placeholder="configuration name" value="'+escapeHtml(name)+'"><select class="cfg-mode"><option value="baseline">baseline</option><option value="llm">llm</option></select><input class="cfg-model" placeholder="model (for LLM)" value="'+escapeHtml(model)+'"><button title="Remove" onclick="this.parentElement.remove()">×</button>';row.querySelector(".cfg-mode").value=mode;$("configs").appendChild(row)}
async function investigate(){setStatus("investStatus","Running investigation…");$("investResult").textContent="";try{const b={scenario_id:$("scenario").value,mode:$("investMode").value};if($("investModel").value)b.model=$("investModel").value;const r=await api("/investigations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});$("investResult").textContent=JSON.stringify(r,null,2);setStatus("investStatus",r.passed?"Evaluation passed":"Completed — evaluation failed",r.passed?"good":"bad");await refreshOperational()}catch(e){$("investResult").textContent=e.message;setStatus("investStatus","Request failed","bad")}}
async function benchmark(){setStatus("benchStatus","Running benchmark…");$("benchResult").textContent="";try{const b={name:$("benchName").value,scenario_ids:await scenarioIds(),repetitions:Number($("benchReps").value),mode:$("benchMode").value};if($("benchModel").value)b.model=$("benchModel").value;const r=await api("/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});$("benchResult").textContent=JSON.stringify(r,null,2);setStatus("benchStatus",r.regression_passed?"Regression gate passed":"Regression gate failed",r.regression_passed?"good":"bad");await loadExperiments()}catch(e){$("benchResult").textContent=e.message;setStatus("benchStatus","Request failed","bad")}}
async function matrix(){setStatus("matrixStatus","Running matrix…");$("matrixResult").textContent="";try{const rows=[...document.querySelectorAll(".config")];const configurations=rows.map(row=>({name:row.querySelector(".cfg-name").value,mode:row.querySelector(".cfg-mode").value,model:row.querySelector(".cfg-model").value||null}));if(configurations.length<2)throw Error("Add at least two configurations.");const r=await api("/experiments/matrix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({matrix_id:$("matrixName").value,scenario_ids:await scenarioIds(),configurations,repetitions:Number($("matrixReps").value),min_pass_rate:1})});$("matrixResult").textContent=JSON.stringify(r,null,2);setStatus("matrixStatus","Matrix completed • best: "+r.best_experiment_id,"good");await loadExperiments()}catch(e){$("matrixResult").textContent=e.message;setStatus("matrixStatus","Request failed","bad")}}
async function loadExperiments(){try{const xs=await api("/experiments?limit=30");if(!xs.length){$("experiments").innerHTML='<div class="empty">No persisted experiments yet.</div>';return}$("experiments").innerHTML='<div class="table-wrap"><table><thead><tr><th></th><th>Name</th><th>Pass rate</th><th>Runs</th><th>Regression</th><th>Created</th></tr></thead><tbody>'+xs.map(x=>'<tr><td><input type="checkbox" name="exp" value="'+escapeHtml(x.experiment_id)+'"></td><td><strong>'+escapeHtml(x.name)+'</strong></td><td>'+pct(x.pass_rate)+'</td><td>'+x.passed_runs+"/"+x.total_runs+'</td><td class="'+(x.regression_passed===false?"bad":"good")+'">'+(x.regression_passed===null?"—":x.regression_passed?"PASS":"FAIL")+'</td><td>'+new Date(x.created_at).toLocaleString()+'</td></tr>').join("")+'</tbody></table></div>'}catch(e){$("experiments").innerHTML='<div class="empty">Unable to load experiments: '+escapeHtml(e.message)+'</div>'}}
async function compareSelected(){const chosen=[...document.querySelectorAll('input[name="exp"]:checked')].map(x=>x.value);if(chosen.length!==2){alert("Select exactly two experiments.");return}try{const r=await api("/experiments/"+encodeURIComponent(chosen[0])+"/compare/"+encodeURIComponent(chosen[1]));$("compareResult").classList.remove("hidden");$("compareMetrics").innerHTML='<div class="metric"><span>Pass-rate delta</span><strong class="'+(r.metrics.pass_rate.delta>=0?"good":"bad")+'">'+pct(r.metrics.pass_rate.delta)+'</strong></div><div class="metric"><span>Confidence delta</span><strong>'+Number(r.average_confidence_delta).toFixed(3)+'</strong></div><div class="metric"><span>Latency delta</span><strong>'+ms(r.average_duration_delta)+'</strong></div><div class="metric"><span>Verdict</span><strong class="'+(r.verdict==="improved"?"good":r.verdict==="regressed"?"bad":"muted")+'">'+escapeHtml(r.verdict)+'</strong></div>';$("compareDetails").textContent=JSON.stringify(r,null,2)}catch(e){alert("Comparison failed: "+e.message)}}
async function refreshOperational(){try{$("jobs").textContent=JSON.stringify(await api("/jobs?limit=10"),null,2)}catch(e){$("jobs").textContent="Unable to load jobs: "+e.message}try{$("runs").textContent=JSON.stringify(await api("/runs?limit=10"),null,2)}catch(e){$("runs").textContent="Unable to load runs: "+e.message}}
init().catch(e=>{console.error(e);$("investResult").textContent="Unable to initialize: "+e.message;setStatus("investStatus","Backend unavailable","bad")});setInterval(refreshOperational,5000);setInterval(loadExperiments,10000);
</script>
</body></html>"""


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return HTML
