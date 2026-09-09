'use client'

import { useEffect, useState } from 'react'
import { ArrowLeft, FlaskConical } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ContentSection } from '@/components/dashboard/content-section'

type Experiment = { experiment_id: string; name: string; dataset_name: string; dataset_version: string; dataset_fingerprint: string; created_at: string; total_runs: number; passed_runs: number; pass_rate: number; regression_passed: boolean | null; provenance?: { provider: string; model: string | null } }
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function ExperimentsPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [detail, setDetail] = useState<Experiment | null>(null)
  useEffect(() => { void fetch(`${API}/experiments?limit=50`).then(r => r.json()).then(setExperiments).catch(() => undefined) }, [])
  if (detail) return <ContentSection title={detail.name} description="Saved experiment details."><Button variant="ghost" size="sm" className="mb-4" onClick={() => setDetail(null)}><ArrowLeft /> Back to experiments</Button><div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Metric label="Pass rate" value={`${Math.round(detail.pass_rate * 100)}%`} /><Metric label="Runs" value={`${detail.passed_runs}/${detail.total_runs}`} /><Metric label="Dataset" value={`${detail.dataset_name} v${detail.dataset_version}`} /><Metric label="Provider" value={detail.provenance?.provider || '—'} /></div><div className="mt-4 rounded-md border border-border p-4 text-sm"><p className="text-xs text-muted-foreground">Dataset fingerprint</p><code className="break-all">{detail.dataset_fingerprint}</code></div></ContentSection>
  return <ContentSection title="Saved experiments" description="Measured benchmark runs and regression outcomes.">{experiments.length ? <div className="divide-y divide-border rounded-lg border border-border">{experiments.map(experiment => <button key={experiment.experiment_id} className="flex w-full items-center gap-4 p-4 text-left hover:bg-accent/40" onClick={() => setDetail(experiment)}><div className="min-w-0 flex-1"><p className="font-medium">{experiment.name}</p><p className="text-xs text-muted-foreground">{experiment.provenance?.provider || 'unknown'}{experiment.provenance?.model ? ` · ${experiment.provenance.model}` : ''}</p></div><div className="text-right"><p className="font-semibold">{Math.round(experiment.pass_rate * 100)}%</p><p className="text-xs text-muted-foreground">{experiment.passed_runs}/{experiment.total_runs}</p></div></button>)}</div> : <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-border p-10 text-sm text-muted-foreground"><FlaskConical className="h-5 w-5" />No experiments yet.</div>}</ContentSection>
}
function Metric({ label, value }: { label: string; value: string }) { return <div><p className="text-xs text-muted-foreground">{label}</p><p className="mt-1 font-medium">{value}</p></div> }
