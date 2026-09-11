'use client'

import { useEffect, useState } from 'react'
import { BookOpen, Check, CircleAlert, Search, ShieldCheck } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'
type Entry = { scenario_id: string; title: string; description: string; root_cause: string; evidence_count: number; required_evidence_ids: string[]; latest_run_id: string | null; latest_run_passed: boolean | null; latest_run_confidence: number | null; latest_run_at: string | null; matched_terms: string[] }

export default function KnowledgePage() {
  const [query, setQuery] = useState('')
  const [entries, setEntries] = useState<Entry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function search(queryValue = query) {
    setLoading(true); setError('')
    try {
      const response = await fetch(`${API}/knowledge?q=${encodeURIComponent(queryValue.trim())}&limit=50`)
      if (!response.ok) throw new Error('Unable to load incident knowledge')
      setEntries(await response.json() as Entry[])
    } catch (item) { setError(item instanceof Error ? item.message : 'Unable to load incident knowledge') }
    finally { setLoading(false) }
  }

  useEffect(() => { void search('') }, [])

  return <div className="space-y-6 pb-10">
    <PageHeader title="Knowledge Base" description="Search reusable incident patterns, ground truth and the latest evaluated run for each scenario." />
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-3"><div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary"><Search className="h-4 w-4" /></div><div><h2 className="text-base font-semibold">Find a known failure</h2><p className="mt-1 text-sm text-muted-foreground">Search scenario descriptions, root causes and evidence content.</p></div></div>
      <form className="mt-5 flex gap-2" onSubmit={(event) => { event.preventDefault(); void search() }}><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="database pool, Redis, retry loop..." /><Button type="submit">Search</Button></form>
    </section>
    {error && <div className="rounded-md border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">{error}</div>}
    {loading ? <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">Searching the knowledge base...</div> : !entries.length ? <div className="rounded-lg border border-dashed p-10 text-center text-sm text-muted-foreground">No matching incident patterns found.</div> : <div className="grid gap-4 lg:grid-cols-2">{entries.map((entry) => <article key={entry.scenario_id} className="rounded-lg border border-border bg-card p-5 shadow-sm"><div className="flex items-start justify-between gap-3"><div><div className="flex items-center gap-2"><BookOpen className="h-4 w-4 text-primary" /><h2 className="text-base font-semibold">{entry.title}</h2></div><p className="mt-1 font-mono text-[11px] text-muted-foreground">{entry.scenario_id}</p></div>{entry.latest_run_passed === true ? <Check className="h-5 w-5 text-primary" /> : entry.latest_run_passed === false ? <CircleAlert className="h-5 w-5 text-destructive" /> : <ShieldCheck className="h-5 w-5 text-muted-foreground" />}</div><p className="mt-4 text-sm leading-6 text-muted-foreground">{entry.description}</p><div className="mt-4 rounded-md bg-muted/30 p-3"><p className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">Known root cause</p><p className="mt-1 text-sm font-semibold">{entry.root_cause}</p></div><div className="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground"><span className="rounded-full bg-muted px-2.5 py-1">{entry.evidence_count} evidence items</span>{entry.required_evidence_ids.length > 0 && <span className="rounded-full bg-muted px-2.5 py-1">{entry.required_evidence_ids.length} required</span>}{entry.latest_run_confidence !== null && <span className="rounded-full bg-muted px-2.5 py-1">Latest confidence {Math.round(entry.latest_run_confidence * 100)}%</span>}</div>{entry.matched_terms.length > 0 && <p className="mt-3 text-xs text-primary">Matched: {entry.matched_terms.join(', ')}</p>}{entry.latest_run_id && <p className="mt-4 border-t border-border pt-3 text-[11px] text-muted-foreground">Latest run: <code>{entry.latest_run_id}</code>{entry.latest_run_at ? `  -  ${new Date(entry.latest_run_at).toLocaleString()}` : ''}</p>}</article>)}</div>}
  </div>
}

