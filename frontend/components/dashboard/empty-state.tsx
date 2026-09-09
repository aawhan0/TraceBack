import type { LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type Props = { icon?: LucideIcon; title: string; description?: string; action?: { label: string; onClick: () => void }; className?: string }
export function EmptyState({ icon: Icon, title, description, action, className }: Props) {
  return <div className={cn('flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 px-6 py-14 text-center', className)}>{Icon && <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-muted"><Icon className="h-6 w-6 text-muted-foreground" /></div>}<h3 className="text-sm font-semibold text-foreground">{title}</h3>{description && <p className="mt-1 max-w-xs text-sm text-muted-foreground">{description}</p>}{action && <Button size="sm" className="mt-4" onClick={action.onClick}>{action.label}</Button>}</div>
}
