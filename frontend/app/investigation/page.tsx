'use client';

import { useState } from 'react';

import { EvidenceExplorer } from '@/components/investigation/evidence-explorer';

export default function InvestigationPage() {
  const [question, setQuestion] = useState(
    'Why did request latency increase?',
  );
  const [rerun, setRerun] = useState(false);

  return (
    <main className="space-y-6">
      <header className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm text-muted-foreground">
            Investigation / INC-1042
          </p>

          <h1 className="text-3xl font-semibold tracking-tight">
            Investigation Workspace
          </h1>

          <p className="text-muted-foreground">
            Inspect evidence, validate the diagnosis, and decide what to do
            next.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setRerun(true)}
          className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-muted"
        >
          {rerun ? 'Analysis queued' : 'Rerun analysis'}
        </button>
      </header>

      <section className="space-y-3 rounded-xl border bg-card p-4 shadow-sm">
        <label htmlFor="question" className="text-sm font-medium">
          Investigation question
        </label>

        <div className="flex flex-col gap-2 md:flex-row">
          <input
            id="question"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm"
          />

          <span className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">
            Editable
          </span>
        </div>
      </section>

      <EvidenceExplorer />

      <section className="space-y-3 rounded-xl border bg-card p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Current diagnosis</h2>

          <span className="rounded-full bg-muted px-3 py-1 text-xs">
            High confidence
          </span>
        </div>

        <p className="text-sm text-muted-foreground">
          The latency increase is most likely caused by a slow database query
          introduced or exposed around the latest deployment. The trace,
          metric, and request log support the same causal path.
        </p>

        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">Primary cause</p>
            <p className="mt-1 font-medium">Database contention</p>
          </div>

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">Impact</p>
            <p className="mt-1 font-medium">Elevated p95 latency</p>
          </div>

          <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">Next action</p>
            <p className="mt-1 font-medium">Inspect query plan</p>
          </div>
        </div>
      </section>
    </main>
  );
}