'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { PanelLeftClose, PanelLeftOpen, Search, FlaskConical, History } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const items = [
  { label: 'Investigate', href: '/', icon: Search },
  { label: 'Experiments', href: '/experiments', icon: FlaskConical },
  { label: 'History', href: '/history', icon: History },
]

export function AppSidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const pathname = usePathname()
  return <aside style={{ width: collapsed ? 56 : 220 }} className="hidden md:flex shrink-0 flex-col overflow-hidden border-r border-border bg-card transition-[width] duration-200">
    <div className={cn('flex h-14 items-center border-b border-border', collapsed ? 'justify-center' : 'gap-2 px-4')}>
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground text-sm font-semibold">T</div>
      {!collapsed && <span className="text-sm font-semibold tracking-tight">TraceBack</span>}
    </div>
    <nav className="flex-1 space-y-1 p-2 pt-4">
      {items.map(({ label, href, icon: Icon }) => {
        const active = href === '/' ? pathname === '/' : pathname.startsWith(href)
        return <Link key={href} href={href} className={cn('flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors', collapsed && 'justify-center px-2', active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground')}>
          <Icon className="h-4 w-4 shrink-0" />
          {!collapsed && <span>{label}</span>}
        </Link>
      })}
    </nav>
    <div className={cn('border-t border-border p-2', collapsed ? 'flex justify-center' : 'flex justify-end')}>
      <Button type="button" variant="ghost" size="icon" className="h-8 w-8" onClick={onToggle} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
        {collapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
      </Button>
    </div>
  </aside>
}
