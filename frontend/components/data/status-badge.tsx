import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Status } from '@/lib/types'

const STATUS_MAP: Record<Status, { label: string; className: string }> = {
  active: { label: 'Active', className: 'border-transparent bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
  inactive: { label: 'Inactive', className: 'border-transparent bg-muted text-muted-foreground' },
  pending: { label: 'Pending', className: 'border-transparent bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' },
  invited: { label: 'Invited', className: 'border-transparent bg-sky-100 text-sky-700 dark:bg-sky-900/30 dark:text-sky-400' },
  suspended: { label: 'Suspended', className: 'border-transparent bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' },
  error: { label: 'Error', className: 'border-transparent bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
  success: { label: 'Success', className: 'border-transparent bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
}

export function StatusBadge({ status, label, className }: { status: Status; label?: string; className?: string }) {
  const config = STATUS_MAP[status] ?? STATUS_MAP.inactive
  return <Badge className={cn(config.className, className)}>{label ?? config.label}</Badge>
}

export type { Status }
