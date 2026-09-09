import Link from 'next/link'
import { BookOpen, ExternalLink } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'

const sections = [
  {
    title: 'Investigations',
    description: 'Select a configured incident and run the deterministic baseline or an LLM-backed investigation. Results include root cause, supporting evidence, confidence, evaluation status and a recommended action.',
  },
  {
    title: 'History',
    description: 'Review persisted investigation runs, including scenario, mode, provider, confidence, duration and pass status.',
  },
  {
    title: 'Experiments',
    description: 'Create repeatable baseline benchmarks across the version-controlled scenario dataset. Saved experiments include pass rate, regression status, provider provenance and dataset fingerprint.',
  },
]

export default function DocumentationPage() {
  return <div className="space-y-6 pb-10">
    <PageHeader title="Documentation" description="A quick guide to the TraceBack investigation and evaluation workflow." />
    <div className="grid gap-4 lg:grid-cols-3">
      {sections.map((section) => <section key={section.title} className="rounded-lg border border-border bg-card p-5 shadow-sm">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary"><BookOpen className="h-4 w-4" /></div>
        <h2 className="mt-4 text-base font-semibold">{section.title}</h2>
        <p className="mt-2 text-sm leading-6 text-muted-foreground">{section.description}</p>
      </section>)}
    </div>
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <h2 className="text-base font-semibold">Developer resources</h2>
      <p className="mt-1 text-sm text-muted-foreground">Detailed architecture and API notes are kept in the repository docs.</p>
      <div className="mt-4 flex flex-wrap gap-2 text-sm">
        <Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/api.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">API reference <ExternalLink className="h-3.5 w-3.5" /></Link>
        <Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/experiments.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">Experiments guide <ExternalLink className="h-3.5 w-3.5" /></Link>
        <Link href="https://github.com/aawhan0/TraceBack" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">GitHub repository <ExternalLink className="h-3.5 w-3.5" /></Link>
      </div>
    </section>
  </div>
}
