'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, History as HistoryIcon } from 'lucide-react'
import { ContentSection } from '@/components/dashboard/content-section'
import { cn } from '@/lib/utils'

type Run = Record<string, unknown>
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function HistoryPage() {
  const [runs, setRuns] = useState<Run[]>([])
  useEffect(() => { void fetch(`${API}/runs?limit=50`).then(r => r.json()).then(setRuns).catch(() => undefined) }, [])
  return <ContentSection title="Investigation history" description="Previous diagnosis runs.">{runs.length ? <div className="divide-y divide-border rounded-lg border border-border">{runs.map((run, index) => { const passed = Boolean(run.passed); return <div key={String(run.run_id || index)} className="flex items-center gap-3 p-4"><div className={cn('flex h-7 w-7 items-center justify-center rounded-full', passed ? 'bg-emerald-500/10 text-emerald-600' : 'bg-destructive/10 text-destructive')}>{passed ? <Check className="h-4 w-4" /> : <CircleAlert className="h-4 w-4" />}</div><div className="min-w-0 flex-1"><p className="font-medium">{String(run.scenario_id || 'Investigation')}</p><p className="text-xs text-muted-foreground">{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</p></div><span className="text-xs text-muted-foreground">{run.created_at ? new Date(String(run.created_at)).toLocaleString() : ''}</span></div> })}</div> : <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-border p-10 text-sm text-muted-foreground"><HistoryIcon className="h-5 w-5" />No investigations yet.</div>}</ContentSection>
}
