export function PageHeader({ title, description }: { title: string; description?: string }) {
  return <div className="border-b border-border pb-3">
    <h1 className="text-xl font-bold tracking-tight">{title}</h1>
    {description && <p className="mt-1 max-w-3xl text-sm text-muted-foreground">{description}</p>}
  </div>
}
