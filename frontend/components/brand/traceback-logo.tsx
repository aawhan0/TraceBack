'use client'

import Image from 'next/image'
import { useEffect, useState } from 'react'

export function TraceBackLogo({
  collapsed = false,
  className,
}: {
  collapsed?: boolean
  className?: string
}) {
  const [dark, setDark] = useState(false)

  useEffect(() => {
    const update = () => {
      setDark(document.documentElement.classList.contains('dark'))
    }

    update()

    const observer = new MutationObserver(update)
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    })

    return () => observer.disconnect()
  }, [])

  return (
    <div className={`flex items-center gap-2 ${className ?? ''}`}>
      <Image
        src={dark ? '/traceback-mark-logo-dark.png' : '/traceback-mark-logo.png'}
        alt="TraceBack"
        width={32}
        height={32}
        className="h-8 w-8 shrink-0 object-contain"
        priority
      />

      {!collapsed && (
        <span className="font-[Montserrat] text-base font-bold tracking-tight">
          TraceBack
        </span>
      )}
    </div>
  )
}
