'use client'

import Link from 'next/link'
import { useState } from 'react'
import { BookOpen, Check, Copy, ExternalLink, FlaskConical, History, Search, Settings, Terminal } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'

const sections = [
  { title: 'Investigate incidents', description: 'Choose a scenario and run the deterministic baseline or LLM-backed investigation path.', icon: Search, href: '/' },
  { title: 'Run experiments', description: 'Create repeatable benchmarks and compare persisted evaluation results.', icon: FlaskConical, href: '/experiments' },
  { title: 'Review history', description: 'Inspect persisted investigation runs, confidence, duration and evaluation status.', icon: History, href: '/history' },
  { title: 'Environment settings', description: 'Check the API connection and change the dashboard theme.', icon: Settings, href: '/settings' },
]

const setup = `python -m pip install trbk
trbk --help
trbk scenarios`

const localSetup = `git clone https://github.com/aawhan0/TraceBack.git
cd TraceBack
python -m venv .venv
python -m pip install -e ".[dev]"
trbk --help`

const commands = `trbk investigate database-pool-exhaustion
trbk runs --limit 10
trbk benchmark --mode baseline --repetitions 3 --name baseline-smoke
trbk experiments --limit 20
trbk compare <baseline-id> <candidate-id>`

function CodeBlock({ value }: { value: string }) {
  const [copied, setCopied] = useState(false)
  return <div className="relative mt-3 overflow-hidden rounded-md border border-slate-800 bg-slate-950">
    <pre className="overflow-x-auto p-4 pr-12 text-[11px] leading-5 text-slate-100"><code>{value}</code></pre>
    <Button type="button" variant="ghost" size="icon" className="absolute right-2 top-2 h-7 w-7 text-slate-300 hover:bg-slate-800 hover:text-white" aria-label="Copy commands" onClick={() => {
      void navigator.clipboard.writeText(value).then(() => {
        setCopied(true)
        window.setTimeout(() => setCopied(false), 1400)
      })
    }}>
      {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
    </Button>
  </div>
}

export default function DocumentationPage() {
  return <div className="space-y-4 pb-6">
    <PageHeader title="Documentation" description="A compact guide to the TraceBack dashboard and its working Python CLI." />

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary"><BookOpen className="h-4 w-4" /></div>
        <div className="min-w-0 flex-1"><h2 className="text-sm font-semibold">Getting started</h2><p className="mt-0.5 text-xs text-muted-foreground">TraceBack is a local incident-investigation and evaluation workspace. Start with Investigate, then use Experiments to measure repeatable behavior.</p></div>
      </div>
      <div className="mt-3 grid gap-2 md:grid-cols-2">
        {sections.map(({ title, description, icon: Icon, href }) => <Link key={href} href={href} className="rounded-md border border-border bg-background p-3 transition-colors hover:bg-accent/40"><div className="flex items-center gap-2"><Icon className="h-3.5 w-3.5 text-primary" /><p className="text-xs font-semibold">{title}</p></div><p className="mt-1 text-[11px] leading-4 text-muted-foreground">{description}</p></Link>)}
      </div>
    </section>

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex items-start gap-3"><div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary"><Terminal className="h-4 w-4" /></div><div><h2 className="text-sm font-semibold">Install the CLI</h2><p className="mt-0.5 text-xs text-muted-foreground">Python 3.12+ is required. Install the published <code>trbk</code> package from PyPI, then use the CLI directly from your terminal.</p></div></div>
      <CodeBlock value={setup} />
      <p className="mt-2 text-[11px] text-muted-foreground">For repository development, use the editable installation shown below.</p>
      <CodeBlock value={localSetup} />
      <p className="mt-2 text-[11px] text-muted-foreground">On Windows PowerShell, activate the environment first with <code className="rounded bg-muted px-1 py-0.5">.\.venv\Scripts\Activate.ps1</code>. On macOS/Linux, use <code className="rounded bg-muted px-1 py-0.5">source .venv/bin/activate</code>.</p>
    </section>

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <h2 className="text-sm font-semibold">Useful CLI commands</h2>
      <p className="mt-0.5 text-xs text-muted-foreground">These operate on the same persisted investigation and experiment data used by the dashboard.</p>
      <CodeBlock value={commands} />
      <Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/cli.md" target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs font-medium hover:bg-accent">Full CLI guide <ExternalLink className="h-3 w-3" /></Link>
    </section>

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm"><h2 className="text-sm font-semibold">Developer resources</h2><p className="mt-0.5 text-xs text-muted-foreground">Architecture, API and experiment notes live in the repository docs.</p><div className="mt-3 flex flex-wrap gap-2 text-xs"><Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/api.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 font-medium hover:bg-accent">API reference <ExternalLink className="h-3 w-3" /></Link><Link href="https://github.com/aawhan0/TraceBack/blob/main/docs/experiments.md" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 font-medium hover:bg-accent">Experiments guide <ExternalLink className="h-3 w-3" /></Link><Link href="https://github.com/aawhan0/TraceBack" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-1.5 font-medium hover:bg-accent">GitHub repository <ExternalLink className="h-3 w-3" /></Link></div></section>
  </div>
}
