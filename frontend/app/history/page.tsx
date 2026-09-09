'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, History as HistoryIcon } from 'lucide-react'
import { DataTable, type ColumnDef } from '@/components/data/data-table'
import { StatusBadge } from '@/components/data/status-badge'
import { EmptyState } from '@/components/dashboard/empty-state'
import { PageHeader } from '@/components/dashboard/page-header'

type Run = Record<string, unknown> & { id?: string }
const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function HistoryPage() {
  const [runs, setRuns] = useState<Run[]>([])
  useEffect(() => { void fetch(`${API}/runs?limit=50`).then(async (response) => { if (!response.ok) throw new Error('Unable to load history'); return response.json() }).then((items) => setRuns(items.map((item: Run, index: number) => ({ ...item, id: String(item.run_id ?? index) })))).catch(() => undefined) }, [])
  const columns: ColumnDef<Run>[] = [
    { key: 'scenario_id', header: 'Scenario', sortable: true, render: (run) => <span className="font-medium">{String(run.scenario_id || 'Investigation')}</span> },
    { key: 'mode', header: 'Mode', sortable: true, render: (run) => <span className="text-muted-foreground">{String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}</span> },
    { key: 'confidence', header: 'Confidence', sortable: true, render: (run) => `${Math.round(Number(run.confidence ?? 0) * 100)}%` },
    { key: 'duration_ms', header: 'Duration', sortable: true, render: (run) => `${Math.round(Number(run.duration_ms ?? 0))} ms` },
    { key: 'passed', header: 'Status', render: (run) => <StatusBadge status={Boolean(run.passed) ? 'success' : 'error'} label={Boolean(run.passed) ? 'Passed' : 'Needs review'} /> },
    { key: 'created_at', header: 'Created', sortable: true, render: (run) => <span className="text-muted-foreground">{run.created_at ? new Date(String(run.created_at)).toLocaleString() : '—'}</span> },
  ]
  return <div className="space-y-8"><PageHeader title="History" description="Previous diagnosis runs and their evaluation signals." />{runs.length ? <DataTable columns={columns} data={runs} searchKeys={['scenario_id', 'mode', 'provider']} searchPlaceholder="Search investigations…" pageSize={10} /> : <EmptyState icon={HistoryIcon} title="No investigations yet" description="Run an investigation to start building the diagnosis history." />}</div>
}
