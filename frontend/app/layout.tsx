import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'TraceBack — Investigate incident',
  description: 'Run and inspect TraceBack incident investigations.',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en" className="bg-[#f5f5f1]"><body>{children}</body></html>
}
