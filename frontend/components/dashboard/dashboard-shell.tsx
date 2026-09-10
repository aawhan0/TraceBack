'use client'

import * as React from 'react'
import { AppSidebar } from '@/components/dashboard/app-sidebar'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = React.useState(false)

  React.useEffect(() => {
    const saved = window.localStorage.getItem('traceback-theme')
    const theme = saved === 'dark' || saved === 'light' ? saved : 'light'
    const dark = theme === 'dark'
    document.documentElement.classList.toggle('dark', dark)
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-7xl px-4 py-4 md:px-6">{children}</div>
        </main>
      </div>
    </div>
  )
}
