'use client'

import { useEffect, useMemo, useState } from 'react'
import { ArrowRight, Check, CircleAlert, GitCompareArrows, LoaderCircle, X } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
type ScenarioComparison = { scenario_id: string; baseline_pass_rate: number; candidate_pass_rate: number; pass_rate_delta: number }
type Comparison = {
  baseline_experiment_id: string
  candidate_experiment_id: string
  dataset: { name: string; version: string; fingerprint: string }
  metrics: { pass_rate: Metric; average_confidence: Metric; average_duration_ms: Metric }
  verdict: 'improved' | 'regressed' | 'unchanged'
  providers: { baseline: string | null; candidate: string | null }
  models: { baseline: string | null; candidate: string | null }
  scenarios: ScenarioComparison[]
}
type Metric = { baseline: number; candidate: number; delta: number }
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function ComparePage() {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [baseline, setBaseline] = useState('')
  const [candidate, setCandidate] = useState('')
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    void fetch(`${API}/experiments?limit=50`).then(async (response) => {
      if (!response.ok) throw new Error('Unable to load experiments')
      return response.json() as Promise<Experiment[]>
    }).then((items) => {
      setExperiments(items)
      if (items.length >= 2) { setBaseline(items[1].experiment_id); setCandidate(items[0].experiment_id) }
    }).catch((item) => setError(item instanceof Error ? item.message : 'Unable to load experiments'))
  }, [])

  const selectedBaseline = useMemo(() => experiments.find((item) => item.experiment_id === baseline), [experiments, baseline])
  const selectedCandidate = useMemo(() => experiments.find((item) => item.experiment_id === candidate), [experiments, candidate])

  async function compare() {
    if (!baseline || !candidate || baseline === candidate) return
    setBusy(true); setError(''); setComparison(null)
    try {
      const response = await fetch(`${API}/experiments/${encodeURIComponent(baseline)}/compare/${encodeURIComponent(candidate)}`)
      const body = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(body.detail || 'Unable to compare experiments')
      setComparison(body as Comparison)
    } catch (item) { setError(item instanceof Error ? item.message : 'Unable to compare experiments') }
    finally { setBusy(false) }
  }

  return <div className="space-y-6">
    <PageHeader title="Compare runs" description="Compare two saved experiments on the same immutable dataset." />
    {error && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span className="flex-1">{error}</span><Button type="button" variant="ghost" size="icon" className="h-7 w-7" onClick={() => setError('')}><X className="h-4 w-4" /></Button></div>}

    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="mb-5 flex items-start gap-3"><div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary"><GitCompareArrows className="h-4 w-4" /></div><div><h2 className="text-base font-semibold">Select experiments</h2><p className="mt-1 text-sm text-muted-foreground">The API rejects comparisons when dataset identity or scenario coverage differs.</p></div></div>
      <div className="grid gap-4 lg:grid-cols-[1fr_auto_1fr_auto] lg:items-end">
        <ExperimentSelect label="Baseline" value={baseline} onChange={setBaseline} experiments={experiments} />
        <ArrowRight className="hidden h-5 w-5 text-muted-foreground lg:block" />
        <ExperimentSelect label="Candidate" value={candidate} onChange={setCandidate} experiments={experiments} />
        <Button type="button" disabled={busy || !baseline || !candidate || baseline === candidate} onClick={compare}>{busy ? <><LoaderCircle className="animate-spin" />Comparing…</> : <><GitCompareArrows />Compare</>}</Button>
      </div>
    </section>

    {comparison && <>
      <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="mb-5 flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs text-muted-foreground">{selectedBaseline?.name} → {selectedCandidate?.name}</p><h2 className="mt-1 text-base font-semibold">Comparison result</h2></div><span className={cn('rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide', comparison.verdict === 'improved' ? 'bg-primary/10 text-primary' : comparison.verdict === 'regressed' ? 'bg-destructive/10 text-destructive' : 'bg-muted text-muted-foreground')}>{comparison.verdict}</span></div>
        <div className="grid gap-3 md:grid-cols-3"><MetricCard label="Pass rate" metric={comparison.metrics.pass_rate} format="percent" /><MetricCard label="Average confidence" metric={comparison.metrics.average_confidence} format="decimal" /><MetricCard label="Average duration" metric={comparison.metrics.average_duration_ms} format="ms" /></div>
      </section>

      <section className="rounded-lg border border-border bg-card p-5 shadow-sm"><h2 className="text-base font-semibold">Configuration</h2><div className="mt-4 grid gap-4 md:grid-cols-2"><ConfigCard label="Baseline" experiment={selectedBaseline} provider={comparison.providers.baseline} model={comparison.models.baseline} /><ConfigCard label="Candidate" experiment={selectedCandidate} provider={comparison.providers.candidate} model={comparison.models.candidate} /></div><p className="mt-4 text-xs text-muted-foreground">Dataset: {comparison.dataset.name} v{comparison.dataset.version} · fingerprint {comparison.dataset.fingerprint}</p></section>

      <section className="rounded-lg border border-border bg-card shadow-sm"><div className="border-b border-border px-5 py-4"><h2 className="text-sm font-semibold">Scenario breakdown</h2><p className="mt-1 text-xs text-muted-foreground">Pass-rate delta for each scenario included in both experiments.</p></div><div className="divide-y divide-border">{comparison.scenarios.map((item) => <div key={item.scenario_id} className="grid gap-2 px-5 py-4 sm:grid-cols-[1fr_auto_auto_auto] sm:items-center"><p className="font-mono text-xs">{item.scenario_id}</p><span className="text-xs text-muted-foreground">{Math.round(item.baseline_pass_rate * 100)}% → {Math.round(item.candidate_pass_rate * 100)}%</span><span className={cn('text-sm font-semibold', item.pass_rate_delta > 0 ? 'text-primary' : item.pass_rate_delta < 0 ? 'text-destructive' : 'text-muted-foreground')}>{item.pass_rate_delta > 0 ? '+' : ''}{Math.round(item.pass_rate_delta * 100)}%</span><span className="text-xs text-muted-foreground">candidate</span></div>)}</div></section>
    </>}

    {!comparison && !error && experiments.length < 2 && <div className="rounded-lg border border-dashed border-border px-5 py-10 text-center text-sm text-muted-foreground">Create at least two saved experiments to compare them.</div>}
  </div>
}

function ExperimentSelect({ label, value, onChange, experiments }: { label: string; value: string; onChange: (value: string) => void; experiments: Experiment[] }) {
  return <div className="space-y-2"><label className="text-xs font-medium">{label}</label><select value={value} onChange={(event) => onChange(event.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring"><option value="">Select experiment</option>{experiments.map((item) => <option key={item.experiment_id} value={item.experiment_id}>{item.name} · {Math.round(item.pass_rate * 100)}%</option>)}</select></div>
}

function MetricCard({ label, metric, format }: { label: string; metric: Metric; format: 'percent' | 'decimal' | 'ms' }) {
  const formatValue = (value: number) => format === 'percent' ? `${Math.round(value * 100)}%` : format === 'ms' ? `${Math.round(value)} ms` : value.toFixed(3)
  const delta = format === 'percent' ? `${metric.delta > 0 ? '+' : ''}${Math.round(metric.delta * 100)} pp` : format === 'ms' ? `${metric.delta > 0 ? '+' : ''}${Math.round(metric.delta)} ms` : `${metric.delta > 0 ? '+' : ''}${metric.delta.toFixed(3)}`
  return <div className="rounded-md border border-border bg-muted/20 p-4"><p className="text-xs text-muted-foreground">{label}</p><div className="mt-2 flex items-end justify-between gap-3"><p className="text-xl font-semibold">{formatValue(metric.candidate)}</p><p className={cn('text-xs font-medium', metric.delta > 0 ? 'text-primary' : metric.delta < 0 ? 'text-destructive' : 'text-muted-foreground')}>{delta}</p></div><p className="mt-1 text-[11px] text-muted-foreground">baseline {formatValue(metric.baseline)}</p></div>
}

function ConfigCard({ label, experiment, provider, model }: { label: string; experiment?: Experiment; provider: string | null; model: string | null }) {
  return <div className="rounded-md border border-border p-4"><p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{label}</p><p className="mt-2 text-sm font-medium">{experiment?.name || 'Unknown experiment'}</p><p className="mt-1 text-xs text-muted-foreground">{provider || 'unknown'}{model ? ` · ${model}` : ''}</p><div className="mt-3 flex gap-4 text-xs text-muted-foreground"><span>{experiment?.passed_runs ?? 0}/{experiment?.total_runs ?? 0} passed</span><span>{experiment ? Math.round(experiment.pass_rate * 100) : 0}%</span></div></div>
}
