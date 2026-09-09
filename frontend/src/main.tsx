import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Activity, ArrowLeft, Check, ChevronDown, CircleAlert, Clock3, FlaskConical, History, LoaderCircle, Play, RotateCcw, Search, Server, SlidersHorizontal, Sparkles, X } from 'lucide-react'
import './styles.css'

type Scenario = { id: string; title: string }
type Diagnosis = { root_cause: string; evidence: string[]; confidence: number; recommended_action: string }
type Investigation = {
  scenario_id: string; mode: 'baseline' | 'llm'; provider: string; diagnosis: Diagnosis
  root_cause_match: boolean; evidence_recall: number; evidence_precision: number
  confidence_valid: boolean; action_present: boolean; passed: boolean; run_id: string
  duration_ms: number; created_at: string
}
type Experiment = {
  experiment_id: string; name: string; dataset_name: string; dataset_version: string
  dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number
  pass_rate: number; regression_passed: boolean | null
  provenance?: { provider: string; model: string | null }
}

type View = 'investigate' | 'experiments' | 'history'
const API = (import.meta as ImportMeta & { env?: Record<string,string> }).env?.VITE_API_URL || ''

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  const body = text ? JSON.parse(text) : null
  if (!response.ok) throw new Error(body?.detail || body?.message || `Request failed (${response.status})`)
  return body as T
}

function App() {
  const [view, setView] = useState<View>('investigate')
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenario, setScenario] = useState('')
  const [mode, setMode] = useState<'baseline'|'llm'>('baseline')
  const [model, setModel] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<Investigation | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [detailExperiment, setDetailExperiment] = useState<Experiment | null>(null)
  const [runList, setRunList] = useState<Array<Record<string, unknown>>>([])

  useEffect(() => {
    void Promise.all([
      api<Scenario[]>('/scenarios').then(data => { setScenarios(data); if (data[0]) setScenario(data[0].id) }),
      api<Experiment[]>('/experiments?limit=50').then(setExperiments).catch(() => setExperiments([])),
      api<Array<Record<string, unknown>>>('/runs?limit=30').then(setRunList).catch(() => setRunList([])),
    ]).catch(e => setError(e.message))
  }, [])

  const activeScenario = useMemo(() => scenarios.find(s => s.id === scenario), [scenarios, scenario])

  async function investigate() {
    setBusy(true); setError(''); setResult(null)
    try {
      const payload: Record<string, unknown> = { scenario_id: scenario, mode }
      if (mode === 'llm' && model.trim()) payload.model = model.trim()
      const data = await api<Investigation>('/investigations', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) })
      setResult(data)
      setRunList(await api<Array<Record<string, unknown>>>('/runs?limit=30'))
    } catch (e) { setError(e instanceof Error ? e.message : 'Investigation failed') }
    finally { setBusy(false) }
  }

  async function refreshExperiments() {
    setError('')
    try { setExperiments(await api<Experiment[]>('/experiments?limit=50')) } catch (e) { setError(e instanceof Error ? e.message : 'Unable to load experiments') }
  }

  const pageTitle = view === 'investigate' ? 'Investigate' : view === 'experiments' ? 'Experiments' : 'History'
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => {setView('investigate'); setResult(null)}} aria-label="TraceBack home">
          <span className="brand-mark">T</span><span>TraceBack</span>
        </button>
        <nav className="nav">
          <NavItem icon={<Search size={16}/>} label="Investigate" active={view==='investigate'} onClick={() => setView('investigate')}/>
          <NavItem icon={<FlaskConical size={16}/>} label="Experiments" active={view==='experiments'} onClick={() => {setView('experiments'); void refreshExperiments()}}/>
          <NavItem icon={<History size={16}/>} label="History" active={view==='history'} onClick={() => {setView('history'); void api<Array<Record<string,unknown>>>('/runs?limit=30').then(setRunList).catch(e=>setError(e.message))}}/>
        </nav>
        <div className="sidebar-bottom"><div className="connection"><span className="dot"/> API connected</div></div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div><div className="eyebrow">Workspace</div><h1>{pageTitle}</h1></div>
          <div className="top-actions">{view === 'experiments' && <button className="icon-btn" onClick={() => void refreshExperiments()} title="Refresh"><RotateCcw size={16}/></button>}<span className="status-chip"><span className="dot"/> Local</span></div>
        </header>

        {error && <div className="error-banner"><CircleAlert size={16}/><span>{error}</span><button onClick={() => setError('')}><X size={15}/></button></div>}

        {view === 'investigate' && (
          <section className="workspace">
            <div className="workspace-copy">
              <div className="kicker"><Sparkles size={15}/> Incident diagnosis</div>
              <h2>Trace the failure.</h2>
              <p>Run a deterministic baseline or a local LLM investigation against a real scenario.</p>
            </div>

            <div className="investigation-panel">
              <div className="field-block"><label>Scenario</label><select value={scenario} onChange={e=>setScenario(e.target.value)}><option value="">Select a scenario</option>{scenarios.map(s=><option key={s.id} value={s.id}>{s.title}</option>)}</select></div>
              <div className="field-row">
                <div className="field-block"><label>Mode</label><div className="segmented"><button className={mode==='baseline'?'selected':''} onClick={()=>setMode('baseline')}>Baseline</button><button className={mode==='llm'?'selected':''} onClick={()=>setMode('llm')}>LLM</button></div></div>
                <div className="field-block"><label>Model <span className="optional">LLM only</span></label><input disabled={mode!=='llm'} value={model} onChange={e=>setModel(e.target.value)} placeholder="llama3.2"/></div>
              </div>
              <div className="panel-footer"><span className="selection-note">{activeScenario?.id || 'Choose a scenario'}</span><button className="primary-btn" disabled={!scenario || busy} onClick={() => void investigate()}>{busy ? <><LoaderCircle size={16} className="spin"/> Investigating</> : <><Play size={16}/> Run investigation</>}</button></div>
            </div>

            {result ? <InvestigationResult result={result} scenario={activeScenario?.title || result.scenario_id}/> : <div className="quiet-state"><Activity size={18}/><span>Your diagnosis will appear here.</span></div>}
          </section>
        )}

        {view === 'experiments' && <ExperimentsPage experiments={experiments} selected={selected} setSelected={setSelected} detail={detailExperiment} setDetail={setDetailExperiment} refresh={refreshExperiments}/>}        
        {view === 'history' && <HistoryPage runs={runList}/>}      
      </main>
    </div>
  )
}

function NavItem({icon,label,active,onClick}:{icon:React.ReactNode;label:string;active:boolean;onClick:()=>void}) {
  return <button className={`nav-item ${active?'active':''}`} onClick={onClick}>{icon}<span>{label}</span></button>
}

function InvestigationResult({result, scenario}:{result:Investigation;scenario:string}) {
  const metrics = [
    ['Root cause', result.root_cause_match], ['Evidence recall', result.evidence_recall], ['Evidence precision', result.evidence_precision], ['Action', result.action_present]
  ] as Array<[string, boolean|number]>
  return <div className="result-wrap">
    <div className="result-head"><div><div className="result-scenario">{scenario}</div><h3>Investigation result</h3></div><span className={`pass-pill ${result.passed?'pass':'fail'}`}>{result.passed ? <Check size={14}/> : <X size={14}/>} {result.passed?'Passed':'Needs review'}</span></div>
    <div className="diagnosis-grid">
      <article className="result-section"><div className="section-label">Root cause</div><p className="root-cause">{result.diagnosis.root_cause}</p></article>
      <article className="result-section"><div className="section-label">Recommended action</div><p>{result.diagnosis.recommended_action}</p></article>
    </div>
    <article className="result-section"><div className="section-label">Evidence</div><div className="evidence-list">{result.diagnosis.evidence.map((item,i)=><div className="evidence-row" key={`${item}-${i}`}><span className="evidence-id">E-{String(i+1).padStart(2,'0')}</span><span>{item}</span></div>)}</div></article>
    <div className="result-footer"><div className="metric-inline"><span>Confidence</span><strong>{Math.round(result.diagnosis.confidence*100)}%</strong></div><div className="metric-inline"><span>Duration</span><strong>{Math.round(result.duration_ms)} ms</strong></div><div className="metric-inline"><span>Provider</span><strong>{result.provider}</strong></div></div>
    <div className="checks">{metrics.map(([label,value])=><div key={label} className="check-row"><span>{label}</span><span className={typeof value==='boolean' ? (value?'good':'bad') : ''}>{typeof value==='number' ? `${(value*100).toFixed(0)}%` : value?'Pass':'Fail'}</span></div>)}</div>
  </div>
}

function ExperimentsPage({experiments, selected, setSelected, detail, setDetail, refresh}:{experiments:Experiment[];selected:string[];setSelected:(v:string[])=>void;detail:Experiment|null;setDetail:(v:Experiment|null)=>void;refresh:()=>Promise<void>}) {
  return <section className="list-page">
    <div className="page-intro"><div><h2>Compare measured behavior.</h2><p>Browse persisted benchmark runs and open one when you need the details.</p></div></div>
    {detail ? <div className="detail-view"><button className="back-btn" onClick={()=>setDetail(null)}><ArrowLeft size={15}/> All experiments</button><div className="detail-title"><div><div className="eyebrow">Experiment</div><h2>{detail.name}</h2></div><span className={`pass-pill ${detail.regression_passed===false?'fail':'pass'}`}>{detail.regression_passed===false?'Regression failed':'Regression passed'}</span></div><div className="detail-stats"><Stat label="Pass rate" value={`${(detail.pass_rate*100).toFixed(0)}%`}/><Stat label="Runs" value={`${detail.passed_runs}/${detail.total_runs}`}/><Stat label="Dataset" value={`${detail.dataset_name} v${detail.dataset_version}`}/><Stat label="Provider" value={detail.provenance?.provider || '—'}/></div><div className="fingerprint"><span>Fingerprint</span><code>{detail.dataset_fingerprint}</code></div></div> : <>
      <div className="list-tools"><span>{experiments.length} experiments</span><span>{selected.length ? `${selected.length} selected` : 'Select for comparison'}</span></div>
      <div className="experiment-list">{experiments.length ? experiments.map(exp=><button key={exp.experiment_id} className="experiment-row" onClick={()=>setDetail(exp)}><input type="checkbox" checked={selected.includes(exp.experiment_id)} onClick={e=>e.stopPropagation()} onChange={()=>setSelected(selected.includes(exp.experiment_id)?selected.filter(x=>x!==exp.experiment_id):[...selected,exp.experiment_id])}/><div className="exp-name"><strong>{exp.name}</strong><span>{exp.provenance?.provider || 'unknown'}{exp.provenance?.model?` · ${exp.provenance.model}`:''}</span></div><div className="exp-meta"><span>{(exp.pass_rate*100).toFixed(0)}%</span><span>{exp.passed_runs}/{exp.total_runs}</span><span>{formatRelative(exp.created_at)}</span></div><ChevronDown size={16} className="row-chevron"/></button>) : <div className="empty-state"><FlaskConical size={20}/><p>No experiments yet.</p><span>Run a benchmark from the CLI or API to see it here.</span></div>}</div>
    </>}
  </section>
}

function HistoryPage({runs}:{runs:Array<Record<string,unknown>>}) {
  return <section className="list-page"><div className="page-intro"><div><h2>Past investigations.</h2><p>A quiet record of what TraceBack has already evaluated.</p></div></div><div className="history-list">{runs.length ? runs.map((r,i)=>{const id=String(r.run_id||r.id||i);const scenario=String(r.scenario_id||'Investigation');const passed=Boolean(r.passed);return <div className="history-row" key={id}><div className="history-icon">{passed?<Check size={15}/>:<CircleAlert size={15}/>}</div><div className="history-main"><strong>{scenario}</strong><span>{String(r.mode||'baseline')} · {String(r.provider||'baseline')}</span></div><div className={`history-status ${passed?'good':'bad'}`}>{passed?'Passed':'Needs review'}</div><div className="history-time">{r.created_at?formatRelative(String(r.created_at)):''}</div></div>}) : <div className="empty-state"><History size={20}/><p>No investigations yet.</p><span>Run your first investigation to start the history.</span></div>}</div></section>
}
function Stat({label,value}:{label:string;value:string}) { return <div className="stat"><span>{label}</span><strong>{value}</strong></div> }
function formatRelative(date:string) { const diff=Date.now()-new Date(date).getTime(); if(!Number.isFinite(diff)) return date; const m=Math.floor(diff/60000); if(m<1)return 'just now'; if(m<60)return `${m}m ago`; const h=Math.floor(m/60); if(h<24)return `${h}h ago`; return `${Math.floor(h/24)}d ago` }

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>)
