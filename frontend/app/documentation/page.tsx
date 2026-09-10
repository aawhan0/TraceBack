import Link from 'next/link'
import { BookOpen, ExternalLink, FlaskConical, History, Search, Settings, Terminal } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'

const sections = [
  { title: 'Investigate incidents', description: 'Choose a scenario and run the deterministic baseline or LLM-backed investigation path.', icon: Search, href: '/' },
  { title: 'Run experiments', description: 'Create repeatable baseline benchmarks across the real scenario catalog and review regression outcomes.', icon: FlaskConical, href: '/experiments' },
  { title: 'Review history', description: 'Inspect persisted investigation runs, confidence, duration and evaluation status.', icon: History, href: '/history' },
  { title: 'Environment settings', description: 'Check the local API connection and runtime defaults used by this dashboard.', icon: Settings, href: '/settings' },
]

export default function DocumentationPage() {
  return <div className="space-y-6 pb-10">
    <PageHeader title="Documentation" description="A quick guide to the TraceBack dashboard and CLI." />
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary"><BookOpen className="h-4 w-4" /></div>
        <div><h2 className="text-base font-semibold">Getting started</h2><p className="mt-1 text-sm text-muted-foreground">TraceBack is a local incident-investigation and evaluation workspace. Start with Investigate, then use Experiments to measure repeatable behavior.</p></div>
      </div>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {sections.map(({ title, description, icon: Icon, href }) => <Link key={href} href={href} className="rounded-md border border-border bg-background p-4 transition-colors hover:bg-accent/40"><div className="flex items-center gap-2"><Icon className="h-4 w-4 text-primary" /><p className="text-sm font-semibold">{title}</p></div><p className="mt-1.5 text-xs leading-5 text-muted-foreground">{description}</p></Link>)}
      </div>
    </section>
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3"><div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary"><Terminal className="h-4 w-4" /></div><div><h2 className="text-base font-semibold">CLI quick start</h2><p className="mt-1 text-sm text-muted-foreground">Run investigations, inspect persisted runs, benchmark scenarios and compare experiments from a terminal.</p></div></div>
      <pre className="mt-4 overflow-x-auto rounded-md bg-muted/50 p-4 text-xs leading-6"><code>{`traceback scenarios\ntraceback investigate database-pool-exhaustion\ntraceback runs --limit 10\ntraceback benchmark --mode baseline --repetitions 3 --name baseline-smoke\ntraceback experiments --limit 20\ntraceback compare <baseline-id> <candidate-id>`}</code></pre>
      <p className="mt-3 text-xs text-muted-foreground">Install with <code className="rounded bg-muted px-1 py-0.5">pip install -e ".[dev]"</code>, then run <code className="rounded bg-muted px-1 py-0.5">traceback --help</code> for command-specific options.</p>
      <Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/cli.md" target="_blank" rel="noreferrer" className="mt-4 inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-accent">Full CLI guide <ExternalLink className="h-3.5 w-3.5" /></Link>
    </section>
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm"><h2 className="text-base font-semibold">Developer resources</h2><p className="mt-1 text-sm text-muted-foreground">Detailed architecture and API notes are kept in the repository docs.</p><div className="mt-4 flex flex-wrap gap-2 text-sm"><Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/api.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">API reference <ExternalLink className="h-3.5 w-3.5" /></Link><Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/experiments.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">Experiments guide <ExternalLink className="h-3.5 w-3.5" /></Link><Link href="https://github.com/aawhan0/TraceBack" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 font-medium hover:bg-accent">GitHub repository <ExternalLink className="h-3.5 w-3.5" /></Link></div></section>
  </div>
}
