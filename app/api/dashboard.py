from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/ui", tags=["ui"])

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Traceback Investigation Console</title>
<style>
body{font-family:system-ui;max-width:1000px;margin:40px auto;padding:0 20px;background:#f5f7fa;color:#18212f}
.card{background:white;border:1px solid #dfe5ec;border-radius:12px;padding:20px;margin:16px 0}
select,input,button{padding:10px;border:1px solid #cbd3dc;border-radius:8px;margin:5px 0;width:100%;box-sizing:border-box}
button{background:#18212f;color:white;cursor:pointer}.row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
pre{white-space:pre-wrap;background:#f7f8fa;padding:12px;border-radius:8px}
@media(max-width:700px){.row{grid-template-columns:1fr}}
</style></head>
<body>
<h1>Traceback</h1><p>Incident investigation console</p>
<div class="card"><h2>Run investigation</h2>
<label>Scenario</label><select id="scenario"></select>
<label>Mode</label><select id="mode"><option>baseline</option><option>llm</option></select>
<label>Model</label><input id="model" placeholder="llama3.2">
<button onclick="run()">Start investigation</button><pre id="result">Ready.</pre></div>
<div class="row"><div class="card"><h2>Jobs</h2><pre id="jobs">Loading…</pre></div>
<div class="card"><h2>Recent runs</h2><pre id="runs">Loading…</pre></div></div>
<script>
async function get(p,o){const r=await fetch(p,o);if(!r.ok)throw Error(await r.text());return r.json()}
async function init(){const s=await get('/scenarios');scenario.innerHTML=s.map(x=>'<option value="'+x.id+'">'+x.title+'</option>').join('');refresh()}
async function run(){result.textContent='Running…';const b={scenario_id:scenario.value,mode:mode.value};if(model.value)b.model=model.value;try{result.textContent=JSON.stringify(await get('/investigations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}),null,2);refresh()}catch(e){result.textContent='Error: '+e.message}}
async function refresh(){try{jobs.textContent=JSON.stringify(await get('/jobs?limit=10'),null,2)}catch(e){jobs.textContent='Unable to load jobs'}try{runs.textContent=JSON.stringify(await get('/runs?limit=10'),null,2)}catch(e){runs.textContent='Unable to load runs'}}
init();setInterval(refresh,5000)
</script></body></html>"""


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return HTML
