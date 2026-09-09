'use client'

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartTooltip } from './chart-tooltip'

type Props = { data: Record<string, string | number>[]; xKey: string; series: { key: string; color: string; label?: string }[]; valuePrefix?: string; valueSuffix?: string; height?: number }

export function AreaChartWidget({ data, xKey, series, valuePrefix, valueSuffix, height = 220 }: Props) {
  return <ResponsiveContainer width="100%" height={height}>
    <AreaChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
      <defs>{series.map((s) => <linearGradient key={s.key} id={`grad-${s.key}`} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor={s.color} stopOpacity={0.25} /><stop offset="95%" stopColor={s.color} stopOpacity={0} /></linearGradient>)}</defs>
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
      <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} dy={6} />
      <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} tickFormatter={(v) => `${valuePrefix ?? ''}${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`} />
      <Tooltip content={<ChartTooltip valuePrefix={valuePrefix} valueSuffix={valueSuffix} />} cursor={{ stroke: 'hsl(var(--border))', strokeWidth: 1 }} />
      {series.map((s) => <Area key={s.key} type="monotone" dataKey={s.key} name={s.label ?? s.key} stroke={s.color} strokeWidth={2} fill={`url(#grad-${s.key})`} dot={false} activeDot={{ r: 4, fill: s.color, strokeWidth: 0 }} />)}
    </AreaChart>
  </ResponsiveContainer>
}
