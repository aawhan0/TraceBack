import type { SVGProps } from 'react'

export function TraceBackMark({ className, ...props }: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" className={className} aria-hidden="true" {...props}>
      <path
        d="M29 7c-3 1-5 6-5 13 0 8 1 15 5 20 3 4 8 4 13 1"
        stroke="currentColor"
        strokeWidth="4.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M24 22C18 22 12 23 5 22m0 0 7-6m-7 6 7 6"
        stroke="currentColor"
        strokeWidth="4.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M28 8c-2 2-3 7-3 13"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
        opacity="0.28"
      />
    </svg>
  )
}

export function TraceBackLogo({ collapsed = false, className }: { collapsed?: boolean; className?: string }) {
  return (
    <div className={`flex items-center gap-2 ${className ?? ''}`}>
      <TraceBackMark className="h-8 w-8 shrink-0 text-primary" />
      {!collapsed && <span className="font-[Montserrat] text-base font-bold tracking-tight">TraceBack</span>}
    </div>
  )
}
