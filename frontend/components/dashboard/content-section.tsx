import * as React from 'react'
import { cn } from '@/lib/utils'

type Props = { title: string; description?: string; action?: React.ReactNode; children: React.ReactNode; className?: string }

export function ContentSection({ title, description, action, children, className }: Props) {
  return <section className={cn('space-y-4', className)}><div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"><div><h2 className="text-base font-semibold tracking-tight">{title}</h2>{description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}</div>{action && <div className="shrink-0">{action}</div>}</div>{children}</section>
}
