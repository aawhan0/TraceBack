'use client'

import { Search } from 'lucide-react'
import { Input } from '@/components/ui/input'

export function DashboardHeader() {
  return <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/95 px-4 backdrop-blur md:px-6">
    <div className="relative hidden max-w-xs flex-1 sm:flex"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Search investigations…" className="h-9 pl-9 text-sm" aria-label="Search investigations" /></div>
    <div className="ml-auto text-xs text-muted-foreground">Local API</div>
  </header>
}
