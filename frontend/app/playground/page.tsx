'use client'

import { useEffect, useState } from 'react'
import { CircleAlert, Gauge, Play, Sparkles } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

type Scenario = {
  id: string
  title: string
  custom?: boolean
}

type Diagnosis = {
  root_cause: string
  evidence_ids: string[]
  confidence: number
  recommended_action: string
}

type Result = {
  scenario_id: string
  provider: string
  diagnosis: Diagnosis
  passed: boolean
  duration_ms: number
  run_id: string
}

export default function PlaygroundPage() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [scenarioId, setScenarioId] = useState('')
  const [model, setModel] = useState('llama3.2:3b')
  const [result, setResult] = useState<Result | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadScenarios()
  }, [])

  async function loadScenarios() {
    try {
      const response = await fetch(`${API}/scenarios`)

      if (!response.ok) {
        throw new Error('Unable to load scenarios')
      }

      const items = (await response.json()) as Scenario[]

      setScenarios(items)

      if (items.length > 0) {
        setScenarioId(items[0].id)
      }
    } catch (item) {
      setError(
        item instanceof Error
          ? item.message
          : 'Unable to load scenarios',
      )
    }
  }

  async function run(mode: 'baseline' | 'llm') {
    setBusy(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API}/investigations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          scenario_id: scenarioId,
          mode,
          ...(mode === 'llm' ? { model } : {}),
        }),
      })

      const body = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(
          body.detail || `Investigation failed (${response.status})`,
        )
      }

      setResult(body as Result)
    } catch (item) {
      setError(
        item instanceof Error
          ? item.message
          : 'Investigation failed',
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Playground"
        description="Run the same incident through baseline or LLM inference and inspect the resulting diagnosis."
      />

      {error && (
        <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          <CircleAlert className="h-4 w-4" />
          <span>{error}</span>
        </div>
      )}

      <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>

          <div>
            <h2 className="text-base font-semibold">
              Investigation sandbox
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Change the scenario or model, then run a real backend
              investigation.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-[2fr_1fr_auto_auto] md:items-end">
          <div className="space-y-2">
            <label
              htmlFor="scenario"
              className="text-xs font-medium"
            >
              Scenario
            </label>

            <select
              id="scenario"
              value={scenarioId}
              onChange={(event) => setScenarioId(event.target.value)}
              disabled={busy}
              className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              {scenarios.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.title}
                  {item.custom ? ' · Custom' : ''}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label
              htmlFor="ollama-model"
              className="text-xs font-medium"
            >
              Ollama model
            </label>

            <select
              id="ollama-model"
              value={model}
              onChange={(event) => setModel(event.target.value)}
              disabled={busy}
              className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="llama3.2:3b">
                llama3.2:3b
              </option>

              <option value="qwen2.5:3b">
                qwen2.5:3b
              </option>
            </select>
          </div>

          <Button
            type="button"
            variant="outline"
            disabled={busy || !scenarioId}
            onClick={() => run('baseline')}
          >
            <Gauge className="h-4 w-4" />
            Baseline
          </Button>

          <Button
            type="button"
            disabled={busy || !scenarioId || !model}
            onClick={() => run('llm')}
          >
            <Play className="h-4 w-4" />
            {busy ? 'Running…' : 'Run LLM'}
          </Button>
        </div>
      </section>

      {result && (
        <section className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <Metric
              label="Result"
              value={result.passed ? 'Passed' : 'Failed'}
            />

            <Metric
              label="Confidence"
              value={`${Math.round(result.diagnosis.confidence * 100)}%`}
            />

            <Metric
              label="Latency"
              value={`${Math.round(result.duration_ms)} ms`}
            />

            <Metric
              label="Provider"
              value={result.provider}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-[1.2fr_.8fr]">
            <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Root cause
              </p>

              <p className="mt-2 text-lg font-semibold">
                {result.diagnosis.root_cause}
              </p>

              <p className="mt-5 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Recommended action
              </p>

              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                {result.diagnosis.recommended_action}
              </p>
            </div>

            <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
              <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Evidence selected
              </p>

              <div className="mt-3 space-y-2">
                {result.diagnosis.evidence_ids.length > 0 ? (
                  result.diagnosis.evidence_ids.map((id) => (
                    <code
                      key={id}
                      className="block rounded-md bg-muted/50 px-3 py-2 text-xs"
                    >
                      {id}
                    </code>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">
                    No evidence IDs returned.
                  </p>
                )}
              </div>

              <p className="mt-5 text-xs text-muted-foreground">
                Run ID: <code>{result.run_id}</code>
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

function Metric({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  )
}