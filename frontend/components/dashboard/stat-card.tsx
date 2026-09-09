import * as React from 'react'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

type Props = { title: string; value: string | number; delta?: number; icon?: LucideIcon; className?: string }
export function StatCard({ title, value, delta, icon: Icon, className }: Props) {
  const trend = delta === undefined ? null : delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat'
  return <Card className={cn('transition-shadow hover:shadow-md', className)}><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>{Icon && <Icon className="h-4 w-4 text-muted-foreground" />}</CardHeader><CardContent><div className="text-2xl font-bold tracking-tight text-foreground">{value}</div>{delta !== undefined && <div className={cn('mt-1 flex items-center gap-1 text-xs font-medium', trend === 'up' && 'text-emerald-600 dark:text-emerald-400', trend === 'down' && 'text-destructive', trend === 'flat' && 'text-muted-foreground')}>{trend === 'up' && <TrendingUp className="h-3 w-3" />}{trend === 'down' && <TrendingDown className="h-3 w-3" />}{trend === 'flat' && <Minus className="h-3 w-3" />}<span>{delta > 0 ? '+' : ''}{delta}% from previous runs</span></div>}</CardContent></Card>
}
