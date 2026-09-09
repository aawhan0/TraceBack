import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { ArrowLeft, Check, ChevronRight, CircleAlert, FlaskConical, History, LoaderCircle, Play, Search, Settings2, X } from 'lucide-react'

type Scenario = { id: string; title: string }
type Diagnosis = { root_cause: string; evidence: string[]; confidence: number; recommended_action: string }
type Investigation = { scenario_id: string; mode: 'baseline' | 'llm'; provider: string; diagnosis: Diagnosis; root_cause_match: boolean; evidence_recall: number; evidence_precision: number; confidence_valid: boolean; action_present: boolean; passed: boolean; run_id: string; duration_ms: number; created_at: string }
type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
type Run = Record<string, unknown>
type View = 'investigate' | 'experiments' | 'history'

const API = import.meta.env.VITE_API_URL || '/api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  const data = text ? JSON.parse(text) : null
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`)
  return data as T
}

function App() {
  const [view, setView] = useState<View>('investigate')
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenario, setScenario] = useState('')
  const [mode, setMode] = useState<'baseline' | 'llm'>('baseline')
  const [model, setModel] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [result, setResult] = useState<Investigation | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [runs, setRuns] = useState<Run[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [experimentDetail, setExperimentDetail] = useState<Experiment | null>(null)

  useEffect(() => {
    void Promise.all([
      api<Scenario[]>('/scenarios').then((items) => { setScenarios(items); if (items[0]) setScenario(items[0].id) }),
      api<Experiment[]>('/experiments?limit=50').then(setExperiments).catch(() => undefined),
      api<Run[]>('/runs?limit=50').then(setRuns).catch(() => undefined),
    ]).catch((error) => setNotice(error instanceof Error ? error.message : 'Unable to connect to TraceBack'))
  }, [])

  const activeScenario = useMemo(() => scenarios.find((item) => item.id === scenario), [scenarios, scenario])

  async function investigate() {
    setBusy(true); setNotice(''); setResult(null)
    try {
      const payload: Record<string, unknown> = { scenario_id: scenario, mode }
      if (mode === 'llm' && model.trim()) payload.model = model.trim()
      const data = await api<Investigation>('/investigations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      setResult(data)
      setRuns(await api<Run[]>('/runs?limit=50'))
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Investigation failed')
    } finally { setBusy(false) }
  }

  async function refreshExperiments() {
    try { setExperiments(await api<Experiment[]>('/experiments?limit=50')) } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load experiments') }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <button className="brand" onClick={() => setView('investigate')}><span className="brand-mark">T</span><span>TraceBack</span></button>
        <div className="nav-group">
          <NavItem icon={<Search size={16} />} label="Investigate" active={view === 'investigate'} onClick={() => setView('investigate')} />
          <NavItem icon={<FlaskConical size={16} />} label="Experiments" active={view === 'experiments'} onClick={() => { setView('experiments'); void refreshExperiments() }} />
          <NavItem icon={<History size={16} />} label="History" active={view === 'history'} onClick={() => { setView('history'); void api<Run[]>('/runs?limit=50').then(setRuns).catch(() => undefined) }} />
        </div>
        <div className="sidebar-footer"><span className="status-dot" /> Local API</div>
      </aside>

      <main className="main">
        <header className="header"><div><span className="overline">TraceBack</span><h1>{view === 'investigate' ? 'Investigate' : view === 'experiments' ? 'Experiments' : 'History'}</h1></div><div className="header-meta"><Settings2 size={16} /> Local</div></header>
        {notice && <div className="notice"><CircleAlert size={16} /><span>{notice}</span><button onClick={() => setNotice('')} aria-label="Dismiss"><X size={15} /></button></div>}
        {view === 'investigate' && <InvestigateView scenarios={scenarios} scenario={scenario} setScenario={setScenario} mode={mode} setMode={setMode} model={model} setModel={setModel} busy={busy} result={result} activeScenario={activeScenario?.title} onRun={investigate} />}
        {view === 'experiments' && <ExperimentsView experiments={experiments} selected={selected} setSelected={setSelected} detail={experimentDetail} setDetail={setExperimentDetail} />}
        {view === 'history' && <HistoryView runs={runs} />}
      </main>
    </div>
  )
}

function NavItem({ icon, label, active, onClick }: { icon: ReactNode; label: string; active: boolean; onClick: () => void }) {
  return <button className={`nav-item ${active ? 'active' : ''}`} onClick={onClick}>{icon}<span>{label}</span></button>
}

function InvestigateView({ scenarios, scenario, setScenario, mode, setMode, model, setModel, busy, result, activeScenario, onRun }: { scenarios: Scenario[]; scenario: string; setScenario: (v: string) => void; mode: 'baseline' | 'llm'; setMode: (v: 'baseline' | 'llm') => void; model: string; setModel: (v: string) => void; busy: boolean; result: Investigation | null; activeScenario?: string; onRun: () => void }) {
  return <section className="content narrow">
    {!result && <div className="intro"><div className="intro-icon"><Search size={18} /></div><div><h2>Trace the failure.</h2><p>Run an investigation against one of TraceBack's production-style scenarios.</p></div></div>}
    <div className="form-panel">
      <div className="field"><label>Incident</label><select value={scenario} onChange={(e) => setScenario(e.target.value)}>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></div>
      <div className="split">
        <div className="field"><label>Mode</label><div className="toggle"><button type="button" className={mode === 'baseline' ? 'selected' : ''} onClick={() => setMode('baseline')}>Baseline</button><button type="button" className={mode === 'llm' ? 'selected' : ''} onClick={() => setMode('llm')}>LLM</button></div></div>
        <div className="field"><label>Model <span>LLM only</span></label><input disabled={mode !== 'llm'} value={model} onChange={(e) => setModel(e.target.value)} placeholder="llama3.2" /></div>
      </div>
      <div className="form-action"><span>{scenario || 'Select an incident'}</span><button type="button" className="primary" disabled={!scenario || busy} onClick={onRun}>{busy ? <><LoaderCircle size={15} className="spin" /> Running</> : <><Play size={15} /> Run investigation</>}</button></div>
    </div>
    {!result && <div className="empty-inline">Results will appear here after the investigation finishes.</div>}
    {result && <InvestigationResult result={result} scenario={activeScenario || result.scenario_id} />}
  </section>
}

function InvestigationResult({ result, scenario }: { result: Investigation; scenario: string }) {
  return <section className="result-card">
    <div className="result-title"><div><span className="overline">{scenario}</span><h2>Investigation result</h2></div><span className={`outcome ${result.passed ? 'pass' : 'fail'}`}>{result.passed ? <Check size={14} /> : <X size={14} />}{result.passed ? 'Passed' : 'Needs review'}</span></div>
    <div className="diagnosis-block"><span className="label">Root cause</span><p className="root-cause">{result.diagnosis.root_cause}</p></div>
    <div className="evidence-block"><span className="label">Evidence</span><div>{result.diagnosis.evidence.map((item, index) => <div className="evidence" key={`${item}-${index}`}><span>E-{String(index + 1).padStart(2, '0')}</span><p>{item}</p></div>)}</div></div>
    <div className="action-block"><span className="label">Recommended action</span><p>{result.diagnosis.recommended_action}</p></div>
    <div className="result-meta"><div><span>Confidence</span><strong>{Math.round(result.diagnosis.confidence * 100)}%</strong></div><div><span>Duration</span><strong>{Math.round(result.duration_ms)} ms</strong></div><div><span>Provider</span><strong>{result.provider}</strong></div></div>
  </section>
}

function ExperimentsView({ experiments, selected, setSelected, detail, setDetail }: { experiments: Experiment[]; selected: string[]; setSelected: (v: string[]) => void; detail: Experiment | null; setDetail: (v: Experiment | null) => void }) {
  if (detail) return <section className="content"><button className="back" onClick={() => setDetail(null)}><ArrowLeft size={15} /> Experiments</button><div className="detail-header"><div><span className="overline">Experiment</span><h2>{detail.name}</h2></div><span className={`outcome ${detail.regression_passed === false ? 'fail' : 'pass'}`}>{detail.regression_passed === false ? 'Regression failed' : 'Regression passed'}</span></div><div className="detail-grid"><Info label="Pass rate" value={`${Math.round(detail.pass_rate * 100)}%`} /><Info label="Runs" value={`${detail.passed_runs}/${detail.total_runs}`} /><Info label="Dataset" value={`${detail.dataset_name} v${detail.dataset_version}`} /><Info label="Provider" value={detail.provenance?.provider || '—'} /></div><div className="fingerprint"><span>Dataset fingerprint</span><code>{detail.dataset_fingerprint}</code></div></section>
  return <section className="content"><div className="page-intro"><div><span className="overline">Measured behavior</span><h2>Experiments</h2><p>Saved benchmark runs, without the dashboard noise.</p></div></div><div className="list-header"><span>{experiments.length} saved</span><span>{selected.length ? `${selected.length} selected` : 'Select two to compare'}</span></div><div className="list">{experiments.length ? experiments.map((experiment) => <button className="list-row" key={experiment.experiment_id} onClick={() => setDetail(experiment)}><input type="checkbox" checked={selected.includes(experiment.experiment_id)} onChange={() => setSelected(selected.includes(experiment.experiment_id) ? selected.filter((id) => id !== experiment.experiment_id) : [...selected, experiment.experiment_id])} onClick={(e) => e.stopPropagation()} /><div className="list-main"><strong>{experiment.name}</strong><span>{experiment.provenance?.provider || 'unknown'}{experiment.provenance?.model ? ` · ${experiment.provenance.model}` : ''}</span></div><div className="list-value"><strong>{Math.round(experiment.pass_rate * 100)}%</strong><span>{experiment.passed_runs}/{experiment.total_runs} · {relative(experiment.created_at)}</span></div><ChevronRight size={15} /></button>) : <Empty icon={<FlaskConical size={18} />} text="No experiments yet." />}</div></section>
}

function HistoryView({ runs }: { runs: Run[] }) {
  return <section className="content"><div className="page-intro"><div><span className="overline">Investigation log</span><h2>History</h2><p>Previous diagnosis runs, kept close to the work.</p></div></div><div className="list">{runs.length ? runs.map((run, index) => { const passed = Boolean(run.passed); return <div className="history-row" key={String(run.run_id || index)}><div className={`history-icon ${passed ? 'pass' : 'fail'}`}>{passed ? <Check size={14} /> : <CircleAlert size={14} />}</div><div className="list-main"><strong>{String(run.scenario_id || 'Investigation')}</strong><span>{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</span></div><div className={`history-outcome ${passed ? 'good' : 'bad'}`}>{passed ? 'Passed' : 'Needs review'}</div><span className="time">{run.created_at ? relative(String(run.created_at)) : ''}</span></div> }) : <Empty icon={<History size={18} />} text="No investigations yet." />}</div></section>
}

function Info({ label, value }: { label: string; value: string }) { return <div className="info"><span>{label}</span><strong>{value}</strong></div> }
function Empty({ icon, text }: { icon: ReactNode; text: string }) { return <div className="empty"><div>{icon}</div><strong>{text}</strong></div> }
function relative(date: string) { const diff = Date.now() - new Date(date).getTime(); if (!Number.isFinite(diff)) return date; const minutes = Math.floor(diff / 60000); if (minutes < 1) return 'just now'; if (minutes < 60) return `${minutes}m ago`; const hours = Math.floor(minutes / 60); if (hours < 24) return `${hours}h ago`; return `${Math.floor(hours / 24)}d ago` }

export default App
