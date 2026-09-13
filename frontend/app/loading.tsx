'use client'

import { Loader2 } from 'lucide-react'

export default function Loading() {
  return (
    <main
      className="flex min-h-[60vh] items-center justify-center px-6 py-16"
      aria-busy="true"
      aria-live="polite"
    >
      <div className="flex flex-col items-center gap-3 text-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" aria-hidden="true" />
        <p className="text-sm text-muted-foreground">Loading TraceBack workspace…</p>
      </div>
    </main>
  )
}
