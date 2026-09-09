'use client'

import { useEffect, useState } from 'react'
import { Check, CircleAlert, ServerCog } from 'lucide-react'
import { PageHeader } from '@/components/dashboard/page-header'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export default function SettingsPage() {
  const [health, setHealth] = useState<'checking' | 'ok' | 'error'>('checking')

  useEffect(() => {
    void fetch(`${API}/health`).then((response) => {
      setHealth(response.ok ? 'ok' : 'error')
    }).catch(() => setHealth('error'))
  }, [])

  return <div className="space-y-6 pb-10">
    <PageHeader title="Settings" description="Review the local TraceBack environment and frontend connection." />
    <section className="rounded-lg border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary"><ServerCog className="h-4 w-4" /></div>
        <div>
          <h2 className="text-base font-semibold">Local API connection</h2>
          <p className="mt-1 text-sm text-muted-foreground">The dashboard uses the configured API route for investigations, runs and experiments.</p>
        </div>
      </div>
      <div className="mt-5 rounded-md border border-border bg-muted/20 px-4 py-3">
        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Status</p>
        <div className="mt-1 flex items-center gap-2 text-sm font-medium">
          {health === 'checking' && <><span className="h-2 w-2 animate-pulse rounded-full bg-muted-foreground" />Checking API…</>}
          {health === 'ok' && <><Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />API reachable</>}
          {health === 'error' && <><CircleAlert className="h-4 w-4 text-destructive" />API unavailable</>}
        </div>
        <p className="mt-1 text-xs text-muted-foreground">Endpoint: {API}</p>
      </div>
    </section>
  </div>
}
