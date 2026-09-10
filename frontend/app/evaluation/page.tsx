'use client'

import { useEffect, useMemo, useState } from 'react'
import { BadgeCheck, CircleAlert, LoaderCircle, RotateCcw, XCircle } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { cn } from '@/lib/utils'

type RunSummary = {
  run_id: string
  scenario_id: string
  mode: 'baseline' | 'llm'
  provider: string
  passed: boolean
  confidence: number
  duration_ms: number
  created_at: string
}

type EvaluationRun = RunSummary & {
  root_cause_match: boolean
  evidence_recall: number
  evidence_precision: number
  confidence_valid: boolean
  action_present: boolean
}

type InvestigationResponse = { run_id: string }

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

const checks = [
  { key: 'root_cause_match', label: 'Root-cause match', description: 'The diagnosis contains every expected root-cause keyword.' },
  { key: 'evidence_recall', label: 'Evidence recall', description: 'Required evidence selected by the diagnosis.' },
  { key: 'evidence_precision', label: 'Evidence precision', description: 'Selected evidence that belongs to the scenario.' },
  { key: 'confidence_valid', label: 'Confidence validity', description: 'Confidence is within the valid 0–1 range.' },
  { key: 'action_present', label: 'Recommended action', description: 'A non-empty remediation action is present.' },
] as const

export default function EvaluationPage() {
  const [runs, setRuns] = useState<RunSummary[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [run, setRun] = useState<EvaluationRun | null>(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [rerunning, setRerunning] = useState(false)
  const [error, setError] = useState('')
  const [rerunMessage, setRerunMessage] = useState('')

  const loadRuns = () => {
    setLoading(true)
    return fetch(`${API}/runs?limit=50`)
      .then(async (response) => { if (!response.ok) throw new Error('Failed to load investigation runs'); return response.json() })
      .then((data: RunSummary[]) => { setRuns(data); if (data[0] && !selectedId) setSelectedId(data[0].run_id) })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => { void loadRuns() }, [])

  useEffect(() => {
    if (!selectedId) return
    setDetailLoading(true)
    setError('')
    fetch(`${API}/runs/${encodeURIComponent(selectedId)}`)
      .then(async (response) => { if (!response.ok) throw new Error('Failed to load evaluation details'); return response.json() })
      .then((data: EvaluationRun) => setRun(data))
      .catch((err: Error) => setError(err.message))
      .finally(() => setDetailLoading(false))
  }, [selectedId])

  const rerun = async () => {
    if (!run) return
    setRerunning(true)
    setError('')
    setRerunMessage('')
    try {
      const response = await fetch(`${API}/investigations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: run.scenario_id, mode: run.mode }),
      })
      if (!response.ok) {
        const detail = await response.text()
        throw new Error(detail || 'Investigation re-run failed')
      }
      const result = await response.json() as InvestigationResponse
      setRerunMessage(`Created new run ${result.run_id}`)
      await loadRuns()
      setSelectedId(result.run_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Investigation re-run failed')
    } finally {
      setRerunning(false)
    }
  }

  const passedCount = useMemo(() => {
    if (!run) return 0
    return checks.filter((check) => {
      const value = run[check.key]
      return check.key === 'evidence_recall' || check.key === 'evidence_precision' ? value === 1 : value === true
    }).length
  }, [run])

  return (
    <div className="space-y-6">
      <PageHeader title="Evaluation" description="Inspect the evaluator dimensions behind an investigation run." />

      {loading ? (
        <div className="flex items-center gap-2 rounded-lg border p-6 text-sm text-muted-foreground"><LoaderCircle className="h-4 w-4 animate-spin" />Loading runs…</div>
      ) : runs.length === 0 ? (
        <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">No investigation runs have been recorded yet.</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <section className="rounded-lg border bg-card p-3">
            <div className="px-2 pb-3 text-sm font-semibold">Recent runs</div>
            <div className="space-y-1">
              {runs.map((item) => (
                <button key={item.run_id} onClick={() => setSelectedId(item.run_id)} className={cn('w-full rounded-md px-3 py-2 text-left transition-colors hover:bg-accent', selectedId === item.run_id && 'bg-accent')}>
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-xs font-medium">{item.run_id}</span>
                    {item.passed ? <BadgeCheck className="h-4 w-4 shrink-0 text-primary" /> : <XCircle className="h-4 w-4 shrink-0 text-muted-foreground" />}
                  </div>
                  <div className="mt-1 truncate text-xs text-muted-foreground">{item.scenario_id} · {item.mode}</div>
                  <div className="mt-1 text-[11px] text-muted-foreground">{new Date(item.created_at).toLocaleString()}</div>
                </button>
              ))}
            </div>
          </section>

          <section className="space-y-4">
            {detailLoading ? (
              <div className="flex items-center gap-2 rounded-lg border p-6 text-sm text-muted-foreground"><LoaderCircle className="h-4 w-4 animate-spin" />Loading evaluation…</div>
            ) : run ? (
              <>
                <div className="rounded-lg border bg-card p-5">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div>
                      <div className="text-xs uppercase tracking-wide text-muted-foreground">Overall result</div>
                      <div className="mt-1 flex items-center gap-2 text-2xl font-semibold">
                        {run.passed ? <BadgeCheck className="h-6 w-6 text-primary" /> : <CircleAlert className="h-6 w-6 text-muted-foreground" />}
                        {run.passed ? 'Passed' : 'Failed'}
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{passedCount}/5 evaluator dimensions fully satisfied.</p>
                    </div>
                    <button onClick={rerun} disabled={rerunning} className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium transition-colors hover:bg-accent disabled:pointer-events-none disabled:opacity-50">
                      {rerunning ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <RotateCcw className="h-4 w-4" />}
                      {rerunning ? 'Re-running…' : 'Re-run investigation'}
                    </button>
                    <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm sm:grid-cols-4">
                      <div><div className="text-xs text-muted-foreground">Scenario</div><div className="font-medium">{run.scenario_id}</div></div>
                      <div><div className="text-xs text-muted-foreground">Mode</div><div className="font-medium">{run.mode}</div></div>
                      <div><div className="text-xs text-muted-foreground">Provider</div><div className="font-medium">{run.provider}</div></div>
                      <div><div className="text-xs text-muted-foreground">Confidence</div><div className="font-medium">{(run.confidence * 100).toFixed(0)}%</div></div>
                    </div>
                  </div>
                </div>

                {rerunMessage && <div className="rounded-lg border bg-card p-4 text-sm text-muted-foreground">{rerunMessage}</div>}

                <div className="grid gap-4 sm:grid-cols-2">
                  {checks.map((check) => {
                    const raw = run[check.key]
                    const numeric = typeof raw === 'number'
                    const satisfied = numeric ? raw === 1 : raw === true
                    return (
                      <div key={check.key} className="rounded-lg border bg-card p-5">
                        <div className="flex items-start justify-between gap-3">
                          <div><div className="font-medium">{check.label}</div><p className="mt-1 text-sm text-muted-foreground">{check.description}</p></div>
                          <span className={cn('rounded-full px-2.5 py-1 text-xs font-medium', satisfied ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground')}>
                            {numeric ? `${(raw * 100).toFixed(0)}%` : satisfied ? 'Pass' : 'Fail'}
                          </span>
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="rounded-lg border bg-card p-5 text-sm text-muted-foreground"><span className="font-medium text-foreground">Evaluation rule:</span> an investigation passes only when root-cause match, evidence recall, evidence precision, confidence validity, and recommended-action presence all satisfy the evaluator. Recall and precision must each equal 100%.</div>
              </>
            ) : null}
          </section>
        </div>
      )}

      {error && <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm"><CircleAlert className="h-4 w-4" />{error}</div>}
    </div>
  )
}
