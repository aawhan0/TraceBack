import * as React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

type Props = { title: string; description?: string; action?: React.ReactNode; children: React.ReactNode; className?: string }

export function ChartCard({ title, description, action, children, className }: Props) {
  return <Card className={cn('flex flex-col', className)}>
    <CardHeader className="flex flex-row items-start justify-between gap-4 pb-2">
      <div><CardTitle className="text-sm font-semibold">{title}</CardTitle>{description && <CardDescription className="mt-0.5 text-xs">{description}</CardDescription>}</div>
      {action && <div className="shrink-0">{action}</div>}
    </CardHeader>
    <CardContent className="flex-1 pt-0">{children}</CardContent>
  </Card>
}
