'use client'

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartTooltip } from './chart-tooltip'

type Props = { data: Record<string, string | number>[]; xKey: string; series: { key: string; color: string; label?: string; dashed?: boolean }[]; valuePrefix?: string; valueSuffix?: string; height?: number; tickInterval?: number }

export function LineChartWidget({ data, xKey, series, valuePrefix, valueSuffix, height = 220, tickInterval }: Props) {
  return <ResponsiveContainer width="100%" height={height}>
    <LineChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
      <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} dy={6} interval={tickInterval ?? 'preserveStartEnd'} />
      <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} tickFormatter={(v) => `${valuePrefix ?? ''}${v}`} />
      <Tooltip content={<ChartTooltip valuePrefix={valuePrefix} valueSuffix={valueSuffix} />} cursor={{ stroke: 'hsl(var(--border))', strokeWidth: 1 }} />
      {series.map((s) => <Line key={s.key} type="monotone" dataKey={s.key} name={s.label ?? s.key} stroke={s.color} strokeWidth={2} strokeDasharray={s.dashed ? '5 3' : undefined} dot={false} activeDot={{ r: 4, fill: s.color, strokeWidth: 0 }} />)}
    </LineChart>
  </ResponsiveContainer>
}
