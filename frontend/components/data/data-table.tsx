'use client'

import * as React from 'react'
import { ArrowUpDown, ArrowUp, ArrowDown, MoreHorizontal } from 'lucide-react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { cn } from '@/lib/utils'

type SortDir = 'asc' | 'desc'
export type ColumnDef<T> = { key: keyof T & string; header: string; sortable?: boolean; className?: string; render?: (row: T) => React.ReactNode }

type Props<T> = { columns: ColumnDef<T>[]; data: T[]; searchKeys?: (keyof T & string)[]; searchPlaceholder?: string; pageSize?: number }

export function DataTable<T>({ columns, data, searchKeys = [], searchPlaceholder = 'Search…', pageSize = 10 }: Props<T>) {
  const [search, setSearch] = React.useState('')
  const [sortKey, setSortKey] = React.useState<keyof T & string | null>(null)
  const [sortDir, setSortDir] = React.useState<SortDir>('asc')
  const [page, setPage] = React.useState(1)
  const filtered = React.useMemo(() => !search.trim() ? data : data.filter((row) => searchKeys.some((key) => String(row[key] ?? '').toLowerCase().includes(search.toLowerCase()))), [data, search, searchKeys])
  const sorted = React.useMemo(() => !sortKey ? filtered : [...filtered].sort((a, b) => { const av = a[sortKey]; const bv = b[sortKey]; if (av === bv) return 0; const result = av < bv ? -1 : 1; return sortDir === 'asc' ? result : -result }), [filtered, sortKey, sortDir])
  const pageCount = Math.max(1, Math.ceil(sorted.length / pageSize))
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize)
  function handleSort(key: keyof T & string) { if (sortKey === key) setSortDir((dir) => dir === 'asc' ? 'desc' : 'asc'); else { setSortKey(key); setSortDir('asc') }; setPage(1) }
  return <div className="space-y-4"><div className="flex items-center justify-between gap-3"><input value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} placeholder={searchPlaceholder} className="h-9 w-full max-w-sm rounded-md border border-input bg-background px-3 text-sm outline-none placeholder:text-muted-foreground focus:ring-2 focus:ring-ring" /><span className="text-xs text-muted-foreground">{sorted.length} results</span></div><div className="overflow-hidden rounded-lg border border-border bg-card"><Table><TableHeader><TableRow className="hover:bg-transparent">{columns.map((col) => <TableHead key={col.key} className={col.className}>{col.sortable ? <button type="button" onClick={() => handleSort(col.key)} className="inline-flex items-center text-xs font-medium uppercase tracking-wider text-muted-foreground hover:text-foreground">{col.header}{sortKey === col.key ? (sortDir === 'asc' ? <ArrowUp className="ml-1.5 h-3.5 w-3.5 text-primary" /> : <ArrowDown className="ml-1.5 h-3.5 w-3.5 text-primary" />) : <ArrowUpDown className="ml-1.5 h-3.5 w-3.5 opacity-40" />}</button> : <span className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{col.header}</span>}</TableHead>)}<TableHead className="w-10"><MoreHorizontal className="h-4 w-4 opacity-0" /></TableHead></TableRow></TableHeader><TableBody>{paginated.map((row, index) => <TableRow key={index}>{columns.map((col) => <TableCell key={col.key} className={cn('py-3', col.className)}>{col.render ? col.render(row) : String(row[col.key] ?? '')}</TableCell>)}<TableCell /></TableRow>)}</TableBody></Table></div><div className="flex items-center justify-between text-xs text-muted-foreground"><span>Page {page} of {pageCount}</span><div className="flex gap-2"><button type="button" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))} className="rounded-md border border-border px-2.5 py-1 disabled:opacity-40">Previous</button><button type="button" disabled={page >= pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))} className="rounded-md border border-border px-2.5 py-1 disabled:opacity-40">Next</button></div></div></div>
}
