import type { ReactNode } from 'react'

export function ContentSection({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return <section className="space-y-4"><div><h2 className="text-base font-semibold tracking-tight">{title}</h2>{description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}</div>{children}</section>
}
