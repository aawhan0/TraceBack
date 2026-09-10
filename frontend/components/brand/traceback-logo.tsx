'use client'

import Image from 'next/image'

export function TraceBackLogo({
  collapsed = false,
  className,
}: {
  collapsed?: boolean
  className?: string
}) {
  return (
    <div className={`flex items-center gap-2 ${className ?? ''}`}>
      <picture>
        <source media="(prefers-color-scheme: dark)" srcSet="/traceback-mark-logo-dark.png" />
        <Image
          src="/traceback-mark-logo.png"
          alt="TraceBack"
          width={32}
          height={32}
          className="h-8 w-8 shrink-0 object-contain"
          priority
        />
      </picture>

      {!collapsed && (
        <span className="font-[Montserrat] text-base font-bold tracking-tight">
          TraceBack
        </span>
      )}
    </div>
  )
}
