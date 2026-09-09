import Link from 'next/link'
import { BookOpen, FlaskConical, History, Search, Settings } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'

const sections = [
  { title: 'Investigate incidents', description: 'Choose a scenario and run the deterministic baseline or LLM-backed investigation path.', icon: Search, href: '/' },
  { title: 'Run experiments', description: 'Create repeatable baseline benchmarks across the real scenario catalog and review regression outcomes.', icon: FlaskConical, href: '/experiments' },
  { title: 'Review history', description: 'Inspect persisted investigation runs, confidence, duration and evaluation status.', icon: History, href: '/history' },
  { title: 'Environment settings', description: 'Check the local API connection and runtime defaults used by this dashboard.', icon: Settings, href: '/settings' },
]

export default function DocumentationPage() {
  return <div className="space-y-6 pb-10">
    <PageHeader title="Documentation" description="A quick guide to using the TraceBack dashboard." />
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary"><BookOpen className="h-4 w-4" /></div>
        <div><h2 className="text-base font-semibold">Getting started</h2><p className="mt-1 text-sm text-muted-foreground">TraceBack is a local incident-investigation and evaluation workspace. Start with Investigate, then use Experiments to measure repeatable behavior.</p></div>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {sections.map(({ title, description, icon: Icon, href }) => <Link key={href} href={href} className="rounded-md border border-border bg-background p-4 transition-colors hover:bg-accent/40"><div className="flex items-center gap-2"><Icon className="h-4 w-4 text-primary" /><p className="text-sm font-semibold">{title}</p></div><p className="mt-1.5 text-xs leading-5 text-muted-foreground">{description}</p></Link>)}
      </div>
    </section>
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm"><h2 className="text-base font-semibold">Core API routes</h2><div className="mt-3 space-y-2 font-mono text-xs"><p><span className="text-primary">GET</span> /scenarios</p><p><span className="text-primary">POST</span> /investigations</p><p><span className="text-primary">GET</span> /runs</p><p><span className="text-primary">POST</span> /experiments</p><p><span className="text-primary">GET</span> /experiments</p><p><span className="text-primary">GET</span> /health</p></div></section>
  </div>
}
