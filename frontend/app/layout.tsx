import type React from 'react'
import './globals.css'
import { DashboardShell } from '@/components/dashboard/dashboard-shell'

export const metadata = {
  title: 'TraceBack',
  description: 'Local-first incident investigation workspace',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <DashboardShell>{children}</DashboardShell>
      </body>
    </html>
  )
}
