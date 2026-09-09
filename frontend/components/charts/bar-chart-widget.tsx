'use client'

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ChartTooltip } from './chart-tooltip'

type Props = { data: Record<string, string | number>[]; xKey: string; series: { key: string; color: string; label?: string }[]; valuePrefix?: string; valueSuffix?: string; height?: number; radius?: number }

export function BarChartWidget({ data, xKey, series, valuePrefix, valueSuffix, height = 220, radius = 4 }: Props) {
  return <ResponsiveContainer width="100%" height={height}>
    <BarChart data={data} margin={{ top: 4, right: 4, left: -16, bottom: 0 }} barCategoryGap="30%">
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
      <XAxis dataKey={xKey} tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} dy={6} />
      <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} tickFormatter={(v) => `${valuePrefix ?? ''}${v >= 1000 ? `${(v / 1000).toFixed(0)}k` : v}`} />
      <Tooltip content={<ChartTooltip valuePrefix={valuePrefix} valueSuffix={valueSuffix} />} cursor={{ fill: 'hsl(var(--muted))', opacity: 0.5 }} />
      {series.map((s) => <Bar key={s.key} dataKey={s.key} name={s.label ?? s.key} fill={s.color} radius={[radius, radius, 0, 0]} />)}
    </BarChart>
  </ResponsiveContainer>
}
