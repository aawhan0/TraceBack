'use client'

import { useEffect, useMemo, useState } from 'react'
import { Check, CircleAlert, FlaskConical, History, LoaderCircle, Play, Search, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageHeader } from '@/components/dashboard/page-header'
import { ContentSection } from '@/components/dashboard/content-section'
import { cn } from '@/lib/utils'

type Scenario = { id: string; title: string }
type Diagnosis = { root_cause: string; evidence: string[]; confidence: number; recommended_action: string }
type Investigation = { scenario_id: string; mode: 'baseline' | 'llm'; provider: string; diagnosis: Diagnosis; passed: boolean; duration_ms: number }
type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
type Run = Record<string, unknown>

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  const data = text ? JSON.parse(text) : null
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`)
  return data as T
}

export default function HomePage() {
  const [view, setView] = useState<'investigate' | 'experiments' | 'history'>('investigate')
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenario, setScenario] = useState('')
  const [mode, setMode] = useState<'baseline' | 'llm'>('baseline')
  const [model, setModel] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [result, setResult] = useState<Investigation | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [runs, setRuns] = useState<Run[]>([])

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
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Investigation failed') }
    finally { setBusy(false) }
  }

  return <div className="space-y-6">
    <PageHeader title={view === 'investigate' ? 'Investigate' : view === 'experiments' ? 'Experiments' : 'History'} description={view === 'investigate' ? 'Trace a production-style failure to its root cause.' : view === 'experiments' ? 'Evaluate saved investigation behavior.' : 'Review previous diagnosis runs.'} />
    <nav className="flex gap-2 border-b border-border pb-2">
      {([['investigate', Search, 'Investigate'], ['experiments', FlaskConical, 'Experiments'], ['history', History, 'History']] as const).map(([key, Icon, label]) => <Button key={key} type="button" size="sm" variant={view === key ? 'secondary' : 'ghost'} onClick={() => setView(key)}><Icon />{label}</Button>)}
    </nav>
    {notice && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span className="flex-1">{notice}</span><Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={() => setNotice('')}><X /></Button></div>}
    {view === 'investigate' && <ContentSection title="Run investigation" description="Choose a scenario and run the baseline or LLM investigation path."><div className="grid gap-5 md:grid-cols-[1.4fr_1fr]"><div className="space-y-4"><div className="space-y-2"><label className="text-sm font-medium">Incident</label><select value={scenario} onChange={(e) => setScenario(e.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"><option value="">Select an incident</option>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></div><div className="space-y-2"><label className="text-sm font-medium">Mode</label><div className="flex rounded-md border border-input p-1"><Button type="button" variant={mode === 'baseline' ? 'secondary' : 'ghost'} className="flex-1" onClick={() => setMode('baseline')}>Baseline</Button><Button type="button" variant={mode === 'llm' ? 'secondary' : 'ghost'} className="flex-1" onClick={() => setMode('llm')}>LLM</Button></div></div><div className="space-y-2"><label className="text-sm font-medium">Model <span className="font-normal text-muted-foreground">LLM only</span></label><Input disabled={mode !== 'llm'} value={model} onChange={(e) => setModel(e.target.value)} placeholder="llama3.2" /></div><Button type="button" disabled={!scenario || busy} onClick={investigate}>{busy ? <><LoaderCircle className="animate-spin" />Running</> : <><Play />Run investigation</>}</Button></div>{result ? <div className="rounded-lg border border-border bg-card p-5"><div className="mb-4 flex items-start justify-between gap-3"><div><p className="text-xs text-muted-foreground">{activeScenario?.title || result.scenario_id}</p><h3 className="text-lg font-semibold">Investigation result</h3></div><span className={cn('inline-flex items-center gap-1 text-sm font-medium', result.passed ? 'text-emerald-600' : 'text-destructive')}>{result.passed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}{result.passed ? 'Passed' : 'Needs review'}</span></div><div className="space-y-4"><div><p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Root cause</p><p className="text-sm leading-6">{result.diagnosis.root_cause}</p></div><div><p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Evidence</p><div className="space-y-2">{result.diagnosis.evidence.map((item, index) => <div key={`${item}-${index}`} className="flex gap-3 text-sm"><span className="font-mono text-xs text-muted-foreground">E-{String(index + 1).padStart(2, '0')}</span><p>{item}</p></div>)}</div></div><div><p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Recommended action</p><p className="text-sm leading-6">{result.diagnosis.recommended_action}</p></div><div className="grid grid-cols-3 gap-3 border-t border-border pt-4"><Metric label="Confidence" value={`${Math.round(result.diagnosis.confidence * 100)}%`} /><Metric label="Duration" value={`${Math.round(result.duration_ms)} ms`} /><Metric label="Provider" value={result.provider} /></div></div></div> : <div className="rounded-lg border border-dashed border-border p-8 text-sm text-muted-foreground">Results will appear here after the investigation finishes.</div>}</div></ContentSection>}
    {view === 'experiments' && <ContentSection title="Saved experiments" description="Measured benchmark runs and regression outcomes."><div className="divide-y divide-border rounded-lg border border-border">{experiments.length ? experiments.map((experiment) => <div key={experiment.experiment_id} className="flex items-center gap-4 p-4"><div className="min-w-0 flex-1"><p className="font-medium">{experiment.name}</p><p className="text-xs text-muted-foreground">{experiment.provenance?.provider || 'unknown'}{experiment.provenance?.model ? ` · ${experiment.provenance.model}` : ''}</p></div><div className="text-right"><p className="font-semibold">{Math.round(experiment.pass_rate * 100)}%</p><p className="text-xs text-muted-foreground">{experiment.passed_runs}/{experiment.total_runs}</p></div></div>) : <div className="p-8 text-center text-sm text-muted-foreground">No experiments yet.</div>}</div></ContentSection>}
    {view === 'history' && <ContentSection title="Investigation history" description="Previous diagnosis runs."><div className="divide-y divide-border rounded-lg border border-border">{runs.length ? runs.map((run, index) => { const passed = Boolean(run.passed); return <div key={String(run.run_id || index)} className="flex items-center gap-3 p-4"><div className={cn('flex h-7 w-7 items-center justify-center rounded-full', passed ? 'bg-emerald-500/10 text-emerald-600' : 'bg-destructive/10 text-destructive')}>{passed ? <Check className="h-4 w-4" /> : <CircleAlert className="h-4 w-4" />}</div><div className="min-w-0 flex-1"><p className="font-medium">{String(run.scenario_id || 'Investigation')}</p><p className="text-xs text-muted-foreground">{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</p></div><span className="text-xs text-muted-foreground">{run.created_at ? new Date(String(run.created_at)).toLocaleString() : ''}</span></div> }) : <div className="p-8 text-center text-sm text-muted-foreground">No investigations yet.</div>}</div></ContentSection>}
  </div>
}

function Metric({ label, value }: { label: string; value: string }) { return <div><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></div> }
