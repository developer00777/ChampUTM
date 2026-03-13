import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import type { ClicksByDimension } from '../../types/utm'

const COLORS = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']

interface SourcePieChartProps {
  data: ClicksByDimension[]
  title?: string
}

function renderLabel({ name, percent }: { name?: string; percent?: number }) {
  return `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`
}

export function SourcePieChart({ data, title = 'Clicks by Source' }: SourcePieChartProps) {
  const chartData = data.map((d) => ({ name: d.label, value: d.count }))

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-700 mb-4">{title}</h3>
      {chartData.length === 0 ? (
        <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
          No data yet
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              outerRadius={80}
              dataKey="value"
              nameKey="name"
              label={renderLabel}
              labelLine={false}
            >
              {chartData.map((_entry, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
