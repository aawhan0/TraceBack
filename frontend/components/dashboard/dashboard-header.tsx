'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Check, Search, Server } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'

const API = process.env.NEXT_PUBLIC_API_URL || '/api'

export function DashboardHeader() {
  const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking')

  useEffect(() => {
    const check = () => {
      void fetch(`${API}/health`).then((response) => setStatus(response.ok ? 'online' : 'offline')).catch(() => setStatus('offline'))
    }
    check()
    const interval = window.setInterval(check, 30000)
    return () => window.clearInterval(interval)
  }, [])

  return <header className="sticky top-0 z-30 flex h-14 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur md:px-6">
    <div className="relative w-full max-w-sm sm:max-w-md">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        placeholder="Search investigations…"
        className="h-9 w-full rounded-md bg-card pl-9 text-sm"
        aria-label="Search investigations"
      />
    </div>
    <Link href="/settings" className="ml-auto inline-flex items-center gap-2 rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors hover:bg-accent" title="API connection settings">
      <span className={cn('h-2 w-2 rounded-full', status === 'online' ? 'bg-emerald-500' : status === 'offline' ? 'bg-destructive' : 'animate-pulse bg-muted-foreground')} />
      <Server className="h-3.5 w-3.5 text-muted-foreground" />
      <span className="hidden sm:inline">{status === 'online' ? 'API online' : status === 'offline' ? 'API offline' : 'Checking API'}</span>
      {status === 'online' && <Check className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />}
    </Link>
  </header>
}
