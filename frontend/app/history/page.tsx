'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { CircleAlert, History as HistoryIcon, LoaderCircle } from 'lucide-react'
import { DataTable, type ColumnDef } from '@/components/data/data-table'
import { StatusBadge } from '@/components/data/status-badge'
import { EmptyState } from '@/components/dashboard/empty-state'
import { PageHeader } from '@/components/dashboard/page-header'

type Run = Record<string, unknown> & { id?: string; run_id?: string }
type Scenario = { id: string; title: string }

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function HistoryPage() {
  const [runs, setRuns] = useState<Run[]>([])
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadHistory() {
      setLoading(true)
      setError('')

      try {
        const [runsResponse, scenariosResponse] = await Promise.all([
          fetch(`${API}/runs?limit=50`),
          fetch(`${API}/scenarios`),
        ])

        if (!runsResponse.ok || !scenariosResponse.ok) {
          throw new Error('Unable to load investigation history')
        }

        const [runItems, scenarioItems] = await Promise.all([
          runsResponse.json() as Promise<Run[]>,
          scenariosResponse.json() as Promise<Scenario[]>,
        ])

        if (cancelled) return

        setRuns(
          runItems.map((item, index) => ({
            ...item,
            id: String(item.run_id ?? index),
          })),
        )
        setScenarios(scenarioItems)
      } catch (item) {
        if (!cancelled) {
          setError(
            item instanceof Error
              ? item.message
              : 'Unable to load investigation history',
          )
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    void loadHistory()

    return () => {
      cancelled = true
    }
  }, [])

  const scenarioTitle = new Map(
    scenarios.map((scenario) => [scenario.id, scenario.title]),
  )

  const columns: ColumnDef<Run>[] = [
    {
      key: 'scenario_id',
      header: 'Scenario',
      sortable: true,
      render: (run) => {
        const runId = String(run.run_id ?? run.id ?? '')
        const scenarioId = String(run.scenario_id || '')

        return (
          <Link
            href={`/history/${encodeURIComponent(runId)}`}
            className="block max-w-[240px] truncate font-medium hover:underline"
            title={scenarioTitle.get(scenarioId) || scenarioId || 'Investigation'}
          >
            {scenarioTitle.get(scenarioId) || scenarioId || 'Investigation'}
          </Link>
        )
      },
    },
    {
      key: 'mode',
      header: 'Mode',
      sortable: true,
      render: (run) => (
        <span className="whitespace-nowrap text-muted-foreground">
          {String(run.mode || 'baseline')} · {String(run.provider || 'baseline')}
        </span>
      ),
    },
    {
      key: 'confidence',
      header: 'Confidence',
      sortable: true,
      render: (run) =>
        run.confidence == null
          ? 'N/A'
          : `${Math.round(Number(run.confidence) * 100)}%`,
    },
    {
      key: 'duration_ms',
      header: 'Duration',
      sortable: true,
      render: (run) =>
        run.duration_ms == null
          ? 'N/A'
          : `${Math.round(Number(run.duration_ms))} ms`,
    },
    {
      key: 'passed',
      header: 'Status',
      render: (run) => (
        <StatusBadge
          status={Boolean(run.passed) ? 'success' : 'error'}
          label={Boolean(run.passed) ? 'Passed' : 'Needs review'}
        />
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      sortable: true,
      render: (run) => (
        <span className="whitespace-nowrap text-muted-foreground">
          {run.created_at
            ? new Date(String(run.created_at)).toLocaleString()
            : '—'}
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="History"
        description="Previous diagnosis runs and their evaluation signals."
      />

      {error ? (
        <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          <CircleAlert className="h-4 w-4" />
          {error}
        </div>
      ) : loading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <LoaderCircle className="h-4 w-4 animate-spin" />
          Loading investigation history...
        </div>
      ) : runs.length ? (
        <DataTable
          columns={columns}
          data={runs}
          searchKeys={['scenario_id', 'mode', 'provider']}
          searchPlaceholder="Search investigations…"
          pageSize={10}
        />
      ) : (
        <EmptyState
          icon={HistoryIcon}
          title="No investigations yet"
          description="Run an investigation to start building the diagnosis history."
        />
      )}
    </div>
  )
}
