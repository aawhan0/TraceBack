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
.shell{max-width:1240px;margin:auto;padding:28px 22px 56px}.topbar{display:flex;justify-content:space-between;align-items:center;gap:20px;margin-bottom:28px}.brand{display:flex;align-items:center;gap:12px}.mark{width:38px;height:38px;border-radius:11px;background:#172033;color:white;display:grid;place-items:center;font-weight:800}h1{font-size:24px;letter-spacing:-.03em;margin:0}h2{font-size:17px;margin:0}h3{font-size:14px;margin:0}p{color:#667085;margin:5px 0 0;font-size:13px}.pill{font-size:12px;padding:6px 10px;border:1px solid #dbe1ea;border-radius:999px;background:white;color:#475467}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.wide{grid-column:1/-1}.card{background:#fff;border:1px solid #e1e6ee;border-radius:16px;padding:20px;box-shadow:0 2px 8px #1018280a}.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:16px}label{display:block;font-size:12px;font-weight:700;color:#475467;margin:12px 0 5px}input,select{width:100%;padding:10px 11px;border:1px solid #d0d5dd;border-radius:9px;background:#fff;color:#172033;outline:none}input:focus,select:focus{border-color:#98a2b3;box-shadow:0 0 0 3px #66708514}button{border:1px solid #172033;border-radius:9px;padding:10px 13px;background:#172033;color:#fff;font-weight:700;cursor:pointer}button:hover{opacity:.92}button.secondary{background:#fff;color:#172033;border-color:#d0d5dd}.actions{display:flex;gap:8px;margin-top:14px}.actions button{flex:1}.status{font-size:12px;font-weight:700;margin-top:10px;min-height:18px}.status.good{color:#067647}.status.bad{color:#b42318}.status.muted{color:#667085}.result{margin:10px 0 0;padding:12px;border-radius:10px;background:#f8fafc;border:1px solid #edf0f4;white-space:pre-wrap;overflow:auto;max-height:280px;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;color:#344054}.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}.metric{padding:13px;border-radius:11px;background:#f8fafc;border:1px solid #edf0f4}.metric span{display:block;font-size:11px;color:#667085}.metric strong{display:block;font-size:19px;margin-top:3px}.table-wrap{overflow:auto;margin-top:8px}table{width:100%;border-collapse:collapse;font-size:13px}th{text-transform:uppercase;font-size:10px;letter-spacing:.06em;color:#667085}th,td{text-align:left;padding:11px 9px;border-bottom:1px solid #eef1f5}tbody tr:hover{background:#fafbfc}.good{color:#067647}.bad{color:#b42318}.muted{color:#667085}.empty{text-align:center;padding:24px;color:#667085}.config{display:grid;grid-template-columns:1.2fr 150px 1fr 38px;gap:8px;margin-bottom:8px}.config button{background:#fff;color:#b42318;border-color:#f0c4c4;padding:8px}.section-note{padding:10px 12px;background:#f8fafc;border-radius:9px;color:#667085;font-size:12px;margin-bottom:12px}.hidden{display:none}.loading{opacity:.65}@media(max-width:820px){.grid{grid-template-columns:1fr}.wide{grid-column:auto}.metric-grid{grid-template-columns:repeat(2,1fr)}.config{grid-template-columns:1fr 1fr}.topbar{align-items:flex-start}}
</style></head>
<body><div class="shell"><header class="topbar"><div class="brand"><div class="mark">T</div><div><h1>Traceback</h1><p>LLM incident evaluation workspace</p></div></div><span class="pill">Backend connected</span></header><div class="grid">
<section class="card"><div class="card-head"><div><h2>Investigate an incident</h2><p>Run one scenario through the live investigation contract.</p></div></div><label>Scenario</label><select id="scenario"></select><label>Mode</label><select id="investMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select><label>Model <span class="muted">(LLM only)</span></label><input id="investModel" placeholder="llama3.2"><button id="investButton" style="margin-top:14px;width:100%">Run investigation</button><div id="investStatus" class="status muted">Ready.</div><pre id="investResult" class="result">Choose a scenario and run an investigation.</pre></section>
<section class="card"><div class="card-head"><div><h2>Run a benchmark</h2><p>Persist a repeatable experiment against the core dataset.</p></div></div><label>Experiment name</label><input id="benchName" value="ui-benchmark"><label>Mode</label><select id="benchMode"><option value="baseline">Baseline</option><option value="llm">LLM</option></select><label>Model <span class="muted">(LLM only)</span></label><input id="benchModel" placeholder="llama3.2"><label>Repetitions</label><input id="benchReps" type="number" min="1" max="100" value="3"><button id="benchButton" style="margin-top:14px;width:100%">Run benchmark</button><div id="benchStatus" class="status muted">Ready.</div><pre id="benchResult" class="result">No benchmark run yet.</pre></section>
<section class="card wide"><div class="card-head"><div><h2>Experiment matrix</h2><p>Compare multiple configurations on the same immutable dataset.</p></div><span class="pill">Comparison-ready</span></div><div class="config" style="grid-template-columns:1fr 1fr"><div><label>Matrix name</label><input id="matrixName" value="ui-matrix"></div><div><label>Repetitions</label><input id="matrixReps" type="number" min="1" max="100" value="3"></div></div><div class="section-note">The first configuration is the comparison baseline. Add candidates to test different modes or models.</div><div id="configs"></div><div class="actions"><button id="addConfigButton" class="secondary">+ Add configuration</button><button id="matrixButton">Run matrix</button></div><div id="matrixStatus" class="status muted">Ready.</div><pre id="matrixResult" class="result">Add configurations, then run the matrix.</pre></section>
<section class="card wide"><div class="card-head"><div><h2>Experiment history</h2><p>Persisted results from the experiment repository.</p></div><div class="actions" style="margin:0"><button id="refreshExperimentsButton" class="secondary">Refresh</button><button id="compareSelectedButton" class="secondary">Compare selected</button></div></div><div id="experiments"><div class="empty">Loading experiments…</div></div><div id="compareResult" class="hidden"><h3 style="margin-top:18px">Comparison</h3><div id="compareMetrics" class="metric-grid"></div><pre id="compareDetails" class="result"></pre></div></section>
<section class="card"><div class="card-head"><div><h2>Recent jobs</h2><p>Operational queue state</p></div></div><pre id="jobs" class="result">Loading…</pre></section><section class="card"><div class="card-head"><div><h2>Recent investigation runs</h2><p>Latest persisted evaluations</p></div></div><pre id="runs" class="result">Loading…</pre></section></div></div>
<script>
const $=id=>document.getElementById(id);
let selectedExperimentIds=new Set();

async function api(path,options={}){
  const r=await fetch(path,options);
  const text=await r.text();
  let data;
  try{data=JSON.parse(text)}catch{data=text}
  if(!r.ok)throw Error(typeof data==="string"?data:(data.detail||data.message||JSON.stringify(data)));
  return data;
}

function setStatus(id,msg,kind="muted"){
  const e=$(id);
  e.textContent=msg;
  e.className="status "+kind;
}

function pct(v){return (Number(v)*100).toFixed(1)+"%"}
function ms(v){return Number(v).toFixed(3)+" ms"}
function escapeHtml(s){
  return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}
function scenarioIds(){return [...$("scenario").options].map(o=>o.value)}

function addConfig(name="",mode="baseline",model=""){
  const row=document.createElement("div");
  row.className="config";
  const nameInput=document.createElement("input");
  nameInput.className="cfg-name";
  nameInput.placeholder="configuration name";
  nameInput.value=name;
  const modeSelect=document.createElement("select");
  modeSelect.className="cfg-mode";
  modeSelect.innerHTML='<option value="baseline">baseline</option><option value="llm">llm</option>';
  modeSelect.value=mode;
  const modelInput=document.createElement("input");
  modelInput.className="cfg-model";
  modelInput.placeholder="model (for LLM)";
  modelInput.value=model;
  const removeButton=document.createElement("button");
  removeButton.type="button";
  removeButton.title="Remove";
  removeButton.textContent="×";
  removeButton.addEventListener("click",()=>row.remove());
  row.append(nameInput,modeSelect,modelInput,removeButton);
  $("configs").appendChild(row);
}

async function investigate(){
  setStatus("investStatus","Running investigation…");
  $("investResult").textContent="";
  try{
    const body={scenario_id:$("scenario").value,mode:$("investMode").value};
    if($("investModel").value)body.model=$("investModel").value;
    const result=await api("/investigations",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    $("investResult").textContent=JSON.stringify(result,null,2);
    setStatus("investStatus",result.passed?"Evaluation passed":"Completed — evaluation failed",result.passed?"good":"bad");
    await refreshOperational();
  }catch(error){
    $("investResult").textContent=error.message;
    setStatus("investStatus","Request failed","bad");
  }
}

async function benchmark(){
  setStatus("benchStatus","Running benchmark…");
  $("benchResult").textContent="";
  try{
    const body={name:$("benchName").value,scenario_ids:scenarioIds(),repetitions:Number($("benchReps").value),mode:$("benchMode").value};
    if($("benchModel").value)body.model=$("benchModel").value;
    const result=await api("/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    $("benchResult").textContent=JSON.stringify(result,null,2);
    setStatus("benchStatus",result.regression_passed?"Regression gate passed":"Regression gate failed",result.regression_passed?"good":"bad");
    await loadExperiments();
  }catch(error){
    $("benchResult").textContent=error.message;
    setStatus("benchStatus","Request failed","bad");
  }
}

async function matrix(){
  setStatus("matrixStatus","Running matrix…");
  $("matrixResult").textContent="";
  try{
    const rows=[...document.querySelectorAll("#configs .config")];
    const configurations=rows.map(row=>({
      name:row.querySelector(".cfg-name").value,
      mode:row.querySelector(".cfg-mode").value,
      model:row.querySelector(".cfg-model").value||null
    }));
    if(configurations.length<2)throw Error("Add at least two configurations.");
    const body={
      matrix_id:$("matrixName").value,
      scenario_ids:scenarioIds(),
      configurations,
      repetitions:Number($("matrixReps").value),
      min_pass_rate:1
    };
    const result=await api("/experiments/matrix",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    $("matrixResult").textContent=JSON.stringify(result,null,2);
    setStatus("matrixStatus","Matrix completed • best: "+result.best_experiment_id,"good");
    await loadExperiments();
  }catch(error){
    $("matrixResult").textContent=error.message;
    setStatus("matrixStatus","Request failed","bad");
  }
}

function toggleExperiment(id,checked){
  if(checked)selectedExperimentIds.add(id);
  else selectedExperimentIds.delete(id);
}

async function loadExperiments(){
  try{
    const experiments=await api("/experiments?limit=30");
    if(!experiments.length){
      $("experiments").innerHTML='<div class="empty">No persisted experiments yet.</div>';
      return;
    }
    const visibleIds=new Set(experiments.map(item=>item.experiment_id));
    selectedExperimentIds=new Set([...selectedExperimentIds].filter(id=>visibleIds.has(id)));
    const wrapper=document.createElement("div");
    wrapper.className="table-wrap";
    const table=document.createElement("table");
    table.innerHTML='<thead><tr><th></th><th>Name</th><th>Pass rate</th><th>Runs</th><th>Regression</th><th>Created</th></tr></thead>';
    const tbody=document.createElement("tbody");
    experiments.forEach(item=>{
      const row=document.createElement("tr");
      const checkboxCell=document.createElement("td");
      const checkbox=document.createElement("input");
      checkbox.type="checkbox";
      checkbox.name="exp";
      checkbox.value=item.experiment_id;
      checkbox.checked=selectedExperimentIds.has(item.experiment_id);
      checkbox.addEventListener("change",()=>toggleExperiment(item.experiment_id,checkbox.checked));
      checkboxCell.appendChild(checkbox);
      const nameCell=document.createElement("td");
      const strong=document.createElement("strong");
      strong.textContent=item.name;
      nameCell.appendChild(strong);
      const passCell=document.createElement("td");
      passCell.textContent=pct(item.pass_rate);
      const runsCell=document.createElement("td");
      runsCell.textContent=item.passed_runs+"/"+item.total_runs;
      const regressionCell=document.createElement("td");
      regressionCell.textContent=item.regression_passed===null?"—":item.regression_passed?"PASS":"FAIL";
      regressionCell.className=item.regression_passed===false?"bad":"good";
      const createdCell=document.createElement("td");
      createdCell.textContent=new Date(item.created_at).toLocaleString();
      row.append(checkboxCell,nameCell,passCell,runsCell,regressionCell,createdCell);
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrapper.appendChild(table);
    $("experiments").replaceChildren(wrapper);
  }catch(error){
    $("experiments").innerHTML='<div class="empty">Unable to load experiments: '+escapeHtml(error.message)+'</div>';
  }
}

async function compareSelected(){
  const chosen=[...selectedExperimentIds];
  if(chosen.length!==2){alert("Select exactly two experiments.");return}
  try{
    const result=await api("/experiments/"+encodeURIComponent(chosen[0])+"/compare/"+encodeURIComponent(chosen[1]));
    $("compareResult").classList.remove("hidden");
    $("compareMetrics").innerHTML=
      '<div class="metric"><span>Pass-rate delta</span><strong class="'+(result.metrics.pass_rate.delta>=0?"good":"bad")+'">'+pct(result.metrics.pass_rate.delta)+'</strong></div>'+ 
      '<div class="metric"><span>Confidence delta</span><strong>'+Number(result.metrics.average_confidence.delta).toFixed(3)+'</strong></div>'+ 
      '<div class="metric"><span>Latency delta</span><strong>'+ms(result.metrics.average_duration_ms.delta)+'</strong></div>'+ 
      '<div class="metric"><span>Verdict</span><strong class="'+(result.verdict==="improved"?"good":result.verdict==="regressed"?"bad":"muted")+'">'+escapeHtml(result.verdict)+'</strong></div>';
    $("compareDetails").textContent=JSON.stringify(result,null,2);
  }catch(error){
    alert("Comparison failed: "+error.message);
  }
}

async function refreshOperational(){
  try{$("jobs").textContent=JSON.stringify(await api("/jobs?limit=10"),null,2)}catch(error){$("jobs").textContent="Unable to load jobs: "+error.message}
  try{$("runs").textContent=JSON.stringify(await api("/runs?limit=10"),null,2)}catch(error){$("runs").textContent="Unable to load runs: "+error.message}
}

async function init(){
  try{
    const scenarios=await api("/scenarios");
    $("scenario").replaceChildren(...scenarios.map(item=>{
      const option=document.createElement("option");
      option.value=item.id;
      option.textContent=item.title;
      return option;
    }));
    addConfig("baseline","baseline","");
    addConfig("candidate","llm","");
    await refreshOperational();
    await loadExperiments();
  }catch(error){
    console.error(error);
    $("investResult").textContent="Unable to initialize: "+error.message;
    setStatus("investStatus","Backend unavailable","bad");
  }
}

$("investButton").addEventListener("click",investigate);
$("benchButton").addEventListener("click",benchmark);
$("matrixButton").addEventListener("click",matrix);
$("addConfigButton").addEventListener("click",()=>addConfig());
$("refreshExperimentsButton").addEventListener("click",loadExperiments);
$("compareSelectedButton").addEventListener("click",compareSelected);

init();
setInterval(refreshOperational,5000);
setInterval(loadExperiments,10000);
</script></body></html>"""

@router.get("", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(HTML)
