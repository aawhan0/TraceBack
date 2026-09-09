from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ui", tags=["ui"])

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Traceback Evaluation Workspace</title>
<style>
:root{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#18212f;background:#f4f6f8}
*{box-sizing:border-box}body{max-width:1180px;margin:0 auto;padding:28px 20px}
header{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:22px}
h1,h2,h3{margin:0 0 8px}p{margin:6px 0;color:#5b6675}.badge{padding:6px 10px;border-radius:999px;background:#e8edf3;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.wide{grid-column:1/-1}
.card{background:#fff;border:1px solid #dce2e8;border-radius:12px;padding:18px;box-shadow:0 1px 2px #0000000a}
label{display:block;font-size:13px;font-weight:600;margin:10px 0 4px}
input,select,button{width:100%;padding:10px;border:1px solid #cbd3dc;border-radius:8px;font:inherit}
button{background:#18212f;color:#fff;border-color:#18212f;cursor:pointer;font-weight:600}
button.secondary{background:#fff;color:#18212f}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
pre{white-space:pre-wrap;overflow:auto;background:#f7f8fa;border-radius:8px;padding:12px;min-height:70px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:9px;border-bottom:1px solid #e8ebef}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:12px 0}
.metric{padding:12px;background:#f7f8fa;border-radius:8px}.metric strong{display:block;font-size:20px}
.good{color:#16733a}.bad{color:#b42318}.muted{color:#667085}
.config{display:grid;grid-template-columns:1fr 120px 1fr 34px;gap:7px;align-items:end;margin-bottom:8px}
.config button{padding:9px;background:#fff;color:#b42318;border-color:#d9a8a8}
.status{margin-top:8px;font-size:13px}.hidden{display:none}
@media(max-width:800px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}.metric-grid{grid-template-columns:repeat(2,1fr)}.config{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<header><div><h1>Traceback</h1><p>LLM incident evaluation workspace</p></div><span class="badge">backend-driven</span></header>

<div class="grid">
<section class="card">
<h2>Investigate</h2><p>Run a single scenario through the existing investigation contract.</p>
<label>Scenario</label><select id="scenario"></select>
<label>Mode</label><select id="investMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select>
<label>Model</label><input id="investModel" placeholder="llama3.2">
<button style="margin-top:10px" onclick="investigate()">Run investigation</button>
<div id="investStatus" class="status"></div><pre id="investResult">Ready.</pre>
</section>

<section class="card">
<h2>Benchmark</h2><p>Persist a repeatable experiment against the immutable core dataset.</p>
<label>Name</label><input id="benchName" value="ui-benchmark">
<label>Mode</label><select id="benchMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select>
<label>Model</label><input id="benchModel" placeholder="llama3.2">
<label>Repetitions</label><input id="benchReps" type="number" min="1" max="100" value="3">
<button style="margin-top:10px" onclick="benchmark()">Run benchmark</button>
<div id="benchStatus" class="status"></div><pre id="benchResult">No benchmark run yet.</pre>
</section>

<section class="card wide">
<h2>Experiment matrix</h2><p>Run multiple configurations against one dataset and compare each candidate to the first configuration.</p>
<label>Matrix name</label><input id="matrixName" value="ui-matrix">
<label>Repetitions</label><input id="matrixReps" type="number" min="1" max="100" value="3">
<div id="configs"></div>
<div class="actions"><button class="secondary" onclick="addConfig()">Add configuration</button><button onclick="matrix()">Run matrix</button></div>
<div id="matrixStatus" class="status"></div><pre id="matrixResult">Add configurations, then run.</pre>
</section>

<section class="card wide">
<h2>Persisted experiments</h2><p>History comes directly from the experiment repository.</p>
<div class="actions"><button class="secondary" onclick="loadExperiments()">Refresh</button><button class="secondary" onclick="compareSelected()">Compare selected</button></div>
<div id="experiments" style="overflow:auto;margin-top:10px">Loading…</div>
<div id="compareResult" class="hidden"><h3 style="margin-top:16px">Comparison</h3><div id="compareMetrics" class="metric-grid"></div><pre id="compareDetails"></pre></div>
</section>

<section class="card">
<h2>Recent jobs</h2><pre id="jobs">Loading…</pre>
</section>
<section class="card">
<h2>Recent investigation runs</h2><pre id="runs">Loading…</pre>
</section>
</div>

<script>
const $=id=>document.getElementById(id);
async function api(path,options={}){const r=await fetch(path,options);const text=await r.text();let data;try{data=JSON.parse(text)}catch{data=text}if(!r.ok)throw Error(typeof data==="string"?data:(data.message||JSON.stringify(data)));return data}
function setStatus(id,msg){$(id).textContent=msg||""}
function pct(v){return (Number(v)*100).toFixed(1)+"%"}
function ms(v){return Number(v).toFixed(1)+" ms"}

async function init(){
 const scenarios=await api("/scenarios");
 $("scenario").innerHTML=scenarios.map(x=>'<option value="'+x.id+'">'+escapeHtml(x.title)+'</option>').join("");
 addConfig("baseline","baseline","");
 addConfig("candidate","llm","");
 await refreshOperational(); await loadExperiments();
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]))}
function configSpec(mode,model){return mode==="baseline"?"baseline":"llm:"+model}
function addConfig(name="",mode="baseline",model=""){
 const row=document.createElement("div");row.className="config";
 row.innerHTML='<input class="cfg-name" placeholder="name" value="'+escapeHtml(name)+'">'+
 '<select class="cfg-mode"><option value="baseline">baseline</option><option value="llm">llm</option></select>'+
 '<input class="cfg-model" placeholder="model (for LLM)" value="'+escapeHtml(model)+'">'+
 '<button title="Remove" onclick="this.parentElement.remove()">×</button>';
 row.querySelector(".cfg-mode").value=mode; $("configs").appendChild(row);
}
async function investigate(){
 setStatus("investStatus","Running…");$("investResult").textContent="";
 try{const b={scenario_id:$("scenario").value,mode:$("investMode").value};if($("investModel").value)b.model=$("investModel").value;
 const r=await api("/investigations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
 $("investResult").textContent=JSON.stringify(r,null,2);setStatus("investStatus",r.passed?"Passed evaluation":"Completed with evaluation failure");await refreshOperational();
 }catch(e){$("investResult").textContent=e.message;setStatus("investStatus","Request failed")}
}
async function benchmark(){
 setStatus("benchStatus","Running benchmark…");$("benchResult").textContent="";
 try{const b={name:$("benchName").value,scenario_ids:await scenarioIds(),repetitions:Number($("benchReps").value),mode:$("benchMode").value};
 if($("benchModel").value)b.model=$("benchModel").value;const r=await api("/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)});
 $("benchResult").textContent=JSON.stringify(r,null,2);setStatus("benchStatus",r.regression_passed?"Regression gate passed":"Regression gate failed");await loadExperiments();
 }catch(e){$("benchResult").textContent=e.message;setStatus("benchStatus","Request failed")}
}
async function matrix(){
 setStatus("matrixStatus","Running matrix…");$("matrixResult").textContent="";
 try{const rows=[...document.querySelectorAll(".config")];const configurations=rows.map(row=>({name:row.querySelector(".cfg-name").value,mode:row.querySelector(".cfg-mode").value,model:row.querySelector(".cfg-model").value||null}));
 const r=await api("/experiments/matrix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({matrix_id:$("matrixName").value,scenario_ids:await scenarioIds(),configurations,repetitions:Number($("matrixReps").value),min_pass_rate:1})});
 $("matrixResult").textContent=JSON.stringify(r,null,2);setStatus("matrixStatus","Matrix completed; best experiment: "+r.best_experiment_id);await loadExperiments();
 }catch(e){$("matrixResult").textContent=e.message;setStatus("matrixStatus","Request failed")}
}
async function scenarioIds(){return [...$("scenario").options].map(o=>o.value)}
async function loadExperiments(){
 try{const xs=await api("/experiments?limit=30");if(!xs.length){$("experiments").textContent="No persisted experiments yet.";return}
 $("experiments").innerHTML='<table><thead><tr><th></th><th>Name</th><th>Pass rate</th><th>Runs</th><th>Regression</th><th>Created</th></tr></thead><tbody>'+
 xs.map((x,i)=>'<tr><td><input type="radio" name="exp" value="'+escapeHtml(x.experiment_id)+'" data-index="'+i+'"></td><td>'+escapeHtml(x.name)+'</td><td>'+pct(x.pass_rate)+'</td><td>'+x.passed_runs+"/"+x.total_runs+'</td><td class="'+(x.regression_passed===false?"bad":"good")+'">'+(x.regression_passed===null?"—":x.regression_passed?"PASS":"FAIL")+'</td><td>'+new Date(x.created_at).toLocaleString()+'</td></tr>').join("")+'</tbody></table>';
 window.experiments=xs;
 }catch(e){$("experiments").textContent="Unable to load experiments: "+e.message}
}
async function compareSelected(){
 const chosen=[...document.querySelectorAll('input[name="exp"]:checked')].map(x=>x.value);
 if(chosen.length!==2){alert("Select exactly two experiments.");return}
 try{const r=await api("/experiments/"+encodeURIComponent(chosen[0])+"/compare/"+encodeURIComponent(chosen[1]));
 $("compareResult").classList.remove("hidden");
 $("compareMetrics").innerHTML='<div class="metric"><span>Pass-rate delta</span><strong class="'+(r.pass_rate_delta>=0?"good":"bad")+'">'+pct(r.pass_rate_delta)+'</strong></div>'+
 '<div class="metric"><span>Confidence delta</span><strong>'+Number(r.average_confidence_delta).toFixed(3)+'</strong></div>'+
 '<div class="metric"><span>Latency delta</span><strong>'+ms(r.average_duration_delta)+'</strong></div>'+
 '<div class="metric"><span>Verdict</span><strong class="'+(r.verdict==="improved"?"good":r.verdict==="regressed"?"bad":"muted")+'">'+escapeHtml(r.verdict)+'</strong></div>';
 $("compareDetails").textContent=JSON.stringify(r,null,2);
 }catch(e){alert("Comparison failed: "+e.message)}
}
async function refreshOperational(){
 try{$("jobs").textContent=JSON.stringify(await api("/jobs?limit=10"),null,2)}catch(e){$("jobs").textContent="Unable to load jobs"}
 try{$("runs").textContent=JSON.stringify(await api("/runs?limit=10"),null,2)}catch(e){$("runs").textContent="Unable to load runs"}
}
init().catch(e=>{console.error(e);$("investResult").textContent="Unable to initialize: "+e.message});
setInterval(refreshOperational,5000);setInterval(loadExperiments,10000);
</script>
</body></html>"""


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return HTML
