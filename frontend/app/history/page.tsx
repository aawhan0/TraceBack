'use client'

import { useEffect, useMemo, useState } from 'react'
import { ArrowDown, ArrowUp, ArrowUpDown, History as HistoryIcon } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { EmptyState } from '@/components/dashboard/empty-state'
import { StatusBadge } from '@/components/data/status-badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

type Run = Record<string, unknown>
type SortKey = 'scenario_id' | 'mode' | 'duration_ms' | 'confidence'
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function HistoryPage() {
  const [runs, setRuns] = useState<Run[]>([])
  const [sortKey, setSortKey] = useState<SortKey>('duration_ms')
  const [descending, setDescending] = useState(true)

  useEffect(() => {
    void fetch(`${API}/runs?limit=50`).then(async (response) => { if (!response.ok) throw new Error('Unable to load history'); return response.json() }).then(setRuns).catch(() => undefined)
  }, [])

  const sortedRuns = useMemo(() => [...runs].sort((a, b) => {
    const av = a[sortKey]; const bv = b[sortKey]
    const left = sortKey === 'scenario_id' || sortKey === 'mode' ? String(av ?? '') : Number(av ?? 0)
    const right = sortKey === 'scenario_id' || sortKey === 'mode' ? String(bv ?? '') : Number(bv ?? 0)
    const comparison = left < right ? -1 : left > right ? 1 : 0
    return descending ? -comparison : comparison
  }), [runs, sortKey, descending])

  function sortBy(key: SortKey) { if (key === sortKey) setDescending((value) => !value); else { setSortKey(key); setDescending(true) } }
  const Header = ({ label, sort }: { label: string; sort: SortKey }) => <button type="button" onClick={() => sortBy(sort)} className="inline-flex items-center text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground">{label}{sort === sortKey ? (descending ? <ArrowDown className="ml-1.5 h-3.5 w-3.5 text-primary" /> : <ArrowUp className="ml-1.5 h-3.5 w-3.5 text-primary" />) : <ArrowUpDown className="ml-1.5 h-3.5 w-3.5 opacity-40" />}</button>

  return <div className="space-y-8"><PageHeader title="History" description="Previous diagnosis runs and their evaluation signals." />{sortedRuns.length ? <div className="overflow-hidden rounded-lg border border-border bg-card shadow-sm"><Table><TableHeader><TableRow><TableHead><Header label="Scenario" sort="scenario_id" /></TableHead><TableHead><Header label="Mode" sort="mode" /></TableHead><TableHead><Header label="Confidence" sort="confidence" /></TableHead><TableHead><Header label="Duration" sort="duration_ms" /></TableHead><TableHead>Status</TableHead><TableHead>Created</TableHead></TableRow></TableHeader><TableBody>{sortedRuns.map((run, index) => { const passed = Boolean(run.passed); return <TableRow key={String(run.run_id || index)}><TableCell className="font-medium">{String(run.scenario_id || 'Investigation')}</TableCell><TableCell className="text-muted-foreground">{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</TableCell><TableCell>{Math.round(Number(run.confidence ?? 0) * 100)}%</TableCell><TableCell>{Math.round(Number(run.duration_ms ?? 0))} ms</TableCell><TableCell><StatusBadge status={passed ? 'success' : 'error'} label={passed ? 'Passed' : 'Needs review'} /></TableCell><TableCell className="text-sm text-muted-foreground">{run.created_at ? new Date(String(run.created_at)).toLocaleString() : '—'}</TableCell></TableRow> })}</TableBody></Table></div> : <EmptyState icon={HistoryIcon} title="No investigations yet" description="Run an investigation to start building the diagnosis history." />}</div>
}
