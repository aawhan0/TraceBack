'use client'

import * as React from 'react'

export function Select({ value, onValueChange, children }: { value: string; onValueChange: (value: string) => void; children: React.ReactNode }) {
  const items = React.Children.toArray(children).flatMap((child) => {
    if (!React.isValidElement(child) || child.type !== SelectContent) return []
    return React.Children.toArray((child.props as { children?: React.ReactNode }).children)
  }) as React.ReactElement<{ value: string; children: React.ReactNode }>[]
  return <select value={value} onChange={(e) => onValueChange(e.target.value)} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring"><option value="">Select an incident</option>{items.map((item) => <option key={item.props.value} value={item.props.value}>{item.props.children}</option>)}</select>
}
export function SelectTrigger({ children }: { children: React.ReactNode }) { return <>{children}</> }
export function SelectValue({ placeholder }: { placeholder?: string }) { return <span>{placeholder}</span> }
export function SelectContent({ children }: { children: React.ReactNode }) { return <>{children}</> }
export function SelectItem({ value, children }: { value: string; children: React.ReactNode }) { return <span data-value={value}>{children}</span> }
