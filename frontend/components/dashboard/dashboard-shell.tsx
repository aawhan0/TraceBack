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
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:text-foreground focus:shadow-lg focus:outline-none focus:ring-2 focus:ring-ring"
      >
        Skip to main content
      </a>
      <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <DashboardHeader />
        <main id="main-content" tabIndex={-1} className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-7xl px-4 py-4 md:px-6">{children}</div>
        </main>
      </div>
    </div>
  )
}
