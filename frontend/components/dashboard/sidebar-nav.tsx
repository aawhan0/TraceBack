'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Search, FlaskConical, History } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

type Item = { label: string; href: string; icon: LucideIcon }
const ITEMS: Item[] = [
  { label: 'Investigate', href: '/', icon: Search },
  { label: 'Experiments', href: '/experiments', icon: FlaskConical },
  { label: 'History', href: '/history', icon: History },
]

export function SidebarNav({ collapsed }: { collapsed: boolean }) {
  const pathname = usePathname()
  return <TooltipProvider><nav className="flex flex-col gap-1 px-2">{ITEMS.map(({ label, href, icon: Icon }) => {
    const active = href === '/' ? pathname === '/' : pathname.startsWith(href)
    const link = <Link href={href} className={cn('group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors', collapsed && 'justify-center px-2', active ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground')}><Icon className={cn('h-4 w-4 shrink-0', active ? 'text-primary' : 'text-muted-foreground group-hover:text-accent-foreground')} />{!collapsed && <span>{label}</span>}</Link>
    return collapsed ? <Tooltip key={href} delayDuration={0}><TooltipTrigger asChild>{link}</TooltipTrigger><TooltipContent side="right">{label}</TooltipContent></Tooltip> : <span key={href}>{link}</span>
  })}</nav></TooltipProvider>
}
