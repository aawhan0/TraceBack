'use client'

import { useEffect, useMemo, useState } from 'react'
import { Activity, Check, CircleAlert, Gauge, LoaderCircle, Play, Search, X } from 'lucide-react'
import { AreaChartWidget } from '@/components/charts/area-chart-widget'
import { BarChartWidget } from '@/components/charts/bar-chart-widget'
import { LineChartWidget } from '@/components/charts/line-chart-widget'
import { ChartCard } from '@/components/charts/chart-card'
import { StatCard } from '@/components/dashboard/stat-card'
import { EmptyState } from '@/components/dashboard/empty-state'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

type Evidence = { id: string; content: string; source: string; kind: string }
type Scenario = { id: string; title: string; evidence: Evidence[] }
type Diagnosis = { root_cause: string; evidence_ids: string[]; confidence: number; recommended_action: string }
type Investigation = { scenario_id: string; mode: 'baseline' | 'llm'; provider: string; diagnosis: Diagnosis; passed: boolean; duration_ms: number }
type Run = Record<string, unknown>

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  let data: unknown = null
  if (text) { try { data = JSON.parse(text) } catch { throw new Error(`Unexpected response from API (${response.status})`) } }
  if (!response.ok) throw new Error(typeof data === 'object' && data && 'detail' in data ? String(data.detail) : `Request failed (${response.status})`)
  return data as T
}

export default function HomePage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenario, setScenario] = useState('')
  const [mode, setMode] = useState<'baseline' | 'llm'>('baseline')
  const [model, setModel] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [result, setResult] = useState<Investigation | null>(null)
  const [runs, setRuns] = useState<Run[]>([])

  useEffect(() => {
    void api<Scenario[]>('/scenarios').then((items) => {
      setScenarios(items)
      if (items[0]) setScenario(items[0].id)
    }).catch((error) => setNotice(error instanceof Error ? error.message : 'Unable to connect to TraceBack'))
    void api<Run[]>('/runs?limit=50').then(setRuns).catch(() => undefined)
  }, [])

  const activeScenario = useMemo(() => scenarios.find((item) => item.id === scenario), [scenarios, scenario])
  const chartRuns = useMemo(() => runs.slice().reverse().slice(-20).map((run, index) => ({ run: String(index + 1), confidence: Math.round(Number(run.confidence ?? 0) * 100), duration: Math.round(Number(run.duration_ms ?? 0)) })), [runs])
  const scenarioCounts = useMemo(() => scenarios.map((item) => ({ scenario: item.title.length > 18 ? `${item.title.slice(0, 18)}…` : item.title, runs: runs.filter((run) => String(run.scenario_id ?? '') === item.id).length })), [scenarios, runs])
  const totalRuns = runs.length
  const passedRuns = runs.filter((run) => Boolean(run.passed)).length
  const passRate = totalRuns ? Math.round((passedRuns / totalRuns) * 100) : 0
  const avgDuration = totalRuns ? Math.round(runs.reduce((sum, run) => sum + Number(run.duration_ms ?? 0), 0) / totalRuns) : 0
  const avgConfidence = totalRuns ? Math.round((runs.reduce((sum, run) => sum + Number(run.confidence ?? 0), 0) / totalRuns) * 100) : 0

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
    } finally {
      setBusy(false)
    }
  }

  const evidenceById = useMemo(() => new Map((activeScenario?.evidence ?? []).map((item) => [item.id, item])), [activeScenario])

  return <div className="space-y-6">
    <PageHeader title="Investigate" description="Trace a production-style failure to its root cause." />
    {notice && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span className="flex-1">{notice}</span><Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={() => setNotice('')}><X /></Button></div>}

    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard title="Investigations" value={totalRuns} icon={Activity} />
      <StatCard title="Pass rate" value={`${passRate}%`} icon={Check} />
      <StatCard title="Avg. confidence" value={`${avgConfidence}%`} icon={Gauge} />
      <StatCard title="Avg. duration" value={`${avgDuration} ms`} icon={Activity} />
    </div>

    <section className="grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="mb-5"><div className="mb-2 flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary"><Search className="h-4 w-4" /></div><h2 className="text-base font-semibold">Run investigation</h2><p className="mt-1 text-sm text-muted-foreground">Choose an incident and run the deterministic baseline or LLM path.</p></div>
        <div className="space-y-4">
          <div className="space-y-2"><label className="text-sm font-medium">Incident</label><select value={scenario} onChange={(e) => setScenario(e.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"><option value="">Select an incident</option>{scenarios.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></div>
          <div className="space-y-2"><label className="text-sm font-medium">Mode</label><div className="grid grid-cols-2 rounded-md bg-muted p-1"><Button type="button" variant={mode === 'baseline' ? 'default' : 'ghost'} className="h-9" onClick={() => setMode('baseline')}>Baseline</Button><Button type="button" variant={mode === 'llm' ? 'default' : 'ghost'} className="h-9" onClick={() => setMode('llm')}>LLM</Button></div></div>
          <div className="space-y-2"><label className="text-sm font-medium">Model <span className="font-normal text-muted-foreground">LLM only</span></label><Input disabled={mode !== 'llm'} value={model} onChange={(e) => setModel(e.target.value)} placeholder="llama3.2" /></div>
          <Button type="button" disabled={!scenario || busy} onClick={investigate}>{busy ? <><LoaderCircle className="animate-spin" />Running</> : <><Play />Run investigation</>}</Button>
        </div>
      </div>
      {result ? <div className="rounded-lg border border-border bg-card p-5 shadow-sm"><div className="mb-4 flex items-start justify-between gap-4"><div><p className="text-xs text-muted-foreground">{activeScenario?.title || result.scenario_id}</p><h2 className="mt-1 text-base font-semibold">Investigation result</h2></div><span className={cn('inline-flex items-center gap-1 text-sm font-medium', result.passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-destructive')}>{result.passed ? <Check className="h-4 w-4" /> : <X className="h-4 w-4" />}{result.passed ? 'Passed' : 'Needs review'}</span></div><div className="space-y-4"><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Root cause</p><p className="mt-1 text-sm leading-6">{result.diagnosis.root_cause}</p></div><div><p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">Evidence</p><div className="space-y-2">{result.diagnosis.evidence_ids.length ? result.diagnosis.evidence_ids.map((item, index) => { const evidence = evidenceById.get(item); return <div key={`${item}-${index}`} className="rounded-md bg-muted/40 px-3 py-2.5"><div className="flex gap-3"><span className="shrink-0 pt-0.5 font-mono text-xs text-muted-foreground">{item}</span><p className="text-sm leading-5">{evidence?.content || 'Evidence unavailable for this ID.'}</p></div>{evidence && <p className="mt-1 pl-[4.25rem] text-[11px] text-muted-foreground">{evidence.source} · {evidence.kind}</p>}</div> }) : <p className="text-sm text-muted-foreground">No evidence IDs returned.</p>}</div></div><div><p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Recommended action</p><p className="mt-1 text-sm leading-6">{result.diagnosis.recommended_action}</p></div><div className="grid grid-cols-3 gap-3 border-t border-border pt-4"><Metric label="Confidence" value={`${Math.round(result.diagnosis.confidence * 100)}%`} /><Metric label="Duration" value={`${Math.round(result.duration_ms)} ms`} /><Metric label="Provider" value={result.provider} /></div></div></div> : <div className="flex min-h-[260px] items-center justify-center rounded-lg border border-dashed border-border bg-muted/10 p-6 text-center lg:min-h-0"><div className="max-w-xs"><div className="mx-auto mb-3 flex h-9 w-9 items-center justify-center rounded-full bg-muted text-muted-foreground"><Search className="h-4 w-4" /></div><h2 className="text-sm font-semibold">No investigation run yet</h2><p className="mt-1 text-xs leading-5 text-muted-foreground">Run an investigation to see the diagnosis, supporting evidence, and recommended action.</p></div></div>}
    </section>

    <section className="grid gap-4 lg:grid-cols-2">
      <ChartCard title="Confidence over runs" description="Observed confidence for the most recent investigations."><LineChartWidget data={chartRuns} xKey="run" series={[{ key: 'confidence', color: 'hsl(var(--primary))', label: 'Confidence' }]} valueSuffix="%" height={190} /></ChartCard>
      <ChartCard title="Investigations by scenario" description="Coverage of the configured incident scenarios."><BarChartWidget data={scenarioCounts} xKey="scenario" series={[{ key: 'runs', color: 'hsl(var(--primary))', label: 'Runs' }]} height={190} /></ChartCard>
    </section>

    <ChartCard title="Investigation duration" description="Latency across the most recent runs."><AreaChartWidget data={chartRuns} xKey="run" series={[{ key: 'duration', color: 'hsl(var(--primary))', label: 'Duration' }]} valueSuffix=" ms" height={185} /></ChartCard>
  </div>
}

function Metric({ label, value }: { label: string; value: string }) { return <div><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></div> }
