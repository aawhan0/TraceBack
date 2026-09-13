'use client';

import { useMemo, useState } from 'react';

const evidence = [
  { id: 'EV-001', type: 'Log', title: 'Request timeout observed', detail: 'POST /v1/investigations exceeded the 30s timeout budget.', confidence: 0.94 },
  { id: 'EV-002', type: 'Trace', title: 'Slow database span', detail: 'The database query consumed 82% of the request duration.', confidence: 0.88 },
  { id: 'EV-003', type: 'Metric', title: 'Latency spike', detail: 'p95 latency increased from 420ms to 2.8s during the incident window.', confidence: 0.91 },
  { id: 'EV-004', type: 'Deploy', title: 'Recent release detected', detail: 'Version 1.8.0 was deployed 11 minutes before the first alert.', confidence: 0.76 },
];

export default function InvestigationPage() {
  const [question, setQuestion] = useState('Why did request latency increase?');
  const [filter, setFilter] = useState('All');
  const [selected, setSelected] = useState(evidence[0].id);
  const [rerun, setRerun] = useState(false);
  const filtered = useMemo(() => filter === 'All' ? evidence : evidence.filter(item => item.type === filter), [filter]);
  const active = evidence.find(item => item.id === selected) ?? evidence[0];

  return (
    <main className="space-y-6">
      <header className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div><p className="text-sm text-muted-foreground">Investigation / INC-1042</p><h1 className="text-3xl font-semibold tracking-tight">Investigation Workspace</h1><p className="text-muted-foreground">Inspect evidence, validate the diagnosis, and decide what to do next.</p></div>
        <button onClick={() => setRerun(true)} className="rounded-md border px-4 py-2 text-sm font-medium hover:bg-muted">{rerun ? 'Analysis queued' : 'Rerun analysis'}</button>
      </header>

      <section className="rounded-xl border bg-card p-4 shadow-sm space-y-3">
        <label htmlFor="question" className="text-sm font-medium">Investigation question</label>
        <div className="flex flex-col gap-2 md:flex-row"><input id="question" value={question} onChange={event => setQuestion(event.target.value)} className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm" /><span className="rounded-md bg-muted px-3 py-2 text-xs text-muted-foreground">Editable</span></div>
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.15fr_1fr]">
        <div className="rounded-xl border bg-card p-4 shadow-sm space-y-4">
          <div className="flex items-center justify-between"><div><h2 className="font-semibold">Evidence timeline</h2><p className="text-sm text-muted-foreground">{filtered.length} signals supporting this investigation</p></div><select value={filter} onChange={event => setFilter(event.target.value)} className="rounded-md border bg-background px-2 py-1 text-sm"><option>All</option><option>Log</option><option>Trace</option><option>Metric</option><option>Deploy</option></select></div>
          <div className="space-y-2">{filtered.map(item => <button key={item.id} onClick={() => setSelected(item.id)} className={`w-full rounded-lg border p-3 text-left transition ${selected === item.id ? 'border-foreground bg-muted' : 'hover:bg-muted/50'}`}><div className="flex items-center justify-between gap-2"><span className="text-xs text-muted-foreground">{item.id} · {item.type}</span><span className="text-xs">{Math.round(item.confidence * 100)}%</span></div><p className="mt-1 font-medium">{item.title}</p></button>)}</div>
        </div>

        <div className="rounded-xl border bg-card p-4 shadow-sm space-y-4"><div><h2 className="font-semibold">Evidence detail</h2><p className="text-sm text-muted-foreground">{active.id}</p></div><div className="rounded-lg bg-muted p-4"><p className="font-medium">{active.title}</p><p className="mt-2 text-sm text-muted-foreground">{active.detail}</p></div><div><p className="text-sm font-medium">Signal confidence</p><div className="mt-2 h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-foreground" style={{ width: `${active.confidence * 100}%` }} /></div><p className="mt-1 text-xs text-muted-foreground">{Math.round(active.confidence * 100)}% confidence based on the available signal.</p></div></div>
      </section>

      <section className="rounded-xl border bg-card p-4 shadow-sm space-y-3"><div className="flex items-center justify-between"><h2 className="font-semibold">Current diagnosis</h2><span className="rounded-full bg-muted px-3 py-1 text-xs">High confidence</span></div><p className="text-sm text-muted-foreground">The latency increase is most likely caused by a slow database query introduced or exposed around the latest deployment. The trace, metric, and request log support the same causal path.</p><div className="grid gap-3 md:grid-cols-3"><div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Primary cause</p><p className="mt-1 font-medium">Database contention</p></div><div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Impact</p><p className="mt-1 font-medium">Elevated p95 latency</p></div><div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Next action</p><p className="mt-1 font-medium">Inspect query plan</p></div></div></section>
    </main>
  );
}
