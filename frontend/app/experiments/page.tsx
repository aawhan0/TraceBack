'use client'

import { useEffect, useMemo, useState } from 'react'
import { Check, CircleAlert, FlaskConical, Play, TrendingUp, X } from 'lucide-react'
import { LineChartWidget } from '@/components/charts/line-chart-widget'
import { BarChartWidget } from '@/components/charts/bar-chart-widget'
import { ChartCard } from '@/components/charts/chart-card'
import { StatCard } from '@/components/dashboard/stat-card'
import { EmptyState } from '@/components/dashboard/empty-state'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
type Scenario = { id: string; title: string }
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [detail, setDetail] = useState<Experiment | null>(null)
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [name, setName] = useState('baseline-smoke')
  const [scenarioIds, setScenarioIds] = useState<string[]>([])
  const [repetitions, setRepetitions] = useState(3)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function loadExperiments() {
    const response = await fetch(`${API}/experiments?limit=50`)
    if (!response.ok) throw new Error('Unable to load experiments')
    setExperiments(await response.json())
  }

  useEffect(() => {
    void Promise.all([
      loadExperiments(),
      fetch(`${API}/scenarios`).then(async (response) => {
        if (!response.ok) throw new Error('Unable to load scenarios')
        return response.json() as Promise<Scenario[]>
      }).then((items) => {
        setScenarios(items)
        if (items.length) setScenarioIds(items.map((item) => item.id))
      }),
    ]).catch((item) => setError(item instanceof Error ? item.message : 'Unable to load experiment data'))
  }, [])

  const passRate = useMemo(() => experiments.length ? Math.round(experiments.reduce((sum, item) => sum + item.pass_rate, 0) / experiments.length * 100) : 0, [experiments])
  const totalRuns = useMemo(() => experiments.reduce((sum, item) => sum + item.total_runs, 0), [experiments])
  const regressionPasses = useMemo(() => experiments.filter((item) => item.regression_passed !== false).length, [experiments])
  const trend = useMemo(() => experiments.slice().reverse().map((item, index) => ({ run: String(index + 1), passRate: Math.round(item.pass_rate * 100) })), [experiments])
  const providerCounts = useMemo(() => Object.entries(experiments.reduce<Record<string, number>>((acc, item) => { const provider = item.provenance?.provider || 'unknown'; acc[provider] = (acc[provider] || 0) + 1; return acc }, {})).map(([provider, count]) => ({ provider, experiments: count })), [experiments])

  async function runExperiment() {
    setBusy(true); setError('')
    try {
      await fetch(`${API}/experiments`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name.trim(), scenario_ids: scenarioIds, repetitions, mode: 'baseline' }) }).then(async (response) => {
        if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || 'Experiment run failed') }
      })
      await loadExperiments()
    } catch (item) { setError(item instanceof Error ? item.message : 'Experiment run failed') }
    finally { setBusy(false) }
  }

  if (detail) return <div className="space-y-6"><PageHeader title={detail.name} description="Saved experiment details." /><Button variant="outline" size="sm" onClick={() => setDetail(null)}>Back to experiments</Button><div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"><StatCard title="Pass rate" value={`${Math.round(detail.pass_rate * 100)}%`} icon={TrendingUp} /><StatCard title="Runs" value={`${detail.passed_runs}/${detail.total_runs}`} icon={FlaskConical} /><StatCard title="Provider" value={detail.provenance?.provider || '—'} /><StatCard title="Regression" value={detail.regression_passed === false ? 'Failed' : 'Passed'} icon={detail.regression_passed === false ? X : Check} /></div><div className="grid gap-4 lg:grid-cols-2"><ChartCard title="Experiment pass rate" description="Benchmark quality for this saved experiment."><BarChartWidget data={[{ metric: 'Pass rate', value: Math.round(detail.pass_rate * 100) }, { metric: 'Remaining', value: 100 - Math.round(detail.pass_rate * 100) }]} xKey="metric" series={[{ key: 'value', color: 'hsl(var(--primary))', label: 'Score' }]} valueSuffix="%" height={220} /></ChartCard><ChartCard title="Dataset fingerprint" description="Dataset identity used for the benchmark."><div className="flex min-h-[220px] items-center"><code className="w-full break-all rounded-md bg-muted/50 p-4 text-xs leading-5">{detail.dataset_fingerprint}</code></div></ChartCard></div></div>

  return <div className="space-y-6"><PageHeader title="Experiments" description="Evaluate saved investigation behavior and regression outcomes." />{error && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span className="flex-1">{error}</span><Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={() => setError('')}><X className="h-4 w-4" /></Button></div>}
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm"><div className="flex items-start justify-between gap-4"><div><h2 className="text-base font-semibold">Run experiment</h2><p className="mt-1 text-sm text-muted-foreground">Create a repeatable baseline benchmark from the real scenario catalog.</p></div><FlaskConical className="mt-0.5 h-4 w-4 text-primary" /></div><div className="mt-4 grid gap-3 lg:grid-cols-[1.5fr_2fr_auto_auto] lg:items-end"><div className="space-y-2"><label className="text-xs font-medium">Name</label><Input value={name} onChange={(event) => setName(event.target.value)} placeholder="baseline-smoke" /></div><div className="space-y-2"><label className="text-xs font-medium">Scenarios</label><div className="flex min-h-10 flex-wrap items-center gap-2 rounded-md border border-input bg-background px-3 py-2">{scenarios.length ? scenarios.map((item) => <label key={item.id} className="inline-flex items-center gap-1.5 text-xs"><input type="checkbox" checked={scenarioIds.includes(item.id)} onChange={(event) => setScenarioIds((current) => event.target.checked ? [...new Set([...current, item.id])] : current.filter((id) => id !== item.id))} />{item.title}</label>) : <span className="text-xs text-muted-foreground">Loading scenarios…</span>}</div></div><div className="space-y-2"><label className="text-xs font-medium">Repetitions</label><Input type="number" min={1} max={100} value={repetitions} onChange={(event) => setRepetitions(Math.max(1, Math.min(100, Number(event.target.value) || 1)))} /></div><Button type="button" disabled={busy || !name.trim() || !scenarioIds.length} onClick={runExperiment}>{busy ? 'Running…' : <><Play className="h-4 w-4" />Run baseline</>}</Button></div></section>

    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3"><StatCard title="Experiments" value={experiments.length} icon={FlaskConical} /><StatCard title="Average pass rate" value={`${passRate}%`} icon={TrendingUp} /><StatCard title="Regression-ready" value={`${regressionPasses}/${experiments.length || 0}`} icon={Check} /></div><div className="grid gap-4 lg:grid-cols-2"><ChartCard title="Pass rate by experiment" description="Saved benchmark quality, in run order.">{trend.length ? <LineChartWidget data={trend} xKey="run" series={[{ key: 'passRate', color: 'hsl(var(--primary))', label: 'Pass rate' }]} valueSuffix="%" height={190} /> : <EmptyState title="No benchmark history" description="Run a baseline experiment to populate this chart." />}</ChartCard><ChartCard title="Experiments by provider" description="Where saved evaluation runs came from.">{providerCounts.length ? <BarChartWidget data={providerCounts} xKey="provider" series={[{ key: 'experiments', color: 'hsl(var(--primary))', label: 'Experiments' }]} height={190} /> : <EmptyState title="No provider data" description="Provider distribution will appear after experiments are saved." />}</ChartCard></div><section className="rounded-lg border border-border bg-card shadow-sm"><div className="border-b border-border px-5 py-4"><h2 className="text-sm font-semibold">Saved experiments</h2><p className="mt-1 text-xs text-muted-foreground">{totalRuns} total benchmark runs.</p></div>{experiments.length ? <div className="divide-y divide-border">{experiments.map((experiment) => <button key={experiment.experiment_id} type="button" className="flex w-full items-center gap-4 p-4 text-left transition-colors hover:bg-accent/40" onClick={() => setDetail(experiment)}><div className={cn('flex h-8 w-8 items-center justify-center rounded-md', experiment.regression_passed === false ? 'bg-destructive/10 text-destructive' : 'bg-primary/10 text-primary')}>{experiment.regression_passed === false ? <CircleAlert className="h-4 w-4" /> : <Check className="h-4 w-4" />}</div><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{experiment.name}</p><p className="text-xs text-muted-foreground">{experiment.provenance?.provider || 'unknown'}{experiment.provenance?.model ? ` · ${experiment.provenance.model}` : ''} · {experiment.dataset_name} v{experiment.dataset_version}</p></div><div className="text-right"><p className="text-sm font-semibold">{Math.round(experiment.pass_rate * 100)}%</p><p className="text-xs text-muted-foreground">{experiment.passed_runs}/{experiment.total_runs}</p></div></button>)}</div> : <EmptyState icon={FlaskConical} title="No experiments yet" description="Create a baseline experiment above to populate saved benchmark results." />}</section></div>
}
