'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, Monitor, Moon, RefreshCw, ServerCog, Sun } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'
type Theme = 'light' | 'dark' | 'system'

function applyTheme(theme: Theme) {
  const dark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
  document.documentElement.classList.toggle('dark', dark)
  window.localStorage.setItem('traceback-theme', theme)
}

const themes: { value: Theme; label: string; icon: typeof Sun }[] = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
]

export default function SettingsPage() {
  const [health, setHealth] = useState<'checking' | 'ok' | 'error'>('checking')
  const [theme, setTheme] = useState<Theme>('light')

  const checkHealth = () => {
    setHealth('checking')
    void fetch(`${API}/health`).then((response) => {
      setHealth(response.ok ? 'ok' : 'error')
    }).catch(() => setHealth('error'))
  }

  useEffect(() => {
    const saved = window.localStorage.getItem('traceback-theme') as Theme | null
    const next = saved === 'dark' || saved === 'light' || saved === 'system' ? saved : 'light'
    setTheme(next)
    applyTheme(next)
    checkHealth()
  }, [])

  return <div className="space-y-4 pb-6">
    <PageHeader title="Settings" description="Manage the small set of preferences that are actually supported by the local TraceBack workspace." />

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary"><Monitor className="h-4 w-4" /></div>
        <div className="min-w-0 flex-1">
          <h2 className="text-sm font-semibold">Appearance</h2>
          <p className="mt-0.5 text-xs text-muted-foreground">Choose how the dashboard handles its light and dark theme.</p>
          <div className="mt-3 grid grid-cols-3 gap-2 sm:max-w-md">
            {themes.map(({ value, label, icon: Icon }) => <Button key={value} type="button" variant={theme === value ? 'secondary' : 'outline'} className={cn('h-9 justify-center gap-2 text-xs', theme === value && 'ring-1 ring-primary/30')} onClick={() => { setTheme(value); applyTheme(value) }}>
              <Icon className="h-3.5 w-3.5" />{label}
            </Button>)}
          </div>
        </div>
      </div>
    </section>

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary"><ServerCog className="h-4 w-4" /></div>
        <div className="min-w-0 flex-1">
          <h2 className="text-sm font-semibold">Local API connection</h2>
          <p className="mt-0.5 text-xs text-muted-foreground">The dashboard talks to the FastAPI backend through the configured frontend API route.</p>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-muted/20 px-3 py-2.5">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Health</p>
              <div className="mt-0.5 flex items-center gap-2 text-sm font-medium">
                {health === 'checking' && <><span className="h-2 w-2 animate-pulse rounded-full bg-muted-foreground" />Checking API…</>}
                {health === 'ok' && <><Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />API reachable</>}
                {health === 'error' && <><CircleAlert className="h-4 w-4 text-destructive" />API unavailable</>}
              </div>
            </div>
            <Button type="button" variant="outline" size="sm" className="h-8 gap-1.5 text-xs" onClick={checkHealth} disabled={health === 'checking'}>
              <RefreshCw className={cn('h-3.5 w-3.5', health === 'checking' && 'animate-spin')} />Refresh
            </Button>
          </div>
          <p className="mt-2 font-mono text-[11px] text-muted-foreground">Frontend API route: {API}</p>
        </div>
      </div>
    </section>

    <section className="rounded-lg border border-border bg-card p-4 shadow-sm">
      <h2 className="text-sm font-semibold">TraceBack runtime</h2>
      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        <div className="rounded-md border border-border bg-muted/20 p-3"><p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Investigations</p><p className="mt-1 text-xs">Deterministic baseline with optional LLM-backed mode.</p></div>
        <div className="rounded-md border border-border bg-muted/20 p-3"><p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">LLM provider</p><p className="mt-1 text-xs">Ollama, when an investigation explicitly selects LLM mode.</p></div>
        <div className="rounded-md border border-border bg-muted/20 p-3"><p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Persistence</p><p className="mt-1 text-xs">SQLite-backed runs and experiments shared by the CLI and dashboard.</p></div>
      </div>
    </section>
  </div>
}
