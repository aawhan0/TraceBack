'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'

export function Select({ value, onValueChange, children }: { value: string; onValueChange: (value: string) => void; children: React.ReactNode }) {
  return <div className="relative">{React.Children.map(children, (child) => React.isValidElement(child) ? React.cloneElement(child as React.ReactElement<{ value?: string; onValueChange?: (value: string) => void }>, { value, onValueChange }) : child)}</div>
}

export function SelectTrigger({ children, className }: { children: React.ReactNode; className?: string }) {
  return <select className={cn('flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring', className)}>{children}</select>
}
export function SelectValue({ placeholder }: { placeholder?: string }) { return <option value="">{placeholder}</option> }
export function SelectContent({ children }: { children: React.ReactNode }) { return <>{children}</> }
export function SelectItem({ value, children }: { value: string; children: React.ReactNode }) { return <option value={value}>{children}</option> }
