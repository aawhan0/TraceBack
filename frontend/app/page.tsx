'use client'

import { useEffect, useMemo, useState } from 'react'
import { Check, CircleAlert, FlaskConical, History, LoaderCircle, Play, Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { PageHeader } from '@/components/dashboard/page-header'
import { ContentSection } from '@/components/dashboard/content-section'
import { cn } from '@/lib/utils'

type Scenario = { id: string; title: string }
type Diagnosis = { root_cause: string; evidence: string[]; confidence: number; recommended_action: string }
type Investigation = { scenario_id: string; mode: 'baseline' | 'llm'; provider: string; diagnosis: Diagnosis; passed: boolean; duration_ms: number }
type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
type Run = Record<string, unknown>

type View = 'investigate' | 'experiments' | 'history'
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  const data = text ? JSON.parse(text) : null
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`)
  return data as T
}

export default function HomePage() {
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
  const [detail, setDetail] = useState<Experiment | null>(null)

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

  function switchView(next: View) {
    setView(next)
    setDetail(null)
    if (next === 'experiments') void refreshExperiments()
    if (next === 'history') void api<Run[]>('/runs?limit=50').then(setRuns).catch(() => undefined)
  }

  return (
    <div className="space-y-6">
      <PageHeader title={view === 'investigate' ? 'Investigate' : view === 'experiments' ? 'Experiments' : 'History'} description={view === 'investigate' ? 'Trace a production-style failure to its root cause.' : view === 'experiments' ? 'Evaluate saved investigation behavior without dashboard noise.' : 'Review previous diagnosis runs.'} />

      <div className="flex gap-2 border-b border-border pb-2 md:hidden">
        {([['investigate', Search, 'Investigate'], ['experiments', FlaskConical, 'Experiments'], ['history', History, 'History']] as const).map(([key, Icon, label]) => (
          <Button key={key} variant={view === key ? 'secondary' : 'ghost'} size="sm" onClick={() => switchView(key)}>
            <Icon />{label}
          </Button>
        ))}
      </div>

      {notice && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span className="flex-1">{notice}</span><Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setNotice('')}><X /></Button></div>}

      {view === 'investigate' && <Investigate scenarios={scenarios} scenario={scenario} setScenario={setScenario} mode={mode} setMode={setMode} model={model} setModel={setModel} busy={busy} result={result} activeScenario={activeScenario?.title} onRun={investigate} />}
      {view === 'experiments' && <Experiments experiments={experiments} detail={detail} setDetail={setDetail} />}
      {view === 'history' && <History runs={runs} />}

      <div className="hidden md:block pt-1 text-xs text-muted-foreground">TraceBack · local investigation workspace</div>
      <div className="hidden md:flex md:gap-2 text-xs">
        {([['investigate', 'Investigate'], ['experiments', 'Experiments'], ['history', 'History']] as const).map(([key, label]) => (
          <button key={key} className={cn('text-muted-foreground hover:text-foreground', view === key && 'text-foreground')} onClick={() => switchView(key)}>{label}</button>
        ))}
      </div>
    </div>
  )
}

function Investigate({ scenarios, scenario, setScenario, mode, setMode, model, setModel, busy, result, activeScenario, onRun }: { scenarios: Scenario[]; scenario: string; setScenario: (v: string) => void; mode: 'baseline' | 'llm'; setMode: (v: 'baseline' | 'llm') => void; model: string; setModel: (v: string) => void; busy: boolean; result: Investigation | null; activeScenario?: string; onRun: () => void }) {
  return <ContentSection title="Run investigation" description="Choose a scenario and compare deterministic baseline behavior with the LLM path.">
    <div className="grid gap-5 md:grid-cols-[1.5fr_1fr]">
      <div className="space-y-4">
        <div className="space-y-2"><label className="text-sm font-medium">Incident</label><Select value={scenario} onValueChange={setScenario}><SelectTrigger><SelectValue placeholder="Select an incident" /></SelectTrigger><SelectContent>{scenarios.map((item) => <SelectItem key={item.id} value={item.id}>{item.title}</SelectItem>)}</SelectContent></Select></div>
        <div className="space-y-2"><label className="text-sm font-medium">Mode</label><div className="flex rounded-md border border-input bg-background p-1"><Button type="button" variant={mode === 'baseline' ? 'secondary' : 'ghost'} className="flex-1" onClick={() => setMode('baseline')}>Baseline</Button><Button type="button" variant={mode === 'llm' ? 'secondary' : 'ghost'} className="flex-1" onClick={() => setMode('llm')}>LLM</Button></div></div>
        <div className="space-y-2"><label className="text-sm font-medium">Model <span className="font-normal text-muted-foreground">LLM only</span></label><Input disabled={mode !== 'llm'} value={model} onChange={(e) => setModel(e.target.value)} placeholder="llama3.2" /></div>
        <Button disabled={!scenario || busy} onClick={onRun}>{busy ? <><LoaderCircle className="animate-spin" />Running</> : <><Play />Run investigation</>}</Button>
      </div>
      {result ? <div className="rounded-lg border border-border bg-card p-5"><div className="mb-4 flex items-start justify-between gap-3"><div><p className="text-xs text-muted-foreground">{activeScenario || result.scenario_id}</p><h3 className="text-lg font-semibold">Investigation result</h3></div><span className={cn('inline-flex items-center gap-1 text-sm font-medium', result.passed ? 'text-emerald-600' : 'text-destructive')}>{result.passed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}{result.passed ? 'Passed' : 'Needs review'}</span></div><div className="space-y-4"><div><p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Root cause</p><p className="text-sm leading-6">{result.diagnosis.root_cause}</p></div><div><p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Evidence</p><div className="space-y-2">{result.diagnosis.evidence.map((item, index) => <div key={`${item}-${index}`} className="flex gap-3 text-sm"><span className="text-xs font-mono text-muted-foreground">E-{String(index + 1).padStart(2, '0')}</span><p>{item}</p></div>)}</div></div><div><p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Recommended action</p><p className="text-sm leading-6">{result.diagnosis.recommended_action}</p></div><div className="grid grid-cols-3 gap-3 border-t border-border pt-4 text-sm"><Metric label="Confidence" value={`${Math.round(result.diagnosis.confidence * 100)}%`} /><Metric label="Duration" value={`${Math.round(result.duration_ms)} ms`} /><Metric label="Provider" value={result.provider} /></div></div></div> : <div className="rounded-lg border border-dashed border-border p-8 text-sm text-muted-foreground">Results will appear here after the investigation finishes.</div>}
    </div>
  </ContentSection>
}

function Experiments({ experiments, detail, setDetail }: { experiments: Experiment[]; detail: Experiment | null; setDetail: (v: Experiment | null) => void }) {
  if (detail) return <ContentSection title={detail.name} description="Saved experiment details."><Button variant="ghost" size="sm" className="mb-4" onClick={() => setDetail(null)}>Back to experiments</Button><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"> <Metric label="Pass rate" value={`${Math.round(detail.pass_rate * 100)}%`} /><Metric label="Runs" value={`${detail.passed_runs}/${detail.total_runs}`} /><Metric label="Dataset" value={`${detail.dataset_name} v${detail.dataset_version}`} /><Metric label="Provider" value={detail.provenance?.provider || '—'} /></div><div className="mt-4 rounded-md border border-border p-4 text-sm"><p className="text-xs text-muted-foreground">Dataset fingerprint</p><code className="break-all">{detail.dataset_fingerprint}</code></div></ContentSection>
  return <ContentSection title="Saved experiments" description="Measured benchmark runs and regression outcomes."><div className="divide-y divide-border rounded-lg border border-border">{experiments.length ? experiments.map((experiment) => <button key={experiment.experiment_id} className="flex w-full items-center gap-4 p-4 text-left transition-colors hover:bg-accent/40" onClick={() => setDetail(experiment)}><div className="min-w-0 flex-1"><p className="font-medium">{experiment.name}</p><p className="text-xs text-muted-foreground">{experiment.provenance?.provider || 'unknown'}{experiment.provenance?.model ? ` · ${experiment.provenance.model}` : ''}</p></div><div className="text-right"><p className="font-semibold">{Math.round(experiment.pass_rate * 100)}%</p><p className="text-xs text-muted-foreground">{experiment.passed_runs}/{experiment.total_runs}</p></div></button>) : <div className="p-8 text-center text-sm text-muted-foreground">No experiments yet.</div>}</div></ContentSection>
}

function History({ runs }: { runs: Run[] }) {
  return <ContentSection title="Investigation history" description="Previous diagnosis runs."><div className="divide-y divide-border rounded-lg border border-border">{runs.length ? runs.map((run, index) => { const passed = Boolean(run.passed); return <div key={String(run.run_id || index)} className="flex items-center gap-3 p-4"><div className={cn('flex h-7 w-7 items-center justify-center rounded-full', passed ? 'bg-emerald-500/10 text-emerald-600' : 'bg-destructive/10 text-destructive')}>{passed ? <Check className="h-4 w-4" /> : <CircleAlert className="h-4 w-4" />}</div><div className="min-w-0 flex-1"><p className="font-medium">{String(run.scenario_id || 'Investigation')}</p><p className="text-xs text-muted-foreground">{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</p></div><span className="text-xs text-muted-foreground">{run.created_at ? new Date(String(run.created_at)).toLocaleString() : ''}</span></div> }) : <div className="p-8 text-center text-sm text-muted-foreground">No investigations yet.</div>}</div></ContentSection>
}

function Metric({ label, value }: { label: string; value: string }) { return <div><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></div> }
