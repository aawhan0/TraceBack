'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { ArrowLeft, Check, CircleAlert, LoaderCircle } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

type Evidence = { id: string; content: string; source: string; kind: string }
type Run = {
  run_id: string
  scenario_id: string
  mode: string
  provider: string
  passed: boolean
  confidence: number | null
  duration_ms: number | null
  created_at: string
  diagnosis?: { root_cause: string; evidence_ids: string[]; recommended_action: string }
}
type Scenario = { id: string; title: string; evidence: Evidence[] }

export default function InvestigationDetailPage({ params }: { params: { run_id: string } }) {
  const [run, setRun] = useState<Run | null>(null)
  const [scenario, setScenario] = useState<Scenario | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    void Promise.all([
      fetch(`${API}/runs/${encodeURIComponent(params.run_id)}`).then(async (response) => {
        if (!response.ok) throw new Error('Unable to load investigation')
        return response.json() as Promise<Run>
      }),
      fetch(`${API}/scenarios`).then(async (response) => {
        if (!response.ok) throw new Error('Unable to load scenario evidence')
        return response.json() as Promise<Scenario[]>
      }),
    ]).then(([runData, scenarios]) => {
      setRun(runData)
      setScenario(scenarios.find((item) => item.id === runData.scenario_id) ?? null)
    }).catch((item) => setError(item instanceof Error ? item.message : 'Unable to load investigation'))
  }, [params.run_id])

  if (error) return <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{error}</div>
  if (!run) return <div className="flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="h-4 w-4 animate-spin" />Loading investigation...</div>

  const selected = new Set(run.diagnosis?.evidence_ids ?? [])

  return <div className="space-y-6">
    <PageHeader title="Investigation detail" description={scenario?.title || run.scenario_id} />
    <div className="flex flex-wrap items-center justify-between gap-3">
      <Link href="/history" className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"><ArrowLeft className="h-4 w-4" />Back to history</Link>
      <span className={run.passed ? 'inline-flex items-center gap-2 text-sm font-medium text-emerald-600' : 'inline-flex items-center gap-2 text-sm font-medium text-destructive'}>{run.passed ? <Check className="h-4 w-4" /> : <CircleAlert className="h-4 w-4" />}{run.passed ? 'Passed' : 'Needs review'}</span>
    </div>
    <div className="grid gap-3 sm:grid-cols-4">
      {[["Mode", run.mode], ["Provider", run.provider], ["Confidence", run.confidence == null ? 'N/A' : `${Math.round(run.confidence * 100)}%`], ["Duration", run.duration_ms == null ? 'N/A' : `${Math.round(run.duration_ms)} ms`]].map(([label, value]) => <div key={label} className="rounded-lg border bg-card p-4"><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 text-sm font-semibold">{value}</p></div>)}
    </div>
    <div className="grid gap-4 lg:grid-cols-2">
      <section className="rounded-lg border bg-card p-5"><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Root cause</p><p className="mt-2 text-sm leading-6">{run.diagnosis?.root_cause || 'Not available.'}</p></section>
      <section className="rounded-lg border bg-card p-5"><p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Recommended action</p><p className="mt-2 text-sm leading-6">{run.diagnosis?.recommended_action || 'Not available.'}</p></section>
    </div>
    <section className="rounded-lg border bg-card p-5"><h2 className="text-base font-semibold">Evidence explorer</h2><p className="mt-1 text-sm text-muted-foreground">Evidence selected by this diagnosis, alongside the remaining incident context.</p><div className="mt-4 space-y-3">{(scenario?.evidence ?? []).map((item) => <article key={item.id} className="rounded-md border p-4"><div className="flex flex-wrap items-center justify-between gap-2"><code className="text-xs">{item.id}</code><span className={selected.has(item.id) ? 'text-xs font-semibold text-primary' : 'text-xs text-muted-foreground'}>{selected.has(item.id) ? 'Selected' : 'Unused'}</span></div><p className="mt-2 text-sm leading-6">{item.content}</p><p className="mt-2 text-xs text-muted-foreground">{item.source} · {item.kind}</p></article>)}</div></section>
    <div className="text-xs text-muted-foreground">Run ID: <code>{run.run_id}</code> · Created {new Date(run.created_at).toLocaleString()}</div>
  </div>
}
