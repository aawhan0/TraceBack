'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, LibraryBig, Plus, Trash2 } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

type ScenarioSummary = { id: string; title: string; custom: boolean }
type EvidenceDraft = { id: string; source: string; kind: string; content: string }

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options)
  const text = await response.text()
  let data: unknown = null
  if (text) {
    try { data = JSON.parse(text) } catch { throw new Error(`Unexpected response from API (${response.status})`) }
  }
  if (!response.ok) {
    throw new Error(typeof data === 'object' && data && 'detail' in data ? String(data.detail) : `Request failed (${response.status})`)
  }
  return data as T
}

const emptyEvidence = (index: number): EvidenceDraft => ({ id: `ev-custom-${index}`, source: 'service', kind: 'logs', content: '' })

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([])
  const [id, setId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [rootCause, setRootCause] = useState('')
  const [keywords, setKeywords] = useState('')
  const [evidence, setEvidence] = useState<EvidenceDraft[]>([emptyEvidence(1)])
  const [requiredIds, setRequiredIds] = useState('')
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [success, setSuccess] = useState('')

  async function loadScenarios() {
    try { setScenarios(await api<ScenarioSummary[]>('/scenarios')) }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load scenarios') }
  }

  useEffect(() => { void loadScenarios() }, [])

  function updateEvidence(index: number, field: keyof EvidenceDraft, value: string) {
    setEvidence((items) => items.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item))
  }

  function addEvidence() { setEvidence((items) => [...items, emptyEvidence(items.length + 1)]) }
  function removeEvidence(index: number) { setEvidence((items) => items.length === 1 ? items : items.filter((_, itemIndex) => itemIndex !== index)) }

  async function createScenario() {
    setBusy(true); setNotice(''); setSuccess('')
    try {
      await api('/scenarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: id.trim(),
          title: title.trim(),
          description: description.trim(),
          expected_root_cause: rootCause.trim(),
          root_cause_keywords: keywords.split(',').map((item) => item.trim()).filter(Boolean),
          evidence: evidence.map((item) => ({ ...item, id: item.id.trim(), source: item.source.trim(), kind: item.kind.trim(), content: item.content.trim() })),
          required_evidence_ids: requiredIds.split(',').map((item) => item.trim()).filter(Boolean),
        }),
      })
      setSuccess(`Scenario “${title.trim()}” created. It is now available in Investigate.`)
      setId(''); setTitle(''); setDescription(''); setRootCause(''); setKeywords(''); setRequiredIds(''); setEvidence([emptyEvidence(1)])
      await loadScenarios()
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to create scenario') }
    finally { setBusy(false) }
  }

  const canSubmit = id.trim() && title.trim() && description.trim() && rootCause.trim() && keywords.trim() && evidence.every((item) => item.id.trim() && item.source.trim() && item.kind.trim() && item.content.trim())

  return <div className="space-y-5 pb-10">
    <PageHeader title="Scenarios" description="Create reusable incident cases with ground truth and evidence for investigation and evaluation." />
    {notice && <div className="flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive"><CircleAlert className="h-4 w-4" /><span>{notice}</span></div>}
    {success && <div className="flex items-center gap-2 rounded-md border border-primary/20 bg-primary/5 px-3 py-2 text-sm text-primary"><Check className="h-4 w-4" /><span>{success}</span></div>}

    <section className="grid gap-4 lg:grid-cols-[minmax(0,1.1fr)_minmax(300px,.9fr)]">
      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="mb-5 flex items-start gap-3"><div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10 text-primary"><LibraryBig className="h-4 w-4" /></div><div><h2 className="text-base font-semibold">Create custom scenario</h2><p className="mt-1 text-sm text-muted-foreground">Define the incident, expected diagnosis, and evidence the evaluator should expect.</p></div></div>
        <div className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Scenario ID"><Input value={id} onChange={(e) => setId(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-'))} placeholder="payment-timeout" /></Field>
            <Field label="Title"><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Payment API timeout spike" /></Field>
          </div>
          <Field label="Incident description"><textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the production symptom and impact..." className="min-h-24 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" /></Field>
          <Field label="Expected root cause"><Input value={rootCause} onChange={(e) => setRootCause(e.target.value)} placeholder="Database connection pool exhaustion" /></Field>
          <Field label="Root-cause keywords"><Input value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="database, connection pool, exhaustion" /><p className="mt-1 text-[11px] text-muted-foreground">Comma-separated terms used by the deterministic evaluator.</p></Field>

          <div className="space-y-3">
            <div className="flex items-center justify-between"><div><label className="text-sm font-medium">Evidence</label><p className="mt-1 text-xs text-muted-foreground">Add the logs, metrics, events, or traces available to the investigator.</p></div><Button type="button" variant="outline" size="sm" onClick={addEvidence}><Plus />Add evidence</Button></div>
            {evidence.map((item, index) => <div key={`${index}-${item.id}`} className="rounded-md border border-border bg-muted/10 p-3"><div className="grid gap-3 sm:grid-cols-3"><Field label="Evidence ID"><Input value={item.id} onChange={(e) => updateEvidence(index, 'id', e.target.value)} /></Field><Field label="Source"><Input value={item.source} onChange={(e) => updateEvidence(index, 'source', e.target.value)} placeholder="api" /></Field><Field label="Kind"><Input value={item.kind} onChange={(e) => updateEvidence(index, 'kind', e.target.value)} placeholder="logs" /></Field></div><div className="mt-3 flex gap-2"><textarea value={item.content} onChange={(e) => updateEvidence(index, 'content', e.target.value)} placeholder="Evidence content..." className="min-h-20 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring" /><Button type="button" variant="ghost" size="icon" disabled={evidence.length === 1} onClick={() => removeEvidence(index)} aria-label="Remove evidence"><Trash2 className="h-4 w-4" /></Button></div></div>)}
          </div>

          <Field label="Required evidence IDs"><Input value={requiredIds} onChange={(e) => setRequiredIds(e.target.value)} placeholder="ev-custom-1, ev-custom-2" /><p className="mt-1 text-[11px] text-muted-foreground">Optional. These IDs must be selected for the evidence recall check to pass.</p></Field>
          <Button type="button" disabled={!canSubmit || busy} onClick={createScenario}>{busy ? 'Creating…' : 'Create scenario'}</Button>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="mb-4"><h2 className="text-base font-semibold">Scenario catalog</h2><p className="mt-1 text-sm text-muted-foreground">Built-in cases and persisted custom cases available to TraceBack.</p></div>
        <div className="space-y-2">{scenarios.map((item) => <div key={item.id} className="rounded-md border border-border px-3.5 py-3"><div className="flex items-start justify-between gap-3"><div className="min-w-0"><p className="truncate text-sm font-medium">{item.title}</p><p className="mt-1 truncate font-mono text-[11px] text-muted-foreground">{item.id}</p></div><span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground">{item.custom ? 'Custom' : 'Built-in'}</span></div></div>)}{!scenarios.length && <p className="py-8 text-center text-sm text-muted-foreground">No scenarios found.</p>}</div>
      </div>
    </section>
  </div>
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <div className="space-y-2"><label className="text-sm font-medium">{label}</label>{children}</div>
}
