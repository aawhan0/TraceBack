import React from 'react'
import { AppSidebar } from '@/components/dashboard/app-sidebar'
import { DashboardHeader } from '@/components/dashboard/dashboard-header'
import './globals.css'

export const metadata = {
  title: 'TraceBack',
  description: 'Local-first incident investigation workspace',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen overflow-hidden bg-background">
          <AppSidebar collapsed={false} onToggle={() => undefined} />
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
            <DashboardHeader />
            <main className="flex-1 overflow-y-auto">
              <div className="mx-auto w-full max-w-5xl px-4 py-6 md:px-8">{children}</div>
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
