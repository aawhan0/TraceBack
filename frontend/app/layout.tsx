'use client'

import React from 'react'
import { ThemeProvider } from 'next-themes'
import { AppSidebar } from '@/components/dashboard/app-sidebar'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'
import './globals.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = React.useState(false)
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex h-screen overflow-hidden bg-background">
            <AppSidebar collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
            <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
              <DashboardHeader />
              <main className="flex-1 overflow-y-auto">
                <div className="mx-auto w-full max-w-5xl px-4 py-6 md:px-8">{children}</div>
              </main>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  )
}
