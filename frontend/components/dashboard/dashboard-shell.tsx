'use client'

import * as React from 'react'
import { AppSidebar } from '@/components/dashboard/app-sidebar'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = React.useState(false)
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-5xl px-4 py-6 md:px-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
