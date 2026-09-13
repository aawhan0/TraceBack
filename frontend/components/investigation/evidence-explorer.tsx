'use client';

import { useMemo, useState } from 'react';

type Evidence = { id: string; type: string; title: string; source: string; timestamp: string; detail: string; confidence: number };
const evidence: Evidence[] = [
  { id: 'EV-001', type: 'Log', title: 'Request timeout observed', source: 'api-gateway', timestamp: '14:02:11', detail: 'POST /v1/investigations exceeded the 30s timeout budget.', confidence: 0.94 },
  { id: 'EV-002', type: 'Trace', title: 'Slow database span', source: 'trace-7f3a', timestamp: '14:02:09', detail: 'The database query consumed 82% of the request duration.', confidence: 0.88 },
  { id: 'EV-003', type: 'Metric', title: 'Latency spike', source: 'api.latency.p95', timestamp: '14:01:52', detail: 'p95 latency increased from 420ms to 2.8s during the incident window.', confidence: 0.91 },
  { id: 'EV-004', type: 'Deploy', title: 'Recent release detected', source: 'release-service', timestamp: '13:51:00', detail: 'Version 1.8.0 was deployed 11 minutes before the first alert.', confidence: 0.76 },
];

export function EvidenceExplorer() {
  const [query, setQuery] = useState('');
  const [type, setType] = useState('All');
  const [selectedId, setSelectedId] = useState(evidence[0].id);
  const filtered = useMemo(() => evidence.filter(item => (type === 'All' || item.type === type) && `${item.title} ${item.source} ${item.detail}`.toLowerCase().includes(query.toLowerCase())), [query, type]);
  const selected = evidence.find(item => item.id === selectedId) ?? filtered[0] ?? evidence[0];

  return <section className="grid gap-4 lg:grid-cols-[1.15fr_1fr]">
    <div className="rounded-xl border bg-card p-4 shadow-sm space-y-4"><div className="flex items-center justify-between"><div><h2 className="font-semibold">Evidence explorer</h2><p className="text-sm text-muted-foreground">Search and inspect supporting signals.</p></div><span className="text-xs text-muted-foreground">{filtered.length} results</span></div><div className="flex flex-col gap-2 sm:flex-row"><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Search evidence…" className="min-w-0 flex-1 rounded-md border bg-background px-3 py-2 text-sm" /><select value={type} onChange={event => setType(event.target.value)} className="rounded-md border bg-background px-2 py-2 text-sm"><option>All</option><option>Log</option><option>Trace</option><option>Metric</option><option>Deploy</option></select></div><div className="space-y-2">{filtered.length ? filtered.map(item => <button key={item.id} onClick={() => setSelectedId(item.id)} className={`w-full rounded-lg border p-3 text-left transition ${selected.id === item.id ? 'border-foreground bg-muted' : 'hover:bg-muted/50'}`}><div className="flex items-center justify-between gap-2"><span className="text-xs text-muted-foreground">{item.id} · {item.type}</span><span className="text-xs text-muted-foreground">{item.timestamp}</span></div><p className="mt-1 font-medium">{item.title}</p><p className="mt-1 text-xs text-muted-foreground">{item.source}</p></button>) : <p className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">No evidence matches this filter.</p>}</div></div>
    <div className="rounded-xl border bg-card p-4 shadow-sm space-y-4"><div><h2 className="font-semibold">Signal detail</h2><p className="text-sm text-muted-foreground">{selected.id} · {selected.source}</p></div><div className="rounded-lg bg-muted p-4"><p className="font-medium">{selected.title}</p><p className="mt-2 text-sm text-muted-foreground">{selected.detail}</p></div><div className="grid grid-cols-2 gap-3"><div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Signal type</p><p className="mt-1 font-medium">{selected.type}</p></div><div className="rounded-lg border p-3"><p className="text-xs text-muted-foreground">Observed at</p><p className="mt-1 font-medium">{selected.timestamp}</p></div></div><div><div className="flex justify-between text-sm"><span className="font-medium">Confidence</span><span>{Math.round(selected.confidence * 100)}%</span></div><div className="mt-2 h-2 rounded-full bg-muted"><div className="h-2 rounded-full bg-foreground" style={{ width: `${selected.confidence * 100}%` }} /></div></div></div>
  </section>;
}
