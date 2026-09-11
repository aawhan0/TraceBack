'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, Download, FileText, LoaderCircle } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { cn } from '@/lib/utils'

type Run = {
  run_id: string
  scenario_id: string
  mode: 'baseline' | 'llm'
  provider: string
  passed: boolean
  confidence: number
  duration_ms: number
  created_at: string
  root_cause_match: boolean
  evidence_recall: number
  evidence_precision: number
  confidence_valid: boolean
  action_present: boolean
  diagnosis?: { root_cause: string; evidence_ids: string[]; confidence: number; recommended_action: string }
}

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

function formatConfidence(value: number | null | undefined) {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${Math.round(value * 100)}%`
    : 'N/A'
}

function download(name: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = name
  anchor.click()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const [runs, setRuns] = useState<Run[]>([])
  const [selected, setSelected] = useState<Run | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch(`${API}/runs?limit=50`)
      .then(async (response) => { if (!response.ok) throw new Error('Unable to load investigation runs'); return response.json() })
      .then((items: Run[]) => { setRuns(items); if (items[0]) void loadRun(items[0].run_id) })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  async function loadRun(id: string) {
    try {
      const response = await fetch(`${API}/runs/${encodeURIComponent(id)}`)
      if (!response.ok) throw new Error('Unable to load report data')
      setSelected(await response.json())
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to load report data') }
  }

  function exportJson() {
    if (!selected) return
    download(`traceback-${selected.run_id}.json`, JSON.stringify(selected, null, 2), 'application/json')
  }

  function exportMarkdown() {
    if (!selected) return
    const lines = [
      `# TraceBack Investigation Report`,
      '',
      `- **Run:** ${selected.run_id}`,
      `- **Scenario:** ${selected.scenario_id}`,
      `- **Mode:** ${selected.mode}`,
      `- **Provider:** ${selected.provider}`,
      `- **Created:** ${new Date(selected.created_at).toISOString()}`,
      `- **Duration:** ${Math.round(selected.duration_ms)} ms`,
      `- **Overall:** ${selected.passed ? 'Passed' : 'Needs review'}`,
      '',
      '## Diagnosis',
      '',
      `### Root cause`,
      selected.diagnosis?.root_cause || 'Not available in this run.',
      '',
      `### Recommended action`,
      selected.diagnosis?.recommended_action || 'Not available in this run.',
      '',
      '## Evaluation',
      '',
      `| Metric | Result |`,
      `| --- | --- |`,
      `| Root-cause match | ${selected.root_cause_match ? 'Pass' : 'Fail'} |`,
      `| Evidence recall | ${Math.round(selected.evidence_recall * 100)}% |`,
      `| Evidence precision | ${Math.round(selected.evidence_precision * 100)}% |`,
      `| Confidence validity | ${selected.confidence_valid ? 'Pass' : 'Fail'} |`,
      `| Recommended action present | ${selected.action_present ? 'Pass' : 'Fail'} |`,
      '',
      `**Confidence:** ${formatConfidence(selected.confidence)}`,
      '',
      `**Evidence IDs:** ${selected.diagnosis?.evidence_ids?.join(', ') || 'None'}`,
    ]
    download(`traceback-${selected.run_id}.md`, lines.join('\n'), 'text/markdown;charset=utf-8')
  }

  return <div className="space-y-6"><PageHeader title="Reports" description="Export a persisted investigation run as a portable report." />
    {loading ? <div className="flex items-center gap-2 rounded-lg border p-6 text-sm text-muted-foreground"><LoaderCircle className="h-4 w-4 animate-spin" />Loading runsÃƒÂ¢Ã¢â€šÂ¬Ã‚Â¦</div> : !runs.length ? <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">No investigation runs are available to export.</div> : <div className="grid gap-6 lg:h-[calc(100vh-9rem)] lg:min-h-0 lg:grid-cols-[280px_minmax(0,1fr)] overflow-hidden">
      <section className="flex min-h-0 flex-col overflow-hidden rounded-lg border bg-card p-3"><div className="px-2 pb-3 text-sm font-semibold">Select run</div><div className="min-h-0 flex-1 overflow-y-auto pr-1"><div className="space-y-1">{runs.map((run) => <button key={run.run_id} type="button" onClick={() => void loadRun(run.run_id)} className={cn('w-full rounded-md px-3 py-2 text-left hover:bg-accent', selected?.run_id === run.run_id && 'bg-accent')}><div className="flex items-center justify-between gap-2"><span className="truncate text-xs font-medium">{run.run_id}</span>{run.passed ? <Check className="h-4 w-4 text-primary" /> : <CircleAlert className="h-4 w-4 text-destructive" />}</div><div className="mt-1 text-xs text-muted-foreground">{run.scenario_id} Ã‚ -  {run.mode}</div></button>)}</div></div></section>
      <section className="min-h-0 min-w-0 overflow-y-auto pr-1 space-y-4">{selected && <><div className="rounded-lg border bg-card p-5"><div className="flex flex-wrap items-start justify-between gap-4"><div><div className="flex items-center gap-2"><FileText className="h-5 w-5 text-primary" /><h2 className="text-lg font-semibold">Investigation report</h2></div><p className="mt-1 text-sm text-muted-foreground">{selected.run_id} Ã‚ -  {selected.scenario_id}</p></div><div className="flex gap-2"><button type="button" onClick={exportMarkdown} className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium hover:bg-accent"><Download className="h-4 w-4" />Markdown</button><button type="button" onClick={exportJson} className="inline-flex items-center gap-2 rounded-md border px-3 py-2 text-sm font-medium hover:bg-accent"><Download className="h-4 w-4" />JSON</button></div></div></div><div className="grid gap-4 sm:grid-cols-2"><div className="rounded-lg border bg-card p-5"><div className="text-xs uppercase tracking-wide text-muted-foreground">Root cause</div><p className="mt-2 text-sm leading-6">{selected.diagnosis?.root_cause || 'Not available in this run.'}</p></div><div className="rounded-lg border bg-card p-5"><div className="text-xs uppercase tracking-wide text-muted-foreground">Recommended action</div><p className="mt-2 text-sm leading-6">{selected.diagnosis?.recommended_action || 'Not available in this run.'}</p></div></div><div className="rounded-lg border bg-card p-5"><div className="mb-3 text-sm font-semibold">Evaluation snapshot</div><div className="grid gap-3 sm:grid-cols-5">{[['Root cause', selected.root_cause_match ? 'Pass' : 'Fail'], ['Recall', `${Math.round(selected.evidence_recall * 100)}%`], ['Precision', `${Math.round(selected.evidence_precision * 100)}%`], ['Confidence', `${Math.round(selected.confidence * 100)}%`], ['Action', selected.action_present ? 'Pass' : 'Fail']].map(([label, value]) => <div key={label} className="rounded-md bg-muted/50 p-3"><div className="text-[11px] text-muted-foreground">{label}</div><div className="mt-1 text-sm font-semibold">{value}</div></div>)}</div></div></>}</section>
    </div>}
    {error && <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">{error}</div>}
  </div>
}

